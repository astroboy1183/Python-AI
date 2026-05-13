# Python AI

A progressive series of AI and LLM projects built with Python, covering tokenization, prompting techniques, local models, AI agents, and RAG pipelines.

---

## Project Structure

```
Python-AI/
├── 01_Tokenization/
├── 02_hello_world/
├── 03_ollama_fastapi/
├── 04_huggingface/
├── 05_weather_agent/
├── 06_cli_agent/
├── 07_RAG/
└── 08_RAG_queue/
```

---

## 01 — Tokenization

**File:** `01_Tokenization/main.py`

Explores how LLMs break text into tokens using OpenAI's `tiktoken` library.

- Encodes a string into token IDs
- Decodes token IDs back into readable text
- Counts the number of tokens in a string

```bash
python 01_Tokenization/main.py
```

---

## 02 — Hello World (Prompting Techniques)

**Files:** `02_hello_world/01_main.py` through `09_alpaca_prompt.py`

A series of scripts exploring different prompting strategies with the OpenAI API.

| File | Technique |
|---|---|
| `01_main.py` | Basic conversation with message history |
| `02_gemini_hello.py` | Same concept using Google Gemini |
| `03_openai_conversation.py` | Multi-turn conversation |
| `04_system_prompt.py` | Using system prompts to set behaviour |
| `05_few_shot_prompting.py` | Providing examples to guide responses |
| `06_structured_output.py` | Forcing JSON structured output |
| `07_chain_of_thought_prompting.py` | Step-by-step reasoning loop with plan → output |
| `08_persona_based_prompt.py` | Giving the model a specific persona |
| `09_alpaca_prompt.py` | Alpaca-style instruction prompting |

```bash
python 02_hello_world/07_chain_of_thought_prompting.py
```

---

## 03 — Ollama + FastAPI

**File:** `03_ollama_fastapi/server.py`

A FastAPI server that connects to a locally running Ollama instance and serves a chat endpoint backed by the `gemma:2b` model.

- `GET /` — health check
- `POST /chat` — sends a message to the local Gemma model and returns the response

**Requirements:** Ollama must be running locally on port `11434`.

```bash
uvicorn 03_ollama_fastapi.server:app --reload
```

---

## 04 — HuggingFace

**Files:** `04_huggingface/main.py`, `gemma.py`, `gemma_4.py`

Experiments with loading and running open-source models directly from HuggingFace using the `transformers` library.

- Loads `google/flan-t5-xl` via the `pipeline` API
- Runs text generation locally without any external API

```bash
python 04_huggingface/main.py
```

---

## 05 — Weather Agent

**Files:** `05_weather_agent/main.py`, `weather.py`

A streaming AI agent with chain-of-thought reasoning that answers weather queries, including support for landmarks and ambiguous locations.

**How it works:**
1. User asks about weather for any city or landmark
2. Agent reasons step-by-step (displayed live via streaming)
3. Calls `search_locations` tool to geocode the query
4. Calls `get_weather` tool to fetch live weather data
5. Presents the result with full location context

**Tools used:**
- Open-Meteo Geocoding API — resolves city/landmark names to coordinates
- Open-Meteo Weather API — fetches live weather data

```bash
python 05_weather_agent/main.py
```

---

## 06 — CLI Coding Agent

**File:** `06_cli_agent/main.py`

A terminal-based AI agent that scaffolds project folder structures and writes code files on demand, narrating every step out loud (chain-of-thought).

**How it works:**
1. User describes a project (e.g. "create a Flask REST API")
2. Agent plans the structure step-by-step
3. Announces each action before executing it
4. Creates folders and writes complete code files

**Tools the agent has:**
| Tool | What it does |
|---|---|
| `create_folder` | Creates directories (including nested) |
| `create_file` | Writes complete files with content |
| `list_directory` | Lists folder contents |
| `read_file` | Reads existing files before modifying |

All projects are created inside the `Python-AI/` root directory.

