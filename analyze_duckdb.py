import duckdb
from pathlib import Path

# Initialize DuckDB connection (in-memory)
con = duckdb.connect()

# Data directory
DATA_DIR = Path('data')

def setup_view():
    """Create a unified view of all CSV files"""
    # DuckDB can query CSV files directly with wildcards!
    # This creates a view that combines all CSV files
    con.execute("""
        CREATE OR REPLACE VIEW all_matches AS
        SELECT
            *,
            CAST(SUBSTRING(regexp_replace(filename, '.*/(\d{4})_.*', '\\1'), 1, 2) ||
                 SUBSTRING(regexp_replace(filename, '.*/(\d{4})_.*', '\\1'), 3, 4) AS VARCHAR) as Season,
            regexp_replace(filename, '.*_([A-Z0-9]+)\.csv', '\\1') as League
        FROM read_csv_auto('data/*.csv', filename=true, ignore_errors=true)
    """)
    print("✓ Created unified view of all CSV files")

def basic_stats():
    """Show basic statistics"""
    print("\n=== Basic Statistics ===")

    # Total matches
    result = con.execute("SELECT COUNT(*) as total_matches FROM all_matches").fetchone()
    print(f"Total matches: {result[0]:,}")

    # Matches per league
    print("\nMatches per league:")
    result = con.execute("""
        SELECT League, COUNT(*) as matches
        FROM all_matches
        GROUP BY League
        ORDER BY matches DESC
    """).fetchall()
    for league, count in result:
        print(f"  {league}: {count:,}")

    # Matches per season
    print("\nMatches per season:")
    result = con.execute("""
        SELECT Season, COUNT(*) as matches
        FROM all_matches
        GROUP BY Season
        ORDER BY Season DESC
    """).fetchall()
    for season, count in result:
        print(f"  {season}: {count:,}")

def home_advantage():
    """Analyze home advantage across leagues"""
    print("\n=== Home Advantage Analysis ===")

    result = con.execute("""
        SELECT
            League,
            COUNT(*) as total_matches,
            SUM(CASE WHEN FTR = 'H' THEN 1 ELSE 0 END) as home_wins,
            SUM(CASE WHEN FTR = 'D' THEN 1 ELSE 0 END) as draws,
            SUM(CASE WHEN FTR = 'A' THEN 1 ELSE 0 END) as away_wins,
            ROUND(100.0 * SUM(CASE WHEN FTR = 'H' THEN 1 ELSE 0 END) / COUNT(*), 1) as home_win_pct,
            ROUND(AVG(FTHG), 2) as avg_home_goals,
            ROUND(AVG(FTAG), 2) as avg_away_goals
        FROM all_matches
        WHERE FTR IS NOT NULL
        GROUP BY League
        ORDER BY home_win_pct DESC
    """).fetchall()

    for row in result:
        league, total, hw, d, aw, hw_pct, avg_hg, avg_ag = row
        print(f"\n{league}:")
        print(f"  Home wins: {hw_pct}% ({hw}/{total})")
        print(f"  Draws: {round(100*d/total, 1)}%")
        print(f"  Away wins: {round(100*aw/total, 1)}%")
        print(f"  Avg goals: Home {avg_hg} - Away {avg_ag}")

def top_scorers():
    """Find teams with most goals"""
    print("\n=== Top Scoring Teams (All Time) ===")

    result = con.execute("""
        WITH team_goals AS (
            SELECT HomeTeam as team, SUM(FTHG) as goals FROM all_matches GROUP BY HomeTeam
            UNION ALL
            SELECT AwayTeam as team, SUM(FTAG) as goals FROM all_matches GROUP BY AwayTeam
        )
        SELECT team, SUM(goals) as total_goals
        FROM team_goals
        GROUP BY team
        ORDER BY total_goals DESC
        LIMIT 10
    """).fetchall()

    for i, (team, goals) in enumerate(result, 1):
        print(f"{i:2d}. {team:20s} {goals:4d} goals")

def high_scoring_matches():
    """Find highest scoring matches"""
    print("\n=== Highest Scoring Matches ===")

    result = con.execute("""
        SELECT
            Date,
            League,
            HomeTeam,
            AwayTeam,
            FTHG,
            FTAG,
            (FTHG + FTAG) as total_goals
        FROM all_matches
        WHERE FTHG IS NOT NULL AND FTAG IS NOT NULL
        ORDER BY total_goals DESC
        LIMIT 10
    """).fetchall()

    for row in result:
        date, league, home, away, hg, ag, total = row
        print(f"{date} [{league}] {home} {int(hg)}-{int(ag)} {away} ({int(total)} goals)")

def goals_trends():
    """Analyze goals trends over seasons"""
    print("\n=== Goals Trends by Season ===")

    result = con.execute("""
        SELECT
            Season,
            COUNT(*) as matches,
            ROUND(AVG(FTHG + FTAG), 2) as avg_goals_per_match,
            ROUND(AVG(FTHG), 2) as avg_home_goals,
            ROUND(AVG(FTAG), 2) as avg_away_goals
        FROM all_matches
        WHERE FTHG IS NOT NULL AND FTAG IS NOT NULL
        GROUP BY Season
        ORDER BY Season DESC
    """).fetchall()

    for season, matches, avg_goals, avg_hg, avg_ag in result:
        print(f"{season}: {avg_goals} goals/match (H:{avg_hg} A:{avg_ag}) [{matches} matches]")

