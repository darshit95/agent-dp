from __future__ import annotations

import hmac
import secrets
from dataclasses import dataclass
from datetime import timedelta

from cardbudget.db.repositories import SessionRecord, SessionRepository, utc_now


@dataclass(frozen=True)
class SessionContext:
    id: str
    user_id: int
    csrf_token: str


class SessionService:
    def __init__(self, repository: SessionRepository, idle_timeout_seconds: int) -> None:
        self.repository = repository
        self.idle_timeout = timedelta(seconds=idle_timeout_seconds)

    def create(self, user_id: int) -> SessionContext:
        now = utc_now()
        record = SessionRecord(
            id=secrets.token_urlsafe(32),
            user_id=user_id,
            csrf_token=secrets.token_urlsafe(32),
            created_at=now,
            last_seen_at=now,
            expires_at=now + self.idle_timeout,
        )
        self.repository.create(record)
        return SessionContext(record.id, record.user_id, record.csrf_token)

    def resolve(self, session_id: str | None) -> SessionContext | None:
        if not session_id:
            return None
        record = self.repository.get(session_id)
        if not record:
            return None
        now = utc_now()
        if record.expires_at <= now:
            self.repository.delete(record.id)
            return None
        self.repository.touch(record.id, now, now + self.idle_timeout)
        return SessionContext(record.id, record.user_id, record.csrf_token)

    def validate_csrf(self, context: SessionContext, supplied_token: str | None) -> bool:
        if not supplied_token:
            return False
        return hmac.compare_digest(context.csrf_token, supplied_token)

    def destroy(self, session_id: str) -> None:
        self.repository.delete(session_id)
