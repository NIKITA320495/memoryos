# app.py  — MemoryOS Streamlit Interface
# Run: streamlit run app.py

import streamlit as st
import json
import sys
import os
import time
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.tools import (
    tool_store_memory,
    tool_search_memory,
    tool_list_memories,
    tool_delete_memory,
    tool_update_memory,
    tool_get_memory,
)
from dotenv import load_dotenv
load_dotenv()

OLLAMA_URL   = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MemoryOS",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:       #0a0a0f;
    --surface:  #111118;
    --border:   #1e1e2e;
    --accent:   #7c6af7;
    --accent2:  #4fd1c7;
    --text:     #e8e8f0;
    --muted:    #6b6b80;
    --success:  #4ade80;
    --warning:  #fbbf24;
    --danger:   #f87171;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem; max-width: 1400px; }

/* sidebar */
[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* metric cards */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    text-align: center;
    transition: border-color .2s;
}
.metric-card:hover { border-color: var(--accent); }
.metric-val {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent);
}
.metric-lbl {
    font-size: .75rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: .08em;
    margin-top: 4px;
}

/* memory cards */
.memory-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: .75rem;
    transition: border-color .2s, transform .15s;
}
.memory-card:hover {
    border-left-color: var(--accent2);
    transform: translateX(2px);
}
.memory-text { font-size: .9rem; line-height: 1.6; color: var(--text); }
.memory-meta {
    font-family: 'Space Mono', monospace;
    font-size: .7rem;
    color: var(--muted);
    margin-top: .5rem;
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}
.tag {
    background: rgba(124,106,247,.15);
    color: var(--accent);
    border: 1px solid rgba(124,106,247,.3);
    border-radius: 99px;
    padding: 1px 8px;
    font-size: .68rem;
}
.importance-bar {
    height: 4px;
    background: var(--border);
    border-radius: 99px;
    margin-top: .6rem;
    overflow: hidden;
}
.importance-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}

/* chat bubbles */
.chat-user {
    background: rgba(124,106,247,.12);
    border: 1px solid rgba(124,106,247,.25);
    border-radius: 12px 12px 4px 12px;
    padding: .75rem 1rem;
    margin: .5rem 0 .5rem 3rem;
    font-size: .9rem;
}
.chat-agent {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px 12px 12px 4px;
    padding: .75rem 1rem;
    margin: .5rem 3rem .5rem 0;
    font-size: .9rem;
    line-height: 1.7;
}
.chat-tool {
    background: rgba(79,209,199,.06);
    border: 1px solid rgba(79,209,199,.2);
    border-radius: 8px;
    padding: .5rem .75rem;
    margin: .25rem 1rem;
    font-family: 'Space Mono', monospace;
    font-size: .72rem;
    color: var(--accent2);
}

/* logo */
.logo {
    font-family: 'Space Mono', monospace;
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: -.02em;
}
.logo span { color: var(--accent); }

/* section headers */
.section-header {
    font-family: 'Space Mono', monospace;
    font-size: .7rem;
    text-transform: uppercase;
    letter-spacing: .12em;
    color: var(--muted);
    border-bottom: 1px solid var(--border);
    padding-bottom: .5rem;
    margin-bottom: 1rem;
}

/* status dot */
.dot-green { color: var(--success); }
.dot-red   { color: var(--danger); }

/* stButton */
div.stButton > button {
    background: var(--accent);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    padding: .4rem 1.2rem;
    transition: opacity .2s, transform .1s;
}
div.stButton > button:hover {
    opacity: .88;
    transform: translateY(-1px);
}
div.stButton > button:active { transform: translateY(0); }

/* inputs */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] select {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}

/* slider */
div[data-testid="stSlider"] div[role="slider"] {
    background: var(--accent) !important;
}

