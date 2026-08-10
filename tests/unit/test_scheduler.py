from __future__ import annotations

from cardbudget.scheduler import macos


def test_launchd_schedule_runs_every_morning(test_stack, monkeypatch):
    settings, _store, _db, _services, _client = test_stack
    monkeypatch.setattr(macos.sys, "platform", "darwin")
    plist = macos.build_plist(settings, hour=8)
    assert plist["Label"] == "com.pockettrack.daily-sync"
    assert plist["StartCalendarInterval"] == {"Hour": 8, "Minute": 0}
    assert plist["ProgramArguments"][-2:] == ["cardbudget", "daily-sync"]
    assert plist["EnvironmentVariables"]["POCKETTRACK_DATA_DIR"] == str(settings.data_dir)
