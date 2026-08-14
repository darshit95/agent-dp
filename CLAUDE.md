# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository layout

This repo contains a single project, **PocketTrack**, in the `pocket-track/` subdirectory. All commands below assume `cd pocket-track` first.

## Commands

```bash
# Setup (from pocket-track/)
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'

# Run the full test suite
python -m pytest -q

# Run a single test file / test
python -m pytest tests/unit/test_config.py -q
python -m pytest tests/unit/test_config.py::test_name -q

# Run the app locally (loopback only, http://127.0.0.1:8000)
pockettrack serve
pockettrack serve --port 8001

# Diagnostics
pockettrack doctor              # non-secret security/dependency checks
pockettrack verify-encryption   # confirms SQLCipher is actually enforced

# Sync / categorization (require setup + Plaid creds already configured)
pockettrack daily-sync
pockettrack backfill 2026-07

# Scheduler (macOS launchd)
pockettrack scheduler-status
pockettrack install-scheduler --hour 8
pockettrack uninstall-scheduler

# Backup / restore
pockettrack backup
pockettrack restore ~/Documents/PocketTrack-Backup-YYYYMMDD-HHMMSS.ptbackup
```

There is no configured linter/formatter (no ruff/black/mypy in `pyproject.toml`) — match existing style rather than introducing one.

Full-stack start/stop (installs system deps, Ollama, launchd job, then runs the server in the background) is via `./start.sh` / `./stop.sh` (macOS) or `.\start.ps1` / `.\stop.ps1` (Windows). These do far more than `pockettrack serve` and are generally not what you want while iterating on code — use `pockettrack serve` plus pytest instead. Runtime logs from `start.sh` land in `.runtime/`.

## Architecture

