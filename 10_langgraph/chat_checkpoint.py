from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.mongodb import MongoDBSaver
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


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# graph = graph_builder.compile()

# ─────────────────────────────────────────────────────────────────────────────
# ❌ MISTAKE I MADE EARLIER (kept here for reference):
#
# def compile_graph_with_checkpointer():
#     DB_URI = "mongodb://admin:admin@localhost:27017"
#     with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
#         graph = graph_builder.compile(checkpointer=checkpointer)
#     return graph                  # ← `with` block exits HERE, closing the Mongo connection
#
# graph_with_checkpointer = compile_graph_with_checkpointer()
# config = {"configurable": {"thread_id": "Jayanth"}}
# updated_state = graph_with_checkpointer.invoke(            # ← crashes with:
#     State({"messages": ["Hi, My name is Jayanth Appalla"]}),  #   pymongo.errors.InvalidOperation:
#     config,                                                    #   Cannot use MongoClient after close
# )
#
# WHY IT BROKE:
# The `with` block closes the Mongo connection on function exit. The returned
# graph still references the (now-dead) checkpointer, so the next .invoke()
# call fails when it tries to read/write checkpoints.
#
# ✅ FIX: keep .invoke() INSIDE the same `with` block so the connection stays open.
# ─────────────────────────────────────────────────────────────────────────────

DB_URI = "mongodb://admin:admin@localhost:27017"
config = {"configurable": {"thread_id": "Jayanth"}}

with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
    graph = graph_builder.compile(checkpointer=checkpointer)
    updated_state = graph.invoke(
        State({"messages": ["What is my name?"]}),
        config,
    )
    print("updated state:", updated_state)