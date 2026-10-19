"""components/page_boot.py - shared page skeleton + the class selector used on every page."""
import streamlit as st
from config.settings import APP_NAME, PAGE_ICON, CLASSES, DEFAULT_CLASS, DEFAULT_YEAR
from styles.css import inject_css
from components.sidebar import render_sidebar
from components.topbar import render_topbar
from components.kpi_card import format_compact
from components.filter_bar import render_filter_bar
from components.page_header import render_page_header
from data.loader import prev_year
from types import SimpleNamespace
from config.settings import PROVINCE_BOARD_MAP
from components.filter_bar import filter_slot

ALL_CLASSES = "All Classes"
ALL_PROV = "All Provinces"
_YEARS_DESC = [2026, 2025, 2024]


def boot(page, subtitle, stat_label="Classes", stat_value="4", stat_icon="school"):
    st.set_page_config(page_title=f"{page} - {APP_NAME}", page_icon=PAGE_ICON, layout="wide")
    inject_css()
    render_sidebar()
    render_topbar(active_page=page, subtitle=subtitle, stat_label=stat_label, stat_value=stat_value, stat_icon=stat_icon)


def _sync(store, wkey):
    """Pill clicked: remember the choice (a pill can't be switched off, so an empty click restores the old value)."""
    v = st.session_state.get(wkey)
    if v is None: st.session_state[wkey] = st.session_state[store]
    else: st.session_state[store] = v


def _pill_card(label, options, store, default):
    ss = st.session_state
    if ss.get(store) not in options: ss[store] = default
    wkey = f"gf_{store}"
    if ss.get(wkey) != ss[store]: ss[wkey] = ss[store]
    with filter_slot():
        with st.container(border=True):
            st.markdown(f'<span class="filter-bar-label">{label}</span>', unsafe_allow_html=True)
            st.pills(label, options=options, key=wkey, selection_mode="single", label_visibility="collapsed",
                     on_change=_sync, args=(store, wkey))
    return ss[store]


def global_filters(note=None, single_class=False):
    """THE sidebar filters, identical on every page: Year, Class, Province. The choice is remembered while
    moving between pages. Returns an object with .year .cls .prov .boards (boards of the chosen province(s)).
    note          - one-line caption shown under the header when a filter does not change this page.
    single_class  - page cannot show 'All Classes': 12th is used instead (and the page says so)."""
    year = _pill_card("Year", _YEARS_DESC, "g_year", DEFAULT_YEAR)
    cls = _pill_card("Class", [ALL_CLASSES] + CLASSES, "g_class", DEFAULT_CLASS)
    prov = _pill_card("Province", [ALL_PROV] + list(PROVINCE_BOARD_MAP), "g_prov", ALL_PROV)
    boards = [b for bs in PROVINCE_BOARD_MAP.values() for b in bs] if prov == ALL_PROV else PROVINCE_BOARD_MAP[prov]
    if note: st.caption(note)
    if single_class and cls == ALL_CLASSES:
        st.caption(f"This page shows one class at a time, so {DEFAULT_CLASS} is shown. Pick a class in the sidebar filters to change it.")
        cls = DEFAULT_CLASS
    return SimpleNamespace(year=year, cls=cls, prov=prov, boards=boards)


def in_boards(df, boards):
    """Keep only rows of the boards in the chosen province(s)."""
    return df[df["Board"].isin(boards)]


def year_and_class(key, years=(2026, 2025, 2024), allow_all=False, title="Select Year to View Results", show_class=True):
    """Year pills (default 2026) + class pills (default 12th), drawn in the sidebar.
    show_class=False hides the class pills (for pages that show all classes). Returns (year, class)."""
    year = render_page_header(title, year_options=list(years), year_default=DEFAULT_YEAR, key=f"{key}_year")
    if not show_class:
        return year, DEFAULT_CLASS
    opts = (["All Classes"] if allow_all else []) + CLASSES
    cls = render_filter_bar("Class", options=opts, default=DEFAULT_CLASS, key=f"{key}_class") or DEFAULT_CLASS
    return year, cls


def delta_kpi(cur, prv, fmt=format_compact, pct=False, invert=False):
    """-> (delta_text, positive). pct=True means values are percentages (shown as points)."""
    if prv is None or cur is None: return "", True
    d = cur - prv
    txt = f"{abs(d):.1f} pts" if pct else fmt(abs(d))
    good = d >= 0
    return txt, (not good if invert else good)


def no_data(cls, year, df):
    ys = sorted(df["Year"].unique()) if len(df) else []
    st.info(f"No {cls} class data for {year}." + (f" Available years: {', '.join(map(str, ys))}." if ys else ""))
    st.stop()


def not_published(cls, what):
    st.info(f"{what} is not published for the {cls} class in the source gazettes, so there is nothing to show here.")
