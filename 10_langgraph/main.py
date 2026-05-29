from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_classic.chat_models import init_chat_model
from typing_extensions import TypedDict
from typing import Annotated
from dotenv import load_dotenv


load_dotenv()  

llm = init_chat_model("gpt-4.1-mini")

class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    response = llm.invoke(state.get("messages"))
    return {"messages": [response]}


def samplenode(state: State):
    return {"messages": ["Sample message appended."]}


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("samplenode", samplenode)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "samplenode")
graph_builder.add_edge("samplenode", END)

graph = graph_builder.compile()

updated_state = graph.invoke({"messages": ["Hi, My name is Jayanth Appalla"]})
print("updated state:", updated_state)
