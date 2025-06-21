import streamlit as st
import sqlite3
import bcrypt
import pandas as pd
import os
import json
import sys
from PIL import Image

# ✅ Fix path to access core/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ✅ Core imports (after fixing sys.path)
from core.ocr_json import extract_text_from_image, parse_text_with_regex, save_to_json
from core.csv import extract_key_fields, write_to_csv, insert_into_db

# -------------------- CONSTANTS --------------------
DB_PATH = "users.db"
INPUT_FOLDER = "data"
OUTPUT_FOLDER = "output"
CSV_PATH = os.path.join(OUTPUT_FOLDER, "summary.csv")


# -------------------- DB FUNCTIONS --------------------
def create_user_table():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password BLOB NOT NULL
            )
        """)
        conn.commit()

def add_user(name, email, username, password):
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute("INSERT INTO users (name, email, username, password) VALUES (?, ?, ?, ?)",
                         (name, email, username, hashed_pw))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def login_user(username, password):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username = ?", (username,))
        data = cur.fetchone()
        if data and bcrypt.checkpw(password.encode(), data[0]):
            return True
    return False


# -------------------- AUTH UI --------------------
def signup_form():
    st.subheader("📝 Signup")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Signup"):
        if name and email and username and password:
            success = add_user(name, email, username, password)
            if success:
                st.success("✅ Signup successful. Please login.")
                st.session_state["show_login"] = True
                st.session_state["show_signup"] = False
            else:
                st.error("❌ Username or email already exists.")
        else:
            st.warning("Please fill all fields.")

def login_form():
    st.subheader("🔓 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login_user(username, password):
            st.success("✅ Login successful.")
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password.")


# -------------------- MARKSHEET TOOL --------------------
def marksheet_tool():
    st.title("📄 Marksheet Analyzer Tool")
    st.session_state.setdefault("process_clicked", False)
    st.session_state.setdefault("db_clicked", False)

    uploaded_files = st.file_uploader("Upload marksheet images (JPG/PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if uploaded_files:
        st.markdown("### 🗂️ Uploaded Files")
        for file in uploaded_files:
            st.markdown(f"📎 **{file.name}** — {round(file.size / 1024, 2)} KB")

        if st.button("Process All Marksheets"):
            st.session_state["process_clicked"] = True

    if uploaded_files and st.session_state["process_clicked"]:
        os.makedirs(INPUT_FOLDER, exist_ok=True)
        total = len(uploaded_files)
        count = 0
        progress_bar = st.progress(0)

        for uploaded_file in uploaded_files:
            image_path = os.path.join(INPUT_FOLDER, uploaded_file.name)
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                text = extract_text_from_image(image_path)
                json_data = parse_text_with_regex(text)
                json_filename = os.path.splitext(uploaded_file.name)[0] + ".json"
                save_to_json(json_data, json_filename, OUTPUT_FOLDER)
                row = extract_key_fields(json_data)
                write_to_csv(row)
            except Exception as e:
                st.error(f"Failed on {uploaded_file.name}: {e}")
                continue

            count += 1
            progress_bar.progress(count / total)

        st.subheader("✅ Processing Summary")
        st.metric("Processed Marksheets", f"{count} / {total}")

        if os.path.exists(CSV_PATH):
            df = pd.read_csv(CSV_PATH)

            col1, _, col2 = st.columns([1.5, 0.5, 1.5])
            with col1:
                download_clicked = st.download_button(
                    label="⬇️ Download Summary CSV",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name="summary.csv",
                    mime="text/csv"
                )
            with col2:
                if st.button("💾 Save to Database", key="save_db_after_csv"):
                    st.session_state["db_clicked"] = True

            if download_clicked:
                st.subheader("🏆 Students Selected for Interview (CGPA ≥ 8)")
                if "CGPA" in df.columns:
                    df['CGPA'] = pd.to_numeric(df['CGPA'], errors='coerce')
                    top_students = df[df['CGPA'] >= 8]
                    if not top_students.empty:
                        st.dataframe(top_students.reset_index(drop=True))
                    else:
                        st.info("No students found with CGPA ≥ 8.")
                else:
                    st.warning("⚠️ CGPA column not found in CSV.")

    if st.session_state["db_clicked"]:
        json_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".json")]
        inserted = 0
        for file in json_files:
            try:
                with open(os.path.join(OUTPUT_FOLDER, file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    row = extract_key_fields(data)
                    insert_into_db(row)
                    inserted += 1
            except Exception as e:
                st.error(f"❌ Error inserting {file}: {e}")
        st.success(f"✅ Inserted {inserted} records into database.")


# -------------------- DB VIEWER --------------------
def view_database():
    st.subheader("📊 Stored Marksheet Records")
    db_file = os.path.join(OUTPUT_FOLDER, "marksheets.db")
    if not os.path.exists(db_file):
        st.info("No database found yet.")
        return

    conn = sqlite3.connect(db_file)
    df = pd.read_sql_query("SELECT name, gpa as CGPA, college, result, backlogs FROM summary", conn)
    conn.close()

    if df.empty:
        st.warning("Database is empty.")
        return

    col1, col2 = st.columns(2)
    with col1:
        cgpa_filter = st.slider("Filter by CGPA ≥", 0.0, 10.0, 0.0, 0.1)
    with col2:
        college_filter = st.text_input("Filter by College (optional)")

    df['CGPA'] = pd.to_numeric(df['CGPA'], errors='coerce')
    filtered = df[df['CGPA'] >= cgpa_filter]

    if college_filter:
        filtered = filtered[filtered['college'].str.contains(college_filter, case=False)]

    st.dataframe(filtered.reset_index(drop=True))


# -------------------- MAIN APP --------------------
create_user_table()
st.set_page_config(page_title="Marksheet Analyzer", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["show_login"] = True
    st.session_state["show_signup"] = False

if st.session_state["logged_in"]:
    st.sidebar.success(f"👤 Welcome, {st.session_state['username']}")
    page = st.sidebar.radio("📌 Menu", ["📄 Marksheet Tool", "📊 View Database"])

    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.experimental_rerun()

    if page == "📄 Marksheet Tool":
        marksheet_tool()
    elif page == "📊 View Database":
        view_database()

else:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔓 Login"):
            st.session_state["show_login"] = True
            st.session_state["show_signup"] = False
    with col2:
        if st.button("📝 Signup"):
            st.session_state["show_signup"] = True
            st.session_state["show_login"] = False

    if st.session_state.get("show_signup"):
        signup_form()
    elif st.session_state.get("show_login"):
        login_form()
