# PocketTrack

Private spending, budgeting, and net-worth tracking for **macOS and Windows**.

## Pre-requisites

- This application can be run on **macOS or Windows**.
- A **Plaid Trial account** is required to connect real bank and credit-card accounts.

### Get Plaid Production Client ID and Secret

1. Go to [https://plaid.com/](https://plaid.com/) and create a free developer account.

2. Verify your email address and log in to the **Plaid Dashboard**.

3. From the Plaid Dashboard, select **Start Trial** or **Apply for Trial Plan**.

4. Complete the Trial Plan application.

   > The Plaid Trial Plan allows you to connect real financial institutions using the **Production environment**. Trial accounts are limited to a small number of Production Items.

5. After Trial access is enabled, navigate to:

   **Plaid Dashboard → Developers → API Keys**

6. Copy the following credentials:

   - **Client ID**
   - **Production Secret**


## Start

PocketTrack currently supports **macOS and Windows only**.

### macOS

```bash
git clone https://github.com/darshit95/agent-dp.git
cd agent-dp/pocket-track
./start.sh
```

Open **https://my-pocket-track**.

The first start installs/checks Python 3.12, Homebrew, Caddy, Ollama, Python dependencies, the local AI model, runs the test suite, configures the private local hostname and locally trusted HTTPS, installs the daily 8 AM refresh job, and starts PocketTrack in the background. macOS may ask for your administrator password while configuring the local hostname/HTTPS certificate.

### Windows

```powershell
git clone https://github.com/darshit95/agent-dp.git
cd agent-dp/pocket-track
.\start.ps1
```

Open **http://127.0.0.1:8000**.

The first start installs/checks Python 3.12, Ollama, Python dependencies, the local AI model, runs the test suite, installs the daily refresh job, and starts PocketTrack in the background.

## Stop

### macOS

```bash
./stop.sh
```

### Windows

```powershell
.\stop.ps1
```

---

## What PocketTrack does

PocketTrack is a local-first personal finance application with two focused workflows:

**Spending & budgets**

- Connect credit cards using Plaid.
- Track any credit card returned by the institution — there are no hardcoded card names.
- Import posted transactions only.
- Ignore pending transactions and obvious credit-card payment/AutoPay entries.
- Refresh automatically every morning at 8 AM.
- Backfill historical months when needed.
- Categorize transactions locally with Ollama and remember manual merchant corrections.
- Create custom spending buckets, including the default `Unknown` bucket.
- Set monthly budgets and see clear within-budget / over-budget status.
- Delete a transaction permanently from PocketTrack without it returning on the next Plaid sync.

**Net worth**

- Add assets and liabilities.
- Edit asset name, institution, and value directly in the asset list.
- Classify assets into:
  - Cash & Cash Equivalents
  - Taxable Investments
  - Retirement & Health
  - Alternative Investments
  - Other Assets
- Use local AI for initial asset classification and manually override it at any time.
- Exclude informational subtotal rows to avoid double counting.
- Calculate `Net Worth = Assets - Liabilities`.
- View asset allocation as a live donut chart.

## Privacy & security

PocketTrack is intentionally designed as a single-user local application.

- The FastAPI backend binds only to `127.0.0.1`.
- On macOS, `https://my-pocket-track` resolves only to your own Mac through `/etc/hosts`.
- On macOS, Caddy is bound to loopback and provides locally trusted HTTPS on port 443. Windows currently uses `http://127.0.0.1:8000`.
- The application database is encrypted with SQLCipher.
- Plaid credentials, access tokens, database keys, and session secrets are stored in the operating-system Keychain rather than source code or the database.
- Passwords are hashed with Argon2id.
- Sessions are server-side, `HttpOnly`, `SameSite=Strict`, and `Secure` when accessed through the HTTPS URL.
- CSRF protection, login throttling, restrictive CSP, Host-header protection, and HSTS over HTTPS are enabled.
- Ollama runs locally; PocketTrack does not fall back to a remote LLM.
- PocketTrack does not include money-transfer or payment-initiation functionality.

PocketTrack's local data lives outside the Git repository in:

```text
~/.pockettrack/
```

Do not commit backups or secrets. The included `.gitignore` excludes the common local/runtime files.

## First-time application setup

After the platform-specific startup script completes:

1. On macOS, open **https://my-pocket-track**. On Windows, open **http://127.0.0.1:8000**.
2. Create your PocketTrack username and password.
3. Open **Settings**.
4. Enter your own Plaid Production Client ID and Production Secret once. They are stored in the operating-system credential store.
5. Click **Connect bank** and complete Plaid Link.
6. Expand each connected bank and enable only the credit cards you want PocketTrack to track.
7. Click **Sync now**, or wait for the next daily refresh.

## Plaid

Every PocketTrack user needs their own Plaid developer credentials. The repository contains no shared Plaid secret.

PocketTrack uses Plaid's Transactions flow only. It does not need Auth, Transfer, ACH, account/routing-number retrieval, or payment initiation.

For development, set:

```bash
export POCKETTRACK_PLAID_ENVIRONMENT=sandbox
```

For normal use, the startup scripts default to Production.

## Historical month import

```bash
source .venv/bin/activate
pockettrack backfill 2026-07
```

The dashboard also provides a historical-month refresh action.

## Manual refresh

```bash
source .venv/bin/activate
pockettrack daily-sync
```

## Daily scheduler

On macOS, `start.sh` installs the default 8 AM `launchd` job. On Windows, `start.ps1` installs the Windows equivalent. To inspect or change it on macOS:

```bash
source .venv/bin/activate
pockettrack scheduler-status
pockettrack install-scheduler --hour 8
```

## Backup and restore

Create a password-encrypted logical backup:

```bash
source .venv/bin/activate
pockettrack backup
```

Restore one:

```bash
pockettrack restore ~/Documents/PocketTrack-Backup-YYYYMMDD-HHMMSS.ptbackup
```

Plaid credentials/access tokens and the SQLCipher Keychain key are intentionally excluded from backups.

## Diagnostics

```bash
source .venv/bin/activate
pockettrack doctor
pockettrack verify-encryption
python -m pytest -q
```

Runtime logs created by `start.sh` are under:

```text
.runtime/
```

## GitHub publishing

The repository includes a helper for publishing an existing local copy:

```bash
./scripts/publish-github.sh YOUR_USERNAME/pockettrack --public
```

The helper uses GitHub CLI, initializes Git if necessary, commits the current source, creates the repository, and pushes the `main` branch.

## Local URL vs public hosting

On macOS, **https://my-pocket-track** is a private local hostname configured by `start.sh`; it is not a public internet domain. On Windows, PocketTrack currently uses **http://127.0.0.1:8000**. This is intentional because PocketTrack handles sensitive financial data.

Publishing the source to GitHub lets other people install their own local instance. Making a centrally hosted public PocketTrack service would require a different multi-user security architecture, public DNS, trusted public TLS, server-side secret isolation, user tenancy, and a deployment platform; the local build should not simply be exposed to the internet.

## Requirements

- PocketTrack currently supports **macOS and Windows only**.
- macOS 14 Sonoma or newer is recommended.
- Windows 10 or Windows 11 is recommended.
- Network access is needed during first setup to install dependencies, download the Ollama model, and communicate with Plaid.
- On macOS, the startup script can install Homebrew and may prompt for administrator privileges.
- On Windows, `winget` is recommended so `start.ps1` can install Python 3.12 and Ollama automatically.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
pockettrack serve
```

The internal Python package remains `cardbudget` for continuity with the original prototype; the distribution, application, CLI, UI, documentation, storage location, and public product name are PocketTrack.

## License

MIT. See [LICENSE](LICENSE).
