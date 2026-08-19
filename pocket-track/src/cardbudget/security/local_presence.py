"""Local device-presence check ("is a human physically at this machine").

Used only by the forgot-password flow (auth/service.py). PocketTrack has no
email, so a forgotten password cannot be proven "yours to reset" by a code or
a link - the alternative used here is asking the OS itself: Touch ID or the
Mac login password on macOS (`LAPolicyDeviceOwnerAuthentication`), Windows
Hello on Windows. A successful result means the OS itself vouches for the
person at the keyboard right now.

This deliberately does NOT read a secret from the OS keychain and treat its
mere presence as proof of identity - `bootstrap_services()` already gives the
server silent, unprompted keychain access on every startup (that's how it
decrypts the database without asking you anything each launch), so a
keychain-read-based check would make `/forgot-password` an unauthenticated
bypass reachable by anything that can open a TCP connection to 127.0.0.1,
not a real proof that a human is at the keyboard. The OS prompt is the part
that can't be forged by a request that merely reaches the port.

Platform APIs are only imported inside the functions that need them, so
importing this module never fails on a platform without the corresponding
package installed - `verify()` raises `LocalPresenceUnavailable` in that case
instead, and callers surface a clear "not available on this system" message.
"""

from __future__ import annotations

import sys
import threading


class LocalPresenceUnavailable(RuntimeError):
    """The OS/hardware/dependency needed for a local-presence check isn't available here."""


class LocalPresenceService:
    """Real implementation - dispatches to the current OS's own auth prompt."""

    #: How long to wait for the user to respond to the OS prompt before giving up.
    timeout_seconds = 60.0

    def verify(self, reason: str) -> bool:
        """Block until the OS reports success, failure, or a timeout.

        Returns True only on a genuine OS-confirmed local presence (Touch ID,
        Mac account password, or Windows Hello, whichever the OS itself
        offers). Returns False on cancellation, timeout, or a failed
        attempt. Raises LocalPresenceUnavailable if this platform/machine
        cannot perform the check at all.
        """
        if sys.platform == "darwin":
            return self._verify_macos(reason)
        if sys.platform == "win32":
            return self._verify_windows(reason)
        raise LocalPresenceUnavailable(f"Local-presence verification is not implemented for {sys.platform}.")

    def _verify_macos(self, reason: str) -> bool:
        try:
            import LocalAuthentication as LA
        except ImportError as exc:
            raise LocalPresenceUnavailable(
                "pyobjc-framework-LocalAuthentication is not installed."
            ) from exc

        context = LA.LAContext.alloc().init()
        # Touch ID, falling back to the Mac account password if Touch ID
        # isn't enrolled/available - mirrors what "unlock with Touch ID"
        # does system-wide, so it doesn't strand machines without a sensor.
        policy = LA.LAPolicyDeviceOwnerAuthentication
        can_evaluate, capability_error = context.canEvaluatePolicy_error_(policy, None)
        if not can_evaluate:
            detail = str(capability_error.localizedDescription()) if capability_error else "unknown reason"
            raise LocalPresenceUnavailable(f"macOS cannot perform local device authentication here: {detail}")

        done = threading.Event()
        outcome: dict[str, object] = {}

        def _reply(success: bool, error) -> None:
            outcome["success"] = bool(success)
            done.set()

        context.evaluatePolicy_localizedReason_reply_(policy, reason, _reply)
        fired = done.wait(timeout=self.timeout_seconds)
        if not fired:
            return False
        return bool(outcome.get("success", False))

    def _verify_windows(self, reason: str) -> bool:
        try:
            import asyncio

            from winsdk.windows.security.credentials.ui import (
                UserConsentVerificationResult,
                UserConsentVerifier,
            )
        except ImportError as exc:
            raise LocalPresenceUnavailable("winsdk is not installed.") from exc

        async def _request() -> "UserConsentVerificationResult":
            availability = await UserConsentVerifier.check_availability_async()
            if availability != 0:  # 0 == Available
                raise LocalPresenceUnavailable(f"Windows Hello is not available here ({availability!r}).")
            return await UserConsentVerifier.request_verification_async(reason)

        try:
            result = asyncio.run(asyncio.wait_for(_request(), timeout=self.timeout_seconds))
        except asyncio.TimeoutError:
            return False
        return result == UserConsentVerificationResult.VERIFIED


class FakeLocalPresence:
    """Test double - never touches real OS auth. See tests/conftest.py.

    Records every call's `reason` so tests can assert the prompt was (or
    was not) triggered, without depending on real hardware.
    """

    def __init__(self, *, succeed: bool = True, available: bool = True) -> None:
        self.succeed = succeed
        self.available = available
        self.calls: list[str] = []

    def verify(self, reason: str) -> bool:
        self.calls.append(reason)
        if not self.available:
            raise LocalPresenceUnavailable("fake: local presence unavailable")
        return self.succeed
