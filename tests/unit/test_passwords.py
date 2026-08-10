import pytest

from cardbudget.security.passwords import PasswordPolicyError, PasswordService


def test_argon2id_hash_and_verify():
    service = PasswordService(minimum_length=12)
    password = "correct-horse-battery-staple"
    password_hash = service.hash_password(password)
    assert password_hash != password
    assert password_hash.startswith("$argon2id$")
    assert service.verify(password_hash, password)
    assert not service.verify(password_hash, "wrong-password-value")


def test_short_password_rejected():
    service = PasswordService(minimum_length=12)
    with pytest.raises(PasswordPolicyError):
        service.hash_password("too-short")
