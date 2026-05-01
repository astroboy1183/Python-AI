from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import pipeline

pipe = pipeline("text-generation", model="google/gemma-3-1b-it")
messages = [
    {"role": "user", "content": "Who are you?"},
]
pipe(messages)


tokenizer = AutoTokenizer.from_pretrained("google/gemma-3-1b-it")
model = AutoModelForCausalLM.from_pretrained("google/gemma-3-1b-it")
messages = [
    {"role": "user", "content": "Who are you?"},
]
inputs = tokenizer.apply_chat_template(
	messages,
	add_generation_prompt=True,
	tokenize=True,
	return_dict=True,
	return_tensors="pt",
).to(model.device)

outputs = model.generate(**inputs, max_new_tokens=40)
print(tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:]))