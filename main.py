import streamlit as st 
import os
from git import Repo

# --- GitHub Configuration ---
GIT_REPO = "https://github.com/mysteriousbug/dlp-audit.git"
GIT_LOCAL_PATH = "dlp-audit"
GIT_BRANCH = "main"
GITHUB_TOKEN = st.secrets["token"]

def clone_or_pull_repo():
    if not os.path.exists(GIT_LOCAL_PATH):
        Repo.clone_from(
            GIT_REPO.replace("https://", f"https://{GITHUB_TOKEN}@"),
            GIT_LOCAL_PATH,
            branch=GIT_BRANCH
        )
    else:
        repo = Repo(GIT_LOCAL_PATH)
        repo.remotes.origin.pull()

def commit_and_push_file(local_file_path, commit_msg="Upload via Streamlit"):
    repo = Repo(GIT_LOCAL_PATH)
    repo.git.add(local_file_path)
    repo.index.commit(commit_msg)
    origin = repo.remote(name="origin")
    origin.push()

# --- Streamlit UI ---
st.title("📤 Upload and Save File to GitHub Repo")

uploaded_file = st.file_uploader("Choose a file")

if uploaded_file:
    clone_or_pull_repo()

    save_path = os.path.join(uploads_folder, uploaded_file.name)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(save_path, "wb") as f:
        f.write(uploaded_file.read())

    commit_and_push_file(save_path)
    st.success(f"✅ Uploaded and pushed `{uploaded_file.name}` to GitHub!")
