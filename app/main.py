import sys
import os

# ✅ Add project root (parent of 'app' and 'core') to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from PIL import Image
import json
import pandas as pd

# ✅ Import custom core modules
from core.ocr_json import extract_text_from_image, parse_text_to_json, save_to_json
from core.csv import extract_key_fields, write_to_csv
from core.insights import generate_suggestions

# ✅ Define folders
INPUT_FOLDER = "data"
OUTPUT_FOLDER = "output"
CSV_PATH = os.path.join(OUTPUT_FOLDER, "summary.csv")

# ✅ Streamlit App UI
st.set_page_config(page_title="Marksheet Analyzer", layout="centered")
st.title("📄 Marksheet Analysis Tool")

# ✅ Upload multiple images
uploaded_files = st.file_uploader("Upload one or more marksheet images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    os.makedirs(INPUT_FOLDER, exist_ok=True)

    if st.button("🔍 Process All Marksheets"):
        for uploaded_file in uploaded_files:
            st.markdown(f"### 📄 Processing: `{uploaded_file.name}`")

            # ✅ Save image
            image_path = os.path.join(INPUT_FOLDER, uploaded_file.name)
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.image(uploaded_file, caption="🖼️ Uploaded Marksheet", use_column_width=True)

            # ✅ OCR & Parsing
            try:
                text = extract_text_from_image(image_path)
            except Exception as e:
                st.error(f"❌ OCR failed for {uploaded_file.name}: {e}")
                continue

            try:
                json_data = parse_text_to_json(text)
                json_filename = os.path.splitext(uploaded_file.name)[0] + ".json"
                save_to_json(json_data, json_filename, OUTPUT_FOLDER)
            except Exception as e:
                st.error(f"❌ JSON parsing/saving failed for {uploaded_file.name}: {e}")
                continue

            # ✅ Write Summary to CSV
            try:
                row = extract_key_fields(json_data)
                write_to_csv(row)
                st.success(f"✅ CSV Summary Updated for {uploaded_file.name}")
            except Exception as e:
                st.error(f"❌ CSV writing failed for {uploaded_file.name}: {e}")
                continue

            # ✅ Show AI Suggestions
            try:
                suggestions = generate_suggestions(json_data)
                if suggestions:
                    st.subheader("💡 AI Insights")
                    st.info(suggestions)
                else:
                    st.warning("⚠ No insights generated.")
            except Exception as e:
                st.warning(f"⚠ AI suggestions failed: {e}")

        # ✅ Show Download Button for CSV
        if os.path.exists(CSV_PATH):
            df = pd.read_csv(CSV_PATH)
            st.download_button(
                label="⬇️ Download Summary CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name="summary.csv",
                mime="text/csv"
            )
