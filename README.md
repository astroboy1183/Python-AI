# Python AI

A progressive series of AI and LLM projects built with Python — covering tokenization, prompting techniques, local models, AI agents, RAG pipelines, async job queues, multimodal inputs, graph-based agents (LangGraph), persistent memory (mem0 + Neo4j graphs), and voice-driven conversational AI.

Designed as a learning track: start at `01_Tokenization` and work your way to `12_Conversational_AI`.

> 📚 **For theory & definitions:** see [CONCEPTS.md](CONCEPTS.md) — a glossary explaining every concept used across the projects (tokens, embeddings, RAG, LangGraph, checkpointing, mem0, etc.) with cross-links back to the projects that use them.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [System Requirements](#system-requirements)
3. [Getting Started](#getting-started)
4. [API Keys](#api-keys)
5. [Per-Project Overview](#per-project-overview)
6. [Port Reference](#port-reference)
7. [Project Details](#project-details)
8. [Troubleshooting](#troubleshooting)
9. [Tips & Conventions](#tips--conventions)

---

## Quick Start

For the impatient — get something running in 5 minutes:

**Windows (PowerShell):**
```powershell
git clone git@github.com:astroboy1183/Python-AI.git
cd Python-AI
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# add your OpenAI key to .env (see "API Keys" section)
python 01_Tokenization\main.py
```

**Mac / Linux (Bash/Zsh):**
```bash
git clone git@github.com:astroboy1183/Python-AI.git
cd Python-AI
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# add your OpenAI key to .env (see "API Keys" section)
python 01_Tokenization/main.py
```

---

## System Requirements

### All platforms
- **Python 3.10 or higher** ([python.org/downloads](https://www.python.org/downloads/))
- **Git** ([git-scm.com](https://git-scm.com/))
- **Docker Desktop** (required for projects 07–11) ([docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/))
- **Node.js 18+** (only needed for `08_RAG_queue` React frontend) ([nodejs.org](https://nodejs.org/))
- **ffmpeg + ffplay** (only needed for `12_Conversational_AI` audio recording/playback)
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
  - Windows: download from [ffmpeg.org/download](https://ffmpeg.org/download.html) and add to PATH
- ~15 GB free disk space (project `04_huggingface` downloads large models)

### Windows-specific
- Use **PowerShell** or **Windows Terminal** — avoid CMD where possible.
- **Docker Desktop** requires **WSL2** enabled. Follow Microsoft's [WSL install guide](https://learn.microsoft.com/en-us/windows/wsl/install) first.
- The Python launcher might be called `py` instead of `python`. If `python` doesn't work, try `py`.
- Folder `11_memory_agent(mem0)` has parentheses — always quote it in commands: `cd "11_memory_agent(mem0)"`.

### Mac-specific
- Install via **Homebrew** for the smoothest experience:
  ```bash
  brew install python git docker node
  brew install --cask docker
  ```
- On Apple Silicon (M1/M2/M3), all projects work without additional config.

### Linux-specific
- Most distributions have Python 3.10+ pre-installed. Verify with `python3 --version`.
- Install Docker Engine via your package manager:
  ```bash
  sudo apt install docker.io docker-compose-plugin   # Ubuntu/Debian
  sudo systemctl start docker
  sudo usermod -aG docker $USER && newgrp docker     # avoid using sudo with docker
  ```

---

## Getting Started

### 1. Clone the repository

```bash
git clone git@github.com:astroboy1183/Python-AI.git
cd Python-AI
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\activate
```
If activation is blocked by execution policy, run once per session:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**Mac / Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your prompt confirming it's active.

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

> **Note:** Some folders (e.g. `10_langgraph/`) have their own `requirements.txt` with project-specific additions. The root one covers all common packages. Re-run `pip install -r <folder>/requirements.txt` if a folder has its own.

### 4. Verify Docker is running (for projects 07+)

```bash
docker --version
docker ps
```

If `docker ps` errors out with "Cannot connect to the Docker daemon", start Docker Desktop (or `sudo systemctl start docker` on Linux).

---

## API Keys

Each project that calls an LLM API needs its own `.env` file **in the same folder as the script**. The `load_dotenv(...)` calls look for `.env` relative to the script.

### Required keys per project

| Project | Keys needed |
|---|---|
| `02_hello_world` | `OPENAI_API_KEY`, optionally `GEMINI_API_KEY` |
| `05_weather_agent` | `OPENAI_API_KEY` |
| `06_cli_agent` | `OPENAI_API_KEY` |
| `07_RAG` | `OPENAI_API_KEY` |
| `08_RAG_queue` | `OPENAI_API_KEY` |
| `09_multimodal_ai` | `OPENAI_API_KEY` |
| `10_langgraph` | `OPENAI_API_KEY`, `GEMINI_API_KEY` (only for `conditional.py`) |
| `11_memory_agent(mem0)` | `OPENAI_API_KEY`, optionally `NEO4J_URI` + `NEO4J_USERNAME` + `NEO4J_PASSWORD` (for graph store) |
| `12_Conversational_AI` | `OPENAI_API_KEY` |

`01_Tokenization`, `03_ollama_fastapi`, and `04_huggingface` need **no API keys** — they run locally.

### Where to get the keys

| Provider | Get a key from |
|---|---|
| **OpenAI** | https://platform.openai.com/api-keys (requires billing setup) |
| **Google Gemini** | https://aistudio.google.com/apikey (free tier available) |
| **Neo4j Aura** (optional, for 11) | https://console.neo4j.io (free tier available) — download `.txt` credentials file when creating an instance |

### Creating `.env` files

Create a file named `.env` (not `env` or `env.txt`) in the project folder. Example for `10_langgraph/.env`:

```
OPENAI_API_KEY=sk-proj-your-key-here
GEMINI_API_KEY=AIza-your-key-here
```

> **Security:** `.env` files are already in `.gitignore` and will never be committed. Never share or commit these keys.

---

## Per-Project Overview

| # | Project | Needs Docker | Needs API key | External dependencies |
|---|---|---|---|---|
| 01 | Tokenization | ❌ | ❌ | None |
| 02 | Hello World (prompting) | ❌ | ✅ OpenAI / Gemini | None |
| 03 | Ollama + FastAPI | ❌ | ❌ | **Ollama installed locally** |
| 04 | HuggingFace | ❌ | ❌ | ~10 GB model download on first run |
| 05 | Weather Agent | ❌ | ✅ OpenAI | None |
| 06 | CLI Coding Agent | ❌ | ✅ OpenAI | None |
| 07 | RAG | ✅ Qdrant | ✅ OpenAI | None |
| 08 | RAG + Redis Queue | ✅ Valkey + Qdrant + Redis Insight | ✅ OpenAI | Node.js for frontend |
| 09 | Multimodal AI | ❌ | ✅ OpenAI | None |
| 10 | LangGraph | ✅ MongoDB + Mongo Express | ✅ OpenAI / Gemini | None |
| 11 | Memory Agent (mem0) | ✅ Qdrant | ✅ OpenAI (+ optional Neo4j Aura) | mem0 v0.1.x required (see project section) |
| 12 | Conversational AI (voice) | ❌ | ✅ OpenAI | **ffmpeg + ffplay** for audio |

---

## Port Reference

Across all projects these ports are used. **Stop containers from one project before starting another if ports conflict.**

| Port | Service | Used in |
|---|---|---|
| `5173` | React dev server | 08 |
| `5540` | Redis Insight | 08 |
| `6333` | Qdrant | 07, 08, 11 |
| `6379` | Valkey / Redis | 08 |
| `8000` | FastAPI server | 03, 08 |
| `8081` | Mongo Express | 10 |
| `9181` | RQ Dashboard | 08 (optional) |
| `11434` | Ollama | 03 |
| `27017` | MongoDB | 10 |

To stop all Docker containers from a project:
```bash
cd <project-folder>
docker compose down
```

To kill a process holding a port:
- **Mac/Linux:** `lsof -ti :<PORT> | xargs kill -9`
- **Windows (PowerShell):** `Get-NetTCPConnection -LocalPort <PORT> | Stop-Process -Id { $_.OwningProcess } -Force`

---

## Project Details

### 01 — Tokenization

**File:** `01_Tokenization/main.py`

Explores how LLMs break text into tokens using OpenAI's `tiktoken` library.

- Encodes a string into token IDs
- Decodes token IDs back into readable text
- Counts the number of tokens

**Run:**
```bash
python 01_Tokenization/main.py
```

---

### 02 — Hello World (Prompting Techniques)

**Files:** `02_hello_world/01_main.py` through `09_alpaca_prompt.py`

A series of scripts exploring different prompting strategies.

| File | Technique |
|---|---|
| `01_main.py` | Basic conversation with message history |
| `02_gemini_hello.py` | Same concept using Google Gemini |
| `03_openai_conversation.py` | Multi-turn conversation |
| `04_system_prompt.py` | Using system prompts to set behaviour |
| `05_few_shot_prompting.py` | Providing examples to guide responses |
| `06_structured_output.py` | Forcing JSON structured output |
| `07_chain_of_thought_prompting.py` | Step-by-step reasoning with plan → output |
| `08_persona_based_prompt.py` | Giving the model a specific persona |
| `09_alpaca_prompt.py` | Alpaca-style instruction prompting |

**Setup:** Create `02_hello_world/.env` with your `OPENAI_API_KEY` (and `GEMINI_API_KEY` if running the Gemini script).

**Run:**
```bash
python 02_hello_world/07_chain_of_thought_prompting.py
```

---

### 03 — Ollama + FastAPI

**File:** `03_ollama_fastapi/server.py`

A FastAPI server that proxies chat to a locally running Ollama instance.

**Setup:**
1. Install Ollama from https://ollama.com/download
2. Pull the model:
   ```bash
   ollama pull gemma:2b
   ```
3. Make sure Ollama is running (its tray icon should be visible, or run `ollama serve`).

**Run the server:**
```bash
uvicorn 03_ollama_fastapi.server:app --reload
```

Visit `http://localhost:8000/docs` and try `POST /chat`.

---

### 04 — HuggingFace

**Files:** `04_huggingface/main.py`, `gemma.py`, `gemma_4.py`

Runs open-source models locally via the `transformers` library.

**⚠️ First run downloads ~10 GB** of model weights for `google/flan-t5-xl`. Make sure you have disk space and a fast internet connection.

**Run:**
```bash
python 04_huggingface/main.py
```

---

### 05 — Weather Agent

**Files:** `05_weather_agent/main.py`, `weather.py`

A streaming agent with chain-of-thought reasoning that fetches weather data for cities or landmarks.

**How it works:**
1. User asks about weather (city, landmark, monument, etc.)
2. Agent reasons step-by-step (streamed live)
3. Calls `search_locations` (Open-Meteo Geocoding) to resolve coordinates
4. Calls `get_weather` (Open-Meteo Forecast) for live data
5. Presents result with full location context

No external API keys needed beyond OpenAI — Open-Meteo is free and key-less.

**Run:**
```bash
python 05_weather_agent/main.py
```

---

### 06 — CLI Coding Agent

**File:** `06_cli_agent/main.py`

A terminal-based agent that scaffolds project folders and writes code, narrating every step out loud.

**Tools the agent has:**

| Tool | What it does |
|---|---|
| `create_folder` | Creates directories (incl. nested) |
| `create_file` | Writes complete files |
| `list_directory` | Lists folder contents |
| `read_file` | Reads existing files before modifying |

All scaffolded projects land in the `Python-AI/` root.

**Run:**
```bash
python 06_cli_agent/main.py
```

---

### 07 — RAG (Retrieval Augmented Generation)

**Files:** `07_RAG/index.py`, `07_RAG/query.py`

Queries a PDF using natural language. Uses Qdrant + OpenAI.

**Setup (run order matters!):**
```bash
# 1. Start Qdrant
cd 07_RAG
docker compose up -d

# 2. Embed the PDF into Qdrant (run ONCE)
python index.py

# 3. Query
python query.py
```

`index.py` only needs to be run once — embeddings persist in Qdrant. Use `query.py` for all subsequent questions.

Qdrant dashboard: `http://localhost:6333/dashboard`

---

### 08 — RAG with Redis Queue

An async RAG pipeline with FastAPI + RQ workers + React frontend. Probably the most involved project — read carefully.

#### Folder Structure
```
08_RAG_queue/
├── docker-compose.yml    — infrastructure (Valkey, Qdrant, Redis Insight)
├── .env                  — OpenAI API key
├── index.py              — PDF ingestion (run once)
├── client/rq_client.py   — CLI client (alternative to frontend)
├── queues/
│   ├── main.py           — FastAPI entry point
│   ├── server.py         — API routes
│   └── worker.py         — RAG logic (runs as RQ worker)
└── frontend/             — React (Vite) UI
```

#### Containers
| Container | Port | Purpose |
|---|---|---|
| Valkey (Redis-compatible) | 6379 | Job queue + result store |
| Qdrant | 6333 | Vector DB for PDF chunks |
| Redis Insight | 5540 | Browser UI for Valkey |

#### Run the full pipeline

You'll need **4 terminals**, all with the venv activated:

```bash
# Terminal 1 — Infrastructure
cd 08_RAG_queue
docker compose up -d
python index.py           # ingest PDF (once)
python -m queues.main     # start FastAPI server (port 8000)

# Terminal 2 — Worker
cd 08_RAG_queue
rq worker

# Terminal 3 — Frontend
cd 08_RAG_queue/frontend
npm install               # first time only
npm run dev               # opens at http://localhost:5173

# Terminal 4 — (Optional) RQ Dashboard
pip install rq-dashboard  # first time only
rq-dashboard --redis-url redis://localhost:6379
# Open http://localhost:9181
```

Open `http://localhost:5173` to use the chat UI.

#### Scaling workers
Run multiple workers for parallel job processing:

**Mac/Linux:**
```bash
for i in {1..4}; do rq worker & done
```

**Windows (PowerShell):**
```powershell
1..4 | ForEach-Object { Start-Process -NoNewWindow rq -ArgumentList "worker" }
```

#### End-to-end flow
```
React UI → POST /query → FastAPI → Valkey queue → RQ Worker → Qdrant search → gpt-4o
                                          ↑                                       ↓
                                          └───── result stored in Valkey ←────────┘
                                                            ↓
                                          React polls GET /result/{job_id}
```

---

### 09 — Multimodal AI

**File:** `09_multimodal_ai/main.py`

Captioning images using OpenAI's vision-capable model `gpt-4.1-mini`. Sends an image URL alongside a text prompt.

**Run:**
```bash
python 09_multimodal_ai/main.py
```

---

### 10 — LangGraph

A progressive intro to **LangGraph**: graph-based orchestration for branching, looping, and stateful LLM workflows.

#### Files

| File | What it demonstrates |
|---|---|
| `main.py` | Simplest graph: `START → chatbot → END` |
| `conditional.py` | Conditional edges + LLM-as-judge with Gemini fallback |
| `chat_checkpoint.py` | MongoDB-backed checkpointing — conversation memory persists across runs |
| `multi_user_chat.py` | Shared graph, isolated memory per user via `thread_id` |

#### Key concepts

- `StateGraph` — defines the graph schema
- `add_node` / `add_edge` — wires nodes
- `add_conditional_edges` — dynamic routing based on a router function
- `Annotated[list, add_messages]` — reducer that appends messages instead of overwriting
- `MongoDBSaver` — persists state to MongoDB
- `thread_id` — isolates conversations per user

#### Setup
```bash
cd 10_langgraph
docker compose up -d      # MongoDB + Mongo Express
```

#### Run any script
```bash
python main.py
python conditional.py     # needs GEMINI_API_KEY in .env
python chat_checkpoint.py
python multi_user_chat.py
```

Mongo Express UI at `http://localhost:8081` (login `admin` / `admin`).

> **Tip — multi-user chat:** in `multi_user_chat.py`, log in as `alice`, chat, then type `/user bob` to switch users. Bob has a separate, isolated memory. Switch back to `alice` and her history returns.

---

### 11 — Memory Agent (mem0)

**File:** `11_memory_agent(mem0)/mem.py`

Persistent fact-based memory using **mem0** — extracts and stores facts about the user in Qdrant (vector store) and optionally Neo4j (graph store), retrieving only relevant ones via vector search.

#### mem0 vs LangGraph checkpointing

| Feature | LangGraph Checkpointer | mem0 |
|---|---|---|
| Stores | Raw messages + full state | Extracted facts only |
| Retrieval | Loads entire history by `thread_id` | Vector search — only relevant facts |
| Scaling | Grows with conversation length | Stays compact long-term |
| Best for | Resumable workflows, replay | Long-term personalization |

#### ⚠️ Critical: install the right mem0 version

mem0 v2.x dropped support for the Neo4j `graph_store` config we use. Install v0.1.x explicitly:

```bash
pip install "mem0ai==0.1.116" rank-bm25 langchain-neo4j neo4j
```

If you skip this, `mem0ai` will install v2.x by default and your Neo4j config will be silently ignored.

#### Setup
```bash
cd "11_memory_agent(mem0)"          # quote the folder name!
docker compose up -d                 # starts Qdrant
python mem.py
```

**Windows users:** the folder has parentheses — quote it everywhere:
```powershell
cd "11_memory_agent(mem0)"
```

#### Neo4j graph store (optional but recommended)

The `docker-compose.yml` only starts Qdrant. For the **graph store** (which tracks relationships between facts like `(Jayanth)-[LIKES]->(food)`), use **Neo4j Aura** (cloud, free tier):

1. Sign up at https://console.neo4j.io
2. Create a free instance — download the credentials file when prompted
3. Add to `.env`:
   ```
   NEO4J_URI=neo4j+s://<your-instance>.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=<from-credentials-file>
   ```
4. Test the connection: `python test_neo4j.py`

#### Persistent storage caveat

The current `docker-compose.yml` for Qdrant **does NOT use a Docker volume**, meaning every `docker compose down` wipes your stored memories. To persist, add a volume:

```yaml
volumes:
  - qdrant_data:/qdrant/storage

volumes:
  qdrant_data:
```

#### Try it
```
> Hi, I'm Jayanth and I love south Indian food
> I am 28 years old
> What's my favorite cuisine and how old am I?
```

Verify graph data in Neo4j Aura console with:
```cypher
MATCH (n)-[r]->(m) RETURN n, r, m
```

---

### 12 — Conversational AI (Voice)

**File:** `12_Conversational_AI/conversational_ai.py`

A voice-driven conversational pipeline chaining three OpenAI APIs:

```
[mic / file / text]  →  Whisper  →  gpt-4o-mini  →  TTS (alloy voice)  →  ffplay
```

#### Three input modes
| Option | What happens |
|---|---|
| 1 (mic) | Records 10s from your microphone via ffmpeg → sends to Whisper |
| 2 (file) | Uses an existing audio file (WAV/MP3/M4A) you provide |
| 3 (text) | Skips Whisper — type your message directly |

All three then go through gpt-4o-mini → TTS → ffplay plays the spoken reply.

#### Prerequisites
- **ffmpeg + ffplay** installed (see [System Requirements](#system-requirements))
- OpenAI API key in `12_Conversational_AI/.env`

The script uses `-f pulse` for mic input which works on Linux. On Mac, change to `-f avfoundation`. On Windows, change to `-f dshow`.

#### Setup
```bash
pip install openai python-dotenv
```

#### Run
```bash
python 12_Conversational_AI/conversational_ai.py
```

When prompted, pick `1` (mic), `2` (file), or `3` (text). Generated audio is saved to `12_Conversational_AI/audio/`.

#### Cost per turn (approx)
| Step | Cost |
|---|---|
| Whisper (10s audio) | ~$0.001 |
| gpt-4o-mini reply | ~$0.0003 |
| TTS-1 (alloy voice) | ~$0.008 |
| **Total** | **~$0.01 per turn** |

---

## Troubleshooting

### Common errors and what they mean

| Error | Cause | Fix |
|---|---|---|
| `Connection refused` on a port | Docker container isn't running | `docker compose up -d` in the project folder |
| `Cannot connect to the Docker daemon` | Docker Desktop isn't running | Start Docker Desktop (or `sudo systemctl start docker`) |
| `ModuleNotFoundError: ...` | venv not activated, or package not installed | Activate venv, then `pip install -r requirements.txt` |
| `ModuleNotFoundError: rank_bm25` | mem0 graph store missing dep | `pip install rank-bm25` |
| `OPENAI_API_KEY not found` / `AuthenticationError` | `.env` is missing or in wrong folder | Create `.env` in the project's own folder, not at root |
| `Cannot use MongoClient after close` | `with` block closed the Mongo connection | Keep `.invoke()` inside the `with` block |
| `Bind for 0.0.0.0:PORT failed: port is already allocated` | Another container/process holds the port | `docker compose down` in other projects, or kill the process |
| `pymongo.errors.ServerSelectionTimeoutError` | MongoDB isn't running | Start MongoDB container: `docker compose up -d` |
| `ValueError: filters must contain at least one of: user_id...` | mem0 v0.1.x search call missing `user_id` | Pass `user_id="..."` directly (not inside `filters={}`) |
| mem0 not writing to Neo4j | You have mem0 v2.x which dropped `graph_store` | Downgrade: `pip install "mem0ai==0.1.116"` |
| `ffmpeg: command not found` | ffmpeg not installed (project 12) | Mac: `brew install ffmpeg`. Linux: `sudo apt install ffmpeg`. Windows: download from ffmpeg.org |
| `LangChainDeprecationWarning` | Just a warning, not an error | Ignore, or upgrade to non-deprecated import path |
| `Set-ExecutionPolicy` error (Windows) | PowerShell blocking venv activation | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| `ollama: command not found` | Ollama not installed | Install from https://ollama.com/download |
| Neo4j `ServiceUnavailable` | Aura free instance is paused (auto-pauses after 3 days idle) | Log in at https://console.neo4j.io to wake it |
| OpenAI `Not Available` on dashboard | You logged in via SSO which created a separate account | Use email login matching the account that has the keys |

### General debugging steps

1. **Verify venv is active** — your shell prompt should start with `(venv)`.
2. **Verify Docker is running** — `docker ps` should list containers (or be empty without erroring).
3. **Check ports** — `docker ps` shows which ports each container exposes.
4. **Check `.env` location** — must be in the project folder, not the root (unless the script's `load_dotenv()` says otherwise).
5. **Re-read the error** — Python tracebacks are usually precise about the file and line number.

---

## Tips & Conventions

- **Always activate venv** before running any project: `(venv)` should appear in your prompt.
- **One project at a time** for Docker — to avoid port conflicts, `docker compose down` an old project before bringing up a new one.
- **API keys live in per-folder `.env` files** — never at the root, never hardcoded.
- **First run of `index.py`** in `07_RAG` and `08_RAG_queue` is required before querying; embeddings persist in Qdrant.
- **HuggingFace download size** in `04_huggingface` is ~10 GB — have disk space ready.
- **Stop containers when done**:
  ```bash
  docker compose down
  ```
- **Free up Docker disk space** periodically:
  ```bash
  docker system prune -a --volumes
  ```

---

## License

Personal learning project. Not licensed for production use.

## Contact

Built by **Jayanth Appalla** — feel free to open issues or PRs on GitHub.
