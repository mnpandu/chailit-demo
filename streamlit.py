import streamlit as st
import os
import base64

BASE_DIR = "custom_blogs"

st.set_page_config(page_title="📘 AI Blog Viewer", layout="wide")
st.title("📘 AI Blog Viewer with Markdown + PDF Support")

# ✅ Updated pattern: match *readme.md (case-insensitive) or *.pdf
def list_blog_files(folder):
    return sorted([
        f for f in os.listdir(folder)
        if (
            f.lower().endswith("readme.md") or
            f.lower().endswith(".pdf")
        ) and os.path.isfile(os.path.join(folder, f))
    ])

blog_files = list_blog_files(BASE_DIR)

# Search box
search_query = st.sidebar.text_input("🔍 Search blogs")
filtered_files = [f for f in blog_files if search_query.lower() in f.lower()]

st.sidebar.subheader("📂 Available Blog Files")

if not filtered_files:
    st.sidebar.warning("No matching files found.")
else:
    selected_file = st.sidebar.radio("Select a file to view:", filtered_files)
    file_path = os.path.join(BASE_DIR, selected_file)

    if selected_file.lower().endswith(".md"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        st.subheader(f"📝 {selected_file}")
        st.markdown(content, unsafe_allow_html=True)

    elif selected_file.lower().endswith(".pdf"):
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")
        pdf_viewer = f"""
            <iframe src="data:application/pdf;base64,{base64_pdf}" 
                    width="100%" height="800px" style="border: none;">
            </iframe>
        """
        st.subheader(f"📄 {selected_file}")
        st.markdown(pdf_viewer, unsafe_allow_html=True)
