"""
Feature engineering module for Tennis Performance Analysis.
Creates advanced features and aggregates player/tournament statistics.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging

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

    h2h = h2h.sort_values("t_date", ascending=False)

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
