import streamlit as st
from streamlit_gsheets import GSheetsConnection
import ollama
import pandas as pd
import json
import os
import re
from docx import Document
from difflib import SequenceMatcher

# ==========================================
# 1. SIDEBAR & CREDITS
# ==========================================
with st.sidebar:
    st.title("🤖 Auditor Settings")
    st.info("**Version:** 2.1.0 (Enterprise)")
    st.markdown("---")
    st.subheader("Credits")
    st.write("Developed for Internal Office Use")
    st.caption("Built with ❤️ using Gemma 3 & Streamlit")
    st.markdown("---")
    
    # API Toggle Logic
    is_cloud = st.toggle("Connect to Cloud AI", value=False, help="Toggle OFF to use your local Office PC's GPU")
    api_url = st.secrets["CLOUD_AI_URL"] if is_cloud else "http://localhost:11434"
    st.success(f"Connected to: {'Cloud' if is_cloud else 'Local Office PC'}")

# ==========================================
# 2. GOOGLE SHEETS MEMORY (PERSISTENT)
# ==========================================
# This requires st-gsheets-connection in requirements.txt
conn = st.connection("gsheets", type=GSheetsConnection)

def get_memory_from_sheets():
    try:
        # Fetches rules from the 'Memory' tab of your linked Google Sheet
        df = conn.read(worksheet="Memory", ttl=0) # ttl=0 ensures fresh data
        return df['Rules'].tolist()
    except:
        return ["Ignore identical numerical changes (e.g. 200 to 200)."]

def save_rule_to_sheets(new_rules):
    current_rules = get_memory_from_sheets()
    updated_rules = list(set(current_rules + new_rules))
    df_to_save = pd.DataFrame(updated_rules, columns=["Rules"])
    conn.update(worksheet="Memory", data=df_to_save)
    st.cache_data.clear() # Clear cache to reflect new learning

# ==========================================
# 3. CORE AI LOGIC
# ==========================================
def agent_call(system, prompt):
    client = ollama.Client(host=api_url)
    res = client.generate(model="gemma3:4b", system=system, prompt=prompt, format="json")
    return json.loads(res['response'])

# [Extraction functions remain as provided in previous turns...]

# ==========================================
# 4. MAIN UI INTERFACE
# ==========================================
st.title("📂 Survey Change Auditor")
tab1, tab2 = st.tabs(["🚀 Audit Run", "🧠 Training & Memory"])

with tab1:
    # File uploaders and "Run Audit" button here
    # (Uses agent_call and displays results in a dataframe)
    st.write("Upload your files to begin the automated audit.")

with tab2:
    st.subheader("Current Learned Rules (from Google Sheets)")
    rules = get_memory_from_sheets()
    for r in rules:
        st.markdown(f"- {r}")
    
    if st.button("🔄 Sync with Google Sheets"):
        st.rerun()
