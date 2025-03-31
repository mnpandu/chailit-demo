# vector_store_claims_data.py
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from sentencetransformer import getSentenceModel
from oracle_client import get_claims_data

# Global vectorstore instance (already built during app startup)
claim_vectorstore = None

def build_claims_vectorstore() -> FAISS:
    global claim_vectorstore
    
    claims_df = get_claims_data()

    documents = []
    for _, row in claims_df.iterrows():
        content = (
            f"{row['base_rate']} {row['units']} {row['discount']} {row['calculated_amount']} {row['expected_amount']}"
        )
        documents.append(Document(
            page_content=content,
            metadata={"case_number": row['case_number'], "claim_number": row['claim_number']}
        ))

    embeddings = HuggingFaceEmbeddings(model_name=getSentenceModel())
    claim_vectorstore = FAISS.from_documents(documents, embeddings)
    return claim_vectorstore

def find_similar_claims(query_text: str, top_n: int = 5) -> list[tuple[str, float]]:
    """
    Perform similarity search using free-text input and return top N case summaries with scores.
    Returns a list of tuples: (case_text, score)
    """
    if claim_vectorstore is None:
        raise ValueError("Vectorstore not initialized. Call build_oracle_vectorstore() first.")

    # Perform semantic similarity search
    results = claim_vectorstore.similarity_search_with_score(query_text, k=top_n)

    # Format the output as tuples: (text, score)
    return [(doc.page_content, score) for doc, score in results]