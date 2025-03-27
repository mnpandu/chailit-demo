from langchain_core.documents import Document

def load_documents_from_txt(file_path: str) -> list[Document]:
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [Document(page_content=line.strip()) for line in lines if line.strip()]
