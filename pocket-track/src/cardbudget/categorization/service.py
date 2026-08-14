from __future__ import annotations

import re
import time
from dataclasses import dataclass

from cardbudget.categorization.ollama import OllamaClassifierClient, OllamaUnavailable
from cardbudget.db.repositories import BucketRepository, MerchantRuleRepository, TransactionRepository

# Shared cap for how many unassigned transactions a single categorization pass
# will touch. Local LLM classification is one blocking HTTP call per transaction
# on constrained hardware (see cli.py, web/routes.py, plaid/routes.py call sites) -
# a large limit turns one sync into a long, uninterrupted burst of full-tilt
# inference. Anything left over is simply picked up by the next sync, since
# list_unassigned() is re-queried every time - nothing is lost by capping this.
DEFAULT_BATCH_LIMIT = 150


def merchant_key(merchant: str | None, description: str | None) -> str:
    raw = (merchant or description or "").upper().strip()
    raw = re.sub(r"[^A-Z0-9]+", " ", raw)
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw[:160]


def _memory_is_tight(threshold_percent: float = 90.0) -> bool:
    """Best-effort local memory-pressure check. Fails soft: if psutil isn't
    installed or the check raises for any reason, assume memory is fine rather
    than block categorization on a diagnostic that couldn't run."""
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


class CategorizationService:
    def __init__(
        self,
        *,
        transactions: TransactionRepository,
        buckets: BucketRepository,
        merchant_rules: MerchantRuleRepository,
        llm: OllamaClassifierClient,
        pace_seconds: float = 0.0,
    ) -> None:
        self.transactions = transactions
        self.buckets = buckets
        self.merchant_rules = merchant_rules
        self.llm = llm
        self.pace_seconds = pace_seconds

    def categorize_unassigned(self, limit: int = DEFAULT_BATCH_LIMIT) -> CategorizationResult:
        candidates = self.transactions.list_unassigned(limit)
        active_buckets = self.buckets.list_active()
        by_name = {b.name: b.id for b in active_buckets}
        names = list(by_name)
        rule_applied = 0
        llm_applied = 0
        left = 0
        unavailable = False
        memory_paused = False

        unknown_id = by_name.get("Unknown")

        for tx in candidates:
            key = merchant_key(tx.merchant_name, tx.description)
            rule = self.merchant_rules.get_by_key(key) if key else None
            if rule:
                self.transactions.assign_bucket(
                    tx.transaction_id, rule.bucket_id, source="merchant_rule", confidence=1.0
                )
                rule_applied += 1
                continue

            if not unavailable and not memory_paused and _memory_is_tight():
                # Stop calling the local model for the rest of this batch rather
                # than push an already-strained machine further. The remaining
                # transactions fall back to Unknown, same as when Ollama is down,
                # and get a real classification attempt on the next sync.
                memory_paused = True

            if unavailable or memory_paused:
                if unknown_id is not None:
                    self.transactions.assign_bucket(tx.transaction_id, unknown_id, source="unknown_fallback", confidence=0.0)
                left += 1
                continue
            if self.pace_seconds:
                time.sleep(self.pace_seconds)
            try:
                result = self.llm.classify(
                    merchant=tx.merchant_name or "",
                    description=tx.description,
                    pfc_primary=tx.pfc_primary,
                    pfc_detailed=tx.pfc_detailed,
                    buckets=names,
                )
            except OllamaUnavailable:
                unavailable = True
                left += 1
                continue

            if result.bucket_name and result.bucket_name in by_name:
                self.transactions.assign_bucket(
                    tx.transaction_id,
                    by_name[result.bucket_name],
                    source="local_llm",
                    confidence=result.confidence,
                )
                llm_applied += 1
            else:
                if unknown_id is not None:
                    self.transactions.assign_bucket(tx.transaction_id, unknown_id, source="unknown_fallback", confidence=0.0)
                else:
                    self.transactions.mark_uncategorized(tx.transaction_id, source="local_llm")
                left += 1

        return CategorizationResult(
            rule_applied=rule_applied,
            llm_applied=llm_applied,
            left_uncategorized=left,
            ollama_unavailable=unavailable,
            memory_paused=memory_paused,
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
