import streamlit as st
import pandas as pd
from db import get_connection

def render():
    st.subheader("📤 Bulk Upload Policies")

    with open("assets/bulk_policy_template.xlsx", "rb") as f:
        st.download_button("Download Excel Template", f, file_name="bulk_policy_template.xlsx")

    uploaded = st.file_uploader("Upload Completed Excel File", type=["xlsx"])

    if uploaded:
        try:
            df = pd.read_excel(uploaded)
            required_cols = [
                "employer_number", "employer_name", "member_number", "member_name", "id_number",
                "period_start", "period_end", "received_date",
                "compliance_officer_date", "branch_manager_date", "cash_office_date"
            ]

            if list(df.columns) != required_cols:
                st.error("❌ Incorrect column structure.")
                st.info(f"Expected columns: {required_cols}")
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
                st.success(f"✅ Uploaded {len(df)} policies successfully.")
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
