SCHEMA_VERSION = 7

CORE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS app_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    csrf_token TEXT NOT NULL,
    created_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);

CREATE TABLE IF NOT EXISTS buckets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    default_budget_cents INTEGER NULL CHECK (default_budget_cents IS NULL OR default_budget_cents >= 0),
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    icon TEXT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    remote_addr TEXT NULL,
    details_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plaid_items (
    item_id TEXT PRIMARY KEY,
    institution_id TEXT NULL,
    institution_name TEXT NULL,
    environment TEXT NOT NULL CHECK (environment IN ('sandbox', 'production')),
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    sync_cursor TEXT NULL,
    transactions_update_status TEXT NULL,
    last_synced_at TEXT NULL,
    last_sync_error_code TEXT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    item_id TEXT NOT NULL REFERENCES plaid_items(item_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    official_name TEXT NULL,
    mask TEXT NULL,
    account_type TEXT NOT NULL,
    subtype TEXT NULL,
    card_key TEXT NULL UNIQUE,
    card_name TEXT NULL,
    enabled INTEGER NOT NULL DEFAULT 0 CHECK (enabled IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_accounts_item_id ON accounts(item_id);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    amount_cents INTEGER NOT NULL,
    iso_currency_code TEXT NOT NULL DEFAULT 'USD',
    posted_date TEXT NULL,
    authorized_date TEXT NULL,
    budget_date TEXT NULL,
    merchant_name TEXT NULL,
    description TEXT NOT NULL,
    pending INTEGER NOT NULL DEFAULT 0 CHECK (pending IN (0, 1)),
    pending_transaction_id TEXT NULL,
    pfc_primary TEXT NULL,
    pfc_detailed TEXT NULL,
    pfc_confidence TEXT NULL,
    bucket_id INTEGER NULL REFERENCES buckets(id) ON DELETE SET NULL,
    classification_source TEXT NULL,
    classification_confidence REAL NULL,
    is_removed INTEGER NOT NULL DEFAULT 0 CHECK (is_removed IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_budget_date ON transactions(budget_date);
CREATE INDEX IF NOT EXISTS idx_transactions_pending_id ON transactions(pending_transaction_id);

CREATE TABLE IF NOT EXISTS deleted_transactions (
    transaction_id TEXT PRIMARY KEY,
    deleted_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS merchant_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_key TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    bucket_id INTEGER NOT NULL REFERENCES buckets(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_merchant_rules_bucket_id ON merchant_rules(bucket_id);

CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    institution TEXT NULL,
    current_value_cents INTEGER NOT NULL CHECK (current_value_cents >= 0),
    asset_bucket TEXT NOT NULL,
    include_in_net_worth INTEGER NOT NULL DEFAULT 1 CHECK (include_in_net_worth IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_assets_bucket ON assets(asset_bucket);

CREATE TABLE IF NOT EXISTS liabilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    institution TEXT NULL,
    current_balance_cents INTEGER NOT NULL CHECK (current_balance_cents >= 0),
    include_in_net_worth INTEGER NOT NULL DEFAULT 1 CHECK (include_in_net_worth IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS asset_rules (
    asset_key TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    asset_bucket TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

# Columns added after a table's first release. CREATE TABLE IF NOT EXISTS leaves
# existing databases untouched, so each entry is applied with ALTER TABLE when the
# column is missing. Append-only, and every column must be nullable or defaulted.
ADDED_COLUMNS: tuple[tuple[str, str, str], ...] = (
    ("buckets", "icon", "TEXT NULL"),
)

DEFAULT_BUCKETS = (
    "Subscriptions",
    "Shopping",
    "Gas + Car Wash",
    "Grocery",
    "Unknown",
)

ASSET_BUCKETS = (
    "Cash & Cash Equivalents",
    "Taxable Investments",
    "Retirement & Health",
    "Alternative Investments",
    "Other Assets",
)
