"""Icon catalog shared by the dashboard and the net-worth view.

Every icon id maps to an SVG sprite symbol (``#i-<id>``) defined in
``web/templates/base.html``. Buckets may store an explicit choice; when they do
not, the name is matched against keywords so a manually created bucket still
gets something recognizable instead of a generic placeholder.

Only ids present in ``ICONS`` are ever rendered — ``normalize_icon_id`` rejects
anything else, so a stored or submitted value can never inject a sprite
reference the templates do not control.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Icon:
    id: str
    label: str
    tint: str


# Tints are CSS classes (.tint-<name>) defined in web/static/app.css.
ICONS: dict[str, Icon] = {
    icon.id: icon
    for icon in (
        Icon("tag", "Other", "slate"),
        Icon("dining", "Dining out", "peach"),
        Icon("coffee", "Coffee", "sand"),
        Icon("grocery", "Groceries", "mint"),
        Icon("shopping", "Shopping", "grape"),
        Icon("car", "Car & transport", "sky"),
        Icon("home", "Home & rent", "teal"),
        Icon("bolt", "Utilities", "sun"),
        Icon("phone", "Phone & internet", "sky"),
        Icon("repeat", "Subscriptions", "lilac"),
        Icon("health", "Health", "rose"),
        Icon("fitness", "Fitness", "mint"),
        Icon("travel", "Travel", "sky"),
        Icon("film", "Entertainment", "grape"),
        Icon("gift", "Gifts & giving", "rose"),
        Icon("pet", "Pets", "sand"),
        Icon("education", "Education", "lilac"),
        Icon("piggy", "Savings", "mint"),
        Icon("card", "Card & payments", "slate"),
        Icon("bank", "Banking & fees", "slate"),
        # Net-worth category tints echo the donut colours (.allocation-0..4) so a
        # category looks the same in the chart, the legend and the row icon.
        Icon("cash", "Cash", "sky"),
        Icon("growth", "Investments", "mint"),
        Icon("shield", "Retirement & health", "lilac"),
        Icon("gem", "Alternatives", "sun"),
        Icon("box", "Other assets", "slate"),
    )
}

DEFAULT_BUCKET_ICON = "tag"
DEFAULT_LIABILITY_ICON = "bank"

# Offered in the bucket icon picker, in the order shown.
BUCKET_ICON_CHOICES: tuple[Icon, ...] = tuple(
    ICONS[icon_id]
    for icon_id in (
        "tag", "dining", "coffee", "grocery", "shopping", "car", "home", "bolt",
        "phone", "repeat", "health", "fitness", "travel", "film", "gift", "pet",
        "education", "piggy", "card", "bank",
    )
)

# Checked in order; the first icon with a matching keyword wins, so more
# specific categories must come before broader ones.
_BUCKET_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("coffee", ("coffee", "cafe", "café", "espresso", "tea", "boba")),
    ("grocery", ("grocery", "groceries", "supermarket", "market", "produce", "pantry")),
    ("dining", ("dining", "restaurant", "dine", "food", "eat", "eating", "takeout",
                "take out", "meal", "lunch", "dinner", "brunch", "breakfast", "pizza",
                "burger", "bar", "drinks")),
    ("car", ("gas", "gasoline", "fuel", "car", "auto", "vehicle", "car wash", "wash",
             "parking", "toll", "transit", "commute", "rideshare", "uber", "lyft",
             "transport", "transportation")),
    ("home", ("home", "rent", "mortgage", "house", "housing", "furniture", "decor",
              "garden", "repair", "maintenance")),
    ("bolt", ("utility", "utilities", "electric", "electricity", "power", "water",
              "gas bill", "energy", "heating", "trash")),
    ("phone", ("phone", "mobile", "cell", "internet", "wifi", "broadband", "cable")),
    ("repeat", ("subscription", "subscriptions", "streaming", "membership", "recurring",
                "saas", "netflix", "spotify")),
    ("health", ("health", "medical", "doctor", "pharmacy", "prescription", "dental",
                "dentist", "vision", "therapy", "insurance", "clinic")),
    ("fitness", ("gym", "fitness", "workout", "yoga", "pilates", "sport", "sports",
                 "running", "climbing")),
    ("travel", ("travel", "flight", "flights", "airfare", "airline", "hotel", "vacation",
                "trip", "holiday", "lodging", "airbnb")),
    ("film", ("entertainment", "movie", "movies", "cinema", "theatre", "theater", "game",
              "gaming", "music", "concert", "hobby", "hobbies", "fun", "leisure")),
    ("gift", ("gift", "gifts", "present", "presents", "donation", "donations", "charity",
              "giving")),
    ("pet", ("pet", "pets", "dog", "cat", "vet", "veterinary")),
    ("education", ("education", "school", "tuition", "book", "books", "course",
                   "courses", "learning", "student", "college", "university", "childcare",
                   "daycare", "kids")),
    ("piggy", ("saving", "savings", "invest", "investing", "investment", "emergency",
               "retirement", "nest egg")),
    ("card", ("card", "credit", "payment", "payments")),
    ("bank", ("bank", "banking", "fee", "fees", "tax", "taxes", "loan", "loans",
              "interest", "debt")),
    ("shopping", ("shopping", "shop", "clothes", "clothing", "apparel", "shoes",
                  "retail", "amazon", "merchandise", "personal care", "beauty",
                  "household", "supplies")),
)

_LIABILITY_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("home", ("mortgage", "home", "house", "heloc", "property")),
    ("education", ("student", "tuition", "school", "college", "university")),
    ("car", ("auto", "car", "vehicle", "lease")),
    ("card", ("card", "credit", "amex", "visa", "mastercard")),
    ("health", ("medical", "health", "hospital", "dental")),
    ("bank", ("loan", "line of credit", "personal", "bank", "tax", "taxes", "debt")),
)

_ASSET_BUCKET_ICONS: dict[str, str] = {
    "Cash & Cash Equivalents": "cash",
    "Taxable Investments": "growth",
    "Retirement & Health": "shield",
    "Alternative Investments": "gem",
    "Other Assets": "box",
}


def normalize_icon_id(value: str | None, *, default: str = DEFAULT_BUCKET_ICON) -> str:
    """Return a known icon id, falling back to ``default`` for anything unknown."""
    candidate = (value or "").strip().lower()
    return candidate if candidate in ICONS else default


def _match(text: str, table: tuple[tuple[str, tuple[str, ...]], ...]) -> str | None:
    haystack = re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()
    if not haystack:
        return None
    for icon_id, keywords in table:
        for keyword in keywords:
            # Allow a trailing plural so "Books" matches the "book" keyword.
            if re.search(rf"\b{re.escape(keyword)}s?\b", haystack):
                return icon_id
    return None


def bucket_icon(name: str, stored: str | None = None) -> Icon:
    """Icon for a spending bucket: the user's explicit pick, else name keywords."""
    if stored:
        chosen = (stored or "").strip().lower()
        if chosen in ICONS:
            return ICONS[chosen]
    return ICONS[_match(name, _BUCKET_KEYWORDS) or DEFAULT_BUCKET_ICON]


def suggest_bucket_icon(name: str) -> str:
    """Icon id the keyword matcher would pick for ``name``."""
    return _match(name, _BUCKET_KEYWORDS) or DEFAULT_BUCKET_ICON


def asset_bucket_icon(asset_bucket: str) -> Icon:
    return ICONS[_ASSET_BUCKET_ICONS.get(asset_bucket, "box")]


def liability_icon(name: str) -> Icon:
    return ICONS[_match(name, _LIABILITY_KEYWORDS) or DEFAULT_LIABILITY_ICON]
