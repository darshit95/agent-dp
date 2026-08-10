from cardbudget.security.throttle import LoginThrottle


def test_throttle_locks_after_failures_and_recovers():
    throttle = LoginThrottle(max_failures=3, window_seconds=60, lockout_seconds=10)
    for t in (1.0, 2.0, 3.0):
        assert throttle.check("user", "127.0.0.1", now=t).allowed
        throttle.record_failure("user", "127.0.0.1", now=t)
    denied = throttle.check("user", "127.0.0.1", now=4.0)
    assert not denied.allowed
    assert denied.retry_after_seconds > 0
    assert throttle.check("user", "127.0.0.1", now=14.0).allowed
