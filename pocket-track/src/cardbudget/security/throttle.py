from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass(frozen=True)
class ThrottleDecision:
    allowed: bool
    retry_after_seconds: int = 0


class LoginThrottle:
    """Small in-memory throttle suitable for a single local process/user."""

    def __init__(
        self,
        max_failures: int = 5,
        window_seconds: int = 300,
        lockout_seconds: int = 30,
    ) -> None:
        self.max_failures = max_failures
        self.window_seconds = window_seconds
        self.lockout_seconds = lockout_seconds
        self._failures: dict[str, deque[float]] = defaultdict(deque)
        self._locked_until: dict[str, float] = {}
        self._lock = threading.Lock()

    @staticmethod
    def _key(username: str, remote_addr: str) -> str:
        return f"{remote_addr}|{username.strip().casefold()}"

    def check(self, username: str, remote_addr: str, now: float | None = None) -> ThrottleDecision:
        current = time.monotonic() if now is None else now
        key = self._key(username, remote_addr)
        with self._lock:
            locked_until = self._locked_until.get(key, 0)
            if current < locked_until:
                return ThrottleDecision(False, max(1, int(locked_until - current + 0.999)))
            if locked_until:
                self._locked_until.pop(key, None)
            self._trim(key, current)
            return ThrottleDecision(True, 0)

    def record_failure(self, username: str, remote_addr: str, now: float | None = None) -> None:
        current = time.monotonic() if now is None else now
        key = self._key(username, remote_addr)
        with self._lock:
            self._trim(key, current)
            failures = self._failures[key]
            failures.append(current)
            if len(failures) >= self.max_failures:
                self._locked_until[key] = current + self.lockout_seconds
                failures.clear()

    def record_success(self, username: str, remote_addr: str) -> None:
        key = self._key(username, remote_addr)
        with self._lock:
            self._failures.pop(key, None)
            self._locked_until.pop(key, None)

    def _trim(self, key: str, current: float) -> None:
        failures = self._failures.get(key)
        if not failures:
            return
        cutoff = current - self.window_seconds
        while failures and failures[0] < cutoff:
            failures.popleft()
        if not failures:
            self._failures.pop(key, None)
