# Git Guide for Football Results Scraper

## What's Ignored

The [.gitignore](.gitignore) file is configured to ignore:

### 🗄️ Database Files
- `*.db` - SQLite databases (including `football.db` - 30MB)
- `*.duckdb` - DuckDB databases
- `football_temp.db` - Temporary Harlequin database

**Why:** Database files are generated from CSV data and can be large. They can be recreated anytime.

### 🐍 Python Files
- `__pycache__/` - Python bytecode cache
- `*.pyc`, `*.pyo` - Compiled Python files
- `.venv/`, `venv/` - Virtual environments
- `*.egg-info/` - Package metadata

### 💻 OS & Editor Files
- `.DS_Store` - macOS folder settings
- `.vscode/` - VS Code settings
- `.idea/` - PyCharm settings
- `Thumbs.db` - Windows thumbnails

### 📊 Generated Data (Optional)
Currently tracking CSV files in `data/` folder, but you can uncomment this line in `.gitignore` if you don't want to track them:
```gitignore
# data/*.csv
```

### 🔐 Sensitive Files
- `.env` - Environment variables
- `*.log` - Log files

## What's Tracked

### ✅ Source Code
- `import-requests.py` - Data scraper
- `analyze_duckdb.py` - Analysis script
- `example_queries.py` - Query examples

### ✅ Scripts
- `launch_harlequin.sh` - Harlequin launcher

### ✅ Documentation
- `README_DUCKDB.md` - DuckDB guide
- `FRONTEND_GUIDE.md` - Frontend options
- `QUICK_START.md` - Quick start guide
- `GIT_GUIDE.md` - This file

### ✅ Configuration
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore rules

### ✅ Data (Currently)
- `data/*.csv` - Football results CSV files

**Note:** The CSV files are currently tracked. If you want to exclude them (since they can be re-downloaded), uncomment the `# data/*.csv` line in [.gitignore](.gitignore).

## Common Git Commands

### Check status
```bash
git status
```

### Add all new/modified files
```bash
git add .
```

### Commit changes
```bash
git commit -m "Add DuckDB analysis tools"
```

### Push to remote
```bash
git push origin main
```

### View ignored files
```bash
git status --ignored
```

### Check what would be committed
```bash
git diff --cached
```

## Recommendations

### Option 1: Track CSV Data (Current Setup)
**Pros:**
- Easy for others to clone and use immediately
- Complete dataset in one place

**Cons:**
- Large repository size (CSV files can be several MB)
- Slower clones/pulls

### Option 2: Don't Track CSV Data
Uncomment this in [.gitignore](.gitignore):
```gitignore
data/*.csv
```

Then add to README instructions for downloading data:
```bash
python3 import-requests.py  # Download CSV files
```

**Pros:**
- Smaller repository
- Faster clones
- CSV files stay up-to-date

**Cons:**
- Users must download data before using

### My Recommendation

**For a public repository:** Don't track CSV files (they can be downloaded)
**For a private/personal repository:** Track CSV files (convenience)

Current branch is **main**, so use that for pushes.

## Database Strategy

The `football.db` (30MB SQLite database) is **already ignored** and won't be committed. This is correct because:

1. It can be regenerated from CSV files
2. It's large (30MB)
3. Binary files don't compress well in git

To recreate it:
```bash
python3 import-requests.py  # Downloads CSVs and creates DB
```

Or users can query CSV files directly with DuckDB without needing the SQLite database at all!

## Quick Workflow

After making changes:

```bash
# See what changed
git status

# Add files (will respect .gitignore)
git add .

# Commit
git commit -m "Your message here"

# Push
git push origin main
```

The `.gitignore` will automatically prevent accidental commits of:
- Database files (*.db)
- Python cache (__pycache__)
- OS files (.DS_Store)
- Virtual environments (venv/)

## Current Repository Size

```bash
# Check repository size
du -sh .git
```

Without database files, your repository should be reasonably sized (mainly CSV files if tracked).
