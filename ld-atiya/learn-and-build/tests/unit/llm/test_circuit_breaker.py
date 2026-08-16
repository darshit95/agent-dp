import time

from llm.circuit_breaker import CircuitBreaker, CircuitState


def test_starts_closed():
    breaker = CircuitBreaker(failure_threshold=3, reset_timeout_s=60)
    assert breaker.state == CircuitState.CLOSED
    assert breaker.allow_request() is True


def test_opens_after_threshold_failures():
    breaker = CircuitBreaker(failure_threshold=3, reset_timeout_s=60)
    breaker.record_failure()
    breaker.record_failure()
    assert breaker.state == CircuitState.CLOSED
    breaker.record_failure()
    assert breaker.state == CircuitState.OPEN
    assert breaker.allow_request() is False


def test_success_resets_failure_count():
    breaker = CircuitBreaker(failure_threshold=3, reset_timeout_s=60)
    breaker.record_failure()
    breaker.record_failure()
    breaker.record_success()
    breaker.record_failure()
    breaker.record_failure()
    assert breaker.state == CircuitState.CLOSED  # only 2 failures since reset


def test_transitions_to_half_open_after_cooldown():
    breaker = CircuitBreaker(failure_threshold=1, reset_timeout_s=0.05)
    breaker.record_failure()
    assert breaker.state == CircuitState.OPEN
    time.sleep(0.06)
    assert breaker.state == CircuitState.HALF_OPEN
    assert breaker.allow_request() is True


def test_half_open_failure_reopens_immediately():
    breaker = CircuitBreaker(failure_threshold=1, reset_timeout_s=0.05)
    breaker.record_failure()
    time.sleep(0.06)
    assert breaker.state == CircuitState.HALF_OPEN
    breaker.record_failure()
    assert breaker.state == CircuitState.OPEN


def test_half_open_success_closes():
    breaker = CircuitBreaker(failure_threshold=1, reset_timeout_s=0.05)
    breaker.record_failure()
    time.sleep(0.06)
    assert breaker.state == CircuitState.HALF_OPEN
    breaker.record_success()
    assert breaker.state == CircuitState.CLOSED
