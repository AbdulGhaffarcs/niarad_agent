# CHANGELOG — NIARAD Evolution

All notable changes and milestones in the NIARAD project are documented here.

---

## **[v3.0] — 2026-07-03 — Full-Stack Rewrite** ✨

### **Architecture Overhaul**

- ✅ Migrated from single-file Streamlit app → full-stack microservices
- ✅ Backend: FastAPI + LangChain ReAct with proper separation of concerns
- ✅ Frontend: Next.js 14 with TypeScript, replacing Streamlit UI
- ✅ RESTful API surface with documented endpoints
- ✅ Support for independent backend/frontend deployment

### **New Features**

#### **Multi-Tool Agents**
- 🔍 Web search integration (DuckDuckGo)
- 💻 Sandbox Python code execution
- 📄 PDF/DOCX file generation from agent responses
- 🎯 LLM-powered intent classification (replaces keyword blocklists)

#### **Spaced-Repetition Study System**
- 📚 SM-2 algorithm implementation for scientifically-backed study
- 🎴 Auto-generate flashcards from document vault
- 📊 Per-topic mastery dashboard with visual progress tracking
- 🔄 Automatic card rescheduling based on review performance
- 💪 "Drill weak spots" feature to focus on problem areas

#### **Professional UI/UX**
- 🎨 Modern, intentional design with warm paper flashcard aesthetic
- 📑 Four-tab interface: Ask / Study / Vault / Files
- 🎯 Mastery ring visualization for progress tracking
- 📱 Responsive design built with Tailwind CSS
- 🔤 Professional typography (Fraunces, Inter, JetBrains Mono)

#### **Type Safety & Developer Experience**
- ✅ Full TypeScript support on frontend
- ✅ Pydantic models on backend
- ✅ Typed API client (`lib/api.ts`)
- ✅ Build verification (`tsc --noEmit`, `next build`)

### **Technical Improvements**

| Aspect | v2 (Kryptos) | v3 (niarad_agent) |
|---|---|---|
| Architecture | Monolith | Microservices |
| Frontend | Streamlit (Python) | Next.js (TypeScript) |
| API | None (app-only) | REST API |
| Query Routing | Keyword heuristic | LLM classifier |
| Study Tools | ❌ | ✅ SM-2 + Flashcards |
| Code Execution | ❌ | ✅ Sandbox |
| File Export | ❌ | ✅ PDF/DOCX |
| Web Search | ❌ | ✅ DuckDuckGo |
| Type Safety | ❌ | ✅ TypeScript + Pydantic |

### **Database & Storage**

- SQLite backend for SM-2 study state (ready for multi-user with `user_id` column)
- FAISS index for document embeddings (persists across sessions)
- Structured storage of generated files for download

### **Migration Notes**

- **Kryptos-Niarad** archived with migration notice
- FAISS index format compatible (can import old vaults)
- Study progress must be manually recreated or exported

---

## **[v2.1] — 2026-03-28 — Cloud-Optimized RAG** 🚀

### **Release Highlights**

- ✅ Cloud LPU inference via Groq API
- ✅ Local FAISS vector store with HuggingFace embeddings
- ✅ Streamlit UI with dark theme
- ✅ Multi-format document support (PDF, DOCX, PPTX, XLSX, CSV)
- ✅ Keyword-based query routing (EXTRACTION vs. SYNTHESIS)
- ✅ Small talk detection for instant responses
- ✅ LangChain RAG pipeline

### **Features**

- 📄 **Document Upload & Indexing** — Upload and persist documents to FAISS
- 🎯 **Extraction Mode** — Pull specific facts, dates, tables from documents
- 📝 **Synthesis Mode** — Summarize lecture slides and notes
- ⚡ **Fast Routing** — Keyword heuristic classifies queries before LLM inference
- 💬 **Small Talk** — Greetings bypass RAG for instant responses
- 🔒 **Privacy** — Documents indexed locally, only inference goes to cloud

### **Technology Stack**

- **UI:** Streamlit
- **RAG:** LangChain
- **Vector Store:** FAISS (local)
- **Embeddings:** HuggingFace `all-MiniLM-L6-v2`
- **Inference:** Groq Cloud API (LLaMA 3.1, Mixtral)
- **Document Parsing:** PyMuPDF, python-pptx, openpyxl, docx2txt
- **Storage:** python-dotenv, .gitignore

### **Performance**

- Small talk responses: ~0.5s (no LLM call)
- General questions: ~1s
- Document queries: ~1.5s
- RAM requirement: 1-2GB (minimal)

### **Known Limitations**

- Keyword-based routing fragile (can block legitimate queries)
- No study/learning features
- Single Streamlit UI (no API)
- Scaling limited by monolithic architecture

---

## **[v2.0] — Initial Release** 🎉

### **Concept**

NIARAD (originally "Kryptos-Niarad") — an offline AI study assistant powered by local LLMs and RAG.

### **Core Features**

- Basic RAG pipeline for document Q&A
- Local FAISS indexing
- Streamlit UI for user interaction
- Cloud-based inference to reduce local resource requirements

---

## **Timeline**

```
March 5, 2026    → Kryptos-Niarad (v2.0) initialized
March 28, 2026   → v2.1 released (cloud LPU, full feature set)
July 2, 2026     → niarad_agent development begins
July 3, 2026     → v3.0 released (full-stack rewrite, production-ready)
```

---

## **Future Roadmap (v3.1+)**

- [ ] **Multi-user support** — Add `user_id` to SM-2 database schema
- [ ] **Advanced scheduling** — SM-2 variants (e.g., SuperMemo 17)
- [ ] **Collaborative vaults** — Share document sets with study groups
- [ ] **Mobile frontend** — React Native companion app
- [ ] **Plugin system** — Custom tools beyond web search/code/docs
- [ ] **Analytics dashboard** — Learning trends and performance metrics
- [ ] **Offline mode** — Optional offline LLM (Ollama) fallback
- [ ] **Database scaling** — PostgreSQL option for production deployments
- [ ] **Export formats** — Anki, Quizlet, CSV export for study cards
- [ ] **Vision support** — OCR for scanned documents and image uploads

---

## **Project Evolution Philosophy**

> NIARAD evolved from a rapid prototype (Streamlit RAG) into a production-grade system because:
>
> 1. **Scope expanded** — Beyond Q&A to include scientifically-backed study loops
> 2. **Quality expectations increased** — From "works locally" to "deployable anywhere"
> 3. **Architecture mattered** — Monolith created friction; microservices enabled parallel development
> 4. **UX became critical** — Students deserve beautiful, intentional interfaces, not prototype forms
> 5. **Type safety reduced bugs** — TypeScript + Pydantic provided confidence for complex features

This is the natural progression of a project that started as a weekend hack and matured into a tool worth maintaining long-term.

---

## **Versions at a Glance**

| Version | Year | Architecture | UI | Study Features | API |
|---|---|---|---|---|---|
| **v2.0–2.1** | 2026-03 | Single Streamlit app | Streamlit | ❌ None | ❌ No |
| **v3.0** | 2026-07 | FastAPI + Next.js | React + TS | ✅ SM-2 Flashcards | ✅ REST API |
| **v3.1+** | TBD | Microservices | React + Mobile | ✅ Multi-user | ✅ GraphQL (planned) |

---

**Last Updated:** July 3, 2026
**Maintained by:** AbdulGhaffarcs