PocketTrack is a **single-user, local-only** FastAPI app (package name `cardbudget`, product name PocketTrack — the internal package kept its original name for continuity; don't rename it). Everything is designed around one invariant: **the server binds only to `127.0.0.1`, and no financial data or secret leaves the machine.** Any change that widens network exposure, adds a remote fallback for secrets, or weakens encryption is off-limits unless the user explicitly asks for it.

### Service composition (start here)

`services.py::bootstrap_services()` is the composition root — it builds every repository/service and wires them into one `ApplicationServices` dataclass, which is stashed on `app.state.services` (`app.py::create_app`) and reachable in routes via `_services(request)`. When adding a new feature, add its repository/service here rather than constructing dependencies ad hoc inside routes.

Bootstrap order matters and encodes the security model:
1. `db.engine.ensure_private_directory` — create `~/.pockettrack` as `0700`.
2. `security.keychain` — fetch-or-create the DB encryption key and session secret in the OS keychain (`OSKeychain`, backed by `keyring`; tests use `MemorySecretStore` instead — never swap this for a file-based store in production code paths).
3. `db.engine.Database` — opens SQLCipher with `require_cipher=True` and fails closed (`EncryptionUnavailable`/`DatabaseOpenError`) rather than ever falling back to plaintext SQLite. Tests inject `sqlite3.connect` with `require_cipher=False`; application bootstrap never takes that path.
4. Repositories (`db/repositories.py`) wrap raw SQL per entity (users, sessions, buckets, transactions, merchant rules, Plaid items, net worth, audit log).
5. Domain services layer on top: `auth`, `sessions`/`csrf`/`throttle` (security), `plaid` (Plaid API + sync), `categorization` (rules + local Ollama LLM), `networth`.

### Request flow

Three routers are mounted in `app.py`: `auth` (login/setup/logout/change-password), `plaid` (Link token creation, item exchange, sync endpoints), and `web` (dashboard, transactions, buckets, net worth — the bulk of the UI, in `web/routes.py`). Routes are plain function-based FastAPI handlers, not classes; session/CSRF checks are explicit helper calls at the top of each handler (`_require_authenticated_page`, `_require_csrf` in `web/routes.py`), not middleware or dependency injection — follow that pattern for new routes rather than introducing `Depends`-based auth.

Global middleware in `app.py` sets strict security headers (CSP, `X-Frame-Options`, HSTS, `Cache-Control: no-store` by default) and a `TrustedHostMiddleware` allowlist (`127.0.0.1`, `localhost`, `my-pocket-track`). The CSP is relaxed only for `/settings` and `/plaid` paths, to allow Plaid Link's hosted JS/iframe from `cdn.plaid.com` — keep that exception narrow if you touch it.

### Secrets vs. data split

Anything secret (Plaid client ID/secret, access tokens, DB encryption key, session signing secret) lives in the **OS keychain** (`security/keychain.py`), never in the SQLCipher database or on disk in plaintext. Non-secret settings persist to `~/.pockettrack/preferences.json` (`config.py::Settings.persist_preferences`). Backups (`backup.py`) are logical, password-encrypted, and deliberately exclude Plaid secrets and the SQLCipher key — restoring a backup does not restore access tokens.

The `Unknown` bucket (`BucketRepository.SYSTEM_BUCKET_NAME`) is load-bearing: `monthly_summary` folds transactions with a NULL `bucket_id` into the bucket with that literal name, and the categorization fallback looks it up the same way. It therefore cannot be renamed or deleted — don't relax those guards without changing both call sites to use an id.

Schema changes to existing tables need an entry in `schema.ADDED_COLUMNS` (applied by `Database._add_missing_columns`), because `CREATE TABLE IF NOT EXISTS` will not alter a database that already exists.

`config.Settings` is a frozen pydantic model read once from env vars (`POCKETTRACK_*`, with legacy `CARDBUDGET_*` aliases still honored for migration) plus the persisted preferences file. `host` is a `Literal["127.0.0.1"]` — this is enforced at the type level so a LAN/0.0.0.0 bind is not constructible.

### Plaid integration

`plaid/client.py` is a thin HTTP client (raises `PlaidAPIError`), `plaid/service.py` owns sync/backfill logic — it imports **posted transactions only** and actively filters out pending transactions and credit-card payment/AutoPay entries (both at sync time and again defensively in `db/engine.py::Database.initialize` for older data). `plaid/routes.py` exposes Link-token creation and item exchange. Only the Transactions product is used — no Auth/Transfer/ACH/payment-initiation code should be added here.

### Icons

`icons.py` is the single catalog mapping an icon id to an SVG sprite symbol (`#i-<id>`), a label and a colour tint. Buckets may store an explicit `icon`; when the column is NULL the id is derived from the bucket name by keyword match, so renaming a bucket updates its icon. Two invariants hold it together, both covered by `tests/unit/test_icons.py`: every id in the catalog must have a `<symbol>` in `base.html`, and only catalog ids ever reach a template (`_icon_or_auto` in `web/routes.py` discards anything else, so a stored or submitted value can't inject a sprite reference). Icons are exposed to Jinja as globals registered in `create_app`, not via context dicts, because they're resolved per row inside loops.

The strict CSP (`style-src 'self'`) means **no inline `style` attributes in templates** — that's why the budget bars are `<progress>` elements styled by class and the donut uses SVG presentation attributes.

### Categorization & net worth

`categorization/service.py` applies remembered merchant-name rules first, falling back to `categorization/ollama.py` (a local Ollama HTTP client) for anything unmatched; it never calls a remote LLM. `networth.py` follows the same local-first pattern for initial asset classification into the five buckets defined in `db/schema.py::ASSET_BUCKETS`, with manual override always available through the UI/routes.

### Testing conventions

`tests/conftest.py::test_stack` is the standard fixture: it builds a full `ApplicationServices` against a temp dir, `MemorySecretStore`, and unencrypted `sqlite3` (never SQLCipher) so tests don't depend on OS keychain or the `sqlcipher3` binding. `create_user` layers a completed `/setup` flow on top. CSRF-protected POSTs in tests must scrape the token first (see `extract_csrf`). Integration tests hit routes through `fastapi.testclient.TestClient`; unit tests exercise services/repositories directly. `tests/integration/test_sqlcipher_encryption.py` and `tests/unit/test_keychain.py` are the ones that actually validate the fail-closed encryption/keychain behavior — real regressions in that area should be caught there, not just in the happy-path fixture.

## Working in this repo

- The repo's own `pocket-track/.venv/`, `.runtime/`, and `__pycache__` directories may show up as modified/untracked in `git status` from prior local runs — don't assume changes there are meaningful, and don't commit them.
- Don't add code paths that send transaction data, account data, or secrets to any network destination other than Plaid's API (for sync) and the local Ollama daemon (for categorization).
