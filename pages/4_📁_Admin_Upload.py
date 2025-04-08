
import streamlit as st
import pandas as pd
from utils.db import listeria_collection

st.title("📁 Admin: Upload Listeria Data")

uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df["sample_date"] = pd.to_datetime(df["sample_date"], errors="coerce")
    st.write(df.head())
    
    if st.button("Upload to MongoDB"):
        data = df.to_dict(orient="records")
        listeria_collection.insert_many(data)
        st.success(f"{len(data)} records uploaded successfully.")
