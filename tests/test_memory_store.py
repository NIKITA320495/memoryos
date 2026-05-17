# tests/test_memory_store.py
import pytest
import os
import shutil
from src.memory_store import MemoryStore
from src.models import StoreRequest, SearchRequest

# use a temp DB so tests never touch your real memory_db
TEST_DB_PATH = "/tmp/memoryos_test_db"

@pytest.fixture(autouse=True)
def clean_db(monkeypatch):
    """wipe test DB before every test"""
    if os.path.exists(TEST_DB_PATH):
        shutil.rmtree(TEST_DB_PATH)
    monkeypatch.setenv("MEMORY_DB_PATH", TEST_DB_PATH)
    monkeypatch.setenv("COLLECTION_NAME", "test_collection")
    yield
    if os.path.exists(TEST_DB_PATH):
        shutil.rmtree(TEST_DB_PATH)

@pytest.fixture
def store():
    return MemoryStore()

@pytest.fixture
def sample_request():
    return StoreRequest(
        text="I am Nikita, targeting Generative AI Engineer roles",
        user_id="nikita_001",
        tags=["profile", "career"],
        importance=9
    )

# ── Store ──────────────────────────────────────────────────────────────────────

def test_store_returns_memory(store, sample_request):
    memory = store.store(sample_request)
    assert memory.id is not None
    assert memory.text == sample_request.text
    assert memory.user_id == "nikita_001"
    assert memory.importance == 9

def test_store_assigns_uuid(store, sample_request):
    m1 = store.store(sample_request)
    m2 = store.store(sample_request)
    assert m1.id != m2.id  # every memory gets a unique ID

def test_store_saves_tags(store, sample_request):
    memory = store.store(sample_request)
    retrieved = store.get_by_id(memory.id)
    assert retrieved.tags == ["profile", "career"]

# ── Search ─────────────────────────────────────────────────────────────────────

def test_search_returns_results(store, sample_request):
    store.store(sample_request)
    req = SearchRequest(
        query="generative AI career",
        user_id="nikita_001",
        top_k=3
    )
    results = store.search(req)
    assert len(results) > 0

def test_search_score_between_0_and_1(store, sample_request):
    store.store(sample_request)
    results = store.search(SearchRequest(
        query="AI engineer", user_id="nikita_001"
    ))
    for r in results:
        assert 0.0 <= r.score <= 1.0

def test_search_user_isolation(store):
    """user A's memories must never appear in user B's search"""
    store.store(StoreRequest(
        text="Secret info for user A",
        user_id="user_a"
    ))
    results = store.search(SearchRequest(
        query="secret info", user_id="user_b"
    ))
    assert len(results) == 0

def test_search_empty_db(store):
    results = store.search(SearchRequest(
        query="anything", user_id="nikita_001"
    ))
    assert results == []

# ── Get by ID ──────────────────────────────────────────────────────────────────

def test_get_by_id(store, sample_request):
    memory = store.store(sample_request)
    fetched = store.get_by_id(memory.id)
    assert fetched.id == memory.id
    assert fetched.text == memory.text

def test_get_by_id_not_found(store):
    result = store.get_by_id("nonexistent-uuid-1234")
    assert result is None

# ── Update ─────────────────────────────────────────────────────────────────────

def test_update_changes_text(store, sample_request):
    memory = store.store(sample_request)
    updated = store.update(memory.id, "Updated: now also knows MCP servers")
    assert updated.text == "Updated: now also knows MCP servers"

def test_update_nonexistent(store):
    result = store.update("fake-id-000", "some text")
    assert result is None

def test_updated_memory_searchable(store, sample_request):
    """after update, new text should be searchable"""
    memory = store.store(sample_request)
    store.update(memory.id, "Expert in MCP server development and ChromaDB")
    results = store.search(SearchRequest(
        query="MCP ChromaDB expert", user_id="nikita_001"
    ))
    assert len(results) > 0
    assert results[0].text == "Expert in MCP server development and ChromaDB"

# ── Delete ─────────────────────────────────────────────────────────────────────

def test_delete_memory(store, sample_request):
    memory = store.store(sample_request)
    success = store.delete(memory.id)
    assert success is True
    assert store.get_by_id(memory.id) is None

def test_delete_nonexistent(store):
    result = store.delete("fake-id-999")
    # should not crash, just return False
    assert result is False

# ── List all ───────────────────────────────────────────────────────────────────

def test_list_all(store):
    store.store(StoreRequest(text="Memory one", user_id="nikita_001"))
    store.store(StoreRequest(text="Memory two", user_id="nikita_001"))
    store.store(StoreRequest(text="Other user memory", user_id="other_user"))

    memories = store.list_all("nikita_001")
    assert len(memories) == 2
    assert all(m.user_id == "nikita_001" for m in memories)