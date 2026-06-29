# 🛍️ Store Customer Support AI Agent
### Built with Gemini + LangGraph

An AI agent that answers customer questions about an online store — intelligently selecting tools, chaining them when required, and returning customer-friendly responses.

Built with **LangGraph** for a production-ready, extensible architecture — not just a script.

---

## 📁 Project Structure

```
store_agent/
│
├── agent.py          # LangGraph graph — core agent logic
├── tools.py          # Tool functions with @tool decorator
├── database.py       # Mock data store (Python dictionaries)
├── app.py            # Streamlit web interface
├── requirements.txt  # Dependencies
├── agent.log         # Auto-generated tool call logs
└── README.md
```

---

## 🔀 Agent Graph

```
START
  ↓
[call_llm]  ←──────────────────┐
  ↓                            │
should_continue?               │
  ↙            ↘              │
END       [execute_tools] ─────┘
```

- **call_llm** — Sends conversation to Claude. Claude decides which tool(s) to call.
- **execute_tools** — LangGraph's `ToolNode` executes the requested tools automatically.
- **should_continue** — Routing function. If Claude made tool calls → loop back. If final answer → END.

---

## ⚙️ Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY=your_key_here

# Run agent in terminal
python agent.py

# Run Streamlit UI
streamlit run app.py
```

---

## 🤖 Available Tools

| Tool | When Claude uses it |
|------|-------------------|
| `get_order(order_id)` | Customer asks about order status, shipping, ETA |
| `search_products(query)` | Customer wants to browse or find alternatives |
| `get_product(product_id)` | Need full details of a specific product |

---

## 💬 Sample Inputs & Outputs

**Q: Where is my order ORD-1002?**
```
Your order ORD-1002 (Nike Air Max 270) has been shipped 
and is expected to arrive in 2 days! 🚚
```

**Q: Is there a cheaper alternative to the shoes in ORD-1002?**
```
Your order ORD-1002 contains Nike Air Max 270 at ₹7,499.

Here are cheaper alternatives:
• Puma Running Shoes — ₹3,499 ⭐ 4.2 (In Stock)
• Reebok Classic Leather Shoes — ₹4,999 ⭐ 4.3 (In Stock)

Puma would save you ₹4,000!
```

**Q: Where is order ORD-9999?**
```
I'm sorry, I couldn't find order ORD-9999. 
Please double-check your order ID and try again.
```

---

## ✅ Features

- **LangGraph state graph** — extensible, production-ready agent architecture
- **Tool chaining** — Claude chains multiple tools automatically when needed
- **Error handling** — graceful responses for invalid orders, products, empty searches
- **Logging** — every tool call logged with timestamp to `agent.log`
- **Streamlit UI** — chat interface with sample questions and agent flow diagram
- **LLM** — Claude (claude-sonnet-4-6) via LangChain-Anthropic

---

## 🏗️ Why LangGraph?

| | Simple While Loop | LangGraph |
|---|---|---|
| Add new agent tomorrow | Refactor entire loop | Add one node + one edge |
| Observability | print() statements | LangSmith dashboard ready |
| State management | Local variables | Explicit, typed AgentState |
| Production ready | No | Yes |

LangGraph makes the agent **extensible by design**. Adding a refund agent, a recommendation agent, or human-in-the-loop approval is just adding nodes — nothing else changes.

---

## 🔮 How to Extend (Production Roadmap)

```python
# Add a refund agent node tomorrow — nothing else changes
graph.add_node("refund_agent", handle_refund)
graph.add_conditional_edges("call_llm", router, {
    "execute_tools": "execute_tools",
    "refund_agent": "refund_agent",  # ← just this line
    END: END
})
```

Other extensions:
- Swap dictionary data with PostgreSQL or Shopify API
- Add LangSmith for full tracing and observability
- Add memory node for multi-turn conversation history
- Deploy as FastAPI microservice
