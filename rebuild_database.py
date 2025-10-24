#!/usr/bin/env python3
"""
Rebuild the football.db database with properly formatted dates (YYYY-MM-DD)
"""
import os
import sys
from pathlib import Path

# Import from import-requests.py
sys.path.insert(0, str(Path(__file__).parent))
import importlib.util
spec = importlib.util.spec_from_file_location("import_requests", "import-requests.py")
import_requests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(import_requests)
create_database = import_requests.create_database

def main():
    # Check if database exists
    db_path = 'football.db'
    if os.path.exists(db_path):
        response = input(f"⚠️  {db_path} already exists. Overwrite? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled.")
            return

        # Backup the old database
        backup_path = 'football.db.backup'
        os.rename(db_path, backup_path)
        print(f"✓ Backed up existing database to {backup_path}")

    # Find all CSV files
    data_dir = Path('data')
    csv_files = sorted(data_dir.glob('*.csv'))

    if not csv_files:
        print("Error: No CSV files found in data/ directory")
        return

    print(f"Found {len(csv_files)} CSV files")
    print("\n=== Rebuilding Database ===")
    print("This will convert dates from dd/mm/yyyy to YYYY-MM-DD format")
    print()

    # Create database with proper date formatting
    create_database(csv_files, db_path)

    print("\n✓ Database rebuilt successfully!")
    print(f"  Location: {db_path}")
    print("\nDate format changed from dd/mm/yyyy to YYYY-MM-DD")
    print("You can now query dates properly:")
    print("  SELECT * FROM matches WHERE Date >= '2024-01-01' ORDER BY Date DESC")

if __name__ == '__main__':
    main()
