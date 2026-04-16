"""
Feature engineering module for Tennis Performance Analysis.
Creates advanced features and aggregates player/tournament statistics.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import logging
from scipy import stats

logger = logging.getLogger(__name__)


def create_win_loss_stats(match_data: pd.DataFrame, groupby_col: str) -> pd.DataFrame:
    """
    Create win/loss statistics grouped by a specific column.

    Args:
        match_data: Match DataFrame with 'w_name' and 'l_name' columns
        groupby_col: Column to group by (e.g., 'surface', 't_level')

    Returns:
        DataFrame with wins, losses, total matches, and win ratio
    """
    # Get wins
    w_stats = (
        match_data.groupby(["w_name", groupby_col]).size().reset_index(name="wins")
    )
    w_stats = w_stats.rename({"w_name": "name"}, axis=1)

    # Get losses
    l_stats = (
        match_data.groupby(["l_name", groupby_col]).size().reset_index(name="losses")
    )
    l_stats = l_stats.rename({"l_name": "name"}, axis=1)

    # Merge
    player_stats = pd.merge(
        w_stats,
        l_stats,
        left_on=["name", groupby_col],
        right_on=["name", groupby_col],
        how="outer",
    )

    # Fill NaNs
    player_stats[["losses", "wins"]] = player_stats[["losses", "wins"]].fillna(0)

    # Calculate totals
    player_stats["total_matches"] = player_stats["wins"] + player_stats["losses"]
    player_stats["wlr"] = (player_stats["wins"] / player_stats["total_matches"]).round(
        3
    )

    logger.info(f"Created win/loss stats grouped by {groupby_col}")
    return player_stats


def create_annual_win_loss_stats(
    match_data: pd.DataFrame, groupby_col: str
) -> pd.DataFrame:
    """
    Create annual win/loss statistics grouped by a specific column and year.

    Args:
        match_data: Match DataFrame
        groupby_col: Column to group by (e.g., 'surface', 't_level')

    Returns:
        DataFrame with annual win/loss ratios
    """
    match_data = match_data.copy()

    # Separate wins and losses
    wins = match_data[["w_name", "t_year", groupby_col]].copy()
    wins["result"] = 1
    wins.columns = ["player", "t_year", groupby_col, "win"]

    losses = match_data[["l_name", "t_year", groupby_col]].copy()
    losses["result"] = 0
    losses.columns = ["player", "t_year", groupby_col, "loss"]

    # Combine
    performance = pd.concat([wins, losses], ignore_index=True)

    # Group and aggregate
    performance_grouped = (
        performance.groupby(["player", "t_year", groupby_col])
        .agg({"win": "sum", "loss": "sum"})
        .reset_index()
    )

    # Calculate ratio
    total = performance_grouped["win"] + performance_grouped["loss"]
    performance_grouped["wlr"] = (performance_grouped["win"] / total).round(3)
    performance_grouped["total_matches"] = total

    logger.info(f"Created annual win/loss stats grouped by {groupby_col}")
    return performance_grouped


def get_head_to_head(
    match_data: pd.DataFrame, player1: str, player2: str, tournament: str = None
) -> pd.DataFrame:
    """
    Get head-to-head match history between two players.

    Args:
        match_data: Match DataFrame
        player1: First player name
        player2: Second player name
        tournament: Optional tournament filter

    Returns:
        DataFrame of matches between the two players
    """
    h2h = match_data[
        ((match_data["w_name"] == player1) & (match_data["l_name"] == player2))
        | ((match_data["w_name"] == player2) & (match_data["l_name"] == player1))
    ].copy()

    if tournament:
        h2h = h2h[h2h["t_name"] == tournament]

    # Sort by most relevant date if available
    if "t_date" in h2h.columns:
        h2h = h2h.sort_values("t_date", ascending=False)
    elif "t_year" in h2h.columns:
        h2h = h2h.sort_values("t_year", ascending=False)
    else:
        # Fall back to reverse index order if no date info available
        h2h = h2h.sort_index(ascending=False)

    logger.info(f"Head-to-head {player1} vs {player2}: {len(h2h)} matches")
    return h2h


def calculate_player_h2h_record(
    match_data: pd.DataFrame, player: str, opponent: str = None
) -> Dict:
    """
    Calculate head-to-head record for a player.

    Args:
        match_data: Match DataFrame
        player: Player name
        opponent: Optional specific opponent name

    Returns:
        Dictionary with head-to-head statistics
    """
    if opponent:
        h2h = get_head_to_head(match_data, player, opponent)
    else:
        h2h = match_data[
            (match_data["w_name"] == player) | (match_data["l_name"] == player)
        ]

    wins = len(h2h[h2h["w_name"] == player])
    losses = len(h2h[h2h["l_name"] == player])
    total = wins + losses

    return {
        "player": player,
        "opponent": opponent,
        "wins": wins,
        "losses": losses,
        "total_matches": total,
        "win_percentage": (wins / total * 100) if total > 0 else 0,
    }


def get_player_surface_stats(match_data: pd.DataFrame, player: str) -> pd.DataFrame:
    """
    Get player statistics by surface.

    Args:
        match_data: Match DataFrame
        player: Player name

    Returns:
        DataFrame with surface breakdown
    """
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy()

    player_matches["result"] = (player_matches["w_name"] == player).astype(int)

    surface_stats = (
        player_matches.groupby("surface")
        .agg({"result": ["sum", "count"]})
        .reset_index()
    )

    surface_stats.columns = ["surface", "wins", "total_matches"]
    surface_stats["losses"] = surface_stats["total_matches"] - surface_stats["wins"]
    surface_stats["wlr"] = (
        surface_stats["wins"] / surface_stats["total_matches"]
    ).round(3)

    return surface_stats.sort_values("total_matches", ascending=False)


def get_player_tournament_level_stats(
    match_data: pd.DataFrame, player: str
) -> pd.DataFrame:
    """
    Get player statistics by tournament level.

    Args:
        match_data: Match DataFrame
        player: Player name

    Returns:
        DataFrame with tournament level breakdown
    """
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy()

    player_matches["result"] = (player_matches["w_name"] == player).astype(int)

    level_stats = (
        player_matches.groupby("t_level")
        .agg({"result": ["sum", "count"]})
        .reset_index()
    )

    level_stats.columns = ["level", "wins", "total_matches"]
    level_stats["losses"] = level_stats["total_matches"] - level_stats["wins"]
    level_stats["wlr"] = (level_stats["wins"] / level_stats["total_matches"]).round(3)

    return level_stats.sort_values("total_matches", ascending=False)


def get_tournament_yearly_stats(
    match_data: pd.DataFrame, tournament: str
) -> pd.DataFrame:
    """
    Get tournament statistics by year.

    Args:
        match_data: Match DataFrame
        tournament: Tournament name

    Returns:
        DataFrame with yearly tournament data
    """
    tournament_matches = match_data[match_data["t_name"] == tournament].copy()

    yearly_stats = (
        tournament_matches.groupby("t_year")
        .agg(
            {
                "t_name": "count",  # total matches
                "surface": lambda x: x.mode()[0] if len(x.mode()) > 0 else "Unknown",
            }
        )
        .reset_index()
    )

    yearly_stats.columns = ["year", "total_matches", "surface"]

    return yearly_stats.sort_values("year", ascending=False)


def get_tournament_player_winners(
    match_data: pd.DataFrame, tournament: str, limit: int = 10
) -> pd.DataFrame:
    """
    Get players with most wins at a specific tournament.

    Args:
        match_data: Match DataFrame
        tournament: Tournament name
        limit: Number of top players to return

    Returns:
        DataFrame with top winners
    """
    tournament_matches = match_data[match_data["t_name"] == tournament]
    winners = tournament_matches["w_name"].value_counts().head(limit).reset_index()
    winners.columns = ["player", "wins"]

    return winners


def create_trend_analysis_features(match_data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Create features for trend analysis across all matches.

    Args:
        match_data: Match DataFrame

    Returns:
        Dictionary of trend analysis DataFrames
    """
    trends = {}

    # Get numeric columns for winners vs losers
    numeric_cols = [
        col
        for col in match_data.columns
        if col.startswith("w_") and match_data[col].dtype in ["float64", "int64"]
    ]

    for col in numeric_cols:
        col_base = col[2:]  # Remove 'w_' prefix
        if f"l_{col_base}" in match_data.columns:
            yearly_trend = (
                match_data.groupby("t_year")
                .agg({col: "mean", f"l_{col_base}": "mean"})
                .reset_index()
            )

            yearly_trend.columns = ["year", f"winners_{col_base}", f"losers_{col_base}"]
            trends[col_base] = yearly_trend

    logger.info(f"Created {len(trends)} trend analysis features")
    return trends


