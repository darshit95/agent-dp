from __future__ import annotations

from dataclasses import dataclass

from cardbudget.db.repositories import AuditRepository, UserRecord, UserRepository
from cardbudget.security.passwords import PasswordService


@dataclass(frozen=True)
class AuthenticationResult:
    user: UserRecord | None
    valid: bool


class AuthService:
    def __init__(
        self,
        users: UserRepository,
        passwords: PasswordService,
        audit: AuditRepository,
    ) -> None:
        self.users = users
        self.passwords = passwords
        self.audit = audit
        # A dummy hash reduces the username-enumeration timing gap for a missing user.
        self._dummy_hash = self.passwords.hash_password("not-a-real-user-password-0123456789")

    def is_initialized(self) -> bool:
        return self.users.count() == 1

    def setup_user(self, username: str, password: str) -> UserRecord:
        normalized = self.passwords.validate_username(username)
        password_hash = self.passwords.hash_password(password)
        return self.users.create_single_user(normalized, password_hash)

    def authenticate(self, username: str, password: str) -> AuthenticationResult:
        normalized = username.strip()
        user = self.users.get_by_username(normalized)
        stored_hash = user.password_hash if user else self._dummy_hash
        valid_password = self.passwords.verify(stored_hash, password)
        if not user or not valid_password:
            return AuthenticationResult(None, False)
        if self.passwords.needs_rehash(user.password_hash):
            new_hash = self.passwords.hash_password(password)
            self.users.update_password_hash(user.id, new_hash)
            user = UserRecord(user.id, user.username, new_hash)
        return AuthenticationResult(user, True)
    def change_password(self, user_id: int, current_password: str, new_password: str) -> None:
        user = self.users.get_by_id(user_id)
        if not user or not self.passwords.verify(user.password_hash, current_password):
            raise ValueError("Current password is incorrect.")
        new_hash = self.passwords.hash_password(new_password)
        self.users.update_password_hash(user_id, new_hash)

