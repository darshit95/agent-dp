from __future__ import annotations

import argparse
import getpass
import sys
from datetime import datetime
from pathlib import Path

import uvicorn

from cardbudget.app import create_app
from cardbudget.backup import BackupError, BackupService
from cardbudget.config import Settings
from cardbudget.db.engine import Database
from cardbudget.errors import CardBudgetError
from cardbudget.plaid.client import PlaidAPIError
from cardbudget.scheduler import autostart as app_autostart
from cardbudget.scheduler import macos as macos_scheduler
from cardbudget.services import bootstrap_services


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pockettrack", description="PocketTrack local spending and net-worth monitor")
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve", help="Run the localhost-only web application")
    serve.add_argument("--port", type=int, default=None, help="Loopback port (default 8000)")

    sub.add_parser("doctor", help="Run non-secret security and dependency checks")
    sub.add_parser("verify-encryption", help="Verify the DB rejects plaintext SQLite and a wrong SQLCipher key")
    sub.add_parser("daily-sync", help="Sync posted Plaid transactions and categorize them")
    sub.add_parser("monthly-sync", help="Compatibility alias for daily-sync")
    backfill = sub.add_parser("backfill", help="Import a historical month, e.g. 2026-07")
    backfill.add_argument("month", help="Month in YYYY-MM format")

    scheduler = sub.add_parser("install-scheduler", help="Install the free macOS automatic sync schedule")
    scheduler.add_argument(
        "--hours",
        default=",".join(str(h) for h in macos_scheduler.DEFAULT_SYNC_HOURS),
        help="Comma-separated local hours to sync every day (0-23; default 8,20)",
    )
    scheduler.add_argument("--hour", type=int, default=None, help="Legacy single-hour form; overrides --hours")
    sub.add_parser("uninstall-scheduler", help="Remove the PocketTrack macOS launchd schedule")
    sub.add_parser("scheduler-status", help="Show whether the PocketTrack daily scheduler is installed and loaded")
    sub.add_parser("install-autostart", help="Keep the web app running and restart it at login")
    sub.add_parser("uninstall-autostart", help="Stop the web app and disable start-at-login")
    sub.add_parser("autostart-status", help="Show whether the web app autostart agent is installed and loaded")
    backup = sub.add_parser("backup", help="Create a password-encrypted logical backup with no Plaid secrets")
    backup.add_argument("--output", default=None, help="Output .ptbackup path (default: ~/Documents/PocketTrack-Backup-<timestamp>.ptbackup)")
    restore = sub.add_parser("restore", help="Restore a PocketTrack logical backup into the encrypted database")
    restore.add_argument("path", help="Path to .ptbackup file")
    restore.add_argument("--yes", action="store_true", help="Skip the destructive restore confirmation")
    return parser


def _settings_with_port(port: int | None) -> Settings:
    settings = Settings.from_env()
    if port is None:
        return settings
    return settings.model_copy(update={"port": port})


def _wrong_key_is_rejected(database: Database) -> bool:
    if not database.path.exists():
        return False
    try:
        from sqlcipher3 import dbapi2 as sqlcipher
    except Exception:
        return False
    wrong = "00" * 32
    if wrong == database.key_hex:
        wrong = "11" * 32
    conn = sqlcipher.connect(str(database.path))
    try:
        conn.execute(f"PRAGMA key = \"x'{wrong}'\"")
        conn.execute("SELECT count(*) FROM sqlite_master").fetchone()
        return False
    except Exception:
        return True
    finally:
        conn.close()


