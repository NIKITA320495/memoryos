# src/embedder.py
from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_MODEL

class Embedder:
    _instance = None  # singleton — model loads once, reused forever

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = SentenceTransformer(EMBEDDING_MODEL)
            print(f"[Embedder] Loaded model: {EMBEDDING_MODEL}")
        return cls._instance

    def embed(self, text: str) -> list[float]:
        return self.model.encode(text, normalize_embeddings=True).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(
            texts, normalize_embeddings=True, batch_size=32
        ).tolist()