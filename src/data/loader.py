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
import hashlib

import pandas as pd

from src import config, dataset

logger = logging.getLogger(__name__)


# =========================================================
# Required dataset contract (strict)
# =========================================================

REQUIRED_DATASETS = {"players", "matches", "tournaments", "yearly_performance"}

DEFAULT_MANIFEST = {
    "players": config.PLAYERS_CSV.name,
    "matches": config.MATCHES_CSV.name,
    "tournaments": config.TOURNAMENTS_CSV.name,
    "yearly_performance": config.PLAYERS_YEARLY_PERFORMANCE_CSV.name,
}

MANIFEST_PATH = Path(__file__).resolve().parent / "manifest.json"


# =========================================================
# Exceptions
# =========================================================

class DataLoadError(RuntimeError):
    pass


class DataValidationError(RuntimeError):
    def __init__(self, issues):
        super().__init__("Data validation failed")
        self.issues = issues


# =========================================================
# MANIFEST LOADING
# =========================================================


def load_manifest() -> Dict[str, str]:
    """
    Load dataset manifest if it exists. Falls back to DEFAULT_MANIFEST.
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
    Will fail fast if any REQUIRED_DATASETS are not resolvable.
    """

    paths: Dict[str, Path] = {}
    missing_required = []

    for key in REQUIRED_DATASETS:
        filename = manifest.get(key) or DEFAULT_MANIFEST.get(key)
        if not filename:
            missing_required.append(key)
            continue

        path = config.get_data_file_path(filename)
        if path is None:
            missing_required.append(filename)
            continue

        paths[key] = path

    if missing_required:
        raise DataLoadError(f"Missing required datasets: {missing_required}")

    return paths


# =========================================================
# DATA LOADING CORE
# =========================================================


def load_all_data(data_paths: Optional[Dict[str, Path]] = None) -> Dict[str, pd.DataFrame]:
    """
    Load all datasets into memory using the single source of truth in `dataset`.

    This function performs strict, fail-fast loading: missing required files or
    schema validation failures raise explicit exceptions.
    """

    if data_paths is None:
        manifest = load_manifest()
        data_paths = resolve_paths(manifest)

    data: Dict[str, pd.DataFrame] = {}

    try:
        data["players"] = dataset.load_players_data(data_paths["players"])
        data["tournaments"] = dataset.load_tournaments_data(data_paths["tournaments"])
        data["yearly_performance"] = dataset.load_yearly_performance_data(
            data_paths["yearly_performance"]
        )
        data["matches"] = dataset.load_matches_data(data_paths["matches"])

    except FileNotFoundError as e:
        raise DataLoadError(str(e)) from e
    except Exception as e:
        raise DataLoadError(f"Failed to load datasets: {e}") from e

    # Strict schema validation (block on failure)
    is_valid, issues = dataset.validate_data_integrity(data)
    if not is_valid:
        raise DataValidationError(issues)

    return data


# =========================================================
# STREAMLIT CACHE WRAPPER
# =========================================================


def cached_load_all_data() -> Dict[str, pd.DataFrame]:
    """
    Streamlit-cached loader. Ensures directories exist, loads datasets, and
    attaches a deterministic `data_version` fingerprint to the returned dict.
    """
    import streamlit as st
    
    @st.cache_resource
    def _load() -> Dict[str, pd.DataFrame]:
        config.ensure_directories_exist()

        manifest = load_manifest()
        data_paths = resolve_paths(manifest)

        data = load_all_data(data_paths)

        # Compute deterministic fingerprint from manifest + file metadata
        m = hashlib.sha256()
        m.update(json.dumps(manifest, sort_keys=True).encode())
        for key in sorted(REQUIRED_DATASETS):
            p = data_paths[key]
            try:
                stat = p.stat()
                m.update(str(p.as_posix()).encode())
                m.update(str(int(stat.st_mtime)).encode())
                m.update(str(stat.st_size).encode())
            except Exception:
                # If stat fails for some reason, still continue with path string
                m.update(str(p.as_posix()).encode())

        data_version = m.hexdigest()
        # Attach version metadata (reserved key)
        data["data_version"] = data_version

        return data
    
    return _load()