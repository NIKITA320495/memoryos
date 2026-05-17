# src/memory_store.py
import chromadb
import json
from datetime import datetime
from src.config import MEMORY_DB_PATH, COLLECTION_NAME, MAX_SEARCH_RESULTS
from src.embedder import Embedder
from src.models import Memory, StoreRequest, SearchRequest, SearchResult

class MemoryStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=MEMORY_DB_PATH)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        self.embedder = Embedder()
        print(f"[MemoryStore] Connected to collection: {COLLECTION_NAME}")

    def store(self, req: StoreRequest) -> Memory:
        memory = Memory(
            text=req.text,
            user_id=req.user_id,
            tags=req.tags,
            importance=req.importance,
        )
        embedding = self.embedder.embed(memory.text)
        self.collection.add(
            ids=[memory.id],
            embeddings=[embedding],
            documents=[memory.text],
            metadatas=[{
                "user_id":     memory.user_id,
                "tags":        json.dumps(memory.tags),
                "importance":  memory.importance,
                "created_at":  memory.created_at,
            }]
        )
        return memory

    def search(self, req: SearchRequest) -> list[SearchResult]:
        query_embedding = self.embedder.embed(req.query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(req.top_k, MAX_SEARCH_RESULTS),
            where={"user_id": req.user_id},
            include=["documents", "metadatas", "distances"]
        )
        output = []
        for i, doc in enumerate(results["documents"][0]):
            meta  = results["metadatas"][0][i]
            dist  = results["distances"][0][i]
            score = round(1 - dist, 4)   # cosine: distance → similarity
            output.append(SearchResult(
                id=results["ids"][0][i],
                text=doc,
                score=score,
                tags=json.loads(meta.get("tags", "[]")),
                importance=meta.get("importance", 5),
                created_at=meta.get("created_at", ""),
            ))
        return output

    def get_by_id(self, memory_id: str) -> Memory | None:
        result = self.collection.get(
            ids=[memory_id],
            include=["documents", "metadatas"]
        )
        if not result["ids"]:
            return None
        meta = result["metadatas"][0]
        return Memory(
            id=memory_id,
            text=result["documents"][0],
            user_id=meta["user_id"],
            tags=json.loads(meta.get("tags", "[]")),
            importance=meta.get("importance", 5),
            created_at=meta.get("created_at", ""),
        )

    def update(self, memory_id: str, new_text: str) -> Memory | None:
        existing = self.get_by_id(memory_id)
        if not existing:
            return None
        new_embedding = self.embedder.embed(new_text)
        self.collection.update(
            ids=[memory_id],
            embeddings=[new_embedding],
            documents=[new_text],
            metadatas=[{
                "user_id":    existing.user_id,
                "tags":       json.dumps(existing.tags),
                "importance": existing.importance,
                "created_at": existing.created_at,
            }]
        )
        existing.text = new_text
        existing.last_accessed = datetime.utcnow().isoformat()
        return existing

    def delete(self, memory_id: str) -> bool:
        try:
            self.collection.delete(ids=[memory_id])
            return True
        except Exception:
            return False

    def list_all(self, user_id: str) -> list[Memory]:
        results = self.collection.get(
            where={"user_id": user_id},
            include=["documents", "metadatas"]
        )
        memories = []
        for i, doc in enumerate(results["documents"]):
            meta = results["metadatas"][i]
            memories.append(Memory(
                id=results["ids"][i],
                text=doc,
                user_id=user_id,
                tags=json.loads(meta.get("tags", "[]")),
                importance=meta.get("importance", 5),
                created_at=meta.get("created_at", ""),
            ))
        return memories