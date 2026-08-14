from __future__ import annotations

import re
from pathlib import Path

import pytest

from cardbudget.db.schema import ASSET_BUCKETS, DEFAULT_BUCKETS
from cardbudget.icons import (
    BUCKET_ICON_CHOICES,
    DEFAULT_BUCKET_ICON,
    ICONS,
    asset_bucket_icon,
    bucket_icon,
    liability_icon,
    normalize_icon_id,
    suggest_bucket_icon,
)

SPRITE = Path(__file__).resolve().parents[2] / "src" / "cardbudget" / "web" / "templates" / "base.html"


def _sprite_symbol_ids() -> set[str]:
    return set(re.findall(r'<symbol id="i-([a-z0-9-]+)"', SPRITE.read_text()))


def test_every_catalog_icon_has_a_sprite_symbol():
    """A missing symbol renders as an invisible <use>, so keep the two in sync."""
    missing = {icon_id for icon_id in ICONS if icon_id not in _sprite_symbol_ids()}
    assert not missing, f"icons.py references sprite symbols that base.html does not define: {sorted(missing)}"


def test_picker_choices_are_all_known_icons():
    assert {choice.id for choice in BUCKET_ICON_CHOICES} <= set(ICONS)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Dining", "dining"),
        ("Restaurants & takeout", "dining"),
        ("Coffee", "coffee"),
        ("Grocery", "grocery"),
        ("Groceries", "grocery"),
        ("Gas + Car Wash", "car"),
        ("Subscriptions", "repeat"),
        ("Shopping", "shopping"),
        ("Rent", "home"),
        ("Utilities", "bolt"),
        ("Gym", "fitness"),
        ("Travel", "travel"),
        ("Pet care", "pet"),
        ("Books", "education"),
        ("Unknown", DEFAULT_BUCKET_ICON),
        ("Zzzz nonsense", DEFAULT_BUCKET_ICON),
        ("", DEFAULT_BUCKET_ICON),
    ],
)
def test_bucket_names_map_to_recognizable_icons(name, expected):
    assert bucket_icon(name).id == expected
    assert suggest_bucket_icon(name) == expected


def test_every_default_bucket_gets_a_non_placeholder_icon_except_unknown():
    for name in DEFAULT_BUCKETS:
        icon = bucket_icon(name)
        if name == "Unknown":
            assert icon.id == DEFAULT_BUCKET_ICON
        else:
            assert icon.id != DEFAULT_BUCKET_ICON, f"{name} fell back to the placeholder icon"


def test_stored_icon_overrides_the_keyword_guess():
    assert bucket_icon("Grocery", "piggy").id == "piggy"


def test_unknown_stored_icon_falls_back_to_the_keyword_guess():
    # A value from an older release or a hand-edited database must never reach the
    # template as-is; it would render a sprite reference that does not exist.
    assert bucket_icon("Grocery", "not-a-real-icon").id == "grocery"
    assert bucket_icon("Grocery", "").id == "grocery"


def test_normalize_icon_id_rejects_unknown_values():
    assert normalize_icon_id("dining") == "dining"
    assert normalize_icon_id("  DINING  ") == "dining"
    assert normalize_icon_id("<script>") == DEFAULT_BUCKET_ICON
    assert normalize_icon_id(None) == DEFAULT_BUCKET_ICON


def test_every_asset_bucket_has_a_distinct_icon():
    icons = [asset_bucket_icon(bucket).id for bucket in ASSET_BUCKETS]
    assert len(set(icons)) == len(ASSET_BUCKETS)
    assert set(icons) <= set(ICONS)


def test_asset_bucket_tints_are_distinct():
    """Categories sit side by side in the allocation legend, so tints must differ."""
    tints = [asset_bucket_icon(bucket).tint for bucket in ASSET_BUCKETS]
    assert len(set(tints)) == len(ASSET_BUCKETS)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Mortgage", "home"),
        ("Student loan", "education"),
        ("Auto loan", "car"),
        ("Chase Sapphire card", "card"),
        ("Personal loan", "bank"),
        ("Something else", "bank"),
    ],
)
def test_liability_names_map_to_icons(name, expected):
    assert liability_icon(name).id == expected


def test_every_icon_has_a_tint_and_label():
    for icon in ICONS.values():
        assert icon.label
        assert icon.tint
