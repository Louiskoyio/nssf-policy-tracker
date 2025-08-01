import streamlit as st
import pandas as pd
from db import get_connection
from utils import format_date
import sqlite3


def render():
    st.subheader("🔍 Search Policy by Member Number or ID")

    # Session state for search and expanded cards
    if "search_term" not in st.session_state:
        st.session_state.search_term = ""
    if "search_triggered" not in st.session_state:
        st.session_state.search_triggered = False
    if "expanded_cards" not in st.session_state:
        st.session_state.expanded_cards = set()

    # Search input
    search = st.text_input("Enter Member Number or ID Number", value=st.session_state.search_term)

    # Handle search button click
    if st.button("Search"):
        st.session_state.search_term = search
        st.session_state.search_triggered = True

    # Only render results if search was triggered
    if st.session_state.search_triggered and st.session_state.search_term.strip() != "":
        render_search_results(st.session_state.search_term.strip())


def render_search_results(search_term):
    conn = get_connection()
    query = '''SELECT * FROM policies WHERE member_number LIKE ? OR id_number LIKE ?'''
    df = pd.read_sql_query(query, conn, params=(f"%{search_term}%", f"%{search_term}%"))

    if df.empty:
        st.warning("No policy found.")
        return

    for _, row in df.iterrows():
        policy_id = row["id"]
        contrib_query = '''SELECT SUM(amount) FROM contributions WHERE policy_id = ?'''
        cur = conn.cursor()
        cur.execute(contrib_query, (policy_id,))
        total = cur.fetchone()[0]
        total_display = f"KES {total:,.2f}" if total else "No contributions yet"

        # Check if this card is expanded
        is_expanded = policy_id in st.session_state.expanded_cards

        with st.container():
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

            toggle_label = "🔽 Show More" if not is_expanded else "🔼 Show Less"
            if st.button(toggle_label, key=f"toggle_{policy_id}"):
                if is_expanded:
                    st.session_state.expanded_cards.remove(policy_id)
                else:
                    st.session_state.expanded_cards.add(policy_id)
                st.rerun()


            # If expanded, show detailed section
            if is_expanded:
                show_extra_details(policy_id, conn)

    conn.close()


def show_extra_details(policy_id, conn):
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    policy = cursor.execute("SELECT * FROM policies WHERE id = ?", (policy_id,)).fetchone()
    contributions = pd.read_sql_query("SELECT * FROM contributions WHERE policy_id = ?", conn, params=(policy_id,))

    st.markdown(f"### 👤 {policy['member_name']} ({policy['member_number']})")
    st.markdown(f"**Employer:** {policy['employer_name']} ({policy['employer_number']})")
    st.markdown(f"**ID Number:** {policy['id_number']}")

    st.markdown("### 🗓️ Dates")
    st.write(f"Period: {format_date(policy['period_start'])} to {format_date(policy['period_end'])}")
    st.write(f"Received Date: {format_date(policy['received_date'])}")
    st.write(f"Compliance Officer Date: {format_date(policy['compliance_officer_date'])}")
    st.write(f"Branch Manager Date: {format_date(policy['branch_manager_date'])}")
    st.write(f"Cash Office Date: {format_date(policy['cash_office_date'])}")

    st.markdown("### 💰 Contributions")
    if contributions.empty:
        st.info("No contributions recorded yet.")
    else:
        contributions["contribution_month"] = contributions["contribution_month"].apply(format_date)
        df = contributions[["contribution_month", "amount"]]
        df.columns = ["Month", "Amount"]
        st.dataframe(df)
        total = df["Amount"].sum()
        st.success(f"Total Contributions: KES {total:,.2f}")
