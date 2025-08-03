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
            st.title(f"{member_name} - {member_number} ({received_date})")

            # Fetch current stage
            cursor.execute("""
                SELECT stage, handled_by, entered_at
                FROM schedule_stages
                WHERE schedule_id = ?
                ORDER BY entered_at DESC
                LIMIT 1
            """, (schedule_id,))
            current_stage = cursor.fetchone()

            all_stages = ["Compliance Officer", "Branch Manager", "Accountant", "Fully Processed"]
            stage = current_stage["stage"] if current_stage else None
            current_stage_index = all_stages.index(stage) if stage in all_stages else -1

            # Stage progress bar
            cursor.execute("""
                SELECT stage, entered_at FROM schedule_stages
                WHERE schedule_id = ?
                ORDER BY entered_at ASC
            """, (schedule_id,))
            history = cursor.fetchall()

            st.markdown("""
                <style>
                .progress-bar {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin: 20px 0;
                }
                .stage {
                    flex-grow: 1;
                    text-align: center;
                    padding: 10px;
                    margin-right: 4px;
                    border-radius: 6px;
                    font-size: 13px;
                    color: white;
                    background-color: #ccc;
                    position: relative;
                }
                .stage.completed {
                    background-color: #4CAF50;
                }
                .stage.current {
                    background-color: #fdd835;
                    color: black;
                    font-weight: bold;
                }
                .stage::after {
                    content: '';
                    position: absolute;
                    top: 50%;
                    right: -2px;
                    transform: translateY(-50%);
                    height: 100%;
                    width: 4px;
                    background-color: white;
                    z-index: 1;
                }
                .stage:last-child::after {
                    display: none;
                }
                .custom-clickable {
                    display: inline-block;
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                    cursor: pointer;
                    transition: 0.3s ease;
                    margin-top: 10px;
                }
                .custom-clickable:hover {
                    background-color: #c1d62f;
                    color: black;
                }
                </style>
            """, unsafe_allow_html=True)

            # Render horizontal progress bar
            progress_html = "<div class='progress-bar'>"
            for i, s in enumerate(all_stages):
                if i < current_stage_index:
                    css_class = "stage completed"
                elif i == current_stage_index:
                    css_class = "stage current"
                else:
                    css_class = "stage"
                progress_html += f"<div class='{css_class}'>{s}</div>"
            progress_html += "</div>"
            st.markdown(progress_html, unsafe_allow_html=True)

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
                table_html = """
                <table class="custom-timeline-table">
                    <thead>
                        <tr>
                """
                for col in df.columns:
                    table_html += f"<th>{col}</th>"
                table_html += "</tr></thead><tbody>"
                for _, row in df.iterrows():
                    table_html += "<tr>"
                    for col in df.columns:
                        table_html += f"<td>{row[col]}</td>"
                    table_html += "</tr>"
                table_html += "</tbody></table>"

                st.markdown("""
                    <style>
                    .custom-timeline-table {
                        border-collapse: collapse;
                        width: 100%;
                        margin-top: 10px;
                    }
                    .custom-timeline-table th {
                        background-color: #c1d72d; 
                        color: black;
                        font-weight: bold;
                        padding: 8px;
                        text-align: left;
                    }
                    .custom-timeline-table td {
                        padding: 8px;
                        border: 1px solid #ddd;
                    }
                    </style>
                """, unsafe_allow_html=True)
                st.markdown(table_html, unsafe_allow_html=True)

            # Auto-progress button logic
            if current_stage_index < len(all_stages) - 1:
                next_stage = all_stages[current_stage_index + 1]
    

                # Use clickable div as a button
                if st.button(f"Move to {next_stage}"):
                    cursor.execute("""
                        INSERT INTO schedule_stages (schedule_id, stage, handled_by, entered_at)
                        VALUES (?, ?, ?, ?)
                    """, (schedule_id, next_stage, "System", datetime.now()))
                    conn.commit()
                    st.success(f"✅ Moved to stage: {next_stage}")
                    st.rerun()
            else:
                st.success("🎉 This schedule is fully processed.")

    conn.close()
