# oracle_vector_store.py
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from sentencetransformer import getSentenceModel
from oracle_client import DB_CONN

def build_oracle_vectorstore() -> FAISS:
    cursor = DB_CONN.cursor()
    cursor.execute("SELECT case_number, case_description, case_comments FROM cases_table")
    rows = cursor.fetchall()

    documents = [
        Document(
            page_content=f"{desc} {comments}",
            metadata={"case_number": num}
        )
        for num, desc, comments in rows
    ]

    embeddings = HuggingFaceEmbeddings(model_name=getSentenceModel())
    return FAISS.from_documents(documents, embeddings)