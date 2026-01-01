"""
Dashboard components for reusable UI elements.
"""

import streamlit as st
import pandas as pd
from src.utils import format_percentage


def display_metric_card(
    label: str, value, suffix: str = "", metric_type: str = "default"
):
    """
    Display a metric card with consistent styling.

    Args:
        label: Metric label
        value: Metric value
        suffix: Suffix to append (e.g., '%', 'years')
        metric_type: Type of metric ('default', 'positive', 'negative', 'neutral')
    """
    delta_color = None
    if metric_type == "positive":
        delta_color = "off"
    elif metric_type == "negative":
        delta_color = "off"

    st.metric(label=label, value=f"{value}{suffix}")


def display_player_header(name: str, col_count: int = 2):
    """
    Display player header with name.

    Args:
        name: Player name
        col_count: Number of columns for layout
    """
    st.header(f"🎾 {name}")


def display_stats_table(data: pd.DataFrame, title: str = ""):
    """
    Display statistics table with consistent formatting.

    Args:
        data: DataFrame to display
        title: Optional table title
    """
    if title:
        st.subheader(title)
    st.dataframe(data, hide_index=True, use_container_width=True)


def display_section_header(title: str, icon: str = "📊"):
    """
    Display section header with icon.

    Args:
        title: Section title
        icon: Optional emoji icon
    """
    st.subheader(f"{icon} {title}")


def create_filter_columns(filter_options: list, default_index: int = 0):
    """
    Create a radio button filter selector.

    Args:
        filter_options: List of filter options
        default_index: Default selected index

    Returns:
        Selected filter option
    """
    return st.radio(
        "Filter/Compare By:",
        options=filter_options,
        index=default_index,
        horizontal=False,
    )


def create_comparison_selector(data_list: list, key_suffix: str = ""):
    """
    Create comparison selector UI.

    Args:
        data_list: List of items to select from
        key_suffix: Unique key suffix

    Returns:
        Selected item
    """
    return st.selectbox(
        "Select an item to compare",
        options=sorted(set(data_list)),
        key=f"compare_{key_suffix}",
    )


def display_metrics_grid(metrics_dict: dict, cols: int = 2):
    """
    Display multiple metrics in a grid layout.

    Args:
        metrics_dict: Dictionary of {label: value} pairs
        cols: Number of columns in grid
    """
    columns = st.columns(cols)

    for idx, (label, value) in enumerate(metrics_dict.items()):
        with columns[idx % cols]:
            display_metric_card(label, value)


def display_info_box(message: str, message_type: str = "info"):
    """
    Display an info/warning/success box.

    Args:
        message: Message text
        message_type: Type of message ('info', 'warning', 'success', 'error')
    """
    if message_type == "warning":
        st.warning(message)
    elif message_type == "success":
        st.success(message)
    elif message_type == "error":
        st.error(message)
    else:
        st.info(message)
