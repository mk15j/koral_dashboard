
import streamlit as st

from utils.db import listeria_collection

# 🔐 Check if user is logged in
if "user" not in st.session_state:
    st.warning("Please log in to access this page.")
    st.stop()

# 🛡️ Optional: Restrict to admins only
if st.session_state.get("user", {}).get("role") != "admin":
    st.error("You do not have permission to access this page.")
    st.stop()

if "user" in st.session_state:
    st.sidebar.markdown(f"👤 Logged in as: `{st.session_state.user['username']}`")
    if st.sidebar.button("Logout"):
        del st.session_state["user"]
        st.success("Logged out successfully")
        st.experimental_rerun()
        
import pandas as pd
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
