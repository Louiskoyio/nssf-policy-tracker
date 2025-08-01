import streamlit as st
import pandas as pd
from db import init_db, get_connection
from datetime import date
from PIL import Image

init_db()
logo = Image.open("assets/nssf_logo.jpg")

st.image(logo, width=250)  # You can adjust width
st.title("📅 NSSF Policy Tracker")


menu = ["Add Policy", "View Policies", "Track Contributions"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Policy":
    st.subheader("Register a New Policy")
    with st.form("policy_form"):
        employer_number = st.text_input("Employer Number")
        employer_name = st.text_input("Employer Name")
        member_number = st.text_input("Member Number")
        member_name = st.text_input("Member Name")
        id_number = st.text_input("ID Number")
        period_start = st.date_input("Period Start")
        period_end = st.date_input("Period End")
        received_date = st.date_input("Received at Office")
        compliance_date = st.date_input("Issued to Compliance Officer")
        branch_date = st.date_input("Moved to Branch Manager")
        cash_date = st.date_input("Finalised at Cash Office")

        submitted = st.form_submit_button("Save Policy")
        if submitted:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('''INSERT INTO policies (
                employer_number, employer_name, member_number, member_name, id_number,
                period_start, period_end, received_date,
                compliance_officer_date, branch_manager_date, cash_office_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (employer_number, employer_name, member_number, member_name, id_number,
             period_start.isoformat(), period_end.isoformat(),
             received_date.isoformat(), compliance_date.isoformat(),
             branch_date.isoformat(), cash_date.isoformat()))
            conn.commit()
            conn.close()
            st.success("Policy registered successfully")

elif choice == "View Policies":
    st.subheader("Search and View Policies")
    search_term = st.text_input("Search by Member Number or ID")
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM policies", conn)
    if search_term:
        df = df[df['member_number'].str.contains(search_term) | df['id_number'].str.contains(search_term)]
    st.dataframe(df)

elif choice == "Track Contributions":
    st.subheader("View Contributions by Policy")
    policy_id = st.number_input("Enter Policy ID", min_value=1, step=1)
    date_range = st.date_input("Select Date Range", [date(2000,1,1), date.today()])
    if st.button("Fetch Contributions"):
        conn = get_connection()
        query = '''SELECT * FROM contributions WHERE policy_id = ? AND contribution_month BETWEEN ? AND ?'''
        df = pd.read_sql_query(query, conn, params=(policy_id, date_range[0].isoformat(), date_range[1].isoformat()))
        st.dataframe(df)