def league_comparison():
    """Compare different leagues"""
    print("\n=== League Comparison (Current Season 2425) ===")

    result = con.execute("""
        SELECT
            League,
            COUNT(*) as matches,
            ROUND(AVG(FTHG + FTAG), 2) as avg_goals,
            ROUND(100.0 * SUM(CASE WHEN FTR = 'H' THEN 1 ELSE 0 END) / COUNT(*), 1) as home_win_pct,
            ROUND(100.0 * SUM(CASE WHEN FTR = 'D' THEN 1 ELSE 0 END) / COUNT(*), 1) as draw_pct,
            ROUND(AVG(TRY_CAST(HS AS DOUBLE) + TRY_CAST("AS" AS DOUBLE)), 1) as avg_shots,
            ROUND(AVG(TRY_CAST(HC AS DOUBLE) + TRY_CAST(AC AS DOUBLE)), 1) as avg_corners
        FROM all_matches
        WHERE Season = '2425'
        GROUP BY League
        ORDER BY League
    """).fetchall()

    print(f"{'League':<8} {'Matches':>7} {'Avg Goals':>10} {'Home%':>8} {'Draw%':>8} {'Shots':>8} {'Corners':>8}")
    print("-" * 70)
    for league, matches, goals, home_pct, draw_pct, shots, corners in result:
        print(f"{league:<8} {matches:>7} {goals:>10} {home_pct:>7}% {draw_pct:>7}% {shots:>8} {corners:>8}")

def custom_query(sql):
    """Execute a custom SQL query"""
    print(f"\n=== Custom Query ===")
    print(f"SQL: {sql}\n")

    result = con.execute(sql)

    # Print column names
    columns = [desc[0] for desc in result.description]
    print(" | ".join(columns))
    print("-" * 80)

    # Print results
    for row in result.fetchall():
        print(" | ".join(str(val) for val in row))

def export_to_parquet():
    """Export all CSV data to a single Parquet file for faster analysis"""
    print("\n=== Exporting to Parquet ===")

    con.execute("""
        COPY all_matches
        TO 'data/all_matches.parquet'
        (FORMAT PARQUET, COMPRESSION ZSTD)
    """)

    parquet_path = Path('data/all_matches.parquet')
    print(f"✓ Exported to {parquet_path}")
    print(f"  Size: {parquet_path.stat().st_size / 1024 / 1024:.2f} MB")

    # Show how to load it
    print("\nTo load from parquet in future:")
    print("  con.execute(\"SELECT * FROM 'data/all_matches.parquet'\")")

def interactive_mode():
    """Start an interactive query session"""
    print("\n=== Interactive Mode ===")
    print("Enter SQL queries (type 'exit' to quit, 'help' for examples)")
    print("Available table: all_matches")

    examples = {
        'help': "Show this help message",
        'schema': "DESCRIBE all_matches",
        'sample': "SELECT * FROM all_matches LIMIT 5",
        'leagues': "SELECT DISTINCT League FROM all_matches ORDER BY League",
        'seasons': "SELECT DISTINCT Season FROM all_matches ORDER BY Season",
    }

    print("\nQuick commands:", ", ".join(examples.keys()))

    while True:
        try:
            query = input("\nSQL> ").strip()

            if query.lower() == 'exit':
                break

            if query.lower() == 'help':
                for cmd, sql in examples.items():
                    print(f"  {cmd:10s} - {sql}")
                continue

            if query.lower() in examples:
                query = examples[query.lower()]

            if not query:
                continue

            result = con.execute(query)

            # Print results in a nice format
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()

            if not rows:
                print("(no results)")
                continue

            # Calculate column widths
            widths = [len(col) for col in columns]
            for row in rows:
                for i, val in enumerate(row):
                    widths[i] = max(widths[i], len(str(val)))

            # Print header
            header = " | ".join(col.ljust(w) for col, w in zip(columns, widths))
            print(header)
            print("-" * len(header))

            # Print rows
            for row in rows:
                print(" | ".join(str(val).ljust(w) for val, w in zip(row, widths)))

            print(f"\n({len(rows)} row{'s' if len(rows) != 1 else ''})")

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Run all analyses"""
    print("=== Football Data Analysis with DuckDB ===")

    setup_view()
    basic_stats()
    home_advantage()
    top_scorers()
    high_scoring_matches()
    goals_trends()
    league_comparison()

    # Optionally export to parquet
    # export_to_parquet()

    print("\n" + "="*50)
    print("Analysis complete!")
    print("\nFor custom queries, use:")
    print("  python analyze_duckdb.py --interactive")
    print("\nOr import this module and use:")
    print("  con.execute('YOUR SQL HERE').fetchall()")

if __name__ == '__main__':
    import sys

    if '--interactive' in sys.argv or '-i' in sys.argv:
        setup_view()
        interactive_mode()
    else:
        main()
