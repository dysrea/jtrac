import streamlit as st
import pandas as pd
import os

# File to store data (acts as your database)
DB_FILE = 'job_applications.csv'

# Initialize CSV if it doesn't exist
if not os.path.exists(DB_FILE):
    df = pd.DataFrame(columns=["Company", "Role", "Status", "Date", "Notes"])
    df.to_csv(DB_FILE, index=False)

st.title("J.TRAC")

# --- SECTION 1: ADD NEW JOB ---
with st.expander("Add New Application", expanded=True):
    with st.form("job_form"):
        col1, col2 = st.columns(2)
        company = col1.text_input("Company Name")
        role = col2.text_input("Role (e.g., Firmware Eng)")
        status = st.selectbox("Status", ["To Apply", "Applied", "Interview", "Rejected", "Offer"])
        notes = st.text_area("Notes (Location, Contact, etc.)")
        
        submitted = st.form_submit_button("Save Job")
        if submitted and company:
            new_data = pd.DataFrame({
                "Company": [company],
                "Role": [role],
                "Status": [status],
                "Date": [pd.Timestamp.now().strftime('%Y-%m-%d')],
                "Notes": [notes]
            })
            # Append to CSV
            new_data.to_csv(DB_FILE, mode='a', header=False, index=False)
            st.success(f"Added {company}!")
            st.rerun()

# --- SECTION 2: VIEW JOBS ---
st.subheader("My Applications")
if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
    
    # Filter options
    filter_status = st.multiselect("Filter by Status", df["Status"].unique(), default=df["Status"].unique())
    view_df = df[df["Status"].isin(filter_status)]
    
    st.dataframe(view_df, use_container_width=True)

    # Simple Stats

    st.metric("Total Applications", len(df))

# --- SECTION 3: DELETE JOBS ---
with st.expander("Manage & Delete Jobs"):
    if os.path.exists(DB_FILE):
        # Load current data
        df = pd.read_csv(DB_FILE)
        
        # Create a dropdown to select companies to delete
        # We use a list of "Company - Role" so you don't accidentally delete the wrong "Google" entry
        job_list = [f"{row['Company']} - {row['Role']}" for index, row in df.iterrows()]
        selected_to_delete = st.multiselect("Select jobs to delete:", job_list)
        
        if st.button("❌ Delete Selected Jobs"):
            if selected_to_delete:
                # Logic: Keep rows that are NOT in the selected list
                # We rebuild the string identifier to match
                df['id_temp'] = df['Company'] + " - " + df['Role']
                df = df[~df['id_temp'].isin(selected_to_delete)]
                df = df.drop(columns=['id_temp'])
                
                # Save back to CSV
                df.to_csv(DB_FILE, index=False)
                st.success("Deleted successfully!")
                st.rerun()
            else:
                st.warning("Select a job first.")

