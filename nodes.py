import re
from transformers import pipeline
from langchain_community.vectorstores import FAISS
from oracle_client import fetch_case_data
from oracle_data_vector_store import build_oracle_vectorstore

model_path = "distilbert-base-cased-distilled-squad"

qa_pipeline = pipeline("question-answering", model=model_path)
oracle_vectorstore = build_oracle_vectorstore()

def oracle_fetch_node(state: dict) -> dict:
    query = state["question"]
    match = re.search(r"\b\d{4,6}\b", query)
    case_number = match.group(0) if match else ""
    state["case_number"] = case_number

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


def get_similarity_node():
    def similarity_node(state: dict) -> dict:
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
       formatted_table += f"| {i+1} | {doc.page_content} | {score:.4f} |\n"
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

# ------------------ QC Nurse Agentic AI ------------------

def qc_fetch_claims_node(state: dict) -> dict:
    case_number = state.get("case_number", "000000")
    claims = [f"Claim-{case_number}-{i}" for i in range(1, 4)]
    progress = "✅ Fetch all claims under the case"
    return {
        **state,
        "qc_claims": claims,
        "qc_progress": [progress],
        "qc_status": progress
    }

def qc_create_task_node(state: dict) -> dict:
    claims = state.get("qc_claims", [])
    qualified = claims
    progress = "✅ Create QC Task"
    return {
        **state,
        "qualified_claims": qualified,
        "qc_status": progress,
        "qc_progress": state.get("qc_progress", []) + [progress]
    }

def qc_review_node(state: dict) -> dict:
    reviewed = [f"{claim}: Reviewed ✅" for claim in state.get("qualified_claims", [])]
    progress = "✅ Review each claim and update QC Status"
    return {
        **state,
        "reviewed_claims": reviewed,
        "qc_status": progress,
        "qc_progress": state.get("qc_progress", []) + [progress]
    }

def qc_check_complete_node(state: dict) -> dict:
    all_done = all("Reviewed" in c for c in state.get("reviewed_claims", []))
    progress = "✅ Check if all claims are reviewed"
    status = "QC Completed" if all_done else "QC Incomplete"
    return {
        **state,
        "qc_status": status,
        "qc_progress": state.get("qc_progress", []) + [progress]
    }

def qc_finalize_node(state: dict) -> dict:
    progress = [
        "✅ Preparing Claims for QC Task.",
        "✅ Create QC Task",
        "✅ Review each claim and update QC Status",
        "✅ Check if all claims are reviewed",
        "✅ QC Task Completed and Close Task.",
        "✅ Send Email for confirmation.",
    ]
    full_log = state.get("qc_progress", []) + progress
    return {
        **state,
        "answer": "\n".join(full_log),
        "qc_status": "Email sent",
        "qc_progress": full_log
    }