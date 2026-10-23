"""
Tests for the money maths and the playground missions.
Run with:   python -m pytest tests     (or: python -m unittest discover tests)
"""

import random
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from finwise import finance
from finwise.models import Transaction, Budget, Goal, INCOME, EXPENSE
from finwise.state import AppState
from finwise.content import challenges
from finwise.content.courses import all_lessons


def tx(amount, kind, category, day="2026-09-10"):
    return Transaction(date=day, description=category, amount=amount, kind=kind, category=category)


class FinanceTests(unittest.TestCase):
    def test_format_money(self):
        self.assertEqual(finance.format_money(1234567), "1.234.567 ₫")
        self.assertEqual(finance.format_money(-20000), "-20.000 ₫")
        self.assertEqual(finance.format_money(999.6), "1.000 ₫")  # rounds, no decimals

    def test_balance_and_savings_rate(self):
        items = [tx(20_000_000, INCOME, "Lương"), tx(15_000_000, EXPENSE, "Nhà ở"),
                 tx(3_000_000, EXPENSE, "Tiết kiệm")]
        self.assertEqual(finance.balance(items), 2_000_000)
        # Savings is not "spent", so the rate is (20M - 15M) / 20M
        self.assertAlmostEqual(finance.savings_rate(items), 0.25)

    def test_previous_months_wraps_year(self):
        self.assertEqual(finance.previous_months(3, date(2026, 2, 5)), ["2025-12", "2026-01", "2026-02"])

    def test_budget_status(self):
        items = [tx(90, EXPENSE, "Thực phẩm")]
        self.assertEqual(finance.budget_status(Budget("Thực phẩm", 100), items)["status"], "warning")
        self.assertEqual(finance.budget_status(Budget("Thực phẩm", 50), items)["status"], "over")
        self.assertEqual(finance.budget_status(Budget("Thực phẩm", 500), items)["status"], "ok")

    def test_vietnamese_dates_and_months(self):
        self.assertEqual(finance.display_date("2026-09-24"), "24/09/2026")
        self.assertEqual(finance.month_label("2026-09"), "Tháng 9/2026")
        self.assertEqual(finance.short_month_label("2026-12"), "T12")

    def test_months_to_reach_rounds_up(self):
        self.assertEqual(finance.months_to_reach(210, 100), 3)
        self.assertIsNone(finance.months_to_reach(100, 0))

    def test_compound_growth_matches_lesson(self):
        # No deposits, 10 years at 5% compounded monthly ~= 16.470.000
        final = finance.compound_growth(10_000_000, 0, 5, 10)[-1]["balance"]
        self.assertAlmostEqual(final, 16_470_095, delta=10)

    def test_debt_trap_detected(self):
        self.assertEqual(finance.credit_card_payoff(50_000_000, 24, 1_000_000), (None, None))
        months, interest = finance.credit_card_payoff(50_000_000, 24, 5_000_000)
        self.assertLessEqual(months, 12)
        self.assertGreater(interest, 0)


class StateTests(unittest.TestCase):
    def test_save_and_reload(self):
        path = Path(__file__).parent / "_tmp_data.json"
        try:
            state = AppState(data_path=path)
            state.add_transaction("2026-09-01", "Lương", 10_000_000, INCOME, "Lương")
            goal = state.add_goal("Trip", 5_000_000)
            state.contribute_to_goal(goal.id, 1_000_000)
            reloaded = AppState(data_path=path)
            self.assertEqual(len(reloaded.transactions), 2)  # pay + savings transfer
            self.assertEqual(reloaded.goals[0].saved, 1_000_000)
        finally:
            path.unlink(missing_ok=True)

    def test_old_english_categories_are_renamed(self):
        old = Transaction.from_dict({"date": "2026-09-01", "description": "Rent",
                                     "amount": 100, "kind": EXPENSE, "category": "Housing"})
        self.assertEqual(old.category, "Nhà ở")
        self.assertEqual(Budget.from_dict({"category": "Groceries", "limit": 5}).category, "Thực phẩm")

    def test_sample_data_never_in_future(self):
        state = AppState(persist=False)
        state.load_sample_data()
        today = date.today().isoformat()
        self.assertTrue(all(t.date <= today for t in state.transactions))


class ChallengeTests(unittest.TestCase):
    def test_every_lesson_challenge_exists(self):
        ids = {c["id"] for c in challenges.CHALLENGES}
        for lesson in all_lessons():
            if lesson.get("challenge"):
                self.assertIn(lesson["challenge"], ids)

    def test_503020_can_be_completed(self):
        challenge = challenges.find_challenge("rule-503020")
        state = AppState(persist=False)
        challenge["setup"](state)
        self.assertFalse(all(done for _d, done in challenges.evaluate(challenge, state)))
        state.add_transaction(date.today().isoformat(), "Ăn tối", 2_000_000, EXPENSE, "Ăn ngoài")
        state.add_transaction(date.today().isoformat(), "Để dành", 5_000_000, EXPENSE, "Tiết kiệm")
        self.assertTrue(all(done for _d, done in challenges.evaluate(challenge, state)))

    def test_needs_wants_can_be_completed(self):
        challenge = challenges.find_challenge("needs-wants")
        state = AppState(persist=False)
        challenge["setup"](state)
        for t in list(state.transactions):
            if t.category in ("Mua sắm", "Du lịch"):
                state.delete_transaction(t.id)
        self.assertTrue(all(done for _d, done in challenges.evaluate(challenge, state)))

    def test_survive_month_with_buffer(self):
        challenge = challenges.find_challenge("survive-month")
        state = AppState(persist=False)
        challenge["setup"](state)
        # Small budgets leave a big enough buffer for even the worst surprise
        state.set_budget("Thực phẩm", 2_000_000)
        state.set_budget("Đi lại", 500_000)
        challenges.simulate_month(state, random.Random(1))
        self.assertTrue(all(done for _d, done in challenges.evaluate(challenge, state)))


if __name__ == "__main__":
    unittest.main()
