"""
Fan Insights Module - Narrative-first insight generation for sports fans.
Creates human-readable, story-focused commentary instead of raw analytics.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


def get_player_story(
    player_name: str,
    match_data: pd.DataFrame,
    players_df: pd.DataFrame,
    num_recent: int = 10,
) -> Dict[str, str]:
    """
    Generate a fan-friendly player story with key highlights.
    
    Returns a dict with:
    - headline: 1-2 sentence hook
    - recent_form: What they're doing NOW
    - specialty: What surface/level they dominate
    - milestone: Any recent achievement
    """
    
    # Get player matches
    player_matches = match_data[
        (match_data["w_name"] == player_name) | (match_data["l_name"] == player_name)
    ].copy()
    
    if len(player_matches) == 0:
        return {"headline": f"No recent data for {player_name}", "recent_form": ""}
    
    player_matches["is_win"] = player_matches["w_name"] == player_name
    
    # Sort by date if available
    if "t_date" in player_matches.columns:
        player_matches = player_matches.sort_values("t_date", ascending=False)
    elif "t_year" in player_matches.columns:
        player_matches = player_matches.sort_values("t_year", ascending=False)
    
    # Recent form (last N matches)
    recent = player_matches.head(num_recent)
    recent_wins = recent["is_win"].sum()
    recent_losses = num_recent - recent_wins
    recent_win_pct = (recent_wins / num_recent * 100) if num_recent > 0 else 0
    
    # Overall stats
    total_wins = player_matches["is_win"].sum()
    total_matches = len(player_matches)
    career_win_pct = (total_wins / total_matches * 100) if total_matches > 0 else 0
    
    # Surface specialty (if available)
    surface_story = ""
    if "surface" in player_matches.columns:
        surfaces = player_matches.groupby("surface")["is_win"].agg(
            lambda x: (x.sum() / len(x) * 100) if len(x) > 0 else 0
        )
        if len(surfaces) > 0:
            best_surface = surfaces.idxmax()
            best_surface_pct = surfaces.max()
            worst_surface = surfaces.idxmin()
            worst_surface_pct = surfaces.min()
            
            if best_surface_pct - worst_surface_pct > 15:  # Significant difference
                surface_story = f"Absolutely owns {best_surface} courts ({best_surface_pct:.0f}% win rate) but struggles on {worst_surface} ({worst_surface_pct:.0f}%)."
            elif best_surface_pct > 60:
                surface_story = f"Dominant on {best_surface} courts with {best_surface_pct:.0f}% win rate."
    
    # Generate headline
    if recent_wins >= num_recent - 2:  # 8+ wins in last 10
        headline = f"🔥 {player_name} is on FIRE"
    elif recent_win_pct > career_win_pct + 10:  # Recently improved
        headline = f"📈 {player_name} is trending UP"
    elif recent_win_pct < career_win_pct - 10:  # Recently declining
        headline = f"📉 {player_name} hitting a rough patch"
    else:
        headline = f"🎾 {player_name} playing steady tennis"
    
    # Recent form description
    if recent_wins == num_recent:
        recent_form = f"Perfect streak: {recent_wins} wins in a row"
    elif recent_wins == 0:
        recent_form = f"Struggling: 0 wins in last {num_recent} matches"
    else:
        recent_form = f"{recent_wins} wins in last {num_recent} matches ({recent_win_pct:.0f}% win rate)"
    
    return {
        "headline": headline,
        "recent_form": recent_form,
        "specialty": surface_story,
        "career_record": f"{total_wins}W-{total_matches - total_wins}L ({career_win_pct:.0f}%)",
        "total_matches": total_matches,
    }


def get_h2h_story(
    player1: str,
    player2: str,
    match_data: pd.DataFrame,
) -> Dict[str, str]:
    """
    Generate fan-friendly head-to-head narrative highlighting interesting asymmetries.
    
    Returns:
    - headline: Who's winning overall?
    - asymmetry: Any surface/context where one player dominates
    - record: Simple "12-8" format
    """
    
    # Get H2H matches
    h2h = match_data[
        ((match_data["w_name"] == player1) & (match_data["l_name"] == player2))
        | ((match_data["w_name"] == player2) & (match_data["l_name"] == player1))
    ].copy()
    
    if len(h2h) == 0:
        return {"headline": f"No head-to-head record", "record": "0-0"}
    
    # Overall record
    p1_wins = (h2h["w_name"] == player1).sum()
    p2_wins = (h2h["w_name"] == player2).sum()
    total = len(h2h)
    
    # Generate headline
    if p1_wins > p2_wins * 1.5:  # Clear domination
        headline = f"🥊 {player1} OWNS this matchup ({p1_wins}-{p2_wins})"
    elif p2_wins > p1_wins * 1.5:
        headline = f"🥊 {player2} OWNS this matchup ({p2_wins}-{p1_wins})"
    elif abs(p1_wins - p2_wins) <= 1:
        headline = f"⚖️ Dead even matchup ({p1_wins}-{p2_wins})"
    else:
        headline = f"⚖️ {player1} leads ({p1_wins}-{p2_wins})"
    
    # Look for surface asymmetry
    asymmetry_story = ""
    if "surface" in h2h.columns:
        for surface in h2h["surface"].unique():
            surface_h2h = h2h[h2h["surface"] == surface]
            if len(surface_h2h) >= 2:  # At least 2 matches
                p1_surface_wins = (surface_h2h["w_name"] == player1).sum()
                p2_surface_wins = (surface_h2h["w_name"] == player2).sum()
                
                if p1_surface_wins >= p2_surface_wins * 2 or p2_surface_wins >= p1_surface_wins * 2:
                    winner = player1 if p1_surface_wins > p2_surface_wins else player2
                    pct = max(p1_surface_wins, p2_surface_wins) / len(surface_h2h) * 100
                    asymmetry_story = f"**But on {surface} courts**: {winner} is untouchable ({pct:.0f}% win rate in this matchup)"
                    break
    
    return {
        "headline": headline,
        "record": f"{p1_wins}-{p2_wins}",
        "asymmetry": asymmetry_story,
        "matches": len(h2h),
    }


def get_trending_players(
    match_data: pd.DataFrame,
    players_df: pd.DataFrame,
    top_n: int = 5,
) -> List[Tuple[str, str]]:
    """
    Get trending players (improving recently) with their story hooks.
    
    Returns list of (player_name, story_headline) tuples
    """
    
    if "t_year" not in match_data.columns:
        return []
    
    current_year = match_data["t_year"].max()
    prev_year = current_year - 1
    
    trending = []
    
    for player in match_data["w_name"].unique():
        current_matches = match_data[
            (match_data["t_year"] == current_year)
            & ((match_data["w_name"] == player) | (match_data["l_name"] == player))
        ]
        prev_matches = match_data[
            (match_data["t_year"] == prev_year)
            & ((match_data["w_name"] == player) | (match_data["l_name"] == player))
        ]
        
        if len(current_matches) >= 5 and len(prev_matches) >= 5:
            current_wr = (current_matches["w_name"] == player).sum() / len(current_matches)
            prev_wr = (prev_matches["w_name"] == player).sum() / len(prev_matches)
            
            improvement = (current_wr - prev_wr) * 100
            
            if improvement > 10:  # Significant improvement
                trending.append((player, improvement, current_wr))
    
    # Sort by improvement and return top N
    trending.sort(key=lambda x: x[1], reverse=True)
    
    return [
        (name, f"📈 Up {improvement:.0f}% this year ({current_wr:.0f}% win rate)")
        for name, improvement, current_wr in trending[:top_n]
    ]


def get_interesting_matchups(
    match_data: pd.DataFrame,
    top_n: int = 3,
) -> List[Tuple[str, str, str]]:
    """
    Get interesting matchups based on surface asymmetries and competitiveness.
    
    Returns list of (player1, player2, story) tuples
    """
    
    matchups = []
    
    # Get all unique player pairs
    for p1 in match_data["w_name"].unique()[:50]:  # Limit to first 50 for performance
        h2h = match_data[
            ((match_data["w_name"] == p1) & (match_data["l_name"].isin(match_data["w_name"].unique())))
            | ((match_data["l_name"] == p1) & (match_data["w_name"].isin(match_data["w_name"].unique())))
        ]
        
        for p2 in h2h["w_name"].unique():
            if p1 == p2:
                continue
                
            # Get surface breakdown
            p1_p2_h2h = match_data[
                ((match_data["w_name"] == p1) & (match_data["l_name"] == p2))
                | ((match_data["w_name"] == p2) & (match_data["l_name"] == p1))
            ]
            
            if len(p1_p2_h2h) < 3:  # Need at least 3 matches
                continue
            
            # Check for asymmetry
            if "surface" in p1_p2_h2h.columns:
                for surface in p1_p2_h2h["surface"].unique():
                    surface_matches = p1_p2_h2h[p1_p2_h2h["surface"] == surface]
                    if len(surface_matches) >= 2:
                        p1_wins = (surface_matches["w_name"] == p1).sum()
                        if p1_wins >= len(surface_matches) * 0.75:  # Clear domination on surface
                            story = f"{p1} dominates {p2} on {surface} courts"
                            matchups.append((p1, p2, story))
                            break
    
    return matchups[:top_n]


def format_trend_emoji(value: float, threshold: float = 0.0) -> str:
    """Return emoji based on trend direction."""
    if value > threshold:
        return "🟢"
    elif value < threshold:
        return "🔴"
    else:
        return "⚪"
