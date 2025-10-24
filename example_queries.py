import duckdb
from pathlib import Path

# Initialize DuckDB connection
con = duckdb.connect()

# Create view of all matches
con.execute("""
    CREATE OR REPLACE VIEW all_matches AS
    SELECT
        *,
        CAST(SUBSTRING(regexp_replace(filename, '.*/(\d{4})_.*', '\\1'), 1, 2) ||
             SUBSTRING(regexp_replace(filename, '.*/(\d{4})_.*', '\\1'), 3, 4) AS VARCHAR) as Season,
        regexp_replace(filename, '.*_([A-Z0-9]+)\.csv', '\\1') as League
    FROM read_csv_auto('data/*.csv', filename=true, ignore_errors=true)
""")

def team_season_stats(team_name, season='2425'):
    """Get comprehensive stats for a team in a season"""
    print(f"\n=== {team_name} - Season {season} ===")

    # Home record
    home = con.execute("""
        SELECT
            COUNT(*) as games,
            SUM(CASE WHEN FTR = 'H' THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN FTR = 'D' THEN 1 ELSE 0 END) as draws,
            SUM(CASE WHEN FTR = 'A' THEN 1 ELSE 0 END) as losses,
            SUM(FTHG) as goals_for,
            SUM(FTAG) as goals_against
        FROM all_matches
        WHERE HomeTeam = ? AND Season = ?
    """, [team_name, season]).fetchone()

    # Away record
    away = con.execute("""
        SELECT
            COUNT(*) as games,
            SUM(CASE WHEN FTR = 'A' THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN FTR = 'D' THEN 1 ELSE 0 END) as draws,
            SUM(CASE WHEN FTR = 'H' THEN 1 ELSE 0 END) as losses,
            SUM(FTAG) as goals_for,
            SUM(FTHG) as goals_against
        FROM all_matches
        WHERE AwayTeam = ? AND Season = ?
    """, [team_name, season]).fetchone()

    if home and away:
        total_games = home[0] + away[0]
        total_wins = home[1] + away[1]
        total_draws = home[2] + away[2]
        total_losses = home[3] + away[3]
        total_gf = home[4] + away[4]
        total_ga = home[5] + away[5]
        points = total_wins * 3 + total_draws

        print(f"Record: {total_wins}W-{total_draws}D-{total_losses}L ({points} pts)")
        print(f"Goals: {total_gf} for, {total_ga} against (GD: {total_gf - total_ga:+d})")
        print(f"\nHome: {home[1]}W-{home[2]}D-{home[3]}L ({home[4]} GF, {home[5]} GA)")
        print(f"Away: {away[1]}W-{away[2]}D-{away[3]}L ({away[4]} GF, {away[5]} GA)")
    else:
        print("No data found for this team/season")

def head_to_head(team1, team2, limit=10):
    """Get head-to-head record between two teams"""
    print(f"\n=== {team1} vs {team2} (Last {limit} matches) ===")

    results = con.execute("""
        SELECT
            Date,
            Season,
            League,
            HomeTeam,
            AwayTeam,
            FTHG,
            FTAG,
            FTR
        FROM all_matches
        WHERE (HomeTeam = ? AND AwayTeam = ?)
           OR (HomeTeam = ? AND AwayTeam = ?)
        ORDER BY Date DESC
        LIMIT ?
    """, [team1, team2, team2, team1, limit]).fetchall()

    if not results:
        print("No matches found")
        return

    t1_wins = t2_wins = draws = 0
    t1_goals = t2_goals = 0

    for date, season, league, home, away, hg, ag, result in results:
        # Determine winner from perspective of team1
        if home == team1:
            score = f"{int(hg)}-{int(ag)}"
            if result == 'H':
                winner = team1
                t1_wins += 1
            elif result == 'A':
                winner = team2
                t2_wins += 1
            else:
                winner = 'Draw'
                draws += 1
            t1_goals += hg
            t2_goals += ag
        else:
            score = f"{int(ag)}-{int(hg)}"
            if result == 'A':
                winner = team1
                t1_wins += 1
            elif result == 'H':
                winner = team2
                t2_wins += 1
            else:
                winner = 'Draw'
                draws += 1
            t1_goals += ag
            t2_goals += hg

        print(f"{date} [{league}] {home} {int(hg)}-{int(ag)} {away} ({winner})")

    print(f"\nOverall: {team1} {t1_wins}W - {draws}D - {t2_wins}W {team2}")
    print(f"Goals: {team1} {int(t1_goals)} - {int(t2_goals)} {team2}")

def form_guide(team_name, n=5, season='2425'):
    """Show recent form for a team"""
    print(f"\n=== {team_name} - Last {n} Matches (Season {season}) ===")

    results = con.execute("""
        SELECT
            Date,
            League,
            HomeTeam,
            AwayTeam,
            FTHG,
            FTAG,
            FTR
        FROM all_matches
        WHERE (HomeTeam = ? OR AwayTeam = ?)
          AND Season = ?
        ORDER BY Date DESC
        LIMIT ?
    """, [team_name, team_name, season, n]).fetchall()

    if not results:
        print("No matches found")
        return

    form = []
    for date, league, home, away, hg, ag, result in results:
        is_home = home == team_name
        opponent = away if is_home else home

        if is_home:
            if result == 'H':
                outcome = 'W'
            elif result == 'D':
                outcome = 'D'
            else:
                outcome = 'L'
            score = f"{int(hg)}-{int(ag)}"
        else:
            if result == 'A':
                outcome = 'W'
            elif result == 'D':
                outcome = 'D'
            else:
                outcome = 'L'
            score = f"{int(ag)}-{int(hg)}"

        form.append(outcome)
        venue = 'H' if is_home else 'A'
        print(f"{date} [{venue}] vs {opponent:20s} {score:5s} ({outcome})")

    # Show form string
    form.reverse()
    print(f"\nForm: {'-'.join(form)}")
    wins = form.count('W')
    draws = form.count('D')
    losses = form.count('L')
    points = wins * 3 + draws
    print(f"Points: {points}/{n*3} ({wins}W-{draws}D-{losses}L)")

