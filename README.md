# MemoryOS

MemoryOS is a Python scaffold for a local, searchable memory service. The project is set up around an MCP-compatible server, ChromaDB for persistent vector storage, and sentence-transformer embeddings for semantic recall.

The current repository is an early scaffold: dependencies, configuration, folders, and test placeholders are present, while the core server and memory-store implementation files are still empty.

## Project Structure

```text
memoryos/
├── src/
│   ├── config.py          # Environment-backed configuration
│   ├── embedder.py        # Embedding model wrapper
│   ├── memory_store.py    # ChromaDB-backed memory persistence
│   ├── models.py          # Request/response data models
│   ├── server.py          # MCP/FastAPI server entry point
│   └── tools.py           # Memory tools exposed to agents
├── scripts/
│   ├── demo.py            # Demo runner
│   └── seed_memories.py   # Local memory seeding script
├── tests/
│   ├── test_embedder.py
│   ├── test_memory_store.py
│   └── test_tools.py
├── memory_db/             # Local ChromaDB persistence directory
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10+
- pip
- A local virtual environment is recommended

## Setup

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Configuration is loaded from environment variables and `.env` via `python-dotenv`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `MEMORY_DB_PATH` | `./memory_db` | Directory used for persistent ChromaDB storage |
| `COLLECTION_NAME` | `agent_memory` | ChromaDB collection name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence Transformers model name |
| `MAX_SEARCH_RESULTS` | `5` | Default number of search results |
| `IMPORTANCE_DEFAULT` | `5` | Default importance score for new memories |

Example `.env`:

```env
MEMORY_DB_PATH=./memory_db
COLLECTION_NAME=agent_memory
EMBEDDING_MODEL=all-MiniLM-L6-v2
MAX_SEARCH_RESULTS=5
IMPORTANCE_DEFAULT=5
```

## Intended Capabilities

MemoryOS is structured to support:

- Storing durable memories with metadata such as importance, source, or tags
- Generating embeddings for natural-language memory content
- Persisting vectors and metadata in ChromaDB
- Searching memories semantically
- Exposing memory operations as tools for an MCP-compatible agent
- Running local demos and seed scripts for development

## Development

Run tests with:

```bash
pytest
```

The test files are currently placeholders, so add coverage as the implementation fills in.

## Suggested Next Steps

1. Implement `src/embedder.py` as a small wrapper around `sentence-transformers`.
2. Implement `src/memory_store.py` to create/load a ChromaDB collection and support add/search/delete operations.
3. Define request and response models in `src/models.py` with Pydantic.
4. Expose memory operations in `src/tools.py`.
5. Wire the server entry point in `src/server.py`.
6. Add focused tests for embedding, persistence, search, and tool behavior.

## Notes

- `memory_db/` is reserved for local ChromaDB data.
- `.env`, generated ChromaDB files, Python caches, build output, and egg metadata are ignored by `.gitignore`.
- The root `server.py` file is currently empty; prefer using `src/server.py` as the main application entry point unless the project later needs a thin root-level launcher.
