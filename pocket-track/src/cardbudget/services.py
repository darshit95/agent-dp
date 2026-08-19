from __future__ import annotations

from dataclasses import dataclass

from cardbudget.auth.service import AuthService
from cardbudget.categorization.ollama import OllamaClassifierClient
from cardbudget.categorization.service import CategorizationService
from cardbudget.config import Settings
from cardbudget.db.engine import Database, ensure_private_directory
from cardbudget.db.repositories import (
    AuditRepository,
    BucketRepository,
    MerchantRuleRepository,
    NetWorthRepository,
    PlaidRepository,
    SessionRepository,
    TransactionRepository,
    UserRepository,
    utc_now,
)
from cardbudget.plaid.service import PlaidService
from cardbudget.networth import NetWorthService
from cardbudget.security.csrf import FormTokenService
from cardbudget.security.keychain import (
    OSKeychain,
    SecretStore,
    ensure_db_key,
    ensure_session_secret,
)
from cardbudget.security.local_presence import LocalPresenceService
from cardbudget.security.passwords import PasswordService
from cardbudget.security.sessions import SessionService
from cardbudget.security.throttle import LoginThrottle


@dataclass
class ApplicationServices:
    settings: Settings
    secret_store: SecretStore
    database: Database
    auth: AuthService
    sessions: SessionService
    form_tokens: FormTokenService
    throttle: LoginThrottle
    recovery_throttle: LoginThrottle
    buckets: BucketRepository
    audit: AuditRepository
    plaid_repository: PlaidRepository
    transactions: TransactionRepository
    merchant_rules: MerchantRuleRepository
    plaid: PlaidService
    categorization: CategorizationService
    ollama: OllamaClassifierClient
    networth_repository: NetWorthRepository
    networth: NetWorthService


def bootstrap_services(
    settings: Settings,
    *,
    secret_store: SecretStore | None = None,
    database: Database | None = None,
    plaid_client_factory=None,
    ollama_client: OllamaClassifierClient | None = None,
    local_presence: LocalPresenceService | None = None,
) -> ApplicationServices:
    ensure_private_directory(settings.data_dir)
    store = secret_store or OSKeychain(settings.keychain_service)
    db_key = ensure_db_key(store)
    session_secret = ensure_session_secret(store)

    db = database or Database(settings.database_path, db_key, require_cipher=True)
    db.initialize()

    users = UserRepository(db)
    session_repo = SessionRepository(db)
    audit = AuditRepository(db)
    buckets = BucketRepository(db)
    plaid_repository = PlaidRepository(db)
    transactions = TransactionRepository(db)
    merchant_rules = MerchantRuleRepository(db)
    networth_repository = NetWorthRepository(db)
    passwords = PasswordService(settings.password_min_length)
    presence = local_presence or LocalPresenceService()
    auth = AuthService(users, passwords, audit, presence)
    sessions = SessionService(session_repo, settings.session_idle_seconds)
    sessions.repository.delete_expired(utc_now())
    plaid = PlaidService(
        secret_store=store,
        plaid_repository=plaid_repository,
        transactions=transactions,
        environment=settings.plaid_environment,
        client_factory=plaid_client_factory,
    )
    ollama = ollama_client or OllamaClassifierClient(model=settings.ollama_model)
    categorization = CategorizationService(
        transactions=transactions,
        buckets=buckets,
        merchant_rules=merchant_rules,
        llm=ollama,
        pace_seconds=settings.categorization_pace_seconds,
    )
    networth = NetWorthService(networth_repository, ollama)

    return ApplicationServices(
        settings=settings,
        secret_store=store,
        database=db,
        auth=auth,
        sessions=sessions,
        form_tokens=FormTokenService(session_secret, settings.form_token_ttl_seconds),
        throttle=LoginThrottle(
            max_failures=settings.login_max_failures,
            window_seconds=settings.login_attempt_window_seconds,
            lockout_seconds=settings.login_lockout_seconds,
        ),
        # Separate instance (separate in-memory counters) from the login
        # throttle above, so repeated failed login attempts and repeated
        # forgot-password attempts don't share - or reset - each other's
        # lockout state. Mainly guards against spamming real OS Touch
        # ID/Windows Hello prompts.
        recovery_throttle=LoginThrottle(
            max_failures=settings.login_max_failures,
            window_seconds=settings.login_attempt_window_seconds,
            lockout_seconds=settings.login_lockout_seconds,
        ),
        buckets=buckets,
        audit=audit,
        plaid_repository=plaid_repository,
        transactions=transactions,
        merchant_rules=merchant_rules,
        plaid=plaid,
        categorization=categorization,
        ollama=ollama,
        networth_repository=networth_repository,
        networth=networth,
    )
