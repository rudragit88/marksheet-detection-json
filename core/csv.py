import os
import json
import csv
import sqlite3

# 🔧 Paths
OUTPUT_FOLDER = "output"
CSV_FILE = os.path.join(OUTPUT_FOLDER, "summary.csv")
DB_FILE = os.path.join(OUTPUT_FOLDER, "marksheets.db")


# ------------------- Normalization Helpers -------------------
def normalize_text(text):
    return text.strip().title() if isinstance(text, str) else "Unknown"

def normalize_gpa(gpa):
    if not gpa or str(gpa).strip().lower() in ["n/a", "na", "", None]:
        return "Missing"
    return str(gpa).strip()

def normalize_result(result):
    return result.strip().upper() if isinstance(result, str) else "UNKNOWN"

def normalize_backlogs(backlog):
    try:
        return int(backlog)
    except:
        return 0


# ------------------- Extract Fields -------------------
def extract_key_fields(json_data):
    name = normalize_text(json_data.get("Student Name", "Unnamed"))
    gpa = normalize_gpa(json_data.get("CGPA") or json_data.get("SGPA"))
    college = normalize_text(json_data.get("College Name", "Unknown College"))
    result = normalize_result(json_data.get("Result", "UNKNOWN"))
    backlogs = normalize_backlogs(json_data.get("Backlogs", 0))
    return [name, gpa, college, result, backlogs]


# ------------------- CSV Write (Avoid Duplicates) -------------------
def write_to_csv(data_row, header=["Name", "CGPA", "College", "Result", "Backlogs"]):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    existing_rows = set()

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                existing_rows.add(tuple(row))

    if tuple(data_row) not in existing_rows:
        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if os.path.getsize(CSV_FILE) == 0:
                writer.writerow(header)
            writer.writerow(data_row)


# ------------------- SQLite Insert -------------------
def insert_into_db(data_row):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            gpa TEXT,
            college TEXT,
            result TEXT,
            backlogs INTEGER,
            UNIQUE(name, gpa, college)
        )
    """)

    try:
        cursor.execute("""
            INSERT INTO summary (name, gpa, college, result, backlogs)
            VALUES (?, ?, ?, ?, ?)
        """, data_row)
    except sqlite3.IntegrityError:
        pass  # Prevent duplicates

    conn.commit()
    conn.close()


# ------------------- Batch Processor -------------------
def process_json_to_csv():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".json")]

    if not files:
        print("⚠️ No JSON files found in output folder.")
        return

    for file in files:
        json_path = os.path.join(OUTPUT_FOLDER, file)
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                row = extract_key_fields(data)
                write_to_csv(row)
                insert_into_db(row)
                print(f"✔ Added {file} to CSV and Database.")
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in: {file}")
        except Exception as e:
            print(f"❌ Failed processing {file}: {e}")


# ------------------- Run standalone for testing -------------------
if __name__ == "__main__":
    process_json_to_csv()
