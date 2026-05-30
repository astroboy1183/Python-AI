import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from mem0 import Memory

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

client = OpenAI()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

USER_ID = "jayanthappalla"

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "openai",
        "config": {"model": "text-embedding-3-small", "api_key": OPENAI_API_KEY},
    },
    "llm": {
        "provider": "openai",
        "config": {"model": "gpt-4.1-mini", "api_key": OPENAI_API_KEY},
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "memory_agent_collection",
        },
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": NEO4J_URI,
            "username": NEO4J_USERNAME,
            "password": NEO4J_PASSWORD,
        },
    },
}


def main():
    mem_client = Memory.from_config(config)
    print("Memory-enabled chat (type 'quit' or press Ctrl+C to exit)\n")

    while True:
        try:
            user_query = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_query:
            continue
        if user_query.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        search_memory = mem_client.search(query=user_query, user_id=USER_ID)
        memory_facts = "\n".join(f"- {m['memory']}" for m in search_memory.get("results", []))

        SYSTEM_PROMPT = f"""You are a helpful assistant with memory of past conversations.
Use the following remembered facts about the user when relevant:
{memory_facts if memory_facts else "(no relevant memories yet)"}
"""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query},
            ],
        )

        ai_response = response.choices[0].message.content
        print(f"AI Response: {ai_response}")

        mem_client.add(
            user_id=USER_ID,
            messages=[
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": ai_response},
            ],
        )
        print("Memory updated with the latest interaction.\n")


if __name__ == "__main__":
    main()
