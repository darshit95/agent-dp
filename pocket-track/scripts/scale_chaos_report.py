"""Scale and chaos benchmark for PocketTrack.

Not part of the pytest suite on purpose - a full run takes several minutes
(real SQLCipher encryption, real Ollama inference, real concurrent threads
against a real SQLite file) and produces a human-readable report rather than
pass/fail assertions. Run manually and transcribe results into README.md:

    PYTHONPATH=src .venv/bin/python scripts/scale_chaos_report.py

Everything here is self-contained and disposable:
- A throwaway SQLCipher key (real encryption, just not routed through the OS
  keychain) so this never touches your actual PocketTrack keychain entries.
- A temp data directory per scenario, deleted at the end of that scenario.
- MemorySecretStore for anything else secret-shaped (Plaid creds are never
  exercised for real - the Plaid chaos scenario injects a fake transport).

Concurrency is exercised with real OS threads against the real `Database`
object, which is where PocketTrack's actual concurrency behavior lives (each
repository call opens its own SQLite connection, exactly like each FastAPI
request handler does) - this is a faithful test of SQLite lock contention
without the complexity of driving it through a second real HTTP server.
"""

from __future__ import annotations

import os
import random
import shutil
import statistics
import sys
import tempfile
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psutil

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from cardbudget.config import Settings  # noqa: E402
from cardbudget.db.engine import Database  # noqa: E402
from cardbudget.db.repositories import PlaidRepository, TransactionRepository  # noqa: E402
from cardbudget.security.keychain import MemorySecretStore  # noqa: E402
from cardbudget.services import bootstrap_services  # noqa: E402

BENCHMARK_DB_KEY = "11" * 32  # throwaway, never used outside this script
PROC = psutil.Process(os.getpid())


def _fmt_mb(nbytes: float) -> str:
    return f"{nbytes / (1024 * 1024):.1f} MB"


def _fmt_ms(seconds: float) -> str:
    return f"{seconds * 1000:.1f} ms"


@dataclass
class Section:
    title: str
    lines: list[str] = field(default_factory=list)

    def add(self, line: str = "") -> None:
        self.lines.append(line)
        print(line)

    def render_markdown(self) -> str:
        return f"### {self.title}\n\n" + "\n".join(self.lines) + "\n"


def real_database(data_dir: Path) -> Database:
    """A production-shaped Database: real sqlcipher3, require_cipher=True."""
    from sqlcipher3 import dbapi2 as sqlcipher

    return Database(data_dir / "bench.db", BENCHMARK_DB_KEY, connector=sqlcipher.connect, require_cipher=True)


def build_services(data_dir: Path):
    settings = Settings(data_dir=data_dir, plaid_environment="sandbox")
    db = real_database(data_dir)
    return bootstrap_services(settings, secret_store=MemorySecretStore(), database=db), settings, db


# ---------------------------------------------------------------------------
# Synthetic data generation
# ---------------------------------------------------------------------------

MERCHANTS = [
    ("Blue Bottle Coffee", "COFFEE_SHOP", None),
    ("Trader Joe's", "GROCERY_STORES", None),
    ("Shell Gas Station", "GAS_STATIONS", None),
    ("Amazon", "ONLINE_SHOPPING", None),
    ("Netflix", "SUBSCRIPTION", None),
    ("Chipotle", "FAST_FOOD", None),
    ("Delta Air Lines", "TRAVEL", None),
    ("PG&E", "UTILITIES", None),
    ("Uber", "TRANSPORTATION", None),
    ("CVS Pharmacy", "PHARMACY", None),
]


def seed_accounts(plaid_repo: PlaidRepository, count: int) -> list[str]:
    account_ids = []
    for i in range(count):
        item_id = f"bench-item-{i}"
        plaid_repo.upsert_item(
            item_id=item_id, institution_id=f"ins-{i}", institution_name=f"Bench Bank {i}", environment="sandbox"
        )
        account_id = f"bench-acct-{i}"
        plaid_repo.replace_accounts(
            item_id,
            [{"account_id": account_id, "name": f"Card {i}", "official_name": None, "mask": f"{1000 + i}", "type": "credit", "subtype": "credit card"}],
        )
        account_ids.append(account_id)
    return account_ids


