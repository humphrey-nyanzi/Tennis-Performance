# 🎾 Tennis Performance Analysis Dashboard

A modular analytics platform for ATP/WTA player and tournament data. Built with Python and Streamlit.

Live demo: [tennis-performance.streamlit.app](https://tennis-performance.streamlit.app)

---

## What it answers

- Which players dominate specific surfaces, and by how much?
- How does a player's win rate shift across tournament levels (Grand Slams vs. Challengers)?
- Who holds the historical edge in a head-to-head, and does recent form change that?
- Where are the outliers — players overperforming or underperforming their career baseline?

---

## Features

**Player Analysis**
- Career stats: win rate, streaks, surface and tournament-level breakdown
- Season-by-season win rate and ranking trajectory
- Head-to-head records with surface splits

**Comparative Analysis**
- Side-by-side player comparison across any dimension
- Surface and tournament-level rankings
- Recent form and momentum tracking

**Tournament Analysis**
- Match volume trends by year
- Top winners at each tournament
- Tournament-to-tournament comparison

**Trend Analysis**
- Winner vs. loser performance metrics over time
- Surface distribution shifts across seasons
- Match volume by year

**Executive Dashboard**
- Dataset-wide KPIs: total matches, active players, tournaments covered
- Top performers overall and by surface
- Yearly match volume trend

---

## Quick Start

```bash
git clone https://github.com/h-frey/Tennis-Performance.git
cd Tennis-Performance

python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt
python -m streamlit run dashboard/app.py
```

Dashboard runs at `http://localhost:8501`.

---

## Project Structure

```
Tennis-Performance/
├── src/
│   ├── config.py           # Paths and global settings
│   ├── constants.py        # Enums, column mappings
│   ├── dataset.py          # CSV loading and validation
│   ├── features.py         # Aggregations and analytics
│   ├── insights.py         # Auto-generated summaries
│   ├── export.py           # CSV and PDF report generation
│   ├── plots.py            # Plotly/Matplotlib wrappers
│   ├── utils.py            # Formatting and helper functions
│   └── data/
│       ├── loader.py       # Centralised data loader (Streamlit-cached)
│       └── schema.py       # Schema validation
│
├── dashboard/
│   ├── app.py              # Entry point and data loading
│   ├── cache.py            # Cached transform layer
│   ├── components/         # Reusable UI components
│   └── views/              # One module per page
│       ├── executive_dashboard.py
│       ├── player_analysis.py
│       ├── comparative_analysis.py
│       ├── tournament_analysis.py
│       └── trend_analysis.py
│
├── data/raw/               
├── docs/
│   ├── DATA_DICTIONARY.txt
│   └── PROJECT_BRIEF.md
└── requirements.txt
```

---

## Data

| File | Description |
|------|-------------|
| `mod_players.csv` | Player career statistics |
| `players_yearly_perfomance.csv` | Season-by-season metrics |
| `tournaments.csv` | Tournament metadata |
| `matches.csv` | Individual match records |

See `docs/DATA_DICTIONARY.txt` for full column descriptions.

Place files in `data/raw/` before running. The loader validates schema on startup and fails fast if required columns are missing.

---

## Architecture notes

Data flows in one direction: `loader.py` → `app.py` (session state) → `cache.py` → views. Pages never load data directly. All expensive transforms are wrapped in `@st.cache_data` with a deterministic `data_version` fingerprint derived from file metadata, so cache invalidation is automatic when source files change.

The architecture is domain-agnostic. Substituting football or cricket match data requires only a schema-compatible CSV and updated column constants.

---

## Tech stack

- Python 3.12+
- Streamlit
- Pandas
- Plotly
- Matplotlib / Seaborn
- SciPy (statistical tests)
- ReportLab (PDF export)
- Pytest

---

## Tests

```bash
pytest tests/ -v
pytest tests/ -v --cov=src
```

---

## Roadmap

- [ ] Statistical significance testing on performance changes (binomial test — logic in `features.py`, not yet surfaced in UI)
- [ ] Prediction model improvements: surface-adjusted Elo
- [ ] PDF report export (ReportLab scaffolding in place)
- [ ] Data refresh automation
- [ ] Mobile layout improvements

---

## Troubleshooting

**Data files not found** — confirm CSVs are in `data/raw/` and filenames match `src/data/manifest.json`.

**Import errors** — verify the virtual environment is active: `python -m pip show streamlit` should return a result.

**Port conflict** — Streamlit defaults to 8501. Run `python -m streamlit run dashboard/app.py --server.port 8502` to use a different port.

---

## Licence

MIT — see `LICENCE` file.

---

*Python 3.12+ · Status: Beta*