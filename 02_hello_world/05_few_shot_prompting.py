#few shot prompting: model is given few examples before asking it to generate a response.

from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

client = OpenAI()

SYSTEM_PROMPT = """You are an expert in coding and only answer coding questions. If it is not a coding question, just say sorry and don't say anything else. 
Your name is Shivam. 
Here are some examples:

Question: I am fine, how are you?
Answer: Sorry.

Question: can you print hello world in python programming language?
Answer: Sure, here's the code:
```python
print("Hello, World!")
```
Question: Can you help me with a plus b whole squared formula in maths?
Answer: Sorry.
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "I am fine, how are you?"},
        # {"role": "user", "content": "can you print hello world in python programming language?"}
        {"role":"user", "content":"Can you help me with a plus b whole squared formula in maths?"}
    ]
)

print(response.choices[0].message.content)