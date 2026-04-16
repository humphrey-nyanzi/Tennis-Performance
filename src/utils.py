"""
Utility functions for Tennis Performance Analysis project.
Common helpers, calculations, and data transformations.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Optional
import logging
from src.constants import COLUMN_DISPLAY_NAMES, TOURNAMENT_LEVELS, BEST_OF_VALUES

logger = logging.getLogger(__name__)


def calculate_win_loss_ratio(wins: int, losses: int) -> float:
    """
    Calculate win/loss ratio as a percentage.

    Args:
        wins: Number of wins
        losses: Number of losses

    Returns:
        Win percentage (0-100)
    """
    total = wins + losses
    if total == 0:
        return 0.0
    return (wins / total) * 100


def calculate_streaks(player_matches: pd.DataFrame) -> Dict[str, Optional[int]]:
    """
    Calculate win/loss streaks for a player.

    Args:
        player_matches: DataFrame of player matches sorted by date
                       Must have 'result' column (1 = win, 0 = loss)

    Returns:
        Dictionary with streak information
    """
    if len(player_matches) == 0:
        return {
            "longest_win_streak": None,
            "longest_losing_streak": None,
            "current_streak_length": None,
            "current_streak_type": None,
        }

    player_matches = player_matches.copy()
    player_matches["streak"] = (
        player_matches["result"] != player_matches["result"].shift()
    ).cumsum()

    streak_lengths = (
        player_matches.groupby(["streak", "result"])
        .size()
        .reset_index(name="streak_length")
    )

    longest_win_streak = streak_lengths[streak_lengths["result"] == 1][
        "streak_length"
    ].max()
    longest_losing_streak = streak_lengths[streak_lengths["result"] == 0][
        "streak_length"
    ].max()

    # Handle NaN values
    longest_win_streak = (
        int(longest_win_streak) if pd.notna(longest_win_streak) else None
    )
    longest_losing_streak = (
        int(longest_losing_streak) if pd.notna(longest_losing_streak) else None
    )

    # Current streak
    try:
        current_streak_length = int(streak_lengths.iloc[-1]["streak_length"])
        current_streak_type = (
            "Winning" if player_matches.iloc[-1]["result"] == 1 else "Losing"
        )
    except (IndexError, KeyError):
        current_streak_length = None
        current_streak_type = None

    return {
        "longest_win_streak": longest_win_streak,
        "longest_losing_streak": longest_losing_streak,
        "current_streak_length": current_streak_length,
        "current_streak_type": current_streak_type,
    }


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format a value as a percentage string.

    Args:
        value: Value to format
        decimals: Number of decimal places

    Returns:
        Formatted percentage string
    """
    try:
        return f"{round(value, decimals)}%"
    except (TypeError, ValueError):
        return "N/A"


def format_duration(minutes: float) -> str:
    """
    Format match duration in minutes to readable string.

    Args:
        minutes: Duration in minutes

    Returns:
        Formatted duration string
    """
    try:
        return f"{round(minutes, 1)} min"
    except (TypeError, ValueError):
        return "N/A"


def safe_get_value(series: pd.Series, index: int = 0, default: str = "N/A") -> str:
    """
    Safely get a value from a pandas Series.

    Args:
        series: Pandas Series
        index: Index to retrieve (non-negative only)
        default: Default value if index not found

    Returns:
        Value or default
    """
    try:
        # Treat negative indices as out-of-range for safety (no Python-style negative indexing)
        if index < 0:
            return default
        return str(series.iloc[index])
    except (IndexError, AttributeError, TypeError):
        return default


def get_numeric_columns(df: pd.DataFrame, exclude: list = None) -> list:
    """
    Get list of numeric columns from a DataFrame.

    Args:
        df: Input DataFrame
        exclude: Columns to exclude

    Returns:
        List of numeric column names
    """
    exclude = exclude or []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    return [col for col in numeric_cols if col not in exclude]


def round_numeric(df: pd.DataFrame, decimals: int = 2) -> pd.DataFrame:
    """
    Round all numeric columns in a DataFrame.

    Args:
        df: Input DataFrame
        decimals: Number of decimal places

    Returns:
        DataFrame with rounded numeric values
    """
    numeric_cols = get_numeric_columns(df)
    df_rounded = df.copy()
    for col in numeric_cols:
        df_rounded[col] = df_rounded[col].round(decimals)
    return df_rounded


def validate_player_exists(players_df: pd.DataFrame, player_name: str) -> bool:
    """
    Check if a player exists in the players DataFrame.

    Args:
        players_df: Players DataFrame
        player_name: Player name to check

    Returns:
        True if player exists, False otherwise
    """
    return player_name in players_df["name"].values


