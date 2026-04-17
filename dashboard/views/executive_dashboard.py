"""
Executive Dashboard - High-level insights and KPIs.
Provides overview of key metrics and trends for stakeholders.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src import features, utils, plots
from dashboard import cache
from dashboard.components import (
    display_styled_metric,
    display_metric_card,
    display_section_header,
    display_info_box,
    create_section_selector,
)


def show():
    """Display the Executive Dashboard."""

    # Get data from session state
    match_data = st.session_state.data["matches"]
    players_df = st.session_state.data["players"]

    st.header("Executive Dashboard")
    
    # ===== CONTROL CARD =====
    with st.container(border=True):
        min_year = int(match_data["t_year"].min())
        max_year = int(match_data["t_year"].max())
        
        year_range = st.slider(
            "Year range",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            step=1,
            label_visibility="collapsed",
        )
    
    st.divider()
    
    # Filter matches by year range
    data_version = st.session_state.data.get("data_version")
    filtered_matches = cache.filter_matches_by_year(
        match_data,
        start_year=year_range[0],
        end_year=year_range[1],
        data_version=data_version,
    )

    # ===== KEY METRICS ROW =====
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    data_version = st.session_state.data.get("data_version")
    metrics = cache.executive_metrics(filtered_matches, players_df, data_version=data_version)
    
    with col1:
        display_styled_metric(
            "Total Matches",
            f"{metrics['total_matches']:,}",
            "📊"
        )
    
    with col2:
        display_styled_metric(
            "Active Players",
            f"{metrics['unique_players']:,}",
            "🏆"
        )
    
    with col3:
        display_styled_metric(
            "Tournaments",
            f"{metrics['unique_tournaments']:,}",
            "🎾"
        )
    
    with col4:
        display_styled_metric(
            "Years Covered",
            f"{metrics['years_covered']}",
            "📅"
        )

    st.divider()

    # ===== TOP PERFORMERS SECTION =====
    display_section_header("Top Performers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Overall Rankings")
        top_players = cache.top_players(filtered_matches, limit=10, min_matches=20, data_version=data_version)
        
        if not top_players.empty:
            # Format for display
            display_data = top_players.copy()
            display_data["rank"] = display_data["rank"].astype(int)
            display_data["wlr"] = (display_data["wlr"] * 100).round(1).astype(str) + "%"
            display_data = display_data.rename({
                "player": "Player",
                "wins": "Wins",
                "losses": "Losses",
                "total_matches": "Matches",
                "wlr": "Win Rate",
                "rank": "Rank"
            }, axis=1)
            
            st.dataframe(
                display_data[["Rank", "Player", "Wins", "Losses", "Matches", "Win Rate"]],
                hide_index=True,
                width="stretch"
            )
        else:
            st.info("No ranking data available for selected period.")
    
    with col2:
        st.subheader("Surface Specialists")
        surface_rankings = cache.surface_rankings(filtered_matches, min_matches=10, data_version=data_version)
        
        if not surface_rankings.empty:
            # Get top 3 for each surface
            top_surface_players = (
                surface_rankings
                .groupby("surface")
                .head(3)
                .copy()
            )
            top_surface_players["rank"] = top_surface_players["rank"].astype(int)
            top_surface_players["wlr"] = (top_surface_players["wlr"] * 100).round(1).astype(str) + "%"
            
            display_cols = ["rank", "player", "surface", "total_matches", "wlr"]
            st.dataframe(
                top_surface_players[display_cols].rename({
                    "rank": "Rank",
                    "player": "Player",
                    "surface": "Surface",
                    "total_matches": "Matches",
                    "wlr": "Win Rate"
                }, axis=1),
                hide_index=True,
                width="stretch"
            )
        else:
            st.info("No surface specialist data available.")

    st.divider()

    # ===== DATA DISTRIBUTION SECTION =====
    display_section_header("📊 Match Distribution", icon="📊")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("By Surface")
        surface_counts = filtered_matches["surface"].value_counts()
        
        if not surface_counts.empty:
            fig = px.pie(
                values=surface_counts.values,
                names=surface_counts.index,
                hole=0.3,
                title="Match Distribution by Surface"
            )
            fig.update_layout(height=400)
            plots.apply_chart_theme(fig)
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No surface data available.")
    
    with col2:
        st.subheader("By Tournament Level")
        level_counts = filtered_matches["t_level"].value_counts()
        
        if not level_counts.empty:
            level_labels = [utils.format_dimension_value("t_level", value) for value in level_counts.index]
            fig = px.pie(
                values=level_counts.values,
                names=level_labels,
                hole=0.3,
                title="Match Distribution by Tournament Level"
            )
            fig.update_layout(height=400)
            plots.apply_chart_theme(fig)
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No tournament level data available.")

    st.divider()

    # ===== TRENDS SECTION =====
    display_section_header("📈 Yearly Trends", icon="📈")
    
    # Match volume trend
    yearly_trend = cache.yearly_match_trend(filtered_matches, data_version=data_version)
    
    if not yearly_trend.empty:
        fig = px.bar(
            yearly_trend,
            x="t_year",
            y="match_count",
            title="Match Count by Year",
            labels={"t_year": "Year", "match_count": "Number of Matches"},
            color="match_count",
            color_continuous_scale=["#d9b15f", "#c96b3b", "#17352b"]
        )
        fig.update_layout(height=400)
        plots.apply_chart_theme(fig, "t_year", "match_count")
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No trend data available.")

    st.divider()

    # ===== RANKINGS BY CATEGORY =====
    display_section_header("🎖️ Category Rankings", icon="🎖️")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("By Tournament Level")
        
        # Tournament level rankings
        level_rankings = cache.level_rankings(
            filtered_matches, 
            min_matches=10,
            data_version=data_version,
        )
        
        if not level_rankings.empty:
            unique_levels = level_rankings["t_level"].unique()
            selected_level = st.selectbox(
                "Tournament Level",
                options=sorted(unique_levels),
                format_func=lambda level: utils.format_dimension_value("t_level", level),
                key="exec_level_select",
            )
            level_data = level_rankings[level_rankings["t_level"] == selected_level].head(10).copy()
            level_data["rank"] = level_data["rank"].astype(int)
            level_data["wlr"] = (level_data["wlr"] * 100).round(1).astype(str) + "%"

            st.dataframe(
                level_data[["rank", "player", "total_matches", "wlr"]].rename({
                    "rank": "Rank",
                    "player": "Player",
                    "total_matches": "Matches",
                    "wlr": "Win Rate"
                }, axis=1),
                hide_index=True,
                width="stretch"
            )
        else:
            st.info("No tournament level ranking data available.")
    
    with col2:
        st.subheader("By Surface")
        
        # Surface rankings
        surface_rankings = cache.surface_rankings(
            filtered_matches,
            min_matches=10,
            data_version=data_version,
        )
        
        if not surface_rankings.empty:
            unique_surfaces = surface_rankings["surface"].unique()
            selected_surface = st.selectbox(
                "Surface",
                options=sorted(unique_surfaces),
                key="exec_surface_select",
            )
            surface_data = surface_rankings[surface_rankings["surface"] == selected_surface].head(10).copy()
            surface_data["rank"] = surface_data["rank"].astype(int)
            surface_data["wlr"] = (surface_data["wlr"] * 100).round(1).astype(str) + "%"

            st.dataframe(
                surface_data[["rank", "player", "total_matches", "wlr"]].rename({
                    "rank": "Rank",
                    "player": "Player",
                    "total_matches": "Matches",
                    "wlr": "Win Rate"
                }, axis=1),
                hide_index=True,
                width="stretch"
            )
        else:
            st.info("No surface ranking data available.")

    st.divider()

    # ===== DATA QUALITY SECTION =====
    with st.expander("📋 Data Summary"):
        summary_col1, summary_col2 = st.columns(2)
        
        with summary_col1:
            st.subheader("Dataset Statistics")
            st.write(f"**Filtered Matches:** {len(filtered_matches):,}")
            st.write(f"**Unique Players:** {filtered_matches['w_name'].nunique():,}")
            st.write(f"**Unique Tournaments:** {filtered_matches['t_name'].nunique():,}")
            st.write(f"**Year Range:** {year_range[0]} - {year_range[1]}")
            st.write(f"**Avg Matches/Player:** {len(filtered_matches) / filtered_matches['w_name'].nunique():.1f}")
        
        with summary_col2:
            st.subheader("Surface Coverage")
            for surface, count in metrics["surface_distribution"].items():
                pct = (count / metrics['total_matches'] * 100) if metrics['total_matches'] > 0 else 0
                st.write(f"**{surface}:** {count:,} matches ({pct:.1f}%)")
