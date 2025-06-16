import os
import subprocess

CONFIG_FILE = "config.py"
SCRIPT_FILE = "main.py"

def update_config(row_start, row_end=None):
    with open(CONFIG_FILE, 'w') as f:
        f.write(f"""# Auto-generated config\n
INPUT_CSV_PATH = "final_locations-1.csv"
OUTPUT_CSV_PATH = "output/translated_output.csv"
FAILED_SENTENCE_PATH = "output/failed_sentence_translations.csv"
FAILED_LOCATION_PATH = "output/failed_location_translations.csv"
MODEL = "gemini-2.0-flash"
ROW_START = {row_start}
ROW_END = {row_end if row_end is not None else 'None'}
""")

def run_translation():
    subprocess.run(["python", SCRIPT_FILE], check=True)

if __name__ == "__main__":
    # Example: Run in batches of 2 rows
    total_rows = 65_000
    batch_size = 20

    for i in range(2_000, total_rows, batch_size):
        start = i
        end = i + batch_size if (i + batch_size) <= total_rows else None

        print(f"\n--- Running batch {start} to {end} ---")
        update_config(start, end)
        run_translation()
