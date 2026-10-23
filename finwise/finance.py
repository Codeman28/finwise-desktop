"""
finance.py - All the money maths, with NO user-interface code.

Why keep maths separate from screens?
  * Each function can be tested on its own (see tests/test_finance.py).
  * The real app AND the learning playground reuse exactly the same maths,
    so what you practise in the playground behaves like the real thing.

Every function here takes plain inputs (lists, numbers) and returns plain
outputs. None of them change anything - they only calculate.
"""

from datetime import date, datetime

from .models import EXPENSE, INCOME, EXPENSE_CATEGORIES, SAVINGS_CATEGORY

# Thresholds used to colour budgets: under 80% = fine, 80-100% = careful,
# over 100% = overspent.
WARNING_LEVEL = 0.8


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------
CURRENCY_SYMBOL = "₫"  # Vietnamese đồng


def format_money(amount, currency=CURRENCY_SYMBOL):
    """Turn 1234567 into '1.234.567 ₫' and -20000 into '-20.000 ₫'.

    Vietnamese đồng has no cents, so we round to a whole number.
    Vietnam writes thousands with DOTS (1.000.000), while Python's
    formatting uses commas (1,000,000) - so we format first, then
    swap the commas for dots. The symbol goes AFTER the number.
    """
    sign = "-" if amount < 0 else ""
    whole_number = round(abs(amount))
    with_commas = f"{whole_number:,}"             # '1,234,567'
    with_dots = with_commas.replace(",", ".")     # '1.234.567'
    return f"{sign}{with_dots} {currency}"


def current_month_key(today=None):
    """Return the current month as 'YYYY-MM', e.g. '2026-09'."""
    today = today or date.today()
    return today.strftime("%Y-%m")


def month_label(month_key):
    """'2026-09' -> 'Tháng 9/2026' (the way months are written in Vietnamese).

    We build the text ourselves instead of using strftime("%b"), because
    strftime gives English month names like 'Sep'.
    """
    year, month = month_key.split("-")
    return f"Tháng {int(month)}/{year}"


def short_month_label(month_key):
    """'2026-09' -> 'T9' (tiny label under each bar of the chart)."""
    _year, month = month_key.split("-")
    return f"T{int(month)}"


def display_date(iso_text):
    """'2026-09-24' -> '24/09/2026' (day/month/year, as used in Vietnam).

    Dates are SAVED as 'YYYY-MM-DD' because that order sorts correctly,
    but they are SHOWN as 'DD/MM/YYYY' because that is what people read.
    """
    parsed = datetime.strptime(iso_text, "%Y-%m-%d")
    return parsed.strftime("%d/%m/%Y")


def previous_months(count, today=None):
    """Return the last `count` month keys, oldest first.

    Example (today = 2026-09-24, count = 3) -> ['2026-07', '2026-08', '2026-09']
    We step backwards one month at a time, wrapping January -> December.
    """
    today = today or date.today()
    year, month = today.year, today.month
    keys = []
    for _ in range(count):
        keys.append(f"{year:04d}-{month:02d}")
        month -= 1
        if month == 0:          # went past January -> go to December last year
            month = 12
            year -= 1
    keys.reverse()              # we collected newest first, so flip the list
    return keys


# ---------------------------------------------------------------------------
# Filtering and totals
# ---------------------------------------------------------------------------
def transactions_in_month(transactions, month_key):
    """Keep only the transactions whose date starts with 'YYYY-MM'."""
    return [t for t in transactions if t.date.startswith(month_key)]


def total_of_kind(transactions, kind):
    """Add up every transaction of one kind (INCOME or EXPENSE)."""
    total = 0.0
    for transaction in transactions:
        if transaction.kind == kind:
            total += transaction.amount
    return total


def total_income(transactions):
    return total_of_kind(transactions, INCOME)


def total_expenses(transactions):
    return total_of_kind(transactions, EXPENSE)


def balance(transactions):
    """Money you have = everything that came in - everything that went out."""
    return total_income(transactions) - total_expenses(transactions)


def savings_rate(transactions):
    """What share of income was NOT spent, as a number between 0 and 1.

    Example: earned 2000, spent 1500 -> saved 500 -> 500 / 2000 = 0.25 (25%).
    Money moved into the savings category ("Tiết kiệm") counts as saved, not spent,
    because it still belongs to you.
    """
    income = total_income(transactions)
    if income <= 0:
        return 0.0  # avoid dividing by zero when there is no income yet

    spent = 0.0
    for transaction in transactions:
        is_expense = transaction.kind == EXPENSE
        if is_expense and transaction.category != SAVINGS_CATEGORY:
            spent += transaction.amount

    return max(0.0, (income - spent) / income)