def get_other_variables_trends(match_data: pd.DataFrame, variable: str) -> pd.DataFrame:
    """
    Get trend data for non-player-specific variables.

    Args:
        match_data: Match DataFrame
        variable: Variable name (e.g., 'minutes', 'best_of')

    Returns:
        DataFrame with yearly trends
    """
    if variable not in match_data.columns:
        logger.warning(f"Variable {variable} not found in match data")
        return pd.DataFrame()

    trend = match_data.groupby("t_year")[variable].mean().reset_index()
    trend.columns = ["year", variable]

    return trend.sort_values("year")


# ============================================================================
# PROFESSIONAL ANALYTICS: Ranking Systems & Executive Dashboard Features
# ============================================================================


def get_player_rankings_by_surface(match_data: pd.DataFrame, min_matches: int = 20) -> pd.DataFrame:
    """
    Generate player rankings by surface (Clay, Hard, Grass).

    Args:
        match_data: Match DataFrame
        min_matches: Minimum matches required to be ranked

    Returns:
        DataFrame with players ranked by win rate for each surface
    """
    surface_rankings = []

    for surface in match_data["surface"].unique():
        if pd.isna(surface):
            continue

        surface_matches = match_data[match_data["surface"] == surface].copy()
        player_stats = create_win_loss_stats(surface_matches, groupby_col="surface")
        
        # Filter by minimum matches
        player_stats = player_stats[player_stats["total_matches"] >= min_matches].copy()
        player_stats["surface"] = surface
        player_stats = player_stats.rename({"name": "player"}, axis=1)
        player_stats["rank"] = player_stats["wlr"].rank(ascending=False, method="min")
        
        surface_rankings.append(player_stats[["rank", "player", "surface", "wins", "losses", "total_matches", "wlr"]])

    rankings_df = pd.concat(surface_rankings, ignore_index=True) if surface_rankings else pd.DataFrame()
    return rankings_df.sort_values(["surface", "rank"])


def get_player_rankings_by_tournament_level(match_data: pd.DataFrame, min_matches: int = 15) -> pd.DataFrame:
    """
    Generate player rankings by tournament level (Grand Slam, Masters, etc).

    Args:
        match_data: Match DataFrame
        min_matches: Minimum matches required to be ranked

    Returns:
        DataFrame with players ranked by win rate for each tournament level
    """
    level_rankings = []

    for level in match_data["t_level"].unique():
        if pd.isna(level):
            continue

        level_matches = match_data[match_data["t_level"] == level].copy()
        player_stats = create_win_loss_stats(level_matches, groupby_col="t_level")
        
        # Filter by minimum matches
        player_stats = player_stats[player_stats["total_matches"] >= min_matches].copy()
        player_stats["t_level"] = level
        player_stats = player_stats.rename({"name": "player"}, axis=1)
        player_stats["rank"] = player_stats["wlr"].rank(ascending=False, method="min")
        
        level_rankings.append(player_stats[["rank", "player", "t_level", "wins", "losses", "total_matches", "wlr"]])

    rankings_df = pd.concat(level_rankings, ignore_index=True) if level_rankings else pd.DataFrame()
    return rankings_df.sort_values(["t_level", "rank"])


