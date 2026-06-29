
import streamlit as st
from agent import run_agent, app   # app is the compiled LangGraph graph

st.set_page_config(
    page_title="Store Assistant",
    page_icon="🛍️",
    layout="centered"
)

st.title("🛍️ Store Customer Assistant")
st.caption("Powered by Claude + LangGraph")

# ---- Sidebar ----
with st.sidebar:
    st.header("💡 Try These")
    samples = [
        "Where is my order ORD-1002?",
        "Is there a cheaper alternative to shoes in ORD-1002?",
        "Show me headphones under ₹5000",
        "What is the status of ORD-1003?",
        "Do you have running shoes?",
        "Where is order ORD-9999?",
    ]
    for q in samples:
        if st.button(q, use_container_width=True):
            st.session_state.prefill = q

    st.divider()



    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---- Chat History ----
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---- Handle sidebar prefill ----
prefill = st.session_state.pop("prefill", "")

# ---- Chat Input ----
user_input = st.chat_input("Ask about your order or search for products...")
if prefill and not user_input:
    user_input = prefill

if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = run_agent(user_input)[0]
            response = response["text"]
        st.write(response)

    st.session_state.messages.append({"role": "assistant", "content": response})