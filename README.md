<div align="center">

# 🧠 MemoryOS

### Persistent Memory Infrastructure for LLM Agents

*Give any AI agent long-term memory — across sessions, forever.*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-Protocol-7C6AF7?style=flat-square)](https://modelcontextprotocol.io)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-4FD1C7?style=flat-square)](https://chromadb.com)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?style=flat-square)](https://ollama.ai)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[Demo](#demo) · [Features](#features) · [Architecture](#architecture) · [Quickstart](#quickstart) · [MCP Tools](#mcp-tools) · [Contributing](#contributing)

---

![MemoryOS Demo](assets/demo.gif)

> *Watch the agent recall user context across two completely separate conversations — no chat history, no prompt stuffing. Pure persistent memory.*

</div>

---

## The Problem

Every LLM conversation starts from zero.

You tell your AI assistant your name, your preferences, your goals — and the moment the session ends, it forgets everything. Developers work around this by stuffing context into prompts, but that's expensive, has hard token limits, and doesn't scale.

**MemoryOS solves this at the infrastructure level.**

---

## What is MemoryOS?

MemoryOS is a **custom MCP (Model Context Protocol) server** that gives any LLM agent a persistent, semantic memory layer backed by ChromaDB. 

Connect it once. Your agent remembers everything — forever.

```
User: "My name is Nikita and I'm targeting Gen AI roles."
Agent: [stores to ChromaDB via store_memory tool]

--- new session, days later ---

User: "What do you know about me?"
Agent: [calls search_memory → retrieves from ChromaDB]
Agent: "You're Nikita, a Gen AI Engineer candidate..."
```

No prompt stuffing. No token waste. No repeated introductions.

---

## Features

- **🔌 MCP Protocol** — plug into Claude Desktop or any MCP-compatible agent in one config line
- **🔍 Semantic Search** — memories retrieved by meaning, not keywords (cosine similarity via ChromaDB)
- **👤 Multi-user Isolation** — strict user_id scoping, memories never leak across users
- **⚡ Importance Scoring** — weight memories 1–10, filter by relevance
- **🏷 Tagging System** — organise memories with custom tags
- **💾 Persistent Storage** — survives server restarts, process kills, machine reboots
- **🌐 Streamlit UI** — visual dashboard for memory management and live demo
- **100% Open Source** — no OpenAI, no paid APIs, runs fully local with Ollama

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Claude Desktop / LLM Agent              │
│              (any MCP-compatible client)             │
└──────────────────────┬──────────────────────────────┘
                       │ MCP Protocol (JSON-RPC / stdio)
                       ▼
┌─────────────────────────────────────────────────────┐
│                  MemoryOS MCP Server                 │
│                                                      │
│   ┌──────────────────────────────────────────────┐  │
│   │              6 MCP Tools                     │  │
│   │  store_memory  │  search_memory              │  │
│   │  get_memory    │  update_memory              │  │
│   │  delete_memory │  list_memories              │  │
│   └─────────────────────┬────────────────────────┘  │
│                         │                            │
│   ┌─────────────────────▼────────────────────────┐  │
│   │           Memory Store Layer                 │  │
│   │     ChromaDB  ←→  sentence-transformers      │  │
│   │     (vector DB)       (embeddings)           │  │
│   └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Project Structure

```
memoryos/
├── src/
│   ├── server.py          # MCP server — tool declarations + routing
│   ├── tools.py           # 6 tool handler functions
│   ├── memory_store.py    # ChromaDB CRUD operations
│   ├── embedder.py        # sentence-transformers wrapper (singleton)
│   ├── models.py          # Pydantic data models
│   └── config.py          # Environment config
├── app.py                 # Streamlit UI
├── server.py              # Entry point
├── requirements.txt
└── .env
```

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| MCP Framework | `mcp` Python SDK | Official Anthropic protocol |
| Vector Database | `ChromaDB` | Persistent, local, fast cosine search |
| Embeddings | `all-MiniLM-L6-v2` | 384-dim, fast, high quality, free |
| Local LLM | `Ollama` + `llama3.2` | 100% local, no API costs |
| Data Validation | `Pydantic v2` | Type-safe tool inputs/outputs |
| UI | `Streamlit` | Rapid demo dashboard |

---

## Quickstart

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai) (for the chat agent)
- [Claude Desktop](https://claude.ai/download) (for MCP integration)

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/NIKITA320495/memoryos.git
cd memoryos

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env            # edit if needed
```

### Run the MCP Server

```bash
python server.py
```

You should see:
```
[Embedder] Loaded model: all-MiniLM-L6-v2
[MemoryStore] Connected to collection: agent_memory
[MemoryOS] Server starting...
```

### Run the Streamlit UI

```bash
# Start Ollama first
ollama serve
ollama pull llama3.2

# Then launch the UI
streamlit run app.py
```

Open `http://localhost:8501`


## Connect to Claude Desktop

Add this to `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "memoryos": {
      "command": "/path/to/memoryos/venv/bin/python3",
      "args": ["/path/to/memoryos/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/memoryos",
        "MEMORY_DB_PATH": "/path/to/memoryos/memory_db",
        "COLLECTION_NAME": "agent_memory",
        "EMBEDDING_MODEL": "all-MiniLM-L6-v2"
      }
    }
  }
}
```

Restart Claude Desktop. The 🔨 hammer icon confirms MemoryOS is connected.



## MCP Tools

| Tool | Description | Key Parameters |
|------|-------------|---------------|
| `store_memory` | Store a new memory with metadata | `text`, `user_id`, `tags[]`, `importance (1-10)` |
| `search_memory` | Semantic similarity search | `query`, `user_id`, `top_k` |
| `get_memory` | Fetch memory by exact ID | `memory_id` |
| `update_memory` | Re-embed and update existing memory | `memory_id`, `new_text` |
| `delete_memory` | Permanently remove a memory | `memory_id` |
| `list_memories` | List all memories for a user | `user_id` |

### Example Tool Call

```python
# store
store_memory(
    text="I prefer Python and am targeting Gen AI Engineer roles",
    user_id="nikita_001",
    tags=["career", "preferences"],
    importance=9
)
# → {"status": "stored", "id": "a3f2c1...", "text": "...", "importance": 9}

# search
search_memory(query="career goals", user_id="nikita_001", top_k=3)
# → {"results": [{"text": "...", "score": 0.91, "tags": [...]}]}
```

---

## Demo

### The Magic Moment

| Session 1 | Session 2 (fresh chat) |
|-----------|----------------------|
| *"My name is Nikita, I'm targeting Gen AI roles"* | *"What do you know about me?"* |
| Agent stores to ChromaDB | Agent retrieves from ChromaDB |
| ✅ Memory saved | ✅ *"You're Nikita, targeting Gen AI roles..."* |

### Streamlit Dashboard

- **💬 Chat tab** — memory-powered conversation with live tool call visibility
- **🗄 Memory Vault** — browse, filter, sort, delete all memories
- **➕ Store Memory** — manual entry + one-click demo presets
- **🔍 Semantic Search** — query memories with similarity scores

---


## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MEMORY_DB_PATH` | `./memory_db` | ChromaDB storage path (use absolute path) |
| `COLLECTION_NAME` | `agent_memory` | ChromaDB collection name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace embedding model |
| `MAX_SEARCH_RESULTS` | `5` | Max results per search query |
| `IMPORTANCE_DEFAULT` | `5` | Default importance score |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2` | Local LLM model name |

---

## Real-World Use Cases

- **Customer support bots** that remember each user's past issues
- **AI tutors** that track what a student has already learned
- **Personal assistants** with persistent preferences across devices
- **Enterprise agents** with organisation-wide knowledge bases
- **Developer tools** that remember your codebase context

---



## Roadmap

- [ ] Memory decay — auto-reduce importance of old memories over time
- [ ] Memory consolidation — merge duplicate/similar memories using LLM
- [ ] REST API wrapper — expose tools via FastAPI for non-MCP agents
- [ ] Memory graph — link related memories with edges
- [ ] Multi-collection support — separate memory spaces per project

---

## Author

**Nikita Babbar**
- GitHub: [@NIKITA320495](https://github.com/NIKITA320495)
- LinkedIn: [nikita-babbar-b0291026a](https://linkedin.com/in/nikita-babbar-b0291026a)

---

<div align="center">

Built with 🧠 by Nikita Babbar 

*If this project helped you, please ⭐ the repo*

</div>