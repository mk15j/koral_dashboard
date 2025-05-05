
import streamlit as st
import pandas as pd
from utils.db import listeria_collection

# 🔐 Check if user is logged in
# if "user" not in st.session_state:
#     st.warning("Please log in to access this page.")
#     st.stop()

# # 🛡️ Optional: Restrict to admins only
# if st.session_state.get("user", {}).get("role") != "admin":
#     st.error("You do not have permission to access this page.")
#     st.stop()

# if "user" in st.session_state:
#     st.sidebar.markdown(f"👤 Logged in as: `{st.session_state.user['username']}`")
#     logout = st.sidebar.button("Logout")
#     if logout:
#         st.session_state.clear()  # safer: clears all session data
#         st.success("🔓 Logged out successfully.")
#         st.stop()  # halts execution and prevents rerun issues
        
# import pandas as pd
# st.title("📁 Admin: Upload Listeria Data")

# uploaded_file = st.file_uploader("Upload CSV", type="csv")
# if uploaded_file:
#     df = pd.read_csv(uploaded_file)
#     df["sample_date"] = pd.to_datetime(df["sample_date"], errors="coerce")
#     st.write(df.head())
    
#     if st.button("Upload to MongoDB"):
#         data = df.to_dict(orient="records")
#         listeria_collection.insert_many(data)
#         st.success(f"{len(data)} records uploaded successfully.")

# 🔐 Check if user is logged in
if "user" not in st.session_state:
    st.warning("Please log in to access this page.")
    st.stop()

# 🛡️ Restrict to admins only
if st.session_state.get("user", {}).get("role") != "admin":
    st.error("You do not have permission to access this page.")
    st.stop()

# 👤 Display user info and logout option
st.sidebar.markdown(f"👤 Logged in as: `{st.session_state.user['username']}`")
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.success("🔓 Logged out successfully.")
    st.stop()

# 📁 Upload section
st.title("📁 Admin: Upload Listeria Results Data")

uploaded_file = st.file_uploader("Upload Results File", type=["csv"])
if uploaded_file is None:
    st.warning("Please upload a CSV file.")
    st.stop()

try:
    df = pd.read_csv(uploaded_file, encoding="utf-8", encoding_errors="replace")
except Exception as e:
    st.error(f"Error reading CSV file: {e}")
    st.stop()

st.write(df.head())  # Preview data

# ✅ Required columns
required_columns = {
    "eurofins_order", "sample_code", "order_ref", "sample_description", 
    "sample_date", "test_code", "test", "parameter", "value", "unit", 
    "receiving_lab", "eng_description", "code", "x", "y", "values", "points"
}
if not required_columns.issubset(df.columns):
    st.error(f"Missing required columns: {', '.join(required_columns - set(df.columns))}")
    st.stop()

# 🕓 Date parsing
df["sample_date"] = pd.to_datetime(df["sample_date"], format="%d-%m-%Y", errors="coerce")
df["sample_date"] = df["sample_date"].where(df["sample_date"].notna(), None)

# 🧑 Add uploader info
username = st.session_state.user.get("username", "admin")
df["uploaded_by"] = username

# 📤 Upload to MongoDB
if st.button("Upload to MongoDB"):
    try:
        data_list = df.to_dict(orient="records")
        result = listeria_collection.insert_many(data_list)
        st.success(f"✅ Inserted {len(result.inserted_ids)} records into the database!")
    except Exception as e:
        st.error(f"❌ Database Error: {e}")