def get_top_players_overall(match_data: pd.DataFrame, limit: int = 10, min_matches: int = 50) -> pd.DataFrame:
    """
    Get top players by overall win rate.

    Args:
        match_data: Match DataFrame
        limit: Number of top players to return
        min_matches: Minimum matches required

    Returns:
        DataFrame with top players ranked by win rate
    """
    # Calculate overall statistics for each player
    wins = match_data.groupby("w_name").size().reset_index(name="wins")
    losses = match_data.groupby("l_name").size().reset_index(name="losses")
    losses = losses.rename({"l_name": "w_name"}, axis=1)
    
    # Merge wins and losses
    player_stats = pd.merge(wins, losses, on="w_name", how="outer").fillna(0)
    player_stats["wins"] = player_stats["wins"].astype(int)
    player_stats["losses"] = player_stats["losses"].astype(int)
    player_stats["total_matches"] = player_stats["wins"] + player_stats["losses"]
    
    # Filter by minimum matches and calculate win rate
    player_stats = player_stats[player_stats["total_matches"] >= min_matches].copy()
    player_stats["wlr"] = (player_stats["wins"] / player_stats["total_matches"]).round(4)
    player_stats["rank"] = player_stats["wlr"].rank(ascending=False, method="min")
    
    return player_stats.sort_values("wlr", ascending=False).head(limit)[
        ["rank", "w_name", "wins", "losses", "total_matches", "wlr"]
    ].rename({"w_name": "player"}, axis=1)


def get_executive_dashboard_metrics(match_data: pd.DataFrame, players_df: pd.DataFrame) -> Dict:
    """
    Calculate key metrics for the executive dashboard.

    Args:
        match_data: Match DataFrame
        players_df: Players DataFrame

    Returns:
        Dictionary with key metrics
    """
    total_matches = len(match_data)
    unique_players = len(pd.concat([match_data["w_name"], match_data["l_name"]]).unique())
    unique_tournaments = match_data["t_name"].nunique()
    years_covered = match_data["t_year"].max() - match_data["t_year"].min() + 1
    
    # Most recent year
    most_recent_year = match_data["t_year"].max()
    recent_matches = match_data[match_data["t_year"] == most_recent_year]
    
    # Surface distribution
    surface_dist = match_data["surface"].value_counts().to_dict()
    
    # Tournament level distribution
    level_dist = match_data["t_level"].value_counts().to_dict()
    
    # Average matches per player
    avg_matches_per_player = total_matches / unique_players if unique_players > 0 else 0
    
    # Recent match count
    recent_match_count = len(recent_matches)
    
    metrics = {
        "total_matches": total_matches,
        "unique_players": unique_players,
        "unique_tournaments": unique_tournaments,
        "years_covered": years_covered,
        "most_recent_year": int(most_recent_year),
        "recent_matches": recent_match_count,
        "avg_matches_per_player": round(avg_matches_per_player, 1),
        "surface_distribution": surface_dist,
        "level_distribution": level_dist,
    }
    
    logger.info("Calculated executive dashboard metrics")
    return metrics


def get_yearly_match_trend(match_data: pd.DataFrame) -> pd.DataFrame:
    """
    Get yearly trend of match counts.

    Args:
        match_data: Match DataFrame

    Returns:
        DataFrame with match counts per year
    """
    yearly_trend = match_data.groupby("t_year").size().reset_index(name="match_count")
    yearly_trend = yearly_trend.sort_values("t_year")
    
    # Calculate year-over-year change
    yearly_trend["yoy_change"] = yearly_trend["match_count"].diff()
    yearly_trend["yoy_change_pct"] = (yearly_trend["yoy_change"] / yearly_trend["match_count"].shift()).round(3) * 100
    
    return yearly_trend


def get_player_momentum(match_data: pd.DataFrame, player: str, window: int = 10) -> Dict:
    """
    Calculate player momentum (recent form) using moving average.

    Args:
        match_data: Match DataFrame
        player: Player name
        window: Number of recent matches to consider

    Returns:
        Dictionary with momentum metrics
    """
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy()
    
    if len(player_matches) == 0:
        return {"player": player, "recent_wlr": 0, "momentum": "No data", "total_matches": 0}
    
    # Sort by date
    if "t_date" in player_matches.columns:
        player_matches = player_matches.sort_values("t_date")
    else:
        player_matches = player_matches.sort_values("t_year")
    
    # Get recent matches
    recent_matches = player_matches.tail(window).copy()
    recent_matches["result"] = (recent_matches["w_name"] == player).astype(int)
    
    recent_wins = recent_matches["result"].sum()
    recent_total = len(recent_matches)
    recent_wlr = recent_wins / recent_total if recent_total > 0 else 0
    
    # Determine momentum
    all_time_wlr = len(player_matches[player_matches["w_name"] == player]) / len(player_matches)
    momentum_diff = recent_wlr - all_time_wlr
    
    if momentum_diff > 0.05:
        momentum = "📈 Improving"
    elif momentum_diff < -0.05:
        momentum = "📉 Declining"
    else:
        momentum = "➡️ Stable"
    
    return {
        "player": player,
        "recent_wlr": round(recent_wlr, 3),
        "recent_wins": int(recent_wins),
        "recent_matches": recent_total,
        "momentum": momentum,
        "all_time_wlr": round(all_time_wlr, 3),
    }


