import streamlit as st 
from pymongo import MongoClient
import gridfs
import io

# Load MongoDB secrets
uri = st.secrets["mongodb"]["uri"]
db_name = st.secrets["mongodb"]["db"]
collection_name = st.secrets["mongodb"]["collection"]

# Connect to MongoDB and GridFS
client = MongoClient(uri)
db = client[db_name]
fs = gridfs.GridFS(db)

st.title("📤 Upload Files to MongoDB")

uploaded_file = st.file_uploader("Choose a file")

if uploaded_file:
    # Save to MongoDB GridFS
    file_data = uploaded_file.read()
    filename = uploaded_file.name

    # Check if file with same name already exists
    existing = db.fs.files.find_one({"filename": filename})
    if existing:
        st.warning("File already exists. Overwriting.")
        db.fs.files.delete_one({"_id": existing["_id"]})

    fs.put(file_data, filename=filename)
    st.success(f"✅ File `{filename}` uploaded to MongoDB!")

# Retrieve and list files
st.subheader("📂 Files in MongoDB")
files = db.fs.files.find().sort("uploadDate", -1)

for f in files:
    st.markdown(f"📄 **{f['filename']}** — {f['length']} bytes")
    file_id = f["_id"]

    if st.button(f"Download {f['filename']}", key=str(file_id)):
        file_data = fs.get(file_id).read()
        st.download_button(
            label=f"⬇️ Save {f['filename']}",
            data=file_data,
            file_name=f['filename'],
            mime="application/octet-stream"
        )
