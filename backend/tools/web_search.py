"""
tools/web_search.py
Web search tool using DuckDuckGo — no API key required.
"""

from langchain_core.tools import tool
from duckduckgo_search import DDGS


@tool
def web_search(query: str) -> str:
    """
    Search the web for current information.
    Use this when the user asks about recent events, news, or anything
    that may not be in the document vault or training data.
    Input: a search query string.
    Output: top search results with titles, URLs, and snippets.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        if not results:
            return "No results found for: " + query

        output = "Web search results for: " + query + "\n\n"
        for i, r in enumerate(results, 1):
            output += (
                str(i) + ". " + r.get("title", "No title") + "\n"
                "   URL: " + r.get("href", "") + "\n"
                "   " + r.get("body", "No snippet") + "\n\n"
            )
        return output.strip()
    except Exception as e:
        return "Web search failed: " + str(e)
