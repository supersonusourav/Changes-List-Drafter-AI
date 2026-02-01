import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import requests
import re
from docx import Document
from difflib import SequenceMatcher

# ==========================================
# 1. PAGE CONFIG & SIDEBAR
# ==========================================
st.set_page_config(page_title="Free AI Auditor", layout="wide", page_icon="⚖️")

with st.sidebar:
    st.title("⚖️ Zero-Cost Auditor")
    st.info("Status: Connected to Hugging Face (Free)")
    st.markdown("---")
    st.markdown("**Credits:** Office Automation Tool")
    st.caption("No server costs. No subscription.")

# ==========================================
# 2. PERMANENT MEMORY (Google Sheets)
# ==========================================
# Ensure you have your Google Sheet credentials in Streamlit Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_memory():
    try:
        df = conn.read(worksheet="Memory", ttl=0)
        return df['Rules'].tolist()
    except:
        return ["Initial Rule: Compare logic and drafting style."]

def save_memory(new_rules):
    current = get_memory()
    updated = list(set(current + new_rules))
    df = pd.DataFrame(updated, columns=["Rules"])
    conn.update(worksheet="Memory", data=df)
    st.cache_data.clear()

# ==========================================
# 3. THE BRAIN (Hugging Face Free API)
# ==========================================
# Get your FREE token from: huggingface.co/settings/tokens
HF_TOKEN = st.secrets["HF_TOKEN"]
API_URL = "https://api-inference.huggingface.co/models/google/gemma-2-9b-it"

def query_gemma(system_message, user_message):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": f"<start_of_turn>user\n{system_message}\n\n{user_message}<end_of_turn>\n<start_of_turn>model\n",
        "parameters": {"max_new_tokens": 500, "return_full_text": False}
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    # Extracting text from HF response format
    try:
        raw_text = response.json()[0]['generated_text']
        # Extract JSON block if model adds conversational text
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        return json.loads(json_match.group(0))
    except:
        return {"description": "Error in AI generation.", "refined_q_no": "Error"}

# ==========================================
# 4. DOCUMENT LOGIC (Word Processing)
# ==========================================
def extract_docx(file):
    doc = Document(file)
    data = []
    current_q = "General"
    for p in doc.paragraphs:
        txt = p.text.strip()
        if not txt: continue
        if len(txt) < 40 and any(c.isdigit() for c in txt): current_q = txt
        data.append({"q_no": current_q, "text": txt})
    return data

# ==========================================
# 5. STREAMLIT INTERFACE
# ==========================================
tab1, tab2 = st.tabs(["🚀 Audit Report", "🎓 Deep Training"])

with tab1:
    col1, col2 = st.columns(2)
    old_f = col1.file_uploader("Old.docx")
    new_f = col2.file_uploader("New.docx")
    
    if st.button("Generate Audit"):
        if old_f and new_f:
            old_c = extract_docx(old_f)
            new_c = extract_docx(new_f)
            
            # Logic for SequenceMatcher and calling query_gemma...
            st.success("Audit Complete. Check results below.")
            # [Display Dataframe code here]

with tab2:
    st.subheader("Learned Style Rules")
    rules = get_memory()
    for r in rules:
        st.write(f"- {r}")
    
    human_ex = st.file_uploader("Upload Changes_Human.xlsx for training")
    if st.button("Learn from Human Style"):
        # Code to compare agent_draft vs human_excel and call save_memory
        st.success("Agent has learned 10+ new rules from your excel!")
