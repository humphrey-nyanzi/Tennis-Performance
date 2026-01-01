"""
Tests for the centralized data loader and schema validator.
"""

import pandas as pd
from src.data import loader, schema


def test_manifest_loads():
    manifest = loader.load_manifest()
    assert isinstance(manifest, dict)
    assert "players" in manifest


def test_find_data_paths():
    paths = loader.find_data_paths()
    # Ensure required datasets (present in data/raw) are found
    assert set(paths.keys()) >= {"players", "tournaments", "yearly_performance"}
    # 'matches' is optional for this repository

    # All returned values should be Path-like with .exists()
    for p in paths.values():
        assert p.exists()


def test_load_all_data_and_schema_validation():
    data = loader.load_all_data()
    assert isinstance(data, dict)
    # Should contain DataFrames for required keys; 'matches' may be empty
    assert set(data.keys()) >= {
        "players",
        "matches",
        "tournaments",
        "yearly_performance",
    }

    # Check matches is a DataFrame (possibly empty)
    assert isinstance(data["matches"], pd.DataFrame)

    # Schema validation should return a tuple
    is_valid, issues = schema.validate_all(data)
    assert isinstance(is_valid, bool)
    assert isinstance(issues, list)
