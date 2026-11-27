from __future__ import annotations

from dataclasses import dataclass

from cardbudget.auth.service import AuthService
from cardbudget.categorization.chatgpt import ChatGPTConnection
from cardbudget.categorization.ollama import OllamaClassifierClient
from cardbudget.categorization.profiles import ProviderProfiles
from cardbudget.categorization.service import CategorizationService
from cardbudget.categorization.worker import CategorizationWorker
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
from cardbudget.errors import DatabaseKeyMissing, DatabaseOpenError
from cardbudget.security.keychain import (
    DB_KEY_NAME,
    OSKeychain,
    SecretStore,
    db_key_exists,
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
    providers: ProviderProfiles
    categorization_worker: CategorizationWorker
    chatgpt: ChatGPTConnection
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
    # Capture both facts before ensure_db_key runs: once it mints a replacement
    # key, "first run" and "the key for this database is gone" look identical.
    database_existed = settings.database_path.exists()
    had_db_key = db_key_exists(store)
    db_key = ensure_db_key(store)
    session_secret = ensure_session_secret(store)

    db = database or Database(settings.database_path, db_key, require_cipher=True)
    try:
        db.initialize()
    except DatabaseOpenError as exc:
        if database_existed and not had_db_key:
            raise DatabaseKeyMissing(
                f"{settings.database_path} exists, but its encryption key is no longer in "
                f"the OS keychain (service {settings.keychain_service!r}, account "
                f"{DB_KEY_NAME!r}), so it cannot be decrypted.\n"
                "The key is deliberately stored only in the keychain - never on disk or in "
                "an environment variable - so there is no copy to recover.\n"
                "If you restored this Mac or reset your login password, unlock the older "
                "login keychain in Keychain Access to get the entry back.\n"
                "Otherwise restore a backup, or move the file aside to start fresh:\n"
                f"  mv {settings.database_path} {settings.database_path}.orphaned"
            ) from exc
        if database_existed:
            # The key is present but does not decrypt this file. Distinct from
            # DatabaseKeyMissing (no key at all) and from a first run, and it
            # was previously indistinguishable from any other open failure.
            # Most often a keychain entry from a different install, or a
            # database copied between machines without its key.
            raise DatabaseOpenError(
                f"{settings.database_path} exists and a key is present in the OS keychain "
                f"(service {settings.keychain_service!r}, account {DB_KEY_NAME!r}), but that "
                "key does not decrypt this database.\n"
                "That usually means the file and the key came from different installs - for "
                "example a database copied from another Mac, or a keychain entry left behind "
                "by an earlier setup.\n"
                "If this database holds no data you need, move it aside and start fresh:\n"
                f"  mv {settings.database_path} {settings.database_path}.orphaned\n"
                "Otherwise restore a backup, or recover the matching keychain entry.\n"
                f"Original failure: {exc}"
            ) from exc
        raise

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
        llm=ollama_client or (ollama if settings.categorization_default == "ollama" else None),
        pace_seconds=settings.categorization_pace_seconds,
    )
    networth = NetWorthService(networth_repository, ollama_client)
    providers = ProviderProfiles(db, store, settings, ollama)
    chatgpt = ChatGPTConnection(db)
    worker = CategorizationWorker(categorization, providers, networth_repository, chatgpt)

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
        providers=providers,
        categorization_worker=worker,
        chatgpt=chatgpt,
        networth_repository=networth_repository,
        networth=networth,
    )
