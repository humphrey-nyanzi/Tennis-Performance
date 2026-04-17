"""
Data loading and validation module for Tennis Performance Analysis.
Handles CSV file loading with caching and validation.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict
import logging
from pandas.api.types import is_numeric_dtype

logger = logging.getLogger(__name__)

HIGH_CARDINALITY_CATEGORY_RATIO = 0.5
MAX_CATEGORY_UNIQUES = 10_000

# Explicit whitelist for safe category conversion
ALLOWED_CATEGORY_COLUMNS = {"surface", "t_level", "country"}


def _strip_object_columns(df: pd.DataFrame, exclude: Optional[set[str]] = None) -> pd.DataFrame:
    """Trim whitespace from string-like columns in place."""
    exclude = exclude or set()
    for col in df.select_dtypes(include=["object", "string"]).columns:
        if col in exclude:
            continue
        df[col] = df[col].astype("string").str.strip()
    return df


def _coerce_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert object columns that are mostly numeric into compact numeric dtypes."""
    for col in df.select_dtypes(include=["object", "string"]).columns:
        non_null = df[col].dropna()
        if non_null.empty:
            continue

        numeric = pd.to_numeric(non_null, errors="coerce")
        if (numeric.notna().mean() >= 0.95):
            converted = pd.to_numeric(df[col], errors="coerce")
            if converted.isna().sum() == df[col].isna().sum():
                df[col] = converted

    for col in df.columns:
        if is_numeric_dtype(df[col]):
            df[col] = pd.to_numeric(df[col], downcast="integer")
            if not is_numeric_dtype(df[col]) or str(df[col].dtype).startswith("float"):
                df[col] = pd.to_numeric(df[col], downcast="float")
    return df


def _convert_repeated_strings_to_category(df: pd.DataFrame) -> pd.DataFrame:
    """Convert repeated string columns to categoricals to reduce memory usage."""
    row_count = len(df)
    if row_count == 0:
        return df
    # Only convert whitelisted columns to category to avoid accidental
    # conversion of high-cardinality fields such as player names or ids.
    for col in df.select_dtypes(include=["object", "string"]).columns:
        if col not in ALLOWED_CATEGORY_COLUMNS:
            continue

        non_null = df[col].dropna()
        if non_null.empty:
            continue

        unique_count = non_null.nunique()
        unique_ratio = unique_count / len(non_null)
        if unique_count <= MAX_CATEGORY_UNIQUES and unique_ratio <= HIGH_CARDINALITY_CATEGORY_RATIO:
            df[col] = df[col].astype("category")
    return df


def optimize_dataframe_memory(df: pd.DataFrame) -> pd.DataFrame:
    """Reduce DataFrame memory footprint without changing displayed values."""
    optimized = df.copy()
    optimized = _coerce_numeric_columns(optimized)
    optimized = _convert_repeated_strings_to_category(optimized)
    return optimized


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

    df = pd.read_csv(filepath, low_memory=False)
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    # Strip whitespace from all string columns
    df = _strip_object_columns(df)

    df = optimize_dataframe_memory(df)

    # Validate required columns
    # Minimal required columns for identification; additional numeric fields
    # may be derived from the match dataset during processing.
    required_cols = ["name", "country"]
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

    df = pd.read_csv(filepath, low_memory=False)
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    
    # Strip whitespace from all string columns
    df = _strip_object_columns(df)
    
    df["t_year"] = pd.to_numeric(df["t_year"], errors="coerce")
    df = optimize_dataframe_memory(df)

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

    df = pd.read_csv(filepath, low_memory=False)
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    # Strip whitespace from player name columns
    if "w_name" in df.columns:
        df["w_name"] = df["w_name"].astype("string").str.strip()
    if "l_name" in df.columns:
        df["l_name"] = df["l_name"].astype("string").str.strip()

    # Strip whitespace from all other string columns
    for col in df.select_dtypes(include=["object", "string"]).columns:
        if col not in ["w_name", "l_name"]:  # Skip already processed columns
            df[col] = df[col].astype("string").str.strip()

    # Convert date columns using a single coercive parse. Log if parsing fails
    # at a high rate to avoid silent partial failures.
    if "t_date" in df.columns:
        df["t_date"] = pd.to_datetime(df["t_date"], errors="coerce")
        failure_rate = df["t_date"].isna().mean()
        if failure_rate > 0.2:
            logger.warning(f"High date parsing failure rate for matches.t_date: {failure_rate:.2f}")
    if "t_year" in df.columns:
        df["t_year"] = pd.to_numeric(df["t_year"], errors="coerce")

    df = optimize_dataframe_memory(df)

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

    df = pd.read_csv(filepath, low_memory=False)
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    
    # Strip whitespace from string columns (common pattern for tournament/player names)
    df = _strip_object_columns(df)
    df = optimize_dataframe_memory(df)
    
    logger.info(f"Loaded {len(df)} tournaments from {filepath.name}")
    return df


# NOTE: `load_all_data` was moved to src/data/loader.py to enforce a single
# loader entrypoint. Keep per-file loaders above (load_players_data, etc.)


def validate_data_integrity(data: Dict[str, pd.DataFrame]) -> None:
    """
    Validate data integrity and consistency.
    Logs any issues found but does not block execution.

    Args:
        data: Dictionary of loaded DataFrames
    """
    # Drop rows with null player names or countries
    players_before = len(data["players"])
    data["players"] = data["players"].dropna(subset=["name", "country"])
    players_after = len(data["players"])
    if players_before > players_after:
        logger.warning(f"Dropped {players_before - players_after} players with null name or country")

    # Check match data consistency
    matches = data["matches"]
    if "w_name" in matches.columns and "l_name" in matches.columns:
        if (matches["w_name"] == matches["l_name"]).any():
            logger.warning("Match data contains winner == loser")


def filter_players_by_matches(df: pd.DataFrame, matches_df: pd.DataFrame | None = None, min_matches: int = 50) -> pd.DataFrame:
    """
    Filter players by minimum number of matches. Preferred usage is to pass
    `matches_df` so match counts are derived from actual match records. If
    `matches_df` is None the function will fall back to a `total_matches`
    column on the players DataFrame (legacy behavior).
    """
    original_count = len(df)

    if matches_df is not None and not matches_df.empty:
        counts = pd.concat([matches_df["w_name"], matches_df["l_name"]]).value_counts()
        eligible = counts[counts >= min_matches].index
        df_filtered = df[df["name"].isin(eligible)].copy()
    else:
        if "total_matches" in df.columns:
            df_filtered = df[df["total_matches"] >= min_matches].copy()
        else:
            logger.warning("No matches_df provided and players DataFrame lacks 'total_matches'; returning original players DataFrame")
            df_filtered = df.copy()

    logger.info(f"Filtered players: {original_count} -> {len(df_filtered)} (min {min_matches} matches)")
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
