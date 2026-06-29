import os
import logging
from typing import Annotated

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

from tools import TOOLS
import time
import streamlit as st

try:
    # Running on Streamlit Cloud
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    # Running locally
    api_key = os.getenv("GEMINI_API_KEY")
    st.write("Loaded from environment:", api_key is not None)


# LOGGING SETUP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("agent.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# SYSTEM PROMPT

Sys_prompt = """You are a helpful and friendly customer support agent for an online store.

Your job is to answer customer questions accurately using the tools available to you.

RULES YOU MUST FOLLOW:
1. Always use tools to fetch real data — never guess or make up information
2. If an order or product is not found, tell the customer clearly and politely
3. If search returns no results, say so — do not suggest products that don't exist
4. Chain multiple tool calls when needed (e.g. get order → then get product details)
5. Always give customer-friendly responses — no raw data dumps, no technical jargon
6. Keep responses concise but complete — answer exactly what was asked
7. If the customer asks for cheaper alternatives, search and compare prices clearly
8. Always mention prices in ₹ (Indian Rupees) format

TONE: Friendly, helpful, and professional — like a real customer support executive."""


# STATE DEFINITION

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# LLM SETUP

llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    google_api_key=api_key
)

llm_with_tools = llm.bind_tools(TOOLS)


# NODE 1 — call_llm

def call_llm(state: AgentState) -> AgentState:
    logger.info("[NODE] call_llm")

    time.sleep(1)
    print("llm_call")

    # Prepend system message on every LLM call
    messages = [SystemMessage(content=Sys_prompt)] + state["messages"]

    response = llm_with_tools.invoke(messages)

    logger.info(
        f"[LLM RESPONSE] tool_calls={len(response.tool_calls) if hasattr(response, 'tool_calls') and response.tool_calls else 0}")

    return {"messages": [response]}


# NODE 2 — execute_tools (ToolNode)

tool_node = ToolNode(TOOLS)


# ROUTING FUNCTION

def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        logger.info(f"[ROUTING] Tool calls detected → execute_tools")
        return "execute_tools"

    logger.info("[ROUTING] No tool calls → END")
    return END


# BUILD THE GRAPH

def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("call_llm", call_llm)
    graph.add_node("execute_tools", tool_node)

    # Entry point
    graph.set_entry_point("call_llm")

    # Conditional edge from call_llm
    graph.add_conditional_edges(
        "call_llm",
        should_continue,
        {
            "execute_tools": "execute_tools",
            END: END
        }
    )

    graph.add_edge("execute_tools", "call_llm")

    return graph.compile()


# Compile
app = build_graph()


# run_agent

def run_agent(question: str) -> str:
    """
    Takes a customer question, runs it through the LangGraph agent,
    and returns a customer-friendly response string.
    """
    logger.info(f"{'=' * 60}")
    logger.info(f"[AGENT START] {question}")

    if not question or not question.strip():
        return "I didn't receive a question. Could you please ask me something?"

    initial_state = {
        "messages": [HumanMessage(content=question.strip())]
    }

    final_state = app.invoke(initial_state)

    final_answer = final_state["messages"][-1].content

    logger.info(f"[AGENT END] {final_answer}")
    logger.info(f"{'=' * 60}")

    return final_answer


# QUICK TEST

if __name__ == "__main__":
    questions = [
        "Where is my order ORD-1002?",
        "Is there a cheaper alternative to the shoes in ORD-1002?",

    ]

    for q in questions:
        print(f"Que: {q}")
        ans = run_agent(q)[0]
        print(f"Ans: {ans['text']}")
