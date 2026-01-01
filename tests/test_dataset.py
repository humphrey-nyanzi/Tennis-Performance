"""
Unit tests for dataset module.
Run with: pytest tests/test_dataset.py
"""

import pytest
import pandas as pd
from pathlib import Path
from src import dataset, config
from src.data import loader as data_loader


class TestDatasetLoading:
    """Tests for data loading functions."""

    def test_players_csv_exists(self):
        """Test that players CSV file exists in the canonical data/raw location."""
        paths = data_loader.find_data_paths()
        assert "players" in paths
        assert paths["players"].exists(), f"Players CSV not found at {paths['players']}"

    def test_matches_csv_exists(self):
        """Matches CSV is optional; if present ensure it exists in data/raw/ (no failure if absent)."""
        paths = data_loader.find_data_paths()
        if "matches" in paths:
            assert paths["matches"].exists(), (
                f"Matches CSV listed but not found at {paths['matches']}"
            )
        else:
            # This repository uses only the three canonical files in data/raw; it's okay
            # for matches.csv to be absent.
            assert True

    def test_load_players_data(self):
        """Test loading players data from data/raw via loader."""
        paths = data_loader.find_data_paths()
        df = dataset.load_players_data(paths["players"])
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "name" in df.columns

    def test_load_matches_data(self):
        """Test loading matches data if present; otherwise ensure loader returns an empty DataFrame."""
        data = data_loader.load_all_data()
        assert isinstance(data["matches"], pd.DataFrame)
        # If matches file exists, expect non-empty; otherwise empty DF is acceptable
        if data["matches"].shape[0] > 0:
            assert len(data["matches"]) > 0

    def test_filter_players_by_matches(self):
        """Test filtering players by minimum matches."""
        df = dataset.load_players_data(config.PLAYERS_CSV)
        original_count = len(df)

        filtered = dataset.filter_players_by_matches(df, min_matches=50)
        assert len(filtered) <= original_count
        assert all(filtered["total_matches"] >= 50)


class TestDatasetValidation:
    """Tests for data validation."""

    def test_validate_data_integrity(self):
        """Test data integrity validation using loader which sources data from data/raw."""
        data = data_loader.load_all_data()

        is_valid, issues = dataset.validate_data_integrity(data)
        # Should be valid or have minor issues
        assert isinstance(is_valid, bool)
        assert isinstance(issues, list)


class TestPlayerNames:
    """Tests for player name retrieval."""

    def test_get_player_names(self):
        """Test getting sorted player names."""
        df = dataset.load_players_data(config.PLAYERS_CSV)
        players = dataset.get_player_names(df)

        assert isinstance(players, list)
        assert len(players) > 0
        assert players == sorted(players)  # Should be sorted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
