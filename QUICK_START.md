# Quick Start Guide - Football Data Analysis

## 🚀 Get Started in 3 Steps

### 1. Launch Harlequin (Terminal UI)
```bash
./launch_harlequin.sh
```

**What you'll see:**
- Left sidebar: Database tables and views
- Center: SQL editor
- Bottom: Results display

**Try this query:**
```sql
SELECT * FROM all_matches LIMIT 10;
```
Press `Ctrl+Enter` to run. Press `Ctrl+Q` to quit.

---

### 2. Run Pre-Built Analysis
```bash
python3 analyze_duckdb.py
```

**You'll get:**
- Statistics on 31,623+ matches
- Home advantage analysis
- Top scoring teams
- Goals trends
- League comparisons

---

### 3. Interactive SQL Mode
```bash
python3 analyze_duckdb.py --interactive
```

Type SQL queries and see results immediately.

---

## 📊 Your Data

**80 CSV files** in [data/](data/) directory:
- 10 leagues (E0, E1, D1, D2, I1, I2, SP1, SP2, F1, F2)
- 9 seasons (2017-18 to 2025-26)
- 31,623 matches total

**Main table:** `all_matches`

**Key columns:**
- `Date`, `Season`, `League`
- `HomeTeam`, `AwayTeam`
- `FTHG`, `FTAG` (full-time goals)
- `FTR` (result: H/D/A)
- `HS`, `AS` (shots)
- `HC`, `AC` (corners)

---

## 🔍 Common Queries

### Find matches for a team
```sql
SELECT Date, League, HomeTeam, AwayTeam, FTHG, FTAG
FROM all_matches
WHERE HomeTeam = 'Liverpool' OR AwayTeam = 'Liverpool'
ORDER BY Date DESC
LIMIT 10;
```

### League table (simplified)
```sql
SELECT
    HomeTeam as team,
    COUNT(*) as games,
    SUM(CASE WHEN FTR = 'H' THEN 3 WHEN FTR = 'D' THEN 1 ELSE 0 END) as points,
    SUM(FTHG) as goals_for,
    SUM(FTAG) as goals_against
FROM all_matches
WHERE Season = '2425' AND League = 'E0'
GROUP BY team
ORDER BY points DESC;
```

### High-scoring matches
```sql
SELECT Date, League, HomeTeam, AwayTeam, FTHG, FTAG,
       (FTHG + FTAG) as total_goals
FROM all_matches
ORDER BY total_goals DESC
LIMIT 10;
```

### Over 2.5 goals percentage
```sql
SELECT
    League,
    ROUND(100.0 * SUM(CASE WHEN (FTHG + FTAG) > 2.5 THEN 1 ELSE 0 END) / COUNT(*), 1) as over_2_5_pct
FROM all_matches
WHERE Season = '2425'
GROUP BY League
ORDER BY over_2_5_pct DESC;
```

---

## 📚 More Resources

- **[README_DUCKDB.md](README_DUCKDB.md)** - Complete DuckDB guide with examples
- **[FRONTEND_GUIDE.md](FRONTEND_GUIDE.md)** - All frontend options explained
- **[analyze_duckdb.py](analyze_duckdb.py)** - Python analysis script
- **[example_queries.py](example_queries.py)** - Advanced query examples

---

## 🎯 Quick Tips

1. **Harlequin keyboard shortcuts:**
   - `Ctrl+Enter` - Run query
   - `Ctrl+Q` - Quit
   - `F2` - Format SQL
   - `Ctrl+H` - Query history

2. **CSV files are queried directly** - no need to import!

3. **Performance tip:** Export to Parquet for faster queries:
   ```python
   python3 -c "
   import duckdb
   con = duckdb.connect()
   con.execute(\"COPY (SELECT * FROM 'data/*.csv') TO 'all_matches.parquet'\")
   "
   ```

4. **Season codes:**
   - `2425` = 2024-25 season
   - `2324` = 2023-24 season
   - etc.

5. **League codes:**
   - `E0` = Premier League
   - `E1` = Championship
   - `SP1` = La Liga
   - `D1` = Bundesliga
   - `I1` = Serie A
   - `F1` = Ligue 1

---

## 🐛 Troubleshooting

**"harlequin: command not found"**
```bash
python3 -m harlequin football_temp.db
```

**Want a GUI?**
- Download DBeaver: https://dbeaver.io/

**Need help?**
- Type `help` in interactive mode
- Check [FRONTEND_GUIDE.md](FRONTEND_GUIDE.md)

---

## 🎉 You're Ready!

Start with:
```bash
./launch_harlequin.sh
```

Happy analyzing! ⚽
