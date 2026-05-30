import subprocess
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=Path(__file__).parent / ".env")
client = OpenAI()

AUDIO_DIR = Path(__file__).parent / "audio"
AUDIO_DIR.mkdir(exist_ok=True)


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


def chat(text):
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": text}],
    ).choices[0].message.content


def speak(text):
    out = AUDIO_DIR / "response.mp3"
    audio = client.audio.speech.create(model="tts-1", voice="alloy", input=text)
    out.write_bytes(audio.content)
    subprocess.run(["ffplay", "-nodisp", "-autoexit", str(out)], check=True)


def main():
    choice = input("1=mic  2=file  3=text\n> ").strip()
    if choice == "1":
        user_text = transcribe(record())
    elif choice == "2":
        user_text = transcribe(input("path: ").strip())
    else:
        user_text = input("message: ").strip()

    print(f"\nYou: {user_text}")
    reply = chat(user_text)
    print(f"AI:  {reply}\n")
    speak(reply)


if __name__ == "__main__":
    main()
