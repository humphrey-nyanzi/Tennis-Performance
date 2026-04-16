"""
Central configuration module for Tennis Performance Analytics.

Responsibilities:
- Define project root and directory structure
- Manage dataset file paths
- Store global constants and settings
- Provide safe helper utilities for path resolution
"""

from pathlib import Path
import os
from typing import Optional

# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# =========================================================
# DIRECTORY STRUCTURE
# =========================================================

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = PROJECT_ROOT / "figures"
LOGS_DIR = PROJECT_ROOT / "logs"

# =========================================================
# DATA FILES (CANONICAL SOURCES)
# =========================================================

PLAYERS_CSV = RAW_DATA_DIR / "mod_players.csv"
MATCHES_CSV = RAW_DATA_DIR / "matches.csv"
TOURNAMENTS_CSV = RAW_DATA_DIR / "tournaments.csv"
PLAYERS_YEARLY_PERFORMANCE_CSV = RAW_DATA_DIR / "players_yearly_perfomance.csv"

# =========================================================
# STREAMLIT SETTINGS
# =========================================================

STREAMLIT_CACHE_TTL = 3600  # seconds
STREAMLIT_MAX_ENTRIES = 100

PAGE_TITLE = "Tennis Player Performance Dashboard"
PAGE_ICON = "🎾"

# =========================================================
# DOMAIN SETTINGS
# =========================================================

MIN_MATCHES_THRESHOLD = 50

DEFAULT_FIGURE_SIZE = (12, 7)
DEFAULT_COLORSCALE = "viridis"

DASHBOARD_THEME = "light"

# =========================================================
# LOGGING
# =========================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "app.log"

# =========================================================
# DIRECTORY SAFETY
# =========================================================

def ensure_directories_exist() -> None:
    """
    Create required directories if they do not exist.
    Safe to call at runtime.
    """
    directories = [
        DATA_DIR,
        RAW_DATA_DIR,
        INTERIM_DATA_DIR,
        PROCESSED_DATA_DIR,
        EXTERNAL_DATA_DIR,
        MODELS_DIR,
        REPORTS_DIR,
        FIGURES_DIR,
        LOGS_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# =========================================================
# DATA FILE UTILITIES
# =========================================================

def get_data_file_path(filename: str) -> Optional[Path]:
    """
    Resolve a dataset file from standard project locations.

    Search order:
    1. data/raw
    2. data/processed
    3. data/interim
    4. project root (legacy support)

    Returns:
        Path if found, else None
    """

    search_paths = [
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        INTERIM_DATA_DIR,
        PROJECT_ROOT,
    ]

    for base in search_paths:
        path = base / filename
        if path.exists():
            return path

    return None

# =========================================================
# VALIDATION HELPERS
# =========================================================

def validate_required_files() -> None:
    """
    Raise error early if required datasets are missing.
    Helps fail fast during deployment instead of runtime Streamlit crash.
    """

    required_files = [
        PLAYERS_CSV,
        MATCHES_CSV,
        TOURNAMENTS_CSV,
        PLAYERS_YEARLY_PERFORMANCE_CSV,
    ]

    missing = [str(f) for f in required_files if not f.exists()]

    if missing:
        raise FileNotFoundError(
            f"Missing required dataset files: {missing}"
        )