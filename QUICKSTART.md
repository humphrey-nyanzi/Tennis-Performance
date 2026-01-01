# Quick Start Guide

## Installation & Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

Or if you have a virtual environment:
```bash
# Windows
.venv\Scripts\activate
pip install -r requirements.txt

# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Run the Dashboard
```bash
streamlit run dashboard/app.py
```

The dashboard will open at `http://localhost:8501`

## Using the Dashboard

### Navigation
The dashboard has 3 main sections:

1. **Player Analysis** - Analyze individual player statistics
   - Select a player from the dropdown
   - View career metrics, streaks, and trends
   - Compare two players
   - Filter by surface, tournament level, year, etc.

2. **Tournament Analysis** - Analyze tournament statistics
   - Select a tournament
   - View tournament info and historical trends
   - See top winners
   - Compare tournaments
   - View head-to-head records

3. **Trend Analysis** - View macro trends across all data
   - Winner vs. loser performance metrics
   - Yearly trends for any variable
   - Surface distribution over time
   - Historical patterns

## Common Tasks

### View a Player's Performance
1. Click "Player Analysis"
2. Select player name from sidebar
3. View metrics in main area
4. Optional: Check "Show Last 5 Matches"
5. Optional: Check "Show Advanced Stats"

### Compare Two Players
1. Click "Player Analysis"  
2. Select first player
3. Check "Compare with Another Player"
4. Select second player in sidebar
5. View comparison charts and metrics

### Analyze by Filter
1. Click "Player Analysis"
2. Select player
3. Choose filter type (Surface, Level, Year, etc.)
4. View statistics and charts for that filter

### View Tournament Details
1. Click "Tournament Analysis"
2. Select tournament name
3. View tournament statistics
4. Check yearly trends

## Data Requirements

Ensure these CSV files exist in the project root:
- `mod_players.csv` - Player statistics
- `players_yearly_perfomance.csv` - Yearly performance data
- `matches.csv` - Match records
- `tournaments.csv` - Tournament information

## Keyboard Shortcuts

- **R** - Rerun the dashboard
- **C** - Clear cache
- **K** - Access command palette (Streamlit)

## Tips & Tricks

- **Caching**: First load may take time; subsequent loads are faster
- **Filters**: Use filters to dig deeper into specific aspects
- **Comparisons**: Compare players to find patterns
- **Raw Data**: Check "Show Raw Data" checkboxes for full datasets
- **Responsive**: Dashboard adapts to different screen sizes

## Troubleshooting

### "File not found" Error
Make sure CSV files are in the project root directory

### Dashboard loading slowly
- Check internet connection
- Try refreshing the page
- Check system resources

### Data looks incorrect
- Verify CSV files are up-to-date
- Check data filters and selections
- View raw data to confirm values

## Module Usage (for Developers)

### Load Data
```python
from src import config, dataset

data = dataset.load_all_data({
    'players': config.PLAYERS_CSV,
    'matches': config.MATCHES_CSV,
    'tournaments': config.TOURNAMENTS_CSV,
    'yearly_performance': config.PLAYERS_YEARLY_PERFORMANCE_CSV,
})
```

### Calculate Statistics
```python
from src import features

# Win/loss by surface
stats = features.create_win_loss_stats(match_data, 'surface')

# Head-to-head
h2h = features.get_head_to_head(match_data, 'Player1', 'Player2')
```

### Create Visualizations
```python
from src import plots

fig = plots.create_bar_comparison(
    data, x='surface', y='wlr',
    title='Win Rate by Surface'
)
```

## Running Tests
```bash
pytest tests/ -v
```

## More Information
See `STRUCTURE.md` for detailed module documentation
