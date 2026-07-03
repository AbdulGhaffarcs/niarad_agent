"""
core/srs.py
Spaced-Repetition System for NIARAD.

- SM-2 scheduling algorithm (the SuperMemo-2 algorithm, same family Anki uses).
- SQLite persistence (stdlib only, no extra deps, survives restarts).
- Weak-topic tracking derived from review history.

Public API:
    add_card(front, back, topic, source) -> int
    add_cards(list_of_dicts) -> int (count inserted, de-duplicated by front+topic)
    get_due_cards(limit=20) -> list[dict]
    review_card(card_id, grade) -> dict   # grade in 0..5
    topic_report() -> list[dict]          # mastery + weakness per topic
    weak_topics(threshold=60) -> list[str]
    stats() -> dict
    reset()                                # wipe (test/demo only)
"""

import os
import sqlite3
import datetime as dt
from contextlib import contextmanager

DB_PATH = os.getenv("NIARAD_SRS_DB", "./niarad_srs.db")

# ---- SM-2 tuning constants -------------------------------------------------
MIN_EASE = 1.3          # ease factor floor (SM-2 standard)
DEFAULT_EASE = 2.5      # starting ease factor
PASS_GRADE = 3          # grade >= 3 counts as a successful recall


@contextmanager
def _conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db():
    with _conn() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS cards (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                front        TEXT NOT NULL,
                back         TEXT NOT NULL,
                topic        TEXT NOT NULL DEFAULT 'General',
                source       TEXT DEFAULT '',
                ease_factor  REAL NOT NULL DEFAULT 2.5,
                interval     INTEGER NOT NULL DEFAULT 0,
                repetitions  INTEGER NOT NULL DEFAULT 0,
                lapses       INTEGER NOT NULL DEFAULT 0,
                due_date     TEXT NOT NULL,
                created_at   TEXT NOT NULL,
                UNIQUE(front, topic)
            );
            CREATE TABLE IF NOT EXISTS reviews (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id     INTEGER NOT NULL,
                topic       TEXT NOT NULL,
                grade       INTEGER NOT NULL,
                reviewed_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_cards_due ON cards(due_date);
            CREATE INDEX IF NOT EXISTS idx_reviews_topic ON reviews(topic);
            """
        )


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _iso(d: dt.datetime) -> str:
    return d.isoformat()


# ---- card creation ---------------------------------------------------------
def add_card(front: str, back: str, topic: str = "General", source: str = "") -> int:
    init_db()
    now = _now()
    with _conn() as con:
        cur = con.execute(
            """INSERT OR IGNORE INTO cards
               (front, back, topic, source, ease_factor, interval, repetitions,
                lapses, due_date, created_at)
               VALUES (?,?,?,?,?,0,0,0,?,?)""",
            (front.strip(), back.strip(), topic.strip(), source,
             DEFAULT_EASE, _iso(now), _iso(now)),
        )
        return cur.lastrowid or 0


def add_cards(cards: list[dict]) -> int:
    """Bulk insert. Each dict: {front, back, topic?, source?}. Returns inserted count."""
    init_db()
    inserted = 0
    for c in cards:
        rid = add_card(
            c["front"], c["back"],
            c.get("topic", "General"), c.get("source", ""),
        )
        if rid:
            inserted += 1
    return inserted


# ---- the SM-2 core ---------------------------------------------------------
def _sm2(ease: float, interval: int, reps: int, grade: int):
    """
    Return (new_ease, new_interval_days, new_reps, lapsed_bool).
    grade: 0-5 quality of recall (5 = perfect, 0 = total blank).
    """
    lapsed = grade < PASS_GRADE

    if lapsed:
        # Failed recall: reset the learning streak, see it again tomorrow.
        new_reps = 0
        new_interval = 1
    else:
        new_reps = reps + 1
        if new_reps == 1:
            new_interval = 1
        elif new_reps == 2:
            new_interval = 6
        else:
            new_interval = round(interval * ease)

    # Ease-factor update (applied on every review, clamped at the floor).
    new_ease = ease + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
    new_ease = max(MIN_EASE, new_ease)

    return round(new_ease, 4), max(1, new_interval), new_reps, lapsed


def review_card(card_id: int, grade: int) -> dict:
    if not (0 <= grade <= 5):
        raise ValueError("grade must be 0..5")
    init_db()
    with _conn() as con:
        row = con.execute("SELECT * FROM cards WHERE id=?", (card_id,)).fetchone()
        if row is None:
            raise ValueError(f"card {card_id} not found")

        ease, interval, reps, lapsed = _sm2(
            row["ease_factor"], row["interval"], row["repetitions"], grade
        )
        now = _now()
        due = now + dt.timedelta(days=interval)
        new_lapses = row["lapses"] + (1 if lapsed else 0)

        con.execute(
            """UPDATE cards SET ease_factor=?, interval=?, repetitions=?,
               lapses=?, due_date=? WHERE id=?""",
            (ease, interval, reps, new_lapses, _iso(due), card_id),
        )
        con.execute(
            "INSERT INTO reviews (card_id, topic, grade, reviewed_at) VALUES (?,?,?,?)",
            (card_id, row["topic"], grade, _iso(now)),
        )
    return {
        "card_id": card_id,
        "topic": row["topic"],
        "grade": grade,
        "lapsed": lapsed,
        "ease_factor": ease,
        "interval_days": interval,
        "repetitions": reps,
        "next_due": _iso(due),
    }


# ---- retrieval -------------------------------------------------------------
def get_due_cards(limit: int = 20, topic: str | None = None) -> list[dict]:
    init_db()
    now_iso = _iso(_now())
    q = "SELECT * FROM cards WHERE due_date <= ?"
    args: list = [now_iso]
    if topic:
        q += " AND topic = ?"
        args.append(topic)
    q += " ORDER BY due_date ASC LIMIT ?"
    args.append(limit)
    with _conn() as con:
        rows = con.execute(q, args).fetchall()
    return [dict(r) for r in rows]


# ---- weak-topic tracking ---------------------------------------------------
def topic_report() -> list[dict]:
    """
    Per-topic mastery dashboard. Mastery (0-100) blends recent recall quality
    with the lapse rate, so a topic you keep blanking on scores low even if a
    few cards went well.
    """
    init_db()
    with _conn() as con:
        topics = [r["topic"] for r in
                  con.execute("SELECT DISTINCT topic FROM cards").fetchall()]
        report = []
        for t in topics:
            total = con.execute(
                "SELECT COUNT(*) c FROM cards WHERE topic=?", (t,)
            ).fetchone()["c"]
            due = con.execute(
                "SELECT COUNT(*) c FROM cards WHERE topic=? AND due_date<=?",
                (t, _iso(_now())),
            ).fetchone()["c"]

            recent = con.execute(
                "SELECT grade FROM reviews WHERE topic=? ORDER BY id DESC LIMIT 10",
                (t,),
            ).fetchall()
            grades = [r["grade"] for r in recent]

            if grades:
                avg = sum(grades) / len(grades)
                lapse_rate = sum(1 for g in grades if g < PASS_GRADE) / len(grades)
                mastery = round((avg / 5) * 100 * (1 - 0.5 * lapse_rate))
            else:
                avg = None
                lapse_rate = 0.0
                mastery = 0  # never reviewed -> not yet mastered

            report.append({
                "topic": t,
                "cards": total,
                "due": due,
                "reviews": len(grades),
                "avg_grade": round(avg, 2) if avg is not None else None,
                "lapse_rate": round(lapse_rate, 2),
                "mastery": mastery,
                "weak": (len(grades) >= 3 and (mastery < 60 or lapse_rate > 0.3)),
            })
    report.sort(key=lambda r: (r["mastery"], -r["due"]))
    return report


def weak_topics(threshold: int = 60) -> list[str]:
    return [r["topic"] for r in topic_report()
            if r["reviews"] >= 3 and r["mastery"] < threshold]


def stats() -> dict:
    init_db()
    with _conn() as con:
        total = con.execute("SELECT COUNT(*) c FROM cards").fetchone()["c"]
        due = con.execute(
            "SELECT COUNT(*) c FROM cards WHERE due_date<=?", (_iso(_now()),)
        ).fetchone()["c"]
        reviews = con.execute("SELECT COUNT(*) c FROM reviews").fetchone()["c"]
    return {"total_cards": total, "due_now": due, "total_reviews": reviews,
            "topics": topic_report()}


def reset():
    init_db()
    with _conn() as con:
        con.execute("DELETE FROM cards")
        con.execute("DELETE FROM reviews")