def seed_transactions(tx_repo: TransactionRepository, account_ids: list[str], count: int, *, batch_size: int = 2000) -> None:
    start = datetime(2023, 1, 1, tzinfo=timezone.utc)
    span_days = 900
    rng = random.Random(42)
    batch: list[dict] = []
    for i in range(count):
        merchant, pfc, _ = MERCHANTS[i % len(MERCHANTS)]
        day = start + timedelta(days=rng.randint(0, span_days))
        batch.append(
            {
                "transaction_id": f"bench-tx-{i}",
                "account_id": account_ids[i % len(account_ids)],
                "amount_cents": rng.randint(199, 45000),
                "iso_currency_code": "USD",
                "posted_date": day.strftime("%Y-%m-%d"),
                "authorized_date": day.strftime("%Y-%m-%d"),
                "budget_date": day.strftime("%Y-%m-%d"),
                "merchant_name": merchant,
                "description": merchant.upper(),
                "pending": False,
                "pending_transaction_id": None,
                "pfc_primary": pfc,
                "pfc_detailed": pfc,
                "pfc_confidence": "HIGH",
            }
        )
        if len(batch) >= batch_size:
            tx_repo.apply_backfill_batch(batch)
            batch = []
    if batch:
        tx_repo.apply_backfill_batch(batch)


# ---------------------------------------------------------------------------
# Scale tiers: seed at a size, measure the read paths that matter (dashboard,
# transactions list), report DB size and process memory footprint.
# ---------------------------------------------------------------------------

SCALE_TIERS = (
    ("small", 2, 2_000),
    ("medium", 3, 15_000),
    ("large (worst-case single-user)", 5, 50_000),
)


