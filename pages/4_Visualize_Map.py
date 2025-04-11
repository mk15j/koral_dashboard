import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import cv2
import numpy as np
import os
from pymongo import MongoClient
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go #0
from PIL import Image
import io
import base64

# MongoDB connection
client = MongoClient(st.secrets["MONGO_URI"])
db = client["koral"]
listeria_collection = db["listeria"]
#1
def load_image_base64(image_path="koral6.png"):
    if not os.path.exists(image_path):
        st.error(f"Image not found at {image_path}")
        return None, None, None
    image = Image.open(image_path)
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    encoded = base64.b64encode(buffered.getvalue()).decode()
    return image, f"data:image/png;base64,{encoded}", image.size  # PIL Image, base64, (width, height)

# ---- Streamlit App ----
st.title("Listeria Sample Map Visualization")

# Load image for background
#image = load_image()

# Load image for background
image_pil, image_base64, (width, height) = load_image_base64()
if image_pil is None:
    st.stop()

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

            # Get image dimensions for scaling
            height, width, _ = image.shape

            # Create figure with background image
            fig = go.Figure()
            #3
            fig.add_layout_image(
                dict(
                    source=image_base64,
                    xref="x",
                    yref="y",
                    x=0,
                    y=height,
                    sizex=width,
                    sizey=height,
                    sizing="stretch",
                    layer="below"
                )
            )

            # Add scatter plot of points
            fig.add_trace(go.Scatter(
                x=filtered['x'],
                y=height - filtered['y'],  # invert y to match image coordinates
                mode='markers',
                marker=dict(
                    size=12,
                    color=filtered['values'].map({1: "#FF0000", 0: "#008000"}).fillna("#FFBF00"),
                    line=dict(width=1, color='DarkSlateGrey')
                ),
                customdata=filtered[['hover_text']],
                hovertemplate="%{customdata[0]}<extra></extra>"
            ))

            fig.update_layout(
                xaxis=dict(visible=False, range=[0, width]),
                yaxis=dict(visible=False, range=[0, height]),
                showlegend=False,
                margin=dict(l=0, r=0, t=40, b=0),
                title=f"Listeria Points on {selected_date}"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data found for the selected date.")
