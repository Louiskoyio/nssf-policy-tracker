import streamlit as st
import pandas as pd
from db import get_connection
from datetime import datetime

def render():
    st.title("📊 Track Schedule Progress")

    conn = get_connection()

    schedules = pd.read_sql_query("SELECT * FROM schedules ORDER BY uploaded_at DESC", conn)

    if schedules.empty:
        st.info("No schedules uploaded yet.")
        return

    for _, row in schedules.iterrows():
        st.markdown(f"### 🗂️ Schedule: {row['member_name']} ({row['member_number']})")
        st.write(f"Uploaded at: {row['uploaded_at']}")
        st.write(f"File: {row['file_path']}")

        stage_query = '''
        SELECT * FROM schedule_stages
        WHERE schedule_id = ?
        ORDER BY entered_at DESC
        LIMIT 1
        '''
        cur = conn.cursor()
        cur.execute(stage_query, (row['id'],))
        current_stage = cur.fetchone()

        if current_stage:
            st.success(f"🧭 Current Stage: {current_stage[0]} (By: {current_stage[1]})")
            entered = pd.to_datetime(current_stage["entered_at"])
            elapsed = (datetime.now() - entered).days
            st.write(f"⏱️ Days at stage: {elapsed}")
        else:
            st.warning("Schedule not yet moved through any stage.")

        with st.expander("📜 View Full History"):
            history = pd.read_sql_query("SELECT * FROM schedule_stages WHERE schedule_id = ?", conn, params=(row['id'],))
            if history.empty:
                st.write("No history recorded.")
            else:
                st.dataframe(history)

        st.markdown("---")

        with st.form(f"move_stage_form_{row['id']}"):
            st.write("➡️ Move to Next Stage")
            next_stage = st.selectbox("Next Stage", ["Compliance Officer", "Branch Manager", "Accountant"])
            handler = st.text_input("Handled By")
            submit = st.form_submit_button("Move")

            if submit:
                now = datetime.now()

                # Exit current stage
                if current_stage:
                    exit_query = '''
                        UPDATE schedule_stages
                        SET exited_at = ?, duration_days = ?
                        WHERE id = ?
                    '''
                    duration = (now - pd.to_datetime(current_stage["entered_at"])).days
                    cur.execute(exit_query, (now, duration, current_stage["id"]))

                # Insert new stage
                insert_query = '''
                    INSERT INTO schedule_stages (schedule_id, stage, entered_at, handled_by)
                    VALUES (?, ?, ?, ?)
                '''
                cur.execute(insert_query, (row["id"], next_stage, now, handler))
                conn.commit()
                st.success("Stage moved successfully!")
                st.rerun()


    conn.close()
