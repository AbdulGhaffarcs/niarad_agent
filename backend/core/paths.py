"""
Runtime paths for local and Hugging Face Space deployments.
"""

import os


def _default_data_dir() -> str:
    if os.getenv("SPACE_ID"):
        return "/data"
    return "."


DATA_DIR = os.getenv("NIARAD_DATA_DIR", _default_data_dir())
FAISS_DIR = os.getenv("NIARAD_FAISS_DIR", os.path.join(DATA_DIR, "faiss_index"))
GENERATED_FILES_DIR = os.getenv(
    "NIARAD_GENERATED_FILES_DIR",
    os.path.join(DATA_DIR, "generated_files"),
)
UPLOADS_DIR = os.getenv("NIARAD_UPLOADS_DIR", os.path.join(DATA_DIR, "uploads"))
SRS_DB_PATH = os.getenv("NIARAD_SRS_DB", os.path.join(DATA_DIR, "niarad_srs.db"))


def ensure_runtime_dirs() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(FAISS_DIR, exist_ok=True)
    os.makedirs(GENERATED_FILES_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(SRS_DB_PATH) or ".", exist_ok=True)
