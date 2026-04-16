"""
Trend Analysis page for the Tennis Performance Dashboard.
Displays macro trends across all players and matches.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src import features, utils, plots
from dashboard import cache
from dashboard.components import display_section_header, display_info_box, create_section_selector


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
            "Winner-Loser Variable",
            options=wl_vars,
            format_func=utils.get_display_name,
            key="wl_var_select",
        )

        other_var = st.selectbox(
            "Other Variable",
            options=other_vars,
            format_func=utils.get_display_name,
            key="other_var_select",
        )

        min_year = int(match_data["t_year"].min())
        max_year = int(match_data["t_year"].max())
        year_range = st.slider(
            "Year Range",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            step=1,
            key="trend_year_range",
        )

    data_version = st.session_state.data.get("data_version")
    filtered_matches = cache.filter_matches_by_year(
        match_data, start_year=year_range[0], end_year=year_range[1], data_version=data_version
    )

    st.header("📊 Trend Analysis")
    st.caption("Track how player performance, match intensity, and surface dynamics evolve across seasons.")

    if filtered_matches.empty:
        st.warning("No match data is available for the selected trend filters.")
        return

    display_trend_summary(filtered_matches, wl_var, other_var)

    active_section = create_section_selector(
        "Trend Section",
        ["🎾 Winner vs Loser", "📈 Match Dynamics", "🏟️ Surfaces & Volume"],
        key="trend_section",
    )

    if active_section == "🎾 Winner vs Loser":
        display_winner_loser_trends(filtered_matches, wl_var)
    elif active_section == "📈 Match Dynamics":
        display_other_trends(filtered_matches, other_var)
        st.divider()
        display_top_variable_seasons(filtered_matches, wl_var, other_var)
    elif active_section == "🏟️ Surfaces & Volume":
        display_yearly_distribution(filtered_matches)
        st.divider()
        display_surface_performance_mix(filtered_matches)


def display_trend_summary(match_data: pd.DataFrame, wl_var: str, other_var: str):
    """Display high-level KPI cards for the trend page."""
    yearly_counts = match_data.groupby("t_year").size().reset_index(name="matches")
    latest_year = int(yearly_counts["t_year"].max())
    peak_row = yearly_counts.loc[yearly_counts["matches"].idxmax()]

    w_col = f"w_{wl_var}"
    l_col = f"l_{wl_var}"
    winner_edge = None
    if w_col in match_data.columns and l_col in match_data.columns:
        winner_edge = match_data[w_col].mean() - match_data[l_col].mean()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Years Analyzed", yearly_counts["t_year"].nunique())
    with col2:
        st.metric("Matches", f"{len(match_data):,}", delta=f"Latest: {latest_year}")
    with col3:
        st.metric("Peak Season", int(peak_row["t_year"]), delta=f"{int(peak_row['matches']):,} matches")
    with col4:
        if winner_edge is not None and pd.notna(winner_edge):
            st.metric("Winner Edge", f"{winner_edge:.2f}", delta=wl_var.replace("_", " ").title())
        else:
            st.metric("Tracked Variable", other_var.replace("_", " ").title())


def display_winner_loser_trends(match_data: pd.DataFrame, variable: str):
    """Display winner vs loser trends for a specific variable."""

    pretty_variable = utils.get_display_name(variable)
    st.subheader(f"🎾 {pretty_variable} - Winners vs Losers Over Time")

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

        trend_data["Winner Edge"] = (
            trend_data[f"Winners {variable}"] - trend_data[f"Losers {variable}"]
        )

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=trend_data["Year"],
            y=trend_data[f"Winners {variable}"],
            mode="lines+markers",
            name=f"Winners {pretty_variable}",
            line=dict(color="#17352b", width=3),
        ))
        fig.add_trace(go.Scatter(
            x=trend_data["Year"],
            y=trend_data[f"Losers {variable}"],
            mode="lines+markers",
            name=f"Losers {pretty_variable}",
            line=dict(color="#c96b3b", width=3),
        ))
        fig.add_trace(go.Scatter(
            x=trend_data["Year"],
            y=trend_data[f"Average {variable}"],
            mode="lines",
            name="Overall Average",
            line=dict(color="#53615b", width=2, dash="dash"),
        ))
        fig.update_layout(
            title=f"{pretty_variable} Over Time - Winners vs Losers",
            xaxis_title="Year",
            yaxis_title=pretty_variable,
            hovermode="x unified",
        )
        plots.apply_chart_theme(fig, "t_year", variable)
        st.plotly_chart(fig, width="stretch", key=f"trend_winner_loser_{variable}")

        edge_col1, edge_col2 = st.columns([1, 2])
        with edge_col1:
            st.metric(
                "Average Winner Edge",
                f"{trend_data['Winner Edge'].mean():.2f}",
                delta=f"Peak: {trend_data['Winner Edge'].max():.2f}",
            )
        with edge_col2:
            edge_fig = px.bar(
                trend_data,
                x="Year",
                y="Winner Edge",
                title=f"Winner Advantage in {pretty_variable}",
                color="Winner Edge",
                color_continuous_scale=["#c96b3b", "#d9b15f", "#17352b"],
            )
            edge_fig.update_layout(coloraxis_showscale=False)
            plots.apply_chart_theme(edge_fig, "t_year", "winner_edge")
            st.plotly_chart(edge_fig, width="stretch", key=f"trend_winner_edge_{variable}")

        # Show data table
        if st.checkbox(f"Show {variable} Trend Data", key=f"trend_data_toggle_{variable}"):
            st.dataframe(trend_data, hide_index=True, width="stretch")

    except Exception as e:
        display_info_box(f"Error processing trends: {str(e)}", "error")


def display_other_trends(match_data: pd.DataFrame, variable: str):
    """Display trends for non-player-specific variables."""

    pretty_variable = utils.get_display_name(variable)
    st.subheader(f"📈 {pretty_variable} Trend Over Time")

    try:
        if variable not in match_data.columns:
            display_info_box(f"Variable {variable} not available", "warning")
            return

        trend_data = match_data.groupby("t_year")[variable].mean().reset_index()
        trend_data.columns = ["Year", variable]
        trend_data = trend_data.sort_values("Year")

        trend_data["YoY Change"] = trend_data[variable].diff()
        fig = px.area(
            trend_data,
            x="Year",
            y=variable,
            title=f"{pretty_variable} Over Time",
            line_shape="spline",
        )
        fig.update_traces(line_color="#17352b", fillcolor="rgba(201,107,59,0.22)")
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title=f"Average {pretty_variable}",
            hovermode="x unified",
        )
        plots.apply_chart_theme(fig, "t_year", variable)
        st.plotly_chart(fig, width="stretch", key=f"trend_other_{variable}")

        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Max", f"{trend_data[variable].max():.2f}")
        with col2:
            st.metric("Min", f"{trend_data[variable].min():.2f}")
        with col3:
            st.metric("Average", f"{trend_data[variable].mean():.2f}")

        yoy = trend_data["YoY Change"].dropna()
        if not yoy.empty:
            col4, col5 = st.columns(2)
            with col4:
                st.metric("Largest Increase", f"{yoy.max():.2f}")
            with col5:
                st.metric("Largest Drop", f"{yoy.min():.2f}")

        # Show data table
        if st.checkbox(f"Show {variable} Trend Data", key=f"other_trend_toggle_{variable}"):
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

    st.plotly_chart(fig, width="stretch", key="trend_yearly_distribution")

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

    st.plotly_chart(fig_surface, width="stretch", key="trend_surface_yearly_distribution")


def display_top_variable_seasons(match_data: pd.DataFrame, wl_var: str, other_var: str):
    """Show standout seasons for the selected metrics."""
    st.subheader("🏅 Standout Seasons")

    w_col = f"w_{wl_var}"
    yearly = match_data.groupby("t_year").agg(
        matches=("t_year", "size"),
        selected_metric=(other_var, "mean"),
        winner_metric=(w_col, "mean") if w_col in match_data.columns else ("t_year", "size"),
    ).reset_index()

    if w_col not in match_data.columns:
        yearly = yearly.rename(columns={"winner_metric": "matches_fallback"})
        yearly["winner_metric"] = yearly["matches_fallback"]
        yearly = yearly.drop(columns=["matches_fallback"])

    top_selected = yearly.nlargest(5, "selected_metric")[["t_year", "selected_metric", "matches"]]
    top_selected.columns = ["Year", utils.get_display_name(other_var), "Matches"]

    top_winner = yearly.nlargest(5, "winner_metric")[["t_year", "winner_metric", "matches"]]
    top_winner.columns = ["Year", f"Winners {utils.get_display_name(wl_var)}", "Matches"]

    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(top_selected, hide_index=True, width="stretch")
    with col2:
        st.dataframe(top_winner, hide_index=True, width="stretch")


def display_surface_performance_mix(match_data: pd.DataFrame):
    """Display surface mix and leaderboards."""
    st.subheader("🎯 Surface Snapshot")

    surface_summary = (
        match_data.groupby("surface")
        .agg(
            matches=("surface", "size"),
            avg_minutes=("minutes", "mean") if "minutes" in match_data.columns else ("t_year", "size"),
            avg_best_of=("best_of", "mean") if "best_of" in match_data.columns else ("t_year", "size"),
        )
        .reset_index()
    )

    if "minutes" not in match_data.columns:
        surface_summary["avg_minutes"] = pd.NA
    if "best_of" not in match_data.columns:
        surface_summary["avg_best_of"] = pd.NA

    col1, col2 = st.columns([1.1, 1.4])

    with col1:
        st.dataframe(
            surface_summary.rename(
                columns={
                    "surface": "Surface",
                    "matches": "Matches",
                    "avg_minutes": "Avg Minutes",
                    "avg_best_of": "Avg Best Of",
                }
            ),
            hide_index=True,
            width="stretch",
        )

    with col2:
        fig = px.bar(
            surface_summary,
            x="surface",
            y="matches",
            color="matches",
            title="Match Volume by Surface",
            color_continuous_scale=["#d9b15f", "#c96b3b", "#17352b"],
        )
        fig.update_layout(
            xaxis_title="Surface",
            yaxis_title="Matches",
            coloraxis_showscale=False,
        )
        plots.apply_chart_theme(fig, "surface", "matches")
        st.plotly_chart(fig, width="stretch", key="trend_surface_volume")
