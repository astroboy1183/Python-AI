# Conversational AI — Voice Chat with Memory

A continuous voice-driven chat: speech-to-text → ChatGPT (with conversation memory) → text-to-speech.

## Features

- 🎤 **Speech recognition** via OpenAI Whisper
- 🤖 **gpt-4o-mini** with full message history per session
- 🔊 **Text-to-speech** via OpenAI TTS (`alloy` voice)
- 🎯 **Three input modes**: microphone, audio file, or text
- 🔁 **Continuous loop** — keeps the conversation going until you say `quit`

## Requirements

### System dependencies

**Linux:**
```bash
sudo apt install ffmpeg pulseaudio
```
PulseAudio is required because the script uses `-f pulse` for microphone capture.

**macOS:**
```bash
brew install ffmpeg
```
Then edit `conversational_ai.py` line 17 — change `"-f", "pulse"` to `"-f", "avfoundation"`.

**Windows:**
1. Download FFmpeg from https://ffmpeg.org/download.html and add to PATH
2. Edit `conversational_ai.py` line 17 — change `"-f", "pulse"` to `"-f", "dshow"`

### Python dependencies

```bash
pip install -r 12_Conversational_AI/requirements.txt
```

## Setup

Add your OpenAI API key to `12_Conversational_AI/.env`:
```
OPENAI_API_KEY=sk-proj-...
```

**Mac / Linux** (alternative to .env):
```bash
export OPENAI_API_KEY="sk-proj-..."
```

**Windows PowerShell** (alternative to .env):
```powershell
$env:OPENAI_API_KEY="sk-proj-..."
```

## Usage

```bash
python 12_Conversational_AI/conversational_ai.py
```

You'll be asked once for input mode:
- **1** — Microphone (records 10 seconds per turn)
- **2** — Audio file (you provide a path each turn)
- **3** — Text (type each turn)

The agent maintains conversation history, so it remembers what you said earlier in the same session.

## Exit

Say or type `quit`, `exit`, `goodbye`, or `bye` — or press Ctrl+C.

## Example session

```
1=mic  2=file  3=text
> 3
(say 'quit' or press Ctrl+C to exit)

you: Hi, my name is Jayanth
You: Hi, my name is Jayanth
AI:  Hi Jayanth! Nice to meet you. How can I help today?
🔊 [audio plays]

you: What's my name?
You: What's my name?
AI:  Your name is Jayanth.
🔊 [audio plays]

you: quit
Goodbye!
```

## Files generated

| File | When |
|---|---|
| `audio/input.wav` | Microphone mode only |
| `audio/response.mp3` | Always (the AI's spoken reply) |

Both stored in `12_Conversational_AI/audio/` (gitignored).

## Troubleshooting

**`ffmpeg: command not found`**
- Install FFmpeg for your OS (see Requirements above).

**`ffplay: command not found`**
- On minimal installs ffplay can be separate from ffmpeg. On Debian/Ubuntu, `sudo apt install ffmpeg` includes it. On Mac, `brew install ffmpeg` includes it.

**`OPENAI_API_KEY not set` / `AuthenticationError`**
- Confirm `.env` is in `12_Conversational_AI/` (not the repo root).
- Verify your key has credit at https://platform.openai.com/usage.

**No audio from microphone**
- Linux: list inputs with `pactl list short sources`, ensure default isn't muted.
- macOS: `system_profiler SPAudioDataType` shows audio devices.
- Windows: Settings → Sound → Input device list.
- Make sure the app/terminal has microphone permission.

**Mic mode records silence**
- The `-f pulse` flag is Linux-only. Use `-f avfoundation` on Mac and `-f dshow` on Windows (see Requirements above).

## Costs (approximate)

| Step | Cost per turn |
|---|---|
| Whisper (10s audio) | ~$0.001 |
| gpt-4o-mini reply | ~$0.0003 (grows slightly each turn as history accumulates) |
| TTS-1 (`alloy` voice) | ~$0.008 |
| **Total** | **~$0.01 per turn** |

A 30-turn conversation typically stays under **$0.30** total.

## Persistence note

Conversation memory is **in-process only** — exit the script and history is gone. For persistent cross-session memory, see [10_langgraph](../10_langgraph/) (checkpointing) or [11_memory_agent(mem0)](../11_memory_agent(mem0)/) (fact extraction).
