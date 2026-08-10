from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from argon2.low_level import Type


class PasswordPolicyError(ValueError):
    pass


class PasswordService:
    def __init__(self, minimum_length: int = 12) -> None:
        self.minimum_length = minimum_length
        # Argon2id with a deliberately substantial memory cost for a single-user,
        # local application. The parameters are encoded into each stored hash.
        self._hasher = PasswordHasher(
            time_cost=3,
            memory_cost=65536,
            parallelism=2,
            hash_len=32,
            salt_len=16,
            type=Type.ID,
        )

    def validate_new_password(self, password: str) -> None:
        if len(password) < self.minimum_length:
            raise PasswordPolicyError(
                f"Password must be at least {self.minimum_length} characters long."
            )
        if len(password) > 256:
            raise PasswordPolicyError("Password is too long.")
        if password.strip() == "":
            raise PasswordPolicyError("Password cannot be blank.")

    @staticmethod
    def validate_username(username: str) -> str:
        normalized = username.strip()
        if not 3 <= len(normalized) <= 64:
            raise PasswordPolicyError("Username must be between 3 and 64 characters.")
        if any(ord(ch) < 32 for ch in normalized):
            raise PasswordPolicyError("Username contains invalid control characters.")
        return normalized

    def hash_password(self, password: str) -> str:
        self.validate_new_password(password)
        return self._hasher.hash(password)

    def verify(self, stored_hash: str, password: str) -> bool:
        try:
            return bool(self._hasher.verify(stored_hash, password))
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False

    def needs_rehash(self, stored_hash: str) -> bool:
        try:
            return self._hasher.check_needs_rehash(stored_hash)
        except InvalidHashError:
            return True