/* tabs */
div[data-testid="stTabs"] button {
    font-family: 'Space Mono', monospace;
    font-size: .75rem;
    color: var(--muted) !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

div.stAlert { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_id" not in st.session_state:
    st.session_state.user_id = "user_001"
if "tool_calls" not in st.session_state:
    st.session_state.tool_calls = []

# ── Helpers ────────────────────────────────────────────────────────────────────
def check_ollama() -> bool:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        models = [m["name"] for m in r.json().get("models", [])]
        return any(OLLAMA_MODEL in m for m in models)
    except Exception:
        return False

def ask_ollama(system_prompt: str, user_message: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ]
    }
    try:
        r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=60)
        return r.json()["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ Ollama error: {e}. Make sure Ollama is running (`ollama serve`)."

def memory_agent(user_input: str, user_id: str) -> tuple[str, list[dict]]:
    """Returns (response, list_of_tool_calls)"""
    calls = []

    # 1. search memory
    calls.append({"tool": "search_memory", "input": {"query": user_input, "user_id": user_id}})
    search_raw = tool_search_memory(query=user_input, user_id=user_id, top_k=3)
    search_result = json.loads(search_raw)
    calls[-1]["output"] = search_result

    memories = search_result.get("results", [])
    context = "\n".join([f"- {m['text']}" for m in memories]) if memories else "No prior memories."

    system_prompt = f"""You are a memory-powered AI assistant.
You have access to the user's long-term memory retrieved from a vector database.

RETRIEVED MEMORIES:
{context}

Use this to give personalised, context-aware responses.
Be warm, concise, and reference specific memories when relevant."""

    # 2. generate response
    response = ask_ollama(system_prompt, user_input)

    # 3. store interaction
    calls.append({"tool": "store_memory", "input": {"text": f"User said: {user_input}", "user_id": user_id}})
    store_raw = tool_store_memory(
        text=f"User said: {user_input}",
        user_id=user_id,
        tags=["chat"],
        importance=5
    )
    calls[-1]["output"] = json.loads(store_raw)

    return response, calls

def render_importance(score: int):
    pct = score * 10
    color = "#4ade80" if score >= 8 else "#fbbf24" if score >= 5 else "#f87171"
    return f"""
    <div class="importance-bar">
      <div class="importance-fill" style="width:{pct}%; background:{color};"></div>
    </div>"""

def render_memory_card(m: dict, show_delete=True):
    tags_html = " ".join([f'<span class="tag">{t}</span>' for t in m.get("tags", [])])
    created   = m.get("created_at", "")[:16].replace("T", " ")
    imp       = m.get("importance", 5)
    imp_bar   = render_importance(imp)
    st.markdown(f"""
    <div class="memory-card">
      <div class="memory-text">{m['text']}</div>
      {imp_bar}
      <div class="memory-meta">
        <span>🕐 {created}</span>
        <span>⚡ {imp}/10</span>
        <span>{tags_html}</span>
      </div>
    </div>""", unsafe_allow_html=True)
    if show_delete:
        if st.button("🗑 Delete", key=f"del_{m['id']}"):
            json.loads(tool_delete_memory(m["id"]))
            st.rerun()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="logo">Memory<span>OS</span></div>', unsafe_allow_html=True)
    st.markdown("*Persistent memory layer for LLM agents*")
    st.divider()

    # user id
    st.markdown('<div class="section-header">Identity</div>', unsafe_allow_html=True)
    user_id = st.text_input("User ID", value=st.session_state.user_id, label_visibility="collapsed", placeholder="Enter user ID...")
    if user_id != st.session_state.user_id:
        st.session_state.user_id = user_id
        st.session_state.chat_history = []
        st.rerun()

    st.divider()

    # ollama status
    st.markdown('<div class="section-header">System Status</div>', unsafe_allow_html=True)
    ollama_ok = check_ollama()
    if ollama_ok:
        st.markdown(f'<span class="dot-green">● Ollama</span> `{OLLAMA_MODEL}`', unsafe_allow_html=True)
    else:
        st.markdown('<span class="dot-red">● Ollama offline</span>', unsafe_allow_html=True)
        st.caption("Run: `ollama serve`")

    # memory stats
    try:
        all_mem = json.loads(tool_list_memories(st.session_state.user_id))
        mem_count = all_mem["count"]
        memories  = all_mem["memories"]
        avg_imp   = round(sum(m["importance"] for m in memories) / mem_count, 1) if mem_count else 0
    except Exception:
        mem_count, memories, avg_imp = 0, [], 0

    st.divider()
    st.markdown('<div class="section-header">Memory Stats</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{mem_count}</div><div class="metric-lbl">Memories</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{avg_imp}</div><div class="metric-lbl">Avg Imp.</div></div>', unsafe_allow_html=True)

    st.divider()

    # danger zone
    st.markdown('<div class="section-header">Danger Zone</div>', unsafe_allow_html=True)
    if st.button("🗑 Clear All Memories", use_container_width=True):
        for m in memories:
            tool_delete_memory(m["id"])
        st.session_state.chat_history = []
        st.success("All memories cleared.")
        st.rerun()

    if st.button("🔄 Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# ── Main area ──────────────────────────────────────────────────────────────────
st.markdown("## 🧠 MemoryOS")
st.markdown("Persistent memory infrastructure for LLM agents — built with MCP · ChromaDB · sentence-transformers")
st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "🗄 Memory Vault", "➕ Store Memory", "🔍 Search"])

