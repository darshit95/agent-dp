from pathlib import Path

import pytest

from cardbudget.backup import BackupError, BackupService


def test_backup_restore_round_trip_without_secrets(test_stack, tmp_path: Path):
    _settings, store, _db, services, _client = test_stack
    services.auth.setup_user("backupuser", "correct-horse-battery-staple")
    services.networth_repository.create_asset(
        name="Emergency Funds", institution="Example Bank", value_cents=123400, asset_bucket="Cash & Cash Equivalents", include=True
    )
    store.set_secret("plaid-secret:production", "super-secret-token")
    backup = tmp_path / "test.ptbackup"
    BackupService(services.database).create(backup, "very-strong-backup-password")
    assert b"super-secret-token" not in backup.read_bytes()

    services.networth_repository.delete_asset(services.networth_repository.list_assets()[0].id)
    assert services.networth_repository.list_assets() == []
    BackupService(services.database).restore(backup, "very-strong-backup-password")
    assert services.networth_repository.list_assets()[0].name == "Emergency Funds"

    with pytest.raises(BackupError):
        BackupService(services.database).restore(backup, "wrong-password-12345")
