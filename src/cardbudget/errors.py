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
