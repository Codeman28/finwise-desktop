"""
challenges.py - Missions for the learning Playground.

A challenge has three parts:
    setup(state)  - puts starting money/bills into the sandbox wallet
    tasks         - a checklist. Each task is (description, check_function).
                    A check function receives the sandbox AppState and
                    returns True when that task is done.
    tip           - a hint shown under the checklist

Because checks are plain functions, the Playground can re-run them after
every click and tick items off live - that instant feedback is what makes
it feel like a game.

`simulate_month()` at the bottom powers the "Survive the month" mission.
"""

import random
from datetime import date

from .. import finance
from ..models import INCOME, EXPENSE


# ---------------------------------------------------------------------------
# Helpers used by the setups and checks
# ---------------------------------------------------------------------------
def _today():
    return date.today().isoformat()


def _add_income(state, amount, description="Lương tháng"):
    state.add_transaction(_today(), description, amount, INCOME, "Lương")


def _add_expense(state, amount, category, description=None):
    state.add_transaction(_today(), description or category, amount, EXPENSE, category)


def _expenses(state):
    return [t for t in state.transactions if t.kind == EXPENSE]


def _income(state):
    return finance.total_income(state.transactions)


def _group_share(state, group):
    """Share of income spent on a 50/30/20 group ('need', 'want', 'savings')."""
    income = _income(state)
    if income <= 0:
        return 0.0
    return finance.spending_by_group(state.transactions)[group] / income


# ---------------------------------------------------------------------------
# Setups - each one fills an EMPTY sandbox wallet with a starting situation
# ---------------------------------------------------------------------------
def setup_free_play(state):
    _add_income(state, 15_000_000)


def setup_track_week(state):
    _add_income(state, 12_000_000)


def setup_first_budget(state):
    _add_income(state, 15_000_000)
    _add_expense(state, 5_000_000, "Nhà ở", "Tiền thuê nhà")


def setup_needs_wants(state):
    # Deliberately overspent on wants so the learner has to cut back.
    _add_income(state, 20_000_000)
    _add_expense(state, 7_000_000, "Nhà ở", "Tiền thuê nhà")
    _add_expense(state, 2_500_000, "Thực phẩm", "Siêu thị")
    _add_expense(state, 500_000, "Đi lại", "Đổ xăng")
    _add_expense(state, 3_500_000, "Mua sắm", "Áo khoác mới")
    _add_expense(state, 2_000_000, "Ăn ngoài", "Nhà hàng & trà sữa")
    _add_expense(state, 1_500_000, "Giải trí", "Vé ca nhạc")
    _add_expense(state, 1_200_000, "Du lịch", "Đặt cọc chuyến Đà Lạt")
    _add_expense(state, 260_000, "Giải trí", "Gói xem phim trực tuyến")


def setup_503020(state):
    _add_income(state, 25_000_000)
    _add_expense(state, 9_000_000, "Nhà ở", "Tiền thuê nhà")
    _add_expense(state, 2_800_000, "Thực phẩm", "Siêu thị")
    _add_expense(state, 700_000, "Đi lại", "Vé tháng metro")


def setup_emergency(state):
    _add_income(state, 20_000_000)
    _add_expense(state, 7_000_000, "Nhà ở", "Tiền thuê nhà")
    _add_expense(state, 2_500_000, "Thực phẩm", "Siêu thị")
    _add_expense(state, 1_000_000, "Hóa đơn", "Điện nước")
    _add_expense(state, 1_500_000, "Đi lại", "Xăng & gửi xe")


def setup_goal_plan(state):
    _add_income(state, 12_000_000)
    _add_expense(state, 4_000_000, "Nhà ở", "Tiền nhà (ở ghép)")
    _add_expense(state, 2_000_000, "Thực phẩm", "Siêu thị")


def setup_survive(state):
    _add_income(state, 15_000_000)
    _add_expense(state, 6_000_000, "Nhà ở", "Tiền thuê nhà")


def setup_nothing(state):
    """Labs (Growth / Debt) do not need any starting transactions."""
    pass


# ---------------------------------------------------------------------------
# Check functions for tasks
# ---------------------------------------------------------------------------
def _has_n_expenses(n):
    def check(state):
        return len(_expenses(state)) >= n
    return check


def _uses_n_categories(n):
    def check(state):
        categories = {t.category for t in _expenses(state)}
        return len(categories) >= n
    return check


def _balance_positive(state):
    return finance.balance(state.transactions) > 0


def _has_n_budgets(n):
    def check(state):
        return len(state.budgets) >= n
    return check


def _has_budget_for(category):
    def check(state):
        return any(b.category == category for b in state.budgets)
    return check


