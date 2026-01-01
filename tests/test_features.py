"""
Tests for features module.
Run with: pytest tests/test_features.py
"""

import pytest
import pandas as pd
from src import features


class TestWinLossStats:
    """Tests for win/loss statistics."""

    def test_create_win_loss_stats(self):
        """Test creating win/loss statistics."""
        match_data = pd.DataFrame(
            {
                "w_name": ["Player A", "Player A", "Player B"],
                "l_name": ["Player B", "Player C", "Player A"],
                "surface": ["Clay", "Hard", "Clay"],
            }
        )

        stats = features.create_win_loss_stats(match_data, "surface")

        assert len(stats) > 0
        assert "wlr" in stats.columns
        assert "total_matches" in stats.columns

    def test_create_annual_win_loss_stats(self):
        """Test creating annual win/loss statistics."""
        match_data = pd.DataFrame(
            {
                "w_name": ["Player A", "Player A", "Player B"],
                "l_name": ["Player B", "Player C", "Player A"],
                "surface": ["Clay", "Hard", "Clay"],
                "t_year": [2020, 2020, 2021],
            }
        )

        stats = features.create_annual_win_loss_stats(match_data, "surface")

        assert len(stats) > 0
        assert "wlr" in stats.columns
        assert "t_year" in stats.columns


class TestHeadToHead:
    """Tests for head-to-head functions."""

    def test_get_head_to_head(self):
        """Test getting head-to-head match history."""
        match_data = pd.DataFrame(
            {
                "w_name": ["A", "B", "A"],
                "l_name": ["B", "A", "B"],
                "t_date": pd.date_range("2020-01-01", periods=3),
                "t_name": ["Wimbledon", "French", "Wimbledon"],
            }
        )

        h2h = features.get_head_to_head(match_data, "A", "B")

        assert len(h2h) == 3
        assert all((h2h["w_name"] == "A") | (h2h["w_name"] == "B"))

    def test_calculate_player_h2h_record(self):
        """Test calculating head-to-head record."""
        match_data = pd.DataFrame(
            {
                "w_name": ["A", "B", "A"],
                "l_name": ["B", "A", "B"],
            }
        )

        record = features.calculate_player_h2h_record(match_data, "A", "B")

        assert record["player"] == "A"
        assert record["opponent"] == "B"
        assert record["wins"] == 2
        assert record["losses"] == 1


class TestSurfaceStats:
    """Tests for surface-based statistics."""

    def test_get_player_surface_stats(self):
        """Test getting player surface statistics."""
        match_data = pd.DataFrame(
            {
                "w_name": ["A", "A", "B"],
                "l_name": ["B", "C", "A"],
                "surface": ["Clay", "Hard", "Clay"],
            }
        )

        stats = features.get_player_surface_stats(match_data, "A")

        assert len(stats) > 0
        assert "wlr" in stats.columns
        assert "surface" in stats.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
