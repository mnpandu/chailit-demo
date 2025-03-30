from typing import TypedDict, Literal
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
    mode: Literal["similarity", "chat", "qc"]
    case_number: str
    retrieved_docs: list
    qc_status: str

class GraphComponents:
    """Container class for organizing graph components."""
    
    @staticmethod
    def core_nodes(builder: StateGraph, vectorstore) -> None:
        """Add core question answering nodes."""
        builder.add_node("oracle", oracle_fetch_node)
        builder.add_node("similarity_case", get_similarity_node("case"))
        builder.add_node("similarity_claim", get_similarity_node("claim"))
        builder.add_node("format_case", format_case_table_node)
        builder.add_node("format_claim", format_claim_table_node)
        builder.add_node("retriever", get_retriever_node(vectorstore))
        builder.add_node("qa", answer_node)
    
    @staticmethod
    def qc_nodes(builder: StateGraph) -> None:
        """Add quality control workflow nodes."""
        builder.add_node("qc_fetch", qc_fetch_claims_node)
        builder.add_node("qc_task", qc_create_task_node)
        builder.add_node("qc_review", qc_review_node)
        builder.add_node("qc_check", qc_check_complete_node)
        builder.add_node("qc_done", qc_finalize_node)
    
    @staticmethod
    def routing(builder: StateGraph) -> None:
        """Configure all routing logic."""
        # Entry point and mode routing
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

        # Oracle → similarity_case/claim routing
        builder.add_conditional_edges(
            "oracle",
            route_by_identifier,
            {
                "similarity_case": "similarity_case",
                "similarity_claim": "similarity_claim",
                "unsupported_case": "format_case",
                "unsupported_claim": "format_claim"
            }
        )

    @staticmethod
    def edges(builder: StateGraph) -> None:
        """Configure all edges between nodes."""
        # Similarity flow edges
        builder.add_edge("similarity_case", "format_case")
        builder.add_edge("similarity_claim", "format_claim")
        
        # Chat flow edge
        builder.add_edge("retriever", "qa")
        
        # QC workflow edges
        builder.add_edge("qc_fetch", "qc_task")
        builder.add_edge("qc_task", "qc_review")
        builder.add_edge("qc_review", "qc_check")
        builder.add_edge("qc_check", "qc_done")
    
    @staticmethod
    def finish_points(builder: StateGraph) -> None:
        """Configure all finish points."""
        builder.set_finish_point("qa")
        builder.set_finish_point("format_case")
        builder.set_finish_point("format_claim")
        builder.set_finish_point("qc_done")

def build_graph(vectorstore) -> StateGraph:
    """Build and compile the QA workflow graph."""
    builder = StateGraph(state_schema=QAState)
    
    # Add all components in logical order
    GraphComponents.core_nodes(builder, vectorstore)
    GraphComponents.qc_nodes(builder)
    GraphComponents.routing(builder)
    GraphComponents.edges(builder)
    GraphComponents.finish_points(builder)
    
    return builder.compile()