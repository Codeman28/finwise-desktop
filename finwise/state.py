"""
state.py - The single place that holds and changes the app's data.

Think of AppState as the app's "wallet + notebook":
  * screens READ from it to draw themselves,
  * screens ask it to CHANGE things (add a transaction, set a budget...),
  * after every change it saves to disk (if it has a save file).

The playground creates a second AppState with `persist=False`.  That
"sandbox" wallet behaves exactly like the real one, but nothing is ever
written to disk - so learners can experiment without touching real data.
"""

from datetime import date, timedelta

from . import storage
from .models import Transaction, Budget, Goal, INCOME, EXPENSE, SAVINGS_CATEGORY


class AppState:
    def __init__(self, persist=True, data_path=None):
        self.persist = persist
        self.data_path = data_path
        # Temporary values that are never saved, e.g. the playground labs
        # store their latest results here so challenge checks can read them.
        self.scratch = {}

        # Start empty, then fill from disk when this is the real wallet.
        raw = storage.load_data(data_path) if persist else storage.empty_data()
        self._load_from_dict(raw)

    # ------------------------------------------------------------------
    # Loading / saving
    # ------------------------------------------------------------------
    def _load_from_dict(self, raw):
        """Turn the plain dicts from the JSON file into model objects."""
        self.transactions = [Transaction.from_dict(t) for t in raw["transactions"]]
        self.budgets = [Budget.from_dict(b) for b in raw["budgets"]]
        self.goals = [Goal.from_dict(g) for g in raw["goals"]]
        # sets make "is this lesson done?" checks fast and avoid duplicates
        self.completed_lessons = set(raw["completed_lessons"])
        self.completed_challenges = set(raw["completed_challenges"])

    def _to_dict(self):
        return {
            "transactions": [t.to_dict() for t in self.transactions],
            "budgets": [b.to_dict() for b in self.budgets],
            "goals": [g.to_dict() for g in self.goals],
            "completed_lessons": sorted(self.completed_lessons),
            "completed_challenges": sorted(self.completed_challenges),
        }

    def save(self):
        """Write everything to disk - skipped for the sandbox wallet."""
        if self.persist:
            storage.save_data(self._to_dict(), self.data_path)

    # ------------------------------------------------------------------
    # Transactions
    # ------------------------------------------------------------------
    def add_transaction(self, date_text, description, amount, kind, category):
        transaction = Transaction(
            date=date_text,
            description=description.strip() or category,
            amount=round(float(amount), 2),
            kind=kind,
            category=category,
        )
        self.transactions.append(transaction)
        self.save()
        return transaction

    def delete_transaction(self, transaction_id):
        # Build a new list that keeps every transaction EXCEPT the one to delete
        self.transactions = [t for t in self.transactions if t.id != transaction_id]
        self.save()

    def sorted_transactions(self):
        """Newest first - the order people expect in a bank statement."""
        return sorted(self.transactions, key=lambda t: t.date, reverse=True)

    # ------------------------------------------------------------------
    # Budgets (one per category - setting it again replaces the old limit)
    # ------------------------------------------------------------------
    def set_budget(self, category, limit):
        for budget in self.budgets:
            if budget.category == category:
                budget.limit = round(float(limit), 2)
                self.save()
                return
        self.budgets.append(Budget(category=category, limit=round(float(limit), 2)))
        self.save()

    def delete_budget(self, category):
        self.budgets = [b for b in self.budgets if b.category != category]
        self.save()

    # ------------------------------------------------------------------
    # Goals
    # ------------------------------------------------------------------
    def add_goal(self, name, target):
        goal = Goal(name=name.strip(), target=round(float(target), 2))
        self.goals.append(goal)
        self.save()
        return goal

    def contribute_to_goal(self, goal_id, amount, record_expense=True):
        """Move money into a goal.

        When `record_expense` is True we also record a savings ("Tiết kiệm") expense,
        so the money leaves your spendable balance - just like moving money
        into a separate savings account at a bank.
        """
        for goal in self.goals:
            if goal.id == goal_id:
                goal.saved = round(goal.saved + float(amount), 2)
                if record_expense:
                    self.transactions.append(Transaction(
                        date=date.today().isoformat(),
                        description=f"Tiết kiệm cho: {goal.name}",
                        amount=round(float(amount), 2),
                        kind=EXPENSE,
                        category=SAVINGS_CATEGORY,
                    ))
                self.save()
                return goal
        return None

    def delete_goal(self, goal_id):
        self.goals = [g for g in self.goals if g.id != goal_id]
        self.save()

    # ------------------------------------------------------------------
    # Learning progress
    # ------------------------------------------------------------------
    def mark_lesson_complete(self, lesson_id):
        self.completed_lessons.add(lesson_id)
        self.save()

    def mark_challenge_complete(self, challenge_id):
        self.completed_challenges.add(challenge_id)
        self.save()

    # ------------------------------------------------------------------
    # Housekeeping
    # ------------------------------------------------------------------
    def reset_money_data(self):
        """Delete all transactions, budgets and goals (keeps lesson progress)."""
        self.transactions = []
        self.budgets = []
        self.goals = []
        self.save()

    def load_sample_data(self, today=None):
        """Fill the wallet with 3 months of realistic example data.

        Handy for first-time users who want to see what the app looks like
        before typing in their own numbers.
        """
        today = today or date.today()
        first_of_this_month = today.replace(day=1)

        # (day of month, description, amount, kind, category)
        monthly_pattern = [
            (1, "Lương tháng", 18_000_000, INCOME, "Lương"),
            (2, "Tiền thuê nhà", 5_500_000, EXPENSE, "Nhà ở"),
            (4, "Siêu thị", 1_250_000, EXPENSE, "Thực phẩm"),
            (6, "Đổ xăng xe máy", 300_000, EXPENSE, "Đi lại"),
            (8, "Tiền điện & internet", 850_000, EXPENSE, "Hóa đơn"),
            (10, "Xem phim với bạn bè", 240_000, EXPENSE, "Giải trí"),
            (12, "Đi chợ", 980_000, EXPENSE, "Thực phẩm"),
            (14, "Ăn lẩu", 450_000, EXPENSE, "Ăn ngoài"),
            (15, "Dự án thiết kế tự do", 3_000_000, INCOME, "Làm thêm"),
            (18, "Giày thể thao mới", 1_200_000, EXPENSE, "Mua sắm"),
            (20, "Siêu thị", 1_150_000, EXPENSE, "Thực phẩm"),
        ]

        # Walk back over the last 3 months (2 months ago, last month, this month)
        for months_back in (2, 1, 0):
            month_start = first_of_this_month
            for _ in range(months_back):
                # jump to the last day of the previous month, then to its 1st
                month_start = (month_start - timedelta(days=1)).replace(day=1)

            for day, description, amount, kind, category in monthly_pattern:
                entry_date = month_start.replace(day=day)
                if entry_date > today:
                    continue  # never create transactions in the future
                self.transactions.append(Transaction(
                    date=entry_date.isoformat(),
                    description=description,
                    amount=amount,
                    kind=kind,
                    category=category,
                ))

        for category, limit in [("Thực phẩm", 3_800_000), ("Ăn ngoài", 800_000),
                                ("Giải trí", 500_000), ("Mua sắm", 1_500_000)]:
            self.set_budget(category, limit)

        self.goals.append(Goal(name="Quỹ khẩn cấp", target=60_000_000, saved=12_000_000))
        self.goals.append(Goal(name="Laptop mới", target=25_000_000, saved=6_000_000))
        self.save()
