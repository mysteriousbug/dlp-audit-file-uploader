import streamlit as st
import pymongo
from pymongo import MongoClient
import gridfs
from gridfs import GridFS
import io
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# MongoDB Configuration
# Option 1: Local MongoDB
MONGO_URI = st.secrets["MONGO_URI"]

# Option 2: MongoDB Atlas (replace with your connection string)
#MONGO_URI = "mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"

# Option 3: If you have SSL issues, try this format:
# MONGO_URI = "mongodb+srv://username:password@cluster.mongodb.net/?ssl=true&ssl_cert_reqs=CERT_NONE"

DATABASE_NAME = "file_storage_poc"
COLLECTION_NAME = "uploaded_files"

#@streamlit.cache_resource
def init_mongodb():
    """Initialize MongoDB connection and GridFS"""
    try:
        client = MongoClient(MONGO_URI)
        # Test the connection
        client.admin.command('ping')
        db = client[DATABASE_NAME]
        fs = GridFS(db)
        return client, db, fs
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {str(e)}")
        return None, None, None

def upload_file_to_gridfs(fs, file, filename, metadata=None):
    """Upload file to GridFS"""
    try:
        file_id = fs.put(
            file.getvalue(),
            filename=filename,
            content_type=file.type,
            upload_date=datetime.now(),
            metadata=metadata or {}
        )
        return file_id
    except Exception as e:
        st.error(f"Error uploading file: {str(e)}")
        return None

def get_files_from_gridfs(fs):
    """Get list of files from GridFS"""
    try:
        files = []
        for file in fs.find():
            files.append({
                'id': str(file._id),
                'filename': file.filename,
                'length': file.length,
                'upload_date': file.upload_date,
                'content_type': file.content_type,
                'metadata': file.metadata
            })
        return files
    except Exception as e:
        st.error(f"Error retrieving files: {str(e)}")
        return []

def download_file_from_gridfs(fs, file_id):
    """Download file from GridFS"""
    try:
        from bson import ObjectId
        file = fs.get(ObjectId(file_id))
        return file
    except Exception as e:
        st.error(f"Error downloading file: {str(e)}")
        return None

def delete_file_from_gridfs(fs, file_id):
    """Delete file from GridFS"""
    try:
        from bson import ObjectId
        fs.delete(ObjectId(file_id))
        return True
    except Exception as e:
        st.error(f"Error deleting file: {str(e)}")
        return False

def main():
    st.set_page_config(
        page_title="File Storage POC",
        page_icon="📁",
        layout="wide"
    )
    
    st.title("📁 File Upload/Download POC")
    st.markdown("### Data Leakage Protection Audit - File Storage System")
    
    # Initialize MongoDB connection
    client, db, fs = init_mongodb()
    
    if client is None or db is None or fs is None:
        st.error("❌ Cannot connect to MongoDB. Please check your connection.")
        st.info("Make sure MongoDB is running and the connection URI is correct.")
        return
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select Page", ["Upload Files", "View & Download Files", "Analytics"])
    
    if page == "Upload Files":
        upload_page(fs)
    elif page == "View & Download Files":
        download_page(fs)
    elif page == "Analytics":
        analytics_page(fs)

