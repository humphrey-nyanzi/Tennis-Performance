"""
Configuration module for Tennis Performance Analysis project.
Manages paths, settings, and environment variables.
"""

import os
from pathlib import Path
from typing import Optional


from pathlib import Path

# Get project root (repo root)
BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data" / "raw"

PLAYERS_CSV = DATA_DIR / "mod_players.csv"
PLAYERS_YEARLY_PERFORMANCE_CSV = DATA_DIR / "players_yearly_perfomance.csv"
MATCHES_CSV = DATA_DIR / "matches.csv"
TOURNAMENTS_CSV = DATA_DIR / "tournaments.csv"


# CSV file paths
# Prefer canonical files under data/raw/ when available; fall back to project root for backwards compatibility
def _data_raw_or_root(filename: str):
    raw_path = PROJECT_ROOT / "data" / "raw" / filename
    if raw_path.exists():
        return raw_path
    return PROJECT_ROOT / filename


PLAYERS_CSV = _data_raw_or_root("mod_players.csv")
PLAYERS_YEARLY_PERFORMANCE_CSV = _data_raw_or_root("players_yearly_perfomance.csv")
MATCHES_CSV = _data_raw_or_root("matches.csv")
TOURNAMENTS_CSV = _data_raw_or_root("tournaments.csv")

# Streamlit cache settings
STREAMLIT_CACHE_TTL = 3600  # 1 hour in seconds
STREAMLIT_MAX_ENTRIES = 100

# Data processing settings
MIN_MATCHES_THRESHOLD = 50  # Minimum matches for player analysis

# Visualization settings
DEFAULT_FIGURE_SIZE = (12, 7)
DEFAULT_COLORSCALE = "viridis"

# Dashboard settings
DASHBOARD_THEME = "light"
PAGE_TITLE = "Tennis Player Performance Dashboard"
PAGE_ICON = "🎾"

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = PROJECT_ROOT / "logs" / "app.log"


def get_data_file_path(filename: str) -> Optional[Path]:
    """
    Get the path to a data file, checking in the project root first,
    then in processed/interim/raw directories.

    Args:
        filename: Name of the data file (e.g., 'matches.csv')

    Returns:
        Path object if file exists, None otherwise
    """
    # Check project root first
    root_path = PROJECT_ROOT / filename
    if root_path.exists():
        return root_path

    # Check subdirectories
    for data_dir in [PROCESSED_DATA_DIR, INTERIM_DATA_DIR, RAW_DATA_DIR]:
        full_path = data_dir / filename
        if full_path.exists():
            return full_path

    return None


def ensure_directories_exist():
    """Create necessary directories if they don't exist."""
    directories = [
        DATA_DIR,
        RAW_DATA_DIR,
        INTERIM_DATA_DIR,
        PROCESSED_DATA_DIR,
        EXTERNAL_DATA_DIR,
        MODELS_DIR,
        REPORTS_DIR,
        FIGURES_DIR,
        PROJECT_ROOT / "logs",
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
