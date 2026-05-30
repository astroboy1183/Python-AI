from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Hi! I am Jayanth. How are you?"},
        {"role": "assistant", "content": "I am fine, how are you?"},
    ],
)

print(response.choices[0].message.content)
