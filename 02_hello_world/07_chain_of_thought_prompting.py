# chain-of-thought prompting:

from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

client = OpenAI()

SYSTEM_PROMPT = """
You are an expert AI assistant in user queries using chain-of-thought.
You work on start, plan and output steps.
You need to first plan what needs to be done. The plan can be multiple steps.
Once you think enough plan has been done, finally you can give the output.

Rules:
Strictly follow the JSON Output.
Only run one step at a time.
The sequence of steps is start(where user gives input), plan (that can be multiple times)
and output(which is going to be displayed).

output JSON format:

{
    "step": "start"| "plan"| "output",
    "content": "string"
}

Example: 
{
Start: can you solve 2+3*5
Plan: { "step": "plan", "content": "The user seems to want to solve 2+3*5. Let's break it down into smaller steps."}
Plan: { "step": "plan", "content":"Looking at the problem. I can solve using the BODMAS Rule."}
Plan:{step: "plan", "First multiply 5 with 3 and get 15. Then add 2 with 15 and get 17.}
Output: { "step": "output", "content": "The answer is 17."} 
}
"""
print("*"*50)

message_history = [{"role": "system", "content": SYSTEM_PROMPT}]
inp = input("Enter your query: ")
message_history.append({"role": "user", "content": inp})

while True:
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    response_format={"type":"json_object"},
    messages=message_history
    )

    raw_results = response.choices[0].message.content
    results = json.loads(raw_results)
    message_history.append({"role": "assistant", "content": raw_results})

    if results["step"] == "output":
        print(results["content"])
        break

    if results["step"] == "plan":
        print(results["content"])


print("*"*50)