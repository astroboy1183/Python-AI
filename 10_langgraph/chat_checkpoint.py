"""Single-thread persistent chat via MongoDB checkpointing.

Run repeatedly with the same thread_id and the conversation continues across
process restarts because state is stored in MongoDB.

Note: keep .invoke() INSIDE the `with MongoDBSaver(...)` block — otherwise the
Mongo connection closes before the graph can use it.
"""

from pathlib import Path
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain_classic.chat_models import init_chat_model

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

llm = init_chat_model("gpt-4.1-mini")


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)


DB_URI = "mongodb://admin:admin@localhost:27017"


def main():
    config = {"configurable": {"thread_id": "Jayanth"}}

    with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
        graph = graph_builder.compile(checkpointer=checkpointer)
        updated_state = graph.invoke(
            State({"messages": ["What is my name?"]}),
            config,
        )
        print("updated state:", updated_state)


if __name__ == "__main__":
    main()
