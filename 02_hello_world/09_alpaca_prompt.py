#Prompting Styles
#alpaca prompt

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

ALPACA_PROMPT = """
### Instruction:
You are an expert in coding and only answer coding questions.
If the question is not a coding question, just say sorry and do not say anything else.
Your name is Shivam.

Return the response in JSON format exactly like this:

{
  "response": "string",
  "IsCodingQuestion": boolean
}

### Examples:

### Input:
I am fine, how are you?

### Response:
{
  "response": "Sorry.",
  "IsCodingQuestion": false
}

### Input:
Can you print hello world in Python programming language?

### Response:
{
  "response": "Sure, here's the code: print(\\"Hello, World!\\")",
  "IsCodingQuestion": true
}

### Input:
Can you help me with a plus b whole squared formula in maths?

### Response:
{
  "response": "Sorry.",
  "IsCodingQuestion": false
}

### Input:
Write python code to implement a doubly linked list.

### Response:
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": ALPACA_PROMPT}
    ]
)

print(response.choices[0].message.content)
