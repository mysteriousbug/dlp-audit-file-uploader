import streamlit as st

st.title("File Uploader")

uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)

if uploaded_files:
    st.success(f"{len(uploaded_files)} file(s) uploaded")

    for file in uploaded_files:
        st.write(f" 🗎 {file.name}")

    try:
        content = file.read().decode("utf-8")
        st.text_area(f"Content of {file.name}:", content, height = 150)

    except Exception:
            st.warning(f"Cannot display contents of {file.name} ")

else:
     st.info("No files uploaded yet.")
