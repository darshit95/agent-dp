# PocketTrack Architecture

PocketTrack is a single-user local FastAPI application. The backend binds only to `127.0.0.1:8000`. On macOS, `start.sh` places Caddy in front of it on `https://my-pocket-track` using a locally trusted internal certificate and a loopback-only bind.

## Components

- FastAPI + Jinja templates: local UI/backend.
- SQLCipher: encrypted SQLite application data.
- macOS Keychain: Plaid credentials/access tokens and local encryption/session secrets.
- Plaid Transactions: read-only credit-card transaction ingestion.
- Categorization worker: processes durable SQLCipher work, applies saved rules and high-confidence Plaid categories, and optionally calls the selected model provider.
- Model providers: rules only, Ollama, a loopback OpenAI-compatible endpoint, ChatGPT plan authorization, or OpenAI and Claude API keys.
- macOS launchd: transaction sync at 8 AM and 8 PM.
- Caddy: loopback-only local HTTPS reverse proxy.

## Data flow

1. The user connects a financial institution using Plaid Link.
2. PocketTrack stores the Plaid access token in Keychain and non-secret account metadata in SQLCipher.
3. The user enables the credit-card accounts they want to track.
4. Daily sync imports posted transactions only and drops pending/payment/AutoPay rows.
5. Sync commits imports and queues categorization. The worker applies local rules, then processes eligible unresolved spending or assets through the selected provider.
6. Automatic writes check that the source record is still current. Deferred jobs stay eligible for retries. Budgets and net-worth calculations use local application logic.

No component contains payment initiation or money-transfer capability.
