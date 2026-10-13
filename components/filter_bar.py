"""
components/filter_bar.py

Capsule filter rows shown under the topbar. Each row is a bordered white card
(st.container) holding a label and a native st.pills / st.multiselect widget.

    selected_year = render_filter_bar("Year", options=[2024, 2025, 2026], default=2026, key="year_filter")
    results = render_filter_row([{"label": "Year", "options": [...], "default": 2026, "key": "f1"}, ...])
"""

import streamlit as st


def filter_slot():
    """Where filters are drawn: the 'Filters' area created by components/sidebar.py
    (falls back to the plain sidebar if the slot isn't there)."""
    return st.session_state.get("_filter_slot") or st.sidebar


def render_filter_bar(label: str, options: list, default=None, key: str = "", multi: bool = False):
    """Single labeled row of capsule filter options."""
    with filter_slot():
        with st.container(border=True):
            st.markdown(f'<span class="filter-bar-label">{label}</span>', unsafe_allow_html=True)
            return st.pills(label, options=options, default=default,
                            selection_mode="multi" if multi else "single", key=key, label_visibility="collapsed")


def render_filter_row(filters: list[dict]):
    """
    Several filters stacked in ONE bordered card in the sidebar. Each dict: label, options, default, key,
    multi (bool), and optionally dropdown=True (multiselect; leave default empty to mean "all"),
    placeholder (text shown in an empty dropdown).
    """
    results = {}
    with filter_slot():
        with st.container(border=True):
            for f in filters:
                st.markdown(f'<span class="filter-bar-label">{f["label"]}</span>', unsafe_allow_html=True)
                if f.get("dropdown"):
                    results[f["key"]] = st.multiselect(f["label"], options=f["options"], default=f.get("default"),
                                                       key=f["key"], label_visibility="collapsed",
                                                       placeholder=f.get("placeholder", "All boards (pick to narrow down)"))
                else:
                    results[f["key"]] = st.pills(f["label"], options=f["options"], default=f.get("default"),
                                                 selection_mode="multi" if f.get("multi") else "single",
                                                 key=f["key"], label_visibility="collapsed")
    return results
