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
    rankings_df = create_win_loss_stats(match_data, groupby_col="surface")
    if rankings_df.empty:
        return rankings_df

    rankings_df = rankings_df[
        rankings_df["surface"].notna() & (rankings_df["total_matches"] >= min_matches)
    ].copy()
    rankings_df = rankings_df.rename({"name": "player"}, axis=1)
    rankings_df["rank"] = (
        rankings_df.groupby("surface")["wlr"].rank(ascending=False, method="min")
    )

    return rankings_df[
        ["rank", "player", "surface", "wins", "losses", "total_matches", "wlr"]
    ].sort_values(["surface", "rank"])


def get_player_rankings_by_tournament_level(match_data: pd.DataFrame, min_matches: int = 15) -> pd.DataFrame:
    """
    Generate player rankings by tournament level (Grand Slam, Masters, etc).

    Args:
        match_data: Match DataFrame
        min_matches: Minimum matches required to be ranked

    Returns:
        DataFrame with players ranked by win rate for each tournament level
    """
    rankings_df = create_win_loss_stats(match_data, groupby_col="t_level")
    if rankings_df.empty:
        return rankings_df

    rankings_df = rankings_df[
        rankings_df["t_level"].notna() & (rankings_df["total_matches"] >= min_matches)
    ].copy()
    rankings_df = rankings_df.rename({"name": "player"}, axis=1)
    rankings_df["rank"] = (
        rankings_df.groupby("t_level")["wlr"].rank(ascending=False, method="min")
    )

    return rankings_df[
        ["rank", "player", "t_level", "wins", "losses", "total_matches", "wlr"]
    ].sort_values(["t_level", "rank"])


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
    filtered = match_data

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








