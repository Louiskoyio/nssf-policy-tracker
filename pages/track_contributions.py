import streamlit as st
import pandas as pd
from db import get_connection

def track_contributions():
    st.subheader("🔢 Total Contributions Summary")

    conn = get_connection()
    summary_query = '''
        SELECT p.id AS policy_id, p.member_name,
               SUM(c.amount) AS total_contribution
        FROM policies p
        LEFT JOIN contributions c ON p.id = c.policy_id
        GROUP BY p.id, p.member_name
        ORDER BY total_contribution DESC
    '''
    df_summary = pd.read_sql_query(summary_query, conn)
    df_summary["total_contribution"] = df_summary["total_contribution"].fillna(0.0)
    st.dataframe(df_summary)

    st.subheader("📆 View Contributions by Policy")
    policy_id = st.number_input("Enter Policy ID", min_value=1)
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")

    if st.button("Filter Contributions"):
        contrib_query = '''
            SELECT * FROM contributions
            WHERE policy_id = ? AND contribution_month BETWEEN ? AND ?
        '''
        df_contrib = pd.read_sql_query(contrib_query, conn, params=(policy_id, start_date, end_date))
        st.dataframe(df_contrib)

    conn.close()