def _doctor(settings: Settings) -> int:
    services = bootstrap_services(settings)
    db = services.database
    cipher_version = db.cipher_version()
    integrity_ok = db.integrity_check()
    checks = [
        ("Loopback bind", settings.host == "127.0.0.1", settings.host),
        ("SQLCipher active", bool(cipher_version), cipher_version or "unavailable"),
        ("Plain SQLite header absent", not db.has_plaintext_sqlite_header(), "encrypted header"),
        ("DB integrity", integrity_ok, "ok" if integrity_ok else "failed"),
        ("Standard SQLite rejected", db.standard_sqlite_is_rejected(), "expected rejection"),
    ]
    failed = False
    for name, ok, detail in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
        failed = failed or not ok
    ollama_reachable, model_installed = services.ollama.status()
    ram_note = ""
    try:
        import psutil

        ram_note = f"; system has {psutil.virtual_memory().total / (1024 ** 3):.1f} GB RAM"
    except Exception:
        pass
    print(
        f"{'PASS' if ollama_reachable and model_installed else 'INFO'}  Local AI: "
        f"{'ready' if ollama_reachable and model_installed else 'not ready'} ({settings.ollama_model}{ram_note})"
    )
    print(f"INFO  Plaid {settings.plaid_environment}: {'configured' if services.plaid.credentials_configured() else 'not configured'}")
    scheduler = macos_scheduler.status()
    print(f"INFO  Daily scheduler: {'loaded' if scheduler.loaded else ('installed, not loaded' if scheduler.installed else 'not installed')}")
    print(f"INFO  Data directory: {settings.data_dir}")
    print("INFO  Secrets: OS keychain (values intentionally not displayed)")
    return 1 if failed else 0


def _daily_sync(settings: Settings) -> int:
    services = bootstrap_services(settings)
    if not services.auth.is_initialized():
        print("PocketTrack setup has not been completed yet.", file=sys.stderr)
        return 2
    if not services.plaid.credentials_configured():
        print("Plaid credentials are not configured. Open Settings in PocketTrack first.", file=sys.stderr)
        return 2
    try:
        sync = services.plaid.sync_all()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except PlaidAPIError as exc:
        print(f"Plaid sync failed: {exc.error_code}", file=sys.stderr)
        return 4
    services.audit.record("transactions_synced")
    categorized = services.categorization.categorize_unassigned()
    services.audit.record("categorization_run")
    print(
        "SYNC  "
        f"items={sync.items_synced} failed={sync.failed_items} added={sync.added} modified={sync.modified} "
        f"removed={sync.removed} ignored_unmapped={sync.ignored_unmapped} "
        f"ignored_pending={sync.ignored_pending} ignored_payments={sync.ignored_payments} "
        f"ignored_deleted={sync.ignored_deleted}"
    )
    print(
        "CATEGORIZATION  "
        f"rules={categorized.rule_applied} local_llm={categorized.llm_applied} "
        f"uncategorized={categorized.left_uncategorized}"
    )
    if categorized.ollama_unavailable:
        print("INFO  Ollama was unavailable; transactions remain available for manual categorization.")
    if categorized.memory_paused:
        print("INFO  Paused local categorization early due to low system memory; remainder will run on the next sync.")
    return 0


