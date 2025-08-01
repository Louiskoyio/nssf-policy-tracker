import streamlit as st
from db import get_connection

def add_contributions():
    st.subheader("➕ Add Contribution Record")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, member_name, member_number FROM policies")
    policies = cursor.fetchall()

    if not policies:
        st.warning("No policies found. Please add a policy first.")
    else:
        policy_options = {f"{p[1]} ({p[2]}) [ID: {p[0]}]": p[0] for p in policies}
        selected_policy = st.selectbox("Select Policy", list(policy_options.keys()))
        policy_id = policy_options[selected_policy]

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
