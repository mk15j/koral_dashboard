
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import listeria_collection

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

st.subheader("🔢 Test Frequency by Code")
code_count = df_filtered["code"].value_counts().reset_index()
code_count.columns = ["Code", "Test Count"]
fig_code = px.bar(code_count, x="Code", y="Test Count", color="Test Count", title="Number of Tests by Code", color_continuous_scale="Sunsetdark")
st.plotly_chart(fig_code, use_container_width=True)

st.subheader("🏭 Test Frequency by Description")
desc_count = df_filtered["eng_description"].value_counts().reset_index()
desc_count.columns = ["Description", "Test Count"]
fig_desc = px.bar(desc_count, x="Test Count", y="Description", orientation="h", title="Test Frequency by Sample Description", color="Test Count", color_continuous_scale="Agsunset")
st.plotly_chart(fig_desc, use_container_width=True)

st.subheader("🧬 Detection Outcome by Code")
if "value" in df_filtered.columns:
    heat_df = df_filtered.groupby(["code", "value"]).size().reset_index(name="count")
    fig_heat = px.bar(heat_df, x="code", y="count", color="value", barmode="group", title="Detection Outcome by Test Code")
    st.plotly_chart(fig_heat, use_container_width=True)

st.subheader("🧬 Detection ratio for Samples")
if 'value' in df_filtered.columns:
    value_counts = df_filtered['value'].value_counts().reset_index()
    value_counts.columns = ['value', 'count']

    fig_value_donut = px.pie(value_counts, names='value', values='count',
                             hole=0.4, title="Listeria Test Result Breakdown",
                             color_discrete_sequence=px.colors.sequential.Tealgrn)
    st.plotly_chart(fig_value_donut, use_container_width=True)

st.subheader("🧬 Detection ratio for Samples")
code_counts = df_filtered['code'].value_counts().reset_index()
code_counts.columns = ['code', 'count']

fig_code_donut = px.pie(code_counts, names='code', values='count',
                        hole=0.4, title="Samples by Machine Code",
                        color_discrete_sequence=px.colors.sequential.RdBu)
st.plotly_chart(fig_code_donut, use_container_width=True)