def spending_by_category(transactions):
    """Return {category: total spent}, biggest category first."""
    totals = {}
    for transaction in transactions:
        if transaction.kind != EXPENSE:
            continue
        # .get(key, 0) returns 0 the first time we see a category
        totals[transaction.category] = totals.get(transaction.category, 0) + transaction.amount

    # sorted(..., reverse=True) puts the largest amounts first
    ordered = sorted(totals.items(), key=lambda pair: pair[1], reverse=True)
    return dict(ordered)


def spending_by_group(transactions):
    """Split expenses into the 50/30/20 groups: needs, wants and savings.

    Returns e.g. {"need": 1200.0, "want": 450.0, "savings": 300.0}
    """
    groups = {"need": 0.0, "want": 0.0, "savings": 0.0}
    for transaction in transactions:
        if transaction.kind != EXPENSE:
            continue
        group = EXPENSE_CATEGORIES.get(transaction.category, "want")
        groups[group] += transaction.amount
    return groups


def monthly_history(transactions, months=6, today=None):
    """Income and expenses for each of the last `months` months (for the chart).

    Returns a list like:
        [{"month": "2026-04", "income": 2000, "expense": 1700}, ...]
    """
    history = []
    for month_key in previous_months(months, today):
        in_month = transactions_in_month(transactions, month_key)
        history.append({
            "month": month_key,
            "income": total_income(in_month),
            "expense": total_expenses(in_month),
        })
    return history


# ---------------------------------------------------------------------------
# Budgets
# ---------------------------------------------------------------------------
def budget_status(budget, month_transactions):
    """Compare what was spent in a category with its monthly limit.

    Returns a dict with everything a screen needs to draw a progress bar:
        spent, limit, remaining, ratio (0..1+), and a status word:
        "ok"      -> below 80% of the limit
        "warning" -> between 80% and 100%
        "over"    -> more than the limit
    """
    spent = 0.0
    for transaction in month_transactions:
        if transaction.kind == EXPENSE and transaction.category == budget.category:
            spent += transaction.amount

    ratio = spent / budget.limit if budget.limit > 0 else 0.0

    if ratio > 1:
        status = "over"
    elif ratio >= WARNING_LEVEL:
        status = "warning"
    else:
        status = "ok"

    return {
        "category": budget.category,
        "spent": spent,
        "limit": budget.limit,
        "remaining": budget.limit - spent,
        "ratio": ratio,
        "status": status,
    }


# ---------------------------------------------------------------------------
# Goals
# ---------------------------------------------------------------------------
def goal_progress(goal):
    """Share of a goal that is already saved, capped at 1.0 (100%)."""
    if goal.target <= 0:
        return 1.0
    return min(1.0, goal.saved / goal.target)


def months_to_reach(remaining, monthly_saving):
    """How many months until a goal is reached if you save a fixed amount.

    We round UP: needing 2.1 months really means 3 months of saving.
    Returns None when it can never be reached (saving 0 per month).
    """
    if remaining <= 0:
        return 0
    if monthly_saving <= 0:
        return None
    months = remaining / monthly_saving
    whole_months = int(months)
    if months > whole_months:   # there is a leftover fraction -> one more month
        whole_months += 1
    return whole_months


# ---------------------------------------------------------------------------
# Growing money (used by the Compound Interest lesson and Growth Lab)
# ---------------------------------------------------------------------------
def compound_growth(start_amount, monthly_deposit, yearly_rate_percent, years):
    """Simulate a savings account month by month.

    Each month two things happen, in this order:
        1. the balance earns interest  (yearly rate / 12)
        2. you add your monthly deposit

    Returns a list with one entry per year (including year 0):
        [{"year": 0, "balance": ..., "deposited": ...}, ...]
    "deposited" is the money YOU put in; balance - deposited = interest earned.
    """
    monthly_rate = (yearly_rate_percent / 100) / 12
    balance_now = float(start_amount)
    deposited = float(start_amount)

    yearly_points = [{"year": 0, "balance": balance_now, "deposited": deposited}]

    for year in range(1, years + 1):
        for _month in range(12):
            balance_now += balance_now * monthly_rate  # step 1: interest
            balance_now += monthly_deposit             # step 2: deposit
            deposited += monthly_deposit
        yearly_points.append({"year": year, "balance": balance_now, "deposited": deposited})

    return yearly_points


def credit_card_payoff(debt, yearly_rate_percent, monthly_payment, max_months=600):
    """How long it takes to pay off a debt, and how much interest it costs.

    Returns (months_needed, total_interest). If the payment is too small to
    ever beat the interest, returns (None, None) - a classic debt trap.
    """
    monthly_rate = (yearly_rate_percent / 100) / 12
    remaining = float(debt)
    interest_paid = 0.0
    months = 0

    while remaining > 0:
        interest = remaining * monthly_rate
        if monthly_payment <= interest:
            return None, None  # payment never even covers the interest
        interest_paid += interest
        remaining = remaining + interest - monthly_payment
        months += 1
        if months >= max_months:
            return None, None

    return months, interest_paid
