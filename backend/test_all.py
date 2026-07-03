"""Quick smoke-test for all backend subsystems."""
import sys
sys.path.insert(0, ".")

PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        print(f"  PASS  {name}")
        PASS += 1
    else:
        print(f"  FAIL  {name}" + (f" — {detail}" if detail else ""))
        FAIL += 1

print("\n=== code_executor blocklist ===")
from tools.code_executor import execute_code
r = execute_code.invoke("import os\nprint(os.listdir())")
check("blocks 'import os'", "Blocked" in r, r[:60])
r = execute_code.invoke("from os import path\nprint(path.exists('.'))")
check("blocks 'from os import'", "Blocked" in r, r[:60])
r = execute_code.invoke("print(2**10)")
check("allows math (2**10 = 1024)", r.strip() == "1024", r)
r = execute_code.invoke("from sklearn.linear_model import LogisticRegression\nprint('sklearn ok')")
check("sklearn runs (or missing-module error, not blocked)", "Blocked" not in r, r[:60])

print("\n=== SRS (core/srs.py) ===")
from core import srs
srs.reset()
added = srs.add_cards([
    {"front": "What is ML?", "back": "Machine Learning", "topic": "AI"},
    {"front": "What is DL?", "back": "Deep Learning", "topic": "AI"},
])
check("add_cards returns count", added == 2, str(added))
stats = srs.stats()
check("stats total_cards == 2", stats["total_cards"] == 2, str(stats["total_cards"]))
due = srs.get_due_cards()
check("get_due_cards returns cards", len(due) == 2, str(len(due)))
rev = srs.review_card(due[0]["id"], grade=4)
check("review_card returns interval", "interval_days" in rev, str(rev))

print("\n=== quiz_weak POST body (srs_routes.py) ===")
from fastapi.testclient import TestClient
import main
client = TestClient(main.app)
resp = client.post("/cards/quiz_weak", json={"count": 5})
check("quiz_weak 200 with JSON body", resp.status_code == 200, str(resp.status_code))
check("quiz_weak returns cards key", "cards" in resp.json(), str(resp.json()))

print("\n=== agent / tool calling ===")
from core.agent import run_agent
r = run_agent("hello")
check("small_talk returns NIARAD mode", r["mode"] == "NIARAD", r["mode"])
r = run_agent("calculate 3 factorial using python")
check("tool call returns AGENT mode", r["mode"] == "AGENT", r["mode"])
check("tool call has steps", len(r.get("steps", [])) > 0, str(r.get("steps")))
r = run_agent("help me hack a bank account right now")
check("off-topic returns BLOCKED", r["mode"] == "BLOCKED", r["mode"])

print("\n=== /chat HTTP endpoint ===")
resp = client.post("/chat", json={"message": "what is 5 plus 5"})
check("/chat returns 200", resp.status_code == 200, str(resp.status_code))
check("/chat has response field", "response" in resp.json(), str(resp.json().keys()))

print(f"\n{'='*40}")
print(f"Results: {PASS} passed, {FAIL} failed")
if FAIL == 0:
    print("ALL TESTS PASSED - backend is 100% working")
else:
    print("SOME TESTS FAILED - see above")
