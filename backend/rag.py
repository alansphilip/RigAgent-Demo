"""
RAG (Retrieval-Augmented Generation) pipeline for equipment knowledge.
Uses scikit-learn TF-IDF + cosine similarity for lightweight, memory-efficient search.
No PyTorch or FAISS required — works within Render's 512MB free tier.
"""
import os
import json
from typing import List

# In-memory TF-IDF index (built once, reused across requests)
_vectorizer = None
_tfidf_matrix = None
_chunks = None

CHUNK_SIZE = 500   # characters per chunk
CHUNK_OVERLAP = 100


# ---------------------------------------------------------------------------
# Text chunking
# ---------------------------------------------------------------------------

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks


# ---------------------------------------------------------------------------
# Index management
# ---------------------------------------------------------------------------

def _build_tfidf(all_chunks: List[str]):
    """Fit a TF-IDF vectorizer on the given chunks and return (vectorizer, matrix)."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=20000,
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform(all_chunks)
    return vectorizer, matrix


def build_index(documents: List[tuple]):
    """
    Build TF-IDF index from a list of (equipment_name, content) tuples.
    Stores everything in memory — no disk I/O required.
    """
    global _vectorizer, _tfidf_matrix, _chunks

    all_chunks = []
    all_metadata = []

    for name, content in documents:
        for chunk in chunk_text(content):
            all_chunks.append(chunk)
            all_metadata.append({"equipment": name, "text": chunk})

    if not all_chunks:
        print("No chunks to index.")
        return

    print(f"Building TF-IDF index over {len(all_chunks)} chunks...")
    _vectorizer, _tfidf_matrix = _build_tfidf(all_chunks)
    _chunks = all_metadata
    print("TF-IDF index built successfully.")


def reset_cache():
    """Clear the in-memory index (useful for testing)."""
    global _vectorizer, _tfidf_matrix, _chunks
    _vectorizer = None
    _tfidf_matrix = None
    _chunks = None


def _ensure_index():
    """Build the index from the DB if it hasn't been built yet."""
    global _vectorizer, _tfidf_matrix, _chunks
    if _vectorizer is not None:
        return
    build_rag_from_db()


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

def retrieve(query: str, top_k: int = 4) -> List[dict]:
    """
    Retrieve top-k relevant chunks for a query.
    Returns list of {equipment, text, score} dicts.
    """
    query_lower = query.lower()

    # 1. Direct DB lookup — exact equipment name match (highest precision)
    try:
        from database import SessionLocal, EquipmentKB
        db = SessionLocal()
        try:
            all_kb = db.query(EquipmentKB).all()
            for kb in all_kb:
                name_lower = kb.equipment_name.lower()
                words = [w for w in name_lower.split() if len(w) > 3]
                if name_lower in query_lower or (words and all(w in query_lower for w in words)):
                    chunks = chunk_text(kb.content)
                    return [{"equipment": kb.equipment_name, "text": c, "score": 0.99} for c in chunks[:top_k]]
        finally:
            db.close()
    except Exception as e:
        print(f"Direct DB lookup error: {e}")

    # 2. TF-IDF semantic search
    _ensure_index()
    if _vectorizer is None or _tfidf_matrix is None or not _chunks:
        return keyword_fallback(query, top_k)

    try:
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        query_vec = _vectorizer.transform([query])
        scores = cosine_similarity(query_vec, _tfidf_matrix)[0]
        top_indices = scores.argsort()[::-1][:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                item = _chunks[idx].copy()
                item["score"] = float(scores[idx])
                results.append(item)

        if results:
            return results
    except Exception as e:
        print(f"TF-IDF search error: {e}")

    return keyword_fallback(query, top_k)


def keyword_fallback(query: str, top_k: int = 4) -> List[dict]:
    """Simple keyword-overlap fallback when the TF-IDF index is unavailable."""
    if not _chunks:
        return []
    query_words = set(query.lower().split())
    scored = []
    for chunk in _chunks:
        text_words = set(chunk["text"].lower().split())
        score = len(query_words & text_words) / max(len(query_words), 1)
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [{"equipment": c["equipment"], "text": c["text"], "score": s} for s, c in scored[:top_k]]


# ---------------------------------------------------------------------------
# Bootstrap from database
# ---------------------------------------------------------------------------

def build_rag_from_db():
    """Load all equipment KB entries from SQLite and build the TF-IDF index."""
    try:
        from database import SessionLocal, EquipmentKB
        db = SessionLocal()
        try:
            entries = db.query(EquipmentKB).all()
            documents = [(e.equipment_name, e.content) for e in entries]
            if documents:
                build_index(documents)
            else:
                print("No equipment KB entries found. Run setup_db.py first.")
        finally:
            db.close()
    except Exception as e:
        print(f"Error building RAG from DB: {e}")
