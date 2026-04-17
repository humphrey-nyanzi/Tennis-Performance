"""
Tennis Performance Analysis Dashboard
Main Streamlit application entry point (production-safe architecture).
"""

import streamlit as st
import logging
import warnings
import sys
from pathlib import Path
import pandas as pd

# =========================================================
# PATH SAFETY (must happen BEFORE src imports)
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src import config
from src import dataset
from src.data.loader import cached_load_all_data, DataLoadError, DataValidationError

from dashboard.views import (
    home,
    player_analysis,
    tournament_analysis,
    trend_analysis,
    comparative_analysis,
    executive_dashboard,
)

# =========================================================
# INITIALIZATION (must happen before everything else)
# =========================================================

warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logging.getLogger("plotly").setLevel(logging.ERROR)
logging.getLogger("matplotlib").setLevel(logging.ERROR)

config.ensure_directories_exist()

# =========================================================
# STREAMLIT CONFIG (must be first Streamlit call)
# =========================================================

st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# DATA LOADING (single source of truth)
# =========================================================

def load_app_data():
    """
    Production-safe data loading layer. Uses the canonical loader
    `cached_load_all_data()` and then applies deterministic business rules:
    - Filter MATCHES globally by `MIN_MATCHES_THRESHOLD` and derive the players
      universe from the filtered matches (Option A).
    """
    try:
        raw = cached_load_all_data()

        # Extract fingerprint and raw datasets
        data_version = raw.get("data_version")
        raw_data = {k: v for k, v in raw.items() if k != "data_version"}

        # Extra validation (loader already enforces schema; double-check defensively)
        dataset.validate_data_integrity(raw_data)

        # Business rule: filter MATCHES globally and derive players from the
        # filtered matches so the players and matches universes are consistent.
        matches = raw_data["matches"].copy()

        # Compute player match counts across winners and losers
        counts = pd.concat([matches["w_name"], matches["l_name"]]).value_counts()
        active_players = counts[counts >= config.MIN_MATCHES_THRESHOLD].index.tolist()

        # Keep only matches where both players meet the threshold
        filtered_matches = matches[
            matches["w_name"].isin(active_players) & matches["l_name"].isin(active_players)
        ].copy()

        # Derive players DataFrame from canonical players list
        players_df = raw_data["players"].copy()
        players_df = players_df[players_df["name"].isin(active_players)].copy()

        processed = {
            "matches": filtered_matches,
            "players": players_df,
            "tournaments": raw_data["tournaments"],
            "yearly_performance": raw_data["yearly_performance"],
            "data_version": data_version,
            "_min_matches": config.MIN_MATCHES_THRESHOLD,
        }

        return processed

    except DataLoadError as e:
        logger.exception("Data loading error")
        raise RuntimeError(f"Critical data loading error: {e}")
    except DataValidationError as e:
        logger.exception("Data validation error")
        error_msg = f"Data validation failed:\n" + "\n".join(f"  - {issue}" for issue in e.issues)
        raise RuntimeError(error_msg)
    except Exception as e:
        logger.exception("Unexpected data loading error")
        raise RuntimeError(f"Data loading failed: {e}")


# =========================================================
# UI STYLES (isolated for clarity)
# =========================================================

