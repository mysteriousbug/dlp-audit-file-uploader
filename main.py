import streamlit as st

st.title("File Uploader")

uploaded_file = st.file_uploader("Choose a file", type = None)

if uploaded_file is not None:
    st.success(f"File Uploaded Successfully: {uploaded_file.name}")