def validate_tournament_exists(
    tournaments_df: pd.DataFrame, tournament_name: str
) -> bool:
    """
    Check if a tournament exists in the tournaments DataFrame.

    Args:
        tournaments_df: Tournaments DataFrame
        tournament_name: Tournament name to check

    Returns:
        True if tournament exists, False otherwise
    """
    return tournament_name in tournaments_df["name"].values


def get_filter_options(matches_df: pd.DataFrame) -> list:
    """
    Get available filter options from matches data.

    Args:
        matches_df: Matches DataFrame

    Returns:
        List of available filter column names
    """
    filters = [
        "None",
        "t_name",
        "surface",
        "t_level",
        "best_of",
        "round",
        "t_year",
        "t_month",
    ]
    available = ["None"] + [f for f in filters[1:] if f in matches_df.columns]
    return available


def get_display_name(column: str) -> str:
    """Convert raw dataset field names into viewer-friendly labels."""
    if column in COLUMN_DISPLAY_NAMES:
        return COLUMN_DISPLAY_NAMES[column]

    cleaned = column.replace("_", " ").strip()
    if cleaned.lower().startswith("w "):
        cleaned = "Winner " + cleaned[2:]
    elif cleaned.lower().startswith("l "):
        cleaned = "Loser " + cleaned[2:]
    return cleaned.title()


def format_dimension_value(column: str, value) -> str:
    """Format common categorical values for reader-friendly display."""
    if pd.isna(value):
        return "Unknown"

    if column == "t_level":
        return TOURNAMENT_LEVELS.get(value, str(value))
    if column == "best_of":
        return BEST_OF_VALUES.get(value, f"Best of {value}")
    if column == "t_month":
        month_lookup = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December",
        }
        return month_lookup.get(int(value), str(value))
    return str(value)


def get_featured_players(
    players_df: pd.DataFrame,
    yearly_perf_df: pd.DataFrame,
    count: int = 3,
    exclude: Optional[list] = None,
) -> list:
    """Return interesting default players using the latest available rankings."""
    exclude = set(exclude or [])

    if not yearly_perf_df.empty and {"player", "t_year", "rank"}.issubset(yearly_perf_df.columns):
        ranked = (
            yearly_perf_df.dropna(subset=["player", "t_year", "rank"])
            .sort_values(["t_year", "rank"], ascending=[False, True])
        )
        latest_year = ranked["t_year"].max()
        featured = [
            player
            for player in ranked[ranked["t_year"] == latest_year]["player"].tolist()
            if player not in exclude
        ]
        deduped = list(dict.fromkeys(featured))
        if len(deduped) >= count:
            return deduped[:count]

    fallback = [
        player
        for player in players_df.sort_values(["wins", "wlr"], ascending=[False, False])["name"].tolist()
        if player not in exclude
    ]
    return list(dict.fromkeys(fallback))[:count]


def format_table_display(df: pd.DataFrame, columns: list = None) -> pd.DataFrame:
    """
    Format DataFrame for display in UI.

    Args:
        df: Input DataFrame
        columns: Columns to include (if None, include all)

    Returns:
        Formatted DataFrame
    """
    display_df = df[columns].copy() if columns else df.copy()

    # Round numeric columns
    numeric_cols = get_numeric_columns(display_df)
    for col in numeric_cols:
        display_df[col] = display_df[col].round(2)

    return display_df


def get_year_range(matches_df: pd.DataFrame) -> Tuple[int, int]:
    """
    Get the range of years in the matches data.

    Args:
        matches_df: Matches DataFrame

    Returns:
        Tuple of (min_year, max_year)
    """
    try:
        if "t_year" in matches_df.columns:
            years = matches_df["t_year"].dropna()
            return int(years.min()), int(years.max())
        return 2000, 2024
    except (ValueError, AttributeError):
        return 2000, 2024


def compare_dataframes_by_column(
    df1: pd.DataFrame, df2: pd.DataFrame, column: str, key1: str, key2: str
) -> pd.DataFrame:
    """
    Compare two DataFrames side by side for a specific column.

    Args:
        df1: First DataFrame
        df2: Second DataFrame
        column: Column to filter by
        key1: Key value in column for df1
        key2: Key value in column for df2

    Returns:
        Combined DataFrame with comparison data
    """
    filtered1 = df1[df1[column] == key1].copy()
    filtered2 = df2[df2[column] == key2].copy()

    return pd.concat([filtered1, filtered2], axis=0, ignore_index=True)