def _budgets_fit_income(state):
    """Budgets + fixed costs that have no budget must not exceed income."""
    if not state.budgets:
        return False
    budgeted = sum(b.limit for b in state.budgets)
    budgeted_categories = {b.category for b in state.budgets}
    unbudgeted_spending = sum(
        t.amount for t in _expenses(state) if t.category not in budgeted_categories
    )
    return budgeted + unbudgeted_spending <= _income(state)


def _wants_at_most(share):
    def check(state):
        return _group_share(state, "want") <= share
    return check


def _needs_at_most(share):
    def check(state):
        return _group_share(state, "need") <= share
    return check


def _savings_at_least(share):
    def check(state):
        return _group_share(state, "savings") >= share
    return check


def _has_some_wants(state):
    return finance.spending_by_group(state.transactions)["want"] > 0


def _rent_still_paid(state):
    return any(t.category == "Nhà ở" for t in _expenses(state))


def _find_emergency_goal(state):
    # Accept the Vietnamese name ("Quỹ khẩn cấp") or the English word.
    for goal in state.goals:
        name = goal.name.lower()
        if "khẩn cấp" in name or "emergency" in name:
            return goal
    return None


def _has_emergency_goal(state):
    return _find_emergency_goal(state) is not None


def _emergency_target_big_enough(state):
    """Target must cover at least 3 months of the essential (need) costs."""
    goal = _find_emergency_goal(state)
    if goal is None:
        return False
    monthly_needs = finance.spending_by_group(state.transactions)["need"]
    return goal.target >= 3 * monthly_needs


def _emergency_funded_10_percent(state):
    goal = _find_emergency_goal(state)
    return goal is not None and goal.saved >= 0.10 * _income(state)


def _has_goal_with_target(minimum):
    def check(state):
        return any(g.target >= minimum for g in state.goals)
    return check


def _goal_contribution_at_least(share_of_income):
    def check(state):
        total_saved = sum(g.saved for g in state.goals)
        return total_saved >= share_of_income * _income(state)
    return check


def _month_simulated(state):
    return state.scratch.get("month_simulated", False)


def _buffer_after_sim(minimum):
    """After playing the month, at least `minimum` đồng must be left."""
    def check(state):
        return _month_simulated(state) and finance.balance(state.transactions) >= minimum
    return check


def _growth_reaches(target, max_years):
    def check(state):
        lab = state.scratch.get("growth")
        return bool(lab) and lab["final"] >= target and lab["years"] <= max_years
    return check


def _growth_interest_beats_deposits(state):
    lab = state.scratch.get("growth")
    return bool(lab) and lab["interest"] > lab["deposited"]


def _debt_months_at_most(months):
    def check(state):
        lab = state.scratch.get("debt")
        return bool(lab) and lab["months"] is not None and lab["months"] <= months
    return check


def _debt_saw_trap(state):
    lab = state.scratch.get("debt")
    return bool(lab) and lab.get("seen_trap", False)