def _backfill(settings: Settings, month: str) -> int:
    services = bootstrap_services(settings)
    if not services.auth.is_initialized():
        print("PocketTrack setup has not been completed yet.", file=sys.stderr)
        return 2
    if not services.plaid.credentials_configured():
        print("Plaid credentials are not configured. Open Settings in PocketTrack first.", file=sys.stderr)
        return 2
    try:
        result = services.plaid.backfill_month(month)
    except (ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 3
    services.audit.record("historical_backfill")
    categorized = services.categorization.categorize_unassigned()
    print(
        "BACKFILL  "
        f"month={result.month} imported={result.imported} failed={result.failed_items} "
        f"ignored_pending={result.ignored_pending} ignored_payments={result.ignored_payments} "
        f"ignored_deleted={result.ignored_deleted}"
    )
    print(f"CATEGORIZATION  rules={categorized.rule_applied} local_llm={categorized.llm_applied} unknown={categorized.left_uncategorized}")
    if categorized.memory_paused:
        print("INFO  Paused local categorization early due to low system memory; remainder will run on the next sync.")
    return 0


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)
    try:
        settings = _settings_with_port(getattr(args, "port", None))
        if args.command == "serve":
            app = create_app(settings)
            # The validated Settings model makes 0.0.0.0/LAN binds impossible here.
            uvicorn.run(
                app,
                host=settings.host,
                port=settings.port,
                access_log=False,
                server_header=False,
                proxy_headers=False,
            )
            return
        if args.command == "doctor":
            raise SystemExit(_doctor(settings))
        if args.command == "verify-encryption":
            services = bootstrap_services(settings)
            db = services.database
            standard_rejected = db.standard_sqlite_is_rejected()
            wrong_key_rejected = _wrong_key_is_rejected(db)
            print(f"{'PASS' if standard_rejected else 'FAIL'}  Standard SQLite cannot read database")
            print(f"{'PASS' if wrong_key_rejected else 'FAIL'}  Wrong SQLCipher key cannot read database")
            raise SystemExit(0 if standard_rejected and wrong_key_rejected else 1)
        if args.command in {"daily-sync", "monthly-sync"}:
            raise SystemExit(_daily_sync(settings))
        if args.command == "backfill":
            raise SystemExit(_backfill(settings, args.month))
        if args.command == "install-scheduler":
            try:
                requested = (args.hour,) if args.hour is not None else [
                    part for part in args.hours.replace(" ", "").split(",") if part
                ]
                hours = macos_scheduler.normalize_hours(requested)
            except ValueError as exc:
                print(f"Invalid --hours value: {exc}", file=sys.stderr)
                raise SystemExit(2) from exc
            result = macos_scheduler.install(settings, hours=hours)
            print(f"Scheduler file: {result.plist_path}")
            print(f"Status: {result.detail}")
            print(f"Schedule: every day at {', '.join(f'{h:02d}:00' for h in hours)} local time")
            raise SystemExit(0 if result.loaded else 1)
        if args.command == "install-autostart":
            path, loaded, detail = app_autostart.install(settings)
            print(f"Autostart file: {path}")
            print(f"Status: {detail}")
            print("PocketTrack will start at login and restart itself if it exits.")
            raise SystemExit(0 if loaded else 1)
        if args.command == "uninstall-autostart":
            removed = app_autostart.uninstall()
            print("Autostart removed; PocketTrack is stopped." if removed else "Autostart was not installed.")
            return
        if args.command == "autostart-status":
            state = app_autostart.status()
            print(f"{'INSTALLED' if state.installed else 'NOT INSTALLED'}  {state.plist_path}")
            print(f"{'LOADED' if state.loaded else 'NOT LOADED'}  launchd agent")
            return
        if args.command == "uninstall-scheduler":
            removed = macos_scheduler.uninstall()
            print("Scheduler removed." if removed else "Scheduler was not installed.")
            return
        if args.command == "scheduler-status":
            status = macos_scheduler.status()
            print(f"{'INSTALLED' if status.installed else 'NOT INSTALLED'}  {status.plist_path}")
            print(f"{'LOADED' if status.loaded else 'NOT LOADED'}  launchd job")
            if status.hours:
                print(f"SCHEDULE   every day at {', '.join(f'{h:02d}:00' for h in status.hours)} local time")
            last_error = settings.data_dir / "logs" / "daily-sync-error.log"
            if last_error.exists() and last_error.stat().st_size > 0:
                tail = last_error.read_text(errors="replace").strip().splitlines()[-1:]
                if tail:
                    print(f"LAST ERROR {tail[0]}")
            return
        if args.command == "backup":
            services = bootstrap_services(settings)
            output = Path(args.output).expanduser() if args.output else (
                Path.home() / "Documents" / f"PocketTrack-Backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.ptbackup"
            )
            password = getpass.getpass("Backup password (12+ characters): ")
            confirm = getpass.getpass("Confirm backup password: ")
            if password != confirm:
                print("Backup passwords do not match.", file=sys.stderr)
                raise SystemExit(2)
            try:
                path = BackupService(services.database).create(output, password)
            except BackupError as exc:
                print(str(exc), file=sys.stderr)
                raise SystemExit(2)
            services.audit.record("backup_created")
            print(f"Backup created: {path}")
            print("Plaid credentials/access tokens were not included.")
            return
        if args.command == "restore":
            services = bootstrap_services(settings)
            if not args.yes:
                answer = input("This replaces local PocketTrack data with the backup. Type RESTORE to continue: ")
                if answer != "RESTORE":
                    print("Restore cancelled.")
                    return
            password = getpass.getpass("Backup password: ")
            try:
                BackupService(services.database).restore(Path(args.path), password)
            except BackupError as exc:
                print(str(exc), file=sys.stderr)
                raise SystemExit(2)
            print("Backup restored. Plaid secrets remain managed separately in the OS Keychain.")
            return
    except CardBudgetError as exc:
        print(f"PocketTrack refused to start: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
