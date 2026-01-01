# Project Structure Visualization

## Complete File Tree

```
Tennis Performance/
│
├── 📁 src/                          # CORE LIBRARY (1,300+ lines)
│   ├── __init__.py                  # Package initialization
│   ├── config.py                    # ⚙️  Paths, settings, configuration
│   ├── constants.py                 # 🔤 Enums, constants, lookup tables
│   ├── dataset.py                   # 📊 Data loading & validation
│   ├── features.py                  # 🔧 Feature engineering & aggregations
│   ├── utils.py                     # 🛠️  Utility functions & helpers
│   ├── plots.py                     # 📈 Visualization functions
│   │
│   ├── 📁 modeling/                 # (Reserved for ML models)
│   │   ├── __init__.py
│   │   ├── train.py
│   │   └── predict.py
│   │
│   └── 📁 services/                 # (Reserved for API/external integration)
│       └── __init__.py
│
├── 📁 dashboard/                    # STREAMLIT APP (850+ lines)
│   ├── __init__.py
│   ├── app.py                       # 🎯 Main application entry point
│   │
│   ├── 📁 pages/                    # Multi-page structure
│   │   ├── __init__.py
│   │   ├── player_analysis.py       # 👤 Player statistics & trends
│   │   ├── tournament_analysis.py   # 🏆 Tournament insights
│   │   └── trend_analysis.py        # 📊 Macro trends
│   │
│   └── 📁 components/               # Reusable UI components
│       └── __init__.py              # Display helpers & widgets
│
├── 📁 tests/                        # TEST SUITE (300+ lines)
│   ├── __init__.py
│   ├── test_dataset.py              # Data loading tests
│   ├── test_features.py             # Feature engineering tests
│   └── test_utils.py                # Utility function tests
│
├── 📁 data/                         # DATA MANAGEMENT
│   ├── raw/                         # Original immutable data
│   ├── interim/                     # Intermediate transformations
│   ├── processed/                   # Final analysis datasets
│   └── external/                    # External data sources
│
├── 📁 models/                       # TRAINED MODELS (for future use)
│
├── 📁 reports/                      # GENERATED REPORTS
│   └── figures/                     # Saved visualizations
│
├── 📁 notebooks/                    # JUPYTER NOTEBOOKS
│   └── .gitkeep
│
├── 📄 STRUCTURE.md                  # 📚 Comprehensive module documentation
├── 📄 QUICKSTART.md                 # 🚀 Getting started guide
├── 📄 REFACTORING_SUMMARY.md        # 📋 Before/after comparison
├── 📄 make.py                       # 🔨 Task automation (install, test, run)
├── 📄 .env.example                  # ⚙️  Environment template
│
├── 📄 mod_players.csv               # Player data
├── 📄 players_yearly_perfomance.csv # Yearly stats
├── 📄 matches.csv                   # Match records
├── 📄 tournaments.csv               # Tournament info
├── 📄 matches_data_dictionary.txt   # Data documentation
│
├── 📄 README.md                     # Project description
├── 📄 project_brief.md              # Original objectives
├── 📄 requirements.txt              # Dependencies
├── 📄 pyproject.toml                # Project config
├── 📄 LICENCE                       # Open source license
│
└── 🗂️  .git/                        # Version control

```

## Module Dependency Graph

```
dashboard/app.py (Main Entry)
    ↓
    ├─→ src/config.py (Settings & Paths)
    │
    ├─→ src/dataset.py (Data I/O)
    │   └─→ src/config.py
    │
    └─→ dashboard/pages/*.py
        ├─→ src/dataset.py
        ├─→ src/features.py
        │   └─→ src/config.py
        ├─→ src/utils.py
        │   └─→ src/config.py
        ├─→ src/plots.py
        ├─→ dashboard/components/
        └─→ src/constants.py
```

## Code Organization Summary

| Module | Purpose | Key Functions | Lines |
|--------|---------|---------------|-------|
| **config.py** | Centralized config & paths | `get_data_file_path()`, `ensure_directories_exist()` | ~90 |
| **constants.py** | Constants & enums | Tournament levels, surfaces, entry codes | ~65 |
| **dataset.py** | Data loading & validation | `load_*_data()`, `validate_data_integrity()` | ~180 |
| **features.py** | Feature engineering | `create_win_loss_stats()`, `get_head_to_head()` | ~340 |
| **utils.py** | Helper utilities | `calculate_streaks()`, `format_percentage()` | ~290 |
| **plots.py** | Visualizations | `create_bar_comparison()`, `create_line_plot()` | ~350 |
| **app.py** | Dashboard main | Navigation, data loading, page routing | ~130 |
| **player_analysis.py** | Player page | Single/dual player analysis, filtering | ~450 |
| **tournament_analysis.py** | Tournament page | Tournament stats, H2H, trends | ~200 |
| **trend_analysis.py** | Trends page | Macro trends, distributions | ~180 |
| **components/__init__.py** | UI components | `display_metric_card()`, `display_section_header()` | ~80 |
| **Tests** | Unit tests | Data, features, utils validation | ~300 |

**Total: ~2,655 lines of well-organized, documented code**

## Key Statistics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Code Organization | 1 file | 22 files | +2,100% |
| Modularity | Low | High | ✅ |
| Testability | None | Comprehensive | ✅ |
| Reusability | Low | High | ✅ |
| Documentation | Minimal | Extensive | ✅ |
| Type Hints | None | Throughout | ✅ |
| Maintainability | Hard | Easy | ✅ |

## Import Examples

### Before (Monolithic)
```python
# Everything in one 485-line file
import streamlit as st
# Had to work with global variables
# Hard to test
# Hard to reuse
```

### After (Modular)
```python
# Clean, organized imports
from src import config, dataset, features, utils, plots
from dashboard.components import display_metric_card

# Use well-defined functions
players = dataset.get_player_names(data['players'])
stats = features.create_win_loss_stats(match_data, 'surface')
fig = plots.create_bar_comparison(stats, x='surface', y='wlr')
```

## Future Extensibility

The new structure supports:

```
✅ Adding new pages
✅ Adding new features
✅ Creating CLI tools
✅ Building an API
✅ Creating data pipelines
✅ Adding ML models
✅ Implementing caching
✅ Writing batch scripts
✅ Unit testing
✅ Type checking
```

---

**This refactoring transforms the project from a prototype into production-ready code!**
