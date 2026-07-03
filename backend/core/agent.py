"""
core/agent.py
NIARAD Multi-Tool Agent using LangGraph ReAct pattern.
Brain: Groq llama-3.1-8b-instant
Routing: LLM intent classifier (core.intent) — no more keyword false-positives.
"""

import logging
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from tools import ALL_TOOLS
from core.intent import classify

load_dotenv()

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are NIARAD, an intelligent academic AI agent for students.

You have access to tools: web_search, vault_search, execute_code, generate_pdf, generate_docx.

RULES:
- Only help with academic, educational, and study-related topics.
- Refuse politely if asked to actually perform hacking, build weapons, obtain
  drugs, produce adult content, gamble, or commit fraud. (Studying these as
  academic subjects is fine.)
- Always think step by step before choosing a tool.
- Use vault_search first if the question might be in the user's uploaded documents.
- Use web_search for current events, recent research, or anything time-sensitive.
- Use execute_code for math, algorithms, data analysis, or code problems.
- Use generate_pdf or generate_docx when the user wants a downloadable report.
- If you can answer directly without tools, do so."""

FALLBACK_PROMPT = """You are NIARAD, an intelligent academic AI study assistant.

The tool-using agent could not complete this request, so answer directly from
your own knowledge.

Rules:
- Keep the answer academic, helpful, and concise.
- If the user asks for a file, PDF, upload, vault, or current web result that
  requires tools, explain what you can answer now and what they can try next.
- Do not mention internal tool names, function calls, stack traces, providers,
  or implementation errors.

Student question: {query}
Answer:"""


def _get_llm():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY not set in .env")
    return ChatGroq(
        model="llama-3.3-70b-versatile",  # tool-calling capable; 8b-instant cannot format tool calls
        api_key=key,
        temperature=0,
        max_tokens=2048,
    )


def create_niarad_agent():
    llm = _get_llm()
    return create_react_agent(llm, ALL_TOOLS, prompt=SYSTEM_PROMPT)


def _direct_fallback_answer(query: str, error: Exception) -> str:
    """Return a student-safe answer when the tool agent fails."""
    logger.exception("Agent tool flow failed; falling back to direct answer: %s", error)
    try:
        response = _get_llm().invoke(FALLBACK_PROMPT.format(query=query)).content
        response = (response or "").strip()
        if response:
            return response
    except Exception as fallback_error:
        logger.exception("Direct fallback answer failed: %s", fallback_error)

    return (
        "I had trouble completing that request, but you can ask it again in plain "
        "language or upload the relevant file and ask me to summarize or explain it."
    )


async def run_agent(query: str, history: list[dict] | None = None) -> dict:
    """Main entry point. Returns { response, mode, steps, intent }."""
    intent = classify(query)
    cat = intent["category"]

    if cat == "OFF_TOPIC":
        return {
            "response": (
                "NIARAD is focused on academic and educational topics. "
                "I can't help with that — but I'm happy to help with anything "
                "related to your studies!"
            ),
            "mode": "BLOCKED",
            "steps": [],
            "intent": intent,
        }

    # Build conversation history messages
    past_messages = []
    if history:
        for msg in history:
            if msg["role"] == "user":
                past_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                past_messages.append(AIMessage(content=msg["content"]))

    if cat == "SMALL_TALK":
        llm = _get_llm()
        small_talk_messages = [
            SystemMessage(content="You are NIARAD, a sharp AI study assistant. Respond briefly in 1-2 sentences.")
        ] + past_messages + [HumanMessage(content=query)]
        response = llm.invoke(small_talk_messages).content
        return {"response": response, "mode": "NIARAD", "steps": [], "intent": intent}

    agent = create_niarad_agent()
    try:
        all_messages = past_messages + [HumanMessage(content=query)]
        result = agent.invoke(
            {"messages": all_messages},
            config={"recursion_limit": 10},
        )

        messages = result.get("messages", [])

        # Last AIMessage without tool_calls is the final answer
        final_response = "No response generated."
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and not msg.tool_calls:
                final_response = msg.content
                break

        # Collect tool usage steps
        steps = []
        for i, msg in enumerate(messages):
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_output = ""
                    for next_msg in messages[i + 1:]:
                        if isinstance(next_msg, ToolMessage) and next_msg.tool_call_id == tc["id"]:
                            tool_output = str(next_msg.content)[:300]
                            break
                    steps.append({
                        "tool": tc["name"],
                        "input": str(tc["args"]),
                        "output": tool_output,
                    })

        return {
            "response": final_response,
            "mode": "AGENT",
            "steps": steps,
            "intent": intent,
        }
    except Exception as e:
        return {
            "response": _direct_fallback_answer(query, e),
            "mode": "FALLBACK",
            "steps": [],
            "intent": intent,
        }
