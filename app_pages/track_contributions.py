import streamlit as st
import pandas as pd
from db import get_connection
from utils import format_date

def render():
    st.subheader("🔍 Search Contributions by Member Number")

    member_number = st.text_input("Enter Member Number")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")

    if st.button("Search"):
        if member_number.strip() == "":
            st.warning("Please enter a valid Member Number.")
        elif start_date > end_date:
            st.warning("Start date cannot be after end date.")
        else:
            conn = get_connection()

            policy_query = '''SELECT id, member_name FROM policies WHERE member_number = ?'''
            policy = conn.execute(policy_query, (member_number.strip(),)).fetchone()

            if not policy:
                st.error("No policy found for that member number.")
            else:
                policy_id, member_name = policy

                contrib_query = '''
                    SELECT contribution_month, amount
                    FROM contributions
                    WHERE policy_id = ? AND contribution_month BETWEEN ? AND ?
                    ORDER BY contribution_month ASC
                '''
                df = pd.read_sql_query(contrib_query, conn, params=(policy_id, start_date, end_date))
                conn.close()

                st.markdown(f"### 🧑 Member: {member_name}")
                st.markdown(f"**Date Range:** {format_date(start_date)} to {format_date(end_date)}")

                if df.empty:
                    st.info("No contributions recorded in the selected date range.")
                else:
                    df["contribution_month"] = df["contribution_month"].apply(format_date)
                    df.columns = ["Contribution Month", "Amount"]
                    total = df["Amount"].sum()
                    st.markdown(f"**Total Contributions:** KES {total:,.2f}")
                    st.dataframe(df)
