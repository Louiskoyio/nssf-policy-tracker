import streamlit as st
import pandas as pd
from db import get_connection
from utils import format_date

def render():
    st.subheader("🔍 Search Policy by Member Number or ID")
    search = st.text_input("Enter Member Number or ID Number")

    if st.button("Search"):
        conn = get_connection()
        query = '''SELECT * FROM policies WHERE member_number LIKE ? OR id_number LIKE ?'''
        df = pd.read_sql_query(query, conn, params=(f"%{search}%", f"%{search}%"))

        if df.empty:
            st.warning("No policy found.")
        else:
            for _, row in df.iterrows():
                policy_id = row["id"]
                contrib_query = '''SELECT SUM(amount) FROM contributions WHERE policy_id = ?'''
                cur = conn.cursor()
                cur.execute(contrib_query, (policy_id,))
                total = cur.fetchone()[0]
                total_display = f"KES {total:,.2f}" if total else "No contributions yet"

                st.markdown(f"""
                <div class='policy-card'>
                    <table class='policy-table'>
                        <tr><td class='label'>Employer Number</td><td>{row['employer_number']}</td>
                        <td class='label'>Employer Name</td><td>{row['employer_name']}</td></tr>
                        <tr><td class='label'>Member Number</td><td>{row['member_number']}</td>
                        <td class='label'>Member Name</td><td>{row['member_name']}</td></tr>
                        <tr><td class='label'>ID Number</td><td>{row['id_number']}</td>
                        <td class='label'>Period Start</td><td>{format_date(row['period_start'])}</td></tr>
                        <tr><td class='label'>Period End</td><td>{format_date(row['period_end'])}</td>
                        <td class='label'>Received Date</td><td>{format_date(row['received_date'])}</td></tr>
                        <tr><td class='label'>Compliance Officer Date</td><td>{format_date(row['compliance_officer_date'])}</td>
                        <td class='label'>Branch Manager Date</td><td>{format_date(row['branch_manager_date'])}</td></tr>
                        <tr><td class='label'>Cash Office Date</td><td>{format_date(row['cash_office_date'])}</td>
                        <td class='label'>Total Contributions</td><td>{total_display}</td></tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
        conn.close()
