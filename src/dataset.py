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
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    # Strip whitespace from all string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()

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
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    
    # Strip whitespace from all string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()
    
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
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    # Strip whitespace from player name columns
    if "w_name" in df.columns:
        df["w_name"] = df["w_name"].str.strip()
    if "l_name" in df.columns:
        df["l_name"] = df["l_name"].str.strip()

    # Strip whitespace from all other string columns
    for col in df.select_dtypes(include=['object']).columns:
        if col not in ["w_name", "l_name"]:  # Skip already processed columns
            df[col] = df[col].str.strip()

    # Convert date columns
    if "t_date" in df.columns:
        # Try multiple date formats
        df["t_date"] = pd.to_datetime(
            df["t_date"], 
            format="%Y-%m-%d", 
            errors="coerce"
        )
        # If all failed, try alternative format
        if df["t_date"].isna().all():
            df["t_date"] = pd.to_datetime(
                df["t_date"], 
                format="%Y%m%d", 
                errors="coerce"
            )
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
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    
    # Strip whitespace from string columns (common pattern for tournament/player names)
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()
    
    logger.info(f"Loaded {len(df)} tournaments from {filepath.name}")
    return df


def load_all_data(data_paths: Dict[str, Path]) -> Dict[str, pd.DataFrame]:
    """
    Load datasets from provided paths. 'matches' is optional (may be missing in some repos).

    Args:
        data_paths: Dictionary of data file paths
                   Expected keys: 'players', 'yearly_performance', 'tournaments'.
                   Optional key: 'matches'

    Returns:
        Dictionary of loaded DataFrames. If 'matches' is missing, an empty DataFrame is returned
        under the 'matches' key and a warning is logged.
    """
    data = {
        "players": load_players_data(data_paths["players"]),
        "yearly_performance": load_yearly_performance_data(
            data_paths["yearly_performance"]
        ),
        "tournaments": load_tournaments_data(data_paths["tournaments"]),
    }

    # Matches may be optional; if provided, load, otherwise create empty DataFrame
    matches_path = data_paths.get("matches")
    if matches_path:
        try:
            data["matches"] = load_matches_data(matches_path)
        except FileNotFoundError:
            data["matches"] = pd.DataFrame()
            logger.warning(
                "Matches file was listed but could not be loaded; using empty DataFrame"
            )
    else:
        data["matches"] = pd.DataFrame()
        logger.info("No matches file provided; using empty DataFrame for 'matches'")

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
