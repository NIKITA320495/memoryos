# tests/test_tools.py
import pytest
import json
import os
import shutil
from unittest.mock import patch, MagicMock

TEST_DB_PATH = "/tmp/memoryos_tools_test_db"

@pytest.fixture(autouse=True)
def clean_db(monkeypatch):
    if os.path.exists(TEST_DB_PATH):
        shutil.rmtree(TEST_DB_PATH)
    monkeypatch.setenv("MEMORY_DB_PATH", TEST_DB_PATH)
    monkeypatch.setenv("COLLECTION_NAME", "tools_test_collection")
    yield
    if os.path.exists(TEST_DB_PATH):
        shutil.rmtree(TEST_DB_PATH)

# reimport tools after env is patched
@pytest.fixture
def tools():
    import importlib
    import src.tools as t
    importlib.reload(t)
    return t

# ── store_memory ───────────────────────────────────────────────────────────────

def test_store_memory_success(tools):
    result = json.loads(tools.tool_store_memory(
        text="I prefer Python over JavaScript",
        user_id="nikita_001",
        tags=["preferences"],
        importance=8
    ))
    assert result["status"] == "stored"
    assert "id" in result
    assert result["text"] == "I prefer Python over JavaScript"

def test_store_memory_default_importance(tools):
    result = json.loads(tools.tool_store_memory(
        text="Some memory", user_id="nikita_001"
    ))
    assert result["importance"] == 5

# ── search_memory ──────────────────────────────────────────────────────────────

def test_search_memory_finds_stored(tools):
    tools.tool_store_memory(
        text="I am building MemoryOS using MCP and ChromaDB",
        user_id="nikita_001"
    )
    result = json.loads(tools.tool_search_memory(
        query="MCP ChromaDB project",
        user_id="nikita_001"
    ))
    assert "results" in result
    assert len(result["results"]) > 0

def test_search_memory_empty(tools):
    result = json.loads(tools.tool_search_memory(
        query="anything", user_id="nikita_001"
    ))
    assert result["results"] == []
    assert "message" in result

def test_search_memory_user_isolation(tools):
    tools.tool_store_memory(
        text="Private memory for user A",
        user_id="user_a"
    )
    result = json.loads(tools.tool_search_memory(
        query="private memory", user_id="user_b"
    ))
    assert result["results"] == []

# ── get_memory ─────────────────────────────────────────────────────────────────

def test_get_memory_success(tools):
    stored = json.loads(tools.tool_store_memory(
        text="Nikita won AIR 5 Unstop Talent Award",
        user_id="nikita_001"
    ))
    fetched = json.loads(tools.tool_get_memory(stored["id"]))
    assert fetched["text"] == "Nikita won AIR 5 Unstop Talent Award"

def test_get_memory_not_found(tools):
    result = json.loads(tools.tool_get_memory("nonexistent-id"))
    assert "error" in result

# ── update_memory ──────────────────────────────────────────────────────────────

def test_update_memory_success(tools):
    stored = json.loads(tools.tool_store_memory(
        text="Old memory text",
        user_id="nikita_001"
    ))
    updated = json.loads(tools.tool_update_memory(
        memory_id=stored["id"],
        new_text="New updated memory text"
    ))
    assert updated["status"] == "updated"
    assert updated["text"] == "New updated memory text"

def test_update_memory_not_found(tools):
    result = json.loads(tools.tool_update_memory(
        memory_id="fake-id", new_text="anything"
    ))
    assert "error" in result

# ── delete_memory ──────────────────────────────────────────────────────────────

def test_delete_memory_success(tools):
    stored = json.loads(tools.tool_store_memory(
        text="Memory to delete", user_id="nikita_001"
    ))
    result = json.loads(tools.tool_delete_memory(stored["id"]))
    assert result["status"] == "deleted"

def test_delete_memory_not_found(tools):
    result = json.loads(tools.tool_delete_memory("fake-id-000"))
    assert result["status"] == "not_found"

# ── list_memories ──────────────────────────────────────────────────────────────

def test_list_memories(tools):
    tools.tool_store_memory(text="Memory 1", user_id="nikita_001")
    tools.tool_store_memory(text="Memory 2", user_id="nikita_001")
    tools.tool_store_memory(text="Other user", user_id="other_user")

    result = json.loads(tools.tool_list_memories("nikita_001"))
    assert result["count"] == 2

def test_list_memories_empty(tools):
    result = json.loads(tools.tool_list_memories("nobody"))
    assert result["count"] == 0