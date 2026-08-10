# Release checklist

- [x] Localhost-only FastAPI bind.
- [x] Local HTTPS at `https://my-pocket-track` through loopback-only Caddy.
- [x] SQLCipher database encryption.
- [x] Keychain secret storage.
- [x] Argon2id password hashing, server sessions, CSRF and login throttling.
- [x] Generic Plaid credit-card discovery (no hardcoded card names).
- [x] Posted-only transaction sync, payment/AutoPay exclusion and user-delete tombstones.
- [x] Daily scheduler and historical month backfill.
- [x] Dynamic budgets and local categorization.
- [x] Net-worth assets/liabilities and allocation chart.
- [x] Inline asset name/institution/value editing.
- [x] Encrypted backup/restore and password change.
- [x] GitHub CI, MIT license and publish helper.
- [x] Startup/stop scripts.
- [ ] Validate real institution transactions against statements before relying on totals.
- [ ] Review Plaid production access and institution-specific OAuth behavior for each user.
