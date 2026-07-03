"""
core/flashcard_gen.py
Generate flashcards from the user's vault (or a free-text topic) and store
them in the SRS. Reuses the existing FAISS vector store and Groq LLM.

Flow:
    generate_from_vault(topic, count)
      -> similarity_search the vault for the topic
      -> ask the LLM for atomic Q/A pairs as JSON
      -> de-duplicate and persist via core.srs.add_cards
"""

import os
import re
import json
from functools import lru_cache
from langchain_groq import ChatGroq

from core import srs

_CARD_PROMPT = """You are creating study flashcards for a student on the topic: "{topic}".

Use ONLY the source material below. Make {count} atomic flashcards. Each card
tests ONE fact or concept. Front = a clear question. Back = a concise answer
(1-2 sentences). Avoid yes/no questions. Do not invent facts not in the source.

SOURCE MATERIAL:
{context}

Respond with ONLY a JSON array, no prose, no markdown fences:
[{{"front": "...", "back": "...", "topic": "{topic}"}}]
"""


@lru_cache(maxsize=1)
def _llm():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY not set")
    return ChatGroq(model="llama-3.1-8b-instant", api_key=key,
                    temperature=0.2, max_tokens=2048)


def _parse_cards(raw: str) -> list[dict]:
    raw = re.sub(r"```(json)?", "", raw).strip()
    m = re.search(r"\[.*\]", raw, re.DOTALL)
    if not m:
        return []
    try:
        items = json.loads(m.group(0))
    except json.JSONDecodeError:
        return []
    out = []
    for it in items:
        f, b = str(it.get("front", "")).strip(), str(it.get("back", "")).strip()
        if f and b:
            out.append({"front": f, "back": b, "topic": it.get("topic", "General")})
    return out


def generate_from_vault(topic: str, count: int = 8) -> dict:
    """Generate `count` cards about `topic` from indexed documents."""
    from core.vector_store import get_vector_store
    db = get_vector_store()
    if db is None:
        return {"ok": False, "error": "No documents in vault. Upload files first.",
                "added": 0}

    docs = db.similarity_search(topic, k=6)
    if not docs:
        return {"ok": False, "error": f"No vault content found for '{topic}'.",
                "added": 0}

    context = "\n\n".join(d.page_content[:600] for d in docs)
    sources = sorted({
        os.path.basename(d.metadata.get("source", "")) for d in docs
        if d.metadata.get("source")
    })

    raw = _llm().invoke(
        _CARD_PROMPT.format(topic=topic, count=count, context=context)
    ).content
    cards = _parse_cards(raw)
    for c in cards:
        c["topic"] = topic
        c["source"] = ", ".join(sources)

    added = srs.add_cards(cards)
    return {"ok": True, "generated": len(cards), "added": added,
            "topic": topic, "sources": sources}


def generate_from_text(topic: str, text: str, count: int = 8) -> dict:
    """Generate cards from raw text (no vault needed)."""
    raw = _llm().invoke(
        _CARD_PROMPT.format(topic=topic, count=count, context=text[:4000])
    ).content
    cards = _parse_cards(raw)
    for c in cards:
        c["topic"] = topic
    added = srs.add_cards(cards)
    return {"ok": True, "generated": len(cards), "added": added, "topic": topic}
