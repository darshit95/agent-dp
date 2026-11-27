from __future__ import annotations

import re
import time
from collections.abc import Callable
from dataclasses import dataclass

from cardbudget.categorization.provider import Classifier, LLMClassification, ProviderUnavailable
from cardbudget.db.repositories import BucketRepository, MerchantRuleRepository, TransactionRepository
from cardbudget.db.schema import ASSET_BUCKETS

DEFAULT_BATCH_LIMIT = 150
RULE_BATCH_LIMIT = 250
MODEL_CALL_LIMIT = 12
MODEL_BATCH_SECONDS = 35
HIGH_PLAID_CONFIDENCE = {"HIGH", "VERY_HIGH"}
PLAID_BUCKETS = {
    "FOOD_AND_DRINK_GROCERIES": "Grocery",
    "TRANSPORTATION_GAS": "Gas + Car Wash",
    "GENERAL_MERCHANDISE_ONLINE_MARKETPLACES": "Shopping",
    "GENERAL_MERCHANDISE_CLOTHING_AND_ACCESSORIES": "Shopping",
    "GENERAL_MERCHANDISE_DEPARTMENT_STORES": "Shopping",
}


def merchant_key(merchant: str | None, description: str | None) -> str:
    raw = (merchant or description or "").upper().strip()
    return re.sub(r"[^A-Z0-9]+", " ", raw).strip()[:160]


def _memory_is_tight(threshold_percent: float = 90.0) -> bool:
    try:
        import psutil

        return psutil.virtual_memory().percent >= threshold_percent
    except Exception:
        return False


@dataclass(frozen=True)
class CategorizationResult:
    rule_applied: int
    llm_applied: int
    left_uncategorized: int
    ollama_unavailable: bool
    memory_paused: bool = False
    status: str = "complete"


