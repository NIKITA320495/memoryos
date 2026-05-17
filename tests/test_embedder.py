# tests/test_embedder.py
import pytest
from src.embedder import Embedder

@pytest.fixture
def embedder():
    return Embedder()

def test_singleton(embedder):
    """Embedder should be a singleton — same instance every time"""
    e2 = Embedder()
    assert embedder is e2

def test_embed_returns_list(embedder):
    """embed() should return a list of floats"""
    result = embedder.embed("I love building AI projects")
    assert isinstance(result, list)
    assert all(isinstance(x, float) for x in result)

def test_embed_fixed_dimension(embedder):
    """all-MiniLM-L6-v2 always outputs 384 dimensions"""
    result = embedder.embed("test sentence")
    assert len(result) == 384

def test_embed_batch(embedder):
    """embed_batch should return one vector per input"""
    texts = ["hello", "world", "generative ai"]
    results = embedder.embed_batch(texts)
    assert len(results) == 3
    assert all(len(r) == 384 for r in results)

def test_similar_texts_close(embedder):
    """semantically similar texts should have high cosine similarity"""
    v1 = embedder.embed("I enjoy machine learning")
    v2 = embedder.embed("I like deep learning")
    v3 = embedder.embed("The weather is sunny today")

    def cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x**2 for x in a) ** 0.5
        norm_b = sum(x**2 for x in b) ** 0.5
        return dot / (norm_a * norm_b)

    # similar texts should score higher than unrelated ones
    assert cosine(v1, v2) > cosine(v1, v3)

def test_empty_string(embedder):
    """empty string should still return a valid vector"""
    result = embedder.embed("")
    assert isinstance(result, list)
    assert len(result) == 384