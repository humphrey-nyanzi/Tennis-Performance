"""Cached data transforms for Streamlit dashboard pages."""

import pandas as pd
import streamlit as st

from src import features


@st.cache_data(show_spinner=False)
def filter_matches_by_year(match_data: pd.DataFrame, start_year: int, end_year: int) -> pd.DataFrame:
    """Cache year-based match filtering."""
    return features.filter_matches_by_date_range(
        match_data,
        start_year=start_year,
        end_year=end_year,
    )


@st.cache_data(show_spinner=False)
def win_loss_stats(match_data: pd.DataFrame, groupby_col: str) -> pd.DataFrame:
    """Cache grouped win/loss statistics."""
    return features.create_win_loss_stats(match_data, groupby_col)


@st.cache_data(show_spinner=False)
def annual_win_loss_stats(match_data: pd.DataFrame, groupby_col: str) -> pd.DataFrame:
    """Cache annual grouped win/loss statistics."""
    return features.create_annual_win_loss_stats(match_data, groupby_col)


@st.cache_data(show_spinner=False)
def surface_rankings(match_data: pd.DataFrame, min_matches: int) -> pd.DataFrame:
    """Cache surface rankings."""
    return features.get_player_rankings_by_surface(match_data, min_matches=min_matches)


@st.cache_data(show_spinner=False)
def level_rankings(match_data: pd.DataFrame, min_matches: int) -> pd.DataFrame:
    """Cache tournament-level rankings."""
    return features.get_player_rankings_by_tournament_level(match_data, min_matches=min_matches)


@st.cache_data(show_spinner=False)
def top_players(match_data: pd.DataFrame, limit: int, min_matches: int) -> pd.DataFrame:
    """Cache overall top-player calculations."""
    return features.get_top_players_overall(match_data, limit=limit, min_matches=min_matches)


@st.cache_data(show_spinner=False)
def executive_metrics(match_data: pd.DataFrame, players_df: pd.DataFrame) -> dict:
    """Cache executive dashboard metrics."""
    return features.get_executive_dashboard_metrics(match_data, players_df)


@st.cache_data(show_spinner=False)
def yearly_match_trend(match_data: pd.DataFrame) -> pd.DataFrame:
    """Cache yearly match trend calculations."""
    return features.get_yearly_match_trend(match_data)
