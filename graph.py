# graph.py (modular graph flow)
from typing import TypedDict
from langgraph.graph import StateGraph
from nodes import (
    input_resolver_node,
    oracle_fetch_node,
    get_similarity_node,
    format_table_node,
    get_retriever_node,
    answer_node
)

class QAState(TypedDict):
    question: str
    context: str
    input_type: str
    retrieved_docs: list
    answer: str
    mode: str  # 👈 add this


def build_graph(vectorstore) -> StateGraph:
    builder = StateGraph(state_schema=QAState)

    builder.add_node("resolver", input_resolver_node)
    builder.add_node("oracle", oracle_fetch_node)
    builder.add_node("similarity", get_similarity_node())
    builder.add_node("format", format_table_node)
    builder.add_node("retriever", get_retriever_node(vectorstore))
    builder.add_node("qa", answer_node)

    builder.set_entry_point("resolver")

    builder.add_conditional_edges(
        "resolver",
        lambda state: state["input_type"],
        {
            "case": "oracle",
            "question": "retriever"
        }
    )

    builder.add_edge("oracle", "similarity")
    builder.add_edge("similarity", "format")

    builder.add_edge("retriever", "qa")

    builder.set_finish_point("format")
    builder.set_finish_point("qa")

    return builder.compile()
