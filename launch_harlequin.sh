#!/bin/bash
# Launch Harlequin with DuckDB for football data analysis

# Create a temporary DuckDB database with a view of all CSV files
python3 -c "
import duckdb
con = duckdb.connect('football_temp.db')
con.execute('''
CREATE OR REPLACE VIEW all_matches AS
SELECT
    *,
    CAST(SUBSTRING(regexp_replace(filename, '.*/(\\\\d{4})_.*', '\\\\1'), 1, 2) ||
         SUBSTRING(regexp_replace(filename, '.*/(\\\\d{4})_.*', '\\\\1'), 3, 4) AS VARCHAR) as Season,
    regexp_replace(filename, '.*_([A-Z0-9]+)\\\\.csv', '\\\\1') as League
FROM read_csv_auto('data/*.csv', filename=true, ignore_errors=true);
''')
con.close()
print('✓ Database view created')
"

echo ""
echo "=== Launching Harlequin ==="
echo ""
echo "Quick tips:"
echo "  - Use UP/DOWN arrows to browse tables"
echo "  - Press ENTER on 'all_matches' to see the schema"
echo "  - Type SQL in the editor and press Ctrl+Enter to run"
echo "  - Press Ctrl+Q to quit"
echo ""
echo "Sample query to get started:"
echo "  SELECT * FROM all_matches LIMIT 10;"
echo ""

# Launch Harlequin with the database
python3 -m harlequin football_temp.db

# Cleanup
rm -f football_temp.db
