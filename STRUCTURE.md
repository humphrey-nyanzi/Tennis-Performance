# Tennis Performance Analysis

## Project Structure

This project follows a modular architecture for data analysis and visualization.

### Directory Structure

```
src/
├── __init__.py          # Package initialization
├── config.py            # Configuration and paths management
├── constants.py         # Constants and enumerations
├── dataset.py           # Data loading and validation
├── features.py          # Feature engineering functions
├── utils.py             # Utility functions
├── plots.py             # Visualization functions
└── modeling/            # (Optional) Machine learning models

dashboard/
├── __init__.py
├── app.py               # Main Streamlit application
├── components/          # Reusable UI components
│   └── __init__.py
└── pages/               # Page modules
    ├── __init__.py
    ├── player_analysis.py
    ├── tournament_analysis.py
    └── trend_analysis.py

tests/
├── __init__.py
├── test_dataset.py      # Dataset tests
├── test_utils.py        # Utility tests
└── test_features.py     # Feature tests

data/
├── raw/                 # Original, immutable data
├── interim/             # Intermediate transformed data
├── processed/           # Final datasets for analysis
└── external/            # External data sources

models/                  # Trained models and predictions

reports/
├── figures/             # Generated visualizations
└── README.md            # Analysis reports

notebooks/              # Jupyter notebooks for exploration
```

## Module Documentation

### `src/config.py`
Centralized configuration management:
- Project paths and directories
- Data file locations
- Streamlit configuration
- Cache settings
- Directory creation utilities

**Key Functions:**
- `get_data_file_path()` - Find data files in project
- `ensure_directories_exist()` - Create missing directories

### `src/constants.py`
Enumeration and constant values:
- Tournament levels (Grand Slam, Masters, etc.)
- Surfaces, rounds, entry codes
- Default thresholds and settings
- Column name mappings for display

### `src/dataset.py`
Data loading and validation:
- Load CSV files with validation
- Validate data integrity
- Filter players by match count
- Get unique player/tournament names

**Key Functions:**
- `load_players_data()` - Load player statistics
- `load_matches_data()` - Load match records
- `load_tournaments_data()` - Load tournament info
- `load_all_data()` - Load all datasets together
- `validate_data_integrity()` - Check data quality

### `src/features.py`
Feature engineering and aggregations:
- Win/loss statistics by category
- Annual performance aggregations
- Head-to-head comparisons
- Surface and tournament level analysis

**Key Functions:**
- `create_win_loss_stats()` - Stats grouped by column
- `create_annual_win_loss_stats()` - Yearly breakdown
- `get_head_to_head()` - H2H match history
- `get_player_surface_stats()` - Surface breakdown

### `src/utils.py`
Utility and helper functions:
- Calculations (win ratios, streaks)
- Formatting (percentages, durations)
- Data validation
- Safe value retrieval
- DataFrame utilities

**Key Functions:**
- `calculate_win_loss_ratio()` - Win percentage
- `calculate_streaks()` - Winning/losing streaks
- `format_percentage()` - Format to %
- `validate_player_exists()` - Check player in data

### `src/plots.py`
Visualization utilities:
- Plotly charts (bar, line, pie)
- Matplotlib/Seaborn plots
- Comparison visualizations
- Heatmaps and distributions

**Key Functions:**
- `create_bar_comparison()` - Group bar charts
- `create_line_plot()` - Line charts with trends
- `create_pie_chart()` - Distribution charts
- `create_heatmap_correlation()` - Correlation matrices

## Running the Dashboard

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Or using the make script
python make.py install
```

### Running the Application
```bash
# Start the dashboard
streamlit run dashboard/app.py

# Or using the make script
python make.py run
```

The dashboard will be available at `http://localhost:8501`

## Pages Overview

### Player Analysis
- Player metrics and statistics
- Performance trends over time
- Win/loss analysis by surface, tournament level
- Comparisons between players
- Head-to-head records
- Streak analysis

### Tournament Analysis
- Tournament information and statistics
- Yearly participation trends
- Top winners at tournament
- Surface distribution
- Head-to-head matchups at specific tournaments

### Trend Analysis
- Winner vs. loser performance metrics
- Macro trends across all matches
- Surface distribution over time
- Yearly statistics and distributions

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src

# Run specific test file
pytest tests/test_dataset.py -v

# Or using make script
python make.py test
```

## Code Quality

```bash
# Format code
python make.py format

# Lint code
python make.py lint

# Type check
python make.py type-check

# Run all checks
python make.py check-all
```

## Development Workflow

1. **Data Exploration**: Work in Jupyter notebooks first
2. **Feature Development**: Move functions to `src/features.py`
3. **Testing**: Write tests in `tests/` directory
4. **Dashboard Integration**: Add UI in `dashboard/pages/`
5. **Documentation**: Add docstrings and comments

## Best Practices

### Module Organization
- Keep modules focused on single responsibility
- Use type hints for all functions
- Write comprehensive docstrings
- Keep functions pure (no side effects)

### Code Style
- Follow PEP 8
- Use descriptive variable names
- Keep functions small (<50 lines)
- Use constants for magic numbers

### Testing
- Write tests for all utility functions
- Test data loading and validation
- Include edge cases
- Aim for >80% coverage

### Documentation
- Document all public functions
- Include usage examples
- Keep README updated
- Add inline comments for complex logic

## Common Tasks

### Adding a New Page
1. Create new file in `dashboard/pages/`
2. Implement `show()` function
3. Import in `dashboard/app.py`
4. Add to navigation

### Adding a New Feature
1. Implement in `src/features.py`
2. Write tests in `tests/`
3. Use in pages or utilities
4. Document with docstring

### Adding New Visualization
1. Create function in `src/plots.py`
2. Use consistent styling
3. Support Plotly or Matplotlib
4. Test with sample data

## Troubleshooting

### Data Not Loading
- Check CSV files exist in project root
- Verify column names match constants
- Check data file paths in config.py
- Review error messages in logs

### Page Not Displaying
- Check import statements
- Verify data in session state
- Look for session state initialization
- Check browser console for errors

### Performance Issues
- Check data loading caching
- Review query performance
- Consider data preprocessing
- Use incremental loading for large datasets

## Future Improvements

- [ ] Add statistical tests and p-values
- [ ] Implement prediction models
- [ ] Add player comparison scoring
- [ ] Create export functionality (PDF/Excel)
- [ ] Add data refresh automation
- [ ] Implement caching for complex queries
- [ ] Add more visualizations
- [ ] Create mobile-responsive design
