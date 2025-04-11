import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import cv2
import numpy as np
import os
from pymongo import MongoClient
from datetime import datetime
import plotly.express as px

# MongoDB connection
client = MongoClient(st.secrets["MONGO_URI"])
db = client["koral"]
listeria_collection = db["listeria"]

def load_image(image_path="koral6.png"):
    if not os.path.exists(image_path):
        st.error(f"Image not found at {image_path}")
        return None
    image = cv2.imread(image_path)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# ---- Streamlit App ----
st.title("Listeria Sample Map Visualization")

# Load image for background
image = load_image()

# Get unique dates from database
all_data = list(listeria_collection.find({"x": {"$exists": True}, "y": {"$exists": True}}))
if not all_data:
    st.warning("No data found with X and Y coordinates in MongoDB.")
else:
    df = pd.DataFrame(all_data)
    df['sample_date'] = pd.to_datetime(df['sample_date']).dt.date

    available_dates = df['sample_date'].dropna().unique()
    selected_date = st.selectbox("Select a Date", sorted(available_dates, reverse=True))

    if selected_date:
        filtered = df[df['sample_date'] == selected_date].copy()
        filtered = filtered.rename(columns={"point": "points"})

        if not filtered.empty:
            # Normalize columns
            filtered['points'] = filtered['points'].astype(str)
            filtered['x'] = pd.to_numeric(filtered['x'], errors='coerce')
            filtered['y'] = pd.to_numeric(filtered['y'], errors='coerce')
            filtered['values'] = pd.to_numeric(filtered['values'], errors='coerce')

            # Ensure description column exists
            if 'description' not in filtered.columns:
                filtered['description'] = ""

            # Construct detailed hover text
            filtered['hover_text'] = (
                "<b>Point:</b> " + filtered['points'] + "<br>"
                + "<b>Description:</b> " + filtered['description'].astype(str) + "<br>"
                + "<b>Status:</b> " + filtered['values'].map({1: "Positive", 0: "Negative"}).fillna("Unknown") + "<br>"
                + "<b>X:</b> " + filtered['x'].astype(str) + "<br>"
                + "<b>Y:</b> " + filtered['y'].astype(str)
            )

            # Create a Plotly scatter plot
            fig = px.scatter(
                filtered,
                x='x',
                y='y',
                color=filtered['values'].map({1: "Positive", 0: "Negative", np.nan: "Unknown"}),
                color_discrete_map={"Positive": "#FF0000", "Negative": "#008000", "Unknown": "#FFBF00"},
                hover_name='points',
                hover_data={"x": False, "y": False, "values": False, "description": False, 'hover_text': True},
                custom_data=['hover_text'],
                title=f"Listeria Points on {selected_date}"
            )
            fig.update_traces(
                marker=dict(size=12, line=dict(width=1, color='DarkSlateGrey')),
                hovertemplate="%{customdata[0]}<extra></extra>"
            )
            fig.update_layout(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                margin=dict(l=0, r=0, t=40, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data found for the selected date.")