class CategorizationService:
    def __init__(
        self,
        *,
        transactions: TransactionRepository,
        buckets: BucketRepository,
        merchant_rules: MerchantRuleRepository,
        llm: Classifier | None = None,
        pace_seconds: float = 0.0,
    ) -> None:
        self.transactions = transactions
        self.buckets = buckets
        self.merchant_rules = merchant_rules
        self.llm = llm
        self.pace_seconds = pace_seconds

    def apply_rules(self, limit: int = RULE_BATCH_LIMIT) -> tuple[int, int]:
        candidates = self.transactions.list_for_categorization(limit)
        if not candidates:
            return 0, 0
        buckets = {bucket.name.casefold(): bucket.id for bucket in self.buckets.list_active()}
        active_ids = set(buckets.values())
        rules = {rule.merchant_key: rule.bucket_id for rule in self.merchant_rules.list_all() if rule.bucket_id in active_ids}
        applied = []
        unresolved = []

        for row in candidates:
            key = merchant_key(row.merchant_name, row.description)
            if key in rules:
                applied.append((row, rules[key], "merchant_rule", 1.0))
                continue
            mapped = PLAID_BUCKETS.get(row.pfc_detailed or "")
            if mapped and row.pfc_confidence in HIGH_PLAID_CONFIDENCE and mapped.casefold() in buckets:
                applied.append((row, buckets[mapped.casefold()], "plaid_rule", 0.98 if row.pfc_confidence == "VERY_HIGH" else 0.90))
                continue
            # A real Unknown bucket keeps legacy reports consistent while the
            # source marks these rows as eligible for a future AI pass.
            unresolved.append((row, buckets.get("unknown"), "rules_unmatched", 0.0))

        return self.transactions.apply_automatic(applied), self.transactions.apply_automatic(unresolved)

    def apply_model(
        self,
        classifier: Classifier,
        *,
        limit: int = DEFAULT_BATCH_LIMIT,
        local: bool = True,
        source: str = "local_llm",
        still_current: Callable[[], bool] = lambda: True,
        assets=None,
        pace_seconds: float | None = None,
    ) -> CategorizationResult:
        rows = self.transactions.list_for_categorization(limit, model=True)
        buckets = {bucket.name: bucket.id for bucket in self.buckets.list_active()}
        unknown = next((key for name, key in buckets.items() if name.casefold() == "unknown"), None)
        active_ids = set(buckets.values())
        rules = {rule.merchant_key: rule.bucket_id for rule in self.merchant_rules.list_all() if rule.bucket_id in active_ids}
        cache: dict[tuple, LLMClassification] = {}
        deadline = time.monotonic() + MODEL_BATCH_SECONDS
        applied = 0
        left = 0
        rules_applied = 0
        status = "complete"
        pause = self.pace_seconds if pace_seconds is None else pace_seconds

        def classify(key: tuple, predict: Callable[[], LLMClassification]) -> LLMClassification:
            if not still_current():
                raise ProviderUnavailable(status="paused")
            if key not in cache:
                if len(cache) >= MODEL_CALL_LIMIT or time.monotonic() >= deadline:
                    raise ProviderUnavailable(status="batch_limit")
                if local and _memory_is_tight():
                    raise ProviderUnavailable(status="memory_paused")
                if local and cache and pause:
                    time.sleep(pause)
                cache[key] = predict()
                if not still_current():
                    raise ProviderUnavailable(status="paused")
            return cache[key]

        try:
            if assets is not None:
                for asset in assets.list_pending_assets(limit):
                    institution = asset.institution or ""
                    result = classify(
                        ("asset", asset.name, institution if local else ""),
                        lambda: classifier.classify_asset(
                            asset_name=asset.name, institution=institution, buckets=list(ASSET_BUCKETS),
                        ),
                    )
                    category = result.bucket_name if result.bucket_name in ASSET_BUCKETS else asset.asset_bucket
                    assets.apply_asset_classification(asset, category)

            for row in rows:
                rule = rules.get(merchant_key(row.merchant_name, row.description))
                if rule is not None:
                    rules_applied += self.transactions.apply_automatic([(row, rule, "merchant_rule", 1.0)])
                    continue
                merchant = row.merchant_name or ""
                description = row.description if local else ""
                if not local:
                    merchant = re.sub(r"\b\d{5,}\b", "", merchant_key(merchant, None)).strip()
                result = classify(
                    ("transaction", merchant, description, row.pfc_primary, row.pfc_detailed),
                    lambda: classifier.classify(
                        merchant=merchant, description=description,
                        pfc_primary=row.pfc_primary, pfc_detailed=row.pfc_detailed, buckets=list(buckets),
                    ),
                )
                bucket_id = buckets.get(result.bucket_name)
                if bucket_id is None or bucket_id == unknown:
                    left += self.transactions.apply_automatic([(row, unknown, "model_abstained", 0.0)])
                    continue
                applied += self.transactions.apply_automatic([(row, bucket_id, source, result.confidence)])
        except ProviderUnavailable as exc:
            status = exc.status
        if status != "complete":
            left = len(rows) - applied - rules_applied
        return CategorizationResult(
            rules_applied, applied, left,
            status in {"unavailable", "reconnect", "configuration", "invalid_response", "limit_reached"},
            status == "memory_paused", status,
        )

    def categorize_unassigned(self, limit: int = DEFAULT_BATCH_LIMIT) -> CategorizationResult:
        """Run one bounded pass for direct callers and diagnostics."""
        rules, unresolved = self.apply_rules(limit)
        if self.llm is None:
            return CategorizationResult(rules, 0, unresolved, False)
        result = self.apply_model(self.llm, limit=limit)
        return CategorizationResult(
            rules + result.rule_applied, result.llm_applied, result.left_uncategorized,
            result.ollama_unavailable, result.memory_paused, result.status,
        )

    def manual_assign(self, transaction_id: str, bucket_id: int | None, remember_merchant: bool) -> None:
        tx = self.transactions.get(transaction_id)
        if not tx:
            raise ValueError("Unknown transaction.")
        if bucket_id is None:
            self.transactions.assign_bucket(transaction_id, None, source="manual", confidence=1.0)
            return
        bucket = self.buckets.get(bucket_id)
        if not bucket or not bucket.active:
            raise ValueError("Unknown bucket.")
        self.transactions.assign_bucket(transaction_id, bucket_id, source="manual", confidence=1.0)
        if remember_merchant:
            key = merchant_key(tx.merchant_name, tx.description)
            if not key:
                raise ValueError("This transaction has no usable merchant name to remember.")
            self.merchant_rules.upsert(key, tx.merchant_name or tx.description, bucket_id)
