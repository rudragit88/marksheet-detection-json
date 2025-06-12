import os
import cv2
import pytesseract
import json

# ✅ Set the Tesseract OCR engine path (for Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image_path: str) -> str:
    """
    Load image and extract raw text using OCR.
    """
    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(f"Unable to load image: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text

def parse_text_to_json(text: str) -> dict:
    """
    Convert structured OCR text to dictionary format (key: value).
    """
    result = {}
    lines = text.splitlines()

    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            result[key.strip()] = value.strip()

    return result

def save_to_json(data: dict, filename: str, output_dir: str = "output") -> str:
    """
    Save dictionary as JSON file in the output directory.
    """
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return filepath

def process_image_to_json(image_path: str) -> dict:
    """
    Full pipeline: Extract text → Parse to JSON → Return JSON dict.
    """
    raw_text = extract_text_from_image(image_path)
    json_data = parse_text_to_json(raw_text)
    return json_data
