"""
RAG (Retrieval-Augmented Generation) pipeline for equipment knowledge.
Uses sentence-transformers for embeddings and FAISS for vector search.
"""
import os
import json
import numpy as np
from typing import List, Tuple

# These will be imported lazily to avoid slow startup if not needed
_model = None
_index = None
_chunks = None

FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./faiss_index")
CHUNK_SIZE = 500  # characters per chunk
CHUNK_OVERLAP = 100


def get_embedding_model():
    """Lazy load the sentence transformer model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            print("Loading embedding model (this may take a moment on first run)...")
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            print("Embedding model loaded.")
        except ImportError:
            print("WARNING: sentence-transformers not installed. RAG will use basic keyword search.")
            _model = None
    return _model


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


def build_index(documents: List[Tuple[str, str]]):
    """
    Build FAISS index from a list of (equipment_name, content) tuples.
    Saves index and chunks to disk for reuse.
    """
    import faiss
    
    model = get_embedding_model()
    if model is None:
        print("Skipping FAISS index build - no embedding model.")
        return
    
    all_chunks = []
    all_metadata = []
    
    for name, content in documents:
        chunks = chunk_text(content)
        for chunk in chunks:
            all_chunks.append(chunk)
            all_metadata.append({"equipment": name, "text": chunk})
    
    print(f"Embedding {len(all_chunks)} chunks...")
    embeddings = model.encode(all_chunks, show_progress_bar=True)
    embeddings = np.array(embeddings, dtype="float32")
    
    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # Build index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product (cosine after normalization)
    index.add(embeddings)
    
    # Save
    os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
    faiss.write_index(index, os.path.join(FAISS_INDEX_PATH, "equipment.index"))
    with open(os.path.join(FAISS_INDEX_PATH, "chunks.json"), "w") as f:
        json.dump(all_metadata, f)
    
    print(f"FAISS index built with {len(all_chunks)} chunks and saved to {FAISS_INDEX_PATH}")


def load_index():
    """Load FAISS index from disk."""
    global _index, _chunks
    if _index is not None:
        return _index, _chunks
    
    index_file = os.path.join(FAISS_INDEX_PATH, "equipment.index")
    chunks_file = os.path.join(FAISS_INDEX_PATH, "chunks.json")
    
    if not os.path.exists(index_file):
        return None, None
    
    try:
        import faiss
        _index = faiss.read_index(index_file)
        with open(chunks_file, "r") as f:
            _chunks = json.load(f)
        print(f"FAISS index loaded: {_index.ntotal} vectors")
        return _index, _chunks
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        return None, None


def reset_cache():
    """Reset in-memory FAISS index cache to force reloading from disk."""
    global _index, _chunks
    _index = None
    _chunks = None


def retrieve(query: str, top_k: int = 4) -> List[dict]:
    """
    Retrieve top-k relevant chunks for a query.
    Returns list of {equipment, text, score} dicts.
    """
    query_lower = query.lower()
    
    # 1. Direct database lookup for exact equipment match
    try:
        from database import SessionLocal, EquipmentKB
        db = SessionLocal()
        try:
            all_kb = db.query(EquipmentKB).all()
            for kb in all_kb:
                name_lower = kb.equipment_name.lower()
                # Check if entire equipment name or key words (e.g., 'iron roughneck', 'mud pump') match
                if name_lower in query_lower or (len(name_lower) > 3 and all(w in query_lower for w in name_lower.split())):
                    chunks = chunk_text(kb.content)
                    results = [{"equipment": kb.equipment_name, "text": chk, "score": 0.99} for chk in chunks[:top_k]]
                    return results
        finally:
            db.close()
    except Exception as e:
        print(f"Direct DB lookup error in RAG: {e}")

    index, chunks = load_index()
    model = get_embedding_model()
    
    if index is None or model is None or not chunks:
        return keyword_fallback(query, top_k)
    
    # Check if query explicitly targets a specific equipment
    query_lower = query.lower()
    exact_matches = []
    for chunk in chunks:
        eq_name = chunk["equipment"].lower()
        if eq_name in query_lower or any(word in query_lower for word in eq_name.split() if len(word) > 3):
            exact_matches.append(chunk)
            
    if exact_matches:
        # If we have exact equipment matches, return top chunks for that equipment
        exact_results = []
        for em in exact_matches:
            item = em.copy()
            item["score"] = 0.95
            exact_results.append(item)
        return exact_results[:top_k]
    
    try:
        import faiss
        query_embedding = model.encode([query])
        query_embedding = np.array(query_embedding, dtype="float32")
        faiss.normalize_L2(query_embedding)
        
        scores, indices = index.search(query_embedding, top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(chunks):
                result = chunks[idx].copy()
                result["score"] = float(score)
                results.append(result)
        
        return results
    except Exception as e:
        print(f"FAISS search error: {e}")
        return keyword_fallback(query, top_k)


def keyword_fallback(query: str, top_k: int = 4) -> List[dict]:
    """Simple keyword-based fallback search when FAISS is unavailable."""
    _, chunks = load_index()
    if not chunks:
        return []
    
    query_words = set(query.lower().split())
    scored = []
    for chunk in chunks:
        text_words = set(chunk["text"].lower().split())
        score = len(query_words & text_words) / max(len(query_words), 1)
        scored.append((score, chunk))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return [{"equipment": c["equipment"], "text": c["text"], "score": s} for s, c in scored[:top_k]]


def build_rag_from_db():
    """Build RAG index from database equipment KB entries."""
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