```bash
python 06_cli_agent/main.py
```

---

## 07 — RAG (Retrieval Augmented Generation)

**Files:** `07_RAG/index.py`, `07_RAG/query.py`

A RAG pipeline that lets you query a PDF document using natural language. Uses Qdrant as the vector database and OpenAI for embeddings and answer generation.

**Infrastructure:** `docker-compose.yml` runs Qdrant on port `6333`.

### index.py — Ingestion
1. Loads the PDF page by page using `PyPDFLoader`
2. Splits it into chunks of 1500 characters with 200-character overlap using `RecursiveCharacterTextSplitter`
3. Embeds each chunk using OpenAI `text-embedding-3-small`
4. Stores all embeddings in Qdrant under the collection `node_js_guide`

### query.py — Retrieval
1. Takes a user question as input
2. Embeds the question and runs similarity search against Qdrant
3. Retrieves the top matching chunks along with page numbers
4. Passes the chunks as context to `gpt-4o-mini`
5. Returns the answer with page citations

```bash
# Start Qdrant
docker compose -f 07_RAG/docker-compose.yml up -d

# Index the PDF (run once)
python 07_RAG/index.py

# Query
python 07_RAG/query.py
```

---

## 08 — RAG with Redis Queue

**Folders:** `08_RAG_queue/queues/`, `08_RAG_queue/client/`, `08_RAG_queue/frontend/`

An extended RAG pipeline that introduces a job queue so queries are processed asynchronously in the background. Includes a FastAPI backend and a React frontend.

**Infrastructure:** `docker-compose.yml` runs three services:
| Container | Port | Purpose |
|---|---|---|
| Valkey (Redis) | `6379` | Job queue and result store |
| Qdrant | `6333` | Vector database |
| Redis Insight | `5540` | Visual browser for Redis data |

### Architecture

```
React Frontend :5173
      ↓
FastAPI Server :8000
      ↓
Valkey Queue  :6379
      ↓
RQ Worker (background process)
      ↓
Qdrant :6333  →  OpenAI API
      ↓
Result stored back in Valkey
      ↓
React Frontend polls and displays result
```

### Files

**`index.py`** — Ingests the PDF into Qdrant (same as 07_RAG but self-contained).

**`queues/worker.py`** — The RQ worker function `process_query(query)`:
- Runs similarity search on Qdrant (top 8 chunks, filtered by relevance score ≥ 0.3)
- Calls `gpt-4o` with retrieved context
- Returns the answer with page citations

**`queues/server.py`** — FastAPI server with three routes:
- `GET /` — health check
- `POST /query` — enqueues a job, returns `job_id` immediately
- `GET /result/{job_id}` — returns job status (`pending` / `completed` / `failed`) and result

**`queues/main.py`** — Entry point that starts the FastAPI server via uvicorn.

**`client/rq_client.py`** — CLI client that enqueues a query and polls until the result is ready.

**`frontend/`** — React (Vite) app that:
- Lets you submit multiple queries without waiting
- Polls every 1.5 seconds per job
- Shows each query as a card with a live status badge (pending → completed)

### Running the full pipeline

```bash
# 1. Start containers
cd 08_RAG_queue
docker compose up -d

# 2. Index the PDF (run once)
python index.py

# 3. Start FastAPI server
python -m queues.main

# 4. Start RQ worker (separate terminal)
rq worker

# 5. Start React frontend (separate terminal)
cd frontend
npm run dev
```

Open `http://localhost:5173` to use the UI.

**Optional monitoring:**
```bash
# RQ Dashboard — view job queues in real time
rq-dashboard --redis-url redis://localhost:6379
# Open http://localhost:9181
```

### Scaling workers

To process multiple queries simultaneously, run multiple workers:
```bash
for i in {1..4}; do rq worker & done
```

---

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker

### Install Python dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment variables
Each project folder that uses an API key needs a `.env` file:
```
OPENAI_API_KEY=your_key_here
```
