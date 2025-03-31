import re
from transformers import pipeline
from langchain_community.vectorstores import FAISS
from oracle_client import fetch_case_data,fetch_claim_data
from vector_store_case_data import build_oracle_vectorstore,find_similar_cases
from vector_store_claims_data import build_claims_vectorstore
from vector_plot import plot_similarity_results

from langchain_huggingface import HuggingFaceEmbeddings
from sentencetransformer import getSentenceModel

embedding_model = HuggingFaceEmbeddings(model_name=getSentenceModel())

model_path = "distilbert-base-cased-distilled-squad"
qa_pipeline = pipeline("question-answering", model=model_path)

oracle_vectorstore = build_oracle_vectorstore()
claims_vectorstore = build_claims_vectorstore()


def oracle_fetch_node(state: dict) -> dict:
    query = state["question"]
    match = re.search(r"\b(MR\d{4,6}|CL\d{4,6})\b", query, re.IGNORECASE)
    identifier = match.group(0) if match else ""
    state["case_number"] = identifier  # keep original field name
    # 1. Handle case ID
    if identifier.startswith("MR"):
        case_text = fetch_case_data(identifier)
        if not case_text.strip():
            return {**state, "retrieved_docs": [], "answer": "⚠️ Case not found."}
        return {**state, "context": case_text}
    # 2. Handle claim ID
    elif identifier.startswith("CL"):
        claim_text = fetch_claim_data(identifier)
        if not claim_text.strip():
            return {**state, "retrieved_docs": [], "answer": "⚠️ Claim not found."}
        return {**state, "context": claim_text}
    # 3. Handle direct case text input
    elif query.lower().startswith("case text:"):
        case_text = query[len("case text:"):].strip()
        return {**state, "context": case_text}

    # 4. Handle direct claim text input
    elif query.lower().startswith("claim text:"):
        claim_text = query[len("claim text:"):].strip()
        return {**state, "context": claim_text}
    return {**state, "retrieved_docs": [], "answer": "⚠️ No valid identifier found."}



def get_similarity_node(source_type="case"):
    def similarity_node(state: dict) -> dict:
        case_number = state.get("case_number", "")
        if source_type == "case":
            docs_and_scores = oracle_vectorstore.similarity_search_with_score(state.get("context", ""), k=5)
        elif source_type == "claim":
            docs_and_scores = claims_vectorstore.similarity_search_with_score(state.get("context", ""), k=5)
        else:
            docs_and_scores = []

        if not docs_and_scores:
            return {
                **state,
                "retrieved_docs": [],
                "answer": f"⚠️ No similar documents found for {case_number}."
            }
        viz_data = plot_similarity_results(docs_and_scores, embedding_model)        

        return {
            **state,
            "retrieved_docs": docs_and_scores
        }
    return similarity_node


def format_case_table_node(state: dict) -> dict:
    docs_and_scores = state.get("retrieved_docs", [])
    formatted_table = "| Rank | Similar Case | Score |\n|------|----------------|-------|\n"
    for i, (doc, score) in enumerate(docs_and_scores):
        formatted_table += f"| {i+1} | {doc.page_content} | {score:.4f} |\n"
    return {**state, "answer": formatted_table}
	

def format_claim_table_node(state: dict) -> dict:
    docs_and_scores = state.get("retrieved_docs", [])
    formatted_table = "| Rank | Case # | Claim # | Claim Text | Score |\n"
    formatted_table += "|------|--------|----------|-------------|--------|\n"

    for i, (doc, score) in enumerate(docs_and_scores):
        meta = doc.metadata
        case_number = meta.get("case_number", "N/A")
        claim_number = meta.get("claim_number", "N/A")

        formatted_table += f"| {i+1} | {case_number} | {claim_number} | {doc.page_content} | {score:.4f} |\n"

    return {**state, "answer": formatted_table}



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
        return {**state, "answer": "⚠️ Chat responses are only available in Chat Mode."}

    result = qa_pipeline(question=state["question"], context=state["context"])
    return {**state, "answer": result["answer"]}


def route_by_identifier(state):
    query = state.get("question", "").strip()
    case_number = state.get("case_number", "")

    # Route based on known identifier
    if case_number.startswith("MR"):
        return "similarity_case"
    elif case_number.startswith("CL"):
        return "similarity_claim"

    # Route based on prefix for free-text input
    if query.lower().startswith("case text:"):
        return "similarity_case"
    elif query.lower().startswith("claim text:"):
        return "similarity_claim"

    # Fallback route
    return "unsupported_case"

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
    progress = "✅ Create QC Task"
    return {
        **state,
        "qualified_claims": claims,
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
