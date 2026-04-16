"""Cached data transforms for Streamlit dashboard pages."""

import pandas as pd
import streamlit as st
from typing import Optional

from src import features


@st.cache_data(show_spinner=False)
def filter_matches_by_year(match_data: pd.DataFrame, start_year: int, end_year: int, data_version: Optional[str] = None) -> pd.DataFrame:
    """Cache year-based match filtering."""
    df = match_data.copy()
    return features.filter_matches_by_date_range(
        df,
        start_year=start_year,
        end_year=end_year,
    )


@st.cache_data(show_spinner=False)
def win_loss_stats(match_data: pd.DataFrame, groupby_col: str, data_version: Optional[str] = None) -> pd.DataFrame:
    """Cache grouped win/loss statistics."""
    df = match_data.copy()
    return features.create_win_loss_stats(df, groupby_col)


@st.cache_data(show_spinner=False)
def annual_win_loss_stats(match_data: pd.DataFrame, groupby_col: str, data_version: Optional[str] = None) -> pd.DataFrame:
    """Cache annual grouped win/loss statistics."""
    df = match_data.copy()
    return features.create_annual_win_loss_stats(df, groupby_col)


@st.cache_data(show_spinner=False)
def surface_rankings(match_data: pd.DataFrame, min_matches: int, data_version: Optional[str] = None) -> pd.DataFrame:
    """Cache surface rankings."""
    df = match_data.copy()
    return features.get_player_rankings_by_surface(df, min_matches=min_matches)


@st.cache_data(show_spinner=False)
def level_rankings(match_data: pd.DataFrame, min_matches: int, data_version: Optional[str] = None) -> pd.DataFrame:
    """Cache tournament-level rankings."""
    df = match_data.copy()
    return features.get_player_rankings_by_tournament_level(df, min_matches=min_matches)


@st.cache_data(show_spinner=False)
def top_players(match_data: pd.DataFrame, limit: int, min_matches: int, data_version: Optional[str] = None) -> pd.DataFrame:
    """Cache overall top-player calculations."""
    df = match_data.copy()
    return features.get_top_players_overall(df, limit=limit, min_matches=min_matches)


@st.cache_data(show_spinner=False)
def executive_metrics(match_data: pd.DataFrame, players_df: pd.DataFrame, data_version: Optional[str] = None) -> dict:
    """Cache executive dashboard metrics."""
    md = match_data.copy()
    pdx = players_df.copy()
    return features.get_executive_dashboard_metrics(md, pdx)


@st.cache_data(show_spinner=False)
def yearly_match_trend(match_data: pd.DataFrame, data_version: Optional[str] = None) -> pd.DataFrame:
    """Cache yearly match trend calculations."""
    df = match_data.copy()
    return features.get_yearly_match_trend(df)
