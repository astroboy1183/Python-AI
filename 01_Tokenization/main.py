import tiktoken

enc = tiktoken.encoding_for_model("gpt-3.5-turbo")

text = "Hey There! I am Jayanth Appalla."

tokens = enc.encode(text)
print("Tokens: ", tokens)

decoded_text = enc.decode([25216, 374, 0, 357, 9309, 643, 1348, 404, 2583, 9930, 13])
print("Decoded Text: ", decoded_text)

token_count = len(tokens)
print("Token Count: ", token_count)