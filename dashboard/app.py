"""
Tennis Performance Analysis Dashboard
Main Streamlit application entry point.
"""

import streamlit as st
import logging
import warnings
from pathlib import Path
import sys

# Suppress warnings for cleaner UI
warnings.filterwarnings("ignore")
logging.getLogger("plotly").setLevel(logging.ERROR)
logging.getLogger("matplotlib").setLevel(logging.ERROR)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import config, dataset
from src.data import loader as data_loader
from dashboard.pages import (
    player_analysis,
    tournament_analysis,
    trend_analysis,
    executive_dashboard,
    comparative_analysis,
)

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
    /* Main app styling - CRITICAL: Set text color to dark */
    .main {
        padding-top: 1rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #1a1a1a;
    }
    
    /* Ensure all text is readable */
    * {
        color: #1a1a1a !important;
    }
    
    /* Header styling */
    [data-testid="stHeader"] {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
    }
    
    /* Title styling */
    h1 {
        color: #1e3c72 !important;
        font-weight: 700;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    h2, h3 {
        color: #2a5298 !important;
    }
    
    p, li, span, div {
        color: #1a1a1a !important;
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
    
    .metric-card * {
        color: white !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white !important;
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
    
    [data-testid="stSidebar"] * {
        color: #1a1a1a !important;
    }
    
    /* Section header styling */
    .section-header {
        color: #1e3c72 !important;
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
        color: #1a1a1a !important;
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
    
    /* ===== MOBILE RESPONSIVENESS & ACCESSIBILITY ===== */
    
    /* Responsive font sizing */
    @media (max-width: 768px) {
        h1 {
            font-size: 1.75rem !important;
        }
        
        h2 {
            font-size: 1.25rem !important;
        }
        
        h3 {
            font-size: 1rem !important;
        }
        
        p, span, div {
            font-size: 0.95rem !important;
        }
        
        /* Responsive button sizing */
        .stButton > button {
            width: 100%;
            padding: 0.85rem 1rem !important;
            font-size: 1rem !important;
            min-height: 48px;
        }
        
        /* Responsive input sizing */
        .stSelectbox input, .stTextInput input {
            min-height: 44px !important;
        }
        
        /* Full-width columns on mobile */
        .stColumn {
            min-width: 100% !important;
        }
        
        /* Sidebar adjustments */
        [data-testid="stSidebar"] {
            width: 100% !important;
        }
        
        /* Metric cards responsive */
        .metric-card {
            width: 100% !important;
            margin: 0.5rem 0 !important;
        }
    }
    
    @media (max-width: 480px) {
        h1 {
            font-size: 1.5rem !important;
        }
        
        h2 {
            font-size: 1.1rem !important;
        }
        
        p, span, div {
            font-size: 0.9rem !important;
        }
        
        /* Extra padding for touch targets */
        .stButton > button, .stSelectbox input, .stTextInput input {
            padding: 0.75rem !important;
            min-height: 48px !important;
        }
    }
    
    /* Improved touch targets for accessibility (WCAG AA compliance) */
    button, input, select, textarea {
        min-height: 48px !important;
        min-width: 48px !important;
    }
    
    /* Keyboard focus visibility for accessibility */
    button:focus, a:focus, input:focus, select:focus, textarea:focus {
        outline: 3px solid #2a5298;
        outline-offset: 2px;
        border-radius: 0.25rem;
    }
    
    /* High contrast mode support */
    @media (prefers-contrast: more) {
        body {
            text-shadow: none !important;
        }
        
        button {
            border: 2px solid #000;
        }
    }
    
    /* Reduced motion support for accessibility */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .main {
            background: #1a1a1a !important;
            color: #ffffff !important;
        }
        
        p, span, div {
            color: #ffffff !important;
        }
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

    # Initialize page state
    if "page" not in st.session_state:
        st.session_state.page = "executive"

    # Sidebar Navigation - SINGLE RADIO BUTTON ONLY
    with st.sidebar:
        st.markdown("## 🎾 Dashboard Navigation")
        st.divider()
        
        page_options = {
            "📊 Executive Dashboard": "executive",
            "🎾 Player Analysis": "player",
            "⚖️ Comparative Analysis": "comparative",
            "🏆 Tournament Analysis": "tournament",
            "📈 Trend Analysis": "trend",
        }
        
        selected_page = st.radio(
            "Select Page",
            options=list(page_options.keys()),
            label_visibility="collapsed",
        )
        
        st.session_state.page = page_options[selected_page]
        
        st.divider()
        st.caption("v0.2.0 | Tennis Performance Analytics")

    # Display selected page
    try:
        if st.session_state.page == "executive":
            executive_dashboard.show()
        elif st.session_state.page == "player":
            player_analysis.show()
        elif st.session_state.page == "comparative":
            comparative_analysis.show()
        elif st.session_state.page == "tournament":
            tournament_analysis.show()
        elif st.session_state.page == "trend":
            trend_analysis.show()
    except Exception as e:
        st.error(f"❌ Error displaying page: {str(e)}")
        st.info("Please try refreshing the page or selecting another page.")
        logger.exception(f"Page rendering error: {str(e)}")


if __name__ == "__main__":
    main()
