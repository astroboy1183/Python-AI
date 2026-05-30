"""
Multi-user chat demo with persistent memory via MongoDB checkpointing.

Each user is identified by a thread_id. The graph and checkpointer are
shared across all users, but conversation history is isolated per thread_id.

Commands inside the chat:
    /user <name>   — switch to a different user (their old history is loaded)
    /history       — show the current user's conversation history
    /quit          — exit
"""

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain_classic.chat_models import init_chat_model
from typing_extensions import TypedDict
from typing import Annotated
from dotenv import load_dotenv

load_dotenv()

llm = init_chat_model("gpt-4.1-mini")


# ── State + graph (same shape as chat_checkpoint.py) ──────────────────────────

class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)


# ── Multi-user chat loop ──────────────────────────────────────────────────────

DB_URI = "mongodb://admin:admin@localhost:27017"


def main():
    print("=" * 60)
    print("  Multi-user Chat (memory persisted in MongoDB)")
    print("=" * 60)
    print("Commands: /user <name>   /history   /quit\n")

    with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
        graph = graph_builder.compile(checkpointer=checkpointer)

        current_user = input("Login as user: ").strip() or "guest"
        print(f"\n→ Logged in as '{current_user}'. Start chatting!\n")

        while True:
            user_input = input(f"{current_user}: ").strip()

            if not user_input:
                continue

            # ─ Commands ─
            if user_input.lower() == "/quit":
                print("Goodbye!")
                break

            if user_input.startswith("/user "):
                current_user = user_input[6:].strip() or "guest"
                print(f"\n→ Switched to user '{current_user}'.\n")
                continue

            if user_input.lower() == "/history":
                config = {"configurable": {"thread_id": current_user}}
                snapshot = graph.get_state(config)
                if not snapshot.values.get("messages"):
                    print("  (no history yet)\n")
                else:
                    print(f"\n── History for '{current_user}' ──")
                    for msg in snapshot.values["messages"]:
                        role = "you" if msg.type == "human" else "bot"
                        print(f"  {role}: {msg.content}")
                    print()
                continue

            # ─ Normal chat ─
            config = {"configurable": {"thread_id": current_user}}
            result = graph.invoke({"messages": [user_input]}, config)
            bot_reply = result["messages"][-1].content
            print(f"bot: {bot_reply}\n")


if __name__ == "__main__":
    main()
