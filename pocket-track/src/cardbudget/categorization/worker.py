from __future__ import annotations

import logging
import threading
import time
import uuid

import httpx

from cardbudget.categorization.profiles import ProviderProfiles
from cardbudget.categorization.provider import ProviderUnavailable
from cardbudget.categorization.service import RULE_BATCH_LIMIT, CategorizationService
from cardbudget.db.repositories import NetWorthRepository, to_iso, utc_now

logger = logging.getLogger(__name__)
LEASE_SECONDS = 180
POLL_SECONDS = 10
AUTOMATIC = 1
MANUAL = 2
JOB_MESSAGES = {
    "queued": "Categorization is queued.",
    "running": "Categorization is running in the background.",
    "complete": "Last categorization pass completed.",
    "batch_limit": "Batch limit reached. Run categorization again to continue.",
    "memory_paused": "Local AI paused because memory was low. Results already saved are available.",
    "limit_reached": "Provider limit reached. Remaining work can be retried.",
    "reconnect": "Reconnect your provider before running AI again.",
    "configuration": "Check the provider configuration and model ID.",
    "invalid_response": "The model returned an unusable result. Remaining work can be retried.",
    "unavailable": "Categorization could not finish. Remaining work can be retried.",
}


class CategorizationWorker:
    """Durable work is coalesced in SQLCipher. An idle worker sleeps between checks."""

    def __init__(
        self, service: CategorizationService, profiles: ProviderProfiles,
        assets: NetWorthRepository, chatgpt,
    ) -> None:
        self.service = service
        self.profiles = profiles
        self.assets = assets
        self.chatgpt = chatgpt
        self.db = profiles.db
        self._wake = threading.Event()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._model_lock = threading.Lock()

    def request(self, *, manual: bool = False) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                "UPDATE categorization_work SET requested = MAX(requested, ?) WHERE id = 1",
                (MANUAL if manual else AUTOMATIC,),
            )
        self._wake.set()

    def status(self) -> str:
        with self.db.connection() as conn:
            row = conn.execute(
                "SELECT requested, running, expires_at, status FROM categorization_work WHERE id = 1"
            ).fetchone()
        if row[1] and row[2] > time.time():
            return "running"
        return "queued" if row[0] or row[1] else str(row[3])

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="pockettrack-classification", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._wake.set()
        if self._thread is not None:
            self._thread.join(timeout=2)

    def _loop(self) -> None:
        while not self._stop.is_set():
            self._wake.clear()
            try:
                if self.run_once():
                    continue
            except Exception:
                # Provider responses and credentials are intentionally absent from logs.
                logger.error("PocketTrack categorization worker could not access local work.")
            self._wake.wait(POLL_SECONDS)

    def _claim(self) -> tuple[str, int] | None:
        now = time.time()
        with self.db.connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM categorization_work WHERE id = 1 AND expires_at <= ? AND MAX(requested, running) > 0",
                (now,),
            ).fetchone()
        if not row:
            return None
        owner = uuid.uuid4().hex
        with self.db.transaction() as conn:
            claimed = conn.execute(
                """
                UPDATE categorization_work
                SET running = MAX(requested, running), requested = 0, owner = ?, expires_at = ?, status = 'running'
                WHERE id = 1 AND expires_at <= ? AND MAX(requested, running) > 0
                """,
                (owner, now + LEASE_SECONDS, now),
            ).rowcount
            if claimed:
                running = conn.execute("SELECT running FROM categorization_work WHERE id = 1").fetchone()[0]
                return owner, int(running)
        return None

    def _finish(self, owner: str, status: str, *, more: int = 0) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                """
                UPDATE categorization_work
                SET requested = MAX(requested, ?), running = 0, owner = NULL, expires_at = 0, status = ?
                WHERE id = 1 AND owner = ?
                """,
                (more, status, owner),
            )

    def run_once(self) -> bool:
        claim = self._claim()
        if claim is None:
            return False
        owner, requested = claim
        status = "complete"
        more = 0
        try:
            for _ in range(4):
                self.service.apply_rules()
                if self._stop.is_set():
                    more = requested
                    break
                if not self.service.transactions.list_for_categorization(1):
                    break
                more = requested
            else:
                return True

            if self._stop.is_set():
                return False
            more = 0
            profile = self.profiles.get()
            if profile.provider == "rules" or profile.paused:
                status = "paused" if profile.paused else "complete"
                return True
            if profile.is_cloud and requested != MANUAL and not profile.scheduled_cloud:
                return True
            with self._model_lock:
                result = self._apply_model(profile, owner, requested)
            status = result.status
            if self._stop.is_set():
                more = requested
        except ProviderUnavailable as exc:
            status = exc.status
        except Exception:
            logger.error("PocketTrack categorization pass failed.")
            status = "unavailable"
        finally:
            self._finish(owner, status, more=more)
        return True

    def _apply_model(self, profile, owner: str, requested: int):
        def still_current() -> bool:
            if self._stop.is_set() or self.profiles.get() != profile:
                return False
            with self.db.connection() as conn:
                return conn.execute(
                    "SELECT 1 FROM categorization_work WHERE id = 1 AND owner = ? AND running = ? AND expires_at > ?",
                    (owner, requested, time.time()),
                ).fetchone() is not None

        with httpx.Client(timeout=httpx.Timeout(15, connect=3), trust_env=False) as http:
            client = self.profiles.client(profile, http, self.chatgpt)
            return self.service.apply_model(
                client,
                limit=RULE_BATCH_LIMIT,
                local=not profile.is_cloud,
                source="cloud_llm" if profile.is_cloud else "local_llm",
                still_current=still_current,
                assets=self.assets if not profile.is_cloud or profile.cloud_assets else None,
            )

    def test_connection(self) -> None:
        if not self._model_lock.acquire(blocking=False):
            raise ProviderUnavailable("Categorization is running. Test the connection after this pass.")
        try:
            self._test_connection()
        finally:
            self._model_lock.release()

    def _test_connection(self) -> None:
        profile = self.profiles.get()
        with httpx.Client(timeout=httpx.Timeout(15, connect=3), trust_env=False) as http:
            client = self.profiles.client(profile, http, self.chatgpt)
            client.classify(
                merchant="Example Grocery", description="Synthetic connection test",
                pfc_primary="FOOD_AND_DRINK", pfc_detailed="FOOD_AND_DRINK_GROCERIES",
                buckets=["Grocery", "Shopping"],
            )
        self.profiles.set_last_test(profile, to_iso(utc_now()))
