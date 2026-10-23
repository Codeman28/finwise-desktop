# FinWise — money manager + financial literacy academy

> **Tải FinWise.exe cho Windows:** [Releases](https://github.com/Codeman28/finwise-desktop/releases/latest) - nhấn đúp để chạy, không cần cài Python.
> Phiên bản điện thoại/web: https://github.com/Codeman28/finwise-mobile


FinWise is a Windows desktop app with two halves:

1. **Real money management**: track income and expenses, set monthly budgets, save toward goals, and see it all on a dashboard.
2. **Learn**: 9 short lessons with quizzes, plus a **Playground** where you practise with pretend money. The Playground uses the same screens as the real app, so what you learn carries over directly.

The whole interface is in **Vietnamese**: screens, categories, lessons, quizzes and missions. Money is shown in đồng (`1.500.000 ₫`) and dates as day/month/year (`24/09/2026`). The code and its comments stay in English so they are easy to share and learn from.

Colours come from the *Colours Cafe* palette: `#005B4C` green, `#DB444E` red, `#FD7B64` coral, `#F9BCC5` pink, `#F1E7E9` off-white.

---

## 1. Running it

| What you want | How |
|---|---|
| **Just use the app** | Double-click `dist\FinWise.exe`. You don't need Python. |
| Run from source | `python -m venv .venv`, then `.venv\Scripts\pip install -r requirements.txt`, then `.venv\Scripts\python main.py` |
| Rebuild the .exe | Double-click `build_exe.bat` (takes about 2 minutes) |
| Run the tests | `.venv\Scripts\python -m unittest discover tests` |

Your data is saved automatically in `%APPDATA%\FinWise\data.json` (for example `C:\Users\you\AppData\Roaming\FinWise\data.json`). Settings (the gear icon) shows the exact path and has a "Clear money data" button.

---

## 2. Tech stack

| Layer | Tool | Why |
|---|---|---|
| Language | **Python 3.12** | Readable and beginner-friendly |
| UI framework | **Flet 1.0** | You write Python, and **Flutter** draws the window. That gives a modern Material 3 look without learning Dart. |
| Charts | Plain Flet `Container`s | Bars are rectangles whose height is proportional to the value, so no chart library is needed |
| Storage | **JSON file** (standard library) | Human-readable, no database server, and plenty fast for one person |
| Data models | `dataclasses` (standard library) | Clear "shapes" for Transaction, Budget and Goal |
| Packaging | **PyInstaller** via `flet pack` | Bundles Python, Flet, the code and the Flutter window into one `.exe` |
| Icon | **Pillow** (`tools/make_icon.py`) | Draws the icon from code, so it's easy to change |
| Tests | `unittest` (standard library) | Checks the maths and that every mission can be completed |

> A note on "Python + Flutter": Flutter apps are normally written in Dart. **Flet** is the bridge that lets you write Python while Flutter does the drawing.

---

## 3. Folder structure

```
FinWise/
├── main.py                  ← start here: window, sidebar, switching screens
├── build_exe.bat            ← one-click build of dist\FinWise.exe
├── requirements.txt
├── assets/icon.ico          ← app icon (made by tools/make_icon.py)
├── dist/FinWise.exe         ← the finished app
├── tests/test_finance.py    ← 15 automated tests
├── tools/make_icon.py
└── finwise/                 ← the app's own package
    ├── theme.py             ← palette, sizes, text styles (the ONLY place colours live)
    ├── models.py            ← Transaction, Budget, Goal + category list
    ├── storage.py           ← load/save data.json safely
    ├── finance.py           ← ALL money maths (no UI code at all)
    ├── state.py             ← AppState: holds data and changes it (real or sandbox)
    ├── content/
    │   ├── courses.py       ← lesson text + quizzes (pure data)
    │   └── challenges.py    ← Playground missions: setup, checklist, month simulation
    └── ui/
        ├── context.py       ← AppContext: the "toolbox" handed to every screen
        ├── components.py    ← reusable pieces: cards, buttons, inputs, charts
        └── views/
            ├── dashboard.py
            ├── transactions.py
            ├── budgets.py
            ├── goals.py
            ├── learn.py
            └── playground.py
```

---

## 4. How it works, in everyday language

### The big picture: four layers, each with one job

```
  Screens (ui/views)     "What you see"      – draw data, react to clicks
        │ ask
  AppState (state.py)    "The wallet"        – holds data, adds/deletes things
        │ uses
  finance.py             "The calculator"    – totals, budgets, interest…
  storage.py             "The filing cabinet" – saves to / loads from disk
```

Think of it like a café. The **screens** are the waiters taking orders. **AppState** is the kitchen that actually changes things. **finance.py** is the recipe book, and **storage.py** is the pantry. Each part does one job, so when something breaks you know where to look.

### What happens when you add an expense

1. You type `12.50`, pick "Groceries", and press **Enter**.
2. `TransactionsView._on_add` checks the input. `parse_money` rejects things like `abc` or `0` and shows a red message under the box.
3. It calls `state.add_transaction(...)`, which creates a `Transaction` object and **saves to disk immediately**, so nothing is lost if the app closes.
4. It calls `ctx.refresh()`, which asks the current screen to **rebuild itself** from the fresh data. Every total, chart and progress bar is recalculated.

Rebuilding the whole screen after each change is the simplest correct approach. Nothing can get out of sync, because the screen is always drawn from the saved data.

### Each main section

| Section | What it does | Key code |
|---|---|---|
| **Home (dashboard)** | Four stat cards (balance, income, spending, savings rate), a 6-month income-vs-expense chart, spending by category, budget watch, recent activity, next lesson and a daily tip. First-time users see a welcome card with a "sample data" button. | `DashboardView`, `finance.monthly_history`, `components.month_chart` |
| **Transactions** | An add form (Expense/Income toggle, amount, category, description, date picker) and a searchable, month-filterable history with delete confirmation. | `TransactionsView` |
| **Budgets** | A monthly limit per category. Bars are **green** under 80%, **coral** from 80–100%, and **red** when over. It also lists spending that has no budget. | `finance.budget_status` |
| **Goals** | Savings targets with progress bars, "save X ₫/month to finish in 6 or 12 months" hints, and an "add money" box. Adding money records a *Savings* expense, like moving cash into a savings account. | `state.contribute_to_goal` |
| **Learn** | 3 courses × 3 lessons. Each lesson has text, tip and example boxes, a 3-question quiz with explanations (2 of 3 correct passes), and a link to a matching Playground mission. | `content/courses.py`, `LearnView` |
| **Playground** | A sandbox wallet with pretend money, 10 missions with **live checklists**, a **Growth Lab** (compound-interest sliders) and a **Debt Lab** (credit-card payoff sliders). | `PlaygroundView`, `content/challenges.py` |

### The Playground trick (why the practice feels real)

```python
self.sandbox = AppState(persist=False)          # a second wallet that never saves
self.ctx = AppContext(page, state=self.sandbox) # a toolbox pointing at it
TransactionsView(self.ctx)                      # the REAL screen, given pretend data
```

The screens only ever talk to `ctx.state`, so they don't know whether the money is real. The Playground reuses the actual Transactions, Budgets, Goals and Dashboard screens, and none of your real data is touched.

A mission is three things (see `challenges.py`):

* `setup(state)` gives you a starting situation, for example "Income 20.000.000 ₫, but you overspent on wants".
* `tasks` is a list of `("description", check_function)` pairs. After every click, each function looks at the sandbox and returns True or False, so the checklist ticks itself off as you work.
* `tip` is a hint.

"Boss level: survive the month" runs `simulate_month()`. It spends about ¼ of each budget per week, randomly between 20% under and 10% over plan, then adds one random surprise (a dentist bill, a phone repair…). The lesson is to always leave a buffer.

### The two maths functions most worth reading

* `finance.compound_growth`: every month, **first** add interest (yearly rate ÷ 12), **then** add your deposit. It records one point per year for the chart.
* `finance.credit_card_payoff`: every month, interest is added and your payment is subtracted. If the payment is smaller than the interest, the debt never shrinks and the function returns `None`. The Debt Lab shows this as the **debt trap**.

---

## 5. Why this approach?

* **Maths is separate from screens.** You can test `finance.py` without opening a window, and the real app and the Playground share the same calculations.
* **Content is data.** To add a lesson, add a dictionary to `courses.py`. To add a mission, add a dictionary to `challenges.py`. No screen code changes.
* **Small named functions.** `_build_form`, `_on_add` and `_budget_card` each do one thing, so you can read any file from top to bottom.
* **One colour file.** Change `theme.py` and the whole app changes.
* **Safe saving.** `storage.save_data` writes a temporary file and then swaps it in. A crash mid-save can't corrupt your data, and a damaged file is backed up as `data.broken.json`.
* **Beginner-readable code.** No dense one-liners, and complex parts (like the regex that filters money input, month wrapping, or chart scaling) have comments explaining them.

---

## 6. Extending it

* **New expense category:** add it to `EXPENSE_CATEGORIES` in `models.py` (mark it `"need"`, `"want"` or `"savings"`) and give it an icon in `components.CATEGORY_ICONS`.
* **New lesson:** copy a lesson dictionary in `courses.py`. Block types are `text`, `tip`, `example` and `list`.
* **New mission:** write a `setup_…` function and some check functions in `challenges.py`, then add an entry to `CHALLENGES`.
* **Language:** all on-screen text lives in plain strings in `finwise/ui/views/*.py`, `main.py`, `content/courses.py` and `content/challenges.py`. Category names are in `models.py`. Data saved by older English versions is renamed automatically when it loads (see `LEGACY_CATEGORY_NAMES`).
* **Dates:** they are saved as `YYYY-MM-DD` because that order sorts correctly, then shown and typed as `DD/MM/YYYY` using `finance.display_date` and `components.parse_date`.
* **Currency:** amounts are in Vietnamese đồng (₫), written like `1.500.000 ₫` with no decimals. You can type amounts with or without dots (`1500000` or `1.500.000`). To change the currency, edit `CURRENCY_SYMBOL` and `format_money` in `finance.py`, and `money_input` in `components.py`.

*Lessons are general education, not financial advice.*

---

## Giấy phép / License

* **Mã nguồn:** MIT - xem [LICENSE](LICENSE).
* Bài học và câu hỏi là nội dung giáo dục tự biên soạn; không phải lời khuyên tài chính.
