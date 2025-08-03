import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from db import get_connection
from utils import format_date


def render():
    search_term = st.text_input("Search by Member Number")
    if search_term:
        render_schedule_results(search_term.strip())
    else:
        st.info("Enter a member number to search for their schedules.")


def render_schedule_results(search_term):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    schedules = pd.read_sql_query("""
        SELECT * FROM schedules 
        WHERE member_number LIKE ? 
        ORDER BY uploaded_at DESC
    """, conn, params=(f"%{search_term}%",))

    if schedules.empty:
        st.warning("No schedules found for that member number.")
        return

    for _, sched in schedules.iterrows():
        schedule_id = sched["id"]
        member_number = sched["member_number"]
        member_name = sched["member_name"]
        file_path = sched["file_path"]
        timestamp = datetime.strptime(sched["uploaded_at"], "%Y%m%d_%H%M%S")
        received_date = format_date(timestamp)

        with st.container():
    
            # Fetch current stage
            cursor.execute("""
                SELECT stage, handled_by, entered_at
                FROM schedule_stages
                WHERE schedule_id = ?
                ORDER BY entered_at DESC
                LIMIT 1
            """, (schedule_id,))
            current_stage = cursor.fetchone()

            if current_stage:
                stage = current_stage["stage"]
                handler = current_stage["handled_by"]
                entered = pd.to_datetime(current_stage["entered_at"])
                days = (datetime.now() - entered).days
                #st.success(f"🧭 Current Stage: {stage} (By: {handler}) — {days} day(s) ago")
                st.markdown(f"### {member_name} - {member_number} ({received_date})")
            else:
                st.info("🕐 Not yet tracked.")

            # Horizontal stage tracker
            all_stages = ["Compliance Officer", "Branch Manager", "Accountant", "Fully Processed"]
            cursor.execute("""
                SELECT stage, entered_at FROM schedule_stages
                WHERE schedule_id = ?
                ORDER BY entered_at ASC
            """, (schedule_id,))
            history = cursor.fetchall()
            completed_stages = [h["stage"] for h in history]

            # Render horizontal progress bar
            # Render horizontal progress bar with inferred progress
            st.markdown("""
                <style>
                .progress-container {
                    display: flex;
                    justify-content: space-between;
                    margin: 12px 0;
                }
                .stage-box {
                    flex: 1;
                    text-align: center;
                    padding: 10px;
                    margin: 0 5px;
                    border-radius: 6px;
                    border: 1px solid #ddd;
                    font-size: 14px;
                }
                .completed {
                    background-color: #4CAF50;
                    color: white;
                    font-weight: bold;
                }
                .current {
                    background-color: #fdd835;
                    color: black;
                    font-weight: bold;
                }
                </style>
            """, unsafe_allow_html=True)

            stages = ["Compliance Officer", "Branch Manager", "Accountant", "Fully Processed"]
            current_stage_index = stages.index(stage) if stage in stages else -1

            st.markdown("<div class='progress-container'>", unsafe_allow_html=True)
            for i, s in enumerate(stages):
                css_class = "stage-box"
                if i < current_stage_index:
                    css_class += " completed"
                elif i == current_stage_index:
                    css_class += " current"
                st.markdown(f"<div class='{css_class}'>{s}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


            # Timeline summary
            if history:
                st.markdown("### Timeline")
                timeline_data = []
                for i, row in enumerate(history):
                    start = pd.to_datetime(row["entered_at"])
                    end = pd.to_datetime(history[i + 1]["entered_at"]) if i + 1 < len(history) else datetime.now()
                    duration = (end - start).days
                    timeline_data.append({
                        "Stage": row["stage"],
                        "Entered At": format_date(start),
                        "Days at Stage": f"{duration} day(s)"
                    })

                df = pd.DataFrame(timeline_data)
                st.dataframe(df)

            # Stage Update Form
            with st.form(f"track_form_{schedule_id}"):
                new_stage = st.selectbox("Move to Stage", ["Compliance Officer", "Branch Manager", "Accountant", "Fully Processed"])
                handled_by = st.text_input("Handled by (name or ID)")
                if st.form_submit_button("📌 Update Stage"):
                    cursor.execute("""
                        INSERT INTO schedule_stages (schedule_id, stage, handled_by, entered_at)
                        VALUES (?, ?, ?, ?)
                    """, (schedule_id, new_stage, handled_by, datetime.now()))
                    conn.commit()
                    st.success("✅ Stage updated!")
                    st.rerun()

    conn.close()
