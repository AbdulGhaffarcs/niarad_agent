# NIARAD — Study Agent

An AI study companion for students. It answers questions with tools (web search,
code, your documents, file generation) **and** runs a spaced-repetition loop that
remembers what you keep getting wrong and brings it back at the right time.

This is the complete project: FastAPI backend + a redesigned Next.js frontend.

```
niarad_agent/
├── backend/            FastAPI · LangChain ReAct · Groq · FAISS · SM-2 (SQLite)
│   ├── core/           agent, intent classifier, srs, flashcard_gen, srs_routes, loaders, vector_store
│   ├── tools/          web_search, vault_search, execute_code, generate_pdf/docx
│   ├── main.py         API + routers
│   └── demo_srs.py     offline demo of the review loop (no API key)
├── frontend/           Next.js 14 · TypeScript · 4 views, modern UI
│   └── src/
│       ├── app/        layout, globals.css (design system), page (app shell)
│       ├── components/ Sidebar, ChatView, StudyView, VaultView, FilesView, Flashcard, MasteryRing
│       └── lib/api.ts  typed backend client
└── design-preview.html open in a browser to see the UI without running anything
```

## What's new vs. the original

- **Study loop** — generate flashcards from your vault, review them with SM-2
  scheduling, and see a per-topic mastery dashboard. "Drill weak spots" pulls
  cards from the topics you score lowest on. (Backend: `core/srs.py`,
  `flashcard_gen.py`, `srs_routes.py`.)
- **LLM intent classifier** replaces the keyword blocklist that used to block
  legitimate coursework ("kill a process", "bomb calorimeter", etc.). It fails
  open to academic so a hiccup never blocks real study. (`core/intent.py`)
- **Redesigned frontend** — a four-tab app (Ask / Study / Vault / Files) with a
  warm-paper flashcard, a mastery-ring dashboard, Fraunces + Inter + JetBrains
  Mono type, and a single gold accent. No new aesthetic; a deliberate one.

## Run it

You need a **free** Groq API key (no credit card): https://console.groq.com
Everything else — DuckDuckGo search, FAISS, HuggingFace embeddings — runs locally.

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then paste your GROQ_API_KEY into .env
uvicorn main:app --reload   # http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local   # points at http://localhost:8000
npm run dev                         # http://localhost:3000
```

### See the loop without any setup
```bash
cd backend && python demo_srs.py
```

## Using it

1. **Vault** — drop in lecture PDFs / notes (PDF, DOCX, PPTX, XLSX, CSV). They're
   indexed locally.
2. **Study** — type a topic, generate cards from the vault, then **Review due**.
   Grade each card 1–5; the schedule and your mastery scores update automatically.
3. **Ask** — chat with the agent; it searches, runs code, reads your docs, and can
   produce a PDF/DOCX.
4. **Files** — download anything the agent generated.

## API surface

```
POST   /chat                {message}              -> {response, mode, steps, intent}
POST   /vault/upload        (multipart file)
GET    /vault/status
DELETE /vault/clear
GET    /files/list
POST   /cards/generate      {topic, count, text?}
GET    /cards/due           ?limit=&topic=
POST   /cards/review        {card_id, grade 0-5}
POST   /cards/quiz_weak     {count}
GET    /cards/stats
GET    /topics/weak         ?threshold=
```

## Notes

- SM-2 lives in `core/srs.py` (~20 commented lines). Storage is one SQLite file
  (`NIARAD_SRS_DB`, default `./niarad_srs.db`) — add a `user_id` column to go
  multi-user; the schema is ready for it.
- On Groq's free tier the binding limit is tokens/minute, not cost. Heavy use may
  hit a 429 — wait a few seconds. No charges.
- Frontend verified with `tsc --noEmit` and a full `next build`.