def league_table(league='E0', season='2425'):
    """Generate a league table"""
    print(f"\n=== {league} Table - Season {season} ===")

    # This is a simplified table - doesn't handle all edge cases
    result = con.execute("""
        WITH home_stats AS (
            SELECT
                HomeTeam as team,
                COUNT(*) as games,
                SUM(CASE WHEN FTR = 'H' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN FTR = 'D' THEN 1 ELSE 0 END) as draws,
                SUM(CASE WHEN FTR = 'A' THEN 1 ELSE 0 END) as losses,
                SUM(FTHG) as gf,
                SUM(FTAG) as ga
            FROM all_matches
            WHERE League = ? AND Season = ?
            GROUP BY HomeTeam
        ),
        away_stats AS (
            SELECT
                AwayTeam as team,
                COUNT(*) as games,
                SUM(CASE WHEN FTR = 'A' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN FTR = 'D' THEN 1 ELSE 0 END) as draws,
                SUM(CASE WHEN FTR = 'H' THEN 1 ELSE 0 END) as losses,
                SUM(FTAG) as gf,
                SUM(FTHG) as ga
            FROM all_matches
            WHERE League = ? AND Season = ?
            GROUP BY AwayTeam
        )
        SELECT
            COALESCE(h.team, a.team) as team,
            COALESCE(h.games, 0) + COALESCE(a.games, 0) as played,
            COALESCE(h.wins, 0) + COALESCE(a.wins, 0) as wins,
            COALESCE(h.draws, 0) + COALESCE(a.draws, 0) as draws,
            COALESCE(h.losses, 0) + COALESCE(a.losses, 0) as losses,
            COALESCE(h.gf, 0) + COALESCE(a.gf, 0) as gf,
            COALESCE(h.ga, 0) + COALESCE(a.ga, 0) as ga,
            (COALESCE(h.gf, 0) + COALESCE(a.gf, 0)) -
            (COALESCE(h.ga, 0) + COALESCE(a.ga, 0)) as gd,
            (COALESCE(h.wins, 0) + COALESCE(a.wins, 0)) * 3 +
            (COALESCE(h.draws, 0) + COALESCE(a.draws, 0)) as points
        FROM home_stats h
        FULL OUTER JOIN away_stats a ON h.team = a.team
        ORDER BY points DESC, gd DESC, gf DESC
    """, [league, season, league, season]).fetchall()

    print(f"{'Pos':<4} {'Team':<20} {'P':>3} {'W':>3} {'D':>3} {'L':>3} {'GF':>4} {'GA':>4} {'GD':>4} {'Pts':>4}")
    print("-" * 75)

    for i, row in enumerate(result, 1):
        team, played, wins, draws, losses, gf, ga, gd, pts = row
        print(f"{i:<4} {team:<20} {played:>3} {wins:>3} {draws:>3} {losses:>3} "
              f"{int(gf):>4} {int(ga):>4} {int(gd):>+4} {pts:>4}")

def betting_analysis(league='E0', season='2425'):
    """Analyze betting trends"""
    print(f"\n=== Betting Analysis: {league} - Season {season} ===")

    result = con.execute("""
        SELECT
            COUNT(*) as total_matches,
            ROUND(100.0 * SUM(CASE WHEN FTR = 'H' THEN 1 ELSE 0 END) / COUNT(*), 1) as home_win_pct,
            ROUND(100.0 * SUM(CASE WHEN FTR = 'D' THEN 1 ELSE 0 END) / COUNT(*), 1) as draw_pct,
            ROUND(100.0 * SUM(CASE WHEN FTR = 'A' THEN 1 ELSE 0 END) / COUNT(*), 1) as away_win_pct,
            ROUND(100.0 * SUM(CASE WHEN (FTHG + FTAG) > 2.5 THEN 1 ELSE 0 END) / COUNT(*), 1) as over_2_5_pct,
            ROUND(100.0 * SUM(CASE WHEN (FTHG + FTAG) < 2.5 THEN 1 ELSE 0 END) / COUNT(*), 1) as under_2_5_pct,
            ROUND(100.0 * SUM(CASE WHEN FTHG > 0 AND FTAG > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) as btts_pct
        FROM all_matches
        WHERE League = ? AND Season = ?
    """, [league, season]).fetchone()

    if result:
        total, home_pct, draw_pct, away_pct, over_pct, under_pct, btts_pct = result
        print(f"Total matches: {total}")
        print(f"\nResult distribution:")
        print(f"  Home wins: {home_pct}%")
        print(f"  Draws: {draw_pct}%")
        print(f"  Away wins: {away_pct}%")
        print(f"\nGoals:")
        print(f"  Over 2.5: {over_pct}%")
        print(f"  Under 2.5: {under_pct}%")
        print(f"  Both teams to score: {btts_pct}%")

# Example usage
if __name__ == '__main__':
    # Uncomment the analyses you want to run

    # Team stats
    team_season_stats('Liverpool', '2425')
    team_season_stats('Arsenal', '2425')

    # Head to head
    head_to_head('Liverpool', 'Man City', limit=10)

    # Recent form
    form_guide('Arsenal', n=5, season='2425')

    # League table
    league_table('E0', '2425')

    # Betting analysis
    betting_analysis('E0', '2425')
    betting_analysis('SP1', '2425')

    con.close()
