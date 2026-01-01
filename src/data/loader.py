"""
Centralized data loader that locates dataset files (via manifest) and loads datasets
using the existing `src.dataset` helpers. This keeps file discovery in one place and
adds an integration point for schema validation.
"""

from pathlib import Path
import json
import logging
from typing import Dict, Optional

import pandas as pd

from src import config, dataset
from src.data import schema

logger = logging.getLogger(__name__)

DEFAULT_MANIFEST = {
    "players": config.PLAYERS_CSV.name,
    "matches": config.MATCHES_CSV.name,
    "tournaments": config.TOURNAMENTS_CSV.name,
    "yearly_performance": config.PLAYERS_YEARLY_PERFORMANCE_CSV.name,
}

MANIFEST_PATH = Path(__file__).parent / "manifest.json"


def load_manifest() -> Dict[str, str]:
    """Load the manifest mapping dataset keys to filenames.

    Falls back to reasonable defaults if the manifest file is missing or invalid.
    """
    if MANIFEST_PATH.exists():
        try:
            return json.loads(MANIFEST_PATH.read_text())
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning(f"Failed to parse manifest.json: {exc}")
    return DEFAULT_MANIFEST


def find_data_paths(manifest: Optional[Dict[str, str]] = None) -> Dict[str, Path]:
    """Return resolved Paths for the files listed in the manifest.

    Uses `src.config.get_data_file_path` which searches project root then processed/interim/raw.
    Raises FileNotFoundError if any expected file cannot be located.
    """
    manifest = manifest or load_manifest()
    paths: Dict[str, Path] = {}
    missing = []

    for key, filename in manifest.items():
        # Prefer files located in data/raw if present (project convention)
        raw_path = config.PROJECT_ROOT / "data" / "raw" / filename
        if raw_path.exists():
            paths[key] = raw_path
            continue

        # Fallback to general search (project root, processed, interim, raw)
        path = config.get_data_file_path(filename)
        if path:
            paths[key] = path
        else:
            missing.append((key, filename))

    # Treat players/tournaments/yearly_performance as required; other files (e.g., matches)
    # are optional to support repos that don't include full match data yet.
    required = {"players", "tournaments", "yearly_performance"}
    missing_required = [k for k, f in missing if k in required]
    if missing_required:
        raise FileNotFoundError(f"Missing required data files: {missing_required}")

    # If any non-required files are missing, log a warning and continue
    optional_missing = [m for m in missing if m[0] not in required]
    if optional_missing:
        logger.warning(f"Optional data files not found: {optional_missing}")

    return paths


def load_all_data(
    data_paths: Optional[Dict[str, Path]] = None,
) -> Dict[str, pd.DataFrame]:
    """Load all datasets and run lightweight schema validation.

    Returns the dict of DataFrames as provided by `src.dataset.load_all_data`.
    Logs a warning if schema validation finds issues but does not raise (to be forgiving
    for now).
    """
    if data_paths is None:
        data_paths = find_data_paths()

    # reuse existing dataset loaders (keeps behaviour consistent)
    data = dataset.load_all_data(data_paths)

    is_valid, issues = schema.validate_all(data)
    if not is_valid:
        logger.warning(f"Schema validation issues: {issues}")

    return data