def upload_page(fs):
    """File upload page"""
    st.header("📤 Upload Files")
    
    # File uploader (supports multiple files)
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        accept_multiple_files=True,
        type=None,  # Accept all file types
        help="Select one or more files to upload to the cloud database"
    )
    
    # Additional metadata input
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Category", ["General", "Documents", "Images", "Data", "Other"])
        source = st.text_input("Source/Department", placeholder="e.g., HR, Finance, IT")
    
    with col2:
        classification = st.selectbox("Classification", ["Public", "Internal", "Confidential", "Restricted"])
        description = st.text_area("Description", placeholder="Brief description of the files")
    
    if uploaded_files:
        st.subheader("Files Ready for Upload:")
        
        # Display file information
        for i, file in enumerate(uploaded_files):
            with st.expander(f"📄 {file.name} ({file.size:,} bytes)"):
                st.write(f"**Type:** {file.type}")
                st.write(f"**Size:** {file.size:,} bytes")
        
        # Upload button
        if st.button("🚀 Upload All Files", type="primary"):
            progress_bar = st.progress(0)
            status_container = st.container()
            
            successful_uploads = 0
            failed_uploads = 0
            
            for i, file in enumerate(uploaded_files):
                progress_bar.progress((i + 1) / len(uploaded_files))
                
                metadata = {
                    "category": category,
                    "source": source,
                    "classification": classification,
                    "description": description,
                    "original_size": file.size,
                    "uploader": "POC_User"  # In a real app, this would be the logged-in user
                }
                
                file_id = upload_file_to_gridfs(fs, file, file.name, metadata)
                
                if file_id:
                    successful_uploads += 1
                    status_container.success(f"✅ Uploaded: {file.name}")
                else:
                    failed_uploads += 1
                    status_container.error(f"❌ Failed: {file.name}")
            
            st.success(f"Upload complete! ✅ {successful_uploads} successful, ❌ {failed_uploads} failed")
            
            if successful_uploads > 0:
                st.balloons()

def download_page(fs):
    """File download and management page"""
    st.header("📥 View & Download Files")
    
    # Get all files
    files = get_files_from_gridfs(fs)
    
    if not files:
        st.info("No files found in the database.")
        return
    
    # Search and filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🔍 Search files", placeholder="Enter filename...")
    
    with col2:
        category_filter = st.selectbox("Filter by Category", ["All"] + ["General", "Documents", "Images", "Data", "Other"])
    
    with col3:
        classification_filter = st.selectbox("Filter by Classification", ["All"] + ["Public", "Internal", "Confidential", "Restricted"])
    
    # Apply filters
    filtered_files = files.copy()
    
    if search_term:
        filtered_files = [f for f in filtered_files if search_term.lower() in f['filename'].lower()]
    
    if category_filter != "All":
        filtered_files = [f for f in filtered_files if f.get('metadata', {}).get('category') == category_filter]
    
    if classification_filter != "All":
        filtered_files = [f for f in filtered_files if f.get('metadata', {}).get('classification') == classification_filter]
    
    st.write(f"**Found {len(filtered_files)} files**")
    
    # Display files in a table-like format
    for file in filtered_files:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.write(f"**📄 {file['filename']}**")
                metadata = file.get('metadata', {})
                st.write(f"Size: {file['length']:,} bytes | Uploaded: {file['upload_date'].strftime('%Y-%m-%d %H:%M')}")
                if metadata.get('classification'):
                    classification_color = {
                        'Public': 'green',
                        'Internal': 'blue',
                        'Confidential': 'orange',
                        'Restricted': 'red'
                    }.get(metadata['classification'], 'gray')
                    st.markdown(f"<span style='color: {classification_color}'>🔒 {metadata['classification']}</span>", unsafe_allow_html=True)
            
            with col2:
                category = file.get('metadata', {}).get('category', 'N/A')
                st.write(f"**Category:** {category}")
            
            with col3:
                # Download button
                if st.button(f"⬇️ Download", key=f"download_{file['id']}"):
                    downloaded_file = download_file_from_gridfs(fs, file['id'])
                    if downloaded_file:
                        st.download_button(
                            label="💾 Save File",
                            data=downloaded_file.read(),
                            file_name=file['filename'],
                            mime=file.get('content_type', 'application/octet-stream'),
                            key=f"save_{file['id']}"
                        )
            
            with col4:
                # Delete button
                if st.button(f"🗑️ Delete", key=f"delete_{file['id']}", type="secondary"):
                    if delete_file_from_gridfs(fs, file['id']):
                        st.success(f"Deleted {file['filename']}")
                        st.rerun()
            
            st.divider()

if __name__ == "__main__":
    main()
