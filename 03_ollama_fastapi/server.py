from fastapi import Body, FastAPI
from ollama import Client

app = FastAPI()
client = Client(host="http://localhost:11434",)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/chat")
def chat(
        message:str = Body(
            ...,
            description="Hi! I am Jayanth. How are you?")   
):
    response = client.chat(
        model="gemma:2b",
        messages=[
            {"role": "user", "content": message},
        ]
    )
    return response