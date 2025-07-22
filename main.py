import streamlit as st 
import os

st.title("📁 Upload Files and Save to Disk")

# Create 'uploads' folder if it doesn't exist
upload_dir = "uploads"
os.makedirs(upload_dir, exist_ok=True)

# File uploader (multiple)
uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)

if uploaded_files:
    st.success(f"{len(uploaded_files)} file(s) uploaded.")

    for file in uploaded_files:
        st.write(f"📄 **{file.name}**")
        
        # Save to uploads/ directory
        save_path = os.path.join(upload_dir, file.name)
        with open(save_path, "wb") as f:
            f.write(file.read())
        
        st.success(f"Saved to 📂 `{save_path}`")

        # Download button
        with open(save_path, "rb") as f:
            st.download_button(
                label=f"⬇️ Download {file.name}",
                data=f,
                file_name=file.name,
                mime="application/octet-stream"
            )

        st.markdown("---")
else:
    st.info("Upload some files to save and download.")
