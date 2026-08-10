from cardbudget.security.csrf import FormTokenService


def test_form_token_is_purpose_bound_and_expires():
    service = FormTokenService("s" * 64, ttl_seconds=60)
    token = service.issue("login", now=1000)
    assert service.validate(token, "login", now=1030)
    assert not service.validate(token, "setup", now=1030)
    assert not service.validate(token, "login", now=1061)
    assert not service.validate(token + "tamper", "login", now=1030)