def filter_matches_by_date_range(match_data: pd.DataFrame, start_year: int = None, end_year: int = None) -> pd.DataFrame:
    """
    Filter matches by year range.

    Args:
        match_data: Match DataFrame
        start_year: Start year (inclusive)
        end_year: End year (inclusive)

    Returns:
        Filtered DataFrame
    """
    filtered = match_data.copy()
    
    if start_year is not None:
        filtered = filtered[filtered["t_year"] >= start_year]
    
    if end_year is not None:
        filtered = filtered[filtered["t_year"] <= end_year]
    
    logger.info(f"Filtered matches: {len(filtered)} from {start_year} to {end_year}")
    return filtered


# ============================================================================
# ADVANCED ANALYTICS: Statistical Testing, Predictions & Anomaly Detection
# ============================================================================


def calculate_performance_variance(match_data: pd.DataFrame, player: str, groupby_col: str = "surface") -> Dict:
    """
    Calculate performance consistency/variance across different categories (surfaces, levels, etc).
    
    Higher variance = inconsistent player. Lower variance = consistent player.
    
    Args:
        match_data: Match DataFrame
        player: Player name
        groupby_col: Column to group by (surface, t_level, t_year, etc)
        
    Returns:
        Dictionary with variance metrics
    """
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy()
    
    if len(player_matches) == 0:
        return {"player": player, "variance": None, "std_dev": None, "mean_wlr": None}
    
    player_matches["result"] = (player_matches["w_name"] == player).astype(int)
    
    # Group by column and calculate win rate for each group
    group_stats = player_matches.groupby(groupby_col).agg({
        "result": ["sum", "count"]
    }).reset_index()
    
    group_stats.columns = [groupby_col, "wins", "total"]
    group_stats["wlr"] = (group_stats["wins"] / group_stats["total"]).round(4)
    
    # Calculate metrics
    wlr_values = group_stats["wlr"].values
    mean_wlr = wlr_values.mean()
    variance = wlr_values.var()
    std_dev = wlr_values.std()
    cv = (std_dev / mean_wlr * 100) if mean_wlr > 0 else 0  # Coefficient of variation
    
    return {
        "player": player,
        "mean_wlr": round(mean_wlr, 4),
        "variance": round(variance, 4),
        "std_dev": round(std_dev, 4),
        "coefficient_of_variation": round(cv, 2),
        "groups_analyzed": len(group_stats),
        "consistency_score": round(100 - cv, 2),  # Higher is more consistent
        "by_group": group_stats.to_dict('records')
    }


def statistical_significance_test_player_improvement(
    match_data: pd.DataFrame, 
    player: str, 
    surface: Optional[str] = None,
    min_matches: int = 10
) -> Dict:
    """
    Test if a player's performance change is statistically significant using binomial test.
    
    Compares recent performance vs all-time performance.
    
    Args:
        match_data: Match DataFrame
        player: Player name
        surface: Optional surface filter
        min_matches: Minimum matches for analysis
        
    Returns:
        Dictionary with statistical test results and p-value
    """
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy()
    
    if surface:
        player_matches = player_matches[player_matches["surface"] == surface]
    
    if len(player_matches) < min_matches * 2:
        return {"player": player, "significant": False, "p_value": None, "reason": "Insufficient data"}
    
    player_matches = player_matches.sort_values("t_year" if "t_year" in player_matches.columns else player_matches.index)
    player_matches["result"] = (player_matches["w_name"] == player).astype(int)
    
    # Split into two periods
    mid_point = len(player_matches) // 2
    period1 = player_matches.iloc[:mid_point]
    period2 = player_matches.iloc[mid_point:]
    
    wins1 = period1["result"].sum()
    total1 = len(period1)
    wins2 = period2["result"].sum()
    total2 = len(period2)
    
    wlr1 = wins1 / total1 if total1 > 0 else 0
    wlr2 = wins2 / total2 if total2 > 0 else 0
    
    # Binomial test: are the wins in period2 significantly different from period1 rate?
    try:
        p_value = stats.binom_test(wins2, total2, wlr1, alternative='two-sided')
        significant = p_value < 0.05
        
        trend = "📈 Improving" if wlr2 > wlr1 else "📉 Declining" if wlr2 < wlr1 else "➡️ Stable"
        
        return {
            "player": player,
            "surface": surface or "All",
            "period1_wlr": round(wlr1, 3),
            "period1_matches": total1,
            "period2_wlr": round(wlr2, 3),
            "period2_matches": total2,
            "trend": trend,
            "p_value": round(p_value, 4),
            "significant": significant,
            "confidence_level": "95%" if significant else "Not significant"
        }
    except Exception as e:
        logger.warning(f"Statistical test failed for {player}: {str(e)}")
        return {"player": player, "significant": False, "p_value": None, "reason": "Test failed"}


def calculate_confidence_interval(
    match_data: pd.DataFrame, 
    player: str,
    confidence: float = 0.95
) -> Dict:
    """
    Calculate confidence interval around a player's win rate.
    
    Uses binomial proportion confidence interval (Wilson score method).
    
    Args:
        match_data: Match DataFrame
        player: Player name
        confidence: Confidence level (0.95 for 95%, 0.99 for 99%)
        
    Returns:
        Dictionary with confidence interval bounds
    """
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy()
    
    if len(player_matches) == 0:
        return {"player": player, "ci_lower": None, "ci_upper": None, "point_estimate": None}
    
    wins = len(player_matches[player_matches["w_name"] == player])
    total = len(player_matches)
    wlr = wins / total
    
    # Wilson score interval
    z = stats.norm.ppf((1 + confidence) / 2)
    denominator = 1 + z**2 / total
    center = (wlr + z**2 / (2*total)) / denominator
    margin = z * np.sqrt(wlr*(1-wlr)/total + z**2/(4*total**2)) / denominator
    
    ci_lower = max(0, center - margin)
    ci_upper = min(1, center + margin)
    
    return {
        "player": player,
        "win_rate": round(wlr, 4),
        "total_matches": total,
        "wins": wins,
        f"ci_{int(confidence*100)}_lower": round(ci_lower, 4),
        f"ci_{int(confidence*100)}_upper": round(ci_upper, 4),
        "margin_of_error": round(margin, 4),
        "interpretation": f"We are {int(confidence*100)}% confident the true win rate is between {round(ci_lower, 3)} and {round(ci_upper, 3)}"
    }


