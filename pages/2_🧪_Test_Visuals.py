import streamlit as st
st.set_page_config(page_title="Test Visuals", layout="wide")  # 🔧 Must be the very first Streamlit call

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

# 🧪 Main content
st.title("🧪 Test Summary Visuals")

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

# 🔢 Test Frequency by Code
st.subheader("🔢 Test Frequency by Code")
code_count = df_filtered["code"].value_counts().reset_index()
code_count.columns = ["Code", "Test Count"]
fig_code = px.bar(code_count, x="Code", y="Test Count", color="Test Count", title="Number of Tests by Code", color_continuous_scale="Sunsetdark")
st.plotly_chart(fig_code, use_container_width=True)

# 🏭 Test Frequency by Description
st.subheader("🏭 Test Frequency by Description")
desc_count = df_filtered["eng_description"].value_counts().reset_index()
desc_count.columns = ["Description", "Test Count"]
fig_desc = px.bar(desc_count, x="Test Count", y="Description", orientation="h", title="Test Frequency by Sample Description", color="Test Count", color_continuous_scale="Agsunset")
st.plotly_chart(fig_desc, use_container_width=True)

# 🧬 Detection Outcome by Code
st.subheader("🧬 Detection Outcome by Code")
if "value" in df_filtered.columns:
    heat_df = df_filtered.groupby(["code", "value"]).size().reset_index(name="count")
    fig_heat = px.bar(heat_df, x="code", y="count", color="value", barmode="group", title="Detection Outcome by Test Code")
    st.plotly_chart(fig_heat, use_container_width=True)

# 🧬 Detection ratio for Samples
st.subheader("🧬 Detection ratio for Samples")
if 'value' in df_filtered.columns:
    value_counts = df_filtered['value'].value_counts().reset_index()
    value_counts.columns = ['value', 'count']
    fig_value_donut = px.pie(value_counts, names='value', values='count',
                             hole=0.4, title="Listeria Test Result Breakdown",
                             color_discrete_sequence=px.colors.sequential.Tealgrn)
    st.plotly_chart(fig_value_donut, use_container_width=True)

# 🧬 Detection ratio by Description
st.subheader("🧬 Detection ratio by Description")
desc_counts = df_filtered['eng_description'].value_counts().reset_index()
desc_counts.columns = ['eng_description', 'count']
fig_desc_donut = px.pie(desc_counts, names='eng_description', values='count',
                        hole=0.4, title="Sample Distribution by Description",
                        color_discrete_sequence=px.colors.sequential.Magma)
st.plotly_chart(fig_desc_donut, use_container_width=True)
