# chain-of-thought prompting:

from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

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


# response = client.chat.completions.create(
#     model="gpt-4o-mini",
#     response_format={"type":"json_object"},
#     messages=[
#         {"role": "system", "content": SYSTEM_PROMPT},
#         # {"role": "user", "content": "I am fine, how are you?"},
#         {"role": "user", "content": "can you print hello world in python programming language?"},
#         {"role":"user", "content":"Can you help me with 2/3*4+7-2*4?"},
#         {"role":"assistant","content":json.dumps({"step": "start", "content": "Can you help me with 2/3*4+7-2*4?"})},
#         {"role":"user", "content":json.dumps({"step": "plan", "content": "The user seems to want to solve 2/3*4+7-2*4. Let's break it down into smaller steps."})},
#         {"role":"user", "content":json.dumps({"step": "plan", "content": "First, we need to follow the order of operations (BODMAS/BIDMAS). We'll start with the division and multiplication."})},
#         {"role":"user", "content":json.dumps({"step": "plan", "content": "Now, let's handle the division first: 2 divided by 3 gives approximately 0.67. Then we will multiply this result by 4."})},
#         {"role":"user", "content":json.dumps({"step": "plan", "content": "Calculating 2 divided by 3 gives approximately 0.67, and now multiplying this by 4 results in approximately 2.67."})},
#         {"role":"user", "content":json.dumps({"step": "plan", "content": "Next, we'll add 7 to the result of the division and multiplication, resulting in 9.67."})},
#         {"role":"user", "content":json.dumps({"step": "plan", "content": "Now, we will handle the multiplication of 2 and 4, which gives us 8."})},
#         {"role":"user", "content":json.dumps({"step": "plan", "content": "Finally, we will subtract the result of the last multiplication (8) from the sum we previously calculated (9.67), which will give us approximately 1.67."})},
#         {"role":"user", "content":json.dumps({"step": "output", "content": "The answer is approximately 1.67."})}
#     ]
# )

# print(response.choices[0].message.content)