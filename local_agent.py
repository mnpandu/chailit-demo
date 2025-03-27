from transformers import pipeline
from langchain_community.llms import HuggingFacePipeline
from langchain.agents import Tool, initialize_agent
from tools import fetch_case_info, find_similar_cases, retrieve_related_info

generator = pipeline("text-generation", model="gpt2", max_new_tokens=100)
llm = HuggingFacePipeline(pipeline=generator)

tools = [
    Tool.from_function(fetch_case_info),
    Tool.from_function(find_similar_cases),
    Tool.from_function(retrieve_related_info),
]

agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True,
)
