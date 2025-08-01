import streamlit as st
import pandas as pd
from db import get_connection
from utils import format_date

def render():
    st.subheader("📋 All Policies Table")

    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM policies", conn)
    conn.close()

    df.columns = [col.replace("_", " ").title() for col in df.columns]
    date_columns = [
        "Period Start", "Period End", "Received Date",
        "Compliance Officer Date", "Branch Manager Date", "Cash Office Date"
    ]
    for col in date_columns:
        df[col] = df[col].apply(lambda x: format_date(x) if pd.notnull(x) else "")

    st.dataframe(df)
