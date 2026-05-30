# 13 — Conversational AI App Builder

A voice-driven coding agent. **You talk, it builds.**

You describe the app you want — by voice or text — and the agent asks clarifying questions, then scaffolds the project on disk, narrating each folder and file it creates.

This project combines two earlier ones:
- **Voice loop** from [12_Conversational_AI](../12_Conversational_AI/) (Whisper + TTS)
- **Tool-using coding agent** from [06_cli_agent](../06_cli_agent/) (function calling)

---

## How it works

```
Voice/text input
       ↓
Whisper (skipped for text mode)
       ↓
gpt-4o (with tools: create_folder, create_file)
       ↓
Agent asks clarifying questions OR calls tools to build the project
       ↓
TTS (alloy voice) → ffplay speaks the reply
       ↓
loop until you say "quit"
```

Each turn the full conversation history is sent to the model, so it remembers your earlier preferences (language, framework, features) across the conversation.

---

## Prerequisites

- **OpenAI API key** with credit
- **ffmpeg + ffplay** (for voice mode — see [main README System Requirements](../README.md#system-requirements))

### Platform note for voice mode
The script uses `-f pulse` for microphone capture which is **Linux + PulseAudio only**. On Mac or Windows you must edit `app_builder.py` line 87 before voice mode works:

| OS | Replace `"-f", "pulse"` with |
|---|---|
| macOS | `"-f", "avfoundation"` |
| Windows | `"-f", "dshow"` |
| Linux | leave as `"-f", "pulse"` |

**Or use text mode (option 2)** which works everywhere without ffmpeg setup.

---

## Setup

```bash
pip install -r 13_Conversational_AI_Create_Apps/requirements.txt
```

Add your key to `13_Conversational_AI_Create_Apps/.env`:
```
OPENAI_API_KEY=sk-proj-...
```

---

## Run

```bash
python 13_Conversational_AI_Create_Apps/app_builder.py
```

You'll be asked to pick an input mode:
- **1** — Microphone (records 10s per turn)
- **2** — Text (type each turn)

The agent greets you, asks what to build, and starts collecting requirements.

---

## Example sessions

### Voice mode
Same flow as text mode below, but you speak each input into the mic instead of typing. The agent's reply is spoken back to you via TTS.

---

## 📝 Worked Example — Building a Todo App by Voice

Here's a real run of the agent building a working todo web app. The user gave the requirements one piece at a time through conversation, refined the design, and asked for an extra feature (dark mode) mid-build.

### The conversation

```
Input mode — 1=mic  2=text
> 1
(say 'quit' or press Ctrl+C to exit)

AI:  Hi! I'm your app-building assistant. What would you like to build today?
🔊 [audio plays]

🎤 Recording 10s... speak now!
You: I want to build a simple todo list web app

AI:  Got it! Should I use plain HTML/CSS/JavaScript, or would you prefer a framework
     like React?
🔊 [audio plays]

🎤 Recording 10s... speak now!
You: Plain HTML CSS and JavaScript please, keep it simple

AI:  Perfect. Should the tasks be numbered, and would you like a delete button next
     to each one?
🔊 [audio plays]

🎤 Recording 10s... speak now!
You: Yes numbered with delete buttons. Also can you add a dark mode toggle?

AI:  Sounds good. Building it now.
  📁 Creating folder: todo-app
  📄 Writing file:   todo-app/index.html
  📄 Writing file:   todo-app/style.css
  📄 Writing file:   todo-app/script.js
  📄 Writing file:   todo-app/README.txt

AI:  Done! The todo-app folder has index.html, style.css, and script.js. Open
     index.html in your browser to use it. Tasks auto-number, each has a delete
     button, and there's a button to toggle dark mode.
🔊 [audio plays]

You: quit
Goodbye!
```

### What the agent built

A complete vanilla web app — 115 lines across 4 files — placed in `Python-AI/todo-app/`:

```
todo-app/
├── index.html      ← markup (input, list, add button, theme toggle)
├── style.css       ← styling including .dark class for dark mode
├── script.js       ← add/delete/renumber logic + theme toggle
└── README.txt      ← brief usage notes
```

**`index.html`** — semantic markup:
```html
<div id="app">
  <h1>Todo List</h1>
  <ul id="todo-list"></ul>
  <input type="text" id="new-task" placeholder="Add a new task">
  <button id="add-task-btn">Add Task</button>
  <button id="toggle-theme-btn">Toggle Theme</button>
</div>
```

**`script.js`** — vanilla JS with three functions:
```js
function addTask() {
  // creates an <li> with auto-incremented number + delete button
}

function updateTaskNumbers() {
  // renumbers remaining tasks after a delete
}

function toggleTheme() {
  document.body.classList.toggle('dark');
}
```

**`style.css`** — light theme by default, with a `.dark` class that flips colours.

### Running the result

```bash
cd todo-app
# Open index.html in any browser — no server, no build step
```

The app works immediately. Add tasks, delete them (numbers auto-reorder), and toggle dark mode.

### What this demonstrates

| Feature | How it shows up |
|---|---|
| **Conversational requirements** | Agent asked 2 clarifying questions before building anything |
| **Iterative refinement** | User added "dark mode" mid-conversation — agent incorporated it without restarting |
| **Memory across turns** | "Plain HTML/CSS/JS" preference carried forward into the build phase |
| **Tool use** | 4 `create_file` calls + 1 `create_folder` call, all narrated aloud |
| **Working code, not stubs** | The generated app runs as-is in a browser — not placeholder TODOs |
| **Self-documenting** | Even threw in a `README.txt` without being asked |

This entire interaction cost roughly **$0.10** in API spend (2 Whisper calls, ~5 gpt-4o turns, ~5 TTS responses).

---

## What it can build

The agent isn't restricted — it'll try anything you ask for. Some examples that work well:

- *"a simple chatbot using OpenAI"*
- *"a FastAPI server with a hello endpoint"*
- *"a Streamlit app that displays the current time"*
- *"a Python script that scrapes Hacker News titles"*
- *"a Node.js Express server with two routes"*

It works best for **small, scaffold-level apps** (1-10 files). Don't expect it to generate a full Next.js commerce site from one voice command — though it'll happily try.

---

## Where it creates files

All scaffolded projects go into your **Python-AI root** (one folder up from this script). So a chatbot the agent builds for you will end up at:

```
Python-AI/
├── 13_Conversational_AI_Create_Apps/
└── simple-chatbot/         ← here
    ├── chatbot.py
    ├── requirements.txt
    └── README.md
```

To clean up an experiment, just `rm -rf <folder>`.

---

## Exiting

- Say or type **"quit"**, **"exit"**, **"goodbye"**, or **"bye"**
- Or press **Ctrl+C**

---

## Cost per turn

| Step | Cost |
|---|---|
| Whisper (10s audio) | ~$0.001 |
| gpt-4o (~1-5k tokens per turn, more for tool calls) | ~$0.01–$0.05 |
| TTS-1 (alloy voice) | ~$0.005 |
| **Total** | **~$0.02–$0.05 per turn** |

Roughly $0.30–$1 for a typical "build me something" session.
