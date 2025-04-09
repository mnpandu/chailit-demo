import streamlit as st
import os

# Folder containing your readmd.md blog files
BASE_DIR = "custom_blogs"
FILE_SUFFIX = "readme.md"

st.set_page_config(page_title="📘 AI Blog Viewer", layout="wide")
st.title("📘 AI Blog Viewer")

# Step 1: Find all *readmd.md files in the folder
def get_readmd_files(folder, suffix):
    return sorted([
        f for f in os.listdir(folder)
        if f.lower().endswith(suffix.lower()) and os.path.isfile(os.path.join(folder, f))
    ])

blog_files = get_readmd_files(BASE_DIR, FILE_SUFFIX)

# Step 2: Search box
search_query = st.sidebar.text_input("🔍 Search blog files")

# Step 3: Filter matching files
filtered_files = [f for f in blog_files if search_query.lower() in f.lower()]

st.sidebar.subheader("📂 Available Blogs")

if not filtered_files:
    st.sidebar.warning("No matching blog files found.")
else:
    selected_file = st.sidebar.radio("Select a blog to view:", filtered_files)

    # Step 4: Show Markdown content
    if selected_file:
        with open(os.path.join(BASE_DIR, selected_file), "r", encoding="utf-8") as f:
            content = f.read()

        st.subheader(f"📝 {selected_file}")
        st.markdown(content, unsafe_allow_html=True)