# ---------------------------------------------------------------------------
# The list of challenges shown in the Playground dropdown
# ---------------------------------------------------------------------------
CHALLENGES = [
    {
        "id": "free-play",
        "title": "Chơi tự do",
        "lesson": None,
        "intro": "Không có luật lệ - bạn nhận 15.000.000 ₫ lương ảo. Hãy thử mọi tính năng "
                 "và xem các con số thay đổi ra sao.",
        "setup": setup_free_play,
        "tasks": [],
        "tip": "Mọi thứ ở đây đều là giả lập. Cứ thử nghiệm thoải mái, có thể làm lại bất cứ lúc nào.",
        "tab": "dashboard",
    },
    {
        "id": "track-first-week",
        "title": "Theo dõi tuần đầu tiên",
        "lesson": "basics-tracking",
        "intro": "Bạn vừa nhận 12.000.000 ₫ tiền lương. Hãy ghi lại vài khoản chi hằng ngày trong tuần này.",
        "setup": setup_track_week,
        "tasks": [
            ("Ghi lại ít nhất 3 khoản chi", _has_n_expenses(3)),
            ("Dùng ít nhất 2 danh mục khác nhau", _uses_n_categories(2)),
            ("Giữ số dư trên 0 ₫", _balance_positive),
        ],
        "tip": "Mở tab Giao dịch và dùng biểu mẫu 'Thêm'. Sau đó xem tab Tổng quan "
               "để thấy biểu đồ chi tiêu thay đổi.",
        "tab": "transactions",
    },
    {
        "id": "first-budget",
        "title": "Lập ngân sách đầu tiên",
        "lesson": "basics-budget",
        "intro": "Thu nhập: 15.000.000 ₫. Đã trả 5.000.000 ₫ tiền nhà. Hãy lên kế hoạch cho phần còn lại của tháng.",
        "setup": setup_first_budget,
        "tasks": [
            ("Tạo ngân sách Thực phẩm", _has_budget_for("Thực phẩm")),
            ("Tạo ngân sách cho ít nhất 3 danh mục", _has_n_budgets(3)),
            ("Tiền nhà + mọi ngân sách nằm trong thu nhập 15.000.000 ₫", _budgets_fit_income),
        ],
        "tip": "Tiền nhà (5.000.000 ₫) không có ngân sách nhưng vẫn được tính. Tổng ngân sách "
               "của bạn phải từ 10.000.000 ₫ trở xuống.",
        "tab": "budgets",
    },
    {
        "id": "needs-wants",
        "title": "Giải cứu tháng chi quá tay",
        "lesson": "basics-needs-wants",
        "intro": "Thu nhập: 20.000.000 ₫, nhưng các khoản 'muốn' đã vượt kiểm soát. Hãy xóa bớt "
                 "vài khoản muốn (coi như đã trả lại hàng) mà không đụng tới khoản cần.",
        "setup": setup_needs_wants,
        "tasks": [
            ("Giảm khoản muốn xuống tối đa 30% thu nhập", _wants_at_most(0.30)),
            ("Vẫn trả tiền nhà (đừng xóa khoản cần!)", _rent_still_paid),
            ("Giữ số dư trên 0 ₫", _balance_positive),
        ],
        "tip": "Khoản muốn gồm Mua sắm, Ăn ngoài, Giải trí và Du lịch. 30% của 20.000.000 ₫ "
               "là 6.000.000 ₫.",
        "tab": "transactions",
    },
    {
        "id": "rule-503020",
        "title": "Áp dụng 50/30/20",
        "lesson": "budget-503020",
        "intro": "Thu nhập: 25.000.000 ₫. Các khoản cần đã được trả. Giờ hãy dành chút cho niềm vui "
                 "và trả cho mình trước.",
        "setup": setup_503020,
        "tasks": [
            ("Khoản cần tối đa 50% thu nhập", _needs_at_most(0.50)),
            ("Chi một chút cho khoản muốn (cuộc sống cần niềm vui!)", _has_some_wants),
            ("Khoản muốn tối đa 30%", _wants_at_most(0.30)),
            ("Tiết kiệm ít nhất 20% (dùng danh mục 'Tiết kiệm' hoặc một Mục tiêu)", _savings_at_least(0.20)),
        ],
        "tip": "20% của 25.000.000 ₫ là 5.000.000 ₫. Thêm tiền vào mục tiêu ở tab Mục tiêu sẽ tự "
               "động ghi nhận là Tiết kiệm.",
        "tab": "transactions",
    },
    {
        "id": "emergency-fund",
        "title": "Lập quỹ khẩn cấp",
        "lesson": "budget-emergency",
        "intro": "Thu nhập: 20.000.000 ₫, chi phí thiết yếu 12.000.000 ₫ mỗi tháng. Hãy bảo vệ "
                 "bản thân trước những bất ngờ.",
        "setup": setup_emergency,
        "tasks": [
            ("Tạo mục tiêu có chữ 'khẩn cấp' trong tên (VD: Quỹ khẩn cấp)", _has_emergency_goal),
            ("Mục tiêu đủ cho 3 tháng chi phí thiết yếu", _emergency_target_big_enough),
            ("Bỏ vào ít nhất 10% thu nhập", _emergency_funded_10_percent),
        ],
        "tip": "Chi phí thiết yếu (khoản cần) ở đây là 12.000.000 ₫, nên hãy đặt từ 36.000.000 ₫ trở lên. "
               "10% thu nhập là 2.000.000 ₫.",
        "tab": "goals",
    },
    {
        "id": "debt-lab",
        "title": "Thoát bẫy nợ",
        "lesson": "budget-debt",
        "intro": "Bạn nợ thẻ tín dụng 50.000.000 ₫ với lãi 24%/năm. Dùng Phòng lab Nợ để "
                 "tìm kế hoạch trả nợ hiệu quả.",
        "setup": setup_nothing,
        "tasks": [
            ("Thử trả 1.000.000 ₫ trở xuống và xem cái bẫy", _debt_saw_trap),
            ("Tìm mức trả giúp hết nợ trong tối đa 12 tháng", _debt_months_at_most(12)),
        ],
        "tip": "Kéo thanh trượt 'Trả mỗi tháng'. Để ý con số 'Tổng tiền lãi phải trả'.",
        "tab": "debt",
    },
    {
        "id": "goal-plan",
        "title": "Lập kế hoạch tiết kiệm",
        "lesson": "grow-goals",
        "intro": "Thu nhập: 12.000.000 ₫. Bạn muốn mua một thứ ý nghĩa. Hãy biến nó thành kế hoạch thật.",
        "setup": setup_goal_plan,
        "tasks": [
            ("Tạo mục tiêu từ 10.000.000 ₫ trở lên", _has_goal_with_target(10_000_000)),
            ("Bỏ ít nhất 10% thu nhập vào các mục tiêu", _goal_contribution_at_least(0.10)),
            ("Giữ số dư trên 0 ₫", _balance_positive),
        ],
        "tip": "Mỗi thẻ mục tiêu cho biết bạn cần để dành bao nhiêu mỗi tháng để kịp thời hạn.",
        "tab": "goals",
    },
    {
        "id": "growth-lab",
        "title": "Nuôi lớn 250 triệu ₫",
        "lesson": "grow-compound",
        "intro": "Dùng Phòng lab Tăng trưởng để khám phá thời gian và lãi suất tạo ra tài sản như thế nào.",
        "setup": setup_nothing,
        "tasks": [
            ("Đạt từ 250.000.000 ₫ trở lên trong vòng 10 năm", _growth_reaches(250_000_000, 10)),
            ("Tìm kế hoạch mà tiền lãi nhiều hơn số tiền bạn gửi vào",
             _growth_interest_beats_deposits),
        ],
        "tip": "Với nhiệm vụ thứ hai, hãy thử thời gian dài (30+ năm) - đó chính là "
               "hiệu ứng lăn cầu tuyết của lãi kép.",
        "tab": "growth",
    },
    {
        "id": "survive-month",
        "title": "Thử thách cuối: sống sót qua tháng",
        "lesson": None,
        "intro": "Thu nhập: 15.000.000 ₫, tiền nhà 6.000.000 ₫. Đặt ngân sách rồi nhấn 'Bắt đầu tháng'. "
                 "Cuộc sống sẽ ném cho bạn một bất ngờ ngẫu nhiên!",
        "setup": setup_survive,
        "tasks": [
            ("Có ngân sách cho Thực phẩm và Đi lại",
             lambda s: _has_budget_for("Thực phẩm")(s) and _has_budget_for("Đi lại")(s)),
            ("Chơi hết tháng", _month_simulated),
            ("Cuối tháng còn dư ít nhất 1.000.000 ₫", _buffer_after_sim(1_000_000)),
        ],
        "tip": "Hãy chừa khoản dự phòng! Bất ngờ có thể tốn từ 500.000 ₫ đến 5.000.000 ₫. Ngân sách "
               "tiêu sạch đến đồng cuối cùng là rất rủi ro.",
        "tab": "budgets",
    },
]