def detect_performance_anomalies(
    match_data: pd.DataFrame,
    player: str,
    threshold_std: float = 2.0,
    surface: Optional[str] = None
) -> Dict:
    """
    Detect anomalous performances (unusual wins/losses at unexpected surfaces/levels).
    
    Flags performances that are >2 standard deviations from player's expected performance.
    
    Args:
        match_data: Match DataFrame
        player: Player name
        threshold_std: Number of standard deviations for anomaly threshold
        surface: Optional surface filter
        
    Returns:
        Dictionary with anomalies and explanations
    """
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy()
    
    if len(player_matches) < 10:
        return {"player": player, "anomalies": [], "total_matches": len(player_matches)}
    
    player_matches["result"] = (player_matches["w_name"] == player).astype(int)
    
    # Calculate baseline win rate
    baseline_wlr = player_matches["result"].mean()
    
    # Analyze by surface if not filtered
    if surface:
        player_matches = player_matches[player_matches["surface"] == surface]
        surface_wlr = player_matches["result"].mean()
        anomalies = []
        
        if surface_wlr < baseline_wlr - 0.15:
            anomalies.append({
                "type": "🚨 Underperforming on " + surface,
                "expected_wlr": round(baseline_wlr, 3),
                "actual_wlr": round(surface_wlr, 3),
                "matches": len(player_matches),
                "severity": "HIGH" if surface_wlr < baseline_wlr - 0.25 else "MEDIUM"
            })
        elif surface_wlr > baseline_wlr + 0.15:
            anomalies.append({
                "type": "✅ Outperforming on " + surface,
                "expected_wlr": round(baseline_wlr, 3),
                "actual_wlr": round(surface_wlr, 3),
                "matches": len(player_matches),
                "severity": "POSITIVE"
            })
    else:
        anomalies = []
        # Check by surface
        for surf in player_matches["surface"].unique():
            if pd.isna(surf):
                continue
            surf_matches = player_matches[player_matches["surface"] == surf]
            if len(surf_matches) < 5:
                continue
            
            surf_wlr = surf_matches["result"].mean()
            diff = surf_wlr - baseline_wlr
            
            if abs(diff) > 0.20:
                anomalies.append({
                    "surface": surf,
                    "type": "🚨 Underperforming" if diff < 0 else "✅ Strong Performance",
                    "expected_wlr": round(baseline_wlr, 3),
                    "actual_wlr": round(surf_wlr, 3),
                    "difference": round(diff, 3),
                    "matches": len(surf_matches),
                    "severity": "HIGH" if abs(diff) > 0.30 else "MEDIUM"
                })
    
    return {
        "player": player,
        "baseline_wlr": round(baseline_wlr, 3),
        "anomalies_detected": len(anomalies),
        "anomalies": sorted(anomalies, key=lambda x: x.get("severity", ""), reverse=True),
        "total_matches": len(player_matches)
    }


def predict_h2h_outcome(
    match_data: pd.DataFrame,
    player1: str,
    player2: str,
    surface: Optional[str] = None,
    tournament_level: Optional[str] = None
) -> Dict:
    """
    Predict head-to-head outcome based on historical performance and conditions.
    
    Simple model using:
    - Overall win rates
    - Head-to-head record
    - Surface-specific performance
    - Tournament level performance
    
    Args:
        match_data: Match DataFrame
        player1: First player
        player2: Second player
        surface: Specific surface condition (optional)
        tournament_level: Specific tournament level (optional)
        
    Returns:
        Dictionary with prediction and confidence
    """
    # Get overall records
    p1_record = calculate_player_h2h_record(match_data, player1)
    p2_record = calculate_player_h2h_record(match_data, player2)
    
    p1_wlr = p1_record["win_percentage"] / 100 if p1_record["total_matches"] > 0 else 0.5
    p2_wlr = p2_record["win_percentage"] / 100 if p2_record["total_matches"] > 0 else 0.5
    
    # Get head-to-head
    h2h_record = calculate_player_h2h_record(match_data, player1, player2)
    h2h_p1_wlr = h2h_record["win_percentage"] / 100 if h2h_record["total_matches"] > 0 else 0.5
    
    # Filter by conditions
    filtered_data = match_data.copy()
    if surface:
        filtered_data = filtered_data[filtered_data["surface"] == surface]
    if tournament_level:
        filtered_data = filtered_data[filtered_data["t_level"] == tournament_level]
    
    # Get conditional performance
    p1_cond = calculate_player_h2h_record(filtered_data, player1)
    p2_cond = calculate_player_h2h_record(filtered_data, player2)
    
    p1_cond_wlr = p1_cond["win_percentage"] / 100 if p1_cond["total_matches"] > 0 else p1_wlr
    p2_cond_wlr = p2_cond["win_percentage"] / 100 if p2_cond["total_matches"] > 0 else p2_wlr
    
    # Weighted prediction (40% overall, 40% conditional, 20% h2h)
    p1_pred_prob = (p1_wlr * 0.4 + p1_cond_wlr * 0.4 + h2h_p1_wlr * 0.2)
    p2_pred_prob = 1 - p1_pred_prob
    
    # Determine confidence
    confidence_factors = [
        h2h_record["total_matches"] > 5,  # Good h2h history
        p1_cond["total_matches"] > 10,    # Good sample for conditions
        p1_record["total_matches"] > 50   # Large overall sample
    ]
    confidence = sum(confidence_factors) / 3
    
    # Determine favorite
    if p1_pred_prob > 0.60:
        favorite = player1
        underdog = player2
        favorite_prob = p1_pred_prob
    elif p2_pred_prob > 0.60:
        favorite = player2
        underdog = player1
        favorite_prob = p2_pred_prob
    else:
        favorite = "Even"
        underdog = "Even"
        favorite_prob = 0.5
    
    return {
        "matchup": f"{player1} vs {player2}",
        "conditions": f"{'Surface: ' + surface if surface else ''} {'Level: ' + tournament_level if tournament_level else ''}".strip() or "Overall",
        "player1": player1,
        "player1_probability": round(p1_pred_prob, 3),
        "player1_wlr": round(p1_wlr, 3),
        "player2": player2,
        "player2_probability": round(p2_pred_prob, 3),
        "player2_wlr": round(p2_wlr, 3),
        "h2h_record": f"{h2h_record['wins']}-{h2h_record['losses']} ({player1} perspective)",
        "prediction": f"{favorite} favored" if favorite != "Even" else "Even match",
        "favorite_probability": round(favorite_prob, 3),
        "confidence": round(confidence, 2),
        "prediction_confidence": "HIGH" if confidence > 0.7 else "MODERATE" if confidence > 0.4 else "LOW"
    }


