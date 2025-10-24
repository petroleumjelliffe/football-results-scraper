# DuckDB Frontend Guide

There are several ways to interact with your football data using DuckDB frontends.

## 1. Harlequin (Terminal UI) ⭐ RECOMMENDED

**Beautiful terminal-based SQL IDE with syntax highlighting and autocomplete**

### Installation
Already installed! Included in `requirements.txt`.

### Launch
```bash
./launch_harlequin.sh
```

Or manually:
```bash
python3 -m harlequin "duckdb:///:memory:"
```

### Features
- ✓ Syntax highlighting
- ✓ Auto-completion
- ✓ Query history (Ctrl+H)
- ✓ Table browser (left sidebar)
- ✓ Export results
- ✓ Keyboard shortcuts
- ✓ Works with CSV files directly

### Keyboard Shortcuts
- `Ctrl+Enter` - Run query
- `Ctrl+Q` - Quit
- `Ctrl+H` - Query history
- `F2` - Format SQL
- `Tab` - Autocomplete
- `Ctrl+E` - Export results
- `F9` - Toggle sidebar

### Quick Start
1. Run `./launch_harlequin.sh`
2. In the left sidebar, click on `all_matches` to see the schema
3. Type a query in the editor:
   ```sql
   SELECT League, COUNT(*) as matches
   FROM all_matches
   GROUP BY League
   ORDER BY matches DESC;
   ```
4. Press `Ctrl+Enter` to run

### Sample Queries in Harlequin
```sql
-- Top scorers
SELECT HomeTeam as team, SUM(FTHG) as goals
FROM all_matches
GROUP BY team
ORDER BY goals DESC
LIMIT 10;

-- Recent matches
SELECT Date, League, HomeTeam, AwayTeam, FTHG, FTAG
FROM all_matches
WHERE Season = '2425'
ORDER BY Date DESC
LIMIT 20;

-- Home advantage by league
SELECT
    League,
    ROUND(100.0 * SUM(CASE WHEN FTR = 'H' THEN 1 ELSE 0 END) / COUNT(*), 1) as home_win_pct
FROM all_matches
GROUP BY League
ORDER BY home_win_pct DESC;
```

---

## 2. DuckDB CLI (Built-in)

**Simple command-line interface**

### Launch
```bash
python3 -m duckdb
```

### Query CSV files directly
```sql
D SELECT * FROM 'data/2425_E0.csv' LIMIT 5;
D SELECT COUNT(*) FROM 'data/*.csv';
D .mode markdown  -- Change output format
D .tables         -- List tables
D .quit           -- Exit
```

### Pros
- ✓ Lightweight
- ✓ No setup needed
- ✓ Fast

### Cons
- ✗ Basic interface
- ✗ No syntax highlighting
- ✗ Limited editing

---

## 3. DBeaver (Desktop GUI)

**Full-featured database GUI (like MySQL Workbench)**

### Installation
1. Download from https://dbeaver.io/
2. Install for your OS
3. Open DBeaver

### Setup
1. Click "New Database Connection"
2. Select "DuckDB"
3. Choose "Create new database" or "In-memory"
4. For persistent: Point to `football.db`

### Features
- ✓ Visual query builder
- ✓ ER diagrams
- ✓ Data editor
- ✓ Export/import wizards
- ✓ Visual explain plans
- ✓ Cross-platform

### Pros
- ✓ Professional features
- ✓ Great for complex queries
- ✓ Data visualization

### Cons
- ✗ Heavier application
- ✗ Separate installation

---

## 4. VS Code Extension

**Query DuckDB from within VS Code**

### Installation
1. Open VS Code
2. Go to Extensions (Cmd+Shift+X)
3. Search for "DuckDB SQL Tools"
4. Install

### Usage
1. Open Command Palette (Cmd+Shift+P)
2. Type "DuckDB: New Query"
3. Write SQL and run with play button

### Pros
- ✓ Integrated with your editor
- ✓ Great for developers
- ✓ Can run alongside Python

### Cons
- ✗ Requires VS Code
- ✗ Less specialized than Harlequin

---

## 5. Python Scripts (Programmatic)

**Custom Python analysis (already set up)**

### analyze_duckdb.py
Pre-built analyses:
```bash
python3 analyze_duckdb.py
```

Interactive mode:
```bash
python3 analyze_duckdb.py --interactive
```

### Custom Script
```python
import duckdb

con = duckdb.connect()

# Query CSV files directly
result = con.execute("""
    SELECT * FROM 'data/2425_E0.csv'
    LIMIT 5
""").fetchall()

for row in result:
    print(row)

con.close()
```

### Pros
- ✓ Automation
- ✓ Integration with other tools
- ✓ Flexible

---

## 6. Jupyter Notebooks

**Interactive data exploration**

### Installation
```bash
pip install jupyter
```

### Usage
```bash
jupyter notebook
```

Then create a new notebook:
```python
import duckdb

con = duckdb.connect()

# Query and display
result = con.execute("""
    SELECT League, COUNT(*) as matches
    FROM 'data/*.csv'
    GROUP BY League
""").df()  # Returns pandas DataFrame

# Display
result
```

### Pros
- ✓ Great for exploration
- ✓ Can mix code, text, and visualizations
- ✓ Shareable

---

## 7. Web Dashboard (Evidence.dev)

**Create interactive web reports**

### Installation
```bash
npx degit evidence-dev/template my-football-dashboard
cd my-football-dashboard
npm install
```

### Create a page (`pages/index.md`)
````markdown
# Football Data Dashboard

```sql matches_by_league
SELECT League, COUNT(*) as matches
FROM 'data/*.csv'
GROUP BY League
```

<BarChart data={matches_by_league} x=League y=matches/>
````

### Launch
```bash
npm run dev
```

Visit http://localhost:3000

### Pros
- ✓ Beautiful dashboards
- ✓ Shareable
- ✓ Reactive

### Cons
- ✗ Requires Node.js
- ✗ More complex setup

---

## My Recommendation

**For your use case, I recommend:**

1. **Harlequin** (Terminal UI) - For quick, interactive queries
   - Launch with `./launch_harlequin.sh`
   - Perfect for ad-hoc analysis
   - Beautiful and fast

2. **analyze_duckdb.py** - For repeated analyses
   - Pre-built reports
   - Can be automated

3. **DBeaver** (Optional) - If you want a full GUI
   - Download from https://dbeaver.io/
   - Great for complex queries and visualization

---

## Quick Comparison

| Frontend | Type | Best For | Complexity |
|----------|------|----------|------------|
| **Harlequin** | Terminal | Interactive queries | ⭐ Low |
| DuckDB CLI | Terminal | Quick checks | ⭐ Low |
| analyze_duckdb.py | Python | Automation | ⭐ Low |
| DBeaver | Desktop GUI | Complex work | ⭐⭐ Medium |
| VS Code | Editor | Developers | ⭐⭐ Medium |
| Jupyter | Notebook | Exploration | ⭐⭐ Medium |
| Evidence.dev | Web | Dashboards | ⭐⭐⭐ High |

---

## Next Steps

Try Harlequin first:
```bash
./launch_harlequin.sh
```

Then explore the pre-built analyses:
```bash
python3 analyze_duckdb.py
```

If you want a full GUI, download DBeaver from https://dbeaver.io/
