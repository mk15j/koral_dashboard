import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import cv2
import numpy as np
import os
from pymongo import MongoClient
from datetime import datetime

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

def plot_markers(image, data):
    if image is None or data.empty:
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(image)

    required_columns = {'x', 'y', 'values', 'points'}
    if not required_columns.issubset(data.columns):
        st.error(f"Missing required columns: {required_columns - set(data.columns)}")
        return

    unique_positions = data.groupby(['x', 'y'])['values'].max().reset_index()

    for _, row in unique_positions.iterrows():
        x, y, value = row['x'], row['y'], row['values']
        color = '#FFBF00' if pd.isna(value) else '#FF0000' if value == 1 else '#008000'
        ax.add_patch(plt.Circle((x, y), 9, color=color, fill=True))
        points_at_location = data[(data['x'] == x) & (data['y'] == y)]
        point_numbers = ', '.join(map(str, points_at_location['points']))
        ax.text(x, y - 15, point_numbers, color=color, fontsize=12, ha='center')

    ax.axis('off')
    st.pyplot(fig)

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
        filtered = df[df['sample_date'] == selected_date]
        filtered = filtered.rename(columns={"point": "points"})  # adapt if your column is named 'point'

        if not filtered.empty:
            plot_markers(image, filtered)
        else:
            st.warning("No data found for the selected date.")
