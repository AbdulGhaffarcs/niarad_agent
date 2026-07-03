"""
core/intent.py
LLM intent classifier — replaces the substring keyword blocklist.

The old guard blocked legitimate coursework: "kill a process", "the better
algorithm", "bomb calorimeter", "drug interactions", most of history and
political science. This classifies the *actual intent* instead.

Returns one of:
    ACADEMIC    -> route to the ReAct agent
    SMALL_TALK  -> fast greeting reply, skip the agent
    OFF_TOPIC   -> politely decline (genuinely non-academic / harmful)

Design choices:
- A tiny heuristic fast-path catches trivial greetings with zero latency/cost.
- The LLM call is cheap (one short JSON response on the 8b model).
- Fail-OPEN to ACADEMIC: if the classifier errors, we'd rather risk answering
  a borderline question than wrongly block a student's real coursework. The
  agent's own system prompt still refuses genuinely harmful requests.
"""

import os
import re
import json
from functools import lru_cache
from langchain_groq import ChatGroq

# Obvious greetings -> skip the LLM entirely.
_GREETING_FASTPATH = {
    "hi", "hello", "hey", "sup", "yo", "greetings", "howdy",
    "good morning", "good evening", "good afternoon", "good night",
    "thanks", "thank you", "thank u", "bye", "goodbye", "ok", "okay",
}

_CLASSIFIER_PROMPT = """You are the intent router for NIARAD, an academic study assistant for students.

Classify the user's message into exactly ONE category:

- ACADEMIC: any genuine learning, study, coursework, research, or knowledge
  question across ANY subject — including chemistry (e.g. bomb calorimetry),
  pharmacology (drug interactions), history/politics (war, weapons, violence as
  subjects of study), computer science ("kill a process", exploits studied
  academically), law, medicine, etc. Academic intent is ACADEMIC even if the
  wording contains scary words.
- SMALL_TALK: greetings, thanks, goodbyes, "who are you", "what can you do",
  casual chit-chat with no informational request.
- OFF_TOPIC: requests with clear harmful or non-academic intent — actually
  helping someone hack/attack a real system, build a real weapon, obtain illegal
  drugs, produce adult content, gamble, defraud, or self-harm. The test is
  INTENT TO ACT, not mere presence of a keyword.

Respond with ONLY a JSON object, no prose, no markdown:
{{"category": "ACADEMIC|SMALL_TALK|OFF_TOPIC", "reason": "<=12 words"}}

Message: {message}
JSON:"""


@lru_cache(maxsize=1)
def _llm():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY not set")
    return ChatGroq(model="llama-3.1-8b-instant", api_key=key,
                    temperature=0, max_tokens=120)


def _fast_small_talk(q: str) -> bool:
    s = q.strip().lower().rstrip("!?. ")
    return s in _GREETING_FASTPATH


def _parse(raw: str) -> dict:
    raw = re.sub(r"```(json)?", "", raw).strip()
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        raise ValueError("no JSON found")
    return json.loads(m.group(0))


def classify(query: str) -> dict:
    """Return {category, reason, via}. Never raises — fails open to ACADEMIC."""
    q = (query or "").strip()
    if not q:
        return {"category": "SMALL_TALK", "reason": "empty", "via": "fastpath"}

    if _fast_small_talk(q):
        return {"category": "SMALL_TALK", "reason": "greeting", "via": "fastpath"}

    try:
        raw = _llm().invoke(_CLASSIFIER_PROMPT.format(message=q)).content
        data = _parse(raw)
        cat = str(data.get("category", "")).upper()
        if cat not in {"ACADEMIC", "SMALL_TALK", "OFF_TOPIC"}:
            cat = "ACADEMIC"
        return {"category": cat,
                "reason": data.get("reason", ""),
                "via": "llm"}
    except Exception as e:
        # Fail open — never block real coursework on a classifier hiccup.
        return {"category": "ACADEMIC", "reason": f"classifier fallback: {e}",
                "via": "fallback"}
