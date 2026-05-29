import os
from pathlib import Path
from typing_extensions import Literal, TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from google import genai
from typing import Optional

load_dotenv()

openai_client = OpenAI()
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class State(TypedDict):
    user_query: str
    llm_output: Optional[str]
    is_good:Optional[bool]

def chatbot_chatgpt(state: State):
    print("chatbot_chatgpt Node", state)
    response = openai_client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": state["user_query"]}]
    )
    state["llm_output"] = response.choices[0].message.content
    return state

def evaluate_response(state: State) -> Literal["chatbot_gemini", "endnode"]:
    print("evaluate_response Node", state)

    judge = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict judge. Reply with ONLY the word 'yes' if the "
                    "answer thoroughly and correctly addresses the question. Reply "
                    "'no' if it is vague, incorrect, refuses, or admits it does not know."
                ),
            },
            {
                "role": "user",
                "content": f"Question: {state['user_query']}\nAnswer: {state['llm_output']}",
            },
        ],
    )
    verdict = judge.choices[0].message.content.strip().lower()
    state["is_good"] = verdict.startswith("y")
    print(f"  Judge verdict: {verdict}  → routing to {'endnode' if state['is_good'] else 'chatbot_gemini'}")

    return "endnode" if state["is_good"] else "chatbot_gemini"

def chatbot_gemini(state: State):
    print("chatbot_gemini Node", state)
    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=state["user_query"],
    )
    state["llm_output"] = response.text
    return state

def endnode(state: State):
    print("endnode",state)
    return state

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot_chatgpt", chatbot_chatgpt)
graph_builder.add_node("chatbot_gemini", chatbot_gemini)
graph_builder.add_node("endnode", endnode)

graph_builder.add_edge(START, "chatbot_chatgpt")
graph_builder.add_conditional_edges("chatbot_chatgpt", evaluate_response)
graph_builder.add_edge("chatbot_gemini", "endnode")
graph_builder.add_edge("endnode", END)

graph = graph_builder.compile() 
updated_state = graph.invoke({"user_query": "What is 2+2?"})
print("updated state:", updated_state)

