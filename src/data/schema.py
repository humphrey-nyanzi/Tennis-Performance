"""
Lightweight schema validation for dataset DataFrames.
This is intentionally minimal (no external dependencies) and checks for required
columns and a few basic type constraints. It returns (is_valid, issues_list)
so callers can decide how to handle problems (warn vs raise).
"""

from typing import Dict, List, Tuple

import pandas as pd

# Required columns by dataset key
REQUIRED_COLUMNS = {
    "players": ["name", "country", "total_matches", "wins", "losses"],
    "matches": ["w_name", "l_name", "t_year", "t_name"],
    "tournaments": ["name", "surface"],
    "yearly_performance": ["player", "t_year", "win", "loss"],
}


def validate_df(df: pd.DataFrame, required: List[str]) -> Tuple[bool, List[str]]:
    """Validate a single DataFrame for required columns and simple type checks.

    Returns (is_valid, issues)
    """
    issues: List[str] = []

    if df is None:
        return False, ["DataFrame is None"]

    # Check required columns
    missing = [c for c in required if c not in df.columns]
    if missing:
        issues.append(f"Missing columns: {missing}")

    # Simple type checks
    if "t_year" in required and "t_year" in df.columns:
        try:
            # Ensure t_year can be coerced to numeric at least for many rows
            coerced = pd.to_numeric(df["t_year"], errors="coerce")
            if coerced.isna().all():
                issues.append("Column 't_year' could not be parsed as numeric")
        except Exception:
            issues.append("Error parsing 't_year' column")

    return (len(issues) == 0), issues


def validate_all(data: Dict[str, pd.DataFrame]) -> Tuple[bool, List[str]]:
    """Validate all expected datasets and return aggregate result and issues list."""
    issues: List[str] = []
    is_all_valid = True

    for key, required in REQUIRED_COLUMNS.items():
        df = data.get(key)
        valid, ds_issues = validate_df(df, required)
        if not valid:
            is_all_valid = False
            issues.append({key: ds_issues})

    return is_all_valid, issues