def analyze_tournament_difficulty(match_data: pd.DataFrame, tournament: str) -> Dict:
    """
    Analyze tournament difficulty based on field composition.
    
    Scores difficulty based on average opponent win rates.
    
    Args:
        match_data: Match DataFrame
        tournament: Tournament name
        
    Returns:
        Dictionary with difficulty metrics
    """
    tournament_matches = match_data[match_data["t_name"] == tournament].copy()
    
    if len(tournament_matches) == 0:
        return {"tournament": tournament, "difficulty_score": None}
    
    all_players = pd.concat([
        tournament_matches["w_name"],
        tournament_matches["l_name"]
    ]).unique()
    
    player_strengths = []
    for player in all_players:
        if pd.isna(player):
            continue
        w_pct = calculate_player_h2h_record(match_data, player)["win_percentage"] / 100
        player_strengths.append(w_pct)
    
    avg_strength = np.mean(player_strengths) if player_strengths else 0.5
    std_strength = np.std(player_strengths) if player_strengths else 0
    
    # Difficulty score: 0-100 where higher = harder
    difficulty_score = round((avg_strength * 100), 1)
    
    return {
        "tournament": tournament,
        "num_players": len(all_players),
        "num_matches": len(tournament_matches),
        "avg_player_strength": round(avg_strength, 3),
        "field_consistency": round(std_strength, 3),
        "difficulty_score": difficulty_score,
        "difficulty_interpretation": 
            "🟢 Easy field" if difficulty_score < 45 else
            "🟡 Moderate field" if difficulty_score < 55 else
            "🔴 Strong field"
    }


# ============================================================================
# TIME SERIES ANALYSIS FUNCTIONS
# ============================================================================

def calculate_moving_average(match_data: pd.DataFrame, player: str, window: int = 10) -> pd.DataFrame:
    """
    Calculate moving average win percentage for a player over time.
    
    Args:
        match_data: Match DataFrame with 'date' and player columns
        player: Player name
        window: Window size for moving average (default 10 matches)
        
    Returns:
        DataFrame with dates and moving average win percentages
    """
    # Get player matches sorted by date
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy().sort_values("date")
    
    if len(player_matches) < window:
        logger.warning(f"Player {player} has fewer than {window} matches")
        return pd.DataFrame()
    
    # Create binary win column (1 for win, 0 for loss)
    player_matches["win"] = (player_matches["w_name"] == player).astype(int)
    
    # Calculate moving average win percentage
    player_matches["moving_avg"] = (
        player_matches["win"].rolling(window=window, min_periods=1).mean() * 100
    )
    
    return player_matches[["date", "moving_avg", "win"]].reset_index(drop=True)


def get_monthly_performance_trend(match_data: pd.DataFrame, player: str) -> pd.DataFrame:
    """
    Get monthly performance metrics for a player.
    
    Args:
        match_data: Match DataFrame with 'date' column
        player: Player name
        
    Returns:
        DataFrame with monthly win rates and match counts
    """
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy()
    
    if len(player_matches) == 0:
        return pd.DataFrame()
    
    # Convert date to datetime if not already
    player_matches["date"] = pd.to_datetime(player_matches["date"])
    player_matches["year_month"] = player_matches["date"].dt.to_period("M")
    
    # Calculate monthly stats
    monthly_stats = []
    for period, group in player_matches.groupby("year_month"):
        wins = (group["w_name"] == player).sum()
        losses = (group["l_name"] == player).sum()
        total = wins + losses
        win_pct = (wins / total * 100) if total > 0 else 0
        
        monthly_stats.append({
            "month": str(period),
            "wins": wins,
            "losses": losses,
            "total_matches": total,
            "win_percentage": round(win_pct, 1)
        })
    
    return pd.DataFrame(monthly_stats)


def get_quarterly_performance_trend(match_data: pd.DataFrame, player: str) -> pd.DataFrame:
    """
    Get quarterly performance metrics for a player.
    
    Args:
        match_data: Match DataFrame with 'date' column
        player: Player name
        
    Returns:
        DataFrame with quarterly win rates and match counts
    """
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy()
    
    if len(player_matches) == 0:
        return pd.DataFrame()
    
    # Convert date to datetime if not already
    player_matches["date"] = pd.to_datetime(player_matches["date"])
    player_matches["year_quarter"] = player_matches["date"].dt.to_period("Q")
    
    # Calculate quarterly stats
    quarterly_stats = []
    for period, group in player_matches.groupby("year_quarter"):
        wins = (group["w_name"] == player).sum()
        losses = (group["l_name"] == player).sum()
        total = wins + losses
        win_pct = (wins / total * 100) if total > 0 else 0
        
        quarterly_stats.append({
            "quarter": str(period),
            "wins": wins,
            "losses": losses,
            "total_matches": total,
            "win_percentage": round(win_pct, 1)
        })
    
    return pd.DataFrame(quarterly_stats)


