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
    st.dataframe(data, hide_index=True, width="stretch")


def display_section_header(title: str, icon: str = "📊"):
    """
    Display section header with icon.

    Args:
        title: Section title
        icon: Optional emoji icon
    """
    st.markdown(
        f"""
        <h2 style="
            color: #17352b;
            border-bottom: 2px solid rgba(23, 53, 43, 0.16);
            padding-bottom: 0.55rem;
            margin-bottom: 1rem;
            font-family: Georgia, 'Times New Roman', serif;
            letter-spacing: -0.02em;
        ">{icon} {title}</h2>
        """,
        unsafe_allow_html=True
    )


def display_info_box(message: str, box_type: str = "info"):
    """
    Display an info box with consistent styling.

    Args:
        message: Message to display
        box_type: Type of box ('info', 'warning', 'error', 'success')
    """
    if box_type == "info":
        st.info(message)
    elif box_type == "warning":
        st.warning(message)
    elif box_type == "error":
        st.error(message)
    elif box_type == "success":
        st.success(message)
    else:
        st.info(message)


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
        "Select Filter",
        filter_options,
        index=default_index,
        horizontal=True
    )


# ============================================================================
# SMART FILTERING SYSTEM
# ============================================================================


def create_smart_filters(match_data: pd.DataFrame, players_df: pd.DataFrame):
    """
    Create an advanced filtering system with presets and multi-select options.
    
    Args:
        match_data: Match DataFrame
        players_df: Players DataFrame
        
    Returns:
        Dictionary with applied filters
    """
    st.sidebar.markdown("## 🔍 Advanced Filters")
    
    filters = {}
    
    # Filter Preset Templates
    st.sidebar.subheader("📋 Filter Presets")
    preset = st.sidebar.selectbox(
        "Quick Templates",
        ["None", "Top 20 Players", "Grand Slams Only", "Recent Year", "All Data"],
        key="filter_preset"
    )
    
    # Apply preset
    if preset == "Top 20 Players":
        from src.features import get_top_players_overall
        top_20 = get_top_players_overall(match_data, limit=20, min_matches=20)
        filters["players"] = top_20["player"].tolist()
        st.sidebar.success("✅ Top 20 players selected")
    elif preset == "Grand Slams Only":
        filters["tournament_levels"] = ["Grand Slam"]
        st.sidebar.success("✅ Grand Slams only")
    elif preset == "Recent Year":
        max_year = int(match_data["t_year"].max())
        filters["year_range"] = (max_year, max_year)
        st.sidebar.success(f"✅ Year {max_year} selected")
    
    st.sidebar.divider()
    
    # Date Range Filter
    st.sidebar.subheader("📅 Date Range")
    min_year = int(match_data["t_year"].min())
    max_year = int(match_data["t_year"].max())
    
    year_range = st.sidebar.slider(
        "Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1,
        key="year_range_filter"
    )
    filters["year_range"] = year_range
    
    st.sidebar.divider()
    
    # Surface Filter
    st.sidebar.subheader("🏟️ Surface")
    surfaces = ["All"] + sorted(match_data["surface"].dropna().unique().tolist())
    selected_surfaces = st.sidebar.multiselect(
        "Select Surfaces",
        surfaces,
        default=["All"],
        key="surface_filter"
    )
    if "All" not in selected_surfaces:
        filters["surfaces"] = selected_surfaces
    
    # Tournament Level Filter
    st.sidebar.subheader("🏆 Tournament Level")
    levels = ["All"] + sorted(match_data["t_level"].dropna().unique().tolist())
    selected_levels = st.sidebar.multiselect(
        "Select Levels",
        levels,
        default=["All"],
        key="level_filter"
    )
    if "All" not in selected_levels:
        filters["tournament_levels"] = selected_levels
    
    st.sidebar.divider()
    
    # Player Filter
    st.sidebar.subheader("🎾 Players")
    player_list = sorted(pd.concat([match_data["w_name"], match_data["l_name"]]).unique().tolist())
    player_list = [p for p in player_list if pd.notna(p)]
    
    selected_players = st.sidebar.multiselect(
        "Filter by Players (optional)",
        player_list,
        key="player_filter"
    )
    if selected_players:
        filters["players"] = selected_players
    
    st.sidebar.divider()
    
    # Match Statistics Filter
    st.sidebar.subheader("📊 Match Statistics")
    min_matches = st.sidebar.slider(
        "Minimum Matches for Analysis",
        min_value=1,
        max_value=100,
        value=20,
        step=5,
        key="min_matches_filter"
    )
    filters["min_matches"] = min_matches
    
    return filters


def apply_filters(match_data: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Apply selected filters to match data.
    
    Args:
        match_data: Match DataFrame
        filters: Dictionary of filters from create_smart_filters()
        
    Returns:
        Filtered DataFrame
    """
    filtered = match_data.copy()
    
    # Apply year range
    if "year_range" in filters:
        start_year, end_year = filters["year_range"]
        filtered = filtered[
            (filtered["t_year"] >= start_year) & 
            (filtered["t_year"] <= end_year)
        ]
    
    # Apply surfaces
    if "surfaces" in filters:
        filtered = filtered[filtered["surface"].isin(filters["surfaces"])]
    
    # Apply tournament levels
    if "tournament_levels" in filters:
        filtered = filtered[filtered["t_level"].isin(filters["tournament_levels"])]
    
    # Apply player filter (matches involving these players)
    if "players" in filters:
        player_mask = (
            filtered["w_name"].isin(filters["players"]) | 
            filtered["l_name"].isin(filters["players"])
        )
        filtered = filtered[player_mask]
    
    return filtered


def display_filter_summary(filters: dict):
    """
    Display a summary of applied filters.
    
    Args:
        filters: Dictionary of applied filters
    """
    if not filters:
        return
    
    summary_parts = []
    
    if "year_range" in filters:
        start, end = filters["year_range"]
        summary_parts.append(f"📅 Years: {start}-{end}")
    
    if "surfaces" in filters:
        surfaces = ", ".join(filters["surfaces"])
        summary_parts.append(f"🏟️ Surfaces: {surfaces}")
    
    if "tournament_levels" in filters:
        levels = ", ".join(filters["tournament_levels"])
        summary_parts.append(f"🏆 Levels: {levels}")
    
    if "players" in filters:
        player_count = len(filters["players"])
        summary_parts.append(f"🎾 Players: {player_count} selected")
    
    if summary_parts:
        st.info("**Active Filters:** " + " | ".join(summary_parts))
