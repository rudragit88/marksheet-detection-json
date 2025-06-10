import cv2
import pytesseract

# ✅ Step 1: Set the path to tesseract.exe on Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ✅ Step 2: Define a function to extract text from a given image path
def extract_text_from_image(image_path):
    # Load image using OpenCV
    img = cv2.imread(image_path)

    if img is None:
        print("❌ Error: Couldn't load the image. Check the path.")
        return ""

    # Convert to grayscale for better OCR accuracy
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Run OCR with pytesseract
    text = pytesseract.image_to_string(gray)

    return text

# ✅ Step 3: Main block to call the function
if __name__ == "__main__":
    image_path = r"C:\Users\HP\Pictures\Screenshots\Screenshot 2025-06-11 004231.png"
    extracted_text = extract_text_from_image(image_path)

    print("📄 Extracted Text:\n")
    print(extracted_text)
