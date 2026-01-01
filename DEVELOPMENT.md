# Development Guide

## Architecture Overview

### Modular Design

The project follows a **clean architecture** pattern with clear separation of concerns:

```
┌─────────────────────────────────────┐
│     Dashboard Layer (UI)            │
│  dashboard/app.py + pages/          │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│    Business Logic Layer             │
│  src/features.py, utils.py, plots.py│
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│      Data Layer                     │
│  src/dataset.py, config.py          │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│    Data Files (CSV)                 │
│  data/ directory                    │
└─────────────────────────────────────┘
```

### Core Modules

#### `src/config.py` (Configuration)
- Centralized paths and settings
- Environment configuration
- Directory management
- Database-like access to project structure

#### `src/constants.py` (Constants)
- Tournament levels, surfaces, rounds
- Entry codes and enumerations
- Default thresholds
- Display name mappings

#### `src/dataset.py` (Data I/O)
- CSV file loading with validation
- Data integrity checking
- Type conversions and cleaning
- Filtering and aggregation

#### `src/features.py` (Feature Engineering)
- Win/loss statistics calculation
- Annual aggregations
- Head-to-head analysis
- Surface and tournament level breakdown

#### `src/utils.py` (Utilities)
- Mathematical calculations (streaks, ratios)
- Formatting utilities
- Validation functions
- Safe value retrieval

#### `src/plots.py` (Visualization)
- Plotly interactive charts
- Matplotlib static plots
- Comparison visualizations
- Statistical plots

### Dashboard Structure

#### `dashboard/app.py`
Main Streamlit application with:
- Session state management
- Data caching
- Page routing
- Header and navigation

#### `dashboard/pages/`
Three analytical pages:
- **player_analysis.py** - Player metrics and comparisons
- **tournament_analysis.py** - Tournament statistics
- **trend_analysis.py** - Macro trends and patterns

#### `dashboard/components/`
Reusable UI components:
- Metric cards
- Section headers
- Display helpers
- Input widgets

## Development Workflow

### Adding a New Feature

1. **Implement in `src/`** - Write pure Python functions
2. **Test** - Add unit tests in `tests/`
3. **Use in Dashboard** - Import in `dashboard/pages/`
4. **Document** - Add docstrings and update README

### Adding a New Dashboard Page

1. Create `dashboard/pages/new_page.py`
2. Implement `show()` function
3. Import in `dashboard/app.py`
4. Add to navigation
5. Test thoroughly

### Example: Adding Win Rate by Year

```python
# In src/features.py
def get_yearly_win_rates(match_data: pd.DataFrame, player: str) -> pd.DataFrame:
    """Get yearly win rates for a player."""
    player_matches = match_data[
        (match_data['w_name'] == player) | 
        (match_data['l_name'] == player)
    ].copy()
    
    player_matches['result'] = (player_matches['w_name'] == player).astype(int)
    
    yearly = player_matches.groupby('t_year').agg({
        'result': ['sum', 'count']
    }).reset_index()
    
    yearly.columns = ['year', 'wins', 'total']
    yearly['wlr'] = (yearly['wins'] / yearly['total']).round(3)
    
    return yearly

# In tests/test_features.py
def test_get_yearly_win_rates():
    from src import features
    df = pd.DataFrame({...})
    result = features.get_yearly_win_rates(df, 'Player1')
    assert len(result) > 0
    assert 'wlr' in result.columns

# In dashboard/pages/player_analysis.py
yearly_rates = features.get_yearly_win_rates(match_data, player)
fig = plots.create_line_plot(yearly_rates, x='year', y='wlr')
st.plotly_chart(fig)
```

## Code Style & Best Practices

### Type Hints
Always include type hints for clarity:

```python
def analyze_data(df: pd.DataFrame, threshold: int = 50) -> dict:
    """Analyze data with given threshold."""
    pass
```

### Docstrings
Use comprehensive docstrings for all functions:

