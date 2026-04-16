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

# Professional CSS styling - tennis editorial theme with strong contrast
st.markdown(
    """
    <style>
    :root {
        --tp-bg: #f6f1e8;
        --tp-bg-soft: #fbf8f2;
        --tp-surface: rgba(255, 252, 246, 0.9);
        --tp-surface-strong: #fffdf8;
        --tp-ink: #19231f;
        --tp-muted: #53615b;
        --tp-line: rgba(25, 35, 31, 0.12);
        --tp-shadow: 0 18px 42px rgba(20, 38, 31, 0.08);
        --tp-green: #17352b;
        --tp-green-2: #214838;
        --tp-clay: #c96b3b;
        --tp-clay-strong: #ab5428;
        --tp-gold: #d9b15f;
        --tp-focus: #2f6a52;
        --tp-heading: "Georgia", "Times New Roman", serif;
        --tp-body: "Aptos", "Segoe UI", "Trebuchet MS", sans-serif;
    }

    html, body, [class*="css"] {
        font-family: var(--tp-body);
        color: var(--tp-ink);
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at top left, rgba(217, 177, 95, 0.18), transparent 28%),
            radial-gradient(circle at top right, rgba(201, 107, 59, 0.12), transparent 24%),
            linear-gradient(180deg, var(--tp-bg-soft) 0%, var(--tp-bg) 42%, #efe5d8 100%);
    }

    .main {
        padding-top: 1.25rem;
    }

    [data-testid="stHeader"] {
        background: linear-gradient(90deg, rgba(23, 53, 43, 0.96) 0%, rgba(33, 72, 56, 0.9) 100%);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(17, 38, 30, 0.98) 0%, rgba(27, 60, 46, 0.98) 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNavItems"],
    [data-testid="stSidebarUserContent"] [href] {
        display: none !important;
    }

    [data-testid="stSidebar"] * {
        color: #f6efe2;
    }

    h1, h2, h3 {
        font-family: var(--tp-heading);
        letter-spacing: -0.02em;
        color: var(--tp-green);
    }

    p, li, label, .stMarkdown, .stCaption {
        color: var(--tp-ink);
    }

    hr {
        border: none;
        border-top: 1px solid var(--tp-line);
        margin: 1.6rem 0 2rem;
    }

    .tp-hero {
        background:
            linear-gradient(135deg, rgba(255, 250, 242, 0.9), rgba(249, 241, 228, 0.88)),
            linear-gradient(120deg, rgba(201, 107, 59, 0.12), rgba(23, 53, 43, 0.08));
        border: 1px solid rgba(23, 53, 43, 0.1);
        border-radius: 24px;
        box-shadow: var(--tp-shadow);
        padding: 1.5rem 1.75rem;
        position: relative;
        overflow: hidden;
    }

    .tp-hero::after {
        content: "";
        position: absolute;
        inset: auto -4rem -4rem auto;
        width: 13rem;
        height: 13rem;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(217, 177, 95, 0.26) 0%, transparent 70%);
    }

    .tp-kicker {
        text-transform: uppercase;
        letter-spacing: 0.18em;
        font-size: 0.72rem;
        font-weight: 700;
        color: var(--tp-clay-strong);
        margin-bottom: 0.35rem;
    }

    .tp-title {
        font-family: var(--tp-heading);
        color: var(--tp-green);
        font-size: clamp(2rem, 3vw, 3.1rem);
        line-height: 1.05;
        margin: 0;
    }

    .tp-subtitle {
        color: var(--tp-muted);
        margin-top: 0.55rem;
        font-size: 1rem;
        max-width: 48rem;
    }

    .stButton > button,
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--tp-clay) 0%, var(--tp-clay-strong) 100%);
        color: #fff8f2;
        border: 1px solid rgba(123, 54, 19, 0.18);
        border-radius: 999px;
        font-weight: 700;
        letter-spacing: 0.01em;
        box-shadow: 0 10px 24px rgba(171, 84, 40, 0.18);
        padding: 0.72rem 1.2rem;
        transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        filter: brightness(1.03);
        box-shadow: 0 14px 28px rgba(171, 84, 40, 0.24);
    }

    .stButton > button:focus,
    .stDownloadButton > button:focus,
    button:focus, a:focus, input:focus, select:focus, textarea:focus {
        outline: 3px solid rgba(47, 106, 82, 0.26);
        outline-offset: 2px;
        box-shadow: 0 0 0 2px rgba(255, 248, 239, 0.9);
    }

    [data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(255, 253, 248, 0.95) 0%, rgba(248, 243, 235, 0.92) 100%);
        border: 1px solid rgba(23, 53, 43, 0.08);
        border-radius: 20px;
        padding: 1rem 1.05rem;
        box-shadow: 0 10px 24px rgba(20, 38, 31, 0.06);
    }

    [data-testid="stMetricLabel"] p {
        color: var(--tp-muted);
        font-weight: 700;
        letter-spacing: 0.02em;
    }

    [data-testid="stMetricValue"] {
        color: var(--tp-green);
        font-family: var(--tp-heading);
    }

    [data-testid="stDataFrame"],
    .stPlotlyChart,
    [data-testid="stTable"] {
        background: var(--tp-surface);
        border: 1px solid rgba(23, 53, 43, 0.08);
        border-radius: 20px;
        box-shadow: 0 12px 30px rgba(20, 38, 31, 0.06);
        padding: 0.2rem;
    }

    .stAlert {
        border: 1px solid rgba(23, 53, 43, 0.08);
        border-left: 5px solid var(--tp-clay);
        border-radius: 18px;
        box-shadow: 0 10px 22px rgba(20, 38, 31, 0.05);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.45rem;
        background: rgba(255, 252, 246, 0.72);
        border: 1px solid rgba(23, 53, 43, 0.08);
        padding: 0.4rem;
        border-radius: 18px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 14px;
        font-weight: 700;
        color: var(--tp-muted);
        min-height: 2.6rem;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(23, 53, 43, 0.96), rgba(33, 72, 56, 0.96));
        color: #fff6ed;
    }

    .stRadio [role="radiogroup"] label,
    .stSelectbox label,
    .stMultiSelect label,
    .stSlider label {
        color: inherit;
        font-weight: 700;
    }

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    .stSelectbox [data-baseweb="select"],
    .stMultiSelect [data-baseweb="select"] {
        background: rgba(255, 252, 246, 0.96);
        border-radius: 14px;
    }

    [data-testid="stSidebar"] .stRadio [role="radiogroup"] > label {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        margin-bottom: 0.45rem;
        padding: 0.45rem 0.65rem;
        transition: background 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
    }

    [data-testid="stSidebar"] .stRadio [role="radiogroup"] > label:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(217, 177, 95, 0.28);
        transform: translateX(2px);
    }

    [data-testid="stSidebar"] .stCaption {
        color: rgba(246, 239, 226, 0.72);
    }

    [data-testid="stFooterContent"] {
        color: var(--tp-muted);
        text-align: center;
        padding: 2rem 0;
    }
    
    /* ===== MOBILE RESPONSIVENESS & ACCESSIBILITY ===== */
    @media (max-width: 768px) {
        .stButton > button {
            width: 100%;
            padding: 0.85rem 1rem !important;
            font-size: 1rem !important;
            min-height: 48px;
        }

        .stColumn {
            min-width: 100% !important;
        }

        .tp-hero {
            padding: 1.25rem;
        }
    }

    @media (max-width: 480px) {
        .stButton > button, .stSelectbox input, .stTextInput input {
            padding: 0.75rem !important;
            min-height: 48px !important;
        }
    }

    button, input, select, textarea {
        min-height: 48px !important;
        min-width: 48px !important;
    }

    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
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
            f"""
            <section class="tp-hero">
                <div class="tp-kicker">Professional Tennis Intelligence</div>
                <h1 class="tp-title">{config.PAGE_ICON} {config.PAGE_TITLE}</h1>
                <p class="tp-subtitle">
                    Explore player form, tournament patterns, surface strengths, and matchup dynamics
                    through a cleaner, executive-style analytics experience.
                </p>
            </section>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # Initialize page state
    if "page" not in st.session_state:
        st.session_state.page = "executive"

    # Sidebar Navigation - SINGLE RADIO BUTTON ONLY
    with st.sidebar:
        st.markdown("## 🏠 Home")
        st.divider()
        
        page_options = {
            "📊 Executive Dashboard": "executive",
            "🎾 Player Analysis": "player",
            "⚖️ Comparative Analysis": "comparative",
            "🏆 Tournament Analysis": "tournament",
            "📈 Trend Analysis": "trend",
        }
        current_label = next(
            (label for label, page_key in page_options.items() if page_key == st.session_state.page),
            "📊 Executive Dashboard",
        )
        
        selected_page = st.radio(
            "Select Page",
            options=list(page_options.keys()),
            index=list(page_options.keys()).index(current_label),
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
