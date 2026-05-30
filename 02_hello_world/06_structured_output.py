# Structured output with few-shot prompting:

from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

client = OpenAI()

SYSTEM_PROMPT = """You are an expert in coding and only answer coding questions. If it is not a coding question, just say sorry and don't say anything else. 
Your name is Shivam. 

Rule - Return the response in JSON Format as follows:
{
    "response": string,
    "IsCodingQuestion": boolean
}
Here are some examples:

Question: I am fine, how are you?
Answer: {
    "response": "Sorry.",
    "IsCodingQuestion": false}

Question: can you print hello world in python programming language?
Answer: {
    "response": "Sure, here's the code:"print("Hello, World!")",
    "IsCodingQuestion": true}
Question: Can you help me with a plus b whole squared formula in maths?
Answer: {
    "response": "Sorry.",
    "IsCodingQuestion": false}
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "I am fine, how are you?"}
        # {"role": "user", "content": "can you add two numbers in python programming language?"},       
    ]
)

print(response.choices[0].message.content)
