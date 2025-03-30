from typing import TypedDict
from langgraph.graph import StateGraph
from nodes import (
    oracle_fetch_node,
    get_similarity_node,
    format_case_table_node,
    format_claim_table_node,
    get_retriever_node,
    answer_node,
    qc_fetch_claims_node,
    qc_create_task_node,
    qc_review_node,
    qc_check_complete_node,
    qc_finalize_node,
    route_by_identifier
)

class QAState(TypedDict):
    question: str
    context: str
    answer: str
    mode: str
    case_number: str
    retrieved_docs: list
    qc_status: str

def build_graph(vectorstore) -> StateGraph:
    builder = StateGraph(state_schema=QAState)

    # Core nodes
    builder.add_node("oracle", oracle_fetch_node)
    builder.add_node("similarity_case", get_similarity_node("case"))
    builder.add_node("similarity_claim", get_similarity_node("claim"))
    builder.add_node("format_case", format_case_table_node)
    builder.add_node("format_claim", format_claim_table_node)
    builder.add_node("retriever", get_retriever_node(vectorstore))
    builder.add_node("qa", answer_node)

    # QC flow nodes
    builder.add_node("qc_fetch", qc_fetch_claims_node)
    builder.add_node("qc_task", qc_create_task_node)
    builder.add_node("qc_review", qc_review_node)
    builder.add_node("qc_check", qc_check_complete_node)
    builder.add_node("qc_done", qc_finalize_node)

    # Entry point and router
    builder.set_entry_point("mode_router")
    builder.add_node("mode_router", lambda state: state)

    builder.add_conditional_edges(
        "mode_router",
        lambda state: state["mode"],
        {
            "similarity": "oracle",
            "chat": "retriever",
            "qc": "qc_fetch"
        }
    )

    # Conditional routing from oracle → similarity_case/claim
    builder.add_conditional_edges(
        "oracle",
        route_by_identifier,
        {
            "similarity_case": "similarity_case",
            "similarity_claim": "similarity_claim",
            "unsupported_case": "format_case",   # fallback
            "unsupported_claim": "format_claim"  # fallback
        }
    )

    # Post-similarity routing
    builder.add_edge("similarity_case", "format_case")
    builder.add_edge("similarity_claim", "format_claim")

    builder.add_edge("retriever", "qa")

    # QC workflow
    builder.add_edge("qc_fetch", "qc_task")
    builder.add_edge("qc_task", "qc_review")
    builder.add_edge("qc_review", "qc_check")
    builder.add_edge("qc_check", "qc_done")

    # Finish points
    builder.set_finish_point("qa")
    builder.set_finish_point("format_case")
    builder.set_finish_point("format_claim")
    builder.set_finish_point("qc_done")

    return builder.compile()