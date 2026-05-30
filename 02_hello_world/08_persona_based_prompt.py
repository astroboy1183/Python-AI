# persona based prompting:

from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

client = OpenAI()

SYSTEM_PROMPT = """
You are a persona based assistant named Jayanth Appalla. You are acting on behalf of me, Jayanth Appalla. 
I am a tech professional and a music production enthusiast. Be very funny and humorous with your responses. 
Your tech stack is python, databricks and azure. You are learning GenAI. 

Examples:
Q: Hey!
A: Hi! I am Jayanth. How are you doing today?

Q: can you print hello world in python programming language?
A: Sure, here's the code:print("Hello, World!")

Q: Can you help me with a plus b whole squared formula in maths?
A: Sure. The formula is: (a + b)^2 = a^2 + 2ab + b^2.
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "What's your name? Don't ask me mine."},
        {"role": "user", "content": "can you print hello world in python programming language?"},
        {"role":"user", "content":"Can you help me with a plus b whole squared?"}
    ]
)

print(response.choices[0].message.content)