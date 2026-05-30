from dotenv import load_dotenv
from mem0 import Memory
import os
from openai import OpenAI

load_dotenv()
client = OpenAI()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

config = {
    "version":"v1.1",
    "embedder":{
        "provider":"openai",
        "config":{
            "model":"text-embedding-3-small",
            "api_key":OPENAI_API_KEY}
    },
    "llm":{"provider":"openai",
        "config":{
            "model":"gpt-4.1-mini",
            "api_key":OPENAI_API_KEY}
    },
    "vector_store":{
        "provider":"qdrant",
        "config":{"host":"localhost",
                "port":6333,
                "collection_name":"memory_agent_collection"}
            },
    "graph_store":{
        "provider":"neo4j",
        "config":{
            "url": NEO4J_URI,
            "username": NEO4J_USERNAME,
            "password": NEO4J_PASSWORD,
        }
    }
}


mem_client = Memory.from_config(config)

while True:
    user_query = input("> ")

    search_memory = mem_client.search(query=user_query, user_id="jayanthappalla")

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
        ]
    )

    ai_response = response.choices[0].message.content
    print(f"AI Response: {ai_response}")

    mem_client.add(user_id = "jayanthappalla",
        messages=[{"role": "user", "content": user_query},
                         {"role": "assistant", "content": ai_response}
                         ])

    print("Memory updated with the latest interaction.")