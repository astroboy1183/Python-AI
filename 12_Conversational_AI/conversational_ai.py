import subprocess
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=Path(__file__).parent / ".env")
client = OpenAI()

AUDIO_DIR = Path(__file__).parent / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

SYSTEM_PROMPT = (
    "You are a friendly conversational assistant. Keep replies natural and concise "
    "(2-3 sentences) so they sound good when spoken aloud."
)


def record(seconds=10):
    out = AUDIO_DIR / "input.wav"
    print(f"Recording {seconds}s... speak now!")
    subprocess.run(
        ["ffmpeg", "-f", "pulse", "-i", "default", "-t", str(seconds), "-y", str(out)],
        check=True, capture_output=True,
    )
    return out


def transcribe(audio_path):
    with open(audio_path, "rb") as f:
        return client.audio.transcriptions.create(model="whisper-1", file=f).text


def chat(messages):
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    ).choices[0].message.content


def speak(text):
    out = AUDIO_DIR / "response.mp3"
    audio = client.audio.speech.create(model="tts-1", voice="alloy", input=text)
    out.write_bytes(audio.content)
    subprocess.run(["ffplay", "-nodisp", "-autoexit", str(out)], check=True)


def get_user_input(mode):
    if mode == "1":
        return transcribe(record())
    if mode == "2":
        return transcribe(input("path: ").strip())
    return input("you: ").strip()


def main():
    mode = input("Pick input mode — 1=mic  2=file  3=text\n> ").strip()
    print("(say 'quit' or press Ctrl+C to exit)\n")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            user_text = get_user_input(mode)
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_text:
            continue
        if user_text.lower().strip(".!? ") in ("quit", "exit", "goodbye", "bye"):
            print(f"You: {user_text}\nGoodbye!")
            break

        print(f"You: {user_text}")
        messages.append({"role": "user", "content": user_text})

        reply = chat(messages)
        messages.append({"role": "assistant", "content": reply})

        print(f"AI:  {reply}\n")
        speak(reply)


if __name__ == "__main__":
    main()
