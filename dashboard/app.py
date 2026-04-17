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
            font-family: "Segoe UI", sans-serif;
            color: var(--tp-ink);
        }

        [data-testid="stAppViewContainer"] {
            background: linear-gradient(180deg, #fbf8f2 0%, #f6f1e8 100%);
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #11261e 0%, #1b3c2e 100%);
        }

        [data-testid="stSidebar"] * {
            color: #f6efe2;
        }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, var(--tp-clay), var(--tp-clay-strong));
            color: white;
            border-radius: 999px;
            font-weight: 700;
            border: none;
        }

        .stButton > button:hover {
            filter: brightness(1.05);
        }

        /* Metrics */
        [data-testid="stMetric"] {
            background: #fffdf8;
            border-radius: 16px;
            border: 1px solid rgba(0,0,0,0.08);
        }

        /* Hide Streamlit chrome */
        #MainMenu {display: none;}
        footer {visibility: hidden;}
        
        /* Ensure sidebar is visible */
        [data-testid="stSidebar"] {
            visibility: visible !important;
            display: block !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

def render_sidebar():
    if "page" not in st.session_state:
        st.session_state.page = "executive"

    page_map = {
        "📊 Executive Dashboard": "executive",
        "🎾 Player Analysis": "player",
        "⚖️ Comparative Analysis": "comparative",
        "🏆 Tournament Analysis": "tournament",
        "📈 Trend Analysis": "trend",
    }

    with st.sidebar:
        st.markdown("## Navigation")
        st.divider()

        selected = st.radio(
            "Page",
            list(page_map.keys()),
            index=list(page_map.values()).index(st.session_state.page),
            label_visibility="collapsed",
        )

        st.session_state.page = page_map[selected]

        st.divider()
        st.caption("Tennis Analytics v0.2.0")


# =========================================================
# PAGE ROUTER
# =========================================================

def render_page():
    page = st.session_state.page

    try:
        if page == "executive":
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
# HEADER
# =========================================================

def render_header():
    col1, col2, col3 = st.columns([0.5, 3, 0.5])

    with col2:
        st.markdown(
            f"""
            <div style="
                padding: 20px;
                border-radius: 16px;
                background: linear-gradient(135deg, #fffaf2, #f9f1e4);
                border: 1px solid rgba(0,0,0,0.08);
            ">
                <h1 style="margin:0;">
                    {config.PAGE_ICON} {config.PAGE_TITLE}
                </h1>
                <p style="color:#555;">
                    Tennis performance intelligence for player and tournament analysis
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


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

    
    render_sidebar()
    render_header()
    st.divider()

    render_page()


# =========================================================
# ENTRY POINT SAFETY
# =========================================================

if __name__ == "__main__":
    main()