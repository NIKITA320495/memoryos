# src/models.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class Memory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    user_id: str
    tags: list[str] = []
    importance: int = Field(default=5, ge=1, le=10)
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    last_accessed: Optional[str] = None

class StoreRequest(BaseModel):
    text: str
    user_id: str
    tags: list[str] = []
    importance: int = Field(default=5, ge=1, le=10)

class SearchRequest(BaseModel):
    query: str
    user_id: str
    top_k: int = Field(default=5, ge=1, le=20)

class SearchResult(BaseModel):
    id: str
    text: str
    score: float
    tags: list[str]
    importance: int
    created_at: str