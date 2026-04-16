"""
Player Analysis page for the Tennis Performance Dashboard.
Displays detailed player statistics, comparisons, and performance trends.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

from src import dataset, features, utils, plots
from src.constants import ANNUAL_FILTERS
from dashboard.components import (
    display_metric_card,
    display_player_header,
    display_stats_table,
    display_section_header,
    display_info_box,
    create_filter_columns,
)


def _sort_player_matches(matches: pd.DataFrame, ascending: bool = True) -> pd.DataFrame:
    """Sort player matches by the best available date field."""
    for col in ("t_date", "date", "t_year"):
        if col in matches.columns:
            return matches.sort_values(col, ascending=ascending)
    return matches.sort_index(ascending=ascending)


def _safe_metric_value(series: pd.Series, default="N/A"):
    """Return the first non-null value from a series for UI metrics."""
    if series.empty:
        return default
    value = series.iloc[0]
    return default if pd.isna(value) else value


def show():
    """Display the Player Analysis page."""

    # Get data from session state
    players_df = st.session_state.data["players"]
    perf_data = st.session_state.data["yearly_performance"]
    match_data = st.session_state.data["matches"]

    # Sidebar filters
    with st.sidebar:
        st.subheader("🎾 Player Selection")
        player = st.selectbox(
            "Select a Player",
            options=dataset.get_player_names(players_df),
            key="player_select",
        )

        compare_players = st.checkbox("Compare with Another Player")

        show_last_matches = st.checkbox("Show Last 5 Matches", value=False)

        st.divider()
        st.subheader("📊 Filters")
        filters = utils.get_filter_options(match_data)
        filter_option = create_filter_columns(filters)

    # Get player data
    player_data = players_df[players_df["name"] == player]
    player_perf = perf_data[perf_data["player"] == player]
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy()

    player_matches["result"] = (player_matches["w_name"] == player).astype(int)
    player_matches = _sort_player_matches(player_matches)

    # Calculate streaks
    streaks = utils.calculate_streaks(player_matches)

    # Main content
    if compare_players:
        display_player_comparison(
            player,
            player_data,
            player_perf,
            player_matches,
            streaks,
            players_df,
            perf_data,
            match_data,
            filter_option,
            show_last_matches,
        )
    else:
        display_single_player(
            player,
            player_data,
            player_perf,
            player_matches,
            streaks,
            match_data,
            filter_option,
            show_last_matches,
        )


def display_single_player(
    player,
    player_data,
    player_perf,
    player_matches,
    streaks,
    match_data,
    filter_option,
    show_last_matches,
):
    """Display analysis for a single player."""

    display_player_header(player)

    if show_last_matches and len(player_matches) > 0:
        st.dataframe(
            _sort_player_matches(player_matches, ascending=False).head(5),
            hide_index=True,
            width="stretch",
        )

    if filter_option != "None":
        display_filter_analysis(player, player_matches, match_data, filter_option)
    else:
        display_overall_stats(player_data, player_perf, player_matches, streaks)


def display_overall_stats(player_data, player_perf, player_matches, streaks):
    """Display overall player statistics."""

    col1, col2 = st.columns(2)

    with col1:
        display_section_header("Basic Info", "👤")
        display_metric_card("Country", player_data["country"].values[0])
        display_metric_card("Gender", player_data["gender"].values[0].title())
        display_metric_card("Dominant Hand", player_data["hand"].values[0])
        display_metric_card("Date of Birth", player_data["birthdate"].values[0])
        display_metric_card(
            "Career Duration", player_data["career_duration"].values[0], " years"
        )

    with col2:
        display_section_header("Career Stats", "📈")
        display_metric_card("Total Matches", player_data["total_matches"].values[0])
        display_metric_card("Total Wins", player_data["wins"].values[0])
        display_metric_card(
            "Win Percentage",
            utils.format_percentage(player_data["wlr"].values[0] * 100),
        )
        display_metric_card(
            "Longest Win Streak", streaks["longest_win_streak"] or "N/A"
        )
        display_metric_card(
            "Longest Lose Streak", streaks["longest_losing_streak"] or "N/A"
        )

    # Additional stats
    if st.checkbox("Show Advanced Stats"):
        col1, col2 = st.columns(2)

        with col1:
            display_section_header("Serve Stats", "🎾")
            display_metric_card(
                "Serve Games Won %",
                utils.format_percentage(player_data["serve_game_won%"].values[0]),
            )

        with col2:
            display_section_header("Break Stats", "🔓")
            display_metric_card(
                "Break Points Saved %",
                utils.format_percentage(player_data["break_points_saved%"].values[0]),
            )

    # Performance trends
    st.divider()
    display_section_header("Performance Trends Over Time", "📊")

    col1, col2 = st.columns(2)

    with col1:
        # Win percentage trend
        fig_wlr = px.line(
            player_perf,
            x="t_year",
            y="wlr",
            title="Win Percentage by Year",
            markers=True,
        )
        st.plotly_chart(fig_wlr, width="stretch")

    with col2:
        # Rank trend
        fig_rank = px.line(
            player_perf, x="t_year", y="rank", title="Ranking by Year", markers=True
        )
        st.plotly_chart(fig_rank, width="stretch")

    col1, col2 = st.columns(2)

    with col1:
        # Wins trend
        fig_wins = px.line(
            player_perf, x="t_year", y="win", title="Wins by Year", markers=True
        )
        st.plotly_chart(fig_wins, width="stretch")

    with col2:
        # Total matches trend
        player_perf_copy = player_perf.copy()
        player_perf_copy["total_matches"] = (
            player_perf_copy["win"] + player_perf_copy["loss"]
        )
        fig_total = px.line(
            player_perf_copy,
            x="t_year",
            y="total_matches",
            title="Total Matches by Year",
            markers=True,
        )
        st.plotly_chart(fig_total, width="stretch")

    # Raw data
    if st.checkbox("Show Raw Data"):
        st.subheader("Player Data")
        st.dataframe(player_data, hide_index=True, width="stretch")
        st.subheader("Yearly Performance")
        st.dataframe(player_perf, hide_index=True, width="stretch")


def display_filter_analysis(player, player_matches, match_data, filter_option):
    """Display analysis filtered by a specific column."""

    wld = features.create_win_loss_stats(match_data, filter_option)
    wld = wld[wld["name"] == player].sort_values("wlr", ascending=False)

    if len(wld) == 0:
        display_info_box(f"No data available for filter: {filter_option}", "warning")
        return

    display_section_header(f"Statistics by {filter_option}", "📊")

    # Top 2 results
    col1, col2 = st.columns(2)

    with col1:
        st.metric(f"Best {filter_option}", wld[filter_option].iloc[0])
        st.metric("Win Percentage", utils.format_percentage(wld["wlr"].iloc[0] * 100))
        st.metric("Total Matches", int(wld["total_matches"].iloc[0]))

    with col2:
        if len(wld) > 1:
            st.metric(f"2nd Best {filter_option}", wld[filter_option].iloc[1])
            st.metric(
                "Win Percentage", utils.format_percentage(wld["wlr"].iloc[1] * 100)
            )
            st.metric("Total Matches", int(wld["total_matches"].iloc[1]))

    # Bar chart
    fig = plots.create_bar_comparison(
        wld,
        x=filter_option,
        y="wlr",
        title=f"{filter_option.title()} Comparison",
        y_label="Win Percentage",
    )
    st.plotly_chart(fig, width="stretch")

    # Annual breakdown
    if filter_option in ANNUAL_FILTERS:
        wlda = features.create_annual_win_loss_stats(match_data, filter_option)
        wlda = wlda[wlda["player"] == player]

        fig_annual = px.line(
            wlda,
            x="t_year",
            y="wlr",
            color=filter_option,
            title=f"Win Percentage Over Time by {filter_option}",
            markers=True,
        )
        st.plotly_chart(fig_annual, width="stretch")

    # Raw data
    if st.checkbox(f"Show {filter_option} Data"):
        st.dataframe(wld, hide_index=True, width="stretch")


def display_player_comparison(
    player1,
    player_data1,
    player_perf1,
    player_matches1,
    streaks1,
    players_df,
    perf_data,
    match_data,
    filter_option,
    show_last_matches,
):
    """Display comparison between two players."""

    with st.sidebar:
        player2 = st.selectbox(
            "Select Player to Compare",
            options=dataset.get_player_names(players_df),
            key="player_compare_select",
        )

    if player2 == player1:
        display_info_box("Please select a different player to compare", "warning")
        return

    # Get second player data
    player_data2 = players_df[players_df["name"] == player2]
    player_perf2 = perf_data[perf_data["player"] == player2]
    player_matches2 = match_data[
        (match_data["w_name"] == player2) | (match_data["l_name"] == player2)
    ].copy()
    player_matches2["result"] = (player_matches2["w_name"] == player2).astype(int)
    player_matches2 = _sort_player_matches(player_matches2)
    streaks2 = utils.calculate_streaks(player_matches2)

    st.header(f"🎾 {player1} vs {player2}")

    if show_last_matches:
        display_head_to_head(player1, player2, match_data)

    if filter_option != "None":
        display_filter_comparison(player1, player2, match_data, filter_option)
    else:
        display_overall_comparison(
            player1,
            player_data1,
            player_perf1,
            streaks1,
            player2,
            player_data2,
            player_perf2,
            streaks2,
        )


def display_head_to_head(player1, player2, match_data):
    """Display head-to-head match history."""

    h2h = features.get_head_to_head(match_data, player1, player2)

    if len(h2h) > 0:
        st.subheader("Recent Head-to-Head Matches")
        st.dataframe(
            _sort_player_matches(h2h, ascending=False).head(5),
            hide_index=True,
            width="stretch",
        )

        # H2H summary
        p1_wins = len(h2h[h2h["w_name"] == player1])
        p2_wins = len(h2h[h2h["w_name"] == player2])

        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"{player1} Wins", p1_wins)
        with col2:
            st.metric(f"{player2} Wins", p2_wins)
    else:
        st.info(f"No head-to-head matches found between {player1} and {player2}.")


def display_overall_comparison(
    player1,
    player_data1,
    player_perf1,
    streaks1,
    player2,
    player_data2,
    player_perf2,
    streaks2,
):
    """Display overall comparison metrics."""

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"👤 {player1}")
        display_metric_card("Country", _safe_metric_value(player_data1["country"]))
        display_metric_card("Total Matches", _safe_metric_value(player_data1["total_matches"], 0))
        display_metric_card("Total Wins", _safe_metric_value(player_data1["wins"], 0))
        display_metric_card(
            "Win %", utils.format_percentage(_safe_metric_value(player_data1["wlr"], 0) * 100)
        )
        highest_rank1 = player_perf1["rank"].dropna().min() if "rank" in player_perf1.columns else None
        display_metric_card("Highest Rank", int(highest_rank1) if pd.notna(highest_rank1) else "N/A")

    with col2:
        st.subheader(f"👤 {player2}")
        display_metric_card("Country", _safe_metric_value(player_data2["country"]))
        display_metric_card("Total Matches", _safe_metric_value(player_data2["total_matches"], 0))
        display_metric_card("Total Wins", _safe_metric_value(player_data2["wins"], 0))
        display_metric_card(
            "Win %", utils.format_percentage(_safe_metric_value(player_data2["wlr"], 0) * 100)
        )
        highest_rank2 = player_perf2["rank"].dropna().min() if "rank" in player_perf2.columns else None
        display_metric_card("Highest Rank", int(highest_rank2) if pd.notna(highest_rank2) else "N/A")

    # Comparison charts
    st.divider()
    st.subheader("📊 Performance Comparison")

    col1, col2 = st.columns(2)

    with col1:
        # Win % over time
        comparison_perf = pd.concat([player_perf1, player_perf2], ignore_index=True)
        fig = px.line(
            comparison_perf,
            x="t_year",
            y="wlr",
            color="player",
            title="Win Percentage Over Time",
            markers=True,
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        # Ranking over time
        fig = px.line(
            comparison_perf,
            x="t_year",
            y="rank",
            color="player",
            title="Ranking Over Time",
            markers=True,
        )
        st.plotly_chart(fig, width="stretch")


def display_filter_comparison(player1, player2, match_data, filter_option):
    """Display filter-based comparison between two players."""

    wld1 = features.create_win_loss_stats(match_data, filter_option)
    wld1 = wld1[wld1["name"] == player1].sort_values("wlr", ascending=False)

    wld2 = features.create_win_loss_stats(match_data, filter_option)
    wld2 = wld2[wld2["name"] == player2].sort_values("wlr", ascending=False)

    st.subheader(f"Comparison by {filter_option}")

    combined_data = pd.concat([wld1, wld2], ignore_index=True)
    if combined_data.empty:
        st.info(f"No comparison data available for {player1} and {player2} by {filter_option}.")
        return

    fig = plots.create_bar_comparison(
        combined_data,
        x=filter_option,
        y="wlr",
        color="name",
        title=f"{filter_option.title()} Comparison",
        y_label="Win Percentage",
    )
    st.plotly_chart(fig, width="stretch")

    if st.checkbox(f"Show {filter_option} Data"):
        st.dataframe(combined_data, hide_index=True, width="stretch")
