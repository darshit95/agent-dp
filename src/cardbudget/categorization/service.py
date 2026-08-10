from __future__ import annotations

import re
from dataclasses import dataclass

from cardbudget.categorization.ollama import OllamaClassifierClient, OllamaUnavailable
from cardbudget.db.repositories import BucketRepository, MerchantRuleRepository, TransactionRepository


def merchant_key(merchant: str | None, description: str | None) -> str:
    raw = (merchant or description or "").upper().strip()
    raw = re.sub(r"[^A-Z0-9]+", " ", raw)
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw[:160]


@dataclass(frozen=True)
class CategorizationResult:
    rule_applied: int
    llm_applied: int
    left_uncategorized: int
    ollama_unavailable: bool


class CategorizationService:
    def __init__(
        self,
        *,
        transactions: TransactionRepository,
        buckets: BucketRepository,
        merchant_rules: MerchantRuleRepository,
        llm: OllamaClassifierClient,
    ) -> None:
        self.transactions = transactions
        self.buckets = buckets
        self.merchant_rules = merchant_rules
        self.llm = llm

    def categorize_unassigned(self, limit: int = 200) -> CategorizationResult:
        candidates = self.transactions.list_unassigned(limit)
        active_buckets = self.buckets.list_active()
        by_name = {b.name: b.id for b in active_buckets}
        names = list(by_name)
        rule_applied = 0
        llm_applied = 0
        left = 0
        unavailable = False

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

            if unavailable:
                if unknown_id is not None:
                    self.transactions.assign_bucket(tx.transaction_id, unknown_id, source="unknown_fallback", confidence=0.0)
                left += 1
                continue
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

        return CategorizationResult(rule_applied, llm_applied, left, unavailable)

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
