"""
Home Page - Fan-facing landing view showing trending stories and featured content.
This is the first thing fans see when they open the app.
"""

import streamlit as st
import pandas as pd
from src import fan_insights, dataset, features
from dashboard import cache


def show():
    """Display the Home page with trending stories and featured insights."""
    
    # Get data from session state
    match_data = st.session_state.data["matches"]
    players_df = st.session_state.data["players"]
    
    # ===== INTRO SECTION =====
    st.markdown(
        """
        ### Welcome
        
        This analysis examines professional tennis through performance metrics—who wins on clay, who peaks under pressure, 
        which rivalries are truly one-sided. The data below highlights notable patterns and trends across players and tournaments.
        
        Use the navigation to explore individual player profiles, head-to-head records, tournament trends, or macro patterns across the dataset.
        """
    )
    
    st.divider()
    
    # ===== TRENDING PLAYERS SECTION =====
    st.markdown("### Current Performance Leaders")
    st.markdown("Players with strong recent form and notable win streaks.")
    
    trending_players = fan_insights.get_trending_players(match_data, players_df, top_n=5)
    
    if trending_players:
        cols = st.columns(min(3, len(trending_players)))
        for idx, (player_name, story) in enumerate(trending_players[:3]):
            with cols[idx]:
                # Get player story for more details
                player_story = fan_insights.get_player_story(player_name, match_data, players_df)
                
                st.markdown(f"**{player_name}**")
                st.markdown(f"_{player_story['headline']}_")
                st.markdown(player_story['recent_form'], help="Recent performance trajectory")
                if player_story['specialty']:
                    st.markdown(f"**Strength:** {player_story['specialty']}")
                
                if st.button(f"View Profile", key=f"home_player_{player_name}"):
                    st.session_state.page = "player"
                    st.session_state.player_select = player_name
                    st.rerun()
    else:
        st.info("Loading player data...")
    
    st.divider()
    
    # ===== FEATURED MATCHUP SECTION =====
    st.markdown("### Notable Head-to-Head Records")
    st.markdown("Rivalries with asymmetrical results or interesting patterns.")
    
    matchups = fan_insights.get_interesting_matchups(match_data, top_n=3)
    
    if matchups:
        cols = st.columns(len(matchups[:3]))
        for idx, (p1, p2, story) in enumerate(matchups[:3]):
            with cols[idx]:
                h2h_info = fan_insights.get_h2h_story(p1, p2, match_data)
                
                st.markdown(f"**{p1} vs {p2}**")
                st.markdown(f"_{h2h_info['headline']}_")
                st.markdown(f"Record: {h2h_info['record']} ({h2h_info['matches']} matches)")
                if h2h_info['asymmetry']:
                    st.markdown(f"**Pattern:** {h2h_info['asymmetry']}")
                
                if st.button(f"Compare", key=f"home_matchup_{p1}_{p2}"):
                    st.session_state.page = "comparative"
                    st.session_state.comp_player1 = p1
                    st.session_state.comp_player2 = p2
                    st.rerun()
    else:
        st.info("Loading matchup data...")
    
    st.divider()
    
    # ===== QUICK STATS SECTION =====
    st.markdown("### Dataset Overview")
    
    data_version = st.session_state.data.get("data_version")
    metrics = cache.executive_metrics(match_data, players_df, data_version=data_version)
    
    # Custom styled metric cards
    year_min = int(match_data["t_year"].min())
    year_max = int(match_data["t_year"].max())
    
    metric_data = [
        ("Total Matches", f"{metrics['total_matches']:,}", "📊"),
        ("Professional Players", f"{metrics['unique_players']:,}", "🏆"),
        ("Tournaments", f"{metrics['unique_tournaments']:,}", "🎾"),
        ("Years Covered", f"{year_max - year_min + 1}", "📅"),
    ]
    
    # Create styled metric cards
    cols = st.columns(4, gap="medium")
    for col, (label, value, emoji) in zip(cols, metric_data):
        with col:
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
    
    st.divider()
    
    # ===== EXPLORE SECTIONS =====
    st.markdown("### Navigate the Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            """
            **Player Analysis**  
            Examine individual player records. Surface performance, tournament-level breakdowns, 
            seasonal trends, and head-to-head comparisons.
            """
        )
        if st.button("Player Analysis", key="nav_player_analysis"):
            st.session_state.page = "player"
            st.rerun()
    
    with col2:
        st.markdown(
            """
            **Comparative Analysis**  
            Side-by-side player comparison across all dimensions—win rates, surfaces, 
            tournament types, and recent form.
            """
        )
        if st.button("Comparative Analysis", key="nav_comparative"):
            st.session_state.page = "comparative"
            st.rerun()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            """
            **Tournament Analysis**  
            Track performance by tournament. Explore which players dominate specific events 
            and how results have evolved over time.
            """
        )
        if st.button("Tournament Analysis", key="nav_tournaments"):
            st.session_state.page = "tournament"
            st.rerun()
    
    with col2:
        st.markdown(
            """
            **Trend Analysis**  
            Examine macro patterns. Surface distribution, match volume trends, 
            and how aggregate player performance evolves across seasons.
            """
        )
        if st.button("Trend Analysis", key="nav_trends"):
            st.session_state.page = "trend"
            st.rerun()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            """
            **Executive Dashboard**  
            High-level overview of the dataset. Top performers by surface, tournament-level breakdowns, 
            and key metrics.
            """
        )
        if st.button("Executive Dashboard", key="nav_executive"):
            st.session_state.page = "executive"
            st.rerun()
    
    # ===== METHODOLOGY SECTION =====
    st.divider()
    st.markdown("### About This Analysis")
    
    with st.expander("Data & Methodology"):
        st.markdown(
            """
            **Data Sources**
            - Professional tennis match records (ATP/WTA)
            - Player statistics and career performance
            - Tournament metadata and results
            
            **Approach**
            This analysis focuses on descriptive statistics and pattern identification. 
            Key metrics include:
            - **Win rates** by surface, tournament level, and opponent strength
            - **Streaks** and seasonal performance trends
            - **Head-to-head records** with surface and context breakdowns
            - **Career trajectories** and ranking correlation
            
            **Scope & Limitations**
            - Analysis is limited to players with a minimum match threshold (threshold filters out outliers)
            - Surface classifications may vary by tournament
            - Recent data reflects most recent records in the dataset
            - No predictive modeling—purely historical analysis
            """
        )
