# Design Decisions — Store Customer Support AI Agent

**Stack:** Gemini + LangGraph + LangChain + Streamlit

---

## 1. Why LangGraph Instead of a Simple Loop

The assignment can be solved with a basic `while True` loop. But that approach has a fundamental problem — it doesn't scale.

LangGraph models the agent as a **directed graph of nodes and edges**. Each node does one thing. Routing between nodes is explicit and testable. Adding new capabilities tomorrow means adding a new node — nothing else changes.

With a while loop, adding a refund agent or recommendation agent means refactoring the entire function. With LangGraph, it's one `add_node` and one `add_edge` call.

This is the difference between writing code that works and writing code that *lasts*.

---

## 2. State — `AgentState` with `add_messages`

LangGraph requires explicit state definition. The `AgentState` uses `Annotated[list, add_messages]` for the messages field.

`add_messages` is a **reducer** — instead of overwriting the message list on each node, it appends. This means the full conversation history is always preserved and passed to gemini on every LLM call, enabling natural multi-turn reasoning.

---

## 3. Tools — `@tool` Decorator (LangChain)

Tools are defined using LangChain's `@tool` decorator instead of raw JSON schemas. Benefits:

- The **docstring becomes the tool description** gemini reads — clean and co-located with the function
- LangGraph's built-in `ToolNode` handles execution automatically — no manual routing needed
- Type hints define the input schema — no separate JSON to maintain

---

## 4. ToolNode — Zero Boilerplate Tool Execution

LangGraph's `ToolNode` reads `tool_calls` from the last LLM message, finds the matching function, executes it, and returns results — all automatically. This eliminates the manual `if tool_name == "get_order": ...` routing that a simple loop requires.

---

## 5. Error Handling at the Tool Level

Each tool returns a structured `{"error": "..."}` dict on invalid input instead of raising exceptions. gemini reads this error and translates it into a polite customer-facing message — preventing hallucination and raw error dumps reaching the user.

---

## 6. Data Layer — Dictionaries, Cleanly Separated

Mock data lives in `database.py`, completely separate from tool logic in `tools.py`. The tools only import from `database.py`. Swapping to a real PostgreSQL database or Shopify REST API only requires changing `database.py` — zero changes to the agent or tools.

---

## 7. Logging

Python's built-in `logging` module records every tool call — name, input, and result — with timestamps to both console and `agent.log`. In production this would feed into LangSmith for full graph-level tracing.

---

## 8. Production Roadmap

This architecture is genuinely production-ready with these additions:
- Replace dict data with PostgreSQL / Shopify API
- Add LangSmith for observability (`LANGCHAIN_TRACING_V2=true`)
- Add a memory node for persistent conversation history
- Wrap `run_agent` in a FastAPI endpoint for deployment
- Add human-in-the-loop node for escalation to human agents
