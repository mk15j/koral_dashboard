
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import listeria_collection

st.title("🧪 Test Summary")

@st.cache_data
def load_data():
    df = pd.DataFrame(listeria_collection.find({}, {"_id": 0}))
    return df

df = load_data()

summary = df.groupby("test")["value"].apply(lambda x: (x != "Not Detected").sum()).reset_index(name="Detections")
fig = px.bar(summary, x="test", y="Detections", color="Detections",
             title="Detection Count by Test Type",
             template="plotly_dark", color_continuous_scale="reds")

st.plotly_chart(fig, use_container_width=True)
