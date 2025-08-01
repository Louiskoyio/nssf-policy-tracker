import streamlit as st
import pandas as pd
from db import get_connection
from utils import format_date

def render_policy_details(policy_id: int):
    st.write(f"Rendering details for policy ID: {policy_id}")  # Debug

    conn = get_connection()
    cursor = conn.cursor()

    # Fetch policy details
    cursor.execute("SELECT * FROM policies WHERE id = ?", (policy_id,))
    row = cursor.fetchone()

    if not row:
        st.error("⚠️ No policy found with that ID.")
        return

    columns = [desc[0] for desc in cursor.description]
    policy = dict(zip(columns, row))

    st.subheader(f"{policy['member_name']} ({policy['member_number']})")

    # Render policy info card
    st.markdown(f"""
    <div class='policy-card'>
        <table class='policy-table'>
            <tr>
                <td class='label'>Employer Number</td><td>{policy['employer_number']}</td>
                <td class='label'>Employer Name</td><td>{policy['employer_name']}</td>
            </tr>
            <tr>
                <td class='label'>Period Start</td><td>{format_date(policy['period_start'])}</td>
                <td class='label'>Period End</td><td>{format_date(policy['period_end'])}</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    # Contributions
    df = pd.read_sql_query(
        "SELECT * FROM contributions WHERE policy_id = ?",
        conn, params=(policy_id,)
    )

    total = df["amount"].sum() if not df.empty else 0
    st.markdown(f"### 💰 Total Contributions: KES {total:,.2f}")

    if not df.empty:
        df["contribution_month"] = pd.to_datetime(df["contribution_month"])
        df = df.sort_values("contribution_month")
        df["contribution_month"] = df["contribution_month"].dt.strftime("%b %Y")
        st.dataframe(df)

    conn.close()
