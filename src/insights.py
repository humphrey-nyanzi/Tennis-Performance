"""
Automated Insight Generation module for Tennis Performance Analysis.
Generates natural language summaries, achievements, and alerts.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def _get_preferred_date_column(df: pd.DataFrame) -> Optional[str]:
    """Return the best available date-like column for ordering match data."""
    for col in ("t_date", "date", "t_year"):
        if col in df.columns:
            return col
    return None


def _sort_by_available_date(df: pd.DataFrame, ascending: bool = False) -> pd.DataFrame:
    """Sort by the first available date-like column, or preserve index order."""
    date_col = _get_preferred_date_column(df)
    if date_col:
        return df.sort_values(date_col, ascending=ascending)
    return df.sort_index(ascending=ascending)


def generate_player_summary(match_data: pd.DataFrame, player: str, 
                           recent_matches: int = 10) -> str:
    """
    Generate a natural language summary of player performance.
    
    Args:
        match_data: Match DataFrame
        player: Player name
        recent_matches: Number of recent matches to analyze
        
    Returns:
        Natural language summary string
    """
    # Get player matches
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy()
    player_matches = _sort_by_available_date(player_matches, ascending=False)
    
    if len(player_matches) == 0:
        return f"No match data available for {player}."
    
    # Overall stats
    wins = (player_matches["w_name"] == player).sum()
    losses = (player_matches["l_name"] == player).sum()
    total = wins + losses
    win_pct = (wins / total * 100) if total > 0 else 0
    
    # Recent form
    recent = player_matches.head(recent_matches)
    recent_wins = (recent["w_name"] == player).sum()
    recent_matches_count = len(recent)
    
    # Build summary
    summary_parts = []
    
    # Overall performance
    if win_pct >= 70:
        summary_parts.append(f"🌟 {player} is performing exceptionally well with a {win_pct:.1f}% win rate across {total} matches.")
    elif win_pct >= 55:
        summary_parts.append(f"✅ {player} has a solid win rate of {win_pct:.1f}% ({wins}W-{losses}L).")
    elif win_pct >= 45:
        summary_parts.append(f"⚠️ {player} has been competitive with a {win_pct:.1f}% win rate.")
    else:
        summary_parts.append(f"📍 {player} has a {win_pct:.1f}% win rate across {total} matches.")
    
    # Recent form
    recent_win_pct = (recent_wins / recent_matches_count * 100) if recent_matches_count > 0 else 0
    if recent_win_pct >= 70:
        summary_parts.append(f"🔥 Recent form is excellent: {recent_wins}/{recent_matches_count} wins in last {recent_matches_count} matches.")
    elif recent_win_pct >= 50:
        summary_parts.append(f"Recent form: {recent_wins}/{recent_matches_count} wins (↑ Momentum building).")
    else:
        summary_parts.append(f"Recent form shows some struggles: {recent_wins}/{recent_matches_count} wins.")
    
    return " ".join(summary_parts)


def generate_tournament_summary(match_data: pd.DataFrame, tournament: str) -> str:
    """
    Generate a natural language summary of tournament highlights.
    
    Args:
        match_data: Match DataFrame
        tournament: Tournament name
        
    Returns:
        Natural language summary string
    """
    tournament_matches = match_data[match_data["t_name"] == tournament].copy()
    
    if len(tournament_matches) == 0:
        return f"No match data available for {tournament}."
    
    # Get tournament stats
    unique_players = pd.concat([
        tournament_matches["w_name"],
        tournament_matches["l_name"]
    ]).unique()
    
    # Find most successful player
    player_wins = tournament_matches["w_name"].value_counts()
    top_winner = player_wins.index[0] if len(player_wins) > 0 else "Unknown"
    top_wins = player_wins.iloc[0] if len(player_wins) > 0 else 0
    
    # Summary
    summary_parts = []
    summary_parts.append(f"📊 {tournament} featured {len(unique_players)} players across {len(tournament_matches)} matches.")
    
    if top_wins > 3:
        summary_parts.append(f"🏆 {top_winner} was dominant with {int(top_wins)} wins.")
    elif top_wins >= 2:
        summary_parts.append(f"⭐ {top_winner} led with {int(top_wins)} victories.")
    else:
        summary_parts.append(f"Multiple winners emerged in this event.")
    
    return " ".join(summary_parts)


def detect_achievement_badges(match_data: pd.DataFrame, player: str) -> List[Dict]:
    """
    Detect achievement badges based on player performance.
    
    Returns a list of achievement badges earned by the player.
    
    Args:
        match_data: Match DataFrame
        player: Player name
        
    Returns:
        List of dictionaries with badge name, description, and emoji
    """
    achievements = []
    
    # Get player matches
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy()
    
    if len(player_matches) == 0:
        return achievements
    
    # Badge calculations
    wins = (player_matches["w_name"] == player).sum()
    total = len(player_matches)
    win_pct = (wins / total * 100) if total > 0 else 0
    
    # Ultra Successful: 70%+ win rate
    if win_pct >= 70 and total >= 20:
        achievements.append({
            "badge": "🌟 Elite Performer",
            "description": f"Maintained 70%+ win rate across {total} matches",
            "emoji": "🌟"
        })
    
    # Consistent Winner: 60-69% over 15+ matches
    if 60 <= win_pct < 70 and total >= 15:
        achievements.append({
            "badge": "🎯 Consistent Winner",
            "description": f"{win_pct:.1f}% win rate - reliable performer",
            "emoji": "🎯"
        })
    
    # Tournament Champion: Won tournament (most wins in dataset)
    player_wins_by_tournament = player_matches[
        player_matches["w_name"] == player
    ].groupby("t_name").size()
    
    if len(player_wins_by_tournament) > 0 and player_wins_by_tournament.max() >= 3:
        achievements.append({
            "badge": "🏆 Tournament Master",
            "description": f"Won {int(player_wins_by_tournament.max())} matches in {player_wins_by_tournament.idxmax()}",
            "emoji": "🏆"
        })
    
    # Surface Specialist: 70%+ on one surface
    surfaces = player_matches["surface"].unique()
    for surface in surfaces:
        surface_matches = player_matches[player_matches["surface"] == surface]
        if len(surface_matches) >= 10:
            surface_wins = (surface_matches["w_name"] == player).sum()
            surface_wp = (surface_wins / len(surface_matches) * 100) if len(surface_matches) > 0 else 0
            if surface_wp >= 70:
                achievements.append({
                    "badge": f"🎪 {surface} Specialist",
                    "description": f"{surface_wp:.1f}% win rate on {surface} courts",
                    "emoji": "🎪"
                })
    
    # Comeback Specialist: Multiple wins after loss streaks
    player_matches_sorted = _sort_by_available_date(player_matches, ascending=False)
    win_streak = 0
    loss_streak = 0
    comebacks = 0
    max_comeback_streak = 0
    current_comeback_streak = 0
    
    for idx, match in player_matches_sorted.iterrows():
        is_win = match["w_name"] == player
        if is_win:
            win_streak += 1
            if loss_streak >= 3:
                comebacks += 1
                current_comeback_streak = win_streak
                max_comeback_streak = max(max_comeback_streak, current_comeback_streak)
            loss_streak = 0
        else:
            loss_streak += 1
            win_streak = 0
    
    if comebacks >= 2:
        achievements.append({
            "badge": "💪 Comeback Artist",
            "description": f"Recorded {comebacks} comebacks from losing streaks",
            "emoji": "💪"
        })
    
    # Rapid Rise: Recent form significantly better than career average
    recent_25 = player_matches_sorted.head(25)
    if len(recent_25) >= 10:
        recent_wins = (recent_25["w_name"] == player).sum()
        recent_wp = (recent_wins / len(recent_25) * 100) if len(recent_25) > 0 else 0
        
        if recent_wp > win_pct + 15:
            achievements.append({
                "badge": "📈 Rising Star",
                "description": f"Recent form ({recent_wp:.1f}%) exceeds career average",
                "emoji": "📈"
            })
    
    # Veteran: 100+ matches
    if total >= 100:
        achievements.append({
            "badge": "👑 Veteran",
            "description": f"Competed in {total} matches - experienced player",
            "emoji": "👑"
        })
    
    # Active Trader: Many matches in recent period
    one_year_ago = pd.to_datetime("today") - pd.Timedelta(days=365)
    recent_date_col = _get_preferred_date_column(player_matches)
    if recent_date_col in {"t_date", "date"}:
        recent_year = player_matches[pd.to_datetime(player_matches[recent_date_col]) > one_year_ago]
        if len(recent_year) >= 20:
            achievements.append({
                "badge": "⚡ Active Player",
                "description": f"{len(recent_year)} matches in the last year",
                "emoji": "⚡"
            })
    
    return achievements


def generate_trend_alert(match_data: pd.DataFrame, player: str, 
                        threshold_change: float = 15.0) -> Optional[Dict]:
    """
    Generate a trend alert if significant performance change detected.
    
    Args:
        match_data: Match DataFrame
        player: Player name
        threshold_change: Minimum % point change to trigger alert (default 15%)
        
    Returns:
        Dictionary with alert details or None if no significant change
    """
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy()
    player_matches = _sort_by_available_date(player_matches, ascending=True)
    
    if len(player_matches) < 20:
        return None  # Need sufficient data for trend detection
    
    # Split into recent and historical
    mid_point = len(player_matches) // 2
    historical = player_matches.iloc[:mid_point]
    recent = player_matches.iloc[mid_point:]
    
    # Calculate win percentages
    hist_wins = (historical["w_name"] == player).sum()
    hist_wp = (hist_wins / len(historical) * 100) if len(historical) > 0 else 0
    
    recent_wins = (recent["w_name"] == player).sum()
    recent_wp = (recent_wins / len(recent) * 100) if len(recent) > 0 else 0
    
    change = recent_wp - hist_wp
    
    if abs(change) < threshold_change:
        return None
    
    if change > 0:
        alert_type = "positive"
        alert_emoji = "🚀"
        description = f"Performance improving! Up {change:.1f} points from {hist_wp:.1f}% to {recent_wp:.1f}%"
    else:
        alert_type = "negative"
        alert_emoji = "⚠️"
        description = f"Performance declining. Down {abs(change):.1f} points from {hist_wp:.1f}% to {recent_wp:.1f}%"
    
    return {
        "alert_type": alert_type,
        "emoji": alert_emoji,
        "player": player,
        "description": description,
        "historical_wp": round(hist_wp, 1),
        "recent_wp": round(recent_wp, 1),
        "change": round(change, 1),
        "severity": "high" if abs(change) >= 25 else "medium"
    }


def generate_matchup_narrative(match_data: pd.DataFrame, player1: str, 
                               player2: str) -> str:
    """
    Generate narrative about head-to-head matchup between two players.
    
    Args:
        match_data: Match DataFrame
        player1: First player name
        player2: Second player name
        
    Returns:
        Narrative string about their matchups
    """
    # Get head-to-head matches
    h2h_matches = match_data[
        ((match_data["w_name"] == player1) & (match_data["l_name"] == player2)) |
        ((match_data["w_name"] == player2) & (match_data["l_name"] == player1))
    ]
    
    if len(h2h_matches) == 0:
        return f"No head-to-head match data available between {player1} and {player2}."
    
    # Calculate h2h record
    p1_wins = ((h2h_matches["w_name"] == player1) & (h2h_matches["l_name"] == player2)).sum()
    p2_wins = ((h2h_matches["w_name"] == player2) & (h2h_matches["l_name"] == player1)).sum()
    total = len(h2h_matches)
    
    # Generate narrative
    narrative_parts = []
    narrative_parts.append(f"📊 {player1} vs {player2}: {p1_wins}-{p2_wins} head-to-head")
    
    if p1_wins > p2_wins:
        dominance = (p1_wins / total * 100) if total > 0 else 0
        if dominance >= 70:
            narrative_parts.append(f"🏆 {player1} has dominated this matchup ({dominance:.0f}% wins)")
        elif dominance >= 60:
            narrative_parts.append(f"✅ {player1} has an edge in this rivalry")
    elif p2_wins > p1_wins:
        dominance = (p2_wins / total * 100) if total > 0 else 0
        if dominance >= 70:
            narrative_parts.append(f"🏆 {player2} has dominated ({dominance:.0f}% wins)")
        elif dominance >= 60:
            narrative_parts.append(f"✅ {player2} has an edge")
    else:
        narrative_parts.append("⚖️ This matchup is evenly balanced")
    
    # Recent form in h2h
    recent_h2h = _sort_by_available_date(h2h_matches.copy(), ascending=False).head(3)
    recent_p1_wins = ((recent_h2h["w_name"] == player1) & (recent_h2h["l_name"] == player2)).sum()
    
    if len(recent_h2h) >= 2:
        if recent_p1_wins == len(recent_h2h):
            narrative_parts.append(f"🔥 {player1} has won all recent encounters")
        elif recent_p1_wins == 0:
            narrative_parts.append(f"🔥 {player2} has won recent encounters")
    
    return " ".join(narrative_parts)


def generate_performance_card(match_data: pd.DataFrame, player: str) -> Dict:
    """
    Generate a comprehensive performance card for dashboard display.
    
    Args:
        match_data: Match DataFrame
        player: Player name
        
    Returns:
        Dictionary with card data for visualization
    """
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy()
    
    if len(player_matches) == 0:
        return {"player": player, "status": "no_data"}
    
    # Calculate metrics
    wins = (player_matches["w_name"] == player).sum()
    total = len(player_matches)
    win_pct = (wins / total * 100) if total > 0 else 0
    
    # Recent performance (last 10 matches)
    recent = _sort_by_available_date(player_matches.copy(), ascending=False).head(10)
    recent_wins = (recent["w_name"] == player).sum()
    recent_wp = (recent_wins / len(recent) * 100) if len(recent) > 0 else 0
    
    # Surface breakdown
    surface_stats = {}
    for surface in player_matches["surface"].unique():
        surf_matches = player_matches[player_matches["surface"] == surface]
        surf_wins = (surf_matches["w_name"] == player).sum()
        surf_wp = (surf_wins / len(surf_matches) * 100) if len(surf_matches) > 0 else 0
        surface_stats[surface] = {
            "matches": len(surf_matches),
            "win_percentage": round(surf_wp, 1)
        }
    
    # Status determination
    if recent_wp >= 70:
        status = "hot"
        status_emoji = "🔥"
    elif recent_wp >= 50:
        status = "good"
        status_emoji = "✅"
    elif recent_wp >= 40:
        status = "struggling"
        status_emoji = "⚠️"
    else:
        status = "cold"
        status_emoji = "❄️"
    
    return {
        "player": player,
        "overall_wp": round(win_pct, 1),
        "recent_wp": round(recent_wp, 1),
        "total_matches": total,
        "status": status,
        "status_emoji": status_emoji,
        "surface_stats": surface_stats,
        "summary": generate_player_summary(match_data, player),
        "achievements": detect_achievement_badges(match_data, player)
    }
