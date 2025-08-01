import streamlit as st
import pandas as pd
from db import get_connection

def all_policies():
    st.subheader("📋 All Policies Table")
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM policies", conn)
    st.dataframe(df)
    conn.close()
