# 🎾 Tennis Performance Analysis Dashboard

A comprehensive analysis and visualization platform for ATP/WTA tennis player and tournament performance data. Built with Python, Streamlit, and modular architecture for scalability and maintainability.

## ✨ Features

### Player Analysis
- Individual player statistics and performance metrics
- Career streaks (winning/losing) tracking
- Performance trends over time
- Player-to-player comparisons
- Win/loss analysis by surface, tournament level, and year
- Head-to-head match records

### Tournament Analysis
- Tournament statistics and information
- Yearly participation trends
- Top winners at each tournament
- Surface distribution analysis
- Head-to-head matchups by tournament
- Tournament-to-tournament comparison

### Trend Analysis
- Winner vs. loser performance metrics
- Macro trends across all matches
- Surface distribution over time
- Yearly match statistics
- Historical pattern analysis

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/h-frey/Tennis-Performance.git
cd Tennis-Performance

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Running the Dashboard

```bash
# Start the Streamlit app
streamlit run dashboard/app.py
```

The dashboard will open at `http://localhost:8501`

## 📁 Project Structure

```
Tennis Performance/
├── src/                    # Core library modules
│   ├── config.py          # Configuration & paths
│   ├── constants.py       # Enums & constants
│   ├── dataset.py         # Data loading & validation
│   ├── features.py        # Feature engineering
│   ├── utils.py           # Utility functions
│   ├── plots.py           # Visualizations
│   └── modeling/          # (Reserved for ML models)
│
├── dashboard/             # Streamlit application
│   ├── app.py             # Main entry point
│   ├── pages/             # Application pages
│   │   ├── player_analysis.py
│   │   ├── tournament_analysis.py
│   │   └── trend_analysis.py
│   └── components/        # Reusable UI components
│
├── tests/                 # Unit tests
│   ├── test_dataset.py
│   ├── test_features.py
│   └── test_utils.py
│
├── notebooks/             # Jupyter notebooks for exploration
│
├── data/                  # Data files
│   ├── raw/              # Original data
│   ├── interim/          # Intermediate data
│   ├── processed/        # Final datasets
│   └── external/         # External sources
│
├── reports/              # Generated reports and figures
│
├── docs/                 # Documentation
│   ├── DATA_DICTIONARY.txt
│   └── PROJECT_BRIEF.md
│
├── README.md             # This file
├── DEVELOPMENT.md        # Developer guide
├── requirements.txt      # Project dependencies
└── pyproject.toml        # Project configuration
```

## 📚 Core Modules

### `src/config.py`
Centralized configuration for paths, settings, and environment management.

**Key Functions:**
- `get_data_file_path()` - Locate data files
- `ensure_directories_exist()` - Create necessary directories

### `src/dataset.py`
Data loading and validation functionality.

**Key Functions:**
- `load_players_data()` - Load player statistics
- `load_matches_data()` - Load match records
- `load_all_data()` - Load all datasets
- `validate_data_integrity()` - Check data quality
- `filter_players_by_matches()` - Filter by match count

### `src/features.py`
Feature engineering and aggregation functions.

**Key Functions:**
- `create_win_loss_stats()` - Win/loss statistics
- `create_annual_win_loss_stats()` - Annual aggregations
- `get_head_to_head()` - H2H match history
- `get_player_surface_stats()` - Surface breakdown
- `get_tournament_player_winners()` - Top tournament winners

### `src/utils.py`
Helper utilities for calculations and formatting.

**Key Functions:**
- `calculate_win_loss_ratio()` - Win percentage calculation
- `calculate_streaks()` - Winning/losing streaks
- `format_percentage()` - Format as percentage
- `validate_player_exists()` - Validation helpers

### `src/plots.py`
Visualization functions using Plotly and Matplotlib.

**Key Functions:**
- `create_bar_comparison()` - Group bar charts
- `create_line_plot()` - Line charts with trends
- `create_pie_chart()` - Distribution charts
- `create_multiline_comparison()` - Multi-series plots

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_dataset.py -v

# Run with coverage report
pytest tests/ -v --cov=src
```

## 🔧 Development

For development guidelines, detailed architecture information, and extending the project, see [DEVELOPMENT.md](DEVELOPMENT.md).

## 📊 Data Files

The project uses the following data files:

| File | Description |
|------|-------------|
| `mod_players.csv` | Player statistics |
| `players_yearly_perfomance.csv` | Yearly performance metrics |
| `tournaments.csv` | Tournament information |
| `matches.csv` | Individual match records |

See [docs/DATA_DICTIONARY.txt](docs/DATA_DICTIONARY.txt) for detailed column descriptions.

## 🛠️ Technical Stack

- **Python 3.12+** - Core language
- **Streamlit** - Dashboard framework
- **Pandas** - Data manipulation
- **Plotly** - Interactive visualizations
- **Matplotlib/Seaborn** - Statistical plots
- **Pytest** - Testing framework

## 🎯 Usage Examples

### Load and Analyze Data

```python
from src import config, dataset, features

# Load data
data = dataset.load_all_data({
    'players': config.PLAYERS_CSV,
    'matches': config.MATCHES_CSV,
    'tournaments': config.TOURNAMENTS_CSV,
    'yearly_performance': config.PLAYERS_YEARLY_PERFORMANCE_CSV,
})

# Get player statistics
stats = features.create_win_loss_stats(data['matches'], 'surface')

# Create visualization
fig = plots.create_bar_comparison(
    stats,
    x='surface',
    y='wlr',
    title='Win Rate by Surface'
)
```

### Player Comparison

```python
from src import features

# Head-to-head record
h2h = features.get_head_to_head(data['matches'], 'Player1', 'Player2')
record = features.calculate_player_h2h_record(data['matches'], 'Player1')
```

## 📈 Roadmap

- [ ] Add statistical testing and significance
- [ ] Implement prediction models
- [ ] Add player ranking predictions
- [ ] Export to PDF/Excel reports
- [ ] Data refresh automation
- [ ] Enhanced caching mechanisms
- [ ] Mobile-responsive design
- [ ] Advanced filtering options

## 🐛 Troubleshooting

### Data Files Not Found
Ensure all CSV files are in the project root or update paths in `src/config.py`.

### Streamlit Port Already in Use
```bash
streamlit run dashboard/app.py --server.port 8502
```

### Import Errors
Make sure the virtual environment is activated and all dependencies are installed:
```bash
pip install -r requirements.txt
```

## 📝 License

This project is licensed under the MIT License - see [LICENCE](LICENCE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📧 Contact

For questions or suggestions, please reach out through GitHub issues.

---

**Last Updated:** January 2026  
**Python Version:** 3.12+  
**Status:** Production Ready ✅
