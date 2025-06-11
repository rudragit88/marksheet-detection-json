import cv2
import pytesseract
import re
import json
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_from_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print("Error: Couldn't load the image. Check the path.")
        return ""


    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


    text = pytesseract.image_to_string(gray)
    return text

def parse_text_to_json(text):
    data = {}
    marks = {}

    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = re.match(r"(\w[\w ]*):\s*(\w[\w ]*)", line)
        if match:
            key, value = match.groups()
            key = key.strip()
            value = value.strip()

            try:
                value = int(value)
            except:
                pass

            if key.lower() in ["name", "roll no", "total"]:
                data[key] = value
            else:
                marks[key] = value

    data["Marks"] = marks
    return data

def save_to_json(data, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"JSON saved to: {output_path}")


if __name__ == "__main__":
  
    image_path = r"C:\Users\HP\Pictures\Screenshots\Screenshot 2025-06-11 004231.png"

    extracted_text = extract_text_from_image(image_path)

    print("Extracted Text:\n")
    print(extracted_text)

    json_data = parse_text_to_json(extracted_text)

    save_to_json(json_data, "output/result.json")
