"""
Constants and enumerations for the Tennis Performance Analysis project.
"""

# Tournament levels (ATP/WTA)
TOURNAMENT_LEVELS = {
    "G": "Grand Slam",
    "M": "Masters 1000",
    "A": "ATP Tour",
    "C": "Challenger",
    "S": "Satellite/ITF",
    "F": "Tour Finals",
    "D": "Davis Cup",
    "P": "Premier",
    "PM": "Premier Mandatory",
    "I": "International",
}

# Surfaces
SURFACES = {
    "Clay": "Clay",
    "Hard": "Hard Court",
    "Grass": "Grass",
    "Carpet": "Carpet",
}

# Best of values
BEST_OF_VALUES = {3: "Best of 3", 5: "Best of 5"}

# Hand dominance
HAND_DOMINANCE = {"R": "Right", "L": "Left", "U": "Unknown"}

# Winner entry codes
ENTRY_CODES = {
    "WC": "Wild Card",
    "Q": "Qualifier",
    "LL": "Lucky Loser",
    "PR": "Protected Ranking",
    "ITF": "ITF Entry",
}

# Match rounds
ROUNDS = [
    "1R",
    "2R",
    "3R",
    "4R",
    "QF",
    "SF",
    "F",
    "RR",
    "BR",
    "W",
]

# Default minimum matches threshold
MIN_MATCHES_THRESHOLD = 50

# Column categories
PLAYER_STATS_EXCLUDE = [
    "f_year",
    "l_year",
    "country",
    "hand",
    "gender",
    "birthdate",
    "wins",
    "losses",
    "wlr",
    "career_duration",
    "total_matches",
    "serve_game_won%",
    "break_points_saved%",
    "breakpoints_permatch",
    "ace_dominance",
    "svpt",
    "1stIn",
    "name",
]

# Performance metrics
PERCENTAGE_METRICS = [
    "break_points_saved%",
    "serve_game_won%",
    "wlr",
    "ace_dominance",
]

# Annual filter categories
ANNUAL_FILTERS = ["surface", "t_level", "best_of"]

# Column name mappings for better readability
COLUMN_DISPLAY_NAMES = {
    "w_name": "Winner",
    "l_name": "Loser",
    "t_name": "Tournament",
    "t_year": "Year",
    "t_month": "Month",
    "t_date": "Date",
    "surface": "Surface",
    "t_level": "Level",
    "best_of": "Best Of",
    "round": "Round",
    "minutes": "Duration (min)",
    "w_ace": "Winner Aces",
    "l_ace": "Loser Aces",
    "w_df": "Winner Double Faults",
    "l_df": "Loser Double Faults",
    "wlr": "Win %",
}
