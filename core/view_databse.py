import streamlit as st
import sqlite3
import pandas as pd
import os

DB_PATH = "output/marksheets.db"

st.set_page_config(page_title="📋 View Database", layout="centered")

st.title("📋 Stored Marksheet Records")

if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM summary", conn)
    conn.close()

    st.dataframe(df, use_container_width=True)
    st.success(f"✅ Total Records: {len(df)}")
else:
    st.warning("⚠️ No database found. Please process marksheets first.")
