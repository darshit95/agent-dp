# PocketTrack

Private spending, budgeting, and net-worth tracking for **macOS and Windows**.

## Install and start

You’ll need Git and an internet connection for the first install. PocketTrack supports macOS 14 or later and Windows 10 or 11. **Rules only** is the default. Ollama and model API keys are optional.

If you already cloned the repo, open the `pocket-track` folder and run just the launcher for your operating system.

### macOS

Open Terminal and run these commands. They put the clone in your local `Projects` folder.

```bash
mkdir -p "$HOME/Projects"
cd "$HOME/Projects"
git clone https://github.com/darshit95/agent-dp.git
cd agent-dp/pocket-track
./start.sh
```

The first run prepares Homebrew, Python 3.12, Caddy, and local HTTPS. Enter your Mac administrator password if prompted. When the launcher prints **Ready**, open [https://my-pocket-track](https://my-pocket-track).

### Windows

Open PowerShell in the folder where you want to keep the clone.

```powershell
git clone https://github.com/darshit95/agent-dp.git
Set-Location .\agent-dp\pocket-track
.\start.ps1
```

The launcher prepares the Python environment and can install Python 3.12 through `winget`. If `winget` is unavailable, install Python 3.12 before running the launcher. When it prints **Ready**, open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## First-time application setup

1. Create your local PocketTrack username and password in the browser.
2. To import bank transactions, obtain your own [Plaid Production credentials](#get-your-plaid-production-client-id-and-secret). Go to **Settings → Plaid credentials**, enter the Client ID and Production Secret, and select **Save securely**.
3. Select **Connect bank**, complete Plaid Link, enable the cards you want to track, and select **Sync now**.

You can open the app and track net worth manually while Plaid access is pending. To choose a model later, open [Settings → Categorization](#categorization-providers).

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

> **Resource usage at a glance** ([details](#resource-usage)): new installs start in Rules-only mode. Optional model work runs in the background.

## What PocketTrack does

PocketTrack is a local-first personal finance application with two focused workflows:

**Spending & budgets**

- Connect credit cards using Plaid.
- Track any credit card returned by the institution — there are no hardcoded card names.
- Import posted transactions only.
- Ignore pending transactions and obvious credit-card payment/AutoPay entries.
- On macOS, refresh automatically at 8 AM and 8 PM.
- Backfill historical months when needed.
- Categorize transactions with saved merchant rules and high-confidence Plaid categories. Optionally refine unresolved transactions with a selected model.
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
- Use local heuristics for initial asset classification and manually override it at any time. An optional model can help with ambiguous assets.
- Exclude informational subtotal rows to avoid double counting.
- Calculate `Net Worth = Assets - Liabilities`.
- View asset allocation as a live donut chart.

## Categorization providers

Open **Settings → Categorization** to choose a provider.

| Provider | Setup |
|---|---|
| Rules only | Default for new installs. Uses saved merchant rules, selected high-confidence Plaid categories, and local asset heuristics. |
| ChatGPT plan | Select the provider, save, then choose **Continue with ChatGPT**. Grant plan usage in the browser and test with the model ID available to your account. This integration uses OpenAI’s local-app preview. |
| OpenAI or Claude API key | Save the provider and model ID, then store your key in the OS credential store from Settings. Requests use the billing and limits of that key. |
| Ollama | Choose Ollama in Settings to opt in. Install it separately and make the selected model available with `ollama pull <model>`, or start PocketTrack with `--update` once Ollama is installed. An older install's saved model ID is used when you opt in. |
| Local OpenAI-compatible endpoint | Run a compatible server with structured Chat Completions and enter a model ID and a loopback URL such as `http://127.0.0.1:8080/v1`. |

**Test connection** sends a synthetic transaction. Use **Categorize with AI** for a bounded pass. Cloud models run during bank sync only after you enable that option. Asset names require a separate cloud opt-in. On a provider error or quota limit, PocketTrack preserves remaining work for another pass and continues to import transactions.

## Resource usage

PocketTrack queues categorization in the encrypted database after import. A single worker handles manual sync, scheduled sync, backfill, and optional asset refinement. CLI imports also queue work, which the app takes when it is running. Previously queued work survives a restart.

- Rules run in batches. Optional model passes reuse identical requests and allow up to 12 distinct calls per pass, with a 35-second budget for starting calls. A request already in flight may finish after that budget.
- Local inference checks available memory before starting each new request. Ollama requests use a short 25-second keep-alive plus bounded context and output.
- Cloud providers run inference remotely. Bank sync and categorization use separate paths, so provider delays do not block importing transactions.

The historical August 2026 benchmark on an 8 GB Apple Silicon MacBook Air measured about **25 MB RSS** at idle, including the Ollama daemon, and about **3.5 GB RSS** for the loaded `qwen3.5:4b` runner. Smaller local models can reduce peak memory. Rules-only mode starts no model process. See [Scale & chaos testing](#scale--chaos-testing) for the original measurements.

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
- Local mode keeps classification on the device. Optional cloud modes send normalized merchant names, Plaid category labels, and allowed bucket names. Cloud asset classification sends asset names only when enabled. API keys are held in the OS credential store. ChatGPT tokens are held in SQLCipher and are excluded from logical backups.
- PocketTrack does not include money-transfer or payment-initiation functionality.

PocketTrack's local data lives outside the Git repository in:

```text
~/.pockettrack/
```

Do not commit backups or secrets. The included `.gitignore` excludes the common local/runtime files.

## Plaid

Use your own Plaid developer credentials to import bank transactions.

PocketTrack uses Plaid's Transactions flow only. It does not need Auth, Transfer, ACH, account/routing-number retrieval, or payment initiation.

For development, set:

```bash
export POCKETTRACK_PLAID_ENVIRONMENT=sandbox
```

For normal use, the startup scripts default to Production.

### Get your Plaid Production Client ID and Secret

You need exactly two values: a **Client ID** and a **Production Secret**. Getting them takes about 2 minutes, plus Plaid's review time.

1. **Create an account** at [dashboard.plaid.com/signup](https://dashboard.plaid.com/signup) and verify your email.

2. **Request Production access.** In the Plaid Dashboard, open the account menu (top right) and choose **Apply for production access** — the same flow may appear as **Start Trial** or **Apply for Trial Plan**.

3. **Complete the application.** Plaid asks for a company/product name, a use-case description, and your contact details. For a personal build, describe it honestly: a personal, local-only, read-only spending and net-worth tracker for your own accounts.

   When asked which **products** you need, select **Transactions** only. PocketTrack never uses Auth, Identity, Transfer, ACH, or payment initiation, and requesting them slows down review.

   > Approval is usually quick but is not always instant — Plaid may email follow-up questions. The Trial Plan connects **real** financial institutions in the Production environment, capped at a small number of connected Items (banks), which is plenty for personal use.

4. **Copy your keys.** Once Production is enabled, go to **Developers → [API Keys](https://dashboard.plaid.com/developers/keys)** and copy:

   | Value | Where it appears | Notes |
   |---|---|---|
   | **Client ID** | `client_id` | One value, shared across environments |
   | **Production Secret** | Secret → **Production** row | Make sure you copy the **Production** secret, not Sandbox |

5. **Keep them handy but do not put them in a file.** Enter them under **Settings → Plaid credentials** after first launch. PocketTrack stores them in your operating system’s credential store.

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

## Automatic sync schedule

On macOS, `start.sh` installs a `launchd` agent that syncs **twice a day, at 8:00 AM and 8:00 PM**. On Windows, use **Sync now** in Settings.

Each run reads *everything* Plaid has for every connected bank — it pages through Plaid's `transactions/sync` cursor until there is nothing left, so a missed run is caught up by the next one rather than skipped.

Check what is actually scheduled, and whether the last run failed:

```bash
pockettrack scheduler-status
```

Change the hours (any number of them, 0–23, local time):

```bash
pockettrack install-scheduler --hours 8,20
```

The agent also runs once when it is loaded, so a reboot or login triggers a catch-up sync. If your Mac is asleep at a scheduled hour, launchd runs the job when it next wakes.

**If automatic sync stops working,** the dashboard shows a warning once the last successful sync is more than 26 hours old. The most common cause is the virtual environment becoming unimportable — check:

```bash
pockettrack scheduler-status
```

and the log at `~/.pockettrack/logs/daily-sync-error.log`. Re-running `./start.sh` reinstalls the agent with a corrected path.

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

To refresh dependencies, run `./start.sh --update` on macOS or `.\start.ps1 -Update` on Windows. To run tests and diagnostics before startup, use `./start.sh --check` or `.\start.ps1 -Check`.

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
- Network access is needed to install dependencies and communicate with Plaid. Optional providers may also need network access.
- On macOS, the startup script can install Homebrew and may prompt for administrator privileges.
- On Windows, `winget` is recommended so `start.ps1` can install Python 3.12.
- Local AI models require additional disk space. The default Ollama model takes about 3.4 GB if you choose to install it.
- On an 8 GB Mac, Rules-only or a cloud provider avoids local model memory use. To use local AI, start with a smaller model and test it on a backfill.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
pockettrack serve
```

The internal Python package remains `cardbudget` for continuity with the original prototype; the distribution, application, CLI, UI, documentation, storage location, and public product name are PocketTrack.

## Scale & chaos testing

Beyond the [Resource usage](#resource-usage) idle/categorizing numbers above, `scripts/scale_chaos_report.py` exercises the app at realistic personal-use scale and injects three specific failure modes, against a real SQLCipher-encrypted database (not a mocked one). It's a manual, standalone script — not part of `pytest -q` — because a full run takes several minutes:

```bash
PYTHONPATH=src .venv/bin/python scripts/scale_chaos_report.py
```

Results below are from the August 19, 2026 run on an 8 GB Apple Silicon MacBook Air. They describe the prior synchronous categorization path and serve as a baseline.

### Scale: read-path latency and database size

"Personal-use realistic" here means what one person actually accumulates: 1–5 linked cards and up to tens of thousands of transactions over a few years. The "large" tier is the worst case for a single user, not a multi-tenant load test.

| Tier | Accounts | Transactions | Seed time | DB file size | `monthly_summary()` (dashboard) | `list_recent(100)` (transactions page) |
|---|---|---|---|---|---|---|
| Small | 2 | 2,000 | 0.10 s | 0.7 MB | 2.3 ms | 3.4 ms |
| Medium | 3 | 15,000 | 0.77 s | 4.2 MB | 13.0 ms | 12.2 ms |
| Large (worst case) | 5 | 50,000 | 2.61 s | 13.7 MB | 102.5 ms | 33.4 ms |

Even at 50,000 transactions — well beyond what most people will accumulate — the dashboard's core query stays around a tenth of a second and the database itself is under 14 MB. Nothing here comes close to being the bottleneck; the local LLM call (below) dominates every other cost in the system by roughly three orders of magnitude.

### Live local-LLM categorization latency

40 real transactions, real Ollama, real `qwen3.5:4b` inference (not mocked):

| | Value |
|---|---|
| p50 per-transaction latency | 2.45 s |
| p95 per-transaction latency | 2.81 s |
| max | 2.94 s |
| Estimated time for a full 150-transaction sync batch (`DEFAULT_BATCH_LIMIT`) | ~6 minutes, at p50 |

That per-call figure is higher than the "~1–2 seconds" quoted in [Resource usage](#resource-usage) above — the difference is real system load, not a different code path: this measurement was taken with the host already at 91–93% memory use from the scale/chaos run itself, a genuine demonstration of how much slower local inference gets under real memory pressure on an 8 GB machine, not just a theoretical concern. Both numbers are honestly reported rather than reconciled to one "clean" figure.

### Chaos scenario 1: Ollama unreachable mid-categorization

200 unassigned transactions, the local model forced unreachable on every call.

- Completed in 731.8 ms — no crash, no hang, no retry storm.
- Exactly 1 real call attempt was made before the service stopped calling the model for the rest of the batch (`ollama_unavailable=True`), falling the remaining 199 straight through to `Unknown`.
- Process memory showed no leak or spike from the failure path.
- **Verified:** matches the documented graceful-degradation behavior — a downed Ollama daemon degrades one sync's categorization quality, it does not degrade the app.

### Chaos scenario 2: Plaid API errors mid-sync across multiple linked banks

4 linked banks in one `sync_all()` call: 1 returns a simulated 500-style error, 1 returns a simulated reauth-required error, 2 succeed normally.

- `sync_all()` completed in 6.0 ms without raising — one failing connection does not block or slow down the others.
- Result: `items_synced=2 failed_items=2`, exactly as expected; each failing item's error code was recorded individually (`INTERNAL_SERVER_ERROR`, `ITEM_LOGIN_REQUIRED`) rather than one bank's failure being conflated with another's.
- **Verified — recovery:** once the simulated outage was cleared, a follow-up `sync_all()` synced all 4 items cleanly (`failed_items=0`) with no manual intervention required.

### Chaos scenario 3: concurrent reads during a large write (SQLite lock contention)

12 threads continuously reading `list_recent()` while a single 5,000-row write batch lands, against 15,000 pre-existing rows (`journal_mode=DELETE`, `busy_timeout=5000ms` per `db/engine.py`).

| | Value |
|---|---|
| Write batch duration (5,000 rows, under concurrent read load) | 27.1 s |
| Concurrent reads completed during that window | 3,137 |
| Read latency p50 / p95 / max | 105 ms / 135 ms / 200 ms |
| `database is locked` errors surfaced to callers | **0** |

`busy_timeout` did its job — no caller ever saw a locking error. The real cost is elsewhere: that same 5,000-row write takes roughly 2.6 seconds with no concurrent readers (see the seed-time-per-row rate in the scale table above), so sustained concurrent reads slowed the writer down by roughly **10x** in this run. For a single-user local app this is an acceptable trade (nobody is blocked, everything eventually completes), but it is a real, measured cost of PocketTrack's current rollback-journal mode under simultaneous heavy read+write activity — not merely a theoretical one.

### An honest side effect of running this

Running the full benchmark (which includes ~55 real local-LLM calls back to back) pushed this 8 GB machine's real system memory to 91–93% for a period. While at that level, `pytest -q`'s own `test_local_llm_categorizes_posted_but_not_pending` — a test that uses a fake LLM client but exercises the *real*, unmocked memory-pressure guard — genuinely failed, because that guard checks whole-system memory, not PocketTrack's own footprint, and correctly decided the host was too loaded to categorize. Re-running the same test with the guard temporarily bypassed confirmed the underlying code is correct; the failure was the guard doing exactly what it's designed to do, triggered by this benchmark's own resource use rather than by any defect. It's included here rather than quietly worked around because it's a genuine, reproducible illustration of the 90% threshold's real-world reach on constrained hardware.

## License

MIT. See [LICENSE](LICENSE).
