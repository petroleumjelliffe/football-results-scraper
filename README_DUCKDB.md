# DuckDB Analysis Guide

This project now includes DuckDB for fast analysis of football results CSV files.

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

Run the pre-built analysis:

```bash
python3 analyze_duckdb.py
```

This will show:
- Basic statistics (total matches, per league, per season)
- Home advantage analysis by league
- Top scoring teams across all seasons
- Highest scoring individual matches
- Goals trends over time
- Current season league comparison

## Interactive Mode

Start an interactive SQL session:

```bash
python3 analyze_duckdb.py --interactive
```

Quick commands in interactive mode:
- `schema` - See all available columns
- `sample` - View sample data
- `leagues` - List all leagues
- `seasons` - List all seasons
- `exit` - Quit interactive mode

## Example Queries

### Find all matches for a specific team

```sql
SELECT Date, League, HomeTeam, AwayTeam, FTHG, FTAG, FTR
FROM all_matches
WHERE HomeTeam = 'Liverpool' OR AwayTeam = 'Liverpool'
ORDER BY Date DESC
LIMIT 10
```

### Team performance at home vs away

```sql
SELECT
    HomeTeam as team,
    COUNT(*) as home_games,
    SUM(CASE WHEN FTR = 'H' THEN 1 ELSE 0 END) as home_wins,
    ROUND(100.0 * SUM(CASE WHEN FTR = 'H' THEN 1 ELSE 0 END) / COUNT(*), 1) as home_win_pct
FROM all_matches
WHERE Season = '2425' AND League = 'E0'
GROUP BY HomeTeam
ORDER BY home_win_pct DESC
```

### Recent form (last 5 matches)

```sql
SELECT
    Date,
    CASE
        WHEN HomeTeam = 'Arsenal' THEN AwayTeam
        ELSE HomeTeam
    END as opponent,
    CASE
        WHEN HomeTeam = 'Arsenal' THEN CONCAT(FTHG, '-', FTAG)
        ELSE CONCAT(FTAG, '-', FTHG)
    END as score,
    CASE
        WHEN (HomeTeam = 'Arsenal' AND FTR = 'H') OR (AwayTeam = 'Arsenal' AND FTR = 'A') THEN 'W'
        WHEN FTR = 'D' THEN 'D'
        ELSE 'L'
    END as result
FROM all_matches
WHERE (HomeTeam = 'Arsenal' OR AwayTeam = 'Arsenal')
    AND Season = '2425'
ORDER BY Date DESC
LIMIT 5
```

### Over/under 2.5 goals analysis

```sql
SELECT
    League,
    COUNT(*) as matches,
    SUM(CASE WHEN (FTHG + FTAG) > 2.5 THEN 1 ELSE 0 END) as over_2_5,
    ROUND(100.0 * SUM(CASE WHEN (FTHG + FTAG) > 2.5 THEN 1 ELSE 0 END) / COUNT(*), 1) as over_pct
FROM all_matches
WHERE Season = '2425'
GROUP BY League
ORDER BY over_pct DESC
```

### Head-to-head records

```sql
SELECT
    Date,
    HomeTeam,
    AwayTeam,
    FTHG,
    FTAG,
    FTR
FROM all_matches
WHERE (HomeTeam = 'Man City' AND AwayTeam = 'Liverpool')
   OR (HomeTeam = 'Liverpool' AND AwayTeam = 'Man City')
ORDER BY Date DESC
```

## Python Usage

You can also use DuckDB directly in your Python scripts:

```python
import duckdb

# Connect
con = duckdb.connect()

# Query CSV files directly
result = con.execute("""
    SELECT * FROM 'data/2425_E0.csv'
    LIMIT 5
""").fetchall()

# Or use the pre-built view
con.execute("CREATE VIEW all_matches AS ...")  # See analyze_duckdb.py
result = con.execute("SELECT * FROM all_matches LIMIT 5").fetchall()

# Close connection
con.close()
```

## Export to Parquet

For faster repeated analysis, export to Parquet format:

```python
from analyze_duckdb import setup_view, export_to_parquet

setup_view()
export_to_parquet()
```

Then query the Parquet file:

```python
result = con.execute("SELECT * FROM 'data/all_matches.parquet'").fetchall()
```

## Available Columns

Key columns in the dataset:
- `Date` - Match date
- `HomeTeam`, `AwayTeam` - Team names
- `FTHG`, `FTAG` - Full-time home/away goals
- `FTR` - Full-time result (H/D/A)
- `HTHG`, `HTAG` - Half-time home/away goals
- `HTR` - Half-time result
- `HS`, `AS` - Home/away shots
- `HST`, `AST` - Home/away shots on target
- `HC`, `AC` - Home/away corners
- `HF`, `AF` - Home/away fouls
- `HY`, `AY` - Home/away yellow cards
- `HR`, `AR` - Home/away red cards
- `Season` - Season (e.g., '2425' for 2024-25)
- `League` - League code (E0, E1, D1, D2, I1, I2, SP1, SP2, F1, F2)

## League Codes

- `E0` - English Premier League
- `E1` - English Championship
- `D1` - German Bundesliga
- `D2` - German Bundesliga 2
- `I1` - Italian Serie A
- `I2` - Italian Serie B
- `SP1` - Spanish La Liga
- `SP2` - Spanish Segunda Division
- `F1` - French Ligue 1
- `F2` - French Ligue 2

## Why DuckDB?

DuckDB advantages over SQLite/Pandas:
- **Fast** - Columnar storage and vectorized execution
- **Direct CSV queries** - No need to import data
- **SQL standard** - Full SQL support with window functions
- **In-memory or persistent** - Flexible deployment
- **Parquet support** - Efficient storage format
- **Zero dependencies** - Embedded database
