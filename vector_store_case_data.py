# oracle_vector_store.py
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from sentencetransformer import getSentenceModel
from oracle_client import DB_CONN

embedding_model = HuggingFaceEmbeddings(model_name=getSentenceModel())

# Global vectorstore instance (already built during app startup)
case_vectorstore = None

def build_oracle_vectorstore() -> FAISS:
    global case_vectorstore

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
    case_vectorstore = FAISS.from_documents(documents, embeddings)
    return case_vectorstore

def find_similar_cases(query_text: str, top_n: int = 5) -> list[tuple[str, float]]:
    """
    Perform similarity search using free-text input and return top N case summaries with scores.
    Returns a list of tuples: (case_text, score)
    """
    if case_vectorstore is None:
        raise ValueError("Vectorstore not initialized. Call build_oracle_vectorstore() first.")

    # Perform semantic similarity search
    results = case_vectorstore.similarity_search_with_score(query_text, k=top_n)

    # Format the output as tuples: (text, score)
    return [(doc.page_content, score) for doc, score in results]
