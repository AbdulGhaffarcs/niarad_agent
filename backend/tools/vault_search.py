"""
tools/vault_search.py
Document vault search tool — queries the FAISS vector store.
"""

from langchain_core.tools import tool


@tool
def vault_search(query: str) -> str:
    """
    Search the user's uploaded documents for relevant information.
    Use this when the user asks about their study material, lecture notes,
    exam papers, schedules, or any uploaded files.
    Input: a search query string.
    Output: relevant passages from the documents.
    """
    try:
        from core.vector_store import get_vector_store
        db = get_vector_store()

        if db is None:
            return "No documents in vault. Ask the user to upload files first."

        docs = db.similarity_search(query, k=4)

        if not docs:
            return "No relevant content found in vault for: " + query

        output = "Relevant content from your documents:\n\n"
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown")
            source = source.split("\\")[-1].split("/")[-1]  # filename only
            slide = doc.metadata.get("slide", "")
            sheet = doc.metadata.get("sheet", "")
            loc = (" — Slide " + str(slide)) if slide else (" — Sheet " + str(sheet)) if sheet else ""
            output += str(i) + ". [" + source + loc + "]\n"
            output += doc.page_content[:500] + "\n\n"

        return output.strip()
    except Exception as e:
        return "Vault search failed: " + str(e)
