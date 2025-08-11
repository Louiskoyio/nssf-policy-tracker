import streamlit as st
import pandas as pd
import os
from datetime import datetime
from db import get_connection

def render():
    excel_file = st.file_uploader("Upload Excel Schedule", type=["xlsx"])
    pdf_file = st.file_uploader("Upload Original PDF", type=["pdf"])

    if excel_file and pdf_file:
        try:
            # Try reading the Excel
            df = pd.read_excel(excel_file)
            df.columns = df.columns.str.strip().str.lower()

            required_columns = [
                "employer number", "member no", "year",
                "january", "february", "march", "april",
                "may", "june", "july", "august", "september",
                "october", "november", "december"
            ]
            
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                st.error(f"❌ Missing required columns: {missing_cols}")
                return

            conn = get_connection()
            cur = conn.cursor()

            inserted = 0
            member_no = None
            member_name = None

            for index, row in df.iterrows():
                employer_number = str(row['employer number']).strip()
                member_no = str(row['member no']).strip()
                year = int(row['year'])

                cur.execute(
                    "SELECT id, member_name FROM policies WHERE employer_number = ? AND member_number = ?",
                    (employer_number, member_no)
                )
                policy = cur.fetchone()

                if not policy:
                    st.warning(f"⚠️ Policy not found for row {index+2}: Employer {employer_number}, Member {member_no}")
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

            if inserted == 0:
                st.warning("⚠️ No valid contributions found. Upload skipped.")
                return

            st.success(f"✅ Successfully added {inserted} contribution records.")

            # Save both files
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"{member_no} - {member_name}"
            folder_path = os.path.join("schedules", folder_name)
            os.makedirs(folder_path, exist_ok=True)

            excel_filename = f"{member_no} - {member_name} - {timestamp}.xlsx"
            pdf_filename = f"{member_no} - {member_name} - {timestamp}.pdf"

            excel_path = os.path.join(folder_path, excel_filename)
            pdf_path = os.path.join(folder_path, pdf_filename)

            with open(excel_path, "wb") as f:
                f.write(excel_file.getbuffer())

            with open(pdf_path, "wb") as f:
                f.write(pdf_file.getbuffer())

            st.success(f"📁 Files saved in `{folder_name}/` as:")
            st.code(excel_filename)
            st.code(pdf_filename)

            # Save to schedules table
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO schedules (member_number, member_name, file_path, uploaded_at)
                VALUES (?, ?, ?, ?)
            ''', (member_no, member_name, excel_filename, timestamp))

            schedule_id = cur.lastrowid
            cur.execute('''
                INSERT INTO schedule_stages (schedule_id, stage, handled_by, entered_at)
                VALUES (?, ?, ?, ?)
            ''', (schedule_id, "Compliance Officer", "System", datetime.now()))

            conn.commit()
            conn.close()

        except Exception as e:
            st.error(f"❌ Error processing upload: {e}")
    elif excel_file or pdf_file:
        st.info("📎 Please upload both the Excel schedule and the original PDF before submitting.")
