import streamlit as st
from db import get_connection

def render():
    st.subheader("Add New Policy")
    with st.form("policy_form"):
        employer_number = st.text_input("Employer Number")
        employer_name = st.text_input("Employer Name")
        member_number = st.text_input("Member Number")
        member_name = st.text_input("Member Name")
        id_number = st.text_input("ID Number")
        period_start = st.date_input("Period Start")
        period_end = st.date_input("Period End")
        received_date = st.date_input("Received Date")
        compliance_officer_date = st.date_input("Compliance Officer Date")
        branch_manager_date = st.date_input("Branch Manager Date")
        cash_office_date = st.date_input("Cash Office Date")
        submit = st.form_submit_button("Add Policy")

        if submit:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO policies (
                employer_number, employer_name, member_number, member_name, id_number,
                period_start, period_end, received_date,
                compliance_officer_date, branch_manager_date, cash_office_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                employer_number, employer_name, member_number, member_name, id_number,
                period_start, period_end, received_date,
                compliance_officer_date, branch_manager_date, cash_office_date
            ))
            conn.commit()
            conn.close()
            st.success("Policy added successfully")
