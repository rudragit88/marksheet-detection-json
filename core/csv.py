import os
import json
import csv

OUTPUT_FOLDER = "output"
CSV_FILE = os.path.join(OUTPUT_FOLDER, "summary.csv")

def extract_key_fields(json_data):
    """
    Extract name, CGPA/GPA, and college from the given JSON dict.
    Handles missing keys gracefully.
    """
    name = json_data.get("Student Name", "Unknown")
    gpa = json_data.get("CGPA", json_data.get("SGPA", "N/A"))
    college = json_data.get("College Name", "Unknown")
    return [name, gpa, college]

def write_to_csv(data_row, header=["Name", "GPA", "College"]):
    """
    Append a row to the summary CSV.
    Creates file and writes header if file doesn't exist.
    """
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(data_row)

def process_json_to_csv():
    """
    Loop through all JSON files in output folder,
    extract required info and append to CSV.
    """
    files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".json")]

    if not files:
        print("No JSON files found in output folder.")
        return

    for file in files:
        json_path = os.path.join(OUTPUT_FOLDER, file)
        with open(json_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                row = extract_key_fields(data)
                write_to_csv(row)
                print(f"✔ Added {file} to CSV.")
            except json.JSONDecodeError:
                print(f"❌ Skipping invalid JSON: {file}")

if __name__ == "__main__":
    process_json_to_csv()
