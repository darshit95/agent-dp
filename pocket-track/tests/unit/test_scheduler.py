from __future__ import annotations

import plistlib

import pytest

from cardbudget.scheduler import macos


def test_launchd_schedule_runs_twice_a_day_by_default(test_stack, monkeypatch):
    settings, _store, _db, _services, _client = test_stack
    monkeypatch.setattr(macos.sys, "platform", "darwin")
    plist = macos.build_plist(settings)
    assert plist["Label"] == "com.pockettrack.daily-sync"
    assert plist["StartCalendarInterval"] == [{"Hour": 8, "Minute": 0}, {"Hour": 20, "Minute": 0}]
    assert plist["ProgramArguments"][-2:] == ["cardbudget", "daily-sync"]
    assert plist["EnvironmentVariables"]["POCKETTRACK_DATA_DIR"] == str(settings.data_dir)


def test_custom_hours_are_sorted_and_deduplicated(test_stack, monkeypatch):
    settings, _store, _db, _services, _client = test_stack
    monkeypatch.setattr(macos.sys, "platform", "darwin")
    plist = macos.build_plist(settings, hours=[20, 6, 20])
    assert plist["StartCalendarInterval"] == [{"Hour": 6, "Minute": 0}, {"Hour": 20, "Minute": 0}]


def test_a_single_hour_still_works(test_stack, monkeypatch):
    settings, _store, _db, _services, _client = test_stack
    monkeypatch.setattr(macos.sys, "platform", "darwin")
    plist = macos.build_plist(settings, hours=[8])
    assert plist["StartCalendarInterval"] == [{"Hour": 8, "Minute": 0}]


@pytest.mark.parametrize("hours", [[], [24], [-1], [8, 99]])
def test_invalid_hours_are_rejected(hours):
    with pytest.raises(ValueError):
        macos.normalize_hours(hours)


def test_agent_pins_pythonpath_so_a_broken_pth_cannot_silence_the_sync(test_stack, monkeypatch):
    """The venv's .pth can stop being read (e.g. cloud-sync marks it hidden),
    which previously left the scheduled sync failing with ModuleNotFoundError."""
    settings, _store, _db, _services, _client = test_stack
    monkeypatch.setattr(macos.sys, "platform", "darwin")
    plist = macos.build_plist(settings)

    import cardbudget

    expected = str(macos.Path(cardbudget.__file__).resolve().parents[1])
    assert plist["EnvironmentVariables"]["PYTHONPATH"] == expected


def test_agent_syncs_after_a_reboot(test_stack, monkeypatch):
    settings, _store, _db, _services, _client = test_stack
    monkeypatch.setattr(macos.sys, "platform", "darwin")
    assert macos.build_plist(settings)["RunAtLoad"] is True


def test_scheduled_hours_are_read_back_from_the_plist(test_stack, monkeypatch, tmp_path):
    settings, _store, _db, _services, _client = test_stack
    monkeypatch.setattr(macos.sys, "platform", "darwin")
    path = tmp_path / "agent.plist"
    with path.open("wb") as fh:
        plistlib.dump(macos.build_plist(settings, hours=[8, 20]), fh)

    assert macos.scheduled_hours(path) == (8, 20)


def test_scheduled_hours_handles_the_older_single_dict_form(tmp_path):
    path = tmp_path / "legacy.plist"
    with path.open("wb") as fh:
        plistlib.dump({"Label": "x", "StartCalendarInterval": {"Hour": 8, "Minute": 0}}, fh)

    assert macos.scheduled_hours(path) == (8,)


def test_scheduled_hours_of_a_missing_plist_is_empty(tmp_path):
    assert macos.scheduled_hours(tmp_path / "nope.plist") == ()


def test_legacy_labels_cover_previously_shipped_agents():
    """An old agent left loaded keeps syncing on its own schedule, unnoticed by
    scheduler-status, which only inspects the current LABEL."""
    assert "com.pockettrack.bidaily-sync" in macos.LEGACY_LABELS
    assert macos.LABEL not in macos.LEGACY_LABELS


def test_install_skips_reload_when_already_up_to_date(test_stack, monkeypatch, tmp_path):
    """RunAtLoad fires an immediate sync + local-LLM categorization pass on every
    reload. Reinstalling an unchanged, already-loaded agent must not touch
    launchd, or every ordinary app restart would trigger a fresh background
    sync burst for no reason (this is what made an 8 GB machine choke)."""
    settings, _store, _db, _services, _client = test_stack
    monkeypatch.setattr(macos.sys, "platform", "darwin")
    plist_path = tmp_path / "agent.plist"
    monkeypatch.setattr(macos, "launch_agent_path", lambda: plist_path)
    monkeypatch.setattr(macos, "_launchctl_loaded", lambda label=macos.LABEL: True)

    def _forbidden_run(*args, **kwargs):
        raise AssertionError("launchctl/subprocess must not run when nothing changed")

    payload = macos.build_plist(settings, hours=(8, 20))
    with plist_path.open("wb") as fh:
        plistlib.dump(payload, fh)
    monkeypatch.setattr(macos.subprocess, "run", _forbidden_run)

    result = macos.install(settings, hours=(8, 20))
    assert result.loaded is True
    assert "skipped" in result.detail


def test_install_reloads_when_configuration_changed(test_stack, monkeypatch, tmp_path):
    settings, _store, _db, _services, _client = test_stack
    monkeypatch.setattr(macos.sys, "platform", "darwin")
    plist_path = tmp_path / "agent.plist"
    monkeypatch.setattr(macos, "launch_agent_path", lambda: plist_path)
    monkeypatch.setattr(macos, "_launchctl_loaded", lambda label=macos.LABEL: True)

    # Stale plist on disk (different hours) - a real config change.
    with plist_path.open("wb") as fh:
        plistlib.dump(macos.build_plist(settings, hours=(9,)), fh)

    calls = []

    class _Result:
        returncode = 0
        stderr = ""

    def _fake_run(*args, **kwargs):
        calls.append(args[0])
        return _Result()

    monkeypatch.setattr(macos.subprocess, "run", _fake_run)

    result = macos.install(settings, hours=(8, 20))
    assert result.loaded is True
    assert any("bootstrap" in call for call in calls)
