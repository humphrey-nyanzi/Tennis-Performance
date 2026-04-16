"""
Tournament Analysis page for the Tennis Performance Dashboard.
Displays tournament statistics and performance metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from src import dataset, features
from dashboard.components import (
    display_metric_card,
    display_stats_table,
    display_section_header,
    display_info_box,
)


def show():
    """Display the Tournament Analysis page."""

    # Get data from session state
    tournaments_df = st.session_state.data["tournaments"]
    match_data = st.session_state.data["matches"]

    # Sidebar filters
    with st.sidebar:
        st.subheader("🏆 Tournament Selection")
        tournament = st.selectbox(
            "Select a Tournament",
            options=dataset.get_tournament_names(tournaments_df),
            key="tournament_select",
        )

        compare_tournaments = st.checkbox("Compare with Another Tournament")

    # Main content
    if compare_tournaments:
        display_tournament_comparison(tournament, tournaments_df, match_data)
    else:
        display_single_tournament(tournament, tournaments_df, match_data)


def display_single_tournament(tournament, tournaments_df, match_data):
    """Display analysis for a single tournament."""

    tournament_data = tournaments_df[tournaments_df["name"] == tournament]

    if tournament_data.empty:
        display_info_box(f"No data found for tournament: {tournament}", "warning")
        return

    st.header(f"🏆 {tournament}")

    # Basic metrics
    col1, col2 = st.columns(2)

    with col1:
        display_section_header("Tournament Info", "ℹ️")
        display_metric_card("Surface", tournament_data["surface"].values[0])
        display_metric_card("Best Of", tournament_data["best_of"].values[0])
        display_metric_card("Month Played", tournament_data["t_month"].values[0])

    with col2:
        display_section_header("Statistics", "📊")
        display_metric_card(
            "Avg Match Duration",
            f"{round(tournament_data['minutes'].values[0], 1)} min",
        )
        display_metric_card("Total Matches", tournament_data["total_matches"].values[0])
        display_metric_card(
            "Tournament Duration",
            f"{tournament_data['tournament_duration'].values[0]} years",
        )

    # Yearly trends
    st.divider()
    st.subheader("📈 Matches Over Time")

    tournament_yearly_stats = (
        match_data[match_data["t_name"] == tournament]
        .groupby("t_year")
        .size()
        .reset_index(name="total_matches")
    )

    fig_yearly = px.line(
        tournament_yearly_stats,
        x="t_year",
        y="total_matches",
        title="Total Matches by Year",
        markers=True,
    )
    st.plotly_chart(fig_yearly, width="stretch")

    # Top players
    st.divider()
    st.subheader("🎾 Top Winners at This Tournament")

    top_winners = features.get_tournament_player_winners(
        match_data, tournament, limit=10
    )

    fig_winners = px.bar(
        top_winners,
        x="player",
        y="wins",
        title="Top 10 Winners",
        labels={"player": "Player", "wins": "Number of Wins"},
    )
    st.plotly_chart(fig_winners, width="stretch")

    st.dataframe(top_winners, hide_index=True, width="stretch")

    # Surface distribution
    st.divider()
    st.subheader("🏟️ Surface Distribution")

    fig_surface = plots.create_surface_distribution(match_data, tournament)
    st.plotly_chart(fig_surface, width="stretch")

    # Head-to-head comparison
    st.divider()
    st.subheader("⚡ Head-to-Head Comparison")

    all_players = sorted(
        set(match_data["w_name"].unique().tolist())
        | set(match_data["l_name"].unique().tolist())
    )

    col1, col2 = st.columns(2)

    with col1:
        player1 = st.selectbox("Player 1", options=all_players, key="h2h_p1")

    with col2:
        player2 = st.selectbox("Player 2", options=all_players, key="h2h_p2")

    if player1 != player2:
        h2h = features.get_head_to_head(match_data, player1, player2, tournament)

        if len(h2h) > 0:
            st.subheader(f"Matches: {player1} vs {player2}")
            st.dataframe(h2h, hide_index=True, width="stretch")

            p1_wins = len(h2h[h2h["w_name"] == player1])
            p2_wins = len(h2h[h2h["w_name"] == player2])

            col1, col2 = st.columns(2)
            with col1:
                st.metric(f"{player1} Wins", p1_wins)
            with col2:
                st.metric(f"{player2} Wins", p2_wins)
        else:
            display_info_box(
                "No matches found between these players at this tournament", "info"
            )
    else:
        display_info_box("Please select different players", "warning")


def display_tournament_comparison(tournament1, tournaments_df, match_data):
    """Display comparison between two tournaments."""

    with st.sidebar:
        tournament2 = st.selectbox(
            "Select Tournament to Compare",
            options=dataset.get_tournament_names(tournaments_df),
            key="tournament_compare_select",
        )

    if tournament2 == tournament1:
        display_info_box("Please select a different tournament to compare", "warning")
        return

    tournament_data1 = tournaments_df[tournaments_df["name"] == tournament1]
    tournament_data2 = tournaments_df[tournaments_df["name"] == tournament2]

    st.header(f"🏆 {tournament1} vs {tournament2}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"📍 {tournament1}")
        display_metric_card("Surface", tournament_data1["surface"].values[0])
        display_metric_card("Best Of", tournament_data1["best_of"].values[0])
        display_metric_card(
            "Avg Match Duration",
            f"{round(tournament_data1['minutes'].values[0], 1)} min",
        )
        display_metric_card(
            "Total Matches", tournament_data1["total_matches"].values[0]
        )
        display_metric_card("Month Played", tournament_data1["t_month"].values[0])

    with col2:
        st.subheader(f"📍 {tournament2}")
        display_metric_card("Surface", tournament_data2["surface"].values[0])
        display_metric_card("Best Of", tournament_data2["best_of"].values[0])
        display_metric_card(
            "Avg Match Duration",
            f"{round(tournament_data2['minutes'].values[0], 1)} min",
        )
        display_metric_card(
            "Total Matches", tournament_data2["total_matches"].values[0]
        )
        display_metric_card("Month Played", tournament_data2["t_month"].values[0])

    # Yearly comparison
    st.divider()
    st.subheader("📈 Matches Over Time Comparison")

    t1_yearly = (
        match_data[match_data["t_name"] == tournament1]
        .groupby("t_year")
        .size()
        .reset_index(name="total_matches")
    )
    t1_yearly["tournament"] = tournament1

    t2_yearly = (
        match_data[match_data["t_name"] == tournament2]
        .groupby("t_year")
        .size()
        .reset_index(name="total_matches")
    )
    t2_yearly["tournament"] = tournament2

    comparison_yearly = pd.concat([t1_yearly, t2_yearly], ignore_index=True)

    fig_comparison = px.line(
        comparison_yearly,
        x="t_year",
        y="total_matches",
        color="tournament",
        title="Total Matches Over Time",
        markers=True,
    )
    st.plotly_chart(fig_comparison, width="stretch")


# Import plots module for surface distribution
from src import plots
