from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are an expert in maths and only answer maths questions. If it is not a maths question, just say sorry and don't say anything else."},
        {"role": "user", "content": "Hi! I am Jayanth. How are you?"},
        {"role": "assistant", "content": "I am fine, how are you?"},
        {"role": "user", "content": "can you print hello world in python programming language?"},
        {"role":"user", "content":"Can you help me with a plus b whole squared?"}
    ]
)

print(response.choices[0].message.content)