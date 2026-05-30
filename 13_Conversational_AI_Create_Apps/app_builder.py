"""
Conversational app-builder agent.

User talks (voice or text) → agent asks clarifying questions → when ready,
agent scaffolds the project by creating folders and writing code files,
while narrating each step out loud.

Combines project 12 (voice loop) + project 06 (tool-using coding agent).
"""

import json
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=Path(__file__).parent / ".env")
client = OpenAI()

# Generated projects land here (one folder up — Python-AI root)
PROJECTS_ROOT = Path(__file__).parent.parent
AUDIO_DIR = Path(__file__).parent / "audio"
AUDIO_DIR.mkdir(exist_ok=True)


SYSTEM_PROMPT = """You are a friendly conversational coding agent that helps users build small applications.

Behaviour:
- Greet the user and ask what they want to build.
- Ask 1-2 short clarifying questions if the request is vague (language, framework, features).
- Once you have enough info, announce the plan in 1-2 short sentences, then create the project.
- For every tool call, narrate plainly what you are doing — keep it brief because it will be spoken aloud.
- After scaffolding, summarise the structure in 2-3 sentences and explain how to run it.
- Keep all conversational responses SHORT (2-3 sentences max) since they will be spoken via TTS.
- All project paths are relative to your working directory. Use a clean kebab-case folder name."""


# ── Tools ─────────────────────────────────────────────────────────────────────

def create_folder(path: str) -> str:
    target = PROJECTS_ROOT / path
    target.mkdir(parents=True, exist_ok=True)
    return json.dumps({"ok": True, "path": str(target)})


def create_file(path: str, content: str) -> str:
    target = PROJECTS_ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return json.dumps({"ok": True, "path": str(target), "bytes": len(content)})


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_folder",
            "description": "Create a folder (and any missing parents).",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Create or overwrite a file with the given content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
]

TOOL_FUNCTIONS = {"create_folder": create_folder, "create_file": create_file}


# ── Audio I/O ─────────────────────────────────────────────────────────────────

def record(seconds=10):
    out = AUDIO_DIR / "input.wav"
    print(f"🎤 Recording {seconds}s... speak now!")
    subprocess.run(
        ["ffmpeg", "-f", "pulse", "-i", "default", "-t", str(seconds), "-y", str(out)],
        check=True, capture_output=True,
    )
    return out


def transcribe(audio_path):
    with open(audio_path, "rb") as f:
        return client.audio.transcriptions.create(model="whisper-1", file=f).text


def speak(text):
    out = AUDIO_DIR / "response.mp3"
    audio = client.audio.speech.create(model="tts-1", voice="alloy", input=text)
    out.write_bytes(audio.content)
    subprocess.run(["ffplay", "-nodisp", "-autoexit", str(out)], check=True)


def get_user_input(mode):
    if mode == "1":
        return transcribe(record())
    return input("you: ").strip()


# ── Agent loop ────────────────────────────────────────────────────────────────

def run_agent_turn(messages):
    """Run one agent turn — may include multiple tool calls. Returns final text reply."""
    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        msg = response.choices[0].message

        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in (msg.tool_calls or [])
            ] or None,
        })

        if not msg.tool_calls:
            return msg.content or ""

        # Execute each tool, narrate, feed result back
        for tc in msg.tool_calls:
            fn_name = tc.function.name
            fn_args = json.loads(tc.function.arguments)

            if fn_name == "create_folder":
                print(f"  📁 Creating folder: {fn_args['path']}")
            elif fn_name == "create_file":
                print(f"  📄 Writing file:   {fn_args['path']}")

            result = TOOL_FUNCTIONS[fn_name](**fn_args)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})


def main():
    mode = input("Input mode — 1=mic  2=text\n> ").strip()
    print("(say 'quit' or press Ctrl+C to exit)\n")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Greet first — agent speaks first
    greeting = run_agent_turn(messages + [{"role": "user", "content": "Greet me and ask what I'd like to build."}])
    messages.append({"role": "user", "content": "Greet me and ask what I'd like to build."})
    messages.append({"role": "assistant", "content": greeting})
    print(f"AI:  {greeting}\n")
    speak(greeting)

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

        reply = run_agent_turn(messages)
        print(f"AI:  {reply}\n")
        if reply:
            speak(reply)


if __name__ == "__main__":
    main()
