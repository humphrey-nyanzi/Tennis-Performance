"""
Unit tests for utility functions.
Run with: pytest tests/test_utils.py
"""

import pytest
import pandas as pd
from src import utils


class TestCalculations:
    """Tests for calculation functions."""

    def test_calculate_win_loss_ratio(self):
        """Test win/loss ratio calculation."""
        assert utils.calculate_win_loss_ratio(10, 10) == 50.0
        assert utils.calculate_win_loss_ratio(75, 25) == 75.0
        assert utils.calculate_win_loss_ratio(0, 0) == 0.0

    def test_format_percentage(self):
        """Test percentage formatting."""
        result = utils.format_percentage(75.555, decimals=1)
        assert result == "75.6%"
        assert isinstance(result, str)

    def test_format_duration(self):
        """Test duration formatting."""
        result = utils.format_duration(120.5)
        assert "min" in result
        assert isinstance(result, str)

    def test_safe_get_value(self):
        """Test safe value retrieval."""
        series = pd.Series([1, 2, 3])
        assert utils.safe_get_value(series, 0) == "1"
        assert utils.safe_get_value(series, 5) == "N/A"
        assert utils.safe_get_value(series, -1, default="DEFAULT") == "DEFAULT"


class TestStreaks:
    """Tests for streak calculation."""

    def test_calculate_streaks_empty(self):
        """Test streak calculation with empty DataFrame."""
        df = pd.DataFrame()
        streaks = utils.calculate_streaks(df)

        assert streaks["longest_win_streak"] is None
        assert streaks["longest_losing_streak"] is None

    def test_calculate_streaks_all_wins(self):
        """Test streak calculation with all wins."""
        df = pd.DataFrame(
            {"result": [1, 1, 1, 1], "t_date": pd.date_range("2020-01-01", periods=4)}
        )

        streaks = utils.calculate_streaks(df)
        assert streaks["longest_win_streak"] == 4
        assert streaks["current_streak_type"] == "Winning"

    def test_calculate_streaks_alternating(self):
        """Test streak calculation with alternating wins/losses."""
        df = pd.DataFrame(
            {
                "result": [1, 0, 1, 0, 1],
                "t_date": pd.date_range("2020-01-01", periods=5),
            }
        )

        streaks = utils.calculate_streaks(df)
        assert streaks["longest_win_streak"] == 1
        assert streaks["longest_losing_streak"] == 1


class TestDataFrameUtilities:
    """Tests for DataFrame utility functions."""

    def test_get_numeric_columns(self):
        """Test getting numeric columns."""
        df = pd.DataFrame({"name": ["A", "B"], "value": [1, 2], "score": [3.5, 4.5]})

        numeric = utils.get_numeric_columns(df)
        assert "value" in numeric
        assert "score" in numeric
        assert "name" not in numeric

    def test_round_numeric(self):
        """Test numeric rounding."""
        df = pd.DataFrame({"value": [1.234567, 2.345678], "name": ["A", "B"]})

        rounded = utils.round_numeric(df, decimals=2)
        assert rounded["value"].iloc[0] == 1.23
        assert rounded["name"].iloc[0] == "A"


class TestValidation:
    """Tests for validation functions."""

    def test_validate_player_exists(self):
        """Test player existence validation."""
        df = pd.DataFrame({"name": ["Federer", "Nadal", "Djokovic"]})

        assert utils.validate_player_exists(df, "Federer") is True
        assert utils.validate_player_exists(df, "Unknown") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
