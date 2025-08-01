import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
from db import get_connection
from utils import format_date
from styles import inject_custom_styles

# Set custom page title
st.set_page_config(
    page_title="NSSF Policy Tracker",
    page_icon="assets/small_logo.png",
    layout="wide"
)

st.markdown(inject_custom_styles(), unsafe_allow_html=True)


# Load logo
logo = Image.open("assets/nssf_logo.jpg")
st.image(logo, width=250)

st.title("NSSF Policy Tracker")

menu = ["View Policies", "Add Policy", "Track Contributions", "Add Contributions", "Bulk Upload", "All Policies"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Policy":
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

elif choice == "View Policies":
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

                # Fetch total contributions
                contrib_query = '''SELECT SUM(amount) FROM contributions WHERE policy_id = ?'''
                cur = conn.cursor()
                cur.execute(contrib_query, (policy_id,))
                total = cur.fetchone()[0]
                total_display = f"KES {total:,.2f}" if total else "No contributions yet"

                st.markdown(f"""
                <div class='policy-card'>
                    <table class='policy-table'>
                        <tr>
                            <td class='label'>Employer Number</td><td>{row['employer_number']}</td>
                            <td class='label'>Employer Name</td><td>{row['employer_name']}</td>
                        </tr>
                        <tr>
                            <td class='label'>Member Number</td><td>{row['member_number']}</td>
                            <td class='label'>Member Name</td><td>{row['member_name']}</td>
                        </tr>
                        <tr>
                            <td class='label'>ID Number</td><td>{row['id_number']}</td>
                            <td class='label'>Period Start</td><td>{format_date(row['period_start'])}</td>
                        </tr>
                        <tr>
                            <td class='label'>Period End</td><td>{format_date(row['period_end'])}</td>
                            <td class='label'>Received Date</td><td>{format_date(row['received_date'])}</td>
                        </tr>
                        <tr>
                            <td class='label'>Compliance Officer Date</td><td>{format_date(row['compliance_officer_date'])}</td>
                            <td class='label'>Branch Manager Date</td><td>{format_date(row['branch_manager_date'])}</td>
                        </tr>
                        <tr>
                            <td class='label'>Cash Office Date</td><td>{format_date(row['cash_office_date'])}</td>
                            <td class='label'>Total Contributions</td><td>{total_display}</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
        conn.close()



elif choice == "Track Contributions":
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

    st.subheader("View Contributions by Policy")
    policy_id = st.number_input("Enter Policy ID", min_value=1)
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    if st.button("Filter Contributions"):
        conn = get_connection()
        query = '''
            SELECT * FROM contributions
            WHERE policy_id = ? AND contribution_month BETWEEN ? AND ?
        '''
        df_contrib = pd.read_sql_query(query, conn, params=(policy_id, start_date, end_date))
        conn.close()
        st.dataframe(df_contrib)

elif choice == "Add Contributions":
    st.subheader("Add Contribution Record")

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

elif choice == "Bulk Upload":
    st.subheader("📤 Bulk Upload Policies")
    with open("assets/bulk_policy_template.xlsx", "rb") as f:
        st.download_button("Download Excel Template", f, file_name="bulk_policy_template.xlsx")

    uploaded_file = st.file_uploader("Upload Completed Excel File", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            expected_columns = [
                "employer_number", "employer_name", "member_number", "member_name", "id_number",
                "period_start", "period_end", "received_date",
                "compliance_officer_date", "branch_manager_date", "cash_office_date"
            ]

            if list(df.columns) != expected_columns:
                st.error("❌ The uploaded file does not match the required column structure.")
                st.info(f"Expected columns: {expected_columns}")
            else:
                conn = get_connection()
                cur = conn.cursor()

                for _, row in df.iterrows():
                    cur.execute('''INSERT INTO policies (
                        employer_number, employer_name, member_number, member_name, id_number,
                        period_start, period_end, received_date,
                        compliance_officer_date, branch_manager_date, cash_office_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (
                        str(row["employer_number"]),
                        str(row["employer_name"]),
                        str(row["member_number"]),
                        str(row["member_name"]),
                        str(row["id_number"]),
                        str(pd.to_datetime(row["period_start"]).date()),
                        str(pd.to_datetime(row["period_end"]).date()),
                        str(pd.to_datetime(row["received_date"]).date()),
                        str(pd.to_datetime(row["compliance_officer_date"]).date()),
                        str(pd.to_datetime(row["branch_manager_date"]).date()),
                        str(pd.to_datetime(row["cash_office_date"]).date())
                    ))

                conn.commit()
                conn.close()
                st.success(f"✅ Successfully uploaded {len(df)} policies.")

        except Exception as e:
            st.error(f"❌ Upload failed: {e}")

elif choice == "All Policies":
    st.subheader("📋 All Policies Table")
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM policies", conn)
    conn.close()
    st.dataframe(df)
