"""
Unit tests for dataset module.
Run with: pytest tests/test_dataset.py
"""

import pytest
import pandas as pd
from pathlib import Path
from src import dataset, config


class TestDatasetLoading:
    """Tests for data loading functions."""

    def test_players_csv_exists(self):
        """Test that players CSV file exists."""
        assert config.PLAYERS_CSV.exists(), (
            f"Players CSV not found at {config.PLAYERS_CSV}"
        )

    def test_matches_csv_exists(self):
        """Test that matches CSV file exists."""
        assert config.MATCHES_CSV.exists(), (
            f"Matches CSV not found at {config.MATCHES_CSV}"
        )

    def test_load_players_data(self):
        """Test loading players data."""
        df = dataset.load_players_data(config.PLAYERS_CSV)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "name" in df.columns

    def test_load_matches_data(self):
        """Test loading matches data."""
        df = dataset.load_matches_data(config.MATCHES_CSV)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

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
        """Test data integrity validation."""
        data = {
            "players": dataset.load_players_data(config.PLAYERS_CSV),
            "yearly_performance": dataset.load_yearly_performance_data(
                config.PLAYERS_YEARLY_PERFORMANCE_CSV
            ),
            "matches": dataset.load_matches_data(config.MATCHES_CSV),
            "tournaments": dataset.load_tournaments_data(config.TOURNAMENTS_CSV),
        }

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