def find_challenge(challenge_id):
    for challenge in CHALLENGES:
        if challenge["id"] == challenge_id:
            return challenge
    return CHALLENGES[0]


def evaluate(challenge, state):
    """Run every task check. Returns a list of (description, done) pairs."""
    results = []
    for description, check in challenge["tasks"]:
        try:
            done = bool(check(state))
        except Exception:
            done = False  # a check should never crash the screen
        results.append((description, done))
    return results


# ---------------------------------------------------------------------------
# "Play the month" simulation
# ---------------------------------------------------------------------------
SURPRISES = [
    ("Thay màn hình điện thoại", 1_500_000, "Khác"),
    ("Đi khám bệnh", 800_000, "Sức khỏe"),
    ("Mừng cưới bạn thân", 500_000, "Khác"),
    ("Sửa xe máy", 700_000, "Đi lại"),
    ("Hỏng sạc laptop", 600_000, "Khác"),
    ("Thay lốp xe máy", 1_200_000, "Đi lại"),
    ("Chữa răng khẩn cấp", 3_000_000, "Sức khỏe"),
    ("Vé máy bay về quê ăn Tết", 5_000_000, "Du lịch"),
]


def simulate_month(state, rng=None):
    """Pretend four weeks pass and spend money in every budgeted category.

    How it works:
      1. For each budget, "you" spend roughly a quarter of the limit each
         week. We multiply by a random factor between 0.80 and 1.10, because
         real life never matches the plan exactly (sometimes you overspend).
      2. One random surprise expense happens - it is NOT covered by any
         budget, which is exactly why a buffer is important.

    Returns a list of text lines describing what happened, for the screen.
    `rng` lets tests pass a fixed random generator so results are repeatable.
    """
    rng = rng or random.Random()
    story = []

    for week in range(1, 5):
        for budget in state.budgets:
            planned_this_week = budget.limit / 4
            randomness = rng.uniform(0.80, 1.10)
            spent = round(planned_this_week * randomness, 2)
            state.add_transaction(_today(), f"Tuần {week}: {budget.category.lower()}",
                                  spent, EXPENSE, budget.category)
        story.append(f"Tuần {week}: đã chi cho {len(state.budgets)} danh mục có ngân sách.")

    name, cost, category = rng.choice(SURPRISES)
    state.add_transaction(_today(), f"Bất ngờ: {name}", cost, EXPENSE, category)
    story.append(f"Bất ngờ! {name} tốn {finance.format_money(cost)}.")

    state.scratch["month_simulated"] = True
    return story
