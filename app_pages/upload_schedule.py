import streamlit as st
import pandas as pd
import os
from datetime import datetime
from db import get_connection

def render():
    st.title("📤 Upload Contribution Schedule")

    uploaded_file = st.file_uploader("Upload Excel Schedule", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)

            required_columns = [
                "employer number", "member no", "year",
                "january", "february", "march", "april",
                "may", "june", "july", "august", "september",
                "october", "november", "december"
            ]
            missing_cols = [col for col in required_columns if col not in df.columns.str.lower()]
            if missing_cols:
                st.error(f"Missing required columns: {missing_cols}")
                return

            # Normalize column names
            df.columns = df.columns.str.strip().str.lower()

            conn = get_connection()
            cur = conn.cursor()

            inserted = 0
            for index, row in df.iterrows():
                employer_number = str(row['employer number']).strip()
                member_no = str(row['member no']).strip()
                year = int(row['year'])

                # Get the matching policy_id
                cur.execute(
                    "SELECT id, member_name FROM policies WHERE employer_number = ? AND member_number = ?",
                    (employer_number, member_no)
                )
                policy = cur.fetchone()

                if not policy:
                    st.warning(f"Policy not found for row {index+2}: Employer {employer_number}, Member {member_no}")
                    continue

                policy_id, member_name = policy

                month_map = {
                    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
                    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
                }

                for month_name, month_num in month_map.items():
                    amount = row.get(month_name)
                    if pd.notnull(amount) and float(amount) > 0:
                        contribution_date = datetime(year, month_num, 1)
                        cur.execute(
                            "INSERT INTO contributions (policy_id, contribution_month, amount) VALUES (?, ?, ?)",
                            (policy_id, contribution_date.strftime("%Y-%m-%d"), float(amount))
                        )
                        inserted += 1

            conn.commit()
            conn.close()

            st.success(f"✅ Successfully added {inserted} contribution records.")

            # Save file
            schedules_dir = "schedules"
            os.makedirs(schedules_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_name = f"{member_no} - {member_name} - {timestamp}.xlsx"
            save_path = os.path.join(schedules_dir, save_name)

            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success(f"📁 Schedule saved as: `{save_name}`")

            # ✅ INSERT into schedules table so it appears in tracking page
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO schedules (member_number, member_name, file_path, uploaded_at)
                VALUES (?, ?, ?, ?)
            ''', (member_no, member_name, save_name, timestamp))
            conn.commit()
            conn.close()

        except Exception as e:
            st.error(f"❌ Error processing file: {e}")
