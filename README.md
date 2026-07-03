<div align="center">

<img src="./banner.svg" width="100%" alt="NIARAD"/>

<br/>

![Status](https://img.shields.io/badge/Status-Active_Development-000000?style=flat-square&logoColor=FFC800&labelColor=060910&color=00FFAA)
![Version](https://img.shields.io/badge/Version-3.0_Full_Stack-000000?style=flat-square&labelColor=060910&color=00C8FF)
![Python](https://img.shields.io/badge/Python-3.10+-000000?style=flat-square&logo=python&logoColor=00FFAA&labelColor=060910&color=1C2A3A)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-000000?style=flat-square&logo=fastapi&logoColor=00FFAA&labelColor=060910&color=1C2A3A)
![Next.js](https://img.shields.io/badge/Next.js_14-Frontend-000000?style=flat-square&logo=next.js&logoColor=00FFAA&labelColor=060910&color=1C2A3A)
![LangChain](https://img.shields.io/badge/LangChain-ReAct_Agents-000000?style=flat-square&logoColor=00FFAA&labelColor=060910&color=1C2A3A)
![FAISS](https://img.shields.io/badge/FAISS-Vector_Store-000000?style=flat-square&logoColor=00FFAA&labelColor=060910&color=1C2A3A)
![Spaced-Repetition](https://img.shields.io/badge/SM--2-Spaced_Repetition-000000?style=flat-square&logoColor=00FFAA&labelColor=060910&color=1C2A3A)

<br/>

> *"Information is the resolution of uncertainty."*

</div>

---

## `// OVERVIEW`

**NIARAD** is a full-stack AI study companion for students. It answers questions with intelligent tools (web search, code execution, your documents, and file generation) **and** runs a spaced-repetition loop that remembers what you struggle with, bringing topics back at scientifically optimal times using the SM-2 algorithm.

This is the complete production-ready project: **FastAPI backend + Next.js 14 frontend**.

```text
Production-grade architecture. Intelligent study loops. Locally-indexed documents. 
Free Groq API (no credit card). TypeScript type-safety. Modern UI/UX.
```

---

## `// MIGRATION NOTE`

**This project is the successor to [Kryptos-Niarad](https://github.com/AbdulGhaffarcs/Kryptos-Niarad)**, our original Streamlit-based RAG application. We've evolved it from a single-file prototype into a complete full-stack system with:

- ✅ Advanced multi-tool agents (web search, code execution, document generation)
- ✅ SM-2 spaced-repetition learning engine with mastery dashboards
- ✅ LLM-powered intent classification (replaces keyword blocklists)
- ✅ Professional microservices architecture (FastAPI + Next.js)
- ✅ Type-safe frontend (TypeScript) with modern UI/UX
- ✅ Production-ready deployment patterns

**Kryptos-Niarad** remains archived for historical reference, but **all active development continues here**.

---

## `// FEATURES`

<table>
<tr>
<td width="50%">

**`MULTI-TOOL AGENT`**
> Ask anything. The agent searches the web, executes Python code, reads your documents, and generates PDFs/DOCX files on demand.

**`SPACED-REPETITION STUDY`**
> Generate flashcards from your vault. Review them with SM-2 scheduling. Weak spots automatically get drilled. Per-topic mastery dashboard.

**`INTELLIGENT INTENT CLASSIFIER`**
> LLM-powered query understanding. Replaces fragile keyword blocklists. Fails open to academic—legitimate coursework ("kill a process", "bomb calorimeter") never gets wrongly blocked.

</td>
<td width="50%">

**`LOCAL DOCUMENT VAULT`**
> Drop PDFs, lecture slides, notes (DOCX, PPTX, XLSX, CSV). Index them locally with FAISS. Query them forever—persist across sessions.

**`FULL-STACK MICROSERVICES`**
> Separate backend (FastAPI + LangChain ReAct) and frontend (Next.js 14 + TypeScript). Independent scaling, clean API contracts.

**`MASTERY DASHBOARD`**
> Real-time tracking of topic mastery. See which subjects need review. "Drill weak spots" pulls from your lowest-scoring topics.

</td>
</tr>
</table>

---

## `// TECH STACK`

| Layer | Technology |
|---|---|
| 🎨 **Frontend UI** | Next.js 14 · TypeScript · React · Tailwind CSS |
| 🔗 **Backend API** | FastAPI · LangChain ReAct · Python 3.10+ |
| 🧠 **LLM Inference** | Groq Cloud API (free tier) — `llama-3.1`, `mixtral`, etc. |
| 🤖 **Agent Tools** | Web search (DuckDuckGo) · Code execution · Document Q&A · PDF/DOCX generation |
| 🔢 **Embeddings** | HuggingFace (`all-MiniLM-L6-v2`) — runs locally |
| 🗄 **Vector Store** | FAISS (local disk persistence) |
| 📚 **Study Engine** | SM-2 spaced-repetition algorithm · SQLite (learning state) |
| 📄 **Document Parsing** | PyMuPDF · python-pptx · openpyxl · docx2txt |
| 🔐 **Environment** | python-dotenv (backend) · Next.js environment variables (frontend) |

---

## `// PROJECT STRUCTURE`

```text
niarad_agent/
├── backend/                  FastAPI · LangChain ReAct · Groq · FAISS · SM-2 (SQLite)
│   ├── core/
│   │   ├── agent.py         ReAct agent orchestration
│   │   ├── intent.py        LLM-based intent classifier
│   │   ├── srs.py           SM-2 spaced-repetition engine (~20 lines)
│   │   ├── flashcard_gen.py Auto-generate cards from vault text
│   │   ├── srs_routes.py    Study loop API endpoints
│   │   ├── loaders.py       File loading & chunking (PDF, DOCX, PPTX, XLSX, CSV)
│   │   └── vector_store.py  FAISS index management & embeddings
│   ├── tools/
│   │   ├── web_search.py    DuckDuckGo integration
│   │   ├── vault_search.py  RAG query against document index
│   │   ├── execute_code.py  Sandbox Python execution
│   │   └── generate_files.py PDF/DOCX export
│   ├── main.py              API entry point + all routers
│   ├── demo_srs.py          Offline demo (no API key needed)
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                Next.js 14 · TypeScript · React
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx       Root layout + theme provider
│   │   │   ├── globals.css      Design system (colors, fonts, spacing)
│   │   │   └── page.tsx         App shell (4-tab layout)
│   │   ├── components/
│   │   │   ├── Sidebar.tsx      Navigation & file upload
│   │   │   ├── ChatView.tsx     Ask the agent
│   │   │   ├── StudyView.tsx    Flashcard review & generation
│   │   │   ├── VaultView.tsx    Document list & management
│   │   │   ├── FilesView.tsx    Generated files download
│   │   │   ├── Flashcard.tsx    Card UI with warm paper design
│   │   │   └── MasteryRing.tsx  Radial mastery dashboard
│   │   └── lib/api.ts          Typed backend client (axios)
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   └── .env.local.example
│
└── design-preview.html      Open in browser to see UI design (no server needed)
```

---

## `// WHAT'S NEW VS. THE ORIGINAL KRYPTOS-NIARAD`

| Feature | Kryptos (Original) | NIARAD Agent (v3.0) |
|---|---|---|
| **Architecture** | Single Streamlit app | Full-stack microservices |
| **Frontend** | Streamlit UI | Next.js 14 + TypeScript |
| **Study Tools** | ❌ Basic Q&A only | ✅ Flashcards + SM-2 + Mastery dashboard |
| **Agent Capabilities** | ❌ None (RAG-only) | ✅ Web search + code execution + file generation |
| **Intent Filtering** | Keyword blocklist (fragile) | LLM-powered classifier (robust) |
| **UI/UX** | Functional prototype | Professional, intentional design |
| **Type Safety** | ❌ | ✅ TypeScript + Pydantic models |
| **API Surface** | ❌ (app-only) | ✅ REST + documented routes |
| **Deployment** | Streamlit Cloud | FastAPI anywhere + static Next.js |
| **Code Generation** | ❌ | ✅ Sandbox Python execution |
| **Document Export** | ❌ | ✅ PDF/DOCX generation |

---

## `// INSTALLATION & SETUP`

### Prerequisites

- **Python** 3.10+
- **Node.js** 18+ (for frontend)
- **Free Groq API key** (no credit card): https://console.groq.com

---

### 1 — Clone Repository

```bash
git clone https://github.com/AbdulGhaffarcs/niarad_agent.git
cd niarad_agent
```

---

### 2 — Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Paste your GROQ_API_KEY into .env
# GROQ_API_KEY=your_api_key_here

# Run backend
uvicorn main:app --reload   # http://localhost:8000
```

---

### 3 — Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.local.example .env.local

# Frontend points to http://localhost:8000 by default

# Run frontend
npm run dev                   # http://localhost:3000
```

---

### 4 — Try Offline Demo (No API Key)

```bash
cd backend
python demo_srs.py
```

This demonstrates the SM-2 study loop without any external dependencies.

---

## `// USAGE`

### **Ask (Agent Mode)**

1. Type any question in the chat
2. The agent automatically:
   - Searches the web if needed
   - Queries your document vault
   - Executes code if you ask
   - Generates files (PDF/DOCX) on request
3. See what tools it used via the "steps" breakdown

### **Study (Spaced Repetition Mode)**

1. Upload documents to your **Vault** tab
2. Go to **Study** → "Generate Cards" → pick a topic
3. **Review Due** shows cards you should review today
4. Grade each card 1–5; SM-2 automatically reschedules
5. Watch your mastery dashboard update

### **Vault (Document Management)**

1. Upload PDFs, DOCX, PPTX, XLSX, or CSV files
2. They're indexed locally into FAISS
3. All agent queries search this vault automatically
4. Clear anytime without losing your study progress

### **Files (Downloads)**

Download anything the agent generated (PDFs, DOCX, code output).

---

## `// SUPPORTED FILE TYPES`

```text
  .pdf    →  PyMuPDF loader (local text extraction)
  .docx   →  docx2txt
  .pptx   →  python-pptx (slide-by-slide)
  .xlsx   →  openpyxl (sheet-by-sheet)
  .csv    →  built-in csv reader
```

> ⚠ **Image-based / scanned PDFs** won't extract text. Use OCR-processed PDFs or convert with Ghostscript first.

---

## `// API SURFACE`

### Chat & Agents

```
POST   /chat                {message}              -> {response, mode, steps, intent}
GET    /chat/history        retrieve past conversations
```

### Vault (Documents)

```
POST   /vault/upload        (multipart file)       index document
GET    /vault/status                               list indexed docs + stats
DELETE /vault/clear                                wipe entire index
```

### Study (Flashcards & SM-2)

```
POST   /cards/generate      {topic, count, text?}  auto-create cards
GET    /cards/due           ?limit=&topic=         cards due today
POST   /cards/review        {card_id, grade 0-5}   log review + reschedule
POST   /cards/quiz_weak     {count}                drill lowest-scoring topics
GET    /cards/stats                                study progress
GET    /topics/weak         ?threshold=            topics below mastery %
```

### Files

```
GET    /files/list                                 generated files
GET    /files/{file_id}                            download file
```

---

## `// PERFORMANCE`

| Query Type | Inference | Speed |
|---|---|---|
| Greeting / small talk | None (LLM skipped) | ⚡ <0.5s |
| General question (no docs) | 1x Groq API | ⚡ ~1s |
| Document query (RAG) | 1x Groq API | ⚡ ~1.5s |
| Web search + agent | 1-3x Groq API | ⚡ ~3-5s |
| Vault sync / indexing | Local (CPU-bound) | Depends on file size |

**Hardware:** Runs comfortably on 2-4GB RAM. Older machines supported.

**Groq Free Tier:** 6,000 tokens/minute. Heavy use may hit rate limits (429). Wait a few seconds; no charges ever.

---

## `// TROUBLESHOOTING`

| Error | Fix |
|---|---|
| `ModuleNotFoundError: faiss` | Run `pip install faiss-cpu` |
| `Groq API 401` | Verify `GROQ_API_KEY` in `.env` is active + valid |
| `Next.js won't connect to backend` | Ensure FastAPI runs on `http://localhost:8000` and CORS is enabled |
| `No text extracted from PDF` | PDF might be scanned/image-based. Use OCR or text-based PDFs |
| `TypeError: 'NoneType'` in agent | Check intent classifier LLM calls; free tier might be rate-limited |
| `SQLite database locked` | Only one FastAPI worker can write to SRS DB at a time. Use 1 worker or upgrade storage. |

---

## `// LEARNING RESOURCES`

- **SM-2 Algorithm**: Original paper by Wozniak — efficient spaced repetition
- **FastAPI**: https://fastapi.tiangolo.com
- **LangChain ReAct**: https://python.langchain.com/docs/modules/agents/agent_types/react
- **Next.js 14**: https://nextjs.org/docs
- **FAISS**: https://github.com/facebookresearch/faiss

---

## `// PHILOSOPHY**

NIARAD is built on the conviction that students deserve:

1. **Intelligent assistance** — agents that understand context and reach across tools (web, code, documents)
2. **Scientifically-backed study** — SM-2 spaced repetition, not cramming
3. **Privacy** — documents stay local, embeddings local, only LLM inference goes to the cloud
4. **Zero vendor lock-in** — run it yourself, no subscriptions, no telemetry
5. **Beautiful, intentional design** — modern UI that respects your time and focus

---

<div align="center">

```text
NIARAD v3.0  //  FULL-STACK SUCCESSOR  //  PRODUCTION-READY  //  LOCALLY INTELLIGENT
```

**For historical reference, see [Kryptos-Niarad](https://github.com/AbdulGhaffarcs/Kryptos-Niarad) (archived).**

</div>
