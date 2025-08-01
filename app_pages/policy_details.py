# app_pages/policy_details.py

import streamlit as st
import pandas as pd
from db import get_connection
from utils import format_date

def render():
    st.subheader("📄 Policy Details")

    # Get query params from URL
    query_params = st.query_params
    policy_id = query_params.get("policy_id", [None])[0]

    if not policy_id:
        st.error("❌ No policy ID provided in the URL.")
        return

    conn = get_connection()

    # Fetch policy details
    policy_query = "SELECT * FROM policies WHERE id = ?"
    policy = conn.execute(policy_query, (policy_id,)).fetchone()

    if not policy:
        st.error("Policy not found.")
        return

    columns = [desc[0] for desc in conn.execute(policy_query, (policy_id,)).description]
    policy_dict = dict(zip(columns, policy))

    # Display Policy Info
    st.markdown("### 🧾 Policy Information")
    for label, value in policy_dict.items():
        if "date" in label or "period" in label:
            value = format_date(value)
        st.markdown(f"**{label.replace('_', ' ').title()}**: {value}")

    # Fetch contributions
    st.markdown("### 💰 Contribution History")
    contrib_query = "SELECT contribution_month, amount FROM contributions WHERE policy_id = ? ORDER BY contribution_month"
    df_contrib = pd.read_sql_query(contrib_query, conn, params=(policy_id,))
    conn.close()

    if df_contrib.empty:
        st.info("No contributions recorded.")
    else:
        df_contrib["contribution_month"] = df_contrib["contribution_month"].apply(format_date)
        df_contrib.columns = ["Contribution Month", "Amount"]
        total = df_contrib["Amount"].sum()
        st.markdown(f"**Total Contributions:** KES {total:,.2f}")
        st.dataframe(df_contrib)
