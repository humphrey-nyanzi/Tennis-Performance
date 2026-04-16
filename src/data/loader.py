"""
Centralized dataset loader for Tennis Performance Analytics.

Design goals:
- Deterministic file loading (no ambiguous fallback chains)
- Fail fast for required datasets
- Clean separation of concerns (no schema logic here)
- Compatible with Streamlit caching
"""

from pathlib import Path
import json
import logging
from typing import Dict, Optional

import pandas as pd

from src import config, dataset
from src.data import schema

logger = logging.getLogger(__name__)

# =========================================================
# MANIFEST (OPTIONAL OVERRIDE SYSTEM)
# =========================================================

DEFAULT_MANIFEST = {
    "players": config.PLAYERS_CSV.name,
    "matches": config.MATCHES_CSV.name,
    "tournaments": config.TOURNAMENTS_CSV.name,
    "yearly_performance": config.PLAYERS_YEARLY_PERFORMANCE_CSV.name,
}

MANIFEST_PATH = Path(__file__).resolve().parent / "manifest.json"

REQUIRED_KEYS = {"players", "tournaments", "yearly_performance"}
OPTIONAL_KEYS = {"matches"}


# =========================================================
# MANIFEST LOADING
# =========================================================

def load_manifest() -> Dict[str, str]:
    """
    Load dataset manifest if it exists.

    Returns:
        dict mapping dataset keys → filenames
    """
    if MANIFEST_PATH.exists():
        try:
            return json.loads(MANIFEST_PATH.read_text())
        except Exception as e:
            logger.warning(f"Invalid manifest.json, using defaults: {e}")

    return DEFAULT_MANIFEST


# =========================================================
# FILE RESOLUTION
# =========================================================

def resolve_paths(manifest: Dict[str, str]) -> Dict[str, Path]:
    """
    Convert manifest filenames into absolute paths using config rules.

    Returns:
        dict mapping dataset keys → Path
    """

    paths: Dict[str, Path] = {}
    missing_required = []

    for key, filename in manifest.items():
        path = config.get_data_file_path(filename)

        if path is None:
            if key in REQUIRED_KEYS:
                missing_required.append(filename)
            else:
                logger.warning(f"Optional dataset missing: {filename}")
            continue

        paths[key] = path

    if missing_required:
        raise FileNotFoundError(
            f"Missing required datasets: {missing_required}"
        )

    return paths


# =========================================================
# DATA LOADING CORE
# =========================================================

def load_all_data(data_paths: Optional[Dict[str, Path]] = None) -> Dict[str, pd.DataFrame]:
    """
    Load all datasets into memory.

    Flow:
    1. Resolve manifest (or use provided paths)
    2. Load CSVs
    3. Run schema validation (non-blocking warning)
    4. Return dict of DataFrames

    Returns:
        dict of {dataset_name: DataFrame}
    """

    if data_paths is None:
        manifest = load_manifest()
        data_paths = resolve_paths(manifest)

    data: Dict[str, pd.DataFrame] = {}

    for key, path in data_paths.items():
        try:
            data[key] = pd.read_csv(path)
        except Exception as e:
            raise RuntimeError(f"Failed to load {key} from {path}: {e}")

    # =====================================================
    # DOMAIN / SCHEMA VALIDATION (soft failure)
    # =====================================================

    try:
        is_valid, issues = schema.validate_all(data)

        if not is_valid:
            logger.warning(f"Schema validation issues detected: {issues}")

    except Exception as e:
        logger.warning(f"Schema validation failed (non-blocking): {e}")

    return data


# =========================================================
# STREAMLIT CACHE WRAPPER (OPTIONAL)
# =========================================================

def cached_load_all_data():
    """
    Streamlit-safe cached loader wrapper.

    Import this in app.py instead of load_all_data directly.
    """

    import streamlit as st

    @st.cache_resource
    def _load():
        config.ensure_directories_exist()
        return load_all_data()

    return _load()