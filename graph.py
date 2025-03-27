from typing import TypedDict
from langgraph.graph import StateGraph
from nodes import (
    oracle_fetch_node,
    get_similarity_node,
    format_table_node,
    get_retriever_node,
    answer_node,
    qc_fetch_claims_node,
    qc_create_task_node,
    qc_review_node,
    qc_check_complete_node,
    qc_finalize_node
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

    builder.add_node("oracle", oracle_fetch_node)
    builder.add_node("similarity", get_similarity_node())
    builder.add_node("format", format_table_node)
    builder.add_node("retriever", get_retriever_node(vectorstore))
    builder.add_node("qa", answer_node)

    builder.add_node("qc_fetch", qc_fetch_claims_node)
    builder.add_node("qc_task", qc_create_task_node)
    builder.add_node("qc_review", qc_review_node)
    builder.add_node("qc_check", qc_check_complete_node)
    builder.add_node("qc_done", qc_finalize_node)

    # Use `mode` directly for entry dispatch
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

    builder.add_edge("oracle", "similarity")
    builder.add_edge("similarity", "format")

    builder.add_edge("retriever", "qa")

    builder.add_edge("qc_fetch", "qc_task")
    builder.add_edge("qc_task", "qc_review")
    builder.add_edge("qc_review", "qc_check")
    builder.add_edge("qc_check", "qc_done")

    builder.set_finish_point("qa")
    builder.set_finish_point("format")
    builder.set_finish_point("qc_done")

    return builder.compile()