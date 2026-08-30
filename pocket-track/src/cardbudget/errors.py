class CardBudgetError(RuntimeError):
    """Base application error."""


class SecurityBootstrapError(CardBudgetError):
    """Raised when required security material cannot be initialized."""


class KeychainUnavailable(SecurityBootstrapError):
    """Raised when the operating-system keychain cannot be used."""


class EncryptionUnavailable(SecurityBootstrapError):
    """Raised when SQLCipher is missing or not actually active."""


class DatabaseOpenError(SecurityBootstrapError):
    """Raised when the encrypted database cannot be opened safely."""


class DatabaseKeyMissing(DatabaseOpenError):
    """Raised when an existing encrypted database is unreadable because the
    keychain entry that encrypted it is gone.

    Distinct from a generic DatabaseOpenError: the database file is intact, the
    key simply no longer exists, so no retry or repair can recover it. The key is
    never written to disk or an environment variable by design.
    """
