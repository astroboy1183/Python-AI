from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

from openai import OpenAI
client = OpenAI()

# Assign the result to 'response' so you can print it later
response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Caption this image in about 50 words."},
                {
                    "type": "image_url", 
                    "image_url": {
                        "url": "https://images.pexels.com/photos/12899191/pexels-photo-12899191.jpeg"
                    }
                }
            ]
        }
    ]
)

print("Response:", response.choices[0].message.content)