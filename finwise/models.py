"""
models.py - The "shapes" of the data the app works with.

A dataclass is a simple Python class that mainly stores values.
Writing `Transaction(amount=5, ...)` is clearer than passing around
anonymous dictionaries like {"amount": 5, ...}.

Each model has:
    to_dict()   -> turns the object into a plain dict (so we can save it as JSON)
    from_dict() -> builds the object back from that dict (when loading)
"""

import uuid
from dataclasses import dataclass, field, asdict

# ---------------------------------------------------------------------------
# Categories (shown to the user in Vietnamese)
# ---------------------------------------------------------------------------
# Every expense category is tagged as a "need", a "want" or "savings".
# The 50/30/20 lesson and the playground use these tags to check whether a
# user's spending is balanced.
SAVINGS_CATEGORY = "Tiết kiệm"   # used in several places, so it gets a name

EXPENSE_CATEGORIES = {
    "Nhà ở": "need",          # housing / rent
    "Thực phẩm": "need",      # groceries
    "Đi lại": "need",         # transport
    "Hóa đơn": "need",        # electricity, water, internet
    "Sức khỏe": "need",       # health
    "Học tập": "need",        # education
    "Ăn ngoài": "want",       # eating out
    "Giải trí": "want",       # entertainment
    "Mua sắm": "want",        # shopping
    "Du lịch": "want",        # travel
    SAVINGS_CATEGORY: "savings",
    "Khác": "want",           # other
}

INCOME_CATEGORIES = ["Lương", "Làm thêm", "Trợ cấp", "Quà tặng", "Thu nhập khác"]

# Older versions of FinWise saved English category names. When such a file
# is loaded, we quietly rename the categories so nothing is lost.
LEGACY_CATEGORY_NAMES = {
    "Housing": "Nhà ở",
    "Groceries": "Thực phẩm",
    "Transport": "Đi lại",
    "Utilities": "Hóa đơn",
    "Health": "Sức khỏe",
    "Education": "Học tập",
    "Eating out": "Ăn ngoài",
    "Entertainment": "Giải trí",
    "Shopping": "Mua sắm",
    "Travel": "Du lịch",
    "Savings": SAVINGS_CATEGORY,
    "Other": "Khác",
    "Salary": "Lương",
    "Freelance": "Làm thêm",
    "Allowance": "Trợ cấp",
    "Gift": "Quà tặng",
    "Other income": "Thu nhập khác",
}


def modern_category(name):
    """Return the current (Vietnamese) name for a possibly old category name."""
    return LEGACY_CATEGORY_NAMES.get(name, name)


INCOME = "income"
EXPENSE = "expense"


def new_id():
    """Return a short random id, e.g. 'a3f9c2d1'. Used to find items later."""
    return uuid.uuid4().hex[:8]


@dataclass
class Transaction:
    """One movement of money: either money coming IN or going OUT."""

    date: str            # stored as text "YYYY-MM-DD" so it is easy to save/sort
    description: str
    amount: float        # always positive; `kind` tells us the direction
    kind: str            # INCOME or EXPENSE
    category: str
    id: str = field(default_factory=new_id)

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return Transaction(
            date=data["date"],
            description=data.get("description", ""),
            amount=float(data["amount"]),
            kind=data["kind"],
            category=modern_category(data["category"]),
            id=data.get("id", new_id()),
        )


@dataclass
class Budget:
    """A monthly spending limit for one expense category."""

    category: str
    limit: float

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return Budget(category=modern_category(data["category"]), limit=float(data["limit"]))


@dataclass
class Goal:
    """Something the user is saving towards, e.g. 'Laptop mới - 25.000.000 ₫'."""

    name: str
    target: float
    saved: float = 0.0
    id: str = field(default_factory=new_id)

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return Goal(
            name=data["name"],
            target=float(data["target"]),
            saved=float(data.get("saved", 0)),
            id=data.get("id", new_id()),
        )