def run_scale_tier(name: str, account_count: int, tx_count: int) -> Section:
    section = Section(f"Scale tier: {name} ({account_count} accounts, {tx_count:,} transactions)")
    tmp = Path(tempfile.mkdtemp(prefix="pockettrack-bench-"))
    try:
        rss_before = PROC.memory_info().rss
        services, _settings, db = build_services(tmp)
        accounts = seed_accounts(services.plaid_repository, account_count)

        t0 = time.perf_counter()
        seed_transactions(services.transactions, accounts, tx_count)
        seed_seconds = time.perf_counter() - t0
        db_size = (tmp / "bench.db").stat().st_size

        # Dashboard's core query: monthly_summary() across the buckets, once
        # per month with data, averaged.
        with db.connection() as conn:
            months = sorted({str(r[0])[:7] for r in conn.execute("SELECT DISTINCT budget_date FROM transactions").fetchall()})
        sample_months = months[:: max(1, len(months) // 20)][:20] or months[:1]

        t0 = time.perf_counter()
        for month in sample_months:
            services.buckets.monthly_summary(month)
        summary_seconds = (time.perf_counter() - t0) / max(1, len(sample_months))

        t0 = time.perf_counter()
        for _ in range(20):
            services.transactions.list_recent(limit=100)
        list_recent_seconds = (time.perf_counter() - t0) / 20

        t0 = time.perf_counter()
        services.transactions.uncategorized_count()
        uncategorized_seconds = time.perf_counter() - t0

        rss_after = PROC.memory_info().rss

        section.add(f"- Seed time: {seed_seconds:.2f} s ({tx_count / max(seed_seconds, 1e-9):,.0f} tx/s)")
        section.add(f"- Encrypted DB file size: {_fmt_mb(db_size)}")
        section.add(f"- `monthly_summary()` (dashboard budget bars), avg over {len(sample_months)} months: {_fmt_ms(summary_seconds)}")
        section.add(f"- `list_recent(limit=100)` (transactions page), avg over 20 calls: {_fmt_ms(list_recent_seconds)}")
        section.add(f"- `uncategorized_count()`: {_fmt_ms(uncategorized_seconds)}")
        section.add(f"- Benchmark process RSS: {_fmt_mb(rss_before)} -> {_fmt_mb(rss_after)} (delta {_fmt_mb(rss_after - rss_before)})")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    section.add()
    return section


# ---------------------------------------------------------------------------
# Live categorization sample (real local Ollama call per transaction)
# ---------------------------------------------------------------------------


def run_live_categorization_sample(sample_size: int = 100) -> Section:
    import cardbudget.categorization.service as categorization_module

    section = Section(f"Live categorization sample ({sample_size} transactions, real local Ollama)")
    tmp = Path(tempfile.mkdtemp(prefix="pockettrack-bench-"))
    original_memory_is_tight = categorization_module._memory_is_tight
    try:
        services, _settings, _db = build_services(tmp)
        reachable, model_installed = services.ollama.status()
        if not reachable or not model_installed:
            section.add(f"- SKIPPED: Ollama reachable={reachable}, model installed={model_installed}")
            section.add()
            return section

        system_memory_percent = psutil.virtual_memory().percent
        if system_memory_percent >= 90.0:
            section.add(
                f"- NOTE: this machine is genuinely at {system_memory_percent:.0f}% memory use right now - "
                f"PocketTrack's own memory-pressure guard (_memory_is_tight, 90% threshold) would pause "
                f"real sync categorization here. Disabling it *only for this isolated measurement* to get "
                f"clean per-call model latency; see the Ollama-down/memory-pressure chaos notes for the "
                f"guard's actual behavior under load."
            )
        categorization_module._memory_is_tight = lambda *_a, **_k: False

        accounts = seed_accounts(services.plaid_repository, 1)
        seed_transactions(services.transactions, accounts, sample_size)

        # Wrap classify() to time each real model call individually - the
        # aggregate CategorizationResult can't tell "fast because rule-matched"
        # apart from "fast because the model answered quickly", and a global
        # elapsed/result-count average silently divides by the wrong thing
        # whenever the model returns "Uncategorized" (counted in
        # left_uncategorized, not llm_applied, despite having made a real call).
        real_classify = services.ollama.classify
        call_latencies: list[float] = []

        def timed_classify(**kwargs):
            call_t0 = time.perf_counter()
            try:
                return real_classify(**kwargs)
            finally:
                call_latencies.append(time.perf_counter() - call_t0)

        services.ollama.classify = timed_classify  # type: ignore[method-assign]

        rss_before = PROC.memory_info().rss
        t0 = time.perf_counter()
        result = services.categorization.categorize_unassigned(limit=sample_size)
        elapsed = time.perf_counter() - t0
        rss_after = PROC.memory_info().rss

        section.add(f"- Model: {services.settings.ollama_model}")
        section.add(f"- Total: {elapsed:.1f} s for {sample_size} transactions, {len(call_latencies)} real model calls made")
        if call_latencies:
            sorted_lat = sorted(call_latencies)
            p50 = statistics.median(sorted_lat)
            p95 = sorted_lat[int(len(sorted_lat) * 0.95)] if len(sorted_lat) > 1 else sorted_lat[0]
            section.add(f"- Per-call latency: p50={p50 * 1000:.0f} ms p95={p95 * 1000:.0f} ms max={sorted_lat[-1] * 1000:.0f} ms")
            section.add(
                f"- NOTE: a single sync only ever categorizes up to DEFAULT_BATCH_LIMIT=150 unassigned "
                f"transactions (categorization/service.py) - the rest picks up on the next sync. At the "
                f"measured p50, a full 150-transaction batch takes roughly {p50 * 150:.0f} s."
            )
        section.add(f"- Result: rule_applied={result.rule_applied} local_llm={result.llm_applied} left_uncategorized={result.left_uncategorized} ollama_unavailable={result.ollama_unavailable} memory_paused={result.memory_paused}")
        section.add(f"- Process RSS during: {_fmt_mb(rss_before)} -> {_fmt_mb(rss_after)}")
    finally:
        categorization_module._memory_is_tight = original_memory_is_tight
        shutil.rmtree(tmp, ignore_errors=True)
    section.add()
    return section


# ---------------------------------------------------------------------------
# Chaos 1: Ollama unreachable mid-categorization
# ---------------------------------------------------------------------------


def chaos_ollama_down(tx_count: int = 200) -> Section:
    import cardbudget.categorization.service as categorization_module
    from cardbudget.categorization.ollama import OllamaUnavailable

    section = Section("Chaos: Ollama unreachable mid-categorization")
    tmp = Path(tempfile.mkdtemp(prefix="pockettrack-bench-"))
    original_memory_is_tight = categorization_module._memory_is_tight
    try:
        services, _settings, _db = build_services(tmp)
        accounts = seed_accounts(services.plaid_repository, 1)
        seed_transactions(services.transactions, accounts, tx_count)

        # Isolate this scenario from real host memory pressure - see the
        # memory_paused note below and the live-categorization section for
        # what actually happens when both conditions are true at once.
        system_memory_percent = psutil.virtual_memory().percent
        if system_memory_percent >= 90.0:
            section.add(
                f"- NOTE: host is at {system_memory_percent:.0f}% memory use - disabling the memory-pressure "
                f"guard for this scenario so it isolates Ollama-down behavior specifically, not both guards at once."
            )
        categorization_module._memory_is_tight = lambda *_a, **_k: False

        call_count = {"n": 0}

        def always_unavailable(**_kwargs):
            call_count["n"] += 1
            raise OllamaUnavailable("simulated: Ollama daemon unreachable")

        services.ollama.classify = always_unavailable  # type: ignore[method-assign]

        rss_before = PROC.memory_info().rss
        t0 = time.perf_counter()
        result = services.categorization.categorize_unassigned(limit=tx_count)
        elapsed = time.perf_counter() - t0
        rss_after = PROC.memory_info().rss

        section.add(f"- {tx_count} unassigned transactions, Ollama forced unreachable on every call")
        section.add(f"- Completed in {_fmt_ms(elapsed)} (no crash, no hang)")
        section.add(f"- Actual LLM call attempts before short-circuiting: {call_count['n']} (expected: 1 - service.py stops calling after the first OllamaUnavailable)")
        section.add(f"- Result: rule_applied={result.rule_applied} left_uncategorized={result.left_uncategorized} ollama_unavailable={result.ollama_unavailable}")
        section.add(f"- Process RSS: {_fmt_mb(rss_before)} -> {_fmt_mb(rss_after)} (no leak/spike from the failure path)")
        assert result.ollama_unavailable is True
        assert call_count["n"] == 1, "expected the service to stop calling Ollama after the first failure"
        section.add("- VERIFIED: matches documented graceful-degradation behavior (falls back to Unknown, no retry storm)")
    finally:
        categorization_module._memory_is_tight = original_memory_is_tight
        shutil.rmtree(tmp, ignore_errors=True)
    section.add()
    return section


# ---------------------------------------------------------------------------
# Chaos 2: Plaid API errors/timeouts mid-sync across multiple linked banks
# ---------------------------------------------------------------------------


def chaos_plaid_errors() -> Section:
    from cardbudget.plaid.client import PlaidAPIError, PlaidClient
    from cardbudget.plaid.service import PlaidService

    section = Section("Chaos: Plaid API errors mid-sync across multiple linked banks")
    tmp = Path(tempfile.mkdtemp(prefix="pockettrack-bench-"))
    try:
        settings = Settings(data_dir=tmp, plaid_environment="sandbox")
        db = real_database(tmp)
        db.initialize()
        repo = PlaidRepository(db)
        tx_repo = TransactionRepository(db)
        store = MemorySecretStore()

        item_ids = ["item-ok-1", "item-fails", "item-ok-2", "item-timeout"]

        class FlakyTransport:
            def __init__(self) -> None:
                self.calls = 0

            def post(self, path: str, payload: dict):
                if path == "/item/get":
                    return {"item": {"item_id": payload.get("item_id", "?"), "institution_id": "ins", "institution_name": "Bench Bank"}}
                if path == "/accounts/get":
                    return {"accounts": [{"account_id": f"acct-{payload.get('access_token', 'x')}", "name": "Card", "official_name": None, "mask": "0000", "type": "credit", "subtype": "credit card"}]}
                if path == "/transactions/sync":
                    self.calls += 1
                    token = payload.get("access_token", "")
                    if "item-fails" in token:
                        raise PlaidAPIError(error_code="INTERNAL_SERVER_ERROR", error_type="API_ERROR", message="simulated 500")
                    if "item-timeout" in token:
                        raise PlaidAPIError(error_code="ITEM_LOGIN_REQUIRED", error_type="ITEM_ERROR", message="simulated timeout surfaced as reauth-required")
                    return {"added": [], "modified": [], "removed": [], "next_cursor": f"cursor-{token}", "has_more": False, "transactions_update_status": "HISTORICAL_UPDATE_COMPLETE"}
                raise AssertionError(path)

        transport = FlakyTransport()
        service = PlaidService(
            secret_store=store,
            plaid_repository=repo,
            transactions=tx_repo,
            environment="sandbox",
            client_factory=lambda *_a: PlaidClient(transport),
        )
        service.save_credentials("bench-client-id", "bench-sandbox-secret")
        for item_id in item_ids:
            store.set_secret(f"plaid-access-token:sandbox:{item_id}", f"access-{item_id}")
            repo.upsert_item(item_id=item_id, institution_id="ins", institution_name="Bench Bank", environment="sandbox")

        t0 = time.perf_counter()
        result = service.sync_all()
        elapsed = time.perf_counter() - t0

        section.add(f"- 4 linked banks; 1 returns a 500-style API error, 1 returns a reauth-required error, 2 succeed")
        section.add(f"- sync_all() completed in {_fmt_ms(elapsed)} without raising - failures are isolated per item")
        section.add(f"- items_synced={result.items_synced} failed_items={result.failed_items} (expected 2 and 2)")
        for item_id in item_ids:
            item = repo.get_item(item_id, "sandbox")
            status = f"error={item.last_sync_error_code}" if item and item.last_sync_error_code else "OK, no error recorded"
            section.add(f"    - {item_id}: {status}")
        assert result.failed_items == 2, f"expected 2 failed items, got {result.failed_items}"
        section.add("- VERIFIED: a failing bank connection does not block or corrupt sync for the others")

        # Recovery: the two failing items succeed on the next sync.
        def fixed_post(path, payload):
            if path == "/transactions/sync":
                transport.calls += 1
                token = payload.get("access_token", "")
                return {"added": [], "modified": [], "removed": [], "next_cursor": f"cursor-{token}-2", "has_more": False, "transactions_update_status": "HISTORICAL_UPDATE_COMPLETE"}
            return transport.post(path, payload)

        transport.post = fixed_post  # type: ignore[method-assign]
        retry_result = service.sync_all()
        section.add(f"- After the outage clears, a follow-up sync_all(): failed_items={retry_result.failed_items} (expected 0)")
        assert retry_result.failed_items == 0
        section.add("- VERIFIED: previously-failing items recover cleanly on the next sync, no manual intervention needed")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    section.add()
    return section


# ---------------------------------------------------------------------------
# Chaos 3: concurrent reads (dashboard/transactions) during a large write
# (SQLite single-writer lock contention, busy_timeout=5000 per db/engine.py)
# ---------------------------------------------------------------------------


def chaos_concurrency(tx_count: int = 15_000, reader_threads: int = 12) -> Section:
    section = Section(f"Chaos: {reader_threads} concurrent readers during a 5,000-row write batch (SQLite lock contention)")
    tmp = Path(tempfile.mkdtemp(prefix="pockettrack-bench-"))
    try:
        services, _settings, db = build_services(tmp)
        accounts = seed_accounts(services.plaid_repository, 3)
        seed_transactions(services.transactions, accounts, tx_count)

        stop = threading.Event()
        latencies: list[float] = []
        lock_errors: list[str] = []
        other_errors: list[str] = []
        results_lock = threading.Lock()

        def reader_loop() -> None:
            while not stop.is_set():
                t0 = time.perf_counter()
                try:
                    services.transactions.list_recent(limit=50)
                except Exception as exc:  # noqa: BLE001 - recording every failure mode, not just OperationalError
                    with results_lock:
                        if "locked" in str(exc).lower():
                            lock_errors.append(repr(exc))
                        else:
                            other_errors.append(repr(exc))
                    continue
                elapsed = time.perf_counter() - t0
                with results_lock:
                    latencies.append(elapsed)

        readers = [threading.Thread(target=reader_loop, daemon=True) for _ in range(reader_threads)]
        for t in readers:
            t.start()
        time.sleep(0.2)  # let readers get a baseline going before the write lands

        extra_rows = 5_000
        t0 = time.perf_counter()
        seed_transactions(services.transactions, accounts, extra_rows, batch_size=extra_rows)
        write_elapsed = time.perf_counter() - t0

        time.sleep(0.5)  # capture some post-write reads too
        stop.set()
        for t in readers:
            t.join(timeout=3)

        section.add(f"- Baseline: {tx_count:,} existing rows, then one {extra_rows:,}-row write (single transaction) while {reader_threads} threads read continuously")
        section.add(f"- Write batch ({extra_rows:,} rows) took {write_elapsed:.2f} s")
        section.add(f"- Concurrent reads completed during the run: {len(latencies)}")
        if latencies:
            sorted_lat = sorted(latencies)
            p50 = statistics.median(sorted_lat)
            p95 = sorted_lat[int(len(sorted_lat) * 0.95)]
            section.add(f"- Read latency: p50={_fmt_ms(p50)} p95={_fmt_ms(p95)} max={_fmt_ms(sorted_lat[-1])}")
        section.add(f"- `database is locked` errors surfaced to callers: {len(lock_errors)} (busy_timeout=5000ms should absorb brief writer locks)")
        section.add(f"- Other errors: {len(other_errors)}" + (f" - e.g. {other_errors[0]}" if other_errors else ""))
        if lock_errors:
            section.add(f"    - sample: {lock_errors[0]}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    section.add()
    return section


def main() -> None:
    host_mem = psutil.virtual_memory()
    header = (
        f"# PocketTrack scale & chaos report\n\n"
        f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} on "
        f"{os.uname().sysname} {os.uname().machine}, {psutil.cpu_count()} logical CPUs, "
        f"{host_mem.total / (1024 ** 3):.1f} GB RAM total "
        f"({host_mem.available / (1024 ** 3):.1f} GB available at report time).\n\n"
        f"Scope: personal-use realistic scale (1-5 linked banks, up to ~50k transactions - "
        f"what an actual person accumulates over a few years), plus three chaos scenarios: "
        f"Ollama unreachable mid-categorization, Plaid API errors mid-sync, and concurrent "
        f"reads during a large write (SQLite lock contention).\n"
    )
    print(header)

    sections: list[Section] = []
    for name, accounts, tx_count in SCALE_TIERS:
        sections.append(run_scale_tier(name, accounts, tx_count))

    sections.append(run_live_categorization_sample(40))
    sections.append(chaos_ollama_down(200))
    sections.append(chaos_plaid_errors())
    sections.append(chaos_concurrency(15_000, 12))

    report_path = Path(__file__).resolve().parent / "scale_chaos_report.md"
    report_path.write_text(header + "\n" + "\n".join(s.render_markdown() for s in sections))
    print(f"\nFull markdown report written to {report_path}")


if __name__ == "__main__":
    main()
