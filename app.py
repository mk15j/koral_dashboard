
import streamlit as st

if "user" not in st.session_state:
    st.warning("Please login first.")
    st.stop()
    
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.experimental_rerun()
    
st.set_page_config(
    page_title="Koral Listeria Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Welcome to Koral Seafood Listeria Dashboard")
st.markdown("Use the sidebar to navigate between different dashboard sections.")
