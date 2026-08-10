# PocketTrack Architecture

PocketTrack is a single-user local FastAPI application. The backend binds only to `127.0.0.1:8000`. On macOS, `start.sh` places Caddy in front of it on `https://my-pocket-track` using a locally trusted internal certificate and a loopback-only bind.

## Components

- FastAPI + Jinja templates: local UI/backend.
- SQLCipher: encrypted SQLite application data.
- macOS Keychain: Plaid credentials/access tokens and local encryption/session secrets.
- Plaid Transactions: read-only credit-card transaction ingestion.
- Ollama: local transaction and asset classification.
- macOS launchd: daily 8 AM transaction sync.
- Caddy: loopback-only local HTTPS reverse proxy.

## Data flow

1. The user connects a financial institution using Plaid Link.
2. PocketTrack stores the Plaid access token in Keychain and non-secret account metadata in SQLCipher.
3. The user enables the credit-card accounts they want to track.
4. Daily sync imports posted transactions only and drops pending/payment/AutoPay rows.
5. Local rules and Ollama classify unassigned spending.
6. Budgets and net-worth calculations are deterministic application logic.

No component contains payment initiation or money-transfer capability.
