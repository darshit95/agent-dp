# PocketTrack Security

PocketTrack is designed for one user on one local Mac. The provided launcher binds both the application and HTTPS proxy to loopback only.

## Security boundaries

- Do not expose port 8000 or the local Caddy listener to a LAN or the public internet.
- Do not commit `~/.pockettrack`, `.runtime`, `.env`, backup files, Plaid credentials, or Keychain exports.
- Use Plaid Transactions only; PocketTrack contains no payment or money-movement integration.
- Keep macOS, Python dependencies, Caddy, Ollama, and your browser updated.
- Review dependency updates and run the included tests before upgrading production data.

## Secret storage

Sensitive runtime secrets are stored in the operating-system Keychain. The encrypted SQLCipher database stores application data but not Plaid access tokens/secrets.

## Reporting a vulnerability

If this repository is published publicly, use GitHub's private security-advisory feature rather than opening a public issue containing exploit details or financial information.
