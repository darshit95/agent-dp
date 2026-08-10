from __future__ import annotations

import re
import threading
from dataclasses import dataclass

from cardbudget.categorization.ollama import OllamaClassifierClient, OllamaUnavailable
from cardbudget.db.repositories import AssetRecord, NetWorthRepository
from cardbudget.db.schema import ASSET_BUCKETS


def asset_key(name: str, institution: str | None) -> str:
    raw = f"{name or ''}|{institution or ''}".upper().strip()
    raw = re.sub(r"[^A-Z0-9|]+", " ", raw)
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw[:200]


def _heuristic_category(name: str, institution: str | None) -> str:
    text = f"{name} {institution or ''}".upper()
    if any(token in text for token in ("401K", "401(K)", "IRA", "RETIRE", "HSA", "HEALTH SAVINGS")):
        return "Retirement & Health"
    if any(token in text for token in ("HYSA", "SAVINGS", "CHECKING", "EMERGENCY", "MONEY MARKET", "CASH", " CD ", "CERTIFICATE OF DEPOSIT")):
        return "Cash & Cash Equivalents"
    if any(token in text for token in ("BROKERAGE", "ROBINHOOD", "ETRADE", "E*TRADE", "ETF", "STOCK", "MUTUAL FUND", "BOND")):
        return "Taxable Investments"
    if any(token in text for token in ("CRYPTO", "BITCOIN", "ETHEREUM", "PRIVATE EQUITY", "STARTUP", "VENTURE")):
        return "Alternative Investments"
    return "Other Assets"


@dataclass(frozen=True)
class AssetClassification:
    asset_bucket: str
    source: str
    confidence: float


class NetWorthService:
    def __init__(self, repository: NetWorthRepository, llm: OllamaClassifierClient) -> None:
        self.repository = repository
        self.llm = llm

    def classify(self, name: str, institution: str | None) -> AssetClassification:
        key = asset_key(name, institution)
        rule = self.repository.get_rule(key) if key else None
        if rule in ASSET_BUCKETS:
            return AssetClassification(rule, "saved_rule", 1.0)
        try:
            result = self.llm.classify_asset(
                asset_name=name,
                institution=institution or "",
                buckets=list(ASSET_BUCKETS),
            )
            if result.bucket_name in ASSET_BUCKETS:
                return AssetClassification(result.bucket_name, "local_llm", result.confidence)
        except OllamaUnavailable:
            pass
        return AssetClassification(_heuristic_category(name, institution), "heuristic_fallback", 0.5)

    def _refine_asset_category_in_background(
        self,
        asset_id: int,
        *,
        name: str,
        institution: str,
        provisional_bucket: str,
    ) -> None:
        """Refine an auto-classified asset without blocking the web request."""
        try:
            result = self.llm.classify_asset(
                asset_name=name,
                institution=institution or "",
                buckets=list(ASSET_BUCKETS),
            )

            if result.bucket_name not in ASSET_BUCKETS:
                return

            current = self.repository.get_asset(asset_id)
            if current is None:
                return

            # Do not overwrite a user's manual edit while Ollama was running.
            if current.name != name:
                return
            if (current.institution or "") != (institution or ""):
                return
            if current.asset_bucket != provisional_bucket:
                return

            if result.bucket_name != provisional_bucket:
                self.repository.update_asset(
                    asset_id,
                    name=current.name,
                    institution=current.institution or "",
                    value_cents=current.current_value_cents,
                    asset_bucket=result.bucket_name,
                    include=current.include_in_net_worth,
                )

            self.repository.upsert_rule(
                asset_key(name, institution),
                name,
                result.bucket_name,
            )

        except Exception:
            # Ollama is optional at runtime. The deterministic heuristic
            # classification remains valid if local AI is unavailable.
            return

    def create_asset(
        self,
        *,
        name: str,
        institution: str,
        value_cents: int,
        requested_bucket: str | None,
        include: bool,
    ) -> tuple[AssetRecord, AssetClassification]:

        # Explicit user-selected category: preserve existing behavior.
        if requested_bucket in ASSET_BUCKETS:
            classification = AssetClassification(
                str(requested_bucket),
                "manual",
                1.0,
            )

            self.repository.upsert_rule(
                asset_key(name, institution),
                name,
                classification.asset_bucket,
            )

            record = self.repository.create_asset(
                name=name,
                institution=institution,
                value_cents=value_cents,
                asset_bucket=classification.asset_bucket,
                include=include,
            )

            return record, classification

        # Auto classification should never make the UI wait for Ollama.
        key = asset_key(name, institution)
        saved_rule = self.repository.get_rule(key) if key else None

        if saved_rule in ASSET_BUCKETS:
            classification = AssetClassification(
                saved_rule,
                "saved_rule",
                1.0,
            )
        else:
            classification = AssetClassification(
                _heuristic_category(name, institution),
                "heuristic_pending_ai",
                0.5,
            )

        record = self.repository.create_asset(
            name=name,
            institution=institution,
            value_cents=value_cents,
            asset_bucket=classification.asset_bucket,
            include=include,
        )

        # Only invoke Ollama when there is no already-learned rule.
        if saved_rule not in ASSET_BUCKETS:
            worker = threading.Thread(
                target=self._refine_asset_category_in_background,
                kwargs={
                    "asset_id": record.id,
                    "name": record.name,
                    "institution": record.institution or "",
                    "provisional_bucket": classification.asset_bucket,
                },
                name=f"pockettrack-asset-classifier-{record.id}",
                daemon=True,
            )
            worker.start()

        return record, classification

    def update_asset(
        self,
        asset_id: int,
        *,
        name: str,
        institution: str,
        value_cents: int,
        asset_bucket: str,
        include: bool,
    ) -> None:
        if asset_bucket not in ASSET_BUCKETS:
            raise ValueError("Unknown asset category.")
        self.repository.update_asset(
            asset_id,
            name=name,
            institution=institution,
            value_cents=value_cents,
            asset_bucket=asset_bucket,
            include=include,
        )
        self.repository.upsert_rule(asset_key(name, institution), name, asset_bucket)
