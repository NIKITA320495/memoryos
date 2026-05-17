# src/tools.py
import json
from src.memory_store import MemoryStore
from src.models import StoreRequest, SearchRequest

store = MemoryStore()  # single shared instance across all tool calls

def tool_store_memory(
    text: str,
    user_id: str,
    tags: list[str] = [],
    importance: int = 5
) -> str:
    req = StoreRequest(
        text=text, user_id=user_id,
        tags=tags, importance=importance
    )
    memory = store.store(req)
    return json.dumps({
        "status":  "stored",
        "id":      memory.id,
        "text":    memory.text,
        "tags":    memory.tags,
        "importance": memory.importance,
        "created_at": memory.created_at,
    })

def tool_search_memory(
    query: str,
    user_id: str,
    top_k: int = 5
) -> str:
    req = SearchRequest(query=query, user_id=user_id, top_k=top_k)
    results = store.search(req)
    if not results:
        return json.dumps({"results": [], "message": "No memories found."})
    return json.dumps({
        "results": [r.model_dump() for r in results]
    })

def tool_get_memory(memory_id: str) -> str:
    memory = store.get_by_id(memory_id)
    if not memory:
        return json.dumps({"error": f"Memory {memory_id} not found."})
    return json.dumps(memory.model_dump())

def tool_update_memory(memory_id: str, new_text: str) -> str:
    updated = store.update(memory_id, new_text)
    if not updated:
        return json.dumps({"error": f"Memory {memory_id} not found."})
    return json.dumps({
        "status":  "updated",
        "id":      updated.id,
        "text":    updated.text,
    })

def tool_delete_memory(memory_id: str) -> str:
    success = store.delete(memory_id)
    return json.dumps({
        "status": "deleted" if success else "not_found",
        "id": memory_id
    })

def tool_list_memories(user_id: str) -> str:
    memories = store.list_all(user_id)
    return json.dumps({
        "count": len(memories),
        "memories": [m.model_dump() for m in memories]
    })