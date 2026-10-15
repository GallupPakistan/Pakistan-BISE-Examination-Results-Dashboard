"""components/notes.py - the 'Important Points' block shown at the end of the Overview page.

Everything about coverage, missing boards and special cases is computed from the data in
data/processed/, so it stays correct whenever the CSVs are updated.
"""
import streamlit as st
from config.settings import CLASSES, LAST_UPDATED, DEFAULT_CLASS, DEFAULT_YEAR
from components.chart_card import chart_card
from data.loader import load, KINDS

LABELS = {"overall": "Pass % / results", "gender": "Gender", "category": "Regular vs Private", "group": "Group wise",
          "subject": "Subject wise", "district": "District wise", "grade": "Grade distribution"}

# A board whose pass % is at or above this is treated as reporting "promoted" results, not strict pass/fail.
PROMOTED_PCT = 97.0
# If more than this many boards are missing, list the boards that DID publish instead.
MAX_LISTED_MISSING = 4


def _years(ys) -> str:
    """[2024, 2025, 2026] -> '2024-2026'; [2024, 2026] -> '2024, 2026'; [2025] -> '2025'."""
    ys = sorted(set(int(y) for y in ys))
    if not ys:
        return ""
    if len(ys) == 1:
        return str(ys[0])
    if ys == list(range(ys[0], ys[-1] + 1)):
        return f"{ys[0]}-{ys[-1]}"
    return ", ".join(str(y) for y in ys)


def _names(items) -> str:
    items = sorted(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def _coverage_lines(ov) -> list[str]:
    all_years = sorted(ov["Year"].unique())
    lines = []
    for c in CLASSES:
        x = ov[ov["Class"] == c]
        all_boards = set(x["Board"].unique())       # boards that publish THIS class (BIEK Karachi only does 12th)
        if x.empty:
            lines.append(f"- **{c}:** no results published")
            continue
        parts = []
        for y in all_years:
            have = set(x[x["Year"] == y]["Board"])
            if not have:
                parts.append(f"{y}: not published")
                continue
            missing = all_boards - have
            if not missing:
                parts.append(f"{y}: all {len(have)} boards")
            elif len(missing) <= MAX_LISTED_MISSING:
                parts.append(f"{y}: {len(have)} boards (no {_names(missing)})")
            else:
                parts.append(f"{y}: **only {len(have)} boards** ({_names(have)})")
        lines.append(f"- **{c}** · " + " · ".join(parts))
    return lines


def _table(all_years) -> str:
    span = _years(all_years)
    rows = []
    for k in KINDS[1:]:
        t = load(k)
        cells = []
        for c in CLASSES:
            x = t[t["Class"] == c]
            n = x["Board"].nunique()
            if not n:
                cells.append("❌ not published")
                continue
            ys = _years(x["Year"].unique())
            cells.append(f"{n} boards" + ("" if ys == span else f" · {ys}"))
        rows.append(f"| {LABELS[k]} | " + " | ".join(cells) + " |")
    return "| Data | " + " | ".join(CLASSES) + " |\n|---|" + "---|" * len(CLASSES) + "\n" + "\n".join(rows)


def _special_cases(ov) -> list[str]:
    out = []
    x = ov.copy()
    x["pct"] = x["Passed"] / x["Appeared"] * 100
    hi = x[x["pct"] >= PROMOTED_PCT]
    if not hi.empty:
        groups = []
        for (c, b), g in hi.groupby(["Class", "Board"]):
            groups.append((CLASSES.index(c), b, f"{c} {b} {_years(g['Year'])}"))
        groups.sort()
        out.append("Pass % of " + f"{PROMOTED_PCT:.0f}%" + " or more (" + "; ".join(t for _, _, t in groups) +
                   "): these boards appear to report *promoted* results rather than strict pass/fail, so their very high "
                   "pass % is not comparable with other boards.")
    # classes where the latest year is only partly published
    latest = int(ov["Year"].max())
    all_boards = ov["Board"].nunique()
    for c in CLASSES:
        n = ov[(ov["Class"] == c) & (ov["Year"] == latest)]["Board"].nunique()
        if 0 < n < all_boards / 2:
            out.append(f"{c} {latest} is only partly published ({n} of {all_boards} boards), so its {latest} totals are not "
                       f"comparable with {c} in earlier years, and some cross-class charts show fewer classes for {latest}.")
    out.append("Sindh = BIEK Karachi, 12th class only, from the official result gazettes (all main groups; Home Economics "
               "and special candidates, a few hundred, are not included; 2024 also lacks Humanities Private, about 2% of candidates). "
               "Other Sindh boards and classes publish roll-number lists or news figures only, so they are not in the dashboard.")
    out.append("Boards that did not publish a class in a given year are left out of that year's totals; "
               "year-on-year changes use only boards that published both years.")
    out.append("Source: official BISE result gazettes, in the class workbooks in `data/source/`.")
    return out


def render_important_points():
    ov = load("overall")
    all_years = sorted(ov["Year"].unique())
    n_boards = ov["Board"].nunique()
    table = _table(all_years)
    with chart_card("Important Points", f"Please read before using the numbers · Last updated {LAST_UPDATED}"):
        st.markdown(
            f"**Defaults:** every page opens on the **{DEFAULT_CLASS} class** and **{DEFAULT_YEAR}**. "
            "Use the Year and Class filters in the sidebar to change them; each page also has a *Compare all classes* section.\n\n"
            f"**Data coverage (results)** · {n_boards} boards, {_years(all_years)}\n\n"
            + "\n".join(_coverage_lines(ov)) + "\n\n"
            "**What each class publishes (number of boards with data"
            f", {_years(all_years)} unless a year range is shown)**\n\n" + table + "\n\n"
            "**Comparison tools:** Class Comparison (insights + board rankings), Head to Head (any two selections), "
            "Cohort Progress (a batch followed from 9th to 12th, a proxy not exact students).\n\n"
            "**How numbers are calculated**\n"
            "- Pass % = Passed ÷ Appeared everywhere (recomputed from counts, not copied from gazettes).\n"
            "- Totals include only boards that published that class and year; changes vs the previous year use only boards that published both years.\n"
            "- Board names are unified (DGK / D.G. Khan → DG Khan, FSD → Faisalabad, FBISE (Islamabad) → FBISE).\n"
            "- Group wise: 9th/10th use Science / Humanities; 11th/12th use Pre-Medical, Pre-Engineering, etc. "
            "For cross-class comparison they are merged into streams (Science, Humanities, Commerce, Other).\n"
            "- Split tables (gender, group, category) are used only where they add up to the board's reported total.\n\n"
            "**Special cases**\n" + "\n".join(f"- {s}" for s in _special_cases(ov))
        )
