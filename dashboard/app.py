"""
Tennis Performance Analysis Dashboard
Main Streamlit application entry point.
"""

import streamlit as st
import logging
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import config, dataset
from src.data import loader as data_loader
from dashboard.pages import player_analysis, tournament_analysis, trend_analysis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_data():
    """Load all required datasets with caching using centralized loader."""
    try:
        config.ensure_directories_exist()

        # Load all data using central loader which prefers data/raw/ and runs schema checks
        data = data_loader.load_all_data()

        # Validate integrity (domain-level checks)
        is_valid, issues = dataset.validate_data_integrity(data)
        if not is_valid:
            logger.warning(f"Data integrity issues: {issues}")

        # Filter players by minimum matches
        data["players"] = dataset.filter_players_by_matches(
            data["players"], min_matches=config.MIN_MATCHES_THRESHOLD
        )

        logger.info("Data loaded successfully")
        return data

    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise


def main():
    """Main dashboard application."""

    # Load data
    if "data" not in st.session_state:
        try:
            with st.spinner("Loading data..."):
                st.session_state.data = load_data()
            st.success("Data loaded successfully!")
        except Exception as e:
            st.error(f"Failed to load data: {str(e)}")
            st.info(
                "Please ensure all CSV files are in the `data/raw/` directory (single source of truth)"
            )
            return

    # Main header
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.title(f"{config.PAGE_ICON} {config.PAGE_TITLE}")

    st.divider()

    # Navigation
    nav_options = ["Player Analysis", "Tournament Analysis", "Trend Analysis"]

    # Use columns for better layout
    nav_col1, nav_col2, nav_col3 = st.columns(3)

    with nav_col1:
        if st.button("🎾 Player Analysis", use_container_width=True):
            st.session_state.page = "player"

    with nav_col2:
        if st.button("🏆 Tournament Analysis", use_container_width=True):
            st.session_state.page = "tournament"

    with nav_col3:
        if st.button("📊 Trend Analysis", use_container_width=True):
            st.session_state.page = "trend"

    st.divider()

    # Initialize page state
    if "page" not in st.session_state:
        st.session_state.page = "player"

    # Display selected page
    if st.session_state.page == "player":
        player_analysis.show()
    elif st.session_state.page == "tournament":
        tournament_analysis.show()
    elif st.session_state.page == "trend":
        trend_analysis.show()

    # Footer
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col2:
        st.caption(
            f"Tennis Performance Analysis Dashboard v{config.__version__ if hasattr(config, '__version__') else '0.1.0'}"
        )


if __name__ == "__main__":
    main()
