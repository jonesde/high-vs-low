import sqlite3
import sys
import os

def add_line_numbers(db_path):
    if not os.path.exists(db_path):
        print(f"Error: File '{db_path}' does not exist.")
        return

    try:
        conn = sqlite3.connect(db_path)
        # This ensures the database is in a state where we can handle
        # transactions cleanly
        conn.isolation_level = None
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documents';")
        if not cursor.fetchone():
            print("Error: Table 'documents' not found.")
            return

        print("Fetching IDs of rows that need updating...")
        # We filter out rows that already start with L001 at the SQL level.
        # This is significantly faster for large databases.
        cursor.execute("SELECT id FROM documents WHERE doc_text NOT LIKE 'L001%'")

        # Fetching just the rowids is memory-efficient.
        # (e.g., 1 million IDs will only take ~8MB of RAM).
        row_ids = [row[0] for row in cursor.fetchall()]
        total_to_process = len(row_ids)

        if total_to_process == 0:
            print("No rows found that need updating.")
            return

        print(f"Found {total_to_process} rows to update. Starting...")

        updated_count = 0
        batch_size = 500 # Commit every 500 updates

        for row_id in row_ids:
            # Fetch the specific text for this row
            cursor.execute("SELECT doc_text FROM documents WHERE id = ?", (row_id,))
            result = cursor.fetchone()

            if not result or result[0] is None:
                continue

            doc_text = result[0]
            if not doc_text:
                continue

            doc_text = doc_text.lstrip()
            if doc_text.startswith("L001"):
                continue

            # Split text and add line numbers
            lines = doc_text.splitlines()
            new_lines = []
            for i, line in enumerate(lines, 1):
                prefix = f"L{i:03d}"
                new_lines.append(f"{prefix} {line}")

            new_text = "\n".join(new_lines)

            # Perform the update
            cursor.execute(
                "UPDATE documents SET doc_text = ? WHERE rowid = ?",
                (new_text, row_id)
            )

            updated_count += 1

            # Progress tracking
            if updated_count % 100 == 0:
                print(f"Progress: {updated_count}/{total_to_process}...", end='\r')

            # Batch commit to keep the journal file small and stay fast
            if updated_count % batch_size == 0:
                conn.commit()

        conn.commit()
        print(f"\nFinished! Successfully updated {updated_count} rows.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add_line_numbers.py <database.db>")
    else:
        add_line_numbers(sys.argv[1])
