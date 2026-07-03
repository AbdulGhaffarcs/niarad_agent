"""
core/vector_store.py — batch embedding, hash tracking
"""

import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

DB_DIR = "./faiss_index"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 32


def _get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True, "batch_size": BATCH_SIZE},
    )


def get_vector_store():
    if not os.path.exists(DB_DIR):
        return None
    try:
        return FAISS.load_local(DB_DIR, _get_embeddings(), allow_dangerous_deserialization=True)
    except Exception:
        return None


def add_to_store(chunks):
    embeddings = _get_embeddings()
    if os.path.exists(DB_DIR):
        vs = FAISS.load_local(DB_DIR, embeddings, allow_dangerous_deserialization=True)
        for i in range(0, len(chunks), BATCH_SIZE):
            vs.add_documents(chunks[i:i+BATCH_SIZE])
    else:
        vs = FAISS.from_documents(chunks[:BATCH_SIZE], embeddings)
        for i in range(BATCH_SIZE, len(chunks), BATCH_SIZE):
            vs.add_documents(chunks[i:i+BATCH_SIZE])
    vs.save_local(DB_DIR)
    return True


def clear_store():
    import shutil
    if os.path.exists(DB_DIR):
        shutil.rmtree(DB_DIR)
