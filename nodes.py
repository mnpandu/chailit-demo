# nodes.py (modularized version)
import re
from transformers import pipeline
from langchain_community.vectorstores import FAISS
from oracle_client import fetch_case_data
from oracle_data_vector_store import build_oracle_vectorstore

model_path = "C:/Users/mnpan/.cache/huggingface/hub/models--distilbert-base-cased-distilled-squad/snapshots/564e9b582944a57a3e586bbb98fd6f0a4118db7f"

qa_pipeline = pipeline("question-answering", model=model_path)

def input_resolver_node(state: dict) -> dict:
    query = state["question"]
    mode = state.get("mode", "chat")

    # Block case inputs in chat mode
    if mode == "chat" and re.fullmatch(r"\d{4,6}", query.strip()):
        return {
            **state,
            "input_type": "invalid",
            "answer": "⚠️ Case numbers are not allowed in Chat Mode. Please switch to Similarity Mode."
        }

    if re.fullmatch(r"\d{4,6}", query.strip()) or re.search(r"\b(case|related|similar|issue)\b", query.lower()):
        return { **state, "input_type": "case" }

    return { **state, "input_type": "question" }




def oracle_fetch_node(state: dict) -> dict:
    # Block case number lookups in chat mode
    if state.get("mode") != "similarity":
        return {
            **state,
            "retrieved_docs": [],
            "answer": "⚠️ Case lookup is only available in Similarity Mode."
        }

    query = state["question"]
    match = re.search(r"\b\d{4,6}\b", query)
    case_number = match.group(0) if match else ""

    case_text = fetch_case_data(case_number)
    if not case_text.strip():
        return {
            **state,
            "retrieved_docs": [],
            "answer": "⚠️ Case not found."
        }

    return {
        **state,
        "context": case_text
    }


oracle_vectorstore = build_oracle_vectorstore()

def get_similarity_node():
    def similarity_node(state: dict) -> dict:
        # 🛑 Block similarity search in chat mode
        if state.get("mode") != "similarity":
            return {
                **state,
                "retrieved_docs": [],
                "answer": "⚠️ Similarity search is only available in Similarity Mode."
            }

        case_text = state.get("context", "").strip()
        if not case_text:
            return {
                **state,
                "retrieved_docs": [],
                "answer": "⚠️ Case not found."
            }

        docs_and_scores = oracle_vectorstore.similarity_search_with_score(case_text, k=5)
        return {
            **state,
            "retrieved_docs": docs_and_scores
        }
    return similarity_node


def format_table_node(state: dict) -> dict:
    docs_and_scores = state.get("retrieved_docs", [])
    formatted_table = "| Rank | Similar Case | Score |\n|------|----------------|-------|\n"
    for i, (doc, score) in enumerate(docs_and_scores):
        snippet = doc.page_content[:80].replace("\n", " ")
        formatted_table += f"| {i+1} | {snippet} | {score:.4f} |\n"
    return {
        **state,
        "answer": formatted_table
    }

def get_retriever_node(vectorstore: FAISS):
    def retriever_node(state: dict) -> dict:
        query = state["question"]
        docs = vectorstore.similarity_search(query)
        return {
            "question": query,
            "context": docs[0].page_content if docs else ""
        }
    return retriever_node

def answer_node(state: dict) -> dict:
    if state.get("mode") != "chat":
        return {
            **state,
            "answer": "⚠️ Chat responses are only available in Chat Mode."
        }

    result = qa_pipeline(
        question=state["question"],
        context=state["context"]
    )

    return {
        **state,
        "answer": result["answer"]
    }