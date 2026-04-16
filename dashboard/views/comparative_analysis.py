"""
Comparative Analysis page - Comprehensive player comparisons and analysis.
Displays head-to-head records, player rankings, momentum analysis, and performance metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

from src import features, dataset, utils, insights, export, plots
from dashboard import cache
from dashboard.components import display_section_header, display_info_box, create_section_selector


def _match_date_column(df: pd.DataFrame) -> str | None:
    """Return the preferred match date column if one is available."""
    for col in ("t_date", "date", "t_year"):
        if col in df.columns:
            return col
    return None


def _matches_column(df: pd.DataFrame) -> str | None:
    """Return the available total-match count column for ranking tables."""
    for col in ("matches", "total_matches"):
        if col in df.columns:
            return col
    return None


def show():
    """Display the Comparative Analysis page."""

    # Get data from session state
    match_data = st.session_state.data["matches"]
    players_df = st.session_state.data["players"]

    st.header("⚖️ Comparative Analysis")
    st.divider()

    # Sidebar player selection for comparisons
    with st.sidebar:
        player_names = dataset.get_player_names(players_df)
        featured_players = utils.get_featured_players(players_df, st.session_state.data["yearly_performance"], count=3)
        default_player1 = featured_players[0] if featured_players else player_names[0]
        st.subheader("👥 Analysis Setup")
        
        player1 = st.selectbox(
            "First Player",
            options=player_names,
            index=player_names.index(default_player1) if default_player1 in player_names else 0,
            key="comp_player1"
        )
        
        comparison_defaults = utils.get_featured_players(
            players_df,
            st.session_state.data["yearly_performance"],
            count=3,
            exclude=[player1],
        )
        default_player2 = comparison_defaults[0] if comparison_defaults else next(
            (name for name in player_names if name != player1),
            player_names[0],
        )
        player2 = st.selectbox(
            "Second Player",
            options=player_names,
            index=player_names.index(default_player2) if default_player2 in player_names else 0,
            key="comp_player2"
        )

    # ===== EXPORT BUTTONS =====
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📥 Comparison CSV", key="export_csv_comp"):
            csv_data = export.generate_comparison_report_csv(match_data, [player1, player2])
            st.download_button(
                label="Download CSV Report",
                data=csv_data,
                file_name=f"{player1}_vs_{player2}_comparison.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("🎯 H2H CSV", key="export_h2h_csv"):
            csv_data = export.generate_matchup_summary_csv(match_data, player1, player2)
            st.download_button(
                label="Download H2H CSV",
                data=csv_data,
                file_name=f"{player1}_vs_{player2}_h2h.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("📄 H2H PDF", key="export_h2h_pdf"):
            pdf_data = export.generate_h2h_report_pdf(match_data, player1, player2)
            st.download_button(
                label="Download H2H PDF",
                data=pdf_data,
                file_name=f"{player1}_vs_{player2}_h2h.pdf",
                mime="application/pdf"
            )
    
    with col4:
        narrative = insights.generate_matchup_narrative(match_data, player1, player2)
        st.write(f"💬 {narrative}")

    # Render only the active section to avoid building every chart/table at once.
    active_section = create_section_selector("Comparative Section", [
        "🎯 Head-to-Head",
        "⚡ Player Momentum",
        "📊 Rankings by Surface",
        "🏆 Rankings by Level",
        "📈 Performance Trends",
        "🔮 Match Prediction"
    ], key="comparative_section")

    # ===== HEAD-TO-HEAD TAB =====
    if active_section == "🎯 Head-to-Head":
        display_section_header("Head-to-Head Analysis", icon="🎯")
        
        if player1 == player2:
            st.warning("⚠️ Please select two different players for head-to-head comparison.")
        else:
            # Get head-to-head data
            h2h_matches = features.get_head_to_head(match_data, player1, player2)
            h2h_record = features.calculate_player_h2h_record(match_data, player1, player2)
            
            if len(h2h_matches) == 0:
                st.info(f"ℹ️ No head-to-head matches found between {player1} and {player2}")
            else:
                # Display metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    player1_wins = len(h2h_matches[h2h_matches["w_name"] == player1])
                    st.metric(f"{player1} Wins", player1_wins)
                
                with col2:
                    player2_wins = len(h2h_matches[h2h_matches["w_name"] == player2])
                    st.metric(f"{player2} Wins", player2_wins)
                
                with col3:
                    st.metric("Total Meetings", len(h2h_matches))
                
                st.divider()
                
                # Surface breakdown
                st.subheader("Performance by Surface")
                
                surface_stats = []
                for surface in h2h_matches["surface"].unique():
                    if pd.notna(surface):
                        surf_matches = h2h_matches[h2h_matches["surface"] == surface]
                        p1_wins = len(surf_matches[surf_matches["w_name"] == player1])
                        p2_wins = len(surf_matches[surf_matches["w_name"] == player2])
                        
                        surface_stats.append({
                            "Surface": surface.title(),
                            f"{player1} Wins": p1_wins,
                            f"{player2} Wins": p2_wins,
                            "Total": len(surf_matches)
                        })
                
                if surface_stats:
                    surf_df = pd.DataFrame(surface_stats)
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.dataframe(surf_df, hide_index=True, width="stretch")
                    
                    with col2:
                        # Stacked bar chart
                        fig = go.Figure(data=[
                            go.Bar(name=player1, x=surf_df["Surface"], y=surf_df[f"{player1} Wins"]),
                            go.Bar(name=player2, x=surf_df["Surface"], y=surf_df[f"{player2} Wins"])
                        ])
                        fig.update_layout(
                            barmode="stack",
                            title="H2H Record by Surface",
                            xaxis_title="Surface",
                            yaxis_title="Wins",
                            hovermode="x unified"
                        )
                        plots.apply_chart_theme(fig, "surface", "win")
                        st.plotly_chart(fig, width="stretch", key=f"comp_h2h_surface_{player1}_{player2}")
                
                st.divider()
                
                # Recent matches
                st.subheader("Recent Meetings")
                
                display_matches = []
                # Sort by date if available, otherwise by year
                match_date_col = _match_date_column(h2h_matches)
                if match_date_col and pd.notna(h2h_matches[match_date_col]).any():
                    sorted_matches = h2h_matches.sort_values(match_date_col, ascending=False)
                else:
                    sorted_matches = h2h_matches.sort_index(ascending=False)
                
                for _, match in sorted_matches.head(10).iterrows():
                    winner = match["w_name"]
                    time_period = f"{match['t_date']}" if 't_date' in match and pd.notna(match.get('t_date')) else f"{match.get('t_year', 'N/A')}"
                    
                    display_matches.append({
                        "Date": time_period,
                        "Winner": winner,
                        "Tournament": match.get("t_name", "N/A"),
                        "Level": match.get("t_level", "N/A"),
                        "Surface": match.get("surface", "N/A")
                    })
                
                if display_matches:
                    st.dataframe(pd.DataFrame(display_matches), hide_index=True, width="stretch")

    # ===== PLAYER MOMENTUM TAB =====
    elif active_section == "⚡ Player Momentum":
        display_section_header("Current Momentum & Form", icon="⚡")
        
        # Analyze both players
        col1, col2 = st.columns(2)
        
        for col, player in zip([col1, col2], [player1, player2]):
            with col:
                st.subheader(f"{player}")
                
                player_matches = match_data[
                    (match_data["w_name"] == player) | (match_data["l_name"] == player)
                ].copy()
                
                player_matches["result"] = (player_matches["w_name"] == player).astype(int)
                
                # Sort by date (handle missing t_date gracefully)
                match_date_col = _match_date_column(player_matches)
                if match_date_col and pd.notna(player_matches[match_date_col]).any():
                    player_matches = player_matches.sort_values(match_date_col, ascending=False)
                else:
                    player_matches = player_matches.sort_index(ascending=False)
                
                # Calculate streaks
                streaks = utils.calculate_streaks(player_matches)
                
                # Get last 10 matches
                recent_10 = player_matches.head(10)
                recent_wins = recent_10["result"].sum() if len(recent_10) > 0 else 0
                recent_total = len(recent_10)
                
                st.metric(
                    "Last 10 Matches",
                    f"{recent_wins}/{recent_total}",
                    delta=f"{(recent_wins/recent_total*100):.0f}% WR" if recent_total > 0 else "N/A"
                )
                
                # Get last 5 matches
                recent_5 = player_matches.head(5)
                recent_5_wins = recent_5["result"].sum() if len(recent_5) > 0 else 0
                
                st.metric(
                    "Last 5 Matches",
                    f"{recent_5_wins}/5",
                    delta=f"{(recent_5_wins/5*100):.0f}% WR" if len(recent_5) > 0 else "N/A"
                )
                
                # Current streak
                if streaks:
                    current_streak_length = streaks.get("current_streak_length", 0)
                    streak_type = "W" if streaks.get("current_streak_type") == "Winning" else "L"
                    st.metric(
                        "Current Streak",
                        f"{abs(current_streak_length)}{streak_type}",
                        delta=f"Best: {streaks.get('longest_win_streak', 0)}W"
                    )

    # ===== RANKINGS BY SURFACE TAB =====
    elif active_section == "📊 Rankings by Surface":
        display_section_header("Player Rankings by Surface", icon="🏖️")
        
        data_version = st.session_state.data.get("data_version")
        surface_rankings = cache.surface_rankings(match_data, min_matches=10, data_version=data_version)
        
        if not surface_rankings.empty:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                selected_surface = st.selectbox(
                    "Select Surface",
                    options=sorted(surface_rankings["surface"].unique()),
                    key="surface_rank_select"
                )
            
            with col2:
                st.empty()  # Spacing
            
            # Filter for selected surface
            surface_data = surface_rankings[surface_rankings["surface"] == selected_surface].head(20)
            
            if not surface_data.empty:
                # Display table
                matches_col = _matches_column(surface_data)
                display_cols = ["rank", "player", "wlr"]
                if matches_col:
                    display_cols.append(matches_col)

                display_df = surface_data[display_cols].copy()
                if matches_col:
                    display_df.columns = ["Rank", "Player", "Win Rate", "Matches"]
                else:
                    display_df.columns = ["Rank", "Player", "Win Rate"]
                    display_df["Matches"] = "N/A"
                display_df["Win Rate"] = (display_df["Win Rate"] * 100).round(1).astype(str) + "%"
                display_df = display_df.reset_index(drop=True)
                
                st.dataframe(display_df, hide_index=True, width="stretch")
                
                # Chart
                fig = px.bar(
                    surface_data.head(15),
                    x="player",
                    y="wlr",
                    title=f"Best Players on {selected_surface.title()}",
                    labels={"player": "Player", "wlr": "Win %"},
                    color="wlr",
                    color_continuous_scale=["#d9b15f", "#c96b3b", "#17352b"]
                )
                plots.apply_chart_theme(fig, "player", "wlr")
                st.plotly_chart(fig, width="stretch", key=f"comp_surface_rankings_{selected_surface}")
            else:
                st.info(f"No data available for {selected_surface} surface")
        else:
            st.info("Insufficient data to calculate surface rankings")

    # ===== RANKINGS BY LEVEL TAB =====
    elif active_section == "🏆 Rankings by Level":
        display_section_header("Player Rankings by Tournament Level", icon="🏆")
        
        level_rankings = cache.level_rankings(match_data, min_matches=10, data_version=data_version)
        
        if not level_rankings.empty:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                selected_level = st.selectbox(
                    "Select Level",
                    options=sorted(level_rankings["t_level"].unique()),
                    key="level_rank_select"
                )
            
            with col2:
                st.empty()  # Spacing
            
            # Filter for selected level
            level_data = level_rankings[level_rankings["t_level"] == selected_level].head(20)
            
            if not level_data.empty:
                # Display table
                matches_col = _matches_column(level_data)
                display_cols = ["rank", "player", "wlr"]
                if matches_col:
                    display_cols.append(matches_col)

                display_df = level_data[display_cols].copy()
                if matches_col:
                    display_df.columns = ["Rank", "Player", "Win Rate", "Matches"]
                else:
                    display_df.columns = ["Rank", "Player", "Win Rate"]
                    display_df["Matches"] = "N/A"
                display_df["Win Rate"] = (display_df["Win Rate"] * 100).round(1).astype(str) + "%"
                display_df = display_df.reset_index(drop=True)
                
                st.dataframe(display_df, hide_index=True, width="stretch")
                
                # Chart
                fig = px.bar(
                    level_data.head(15),
                    x="player",
                    y="wlr",
                    title=f"Best Players in {utils.format_dimension_value('t_level', selected_level)}",
                    labels={"player": "Player", "wlr": "Win %"},
                    color="wlr",
                    color_continuous_scale=["#d9b15f", "#c96b3b", "#17352b"]
                )
                plots.apply_chart_theme(fig, "player", "wlr")
                st.plotly_chart(fig, width="stretch", key=f"comp_level_rankings_{selected_level}")
            else:
                st.info(f"No data available for {selected_level} level")
        else:
            st.info("Insufficient data to calculate level rankings")

    # ===== PERFORMANCE TRENDS TAB =====
    elif active_section == "📈 Performance Trends":
        display_section_header("Individual Performance Trends", icon="📈")
        
        col1, col2 = st.columns(2)
        
        for col, player in zip([col1, col2], [player1, player2]):
            with col:
                st.subheader(f"{player} Trends")
                
                player_perf = st.session_state.data["yearly_performance"]
                player_perf_data = player_perf[player_perf["player"] == player]
                
                if not player_perf_data.empty:
                    fig = px.line(
                        player_perf_data,
                        x="t_year",
                        y="wlr",
                        title=f"{player} Win Rate by Season",
                        markers=True,
                        labels={"wlr": "Win %", "t_year": "Year"}
                    )
                    plots.apply_chart_theme(fig, "t_year", "wlr")
                    st.plotly_chart(fig, width="stretch", key=f"comp_player_trends_{player}")
                else:
                    st.info(f"No yearly data for {player}")

    # ===== MATCH PREDICTION TAB =====
    elif active_section == "🔮 Match Prediction":
        display_section_header("Head-to-Head Match Prediction", icon="🔮")
        
        if player1 == player2:
            st.warning("⚠️ Please select two different players for match prediction.")
        else:
            st.markdown("""
            **Prediction Model:**
            This model uses historical data to estimate match outcome probability:
            - 40% Overall win rates (all-time performance)
            - 40% Conditional performance (e.g., specific surface/level)
            - 20% Head-to-head history
            """)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Surface-Specific Prediction")
                surfaces = ["Overall"] + sorted([s for s in match_data["surface"].unique() if pd.notna(s)])
                selected_surface = st.selectbox("Select Surface", surfaces, key="pred_surface")
                
                prediction = features.predict_h2h_outcome(
                    match_data,
                    player1,
                    player2,
                    surface=None if selected_surface == "Overall" else selected_surface
                )
                
                # Display prediction
                st.markdown("---")
                
                pred_prob_p1 = prediction["player1_probability"]
                pred_prob_p2 = prediction["player2_probability"]
                
                # Visual representation
                predict_col1, predict_col2 = st.columns([1, 1])
                
                with predict_col1:
                    st.metric(
                        player1,
                        f"{pred_prob_p1:.1%}",
                        delta="Favored" if pred_prob_p1 > 0.6 else "Underdog" if pred_prob_p1 < 0.4 else "Even"
                    )
                
                with predict_col2:
                    st.metric(
                        player2,
                        f"{pred_prob_p2:.1%}",
                        delta="Favored" if pred_prob_p2 > 0.6 else "Underdog" if pred_prob_p2 < 0.4 else "Even"
                    )
                
                # Prediction confidence
                st.divider()
                st.subheader("Model Confidence")
                
                confidence = prediction["confidence"]
                confidence_color = "green" if confidence > 0.7 else "orange" if confidence > 0.4 else "red"
                
                st.markdown(f"""
                **Confidence Level: {prediction['prediction_confidence']}**
                
                Score: {confidence:.0%}
                
                *Higher confidence: More historical data available for prediction*
                """)
            
            with col2:
                st.subheader("Tournament Level Prediction")
                levels = ["Overall"] + sorted([l for l in match_data["t_level"].unique() if pd.notna(l)])
                selected_level = st.selectbox("Select Tournament Level", levels, key="pred_level")
                
                prediction_level = features.predict_h2h_outcome(
                    match_data,
                    player1,
                    player2,
                    tournament_level=None if selected_level == "Overall" else selected_level
                )
                
                # Display prediction
                st.markdown("---")
                
                pred_prob_p1_level = prediction_level["player1_probability"]
                pred_prob_p2_level = prediction_level["player2_probability"]
                
                # Visual representation
                predict_col1, predict_col2 = st.columns([1, 1])
                
                with predict_col1:
                    st.metric(
                        player1,
                        f"{pred_prob_p1_level:.1%}",
                        delta="Favored" if pred_prob_p1_level > 0.6 else "Underdog" if pred_prob_p1_level < 0.4 else "Even"
                    )
                
                with predict_col2:
                    st.metric(
                        player2,
                        f"{pred_prob_p2_level:.1%}",
                        delta="Favored" if pred_prob_p2_level > 0.6 else "Underdog" if pred_prob_p2_level < 0.4 else "Even"
                    )
                
                # Prediction confidence
                st.divider()
                st.subheader("Model Confidence")
                
                confidence_level = prediction_level["confidence"]
                
                st.markdown(f"""
                **Confidence Level: {prediction_level['prediction_confidence']}**
                
                Score: {confidence_level:.0%}
                """)
            
            # Head-to-head summary
            st.divider()
            st.subheader("Historical Context")
            
            h2h_record = features.calculate_player_h2h_record(match_data, player1, player2)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(f"{player1} Career WR", f"{h2h_record['win_percentage']:.1f}%")
            
            with col2:
                opp_record = features.calculate_player_h2h_record(match_data, player2, player1)
                st.metric(f"{player2} Career WR", f"{opp_record['win_percentage']:.1f}%")
            
            with col3:
                h2h_wins = h2h_record["wins"]
                h2h_total = h2h_record["total_matches"]
                st.metric("H2H Total", f"{h2h_total} meetings", delta=f"{player1}: {h2h_wins}")
            
            with col4:
                if h2h_total > 0:
                    h2h_wlr = (h2h_wins / h2h_total * 100)
                    st.metric("H2H Advantage", f"{h2h_wlr:.1f}%" if h2h_wlr >= 50 else f"{100-h2h_wlr:.1f}%", delta=player1 if h2h_wlr >= 50 else player2)
                else:
                    st.metric("H2H Record", "Never played")
