import os
import cv2
import json
import pytesseract
import tkinter as tk
from tkinter import filedialog, messagebox


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def parse_text_to_json(text):
    result = {}
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def extract_text_from_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return ""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text


def save_to_json(data, original_file):
    filename = os.path.splitext(os.path.basename(original_file))[0] + ".json"
    json_path = os.path.join(OUTPUT_FOLDER, filename)
    with open(json_path, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def process_files(file_paths):
    if not file_paths:
        messagebox.showwarning("No Files", "Please upload at least one marksheet image.")
        return

    if len(file_paths) > 20:
        messagebox.showwarning("Limit Exceeded", "Please upload a maximum of 20 files.")
        return

    success_count = 0
    for path in file_paths:
        try:
            text = extract_text_from_image(path)
            data = parse_text_to_json(text)
            save_to_json(data, path)
            success_count += 1
        except Exception as e:
            print(f"Error processing {path}: {e}")

    messagebox.showinfo("Done", f"Processed {success_count} files successfully.")


def build_gui():
    window = tk.Tk()
    window.title(" Marksheet Text Extractor")
    window.geometry("450x250")
    window.resizable(False, False)

    label = tk.Label(window, text="Upload Marksheet Images (Max: 20)", font=("Arial", 12))
    label.pack(pady=10)

    file_listbox = tk.Listbox(window, width=50, height=6)
    file_listbox.pack(pady=5)

    selected_files = []

    def upload_files():
        files = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if not files:
            return
        file_listbox.delete(0, tk.END)
        selected_files.clear()
        selected_files.extend(files[:20])  # limit to 20
        for file in selected_files:
            file_listbox.insert(tk.END, os.path.basename(file))

    def run_extraction():
        process_files(selected_files)

    upload_btn = tk.Button(window, text="📂 Upload Images", command=upload_files, width=20)
    upload_btn.pack(pady=5)

    run_btn = tk.Button(window, text="🚀 Extract Text & Save JSON", command=run_extraction, width=30, bg="#4CAF50", fg="white")
    run_btn.pack(pady=15)

    window.mainloop()


if __name__ == "__main__":
    build_gui()
