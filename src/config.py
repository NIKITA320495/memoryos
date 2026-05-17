# src/config.py
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).parent.parent

MEMORY_DB_PATH = os.getenv("MEMORY_DB_PATH", str(BASE_DIR / "memory_db"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "agent_memory")
EMBEDDING_MODEL  = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
IMPORTANCE_DEFAULT = int(os.getenv("IMPORTANCE_DEFAULT", "5"))