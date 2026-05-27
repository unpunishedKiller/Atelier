"""
migrate_add_profile_fields.py

Adds optional profile columns to the 'user' table in the existing SQLite database.
Safe to re-run: each ALTER TABLE is wrapped in try/except so already-present
columns are skipped without error.

Run from the project root:
    python migrate_add_profile_fields.py
"""

import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance", "database.db")

# Each entry: (column_name, sqlite_type_definition)
NEW_COLUMNS = [
    ("display_name",     "TEXT NOT NULL DEFAULT ''"),
    ("bio",              "TEXT NOT NULL DEFAULT ''"),
    ("location",         "TEXT NOT NULL DEFAULT ''"),
    ("contact_email",    "TEXT NOT NULL DEFAULT ''"),
    ("instagram_handle", "TEXT NOT NULL DEFAULT ''"),
    ("website_url",      "TEXT NOT NULL DEFAULT ''"),
]


def main():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: database not found at {DB_PATH}")
        sys.exit(1)

    print(f"Connecting to {DB_PATH}\n")
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # Fetch existing column names so we can report skips accurately
    cur.execute("PRAGMA table_info(user)")
    existing = {row[1] for row in cur.fetchall()}

    added  = []
    skipped = []

    for column, definition in NEW_COLUMNS:
        if column in existing:
            skipped.append(column)
            continue
        try:
            cur.execute(f"ALTER TABLE user ADD COLUMN {column} {definition}")
            added.append(column)
        except sqlite3.OperationalError as e:
            # Handles any edge case where PRAGMA missed it
            if "duplicate column" in str(e).lower():
                skipped.append(column)
            else:
                con.close()
                print(f"ERROR adding column '{column}': {e}")
                sys.exit(1)

    con.commit()
    con.close()

    if added:
        print("Columns added:")
        for col in added:
            print(f"  + {col}")
    else:
        print("No new columns to add.")

    if skipped:
        print("\nColumns already present (skipped):")
        for col in skipped:
            print(f"  = {col}")

    print("\nDone. No existing data was modified.")


if __name__ == "__main__":
    main()