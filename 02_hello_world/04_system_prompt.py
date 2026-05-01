# Zero Shot Prompting: The model is given direct question or task without prior examples.

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

SYSTEM_PROMPT = "You are an expert in coding and only answer coding questions. If it is not a coding question, just say sorry and don't say anything else. Your name is Shivam."

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "I am fine, how are you?"},
        {"role": "user", "content": "can you print hello world in python programming language?"}
        # {"role":"user", "content":"Can you help me with a plus b whole squared formula in maths?"}
    ]
)

print(response.choices[0].message.content)

