import os
import cv2
import pytesseract
import json
import re


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


INPUT_FOLDER = "data"
OUTPUT_FOLDER = "output"


def parse_text_to_json(text):
    result = {}
    lines = text.splitlines()

    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def extract_text_from_image(image_path):
    img = cv2.imread(image_path)

    if img is None:
        print(f" Failed to load image: {image_path}")
        return ""

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text


def save_to_json(data, filename):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    json_path = os.path.join(OUTPUT_FOLDER, filename)
    with open(json_path, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def process_all_marksheets():
    print("🔍 Looking for marksheet images in 'data/'...")
    files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not files:
        print("No image files found in 'data/' folder.")
        return

    for file in files:
        img_path = os.path.join(INPUT_FOLDER, file)
        print(f"Processing: {file}")
        extracted_text = extract_text_from_image(img_path)
        json_data = parse_text_to_json(extracted_text)

        json_filename = os.path.splitext(file)[0] + ".json"
        save_to_json(json_data, json_filename)
        print(f" Saved JSON as: {json_filename}\n")

# ✅ Run
if __name__ == "__main__":
    process_all_marksheets()