def detect_seasonal_patterns(match_data: pd.DataFrame, player: str) -> Dict:
    """
    Detect seasonal performance patterns for a player.
    
    Args:
        match_data: Match DataFrame with 'date' column
        player: Player name
        
    Returns:
        Dictionary with seasonal performance metrics
    """
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy()
    
    if len(player_matches) == 0:
        return {}
    
    # Convert date to datetime if not already
    player_matches["date"] = pd.to_datetime(player_matches["date"])
    player_matches["month"] = player_matches["date"].dt.month
    
    # Calculate performance by month (1-12)
    monthly_performance = {}
    for month in range(1, 13):
        month_matches = player_matches[player_matches["month"] == month]
        if len(month_matches) > 0:
            wins = (month_matches["w_name"] == player).sum()
            total = len(month_matches)
            win_pct = (wins / total * 100) if total > 0 else 0
            monthly_performance[month] = {
                "month_name": pd.to_datetime(f"2021-{month:02d}-01").strftime("%B"),
                "matches": total,
                "win_percentage": round(win_pct, 1)
            }
    
    # Find best and worst months
    if monthly_performance:
        best_month = max(monthly_performance.items(), 
                        key=lambda x: x[1]["win_percentage"])
        worst_month = min(monthly_performance.items(), 
                         key=lambda x: x[1]["win_percentage"])
        
        best_months = [m for m, data in monthly_performance.items() 
                      if data["win_percentage"] >= 60]
        worst_months = [m for m, data in monthly_performance.items() 
                       if data["win_percentage"] <= 40]
    else:
        best_month = worst_month = None
        best_months = worst_months = []
    
    return {
        "player": player,
        "monthly_performance": monthly_performance,
        "best_month": {
            "month": best_month[0] if best_month else None,
            "month_name": best_month[1]["month_name"] if best_month else None,
            "win_percentage": round(best_month[1]["win_percentage"], 1) if best_month else None
        },
        "worst_month": {
            "month": worst_month[0] if worst_month else None,
            "month_name": worst_month[1]["month_name"] if worst_month else None,
            "win_percentage": round(worst_month[1]["win_percentage"], 1) if worst_month else None
        },
        "strong_season_months": best_months,
        "weak_season_months": worst_months,
        "seasonality_detected": len(best_months) > 0 and len(worst_months) > 0
    }


def analyze_performance_trend(match_data: pd.DataFrame, player: str) -> Dict:
    """
    Analyze overall performance trend (improving/declining/stable).
    
    Divides career into early, middle, late periods and compares win rates.
    
    Args:
        match_data: Match DataFrame
        player: Player name
        
    Returns:
        Dictionary with trend analysis
    """
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy().sort_values("date")
    
    if len(player_matches) < 10:
        return {"player": player, "trend": "insufficient_data", "matches": len(player_matches)}
    
    # Divide into three periods
    third = len(player_matches) // 3
    early_period = player_matches.iloc[:third]
    middle_period = player_matches.iloc[third:2*third]
    late_period = player_matches.iloc[2*third:]
    
    def calc_win_pct(period):
        if len(period) == 0:
            return None
        wins = (period["w_name"] == player).sum()
        total = len(period)
        return (wins / total * 100) if total > 0 else 0
    
    early_wp = calc_win_pct(early_period)
    middle_wp = calc_win_pct(middle_period)
    late_wp = calc_win_pct(late_period)
    
    # Determine trend
    if late_wp > middle_wp > early_wp:
        trend = "📈 Improving"
        trend_type = "improving"
    elif late_wp < middle_wp < early_wp:
        trend = "📉 Declining"
        trend_type = "declining"
    elif abs(late_wp - early_wp) < 5:
        trend = "➡️ Stable"
        trend_type = "stable"
    else:
        trend = "↔️ Fluctuating"
        trend_type = "fluctuating"
    
    # Calculate trend magnitude
    trend_change = late_wp - early_wp
    
    return {
        "player": player,
        "early_period_wp": round(early_wp, 1) if early_wp else None,
        "middle_period_wp": round(middle_wp, 1) if middle_wp else None,
        "late_period_wp": round(late_wp, 1) if late_wp else None,
        "trend": trend,
        "trend_type": trend_type,
        "overall_change": round(trend_change, 1),
        "matches_analyzed": len(player_matches)
    }


def create_career_arc_visualization(match_data: pd.DataFrame, player: str, 
                                    segment_size: int = 20) -> pd.DataFrame:
    """
    Create career arc data for visualization showing player development over time.
    
    Segments player career into chunks and shows progression of win rates,
    tournament wins, and ranking trajectory.
    
    Args:
        match_data: Match DataFrame
        player: Player name
        segment_size: Number of matches per segment (default 20)
        
    Returns:
        DataFrame with career arc phases and performance metrics
    """
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy().sort_values("date")
    
    if len(player_matches) < segment_size:
        return pd.DataFrame()
    
    # Create segments
    num_segments = len(player_matches) // segment_size
    segments = []
    
    for seg_idx in range(num_segments):
        start_idx = seg_idx * segment_size
        end_idx = (seg_idx + 1) * segment_size
        segment = player_matches.iloc[start_idx:end_idx]
        
        if len(segment) == 0:
            continue
        
        # Calculate segment stats
        wins = (segment["w_name"] == player).sum()
        total = len(segment)
        win_pct = (wins / total * 100) if total > 0 else 0
        
        # Tournament variety
        tournaments_in_segment = segment["t_name"].nunique()
        
        # Rank calculation (simplified - based on win pct)
        tournament_wins = (segment["w_name"] == player).sum()
        
        # Career phase
        phase_pct = (seg_idx + 1) / num_segments * 100
        if phase_pct <= 25:
            phase = "Early"
            phase_emoji = "🌱"
        elif phase_pct <= 50:
            phase = "Rising"
            phase_emoji = "📈"
        elif phase_pct <= 75:
            phase = "Peak"
            phase_emoji = "⭐"
        else:
            phase = "Late"
            phase_emoji = "👑"
        
        segments.append({
            "segment": seg_idx + 1,
            "phase": phase,
            "phase_emoji": phase_emoji,
            "phase_percent": round(phase_pct, 1),
            "date_start": segment["date"].min(),
            "date_end": segment["date"].max(),
            "matches": total,
            "wins": wins,
            "win_percentage": round(win_pct, 1),
            "tournaments": tournaments_in_segment,
            "tournament_wins": tournament_wins
        })
    
    return pd.DataFrame(segments)


