import os
import cv2
import easyocr
import json
import re

# ✅ Initialize EasyOCR reader (English only; GPU=False for compatibility)
reader = easyocr.Reader(['en'], gpu=False)

# ✅ Regex patterns to extract fields from OCR output
FIELD_PATTERNS = {
    "Student Name": r"Student\s*Name\s*[:\-]?\s*(.*)",
    "College Name": r"College\s*Name\s*[:\-]?\s*(.*)",
    "SGPA": r"SGPA\s*[:\-]?\s*(\d+\.\d+)",
    "CGPA": r"CGPA\s*[:\-]?\s*(\d+\.\d+)",
    "Result": r"Result\s*[:\-]?\s*(PASS|FAIL)",
    # Optional: Add more fields as needed
}

# ✅ Extract raw text from an image using EasyOCR
def extract_text_from_image(image_path: str) -> str:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    results = reader.readtext(image_path)
    text = "\n".join([item[1] for item in results])
    # print("🔍 OCR Text Extracted:\n", text)
    return text

# ✅ Parse key fields using regex patterns
def parse_text_with_regex(text: str) -> dict:
    result = {}
    for field, pattern in FIELD_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        result[field] = match.group(1).strip() if match else ""
    return result

# ✅ Save extracted dictionary data to JSON
def save_to_json(data: dict, filename: str, output_dir: str = "output") -> str:
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return filepath

# ✅ Complete processing: from image to parsed data
def process_image_to_json(image_path: str) -> dict:
    raw_text = extract_text_from_image(image_path)
    extracted_data = parse_text_with_regex(raw_text)
    return extracted_data
