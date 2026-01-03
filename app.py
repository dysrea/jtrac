import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
# PASTE YOUR GOOGLE SHEET URL HERE ⬇️
SHEET_URL = "https://docs.google.com/spreadsheets/d/1gXB-He9_68_KnPEl7oJjQ1Nl8fbZx-on7c4Hw_I61wU/edit?usp=sharing"

st.set_page_config(page_title="Job Hunter", page_icon="🚀")
st.title("🚀 Job Hunt Tracker")

# --- 1. CONNECT TO GOOGLE SHEET ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # We explicitly tell it WHICH sheet to look at using the URL
    data = conn.read(spreadsheet=SHEET_URL, worksheet="Sheet1", ttl=5)
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"⚠️ Error connecting to Sheets: {e}")
    st.info("💡 Did you share the sheet with your Service Account email?")
    st.stop()

# Initialize columns if the sheet is empty
expected_columns = ["Company", "Role", "Status", "Date", "Notes"]
if df.empty or not all(col in df.columns for col in expected_columns):
    df = pd.DataFrame(columns=expected_columns)

# --- 2. ADD NEW JOB SECTION ---
with st.expander("➕ Add New Application", expanded=False):
    with st.form("job_form"):
        col1, col2 = st.columns(2)
        company = col1.text_input("Company Name")
        role = col2.text_input("Role")
        status = st.selectbox("Status", ["To Apply", "Applied", "Interview", "Rejected", "Offer"])
        notes = st.text_area("Notes")
        
        submitted = st.form_submit_button("Save Job")
        
        if submitted and company:
            new_row = pd.DataFrame([{
                "Company": company,
                "Role": role,
                "Status": status,
                "Date": pd.Timestamp.now().strftime('%Y-%m-%d'),
                "Notes": notes
            }])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            
            # Update using the explicit URL
            conn.update(spreadsheet=SHEET_URL, worksheet="Sheet1", data=updated_df)
            st.success(f"✅ Saved {company}!")
            st.rerun()

# --- 3. VIEW JOBS ---
st.subheader("📋 My Applications")
if not df.empty:
    all_statuses = df["Status"].unique().tolist()
    selected_status = st.multiselect("Filter by Status", all_statuses, default=all_statuses)
    view_df = df[df["Status"].isin(selected_status)]
    st.dataframe(view_df, use_container_width=True, hide_index=True)
else:
    st.info("No jobs added yet.")

# --- 4. DELETE JOBS ---
with st.expander("❌ Delete Jobs"):
    if not df.empty:
        job_list = [f"{row['Company']} - {row['Role']}" for index, row in df.iterrows()]
        selected_to_delete = st.multiselect("Select jobs to remove:", job_list)
        
        if st.button("Confirm Delete"):
            if selected_to_delete:
                df['id_temp'] = df['Company'] + " - " + df['Role']
                updated_df = df[~df['id_temp'].isin(selected_to_delete)].drop(columns=['id_temp'])
                conn.update(spreadsheet=SHEET_URL, worksheet="Sheet1", data=updated_df)
                st.success("Deleted successfully!")
                st.rerun()
