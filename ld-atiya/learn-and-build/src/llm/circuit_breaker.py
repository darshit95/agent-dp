"""Per-provider circuit breaker.

::

    CLOSED (normal) --failures >= threshold--> OPEN
       ^                                         |
       |                                  cooldown elapsed
       |                                         v
       +---------------- success ---------- HALF_OPEN
                                                  |
                                              failure
                                                  v
                                                 OPEN

While OPEN, `allow_request()` returns False so the gateway skips the
provider immediately instead of waiting out a timeout on a call that is
very likely to fail (see complete-learning.md "Pattern 2: Circuit
Breaker").
"""

from __future__ import annotations

import time
from enum import Enum
from threading import Lock


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(self, *, failure_threshold: int = 5, reset_timeout_s: float = 60.0) -> None:
        self._failure_threshold = failure_threshold
        self._reset_timeout_s = reset_timeout_s
        self._failure_count = 0
        self._state = CircuitState.CLOSED
        self._opened_at: float | None = None
        self._lock = Lock()

    @property
    def state(self) -> CircuitState:
        with self._lock:
            self._maybe_half_open()
            return self._state

    def allow_request(self) -> bool:
        """False means: don't bother calling this provider right now."""
        with self._lock:
            self._maybe_half_open()
            return self._state != CircuitState.OPEN

    def record_success(self) -> None:
        with self._lock:
            self._failure_count = 0
            self._state = CircuitState.CLOSED
            self._opened_at = None

    def record_failure(self) -> None:
        with self._lock:
            self._failure_count += 1
            if self._state == CircuitState.HALF_OPEN or self._failure_count >= self._failure_threshold:
                self._trip()

    def _trip(self) -> None:
        self._state = CircuitState.OPEN
        self._opened_at = time.monotonic()

    def _maybe_half_open(self) -> None:
        if self._state == CircuitState.OPEN and self._opened_at is not None:
            if time.monotonic() - self._opened_at >= self._reset_timeout_s:
                self._state = CircuitState.HALF_OPEN
