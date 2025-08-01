import streamlit as st
import pandas as pd
from db import init_db, get_connection
from datetime import date
from PIL import Image

init_db()
logo = Image.open("assets/nssf_logo.jpg")

st.image(logo, width=250)  # You can adjust width
st.title("NSSF Policy Tracker")


menu = ["Add Policy", "View Policies", "Track Contributions", "Add Contributions"]
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
        # --- Show total contributions per policy ---
    st.subheader("🔢 Total Contributions Summary")

    conn = get_connection()
    query = '''
        SELECT 
            p.id AS policy_id,
            p.member_name,
            SUM(c.amount) AS total_contribution
        FROM policies p
        LEFT JOIN contributions c ON p.id = c.policy_id
        GROUP BY p.id, p.member_name
        ORDER BY total_contribution DESC
    '''
    df_summary = pd.read_sql_query(query, conn)
    df_summary["total_contribution"] = df_summary["total_contribution"].fillna(0.0)
    st.dataframe(df_summary)
    conn.close()

    policy_id = st.number_input("Enter Policy ID", min_value=1, step=1)
    date_range = st.date_input("Select Date Range", [date(2000,1,1), date.today()])
    if st.button("Fetch Contributions"):
        conn = get_connection()
        query = '''SELECT * FROM contributions WHERE policy_id = ? AND contribution_month BETWEEN ? AND ?'''
        df = pd.read_sql_query(query, conn, params=(policy_id, date_range[0].isoformat(), date_range[1].isoformat()))
        st.dataframe(df)
elif choice == "Add Contributions":
    st.subheader("Add Contribution Record")

    conn = get_connection()
    cursor = conn.cursor()

    # Fetch policy options
    cursor.execute("SELECT id, member_name, member_number FROM policies")
    policies = cursor.fetchall()

    if not policies:
        st.warning("No policies found. Please add a policy first.")
    else:
        policy_options = {f"{p[1]} ({p[2]}) [ID: {p[0]}]": p[0] for p in policies}
        selected_policy = st.selectbox("Select Policy", list(policy_options.keys()))
        policy_id = policy_options[selected_policy]

        # Contribution form
        with st.form("contribution_form"):
            contrib_month = st.date_input("Contribution Month")
            amount = st.number_input("Amount", min_value=0.0, step=100.0)
            submitted = st.form_submit_button("Add Contribution")

            if submitted:
                cursor.execute(
                    "INSERT INTO contributions (policy_id, contribution_month, amount) VALUES (?, ?, ?)",
                    (policy_id, contrib_month.isoformat(), amount)
                )
                conn.commit()
                st.success("Contribution added successfully")
    conn.close()
