from transformers import pipeline

# flan-t5-xl is an encoder-decoder (seq2seq) model — use text2text-generation, not text-generation
pipe = pipeline("text2text-generation", model="google/flan-t5-xl")
output = pipe("Who are you?", max_new_tokens=64)
print(output[0]["generated_text"])
