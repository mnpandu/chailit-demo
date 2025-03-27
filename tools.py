from langchain_core.tools import tool
from oracle_client import fetch_case_data
from chat_data_vector_store import build_vectorstore

vectorstore = build_vectorstore("data.txt")

@tool
def fetch_case_info(case_number: str) -> str:
    """Fetch description and comments for a given case number."""
    return fetch_case_data(case_number)

@tool
def find_similar_cases(text: str) -> str:
    """Find top 5 similar cases based on input text."""
    docs_and_scores = vectorstore.similarity_search_with_score(text, k=5)
    formatted_table = "| Rank | Similar Case | Score |\n|------|----------------|-------|\n"
    for i, (doc, score) in enumerate(docs_and_scores):
        snippet = doc.page_content[:80].replace("\n", " ")
        formatted_table += f"| {i+1} | {snippet} | {score:.4f} |\n"
    return formatted_table

@tool
def retrieve_related_info(query: str) -> str:
    """Retrieve relevant info for a business question."""
    docs = vectorstore.similarity_search(query)
    return docs[0].page_content if docs else "No relevant information found."