def get_peak_performance_period(match_data: pd.DataFrame, player: str) -> Dict:
    """
    Identify player's peak performance period (best career phases).
    
    Args:
        match_data: Match DataFrame
        player: Player name
        
    Returns:
        Dictionary with peak period details
    """
    career_arc = create_career_arc_visualization(match_data, player)
    
    if len(career_arc) == 0:
        return {}
    
    # Find peak
    peak_row = career_arc.loc[career_arc["win_percentage"].idxmax()]
    
    # Find sustained excellence (3+ segments with 60%+ win rate)
    excellent_periods = career_arc[career_arc["win_percentage"] >= 60]
    
    return {
        "player": player,
        "peak_period": peak_row["phase"],
        "peak_segment": int(peak_row["segment"]),
        "peak_win_percentage": peak_row["win_percentage"],
        "peak_date_start": peak_row["date_start"],
        "peak_date_end": peak_row["date_end"],
        "peak_matches": int(peak_row["matches"]),
        "sustained_excellence_segments": len(excellent_periods),
        "total_segments": len(career_arc),
        "has_consistent_peak": len(excellent_periods) >= 3,
        "career_trajectory": "ascending" if len(career_arc) > 0 and 
                            career_arc.iloc[-1]["win_percentage"] > career_arc.iloc[0]["win_percentage"] 
                            else "descending"
    }


def identify_career_phases(match_data: pd.DataFrame, player: str) -> Dict:
    """
    Identify distinct phases in player's career (rise, peak, decline, etc.).
    
    Args:
        match_data: Match DataFrame
        player: Player name
        
    Returns:
        Dictionary with identified career phases
    """
    player_matches = match_data[
        (match_data["w_name"] == player) | (match_data["l_name"] == player)
    ].copy().sort_values("date")
    
    if len(player_matches) < 50:
        return {"player": player, "status": "insufficient_data"}
    
    # Divide into 5-year windows (approximate)
    player_matches["date"] = pd.to_datetime(player_matches["date"])
    player_matches["year"] = player_matches["date"].dt.year
    
    unique_years = sorted(player_matches["year"].unique())
    year_span = unique_years[-1] - unique_years[0]
    
    if year_span < 3:
        return {"player": player, "status": "insufficient_timespan"}
    
    # Create yearly analysis
    yearly_performance = []
    for year in unique_years:
        year_matches = player_matches[player_matches["year"] == year]
        if len(year_matches) > 0:
            wins = (year_matches["w_name"] == player).sum()
            total = len(year_matches)
            wp = (wins / total * 100) if total > 0 else 0
            yearly_performance.append({
                "year": year,
                "matches": total,
                "wins": wins,
                "win_percentage": wp
            })
    
    if len(yearly_performance) < 3:
        return {"player": player, "status": "insufficient_history"}
    
    df_yearly = pd.DataFrame(yearly_performance)
    
    # Identify phases
    phases = []
    
    # Find peak year
    peak_idx = df_yearly["win_percentage"].idxmax()
    peak_year = df_yearly.loc[peak_idx, "year"]
    peak_wp = df_yearly.loc[peak_idx, "win_percentage"]
    
    # Early years (before peak)
    if peak_idx > 0:
        early = df_yearly.iloc[:peak_idx]
        early_trend = "rising" if early.iloc[-1]["win_percentage"] > early.iloc[0]["win_percentage"] else "variable"
        phases.append({
            "phase": "Early Career",
            "years": f"{early.iloc[0]['year']}-{early.iloc[-1]['year']}",
            "trend": early_trend,
            "avg_wp": round(early["win_percentage"].mean(), 1)
        })
    
    # Peak years
    peak_buffer = 2
    peak_start = max(0, peak_idx - peak_buffer)
    peak_end = min(len(df_yearly) - 1, peak_idx + peak_buffer)
    peak_phase = df_yearly.iloc[peak_start:peak_end + 1]
    phases.append({
        "phase": "Peak Performance",
        "years": f"{peak_phase.iloc[0]['year']}-{peak_phase.iloc[-1]['year']}",
        "trend": "sustained high performance",
        "avg_wp": round(peak_phase["win_percentage"].mean(), 1)
    })
    
    # Later years (after peak)
    if peak_idx < len(df_yearly) - 1:
        later = df_yearly.iloc[peak_idx + 1:]
        later_trend = "declining" if later.iloc[-1]["win_percentage"] < later.iloc[0]["win_percentage"] else "variable"
        phases.append({
            "phase": "Later Career",
            "years": f"{later.iloc[0]['year']}-{later.iloc[-1]['year']}",
            "trend": later_trend,
            "avg_wp": round(later["win_percentage"].mean(), 1)
        })
    
    return {
        "player": player,
        "career_span_years": year_span,
        "peak_year": int(peak_year),
        "peak_win_percentage": round(peak_wp, 1),
        "phases": phases,
        "total_matches_analyzed": len(player_matches)
    }
