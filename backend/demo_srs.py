"""
demo_srs.py — run the spaced-repetition loop end-to-end with NO API key.

    python demo_srs.py

Simulates a student studying two topics over several cram sessions, shows SM-2
rescheduling, and prints the weak-topic dashboard. Uses a throwaway DB.
"""

import os
os.environ["NIARAD_SRS_DB"] = "./demo_srs.db"

from core import srs

srs.reset()

print("1) Seeding flashcards (this is what flashcard_gen produces from the vault)\n")
seed = [
    {"front": "Time complexity of binary search?", "back": "O(log n)", "topic": "Algorithms"},
    {"front": "What does a stack's 'pop' do?", "back": "Removes/returns the top (LIFO) element.", "topic": "Algorithms"},
    {"front": "Worst-case of quicksort?", "back": "O(n^2) with a bad pivot.", "topic": "Algorithms"},
    {"front": "What is a deadlock?", "back": "Circular wait — each process holds what another needs.", "topic": "Operating Systems"},
    {"front": "What is a semaphore?", "back": "Integer sync primitive guarding shared resources.", "topic": "Operating Systems"},
    {"front": "Define a race condition.", "back": "Outcome depends on unsynchronized concurrent timing.", "topic": "Operating Systems"},
]
srs.add_cards(seed)
s = srs.stats()
print(f"   total cards: {s['total_cards']}, due now: {s['due_now']}\n")

# Card ids are assigned in seed order (1..N) -> map id to its topic directly.
ID_TOPIC = {i + 1: seed[i]["topic"] for i in range(len(seed))}

GRADE_BY_TOPIC = {"Algorithms": 5, "Operating Systems": 2}  # strong vs weak student

print("2) Three cram sessions — strong on Algorithms (g=5), weak on OS (g=2)\n")
n_cards = s["total_cards"]
for session in range(1, 4):
    for cid in range(1, n_cards + 1):
        topic = ID_TOPIC[cid]
        r = srs.review_card(cid, GRADE_BY_TOPIC[topic])
    print(f"   session {session}: reviewed {n_cards} cards")

print("\n3) Weak-topic dashboard\n")
for t in srs.topic_report():
    flag = "   <== WEAK, prioritize" if t["weak"] else ""
    print(f"   {t['topic']:<18} mastery={t['mastery']:>3}/100  "
          f"avg_grade={t['avg_grade']}  lapse_rate={t['lapse_rate']}  "
          f"reviews={t['reviews']}{flag}")

print(f"\n   weak_topics() -> {srs.weak_topics()}")
print("4) 'Quiz me on my weak spots' would draw from:",
      srs.weak_topics() or "(nothing weak yet)")

os.remove("./demo_srs.db")
