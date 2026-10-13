"""
components/page_header.py

Clean section directly under the navy topbar. No duplicated page title
(the topbar already shows it) — just a bold heading on the left telling
the user which year to select, and the year selector pills on the
right. This keeps the area above the data sections minimal.

Styling lives in styles/css.py (_page_header_css) — edit there, not here.
"""

import streamlit as st
from components.filter_bar import filter_slot


def render_page_header(
    title: str,
    year_options: list[int] | None = None,
    year_default: int | None = None,
    key: str = "page_header_year",
):
    """
    When `year_options` is given, draws the Year pills in the SIDEBAR filter area and
    returns the selected year as an int (defaulting to year_default). Without
    `year_options` it just shows the heading in the page and returns None.
    """
    if not year_options:
        st.markdown(f'<div class="page-header-title">{title}</div>', unsafe_allow_html=True)
        return None

    labels = [str(y) for y in year_options]
    with filter_slot():
        with st.container(border=True):
            st.markdown('<span class="filter-bar-label">Year</span>', unsafe_allow_html=True)
            picked = st.pills(
                "Year",
                options=labels,
                default=str(year_default) if year_default is not None else labels[0],
                key=key,
                selection_mode="single",
                label_visibility="collapsed",
            )
    return int(picked) if picked is not None else year_default
