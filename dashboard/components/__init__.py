"""
Dashboard components for reusable UI elements.
"""

import streamlit as st
import pandas as pd
from src.utils import format_percentage, get_display_name


def display_styled_metric(label: str, value: str, emoji: str = "📊"):
    """
    Display a custom styled metric card with centered content.
    
    Args:
        label: Metric label
        value: Metric value (as string)
        emoji: Optional emoji to display
    """
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #fffefb 0%, #fdf9f0 100%);
            border: 2px solid rgba(201, 107, 59, 0.2);
            border-radius: 16px;
            padding: 24px 16px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            min-height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        ">
            <div style="font-size: 2.8rem; margin-bottom: 8px; font-weight: 800; color: #c96b3b;">
                {emoji}
            </div>
            <div style="
                font-size: 2rem;
                font-weight: 800;
                color: #19231f;
                margin-bottom: 12px;
                line-height: 1.2;
            ">
                {value}
            </div>
            <div style="
                font-size: 0.95rem;
                color: #53615b;
                font-weight: 600;
                letter-spacing: 0.3px;
            ">
                {label}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
        format_func=lambda value: "Overview" if value == "None" else get_display_name(value),
        horizontal=True
    )


def create_section_selector(label: str, options: list[str], key: str):
    """Render a lightweight single-section selector instead of eager tab rendering."""
    return st.radio(
        label,
        options,
        key=key,
        horizontal=True,
        label_visibility="collapsed",
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


# ============================================================================
# FAN-FRIENDLY INSIGHT COMPONENTS
# ============================================================================


def display_player_highlight_story(
    player_name: str, 
    headline: str,
    recent_form: str,
    specialty: str = "",
    record: str = ""
):
    """
    Display a player story in fan-friendly narrative format.
    
    Args:
        player_name: Player name
        headline: Main headline (e.g., "🔥 On Fire")
        recent_form: Recent performance description
        specialty: Surface specialty or strength
        record: Career record for context
    """
    st.markdown(f"### {player_name}")
    st.markdown(f"**{headline}**")
    st.markdown(f"📊 {recent_form}")
    if specialty:
        st.markdown(f"💡 {specialty}")
    if record:
        st.markdown(f"📈 {record}")


def display_h2h_highlight(
    player1: str,
    player2: str,
    headline: str,
    record: str,
    asymmetry: str = ""
):
    """
    Display head-to-head matchup in fan-friendly format.
    
    Args:
        player1: First player name
        player2: Second player name
        headline: Main headline about the matchup
        record: The H2H record (e.g., "12-8")
        asymmetry: Any interesting asymmetries (surface/level differences)
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown(f"#### {player1}")
    
    with col2:
        st.markdown(f"**{headline}**")
        st.markdown(f"<p style='text-align: center; font-size: 1.1em;'>{record}</p>", 
                   unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"#### {player2}")
    
    if asymmetry:
        st.markdown(f"⚡ **Notable:** {asymmetry}")


def display_trend_indicator(metric_name: str, current_value: float, previous_value: float = None):
    """
    Display a metric with visual trend indicator.
    
    Args:
        metric_name: Name of the metric
        current_value: Current value
        previous_value: Previous value for comparison (shows trend)
    """
    if previous_value is not None:
        change = current_value - previous_value
        
        if change > 5:
            indicator = "🟢 ⬆️ Up"
            color = "green"
        elif change < -5:
            indicator = "🔴 ⬇️ Down"
            color = "red"
        else:
            indicator = "⚪ → Stable"
            color = "gray"
        
        st.markdown(f"**{metric_name}**: {current_value:.1f} ({indicator})")
    else:
        st.markdown(f"**{metric_name}**: {current_value:.1f}")


def display_achievement(title: str, description: str, emoji: str = "🏆"):
    """
    Display an achievement or milestone.
    
    Args:
        title: Achievement title
        description: Achievement description
        emoji: Achievement emoji icon
    """
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #ffd89b 0%, #19230f 100%);
            border-radius: 12px;
            padding: 16px;
            margin: 8px 0;
            border-left: 4px solid #c96b3b;
        ">
            <div style="font-size: 1.2em; font-weight: bold; margin-bottom: 4px;">
                {emoji} {title}
            </div>
            <div style="font-size: 0.95em; color: #333;">
                {description}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def display_surface_breakdown(surfaces_data: dict):
    """
    Display surface performance breakdown in an easy-to-scan format.
    
    Args:
        surfaces_data: Dict with surface names as keys and win rates as values
    """
    st.markdown("**Performance by Surface:**")
    
    for surface, win_rate in surfaces_data.items():
        # Create visual bar
        bar_width = int(win_rate / 100 * 50)
        
        if win_rate >= 60:
            color = "🟢"
            label = "Strong"
        elif win_rate >= 50:
            color = "🟡"
            label = "Solid"
        else:
            color = "🔴"
            label = "Weak"
        
        st.markdown(
            f"{color} **{surface}**: {win_rate:.0f}% ({label})"
        )
