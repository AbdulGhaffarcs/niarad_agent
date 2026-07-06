"""
NIARAD Agent Backend — FastAPI
v3.1.0 — adds spaced-repetition / flashcard loop (core.srs_routes)
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import tempfile, os
from dotenv import load_dotenv

from core.srs_routes import router as srs_router  # NEW

load_dotenv()

app = FastAPI(title="NIARAD Agent API", version="3.1.0")

frontend_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://niarad-frontend.vercel.app",  # Update with your actual Vercel URL
        *frontend_origins,
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("./generated_files", exist_ok=True)
app.mount("/files", StaticFiles(directory="./generated_files"), name="files")

app.include_router(srs_router)  # NEW — /cards/* and /topics/* endpoints


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    response: str
    mode: str
    steps: list = []
    intent: dict | None = None  # NEW — classifier decision, useful for UI/debug


@app.get("/")
def root():
    return {"status": "NIARAD Agent API online", "version": "3.1.0"}


@app.get("/vault/status")
def vault_status():
    from core.vector_store import get_vector_store
    db = get_vector_store()
    if db is None:
        return {"has_docs": False, "doc_count": 0}
    try:
        count = db.index.ntotal
    except Exception:
        count = 0
    return {"has_docs": True, "doc_count": count}


@app.post("/vault/upload")
async def upload_file(file: UploadFile = File(...)):
    from core.loaders import load_file_dynamically, get_chunks, is_already_indexed, mark_as_indexed
    from core.vector_store import add_to_store

    suffix = os.path.splitext(file.filename)[1].lower()
    allowed = {".pdf", ".docx", ".pptx", ".xlsx", ".csv"}
    if suffix not in allowed:
        raise HTTPException(400, "Unsupported file type: " + suffix)

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        if is_already_indexed(tmp_path):
            return {"success": True, "filename": file.filename, "skipped": True,
                    "message": "Already indexed"}
        docs = load_file_dynamically(tmp_path)
        chunks = get_chunks(docs)
        add_to_store(chunks)
        mark_as_indexed(tmp_path)
        return {"success": True, "filename": file.filename,
                "chunks": len(chunks), "pages": len(docs), "skipped": False}
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        os.unlink(tmp_path)


@app.delete("/vault/clear")
def clear_vault():
    from core.vector_store import clear_store
    clear_store()
    return {"success": True}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    from core.agent import run_agent
    history = [{"role": m.role, "content": m.content} for m in req.history]
    result = await run_agent(req.message.strip(), history=history)
    return ChatResponse(
        response=result["response"],
        mode=result["mode"],
        steps=result.get("steps", []),
        intent=result.get("intent"),
    )


@app.get("/files/list")
def list_files():
    files_dir = "./generated_files"
    if not os.path.exists(files_dir):
        return {"files": []}
    files = [{"name": f, "url": "/files/" + f}
             for f in os.listdir(files_dir) if f.endswith((".pdf", ".docx"))]
    return {"files": files}
