import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="Job Hunter", page_icon="🚀")
st.title("J.TRAC")

# --- 1. CONNECT TO GOOGLE SHEET ---
# This looks for the [connections.gsheets] in your Secrets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # TTL=5 means it refreshes data every 5 seconds so you see updates instantly
    data = conn.read(worksheet="Sheet1", ttl=5)
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"⚠️ Error connecting to Sheets: {e}")
    st.stop()

# Initialize columns if the sheet is brand new/empty
expected_columns = ["Company", "Role", "Status", "Date", "Notes"]
if df.empty or not all(col in df.columns for col in expected_columns):
    df = pd.DataFrame(columns=expected_columns)

# --- 2. ADD NEW JOB SECTION ---
with st.expander("Add New Application", expanded=False):
    with st.form("job_form"):
        col1, col2 = st.columns(2)
        company = col1.text_input("Company Name")
        role = col2.text_input("Role")
        status = st.selectbox("Status", ["To Apply", "Applied", "Interview", "Rejected", "Offer"])
        notes = st.text_area("Notes (Location, POC, etc.)")
        
        submitted = st.form_submit_button("Save Job")
        
        if submitted and company:
            # Create a new row
            new_row = pd.DataFrame([{
                "Company": company,
                "Role": role,
                "Status": status,
                "Date": pd.Timestamp.now().strftime('%Y-%m-%d'),
                "Notes": notes
            }])
            
            # Combine old data with new row
            updated_df = pd.concat([df, new_row], ignore_index=True)
            
            # Push back to Google Sheets
            conn.update(worksheet="Sheet1", data=updated_df)
            
            st.success(f"Saved {company} to the Cloud!")
            st.rerun()

# --- 3. VIEW JOBS (The Dashboard) ---
st.subheader("My Applications")

if not df.empty:
    # Filter by Status
    all_statuses = df["Status"].unique().tolist()
    selected_status = st.multiselect("Filter by Status", all_statuses, default=all_statuses)
    
    view_df = df[df["Status"].isin(selected_status)]
    st.dataframe(view_df, use_container_width=True, hide_index=True)
    
    st.caption(f"Total Applications: {len(df)}")
else:
    st.info("No jobs added yet. Start applying!")

# --- 4. DELETE JOBS SECTION ---
with st.expander("Delete Jobs"):
    if not df.empty:
        # Create a specific list string to identify rows easily
        job_list = [f"{row['Company']} - {row['Role']}" for index, row in df.iterrows()]
        selected_to_delete = st.multiselect("Select jobs to remove:", job_list)
        
        if st.button("Confirm Delete"):
            if selected_to_delete:
                # Filter out the selected rows
                df['id_temp'] = df['Company'] + " - " + df['Role']
                updated_df = df[~df['id_temp'].isin(selected_to_delete)].drop(columns=['id_temp'])
                
                # Push update to Google Sheets
                conn.update(worksheet="Sheet1", data=updated_df)
                
                st.success("Deleted successfully!")
                st.rerun()
