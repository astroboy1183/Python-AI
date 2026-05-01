from transformers import AutoTokenizer, pipeline

pipe = pipeline("text-generation", model="google/flan-t5-xl")
messages = [
    {"role": "user", "content": "Who are you?"},
]
pipe(messages)