def apply_styles():
    st.markdown(
        """
        <style>
        /* ===== BASE THEME ===== */
        :root {
            --tp-bg: #f6f1e8;
            --tp-ink: #19231f;
            --tp-muted: #53615b;
            --tp-green: #17352b;
            --tp-clay: #c96b3b;
            --tp-clay-strong: #ab5428;
        }

        html, body, [class*="css"] {
            font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
            color: var(--tp-ink);
        }

        /* ===== TENNIS COURT INSPIRED BACKGROUND ===== */
        [data-testid="stAppViewContainer"] {
            background: 
                repeating-linear-gradient(
                    45deg,
                    transparent,
                    transparent 120px,
                    rgba(201, 107, 59, 0.03) 120px,
                    rgba(201, 107, 59, 0.03) 240px
                ),
                repeating-linear-gradient(
                    -45deg,
                    transparent,
                    transparent 120px,
                    rgba(23, 53, 43, 0.02) 120px,
                    rgba(23, 53, 43, 0.02) 240px
                ),
                linear-gradient(
                    180deg, 
                    #fdfbf7 0%,
                    #f5ede2 25%,
                    #efe6d9 50%,
                    #e8dfcf 75%,
                    #e1d8c4 100%
                );
        }

        /* ===== MODERN TOP NAVIGATION BAR ===== */
        .nav-container {
            background: linear-gradient(135deg, #1a3829 0%, #0f2418 100%);
            padding: 1.5rem 1.5rem;
            border-radius: 0;
            box-shadow: 
                0 8px 24px rgba(0, 0, 0, 0.15),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            margin-bottom: 2rem;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }

        .nav-content {
            max-width: 1400px;
            margin: 0 auto;
        }

        .nav-title {
            color: #f0ebe2;
            font-size: 1.8rem;
            font-weight: 800;
            margin: 0 0 1rem 0;
            letter-spacing: 0.3px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        /* Navigation button styling */
        .nav-container button {
            background: rgba(255, 255, 255, 0.12) !important;
            color: #c9d5ce !important;
            border: 2px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            transition: all 0.3s cubic-bezier(0.23, 1, 0.320, 1) !important;
            padding: 0.9rem 1.5rem !important;
            white-space: nowrap !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        }

        .nav-container button:hover {
            background: rgba(201, 107, 59, 0.25) !important;
            color: #fce8dc !important;
            border-color: #d99060 !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 16px rgba(201, 107, 59, 0.25) !important;
        }

        /* Active button state - styled by checking if it should be highlighted */
        .stButton button:focus {
            background: linear-gradient(135deg, #c96b3b, #ab5428) !important;
            color: white !important;
            border-color: #c96b3b !important;
        }

        /* Mobile responsiveness */
        @media (max-width: 1024px) {
            .nav-container {
                padding: 0.6rem 1.2rem;
                margin-bottom: 1.2rem;
            }

            .nav-title {
                font-size: 1rem;
                margin-bottom: 0.6rem;
            }

            .nav-container button {
                padding: 0.6rem 1rem !important;
                font-size: 0.9rem !important;
            }
        }

        @media (max-width: 768px) {
            .nav-container {
                padding: 0.5rem 1rem;
                margin-bottom: 1rem;
            }

            .nav-title {
                font-size: 0.95rem;
                margin-bottom: 0.5rem;
            }

            .nav-container button {
                padding: 0.55rem 0.8rem !important;
                font-size: 0.85rem !important;
            }

            [data-testid="stHorizontalBlock"] {
                gap: 0.3rem !important;
            }
        }

        @media (max-width: 480px) {
            .nav-container {
                padding: 0.4rem 0.75rem;
                margin-bottom: 0.75rem;
            }

            .nav-title {
                font-size: 0.85rem;
            }

            .nav-container button {
                padding: 0.5rem 0.6rem !important;
                font-size: 0.75rem !important;
            }
        }

        /* Sidebar - minimal styling for secondary info */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f2418 0%, #1a3829 100%);
            box-shadow: inset -4px 0 12px rgba(0, 0, 0, 0.2);
        }

        [data-testid="stSidebar"] * {
            color: #e8dfd4;
        }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #d97e48 0%, #c96b3b 50%, #ab5428 100%);
            color: white;
            border-radius: 12px;
            font-weight: 700;
            border: none;
            transition: all 0.3s cubic-bezier(0.23, 1, 0.320, 1);
            box-shadow: 0 4px 12px rgba(201, 107, 59, 0.25);
            font-size: 1.05rem;
        }

        .stButton > button:hover {
            filter: brightness(1.08);
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(201, 107, 59, 0.35);
        }

        /* Metrics - enhanced with texture */
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, #fffefb 0%, #fdf9f0 100%);
            border-radius: 16px;
            border: 1px solid rgba(201, 107, 59, 0.12);
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }

        [data-testid="stMetric"]:hover {
            box-shadow: 0 6px 16px rgba(201, 107, 59, 0.15);
            border-color: rgba(201, 107, 59, 0.2);
            transform: translateY(-2px);
        }

        /* Hide Streamlit chrome */
        #MainMenu {display: none;}
        footer {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# MODERN TOP NAVIGATION
# =========================================================

def render_top_navigation():
    """Render a modern, responsive top navigation bar with buttons"""
    if "page" not in st.session_state:
        st.session_state.page = "home"
    
    # Ensure current page is valid
    valid_pages = ["home", "executive", "player", "comparative", "tournament", "trend"]
    if st.session_state.page not in valid_pages:
        st.session_state.page = "home"

    nav_items = [
        ("Home", "home"),
        ("Executive", "executive"),
        ("Player Analysis", "player"),
        ("Comparative", "comparative"),
        ("Tournaments", "tournament"),
        ("Trends", "trend"),
    ]

    # Navigation header with title and buttons in a clean layout
    st.markdown(
        '<div class="nav-container"><div class="nav-content">'
        '<div class="nav-title">🎾 Tennis Performance Analytics</div>',
        unsafe_allow_html=True,
    )
    
    # Create responsive navigation buttons
    nav_cols = st.columns(len(nav_items), gap="small")
    
    for col, (label, page_key) in zip(nav_cols, nav_items):
        with col:
            is_active = st.session_state.page == page_key
            
            if st.button(
                label,
                key=f"topnav_{page_key}",
                use_container_width=True,
                help=f"Go to {label}"
            ):
                st.session_state.page = page_key
                st.rerun()
    
    st.markdown('</div></div>', unsafe_allow_html=True)


# =========================================================
# PAGE ROUTER
# =========================================================

def render_page():
    page = st.session_state.page

    try:
        if page == "home":
            home.show()

        elif page == "executive":
            executive_dashboard.show()

        elif page == "player":
            player_analysis.show()

        elif page == "comparative":
            comparative_analysis.show()

        elif page == "tournament":
            tournament_analysis.show()

        elif page == "trend":
            trend_analysis.show()

    except Exception as e:
        logger.exception("Page rendering failed")
        st.error(f"Page error: {e}")


# =========================================================
# MAIN APP
# =========================================================

def main():
    apply_styles()

    # Load data first (critical path)
    if "data" not in st.session_state:
        try:
            with st.spinner("Loading data..."):
                st.session_state.data = load_app_data()

        except Exception as e:
            st.error(f"Startup failure: {e}")
            st.stop()

    # Render modern top navigation (consolidated header)
    render_top_navigation()
    st.divider()

    render_page()
    
    # Professional footer
    st.divider()
    st.markdown(
        """
        <div style="text-align: center; color: #888; padding: 40px 20px 20px 20px; font-size: 0.9rem; border-top: 1px solid #e0e0e0;">
            <p style="margin: 5px 0;"><strong>About this Analysis</strong></p>
            <p style="margin: 8px 0; line-height: 1.6; color: #777;">
                This dashboard presents descriptive analysis of professional tennis match data. 
                It examines player performance across surfaces, tournament levels, and head-to-head matchups, 
                with an emphasis on identifying patterns and trends in career trajectories.
            </p>
            <p style="margin: 15px 0 5px 0;">
                <a href="https://github.com/humphrey-nyanzi/Tennis-Performance" target="_blank" style="color: #c96b3b; text-decoration: none;">GitHub Repository</a> 
                · Built by <strong>Humphrey Nyanzi</strong>
            </p>
            <p style="margin: 3px 0; font-size: 0.85rem;">Data sourced from professional tennis records</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# ENTRY POINT SAFETY
# =========================================================

if __name__ == "__main__":
    main()