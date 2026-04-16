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
from dashboard.pages import player_analysis, tournament_analysis, trend_analysis, executive_dashboard

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

# Professional CSS styling - Tennis themed with modern design
st.markdown(
    """
    <style>
    /* Main app styling */
    .main {
        padding-top: 1rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header styling */
    [data-testid="stHeader"] {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
    }
    
    /* Title styling */
    h1 {
        color: #1e3c72;
        font-weight: 700;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    h2, h3 {
        color: #2a5298;
    }
    
    /* Divider styling */
    hr {
        border: 1px solid #2a5298;
        margin: 2rem 0;
    }
    
    /* Metric card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        color: white;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        padding: 0.75rem 1.5rem;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #2a5298 0%, #1e3c72 100%);
        box-shadow: 0 4px 12px rgba(30, 60, 114, 0.3);
        transform: translateY(-2px);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f5f7fa 0%, #e9ecef 100%);
    }
    
    /* Section header styling */
    .section-header {
        color: #1e3c72;
        font-weight: 700;
        padding: 1rem 0;
        border-bottom: 3px solid #2a5298;
        margin-bottom: 1.5rem;
    }
    
    /* Stats table styling */
    [data-testid="stDataFrame"] {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Info box styling */
    .stAlert {
        border-radius: 0.5rem;
        border-left: 5px solid #2a5298;
    }
    
    /* Tab styling */
    [role="tab"] {
        font-weight: 600;
    }
    
    /* Select styling */
    .stSelectbox, .stSlider {
        background-color: white;
    }
    
    /* Plotly charts styling */
    .plotly-graph-div {
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Footer styling */
    [data-testid="stFooterContent"] {
        color: #666;
        text-align: center;
        padding: 2rem 0;
    }
    
    /* Metric styling */
    .metric-container {
        background: white;
        border-radius: 0.75rem;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 5px solid #2a5298;
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
            with st.spinner("🔄 Loading data..."):
                st.session_state.data = load_data()
            st.success("✅ Data loaded successfully!")
        except Exception as e:
            st.error(f"❌ Failed to load data: {str(e)}")
            st.info(
                "Please ensure all CSV files are in the `data/raw/` directory (single source of truth)"
            )
            return

    # Main header with professional styling
    col1, col2, col3 = st.columns([0.5, 3, 0.5])
    with col2:
        st.markdown(
            f"<h1 style='text-align: center; color: #1e3c72;'>{config.PAGE_ICON} {config.PAGE_TITLE}</h1>",
            unsafe_allow_html=True
        )

    st.divider()

    # Professional navigation with better styling
    st.markdown("<div style='margin-bottom: 1rem;'><bold>Navigation:</bold></div>", unsafe_allow_html=True)
    
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

    with nav_col1:
        if st.button("📊 Executive Dashboard", use_container_width=True, key="btn_exec"):
            st.session_state.page = "executive"

    with nav_col2:
        if st.button("🎾 Player Analysis", use_container_width=True, key="btn_player"):
            st.session_state.page = "player"

    with nav_col3:
        if st.button("🏆 Tournament Analysis", use_container_width=True, key="btn_tournament"):
            st.session_state.page = "tournament"

    with nav_col4:
        if st.button("📈 Trend Analysis", use_container_width=True, key="btn_trend"):
            st.session_state.page = "trend"

    st.divider()

    # Initialize page state
    if "page" not in st.session_state:
        st.session_state.page = "executive"

    # Display selected page
    if st.session_state.page == "executive":
        executive_dashboard.show()
    elif st.session_state.page == "player":
        player_analysis.show()
    elif st.session_state.page == "tournament":
        tournament_analysis.show()
    elif st.session_state.page == "trend":
        trend_analysis.show()

    # Professional footer
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col2:
        st.caption(
            f"🎾 Tennis Performance Analysis Dashboard | v0.2.0 | Professional Grade Analytics"
        )


if __name__ == "__main__":
    main()