```python
def calculate_streaks(matches: pd.DataFrame) -> dict:
    """
    Calculate win/loss streaks for a player.
    
    Args:
        matches: DataFrame with 'result' column (1=win, 0=loss)
    
    Returns:
        dict with longest_win_streak, longest_losing_streak, current_streak
    
    Example:
        >>> df = pd.DataFrame({'result': [1, 1, 0, 1]})
        >>> streaks = calculate_streaks(df)
    """
```

### Error Handling
Validate inputs and handle errors gracefully:

```python
def load_player_data(filepath: Path) -> pd.DataFrame:
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    df = pd.read_csv(filepath)
    
    required = ['name', 'wins', 'losses']
    if not all(col in df.columns for col in required):
        raise ValueError(f"Missing required columns: {required}")
    
    return df
```

### Testing
Write tests for all non-trivial functions:

```python
class TestFeatures:
    def test_create_win_loss_stats(self):
        data = pd.DataFrame({
            'w_name': ['A', 'A', 'B'],
            'l_name': ['B', 'C', 'A'],
            'surface': ['Clay', 'Hard', 'Clay']
        })
        
        stats = features.create_win_loss_stats(data, 'surface')
        assert 'wlr' in stats.columns
        assert len(stats) > 0
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific file
pytest tests/test_dataset.py -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test
pytest tests/test_features.py::test_create_win_loss_stats -v
```

## Performance Optimization

### Caching

Use Streamlit's caching to improve performance:

```python
@st.cache_data
def load_data():
    return dataset.load_all_data({...})
```

### Data Filtering

Apply filters early to reduce data size:

```python
# Good - filter first
filtered = df[df['t_year'] >= 2020]
stats = features.analyze(filtered)

# Inefficient - process all then filter
stats = features.analyze(df)
stats = stats[stats['t_year'] >= 2020]
```

## Extending the Project

### Adding a New Data Source

1. Create loader in `src/dataset.py`:
```python
def load_custom_data(filepath: Path) -> pd.DataFrame:
    """Load custom data with validation."""
    pass
```

2. Register in `config.py`:
```python
CUSTOM_CSV = PROJECT_ROOT / "custom_data.csv"
```

3. Use in features or dashboard

### Adding New Visualizations

1. Create in `src/plots.py`:
```python
def create_custom_chart(data: pd.DataFrame, **kwargs) -> go.Figure:
    """Create custom chart."""
    pass
```

2. Use in dashboard pages:
```python
from src import plots
fig = plots.create_custom_chart(data)
st.plotly_chart(fig)
```

### Adding ML Models

1. Use `src/modeling/` directory
2. Create `train.py` for training
3. Create `predict.py` for inference
4. Integrate in dashboard or features

## Troubleshooting

### Import Errors
```bash
# Ensure src is a package
ls src/__init__.py  # Should exist

# Install in development mode
pip install -e .
```

### Data Issues
```python
from src import dataset

# Validate data
is_valid, issues = dataset.validate_data_integrity(data)
print(issues)
```

### Streamlit Issues
```bash
# Clear cache
streamlit cache clear

# Check logs
streamlit run dashboard/app.py --logger.level=debug
```

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and test
pytest tests/

# Commit with clear messages
git commit -m "Add new feature: description"

# Push to remote
git push origin feature/new-feature

# Create pull request on GitHub
```

## Project Stats

- **Python Files:** 26
- **Lines of Code:** 2,655+
- **Test Coverage:** Core modules
- **Type Hint Coverage:** 100%
- **Documentation:** Comprehensive

## Resources

- [Streamlit Docs](https://docs.streamlit.io)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Plotly Documentation](https://plotly.com/python/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

## Common Commands

```bash
# Development
streamlit run dashboard/app.py          # Run app
pytest tests/ -v                        # Run tests
black src/ dashboard/ tests/            # Format code
flake8 src/ dashboard/ tests/           # Lint code

# Git
git status                              # Check status
git add .                               # Stage changes
git commit -m "message"                 # Commit
git push origin main                    # Push to remote
git pull origin main                    # Pull from remote
```

---

**For more information, see README.md for usage guide and project overview.**
