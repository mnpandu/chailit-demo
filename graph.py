from typing import TypedDict
from langgraph.graph import StateGraph
from nodes import (
    input_resolver_node,
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
    input_type: str
    retrieved_docs: list
    answer: str
    mode: str
    case_number: str
    qc_status: str

def build_graph(vectorstore) -> StateGraph:
    builder = StateGraph(state_schema=QAState)

    builder.add_node("resolver", input_resolver_node)
    builder.add_node("oracle", oracle_fetch_node)
    builder.add_node("similarity", get_similarity_node())
    builder.add_node("format", format_table_node)
    builder.add_node("retriever", get_retriever_node(vectorstore))
    builder.add_node("qa", answer_node)

    # QC Agent nodes
    builder.add_node("qc_fetch", qc_fetch_claims_node)
    builder.add_node("qc_task", qc_create_task_node)
    builder.add_node("qc_review", qc_review_node)
    builder.add_node("qc_check", qc_check_complete_node)
    builder.add_node("qc_done", qc_finalize_node)

    builder.set_entry_point("resolver")

    builder.add_conditional_edges(
        "resolver",
        lambda state: state["input_type"],
        {
            "case": "oracle",
            "question": "retriever",
            "qc": "qc_fetch"
        }
    )

    builder.add_edge("oracle", "similarity")
    builder.add_edge("similarity", "format")

    builder.add_edge("retriever", "qa")

    # QC Flow
    builder.add_edge("qc_fetch", "qc_task")
    builder.add_edge("qc_task", "qc_review")
    builder.add_edge("qc_review", "qc_check")
    builder.add_edge("qc_check", "qc_done")

    builder.set_finish_point("format")
    builder.set_finish_point("qa")
    builder.set_finish_point("qc_done")

    return builder.compile()