import requests
import pandas as pd
import sqlite3
from pathlib import Path
import time

# Define leagues and seasons
LEAGUES = ['E0', 'E1', 'D1', 'D2', 'I1', 'I2', 'SP1', 'SP2', 'F1', 'F2']
# LEAGUES = ['D1']
SEASONS = ['2526', '2425', '2324', '2223', '2122', '2021', '1920', '1819', '1718']  # Add more as needed
BASE_URL = "https://www.football-data.co.uk/mmz4281"

def download_csv(season, league, data_dir='data'):
    """Download a single CSV file"""
    url = f"{BASE_URL}/{season}/{league}.csv"
    output_dir = Path(data_dir)
    output_dir.mkdir(exist_ok=True)
    
    filepath = output_dir / f"{season}_{league}.csv"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ Downloaded {season}/{league}")
        return filepath
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed {season}/{league}: {e}")
        return None

def download_all(seasons, leagues):
    """Download all CSV files"""
    files = []
    for season in seasons:
        for league in leagues:
            filepath = download_csv(season, league)
            if filepath:
                files.append(filepath)
            time.sleep(0.5)  # Be nice to the server
    return files

def inspect_schemas(filepaths):
    """Check all CSV schemas and find common columns"""
    all_columns = {}
    
    for filepath in filepaths:
        try:
            df = pd.read_csv(filepath, nrows=1)
            columns = set(df.columns)
            all_columns[filepath.name] = columns
            print(f"{filepath.name}: {len(columns)} columns")
        except Exception as e:
            print(f"Error reading {filepath.name}: {e}")
    
    # Find common columns
    if all_columns:
        common_cols = set.intersection(*all_columns.values())
        all_cols = set.union(*all_columns.values())
        
        print(f"\nCommon columns: {len(common_cols)}")
        print(f"All unique columns: {len(all_cols)}")
        print(f"\nColumns not in all files: {all_cols - common_cols}")
        
        return common_cols, all_cols
    return set(), set()

def load_csv_with_metadata(filepath):
    """Load CSV and add season/league metadata"""
    df = pd.read_csv(filepath)

    # Convert Date column to proper datetime format (from dd/mm/yyyy or dd/mm/yy)
    if 'Date' in df.columns:
        # Use dayfirst=True to handle dd/mm/yyyy format correctly
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        # Convert to string in ISO format (YYYY-MM-DD) for SQLite compatibility
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

    # Extract season and league from filename
    parts = filepath.stem.split('_')
    df['Season'] = parts[0]
    df['League'] = parts[1]
    df['Source_File'] = filepath.name

    return df
def create_database(filepaths, db_path='football.db', use_common_cols=False):
    """Create SQLite database from CSV files"""
    conn = sqlite3.connect(db_path)
    
    all_dfs = []
    for filepath in filepaths:
        try:
            df = load_csv_with_metadata(filepath)
            all_dfs.append(df)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
    
    if not all_dfs:
        print("No data to import")
        return
    
    # Combine all dataframes
    combined_df = pd.concat(all_dfs, ignore_index=True, sort=False)
    
    # Clean column names (remove spaces, special chars)
    combined_df.columns = combined_df.columns.str.strip()
    
    # Create table
    combined_df.to_sql('matches', conn, if_exists='replace', index=False)
    
    # Create indexes for better query performance
    conn.execute('CREATE INDEX IF NOT EXISTS idx_date ON matches(Date)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_league ON matches(League)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_season ON matches(Season)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_teams ON matches(HomeTeam, AwayTeam)')
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Database created: {db_path}")
    print(f"  Total rows: {len(combined_df)}")
    print(f"  Columns: {len(combined_df.columns)}")
def update_database(new_csv_path, db_path='football.db'):
    """Add only new rows from a CSV to the database"""
    conn = sqlite3.connect(db_path)
    
    # Load new data
    new_df = load_csv_with_metadata(Path(new_csv_path))
    new_df.columns = new_df.columns.str.strip()
    
    # Get existing data for this season/league
    season = new_df['Season'].iloc[0]
    league = new_df['League'].iloc[0]
    
    query = f"""
    SELECT * FROM matches 
    WHERE Season = '{season}' AND League = '{league}'
    """
    existing_df = pd.read_sql(query, conn)
    
    if len(existing_df) == 0:
        # No existing data, insert all
        new_df.to_sql('matches', conn, if_exists='append', index=False)
        print(f"Added {len(new_df)} new rows")
    else:
        # Find rows that don't exist yet
        # Create a unique key from match details
        def make_key(df):
            return df['Date'].astype(str) + '_' + df['HomeTeam'] + '_' + df['AwayTeam']
        
        existing_keys = set(make_key(existing_df))
        new_df['_key'] = make_key(new_df)
        
        new_rows = new_df[~new_df['_key'].isin(existing_keys)]
        new_rows = new_rows.drop('_key', axis=1)
        
        if len(new_rows) > 0:
            new_rows.to_sql('matches', conn, if_exists='append', index=False)
            print(f"Added {len(new_rows)} new rows out of {len(new_df)} total")
        else:
            print("No new rows to add")
    
    conn.close()

def sync_latest(db_path='football.db'):
    """Download and update with latest data for current season"""
    current_season = '2526'  # Update this as needed
    
    for league in LEAGUES:
        print(f"Syncing {league}...")
        filepath = download_csv(current_season, league, data_dir='temp')
        if filepath:
            update_database(filepath, db_path)
            filepath.unlink()  # Clean up temp file


def main():
    # Initial setup
    print("=== Downloading CSVs ===")
    files = download_all(SEASONS, LEAGUES)
    
    print("\n=== Inspecting Schemas ===")
    common_cols, all_cols = inspect_schemas(files)
    
    print("\n=== Creating Database ===")
    create_database(files)
    
    print("\n=== Database ready! ===")

def update():
    """Run this periodically to get new matches"""
    print("=== Updating Database ===")
    sync_latest()

if __name__ == '__main__':
    # main()
    update()
    # Later, run: update()