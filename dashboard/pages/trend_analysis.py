"""
Trend Analysis page for the Tennis Performance Dashboard.
Displays macro trends across all players and matches.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

from src import features, utils
from dashboard.components import display_section_header, display_info_box


def show():
    """Display the Trend Analysis page."""

    # Get data from session state
    match_data = st.session_state.data["matches"]

    # Sidebar filters
    with st.sidebar:
        st.subheader("📊 Trend Filters")

        # Get available variables
        wl_vars = [
            x[2:]
            for x in match_data.columns
            if x.startswith("w_") and match_data[x].dtype in ["float64", "int64"]
        ]

        other_vars = [
            x
            for x in match_data.columns
            if not (x.startswith("w_") or x.startswith("l_"))
            and match_data[x].dtype in ["float64", "int64"]
        ]

        wl_var = st.selectbox(
            "Winner-Loser Variable", options=wl_vars, key="wl_var_select"
        )

        other_var = st.selectbox(
            "Other Variable", options=other_vars, key="other_var_select"
        )

    st.header("📊 Trend Analysis")

    # Display trend analyses
    display_winner_loser_trends(match_data, wl_var)

    st.divider()

    display_other_trends(match_data, other_var)

    st.divider()

    display_yearly_distribution(match_data)


def display_winner_loser_trends(match_data: pd.DataFrame, variable: str):
    """Display winner vs loser trends for a specific variable."""

    st.subheader(f"🎾 {variable.title()} - Winner vs Loser Over Time")

    try:
        # Prepare data
        w_col = f"w_{variable}"
        l_col = f"l_{variable}"

        if w_col not in match_data.columns or l_col not in match_data.columns:
            display_info_box(f"Variable {variable} not available", "warning")
            return

        trend_data = (
            match_data.groupby("t_year")
            .agg({w_col: "mean", l_col: "mean"})
            .reset_index()
        )

        trend_data.columns = ["Year", f"Winners {variable}", f"Losers {variable}"]

        # Calculate average
        trend_data[f"Average {variable}"] = (
            trend_data[f"Winners {variable}"] + trend_data[f"Losers {variable}"]
        ) / 2

        # Plot using matplotlib
        fig, ax = plt.subplots(figsize=(12, 7))

        sns.lineplot(
            data=trend_data,
            x="Year",
            y=f"Winners {variable}",
            marker="x",
            label=f"Winners {variable}",
            ax=ax,
            linewidth=2,
        )
        sns.lineplot(
            data=trend_data,
            x="Year",
            y=f"Losers {variable}",
            marker="o",
            label=f"Losers {variable}",
            ax=ax,
            linewidth=2,
        )
        sns.lineplot(
            data=trend_data,
            x="Year",
            y=f"Average {variable}",
            label=f"Average {variable}",
            ax=ax,
            linewidth=2,
            linestyle="--",
        )

        ax.set_title(
            f"{variable.title()} Over Time - Winners vs Losers",
            fontsize=14,
            fontweight="bold",
        )
        ax.set_xlabel("Year", fontsize=12)
        ax.set_ylabel(variable.title(), fontsize=12)
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig)

        # Show data table
        if st.checkbox(f"Show {variable} Trend Data"):
            st.dataframe(trend_data, hide_index=True, width="stretch")

    except Exception as e:
        display_info_box(f"Error processing trends: {str(e)}", "error")


def display_other_trends(match_data: pd.DataFrame, variable: str):
    """Display trends for non-player-specific variables."""

    st.subheader(f"📈 {variable.title()} Trend Over Time")

    try:
        if variable not in match_data.columns:
            display_info_box(f"Variable {variable} not available", "warning")
            return

        trend_data = match_data.groupby("t_year")[variable].mean().reset_index()
        trend_data.columns = ["Year", variable]
        trend_data = trend_data.sort_values("Year")

        # Plot using matplotlib
        fig, ax = plt.subplots(figsize=(12, 7))

        sns.lineplot(
            data=trend_data, x="Year", y=variable, marker="o", ax=ax, linewidth=2
        )

        ax.set_title(f"{variable.title()} Over Time", fontsize=14, fontweight="bold")
        ax.set_xlabel("Year", fontsize=12)
        ax.set_ylabel(f"Average {variable}", fontsize=12)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig)

        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Max", f"{trend_data[variable].max():.2f}")
        with col2:
            st.metric("Min", f"{trend_data[variable].min():.2f}")
        with col3:
            st.metric("Average", f"{trend_data[variable].mean():.2f}")

        # Show data table
        if st.checkbox(f"Show {variable} Trend Data"):
            st.dataframe(trend_data, hide_index=True, width="stretch")

    except Exception as e:
        display_info_box(f"Error processing trends: {str(e)}", "error")


def display_yearly_distribution(match_data: pd.DataFrame):
    """Display distribution of matches across years."""

    st.subheader("📅 Matches Distribution by Year")

    yearly_counts = match_data["t_year"].value_counts().sort_index().reset_index()
    yearly_counts.columns = ["Year", "Number of Matches"]

    fig = px.bar(
        yearly_counts,
        x="Year",
        y="Number of Matches",
        title="Total Matches Per Year",
        labels={"Year": "Year", "Number of Matches": "Matches"},
    )

    st.plotly_chart(fig, width="stretch")

    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Years", len(yearly_counts))
    with col2:
        st.metric("Total Matches", yearly_counts["Number of Matches"].sum())
    with col3:
        st.metric("Avg per Year", f"{yearly_counts['Number of Matches'].mean():.0f}")
    with col4:
        st.metric(
            "Peak Year",
            f"{yearly_counts.loc[yearly_counts['Number of Matches'].idxmax(), 'Year']:.0f}",
        )

    # Surface trends
    st.subheader("🏟️ Surface Distribution Over Time")

    surface_yearly = (
        match_data.groupby(["t_year", "surface"]).size().reset_index(name="matches")
    )

    fig_surface = px.bar(
        surface_yearly,
        x="t_year",
        y="matches",
        color="surface",
        title="Matches by Surface Over Time",
        labels={"t_year": "Year", "matches": "Matches", "surface": "Surface"},
    )

    st.plotly_chart(fig_surface, width="stretch")
