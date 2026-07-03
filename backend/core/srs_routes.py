"""
core/srs_routes.py
FastAPI router exposing the spaced-repetition + flashcard loop.

Wire into main.py with two lines:
    from core.srs_routes import router as srs_router
    app.include_router(srs_router)

Endpoints:
    POST   /cards/generate   {topic, count, text?}  -> make cards from vault (or text)
    GET    /cards/due        ?limit=&topic=         -> cards due for review now
    POST   /cards/review     {card_id, grade(0-5)}  -> grade a card, reschedule (SM-2)
    GET    /cards/stats                              -> overall + per-topic dashboard
    GET    /topics/weak      ?threshold=             -> list of weak topics
    POST   /cards/quiz_weak  {count}                 -> due cards drawn from weak topics
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from core import srs

router = APIRouter(tags=["spaced-repetition"])


class GenerateReq(BaseModel):
    topic: str
    count: int = Field(8, ge=1, le=30)
    text: str | None = None  # if provided, generate from raw text instead of vault


class ReviewReq(BaseModel):
    card_id: int
    grade: int = Field(..., ge=0, le=5)


class QuizWeakReq(BaseModel):
    count: int = Field(10, ge=1, le=100)


@router.post("/cards/generate")
def generate(req: GenerateReq):
    from core.flashcard_gen import generate_from_vault, generate_from_text
    try:
        if req.text:
            return generate_from_text(req.topic, req.text, req.count)
        return generate_from_vault(req.topic, req.count)
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/cards/due")
def due(limit: int = 20, topic: str | None = None):
    return {"cards": srs.get_due_cards(limit=limit, topic=topic)}


@router.post("/cards/review")
def review(req: ReviewReq):
    try:
        return srs.review_card(req.card_id, req.grade)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/cards/stats")
def card_stats():
    return srs.stats()


@router.get("/topics/weak")
def weak(threshold: int = 60):
    return {"weak_topics": srs.weak_topics(threshold), "threshold": threshold}


@router.post("/cards/quiz_weak")
def quiz_weak(req: QuizWeakReq):
    """Pull due cards preferentially from the student's weakest topics."""
    weak = set(srs.weak_topics())
    due_cards = srs.get_due_cards(limit=100)
    weak_first = [c for c in due_cards if c["topic"] in weak]
    rest = [c for c in due_cards if c["topic"] not in weak]
    return {"cards": (weak_first + rest)[:req.count], "weak_topics": sorted(weak)}
