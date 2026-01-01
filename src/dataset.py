"""
Data loading and validation module for Tennis Performance Analysis.
Handles CSV file loading with caching and validation.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


def load_players_data(filepath: Path) -> pd.DataFrame:
    """
    Load and validate player data.

    Args:
        filepath: Path to the players CSV file

    Returns:
        DataFrame containing player data

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If required columns are missing
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Players data file not found: {filepath}")

    df = pd.read_csv(filepath)

    # Validate required columns
    required_cols = ["name", "country", "total_matches", "wins", "losses"]
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    logger.info(f"Loaded {len(df)} players from {filepath.name}")
    return df


def load_yearly_performance_data(filepath: Path) -> pd.DataFrame:
    """
    Load and validate yearly player performance data.

    Args:
        filepath: Path to the yearly performance CSV file

    Returns:
        DataFrame containing yearly performance metrics

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Yearly performance data file not found: {filepath}")

    df = pd.read_csv(filepath)
    df["t_year"] = pd.to_numeric(df["t_year"], errors="coerce")

    logger.info(f"Loaded yearly performance data: {df.shape}")
    return df


def load_matches_data(filepath: Path) -> pd.DataFrame:
    """
    Load and validate match data.

    Args:
        filepath: Path to the matches CSV file

    Returns:
        DataFrame containing match data

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Matches data file not found: {filepath}")

    df = pd.read_csv(filepath)

    # Convert date columns
    if "t_date" in df.columns:
        df["t_date"] = pd.to_datetime(df["t_date"], format="%Y%m%d", errors="coerce")
    if "t_year" in df.columns:
        df["t_year"] = pd.to_numeric(df["t_year"], errors="coerce")

    logger.info(f"Loaded {len(df)} matches from {filepath.name}")
    return df


def load_tournaments_data(filepath: Path) -> pd.DataFrame:
    """
    Load and validate tournament data.

    Args:
        filepath: Path to the tournaments CSV file

    Returns:
        DataFrame containing tournament data

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Tournaments data file not found: {filepath}")

    df = pd.read_csv(filepath)
    logger.info(f"Loaded {len(df)} tournaments from {filepath.name}")
    return df


def load_all_data(data_paths: Dict[str, Path]) -> Dict[str, pd.DataFrame]:
    """
    Load all required datasets.

    Args:
        data_paths: Dictionary of data file paths
                   Keys: 'players', 'yearly_performance', 'matches', 'tournaments'

    Returns:
        Dictionary of loaded DataFrames

    Raises:
        FileNotFoundError: If any required file doesn't exist
    """
    data = {
        "players": load_players_data(data_paths["players"]),
        "yearly_performance": load_yearly_performance_data(
            data_paths["yearly_performance"]
        ),
        "matches": load_matches_data(data_paths["matches"]),
        "tournaments": load_tournaments_data(data_paths["tournaments"]),
    }

    return data


def validate_data_integrity(data: Dict[str, pd.DataFrame]) -> Tuple[bool, list]:
    """
    Validate data integrity and consistency.

    Args:
        data: Dictionary of loaded DataFrames

    Returns:
        Tuple of (is_valid, list of issues found)
    """
    issues = []

    # Check for null values in critical columns
    players_null = data["players"][["name", "country"]].isnull().sum()
    if players_null.any():
        issues.append(
            f"Null values in players data: {players_null[players_null > 0].to_dict()}"
        )

    # Check match data consistency
    matches = data["matches"]
    if "w_name" in matches.columns and "l_name" in matches.columns:
        if (matches["w_name"] == matches["l_name"]).any():
            issues.append("Match data contains winner == loser")

    return len(issues) == 0, issues


def filter_players_by_matches(df: pd.DataFrame, min_matches: int = 50) -> pd.DataFrame:
    """
    Filter players by minimum number of matches.

    Args:
        df: Players DataFrame
        min_matches: Minimum number of matches required

    Returns:
        Filtered DataFrame
    """
    original_count = len(df)
    df_filtered = df[df["total_matches"] >= min_matches].copy()
    logger.info(
        f"Filtered players: {original_count} -> {len(df_filtered)} (min {min_matches} matches)"
    )
    return df_filtered


def get_player_names(players_df: pd.DataFrame) -> list:
    """
    Get sorted list of player names.

    Args:
        players_df: Players DataFrame

    Returns:
        Sorted list of player names
    """
    return sorted(players_df["name"].unique().tolist())


def get_tournament_names(tournaments_df: pd.DataFrame) -> list:
    """
    Get sorted list of tournament names.

    Args:
        tournaments_df: Tournaments DataFrame

    Returns:
        Sorted list of tournament names
    """
    return sorted(tournaments_df["name"].unique().tolist())
