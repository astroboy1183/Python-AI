# Concepts & Glossary

This document explains the **what** and **why** behind every concept used across the Python-AI projects. For setup instructions and how to actually run the code, see [README.md](README.md).

Each entry includes:
- **Definition** — plain-language explanation
- **Why it matters** — real-world context
- **Used in** — which projects use it
- Sometimes a small example or analogy

---

## Table of Contents

1. [Foundations](#1-foundations)
2. [Prompting Techniques](#2-prompting-techniques)
3. [AI Agents](#3-ai-agents)
4. [RAG (Retrieval Augmented Generation)](#4-rag-retrieval-augmented-generation)
5. [LangChain Ecosystem](#5-langchain-ecosystem)
6. [LangGraph](#6-langgraph)
7. [Memory](#7-memory)
8. [Production Patterns](#8-production-patterns)
9. [Databases & Drivers](#9-databases--drivers)
10. [Multimodal](#10-multimodal)
11. [Infrastructure](#11-infrastructure)

---

## 1. Foundations

### Tokens & Tokenization

A **token** is the smallest unit an LLM reads or writes. It's usually a word fragment — common words like *"the"* are one token, while rare words like *"tokenization"* might split into `token`, `ization`. Tokenization is the process of converting raw text into a sequence of numeric token IDs.

**Why it matters:**
- LLMs charge **per token** (input and output), so token count directly affects cost
- Context windows are measured in tokens, not characters or words
- Different models use different tokenizers — the same text can be 100 tokens in GPT-4 and 120 tokens in Claude

**Used in:** [01_Tokenization](README.md#01--tokenization)

**Example:**
```
Text:    "Hey there!"
Tokens:  [25216, 374, 0]   ← 3 tokens
Decoded: "Hey there!"
```

Tools: `tiktoken` (OpenAI's tokenizer library).

---

### Embeddings & Vector Space

An **embedding** is a fixed-length list of numbers (a vector) that represents the *meaning* of a piece of text. Texts with similar meaning produce vectors close together in N-dimensional space.

**Why it matters:**
- Enables semantic search — *"capital of France"* and *"Paris"* live near each other in vector space, even though they share no words
- Foundation for RAG, recommendation systems, clustering, deduplication
- Different models produce different-dimensional vectors (e.g. OpenAI `text-embedding-3-small` = 1536 dimensions)

**Used in:** [07_RAG](README.md#07--rag-retrieval-augmented-generation), [08_RAG_queue](README.md#08--rag-with-redis-queue), [11_memory_agent](README.md#11--memory-agent-mem0)

**Analogy:** every concept gets a location on a high-dimensional map. *"Dog"* and *"puppy"* are neighbours. *"Dog"* and *"calculus"* are far apart.

---

### Context Window

The **context window** is the maximum number of tokens an LLM can process in a single request — both input and output combined.

| Model | Context window |
|---|---|
| `gpt-4o` | ~128,000 tokens |
| `gpt-4o-mini` | ~128,000 tokens |
| `gpt-4.1-mini` | ~1,000,000 tokens |
| `gemini-2.0-flash` | ~1,000,000 tokens |
| `claude-opus-4-7` | ~200,000 tokens |

**Why it matters:**
- If your prompt + retrieved context + expected output exceeds the window, you'll get truncation or an error
- Larger windows = stuff more chat history / documents in, but also higher cost and slower responses
- A key motivation for RAG: rather than dump 1,000 pages into the prompt, retrieve only the 5 relevant chunks

**Used in:** every LLM-based project, especially relevant for [07_RAG](README.md#07--rag-retrieval-augmented-generation) where context size determines what fits.

---

### Model Providers

The major LLM providers used in these projects.

| Provider | Models | SDK | Pricing |
|---|---|---|---|
| **OpenAI** | gpt-4o, gpt-4o-mini, gpt-4.1, text-embedding-3-* | `openai` | Paid, per-token |
| **Google** | gemini-2.0-flash, gemini-2.0-pro | `google-genai` | Free tier + paid |
| **HuggingFace** | Hosted open-source models (Flan-T5, Gemma, etc.) | `transformers` | Free (runs locally) |
| **Ollama** | Local hosting of open-source models | `ollama` | Free (runs locally) |

**Used in:** [02_hello_world](README.md#02--hello-world-prompting-techniques) (OpenAI + Gemini), [03_ollama_fastapi](README.md#03--ollama--fastapi) (Ollama), [04_huggingface](README.md#04--huggingface) (HuggingFace), [10_langgraph/conditional.py](README.md#10--langgraph) (multi-provider with fallback).

---

## 2. Prompting Techniques

### Zero-shot, One-shot, Few-shot Prompting

How many examples you show the model before asking it to do the task.

- **Zero-shot:** *"Translate this to French: 'Hello'"* — no examples
- **One-shot:** *"Translate to French. Example: 'Hi' → 'Salut'. Now: 'Hello'"* — one example
- **Few-shot:** Same as one-shot but with 3-5 examples — usually most reliable

**Why it matters:**
- More examples generally = better accuracy, but more tokens (cost)
- For structured tasks (JSON extraction, classification), few-shot dramatically improves consistency
- Trade-off: longer prompt vs. better output quality

**Used in:** [02_hello_world/05_few_shot_prompting.py](README.md#02--hello-world-prompting-techniques)

---

### System Prompt

A persistent instruction at the start of every conversation that sets the model's behaviour, role, and constraints. Treated with higher priority than user messages by most models.

**Why it matters:**
- Locks in the model's persona/tone across multiple turns
- Used to enforce safety guidelines, output format, domain restrictions
- Anti-jailbreak: harder for users to override system-level instructions

**Used in:** every project from [02_hello_world](README.md#02--hello-world-prompting-techniques) onwards.

**Example:**
```python
messages = [
    {"role": "system", "content": "You are a Python tutor. Always show code examples."},
    {"role": "user", "content": "How do loops work?"}
]
```

---

### Chain-of-Thought (CoT)

A prompting technique where you instruct the model to **reason step-by-step** before giving the final answer.

**Why it matters:**
- Dramatically improves performance on math, logic, and multi-step problems
- Gives users transparency into the model's reasoning
- Lets you debug failures by inspecting the reasoning trace

**Used in:** [02_hello_world/07_chain_of_thought_prompting.py](README.md#02--hello-world-prompting-techniques), [05_weather_agent](README.md#05--weather-agent), [06_cli_agent](README.md#06--cli-coding-agent)

**Example:**
```
Q: If a train leaves at 3pm going 60 mph and another at 4pm going 80 mph, when do they meet?

Without CoT: "5pm" (often wrong)

With CoT: 
"Step 1: First train has 1-hour head start, covers 60 miles by 4pm.
 Step 2: From 4pm, gap is 60 miles, closing speed is 80-60=20 mph...
 Step 3: 60/20 = 3 hours.
 Answer: 7pm"
```

---

### Structured Output (JSON Mode)

Forcing the model to return data in a specific structured format (JSON, Pydantic, etc.) rather than free-form text.

**Why it matters:**
- Makes LLM output **machine-parseable** — feed directly into downstream code
- Eliminates brittle regex parsing of natural language
- Modern models support this natively via `response_format={"type": "json_object"}` or function calling

**Used in:** [02_hello_world/06_structured_output.py](README.md#02--hello-world-prompting-techniques), [05_weather_agent](README.md#05--weather-agent) (function calling for tools)

---

### Persona-Based Prompting

Giving the model a **specific identity** — role, expertise, or personality — to influence its tone and style.

**Why it matters:**
- Same question, different personas → different answers
- *"As a senior engineer..."* vs *"As a beginner tutor..."* changes the level of explanation
- Useful for products with specific brand voice

**Used in:** [02_hello_world/08_persona_based_prompt.py](README.md#02--hello-world-prompting-techniques)

---

### Alpaca-Style Instruction Format

A specific prompt format with three sections: `### Instruction`, `### Input`, `### Response`. Originated from the Stanford Alpaca project (instruction-tuned LLaMA).

**Why it matters:**
- Many open-source models (LLaMA, Mistral, Gemma) are fine-tuned on this exact format
- Using it correctly often improves their output quality significantly
- Different from OpenAI's chat format — important when using HuggingFace models

**Used in:** [02_hello_world/09_alpaca_prompt.py](README.md#02--hello-world-prompting-techniques)

---

## 3. AI Agents

### What is an AI Agent

An **agent** is an LLM-driven program that can take actions in the real world by calling tools (APIs, functions, databases). Unlike a chatbot that just responds, an agent **decides what to do next** based on context.

**Loop pattern:**
```
1. User gives a goal
2. LLM thinks about which tool to use
3. LLM calls the tool (with arguments)
4. Tool returns a result
5. LLM evaluates: done? or call another tool?
6. Repeat 2-5 until the goal is met
7. LLM gives the final answer
```

**Why it matters:**
- Pure LLMs can only answer from training data — agents can fetch live data, write files, send emails, etc.
- Foundation for assistants like ChatGPT with web browsing, Cursor, Claude Code
- Combine reasoning (LLM) with action (tools)

**Used in:** [05_weather_agent](README.md#05--weather-agent), [06_cli_agent](README.md#06--cli-coding-agent), [10_langgraph](README.md#10--langgraph)

---

### Tool / Function Calling

The mechanism by which an LLM tells your code *"call this function with these arguments"*. The LLM doesn't actually execute the function — your code does, then feeds the result back to the LLM.

**How it works:**
1. You give the LLM a schema describing available tools (name, parameters, what they do)
2. LLM decides to use one — returns a structured `tool_call` with arguments
3. Your code executes the actual function
4. You send the result back to the LLM as a `tool` message
5. LLM uses the result to compose its next move

**Why it matters:**
- This is how agents "do things" — the LLM is the brain, tools are the hands
- Schema-driven so the LLM knows what's available without hardcoding logic
- Modern models support parallel tool calls (call N tools at once)

**Used in:** [05_weather_agent](README.md#05--weather-agent), [06_cli_agent](README.md#06--cli-coding-agent)

**Example schema:**
```python
{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
            },
            "required": ["latitude", "longitude"],
        },
    },
}
```

---

### Streaming Responses

Receiving the LLM's output **as it's generated**, token by token, instead of waiting for the entire response.

**Why it matters:**
- Drastically better UX — users see text appearing immediately instead of staring at a spinner for 10 seconds
- Lets you display chain-of-thought reasoning in real-time
- Slightly more complex code (handle deltas, accumulate state)

**Used in:** [05_weather_agent](README.md#05--weather-agent), [06_cli_agent](README.md#06--cli-coding-agent)

---

## 4. RAG (Retrieval Augmented Generation)

### What is RAG

A pattern where you:
1. **Retrieve** relevant information from a knowledge source (vector DB, search engine)
2. **Augment** the LLM's prompt with that information
3. **Generate** an answer grounded in the retrieved content

**Why it matters:**
- LLMs only know what they were trained on — RAG lets them answer questions about your private/recent data
- Reduces hallucinations because answers are based on real retrieved text
- Far cheaper than fine-tuning when you just need the model to know "your" facts
- Citations become possible — you can point to which document the answer came from

**Used in:** [07_RAG](README.md#07--rag-retrieval-augmented-generation), [08_RAG_queue](README.md#08--rag-with-redis-queue)

---

### Document Loaders

Modules that read raw documents (PDF, web pages, CSV, etc.) and convert them into a standardized format — usually a list of `Document` objects with `page_content` and `metadata` fields.

**Why it matters:**
- Different file types have different parsing quirks — loaders handle them uniformly
- Metadata (page number, source URL, author) is preserved through the pipeline
- Lets you swap "load from PDF" for "load from web" without rewriting downstream code

**Used in:** [07_RAG](README.md#07--rag-retrieval-augmented-generation), [08_RAG_queue](README.md#08--rag-with-redis-queue) — both use `PyPDFLoader`

**Example:**
```python
from langchain_community.document_loaders import PyPDFLoader
pages = PyPDFLoader("guide.pdf").load()
# pages[0].page_content → "..."
# pages[0].metadata → {"source": "guide.pdf", "page": 0}
```

---

### Chunking (Text Splitting)

Breaking large documents into smaller pieces (**chunks**) so each piece fits in the LLM's context window and embedding model's input limit.

**Key parameters:**
- **`chunk_size`** — max characters/tokens per chunk
- **`chunk_overlap`** — characters shared between consecutive chunks (preserves context across boundaries)
- **`separators`** — preferred split points (paragraph breaks > sentences > spaces > characters)

**Why it matters:**
- Too-large chunks waste tokens with irrelevant content
- Too-small chunks lose context — a sentence might be split across chunks
- Overlap prevents losing context when a key answer spans a chunk boundary

**Used in:** [07_RAG](README.md#07--rag-retrieval-augmented-generation), [08_RAG_queue](README.md#08--rag-with-redis-queue) (both use `chunk_size=1500, chunk_overlap=200`)

**Recursive vs other strategies:**
- `RecursiveCharacterTextSplitter` — tries to split at paragraph breaks first, falls back to sentences, then spaces
- `MarkdownHeaderTextSplitter` — splits at `#` headers
- `SemanticChunker` — splits where embedding similarity drops (newer, smarter)

---

### Embedding Models

Models specifically designed to convert text → vectors. Smaller and faster than chat models because they only output vectors, not text.

**Common embedding models:**
| Model | Provider | Dimensions | Notes |
|---|---|---|---|
| `text-embedding-3-small` | OpenAI | 1536 | Cheap, fast, good baseline |
| `text-embedding-3-large` | OpenAI | 3072 | Better quality, more expensive |
| `all-MiniLM-L6-v2` | HuggingFace | 384 | Free, runs locally |
| `bge-base-en-v1.5` | BAAI | 768 | Strong open-source choice |

**Why it matters:**
- Choosing an embedding model determines retrieval quality
- The **same** model must be used for indexing and querying — otherwise vectors live in different "spaces"
- Higher dimensions = more nuance but slower search

**Used in:** [07_RAG](README.md#07--rag-retrieval-augmented-generation), [08_RAG_queue](README.md#08--rag-with-redis-queue), [11_memory_agent](README.md#11--memory-agent-mem0) — all use `text-embedding-3-small`.

---

### Vector Databases

Databases specialized for storing and searching high-dimensional vectors. Optimized for similarity search rather than exact matches.

**Examples:**
| Vector DB | Notes |
|---|---|
| **Qdrant** | Open source, used in this project |
| **Pinecone** | Managed SaaS |
| **Chroma** | Lightweight, embedded |
| **Weaviate** | Open source with GraphQL |
| **PGVector** | PostgreSQL extension |

**Why it matters:**
- Regular databases (Postgres, MongoDB) can't efficiently find "the 5 closest vectors to this query vector" — vector DBs use specialized indexes (HNSW, IVF) for sub-millisecond search even with millions of vectors

**Used in:** [07_RAG](README.md#07--rag-retrieval-augmented-generation), [08_RAG_queue](README.md#08--rag-with-redis-queue), [11_memory_agent](README.md#11--memory-agent-mem0) — all use Qdrant.

---

### Similarity Search & Relevance Scores

The operation of finding the K most similar vectors to a query vector. Usually measured by **cosine similarity** — how aligned two vectors are in direction.

**Scoring:**
- `1.0` — perfect match (identical direction)
- `0.0` — orthogonal (unrelated)
- `-1.0` — opposite direction

**Why it matters:**
- Threshold filtering: drop results below `0.3` to skip noise
- Top-K selection: `k=8` retrieves 8 nearest chunks
- Score gives a quality signal — low scores mean the question doesn't have a good answer in the index

**Used in:** [07_RAG](README.md#07--rag-retrieval-augmented-generation) (basic), [08_RAG_queue/worker.py](README.md#08--rag-with-redis-queue) (with score filtering)

---

### Retrieval → Generation Pipeline

The complete RAG flow as implemented in these projects:

```
1. User question
       ↓
2. Embed the question (text-embedding-3-small)
       ↓
3. Similarity search in vector DB (top-K)
       ↓
4. Filter chunks by relevance score
       ↓
5. Format chunks with metadata as context
       ↓
6. Build prompt:  [system: "Use this context..."]
                  [context: {chunk 1} {chunk 2} ...]
                  [user: original question]
       ↓
7. Call LLM (gpt-4o or gpt-4o-mini)
       ↓
8. Return answer (with citations)
```

**Used in:** [07_RAG/query.py](README.md#07--rag-retrieval-augmented-generation), [08_RAG_queue/queues/worker.py](README.md#08--rag-with-redis-queue)

---

## 5. LangChain Ecosystem

### What LangChain Is

LangChain is a Python (and JS) framework that provides **building blocks for LLM applications** — standardized interfaces for LLMs, vector stores, document loaders, prompts, output parsers, memory, tools, etc.

**Core value:**
- Swap providers with one line: `OpenAIEmbeddings()` → `HuggingFaceEmbeddings()` and your code keeps working
- Pre-built integrations for hundreds of services (databases, APIs, file types)
- Composable: chain components together into pipelines

**Used in:** [07_RAG](README.md#07--rag-retrieval-augmented-generation), [08_RAG_queue](README.md#08--rag-with-redis-queue), [10_langgraph](README.md#10--langgraph), [11_memory_agent](README.md#11--memory-agent-mem0)

---

### LangChain vs Direct API Use

When you `from openai import OpenAI` and call it directly, you're skipping LangChain. That's **fine for simple apps** but you lose:
- Easy provider swapping
- Pre-built loaders/splitters/vector store wrappers
- Memory abstractions
- Tracing and observability (LangSmith)

These projects mix both: simple scripts (`02_hello_world`, `05_weather_agent`, `09_multimodal_ai`) use the OpenAI SDK directly; RAG/agent projects use LangChain for the heavy lifting.

---

### LangChain Package Family

LangChain isn't a single package — it's a family:

| Package | What it provides |
|---|---|
| `langchain-core` | Base abstractions (Document, Message types) |
| `langchain-community` | Loaders, splitters, integrations with other libraries |
| `langchain-openai` | OpenAI-specific wrappers (`ChatOpenAI`, `OpenAIEmbeddings`) |
| `langchain-qdrant` | Qdrant vector store integration |
| `langchain-text-splitters` | Chunking strategies |
| `langgraph` | Graph-based orchestration (see [Section 6](#6-langgraph)) |
| `langchain-classic` | Legacy/compat re-exports for older code |

**Why split into many packages:**
- Smaller installs — you don't pull in Pinecone deps if you only use Qdrant
- Independent versioning — community integrations can update faster than core
- Clearer ownership

---

### LangChain vs LangGraph

| | LangChain | LangGraph |
|---|---|---|
| **Best for** | Fixed pipelines (load → embed → search → answer) | Branching, looping, stateful workflows |
| **Control flow** | Linear chains | Graphs with conditional edges |
| **State** | Implicit / per-call | Explicit, typed, persistent |
| **Examples** | Plain RAG, ETL, batch processing | Agents, multi-step reasoning, chatbots with memory |

**Used in:** LangChain throughout the RAG projects; LangGraph in [10_langgraph](README.md#10--langgraph).

---

### Who Built LangChain

Created by **Harrison Chase** in October 2022 as a side project. Became LangChain Inc. in early 2023 with Sequoia/Benchmark backing. **Fully open source under MIT license**. They monetize through LangSmith (observability platform) and LangGraph Cloud (managed hosting).

---

## 6. LangGraph

### What LangGraph Is

LangGraph is a Python library for building **agents and stateful workflows as graphs** instead of linear chains. Built by the LangChain team but a separate package.

**Core idea:** model your LLM application as a graph of nodes connected by edges, where the next node can be chosen dynamically based on state.

**Used in:** [10_langgraph](README.md#10--langgraph) (all 4 files).

---

### StateGraph

The main builder class. Takes a schema describing the shape of data flowing through the graph, then you add nodes and edges to it.

```python
from langgraph.graph import StateGraph
graph_builder = StateGraph(MyState)
```

**Used in:** all [10_langgraph](README.md#10--langgraph) files.

---

### State (TypedDict)

A `TypedDict` defining the shape of data that flows through every node. Each node receives state, modifies it, and returns it.

```python
from typing_extensions import TypedDict

class State(TypedDict):
    messages: list
    user_query: str
    is_good: bool
```

**Why it matters:**
- Typed state catches errors early (typos in keys)
- Acts as a "shared notebook" all nodes can read/write
- Determines what gets persisted by checkpointers

---

### Annotated + Reducers (add_messages)

By default, when nodes update state, LangGraph **overwrites** the value. To accumulate (e.g., chat history), use `Annotated` with a reducer function.

```python
from typing import Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
```

Now when nodes return `{"messages": [new_msg]}`, the new message is **appended** to the existing list instead of replacing it.

**Common reducers:**
- `add_messages` — smart appender for chat (handles dedup by ID, converts types)
- `operator.add` — concatenates lists, sums numbers
- `operator.or_` — unions sets

**Used in:** [10_langgraph/main.py](README.md#10--langgraph), [chat_checkpoint.py](README.md#10--langgraph), [multi_user_chat.py](README.md#10--langgraph)

---

### Nodes

Functions registered in the graph. Each one takes state, modifies it, returns it.

```python
def chatbot(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

graph_builder.add_node("chatbot", chatbot)
```

The first arg to `add_node` is a **label** — used in edges to reference this node.

---

### Edges

Connections between nodes that define the flow.

```python
graph_builder.add_edge(START, "chatbot")    # entry
graph_builder.add_edge("chatbot", END)       # exit
```

`START` and `END` are built-in constants marking the entry and exit points.

---

### Conditional Edges

The key power of LangGraph. After a node runs, call a router function to decide which node comes next based on state.

```python
def route(state: State) -> str:
    return "endnode" if state["is_good"] else "fallback_node"

graph_builder.add_conditional_edges("evaluator", route)
```

The router returns a string that matches another node's label.

**Used in:** [10_langgraph/conditional.py](README.md#10--langgraph) — LLM-as-judge pattern.

---

### Compile vs Invoke

| Step | What it does | When |
|---|---|---|
| `graph.compile(...)` | Validates the graph, freezes it into a runnable program | **Once**, at startup |
| `graph.invoke(initial_state)` | Actually runs the graph with input | **Many** times, per query |

`compile()` is analogous to building an executable; `invoke()` is running it.

A compiled graph also exposes `.stream()`, `.ainvoke()`, and `.astream()` for streaming and async use.

---

### Checkpointers

Mechanism that **persists graph state** at every step to a backend (memory, SQLite, MongoDB, Redis).

**Why it matters:**
- Conversation memory across runs
- Resume interrupted workflows from the last successful step
- Time-travel debugging — replay from any past checkpoint
- Human-in-the-loop — pause, wait for approval, resume

**Backends:**
- `MemorySaver` — in-process dict, for dev
- `SqliteSaver` — file-based, simple persistence
- `MongoDBSaver` — production-grade, used here

**Used in:** [10_langgraph/chat_checkpoint.py](README.md#10--langgraph), [multi_user_chat.py](README.md#10--langgraph)

---

### thread_id

The **unique key** that identifies which checkpoint to load when invoking the graph. Passed via `config`.

```python
config = {"configurable": {"thread_id": "alice"}}
graph.invoke({"messages": [msg]}, config)
```

**Why it matters:**
- One graph + one checkpointer + per-user `thread_id` = multi-user chat with isolated, persistent memory
- Same `thread_id` → continues the same conversation
- Different `thread_id` → fresh start, isolated history

**Used in:** [10_langgraph/multi_user_chat.py](README.md#10--langgraph) — demonstrates user switching.

---

### Multi-Agent Systems

A pattern where multiple specialized agents collaborate, each represented as a node in the graph. Example: a `planner` agent decides what to do, then dispatches to `researcher`, `writer`, or `critic` agents.

LangGraph is the natural way to wire this — the graph structure encodes the collaboration logic.

**Used in:** not directly in these projects, but [10_langgraph/conditional.py](README.md#10--langgraph) shows the foundational idea — multiple LLM nodes (OpenAI + Gemini) collaborating with conditional routing.

---

## 7. Memory

### Why LLMs Are Stateless

By default, LLM API calls have **no memory** of previous calls. Each request is independent. If you want a chatbot to remember earlier messages, **you** have to pass the chat history with every request.

**Why it matters:**
- Naive approach: send the entire conversation history every time → cost grows linearly with conversation length
- Solutions:
  - **Checkpointing** (raw history persistence)
  - **Memory layers** (fact extraction)
  - **Summarization** (compress old turns)

---

### Checkpointing vs Fact-Based Memory

Two fundamentally different approaches:

| Aspect | Checkpointing (LangGraph) | Fact-Based (mem0) |
|---|---|---|
| **What's stored** | Full message history | Extracted facts only |
| **Storage growth** | Linear (every turn adds messages) | Logarithmic (facts deduped/merged) |
| **Retrieval** | Loads everything by `thread_id` | Vector-search relevant facts |
| **Best for** | Resumable workflows, replay, audit | Long-term personalization |
| **Token cost at scale** | High (full history every call) | Low (only relevant facts) |
| **Backend** | MongoDB, SQLite, etc. | Vector DB (Qdrant) |

**Analogy:**
- Checkpointing = a video recording of every conversation
- mem0 = your therapist's notebook of takeaways

**Used in:** [10_langgraph](README.md#10--langgraph) (checkpointing), [11_memory_agent](README.md#11--memory-agent-mem0) (mem0).

---

### mem0

An open-source memory layer for AI agents. Extracts facts from conversations using an LLM, embeds them with an embedding model, and stores them in a vector database for retrieval.

**Flow per turn:**
1. **Search** — `mem_client.search(query, user_id=...)` retrieves relevant past facts via vector similarity
2. **Inject** — facts go into the system prompt as context
3. **Generate** — LLM responds with full awareness of remembered facts
4. **Extract** — `mem_client.add(messages, user_id=...)` runs an LLM over the new exchange to extract any new facts and store them

**Why it matters:**
- Scales to long-term personalization without bloating context windows
- Powers ChatGPT's "memory" feature, personal AI assistants, customer support history

**Used in:** [11_memory_agent](README.md#11--memory-agent-mem0).

---

### User Isolation Patterns

When building a multi-user system, you need separate memory per user. Standard pattern: use the user's authenticated ID as the scoping key.

**LangGraph:**
```python
config = {"configurable": {"thread_id": user_id}}
```

**mem0:**
```python
mem_client.search(query=q, filters={"user_id": user_id})
mem_client.add(messages=[...], user_id=user_id)
```

For multiple conversations per user (like ChatGPT's sidebar), use **compound keys**:
```python
thread_id = f"{user_id}__{chat_session_id}"
```

**Used in:** [10_langgraph/multi_user_chat.py](README.md#10--langgraph).

---

## 8. Production Patterns

### Why Use a Job Queue

Synchronous LLM calls (RAG with 5-10 second latency) don't scale:
- HTTP request hangs the entire time
- Many concurrent users exhaust the server's connection pool
- A traffic spike crashes everything
- No way to retry failed jobs gracefully

A **queue** decouples the API server from the heavy work:
- API server enqueues a job and returns a `job_id` instantly (~50ms)
- Background workers pull jobs at their own pace
- Failures go to a retry queue
- You can scale workers independently from the API

**Used in:** [08_RAG_queue](README.md#08--rag-with-redis-queue).

---

### Redis / Valkey

**Redis** is an in-memory key-value database. Used here as both a job queue and a result store.

**Valkey** is an open-source fork of Redis created in 2024 after Redis changed its license to a non-open one. The Linux Foundation backs Valkey. It's **100% protocol-compatible** with Redis — all Redis clients work unchanged.

**Why it matters:**
- Fast (in-memory)
- Rich data types (lists, hashes, sets, sorted sets, streams)
- Pub/sub for real-time messaging
- Used industry-wide for caching, queues, sessions, rate limiting

**Used in:** [08_RAG_queue](README.md#08--rag-with-redis-queue) — Valkey serves both queue and result store.

---

### RQ (Redis Queue)

A Python library that implements a simple, Redis-backed job queue. Workers run as separate processes that watch the queue and execute jobs.

**Key components:**
- **Queue** — Redis list holding pending jobs (`q.enqueue(func, args)`)
- **Worker** — process that pops jobs and runs them (`rq worker`)
- **Job** — represents one task, has a status (`queued → started → finished`), arguments, result

**Why it matters:**
- Dead simple to use compared to alternatives (Celery, Dramatiq)
- Built-in dashboard for monitoring (`rq-dashboard`)
- Retries, scheduling, timeouts all built in

**Used in:** [08_RAG_queue/queues/worker.py](README.md#08--rag-with-redis-queue).

---

### Workers and Scaling

Workers are separate processes that watch the queue. To scale throughput, run more workers.

**Single worker:**
```bash
rq worker
```

**Multiple workers (parallel processing):**
```bash
for i in {1..4}; do rq worker & done    # Mac/Linux
```

Each worker can process one job at a time. 4 workers = 4 jobs processed concurrently.

**Used in:** [08_RAG_queue](README.md#08--rag-with-redis-queue).

---

### Async APIs (FastAPI)

**FastAPI** is a modern Python web framework. Used here to expose the RAG pipeline as HTTP endpoints.

**Key features used:**
- Auto-generated OpenAPI/Swagger UI (`/docs`)
- Pydantic models for request validation
- CORS middleware to allow cross-origin requests from the React frontend

**Why it matters:**
- Async by default — handles thousands of concurrent connections efficiently
- Type hints become validation + docs automatically

**Used in:** [03_ollama_fastapi](README.md#03--ollama--fastapi), [08_RAG_queue/queues/server.py](README.md#08--rag-with-redis-queue).

---

### CORS (Cross-Origin Resource Sharing)

A browser security mechanism. By default, browsers block JavaScript on `http://localhost:5173` from making requests to `http://localhost:8000` because they're "different origins" (different ports count).

**CORS middleware** adds response headers like `Access-Control-Allow-Origin: http://localhost:5173` that tell the browser "yes, this cross-origin request is OK".

**Why it matters:**
- Without it, your React frontend can't talk to your FastAPI backend
- One of the most common production headaches when wiring frontends to backends

**Used in:** [08_RAG_queue/queues/server.py](README.md#08--rag-with-redis-queue).

---

### Pydantic Models

Pydantic provides **runtime type validation** for Python data. FastAPI uses Pydantic models as request/response schemas.

```python
class QueryRequest(BaseModel):
    query: str

@app.post("/query")
def enqueue_query(request: QueryRequest):
    ...
```

**Why it matters:**
- Automatic validation: if the request body is missing `query`, FastAPI returns a 422 error without your code running
- Auto-generated docs at `/docs`
- Type safety in your code

**Used in:** [08_RAG_queue/queues/server.py](README.md#08--rag-with-redis-queue).

---

### Observability Tools

UIs for monitoring what's happening inside your infrastructure:

| Tool | What it shows | Port |
|---|---|---|
| **RQ Dashboard** | Job queue status (queued, active, failed) | 9181 |
| **Redis Insight** | All Redis/Valkey keys, values, memory usage | 5540 |
| **Mongo Express** | MongoDB databases, collections, documents | 8081 |
| **Qdrant Dashboard** | Collections, vector counts, search testing | 6333/dashboard |
| **FastAPI /docs** | Auto-generated Swagger UI | 8000/docs |

**Why it matters:**
- Debugging production issues requires seeing what's actually happening
- During dev: see jobs flow through the queue, confirm vectors are stored, etc.

**Used in:** [08_RAG_queue](README.md#08--rag-with-redis-queue) (RQ Dashboard + Redis Insight + Qdrant), [10_langgraph](README.md#10--langgraph) (Mongo Express), [03_ollama_fastapi](README.md#03--ollama--fastapi) (Swagger UI).

---

## 9. Databases & Drivers

### Native Database Protocols vs HTTP

Most databases use **custom binary protocols** for performance, not HTTP. That's why you can't browse `localhost:27017` (MongoDB) or `localhost:6379` (Redis) in a browser — the browser sends HTTP, the DB expects binary frames.

| Database | Port | Protocol | Browseable? |
|---|---|---|---|
| MongoDB | 27017 | MongoDB Wire Protocol (binary, BSON) | ❌ |
| Redis / Valkey | 6379 | RESP (text-based) | ❌ |
| PostgreSQL | 5432 | PG Frontend/Backend Protocol (binary) | ❌ |
| Qdrant | 6333 | gRPC + REST | ✅ (REST API exposed) |

To browse non-HTTP databases, use a **web-based admin tool** (Mongo Express, Redis Insight) that translates between HTTP and the native protocol.

---

### MongoDB Wire Protocol

MongoDB's binary protocol built on TCP. Messages have a 16-byte header (length, op code, request ID) wrapping a BSON payload.

**Why it matters:**
- Understanding this explains why `pymongo` exists — to bridge Python objects to binary bytes
- Helps when debugging connection issues
- Performance: binary protocols are faster than HTTP for high-frequency DB operations

---

### BSON (Binary JSON)

MongoDB's data format. Same conceptual model as JSON but stored as binary bytes — faster to parse and supports more types (dates, binary blobs, ObjectId).

```
JSON:  {"name": "Jayanth"}
BSON:  20 00 00 00 02 6E 61 6D 65 00 08 00 00 00 4A 61 79 61 6E 74 68 00 00
```

**Why it matters:**
- Why MongoDB queries are fast even on large datasets
- Lets MongoDB store binary data (images, files) natively

---

### PyMongo

Python's official MongoDB driver. Translates Python dicts to BSON, wraps them in Wire Protocol messages, and handles the TCP communication with MongoDB.

```python
from pymongo import MongoClient
client = MongoClient("mongodb://admin:admin@localhost:27017/")
client["mydb"]["users"].insert_one({"name": "Jayanth"})
```

**Why it matters:**
- Without PyMongo (or another driver), you'd have to implement the entire binary protocol yourself
- LangGraph's `MongoDBSaver` uses PyMongo under the hood

**Used in:** [10_langgraph/chat_checkpoint.py](README.md#10--langgraph), [multi_user_chat.py](README.md#10--langgraph) (via `MongoDBSaver`).

---

### MongoDB

A document-oriented NoSQL database. Stores JSON-like documents (BSON internally) instead of rows in tables. Flexible schema — different documents in the same collection can have different fields.

**Used in this project as:**
- Backend for LangGraph checkpointer (stores conversation state)

**Used in:** [10_langgraph](README.md#10--langgraph).

---

### Qdrant

An open-source vector database written in Rust. Specialized for storing embeddings and performing fast similarity search.

**Why it matters:**
- Production-ready vector search at millions-of-vectors scale
- Built-in REST API and a web dashboard at `:6333/dashboard`
- Supports filtering, payload metadata, multiple distance metrics

**Used in:** [07_RAG](README.md#07--rag-retrieval-augmented-generation), [08_RAG_queue](README.md#08--rag-with-redis-queue), [11_memory_agent](README.md#11--memory-agent-mem0).

---

### Mongo Express

A web-based GUI for MongoDB. Connects to MongoDB over the Wire Protocol, exposes an HTTP UI on a separate port (8081) that you can browse to inspect data.

**Used in:** [10_langgraph](README.md#10--langgraph).

---

### Redis Insight

A web-based GUI for Redis/Valkey. Same idea as Mongo Express but for Redis.

**Used in:** [08_RAG_queue](README.md#08--rag-with-redis-queue).

---

## 10. Multimodal

### Vision in Chat Completions

Modern OpenAI models (`gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`) accept images as inputs alongside text. The API uses content blocks with mixed types.

```python
messages=[
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this image."},
            {"type": "image_url", "image_url": {"url": "https://..."}}
        ]
    }
]
```

**Why it matters:**
- One model handles text + images instead of needing separate OCR/vision pipelines
- Unlocks use cases: captioning, document analysis, accessibility, content moderation

**Used in:** [09_multimodal_ai](README.md#09--multimodal-ai).

---

### Image URL vs Base64

You can send images two ways:

| Method | Use when |
|---|---|
| **URL** | Image is publicly accessible (CDN, Wikipedia, etc.) |
| **Base64** | Image is local/private; encode to a `data:image/jpeg;base64,...` string |

URL is simpler when possible. Base64 is needed for user uploads or sensitive content.

**Used in:** [09_multimodal_ai](README.md#09--multimodal-ai) uses URL.

---

## 11. Infrastructure

### Docker Fundamentals

**Docker** runs applications in isolated containers — like lightweight VMs but sharing the host OS kernel.

**Key concepts:**
- **Image** — a snapshot template (e.g. `mongo:latest`)
- **Container** — a running instance of an image
- **Volume** — persistent storage outside the container's filesystem
- **Port mapping** — exposes a container port to the host (`6379:6379` = host:container)

**Why it matters:**
- Each project's infrastructure (Qdrant, Mongo, Redis) runs in its own container
- No need to install services system-wide — just `docker compose up`
- Easy cleanup: `docker compose down` removes everything

**Used in:** [07_RAG](README.md#07--rag-retrieval-augmented-generation), [08_RAG_queue](README.md#08--rag-with-redis-queue), [10_langgraph](README.md#10--langgraph), [11_memory_agent](README.md#11--memory-agent-mem0).

---

### docker-compose

A YAML config file (`docker-compose.yml`) that declares multiple containers and their config in one place. Run all of them with `docker compose up -d`.

```yaml
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
  valkey:
    image: valkey/valkey:latest
    ports:
      - "6379:6379"
```

**Why it matters:**
- Reproducible infrastructure across machines
- Easy to add monitoring sidecars (Mongo Express, Redis Insight)
- One command to start/stop the whole stack

---

### Volumes (Persistence)

By default, when you delete a container, its data is **gone**. Volumes are filesystem-backed storage that survives container deletion.

```yaml
services:
  mongodb:
    image: mongo:latest
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

**Why it matters:**
- Without volumes, you lose embeddings/checkpoints every time you `docker compose down`
- With volumes, you can rebuild containers without losing data
- The `07_RAG` project intentionally **doesn't** use volumes — but `10_langgraph` does

---

### Port Mapping

The `ports: "6379:6379"` syntax maps `host_port:container_port`. Multiple containers can run if they map to different host ports.

**Why it matters:**
- Port conflicts: if two projects both want port 6379, only one can run at a time
- See the [Port Reference](README.md#port-reference) table in the README

---

### Networking Between Containers

When containers run in the same Docker network (which `docker-compose` creates automatically), they can reach each other by **container name** instead of `localhost`.

Example: Redis Insight connecting to Valkey uses host `valkey`, not `localhost`:
```
Redis Insight container → host: "valkey" → Valkey container
```

But your Python code on the **host machine** uses `localhost:6379` because Docker port-maps it.

**Why it matters:**
- Common confusion source: same DB, different connection strings depending on whether you're inside or outside Docker

---

## Cross-Reference: Concepts by Project

For quick lookup — which concepts each project introduces:

| Project | New concepts introduced |
|---|---|
| [01_Tokenization](README.md#01--tokenization) | [Tokens](#tokens--tokenization) |
| [02_hello_world](README.md#02--hello-world-prompting-techniques) | [System prompts](#system-prompt), [Zero/few-shot](#zero-shot-one-shot-few-shot-prompting), [CoT](#chain-of-thought-cot), [Structured output](#structured-output-json-mode), [Personas](#persona-based-prompting), [Alpaca](#alpaca-style-instruction-format) |
| [03_ollama_fastapi](README.md#03--ollama--fastapi) | [Ollama](#model-providers), [FastAPI](#async-apis-fastapi), local model serving |
| [04_huggingface](README.md#04--huggingface) | [HuggingFace](#model-providers), `transformers` library |
| [05_weather_agent](README.md#05--weather-agent) | [Agents](#what-is-an-ai-agent), [Tool calling](#tool--function-calling), [Streaming](#streaming-responses) |
| [06_cli_agent](README.md#06--cli-coding-agent) | Same agent pattern as 05, applied to filesystem tools |
| [07_RAG](README.md#07--rag-retrieval-augmented-generation) | [Embeddings](#embeddings--vector-space), [Chunking](#chunking-text-splitting), [Vector DB](#vector-databases), [Similarity search](#similarity-search--relevance-scores), [LangChain](#what-langchain-is) |
| [08_RAG_queue](README.md#08--rag-with-redis-queue) | [Job queues](#why-use-a-job-queue), [Redis/Valkey](#redis--valkey), [RQ](#rq-redis-queue), [Workers](#workers-and-scaling), [CORS](#cors-cross-origin-resource-sharing), [Pydantic](#pydantic-models), production patterns |
| [09_multimodal_ai](README.md#09--multimodal-ai) | [Vision in chat](#vision-in-chat-completions), [Image URL vs base64](#image-url-vs-base64) |
| [10_langgraph](README.md#10--langgraph) | [LangGraph](#what-langgraph-is), [StateGraph](#stategraph), [State](#state-typeddict), [Reducers](#annotated--reducers-add_messages), [Conditional edges](#conditional-edges), [Checkpointing](#checkpointers), [thread_id](#thread_id), [MongoDB](#mongodb) |
| [11_memory_agent](README.md#11--memory-agent-mem0) | [mem0](#mem0), [Fact-based memory](#checkpointing-vs-fact-based-memory), [User isolation](#user-isolation-patterns) |

---

## Further Reading

- **LangChain docs:** https://python.langchain.com/docs/
- **LangGraph docs:** https://langchain-ai.github.io/langgraph/
- **mem0 docs:** https://docs.mem0.ai/
- **OpenAI docs:** https://platform.openai.com/docs/
- **Qdrant docs:** https://qdrant.tech/documentation/
- **RQ docs:** https://python-rq.org/
- **FastAPI docs:** https://fastapi.tiangolo.com/
- **MongoDB docs:** https://www.mongodb.com/docs/

---

*Last updated alongside the projects. If a concept here doesn't match the code, prefer the code as the source of truth.*
