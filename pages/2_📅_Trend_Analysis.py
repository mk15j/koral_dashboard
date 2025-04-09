import streamlit as st
st.set_page_config(page_title="Trend Analysis", layout="wide")  # MUST be first Streamlit command

import pandas as pd
import plotly.express as px
from utils.db import listeria_collection

# 🔐 Authentication check
if "user" not in st.session_state:
    st.warning("Please log in to access this page.")
    st.stop()

# 👤 Show user info and logout button
st.sidebar.markdown(f"👤 Logged in as: `{st.session_state.user['username']}`")
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.success("🔓 Logged out successfully.")
    st.stop()

# 📅 Page content
st.title("📅 Trend Analysis")

@st.cache_data
def load_data():
    df = pd.DataFrame(listeria_collection.find({}, {"_id": 0}))
    df["sample_date"] = pd.to_datetime(df["sample_date"], errors="coerce")
    return df

df = load_data()

trend = df.groupby(["test", "sample_date"])["value"].apply(lambda x: (x != "Not Detected").sum()).reset_index()

fig = px.line(trend, x="sample_date", y="value", color="test",
              title="Detection Trends by Test",
              template="plotly_dark", color_discrete_sequence=px.colors.qualitative.T10)

st.plotly_chart(fig, use_container_width=True)
