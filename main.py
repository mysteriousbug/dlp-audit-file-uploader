import streamlit as st 
from pymongo import MongoClient
import gridfs
import io
from urllib.parse import quote_plus

# Load MongoDB secrets
us = st.secrets["mongodb"]["us"]
pwd = st.secrets["mongodb"]["pwd"]
username = quote_plus(us)
password = quote_plus(pwd)
db_name = 'mydb'

cluster = 'cluster0.pfago9a.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
authSource = '<authSource>'
authMechanism = '<authMechanism>'
uri = 'mongodb+srv://' + username + ':' + password + '@' + cluster


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
