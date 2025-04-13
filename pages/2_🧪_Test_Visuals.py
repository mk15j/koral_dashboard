import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import listeria_collection

# 🔐 Authentication check
if "user" not in st.session_state:
    st.warning("Please log in to access this page.")
    st.stop()

# 👤 Show user info and logout
st.sidebar.markdown(f"👤 Logged in as: `{st.session_state.user['username']}`")
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.success("🔓 Logged out successfully.")
    st.stop()

# 🥚 Main content
st.title("🥚 Test Summary Visuals")

@st.cache_data
def load_data():
    data = list(listeria_collection.find({}, {"_id": 0}))
    df = pd.DataFrame(data)
    if "sample_date" in df.columns:
        df["sample_date"] = pd.to_datetime(df["sample_date"], errors="coerce")
    return df

df = load_data()
if df.empty:
    st.warning("No data available.")
    st.stop()

st.sidebar.header("Filters")
date_range = st.sidebar.date_input("Date Range", [df["sample_date"].min(), df["sample_date"].max()])
df_filtered = df[(df["sample_date"] >= pd.to_datetime(date_range[0])) & (df["sample_date"] <= pd.to_datetime(date_range[1]))]

# 🔢 Test Frequency by Code (Stacked)
st.subheader("🔢 Test Frequency by Code")
if "value" in df_filtered.columns and "code" in df_filtered.columns:
    df_code = df_filtered.copy()
    df_code['Detection'] = df_code['value'].apply(lambda x: "Detected" if x == 1 else ("Not Detected" if x == 0 else "Unknown"))
    code_detection_counts = df_code.groupby(['code', 'Detection']).size().reset_index(name='count')

    if not code_detection_counts.empty:
        fig_code = px.bar(
            code_detection_counts,
            x="code",
            y="count",
            color="Detection",
            barmode="stack",
            title="Number of Tests by Code (Detected vs Not Detected)",
            color_discrete_map={"Detected": "#D62728", "Not Detected": "#2CA02C", "Unknown": "#FF7F0E"}
        )
        fig_code.update_layout(legend_title_text="Detection Outcome")
        st.plotly_chart(fig_code, use_container_width=True)
    else:
        st.info("No data available to display the Test Frequency by Code chart.")