# ── Tab 1: Chat ────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-header">Memory-Powered Chat</div>', unsafe_allow_html=True)

    if not ollama_ok:
        st.warning("⚠️ Ollama is offline. Start it with `ollama serve` and pull a model with `ollama pull llama3.2`")

    # render chat history
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div style="text-align:center; padding: 3rem 0; color: var(--muted);">
                <div style="font-size:2.5rem">🧠</div>
                <div style="margin-top:.5rem; font-size:.9rem">Start a conversation. Everything is remembered forever.</div>
            </div>""", unsafe_allow_html=True)

        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
            elif msg["role"] == "tool":
                st.markdown(f'<div class="chat-tool">⚙ {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-agent">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

    # input
    st.divider()
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "Message",
            placeholder="Ask me anything — I remember everything about you...",
            label_visibility="collapsed",
            key="chat_input"
        )
    with col_btn:
        send = st.button("Send →", use_container_width=True)

    if send and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Searching memory & generating response..."):
            response, tool_calls = memory_agent(user_input, st.session_state.user_id)

        # show tool calls
        for call in tool_calls:
            st.session_state.chat_history.append({
                "role": "tool",
                "content": f"Called {call['tool']}({json.dumps(call['input'])[:80]}...)"
            })

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

# ── Tab 2: Memory Vault ────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-header">All Stored Memories</div>', unsafe_allow_html=True)

    if not memories:
        st.info("No memories stored yet. Start chatting or add memories manually.")
    else:
        # filter + sort controls
        col_sort, col_filter = st.columns([1, 2])
        with col_sort:
            sort_by = st.selectbox("Sort by", ["importance ↓", "importance ↑", "newest", "oldest"])
        with col_filter:
            search_filter = st.text_input("Filter memories", placeholder="Type to filter...")

        # apply filter
        filtered = memories
        if search_filter:
            filtered = [m for m in memories if search_filter.lower() in m["text"].lower()]

        # apply sort
        if sort_by == "importance ↓":
            filtered.sort(key=lambda m: m["importance"], reverse=True)
        elif sort_by == "importance ↑":
            filtered.sort(key=lambda m: m["importance"])
        elif sort_by == "newest":
            filtered.sort(key=lambda m: m.get("created_at", ""), reverse=True)
        else:
            filtered.sort(key=lambda m: m.get("created_at", ""))

        st.markdown(f"Showing **{len(filtered)}** of **{len(memories)}** memories")
        st.divider()

        for m in filtered:
            render_memory_card(m, show_delete=True)

# ── Tab 3: Store Memory ────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">Manually Store a Memory</div>', unsafe_allow_html=True)

    with st.form("store_form"):
        text = st.text_area("Memory content", placeholder="Enter what you want to remember...", height=100)
        col_tags, col_imp = st.columns([2, 1])
        with col_tags:
            tags_input = st.text_input("Tags (comma separated)", placeholder="career, skills, preferences")
        with col_imp:
            importance = st.slider("Importance", 1, 10, 7)
        submitted = st.form_submit_button("💾 Store Memory", use_container_width=True)

        if submitted and text.strip():
            tags = [t.strip() for t in tags_input.split(",") if t.strip()]
            result = json.loads(tool_store_memory(
                text=text,
                user_id=st.session_state.user_id,
                tags=tags,
                importance=importance
            ))
            st.success(f"✅ Memory stored! ID: `{result['id'][:20]}...`")
            st.rerun()

    # quick store presets (useful for demo)
    st.divider()
    st.markdown('<div class="section-header">Quick Demo Presets</div>', unsafe_allow_html=True)
    st.caption("Click to instantly store sample memories for demo purposes")

    presets = [
        ("👤 Profile", "My name is Nikita Babbar. I am a final year B.Tech student in AI & Data Science.", ["profile"], 9),
        ("🎯 Career Goal", "I am targeting Generative AI Engineer roles at top tech companies.", ["career"], 9),
        ("🏆 Achievement", "I ranked All India #5 in the Unstop Talent Award 2026.", ["achievement"], 10),
        ("💻 Skills", "My strongest skills are LangChain, RAG pipelines, ChromaDB and MCP servers.", ["skills"], 8),
        ("🥇 Hackathon", "I won 4th place nationally in the TruthTell Hackathon by Government of India.", ["achievement"], 9),
    ]

    cols = st.columns(len(presets))
    for i, (label, text, tags, imp) in enumerate(presets):
        with cols[i]:
            if st.button(label, use_container_width=True, key=f"preset_{i}"):
                tool_store_memory(text=text, user_id=st.session_state.user_id, tags=tags, importance=imp)
                st.success("Stored!")
                st.rerun()

# ── Tab 4: Search ──────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-header">Semantic Memory Search</div>', unsafe_allow_html=True)
    st.caption("Search uses vector similarity — results are ranked by semantic relevance, not keyword match")

    col_q, col_k = st.columns([4, 1])
    with col_q:
        query = st.text_input("Search query", placeholder="What are my career goals?", label_visibility="collapsed")
    with col_k:
        top_k = st.number_input("Top K", min_value=1, max_value=20, value=5, label_visibility="collapsed")

    if st.button("🔍 Search", use_container_width=False) and query:
        with st.spinner("Running semantic search..."):
            results = json.loads(tool_search_memory(
                query=query,
                user_id=st.session_state.user_id,
                top_k=top_k
            ))

        if not results.get("results"):
            st.info("No memories found for this query.")
        else:
            st.markdown(f"Found **{len(results['results'])}** results")
            st.divider()
            for r in results["results"]:
                score_color = "#4ade80" if r["score"] > 0.7 else "#fbbf24" if r["score"] > 0.4 else "#f87171"
                tags_html = " ".join([f'<span class="tag">{t}</span>' for t in r.get("tags", [])])
                st.markdown(f"""
                <div class="memory-card">
                  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:.4rem">
                    <span style="font-family:'Space Mono',monospace; font-size:.7rem; color:{score_color}">
                      ▶ similarity: {r['score']:.4f}
                    </span>
                    <span style="font-size:.7rem; color:var(--muted)">{r.get('created_at','')[:16].replace('T',' ')}</span>
                  </div>
                  <div class="memory-text">{r['text']}</div>
                  <div class="memory-meta"><span>{tags_html}</span></div>
                </div>""", unsafe_allow_html=True)