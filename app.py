import json
import os
import re
import time
from pathlib import Path

import streamlit as st

from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# -----------------------------------------------------------------------------
# App configuration
# -----------------------------------------------------------------------------
GROQ_MODEL = "openai/gpt-oss-120b"
APP_NAME = "ResearchMind"

st.set_page_config(
    page_title=f"{APP_NAME} · Multi-Agent Research",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Styling
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #0f0a1e;
    --panel: rgba(20, 12, 40, 0.65);
    --panel-2: rgba(15, 10, 28, 0.88);
    --border: rgba(168, 85, 247, .15);
    --border-strong: rgba(139, 92, 246, .45);
    --text: #f0f4ff;
    --muted: #a0afc0;
    --accent: #8b5cf6;
    --accent-2: #06b6d4;
    --accent-3: #ec4899;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
}

@keyframes glow-pulse {
    0%, 100% { box-shadow: 0 0 20px rgba(139, 92, 246, 0.4), 0 10px 30px rgba(139, 92, 246, 0.15); }
    50% { box-shadow: 0 0 40px rgba(139, 92, 246, 0.6), 0 10px 40px rgba(139, 92, 246, 0.25); }
}

@keyframes slide-up {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fade-in-scale {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}

@keyframes shimmer-pulse {
    0%, 100% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

@keyframes counter-up {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes step-enter {
    from { opacity: 0; transform: translateX(-12px); }
    to { opacity: 1; transform: translateX(0); }
}

html, body, [class*="css"] {
    font-family: 'Manrope', sans-serif;
}

.stApp {
    color: var(--text);
    background:
        radial-gradient(900px 500px at 8% -8%, rgba(139, 92, 246, .22), transparent 60%),
        radial-gradient(760px 480px at 94% 8%, rgba(6, 182, 212, .12), transparent 58%),
        radial-gradient(900px 560px at 50% 110%, rgba(236, 72, 153, .06), transparent 62%),
        var(--bg);
    background-attachment: fixed;
}

#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; }
.block-container { max-width: 1380px; padding: 1.25rem 2rem 4rem; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(15, 10, 28, .95), rgba(10, 8, 20, .98));
    border-right: 1.5px solid var(--border);
}
section[data-testid="stSidebar"] .block-container { 
    padding: 1.6rem 1.2rem;
}
section[data-testid="stSidebar"] h3 {
    color: #e9d5ff;
    font-weight: 700;
}

/* Hero */
.hero-wrap {
    position: relative;
    overflow: hidden;
    border: 2px solid var(--border-strong);
    border-radius: 28px;
    padding: 2.8rem 3rem 2.5rem;
    background: linear-gradient(135deg, rgba(30, 15, 50, .85), rgba(15, 10, 28, .92));
    box-shadow: 0 20px 60px rgba(139, 92, 246, .12), 0 0 60px rgba(139, 92, 246, .08);
    animation: slide-up 0.8s ease-out;
}
.hero-wrap::before {
    content: '';
    position: absolute;
    width: 300px;
    height: 300px;
    left: -150px;
    top: -150px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(139, 92, 246, .15), transparent 70%);
    pointer-events: none;
}
.hero-wrap::after {
    content: '';
    position: absolute;
    width: 280px;
    height: 280px;
    right: -100px;
    top: -80px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(6, 182, 212, .12), transparent 68%);
    pointer-events: none;
}
.eyebrow {
    display: inline-flex;
    align-items: center;
    gap: .5rem;
    padding: .45rem .85rem;
    border: 1.5px solid rgba(139, 92, 246, .4);
    border-radius: 999px;
    background: linear-gradient(135deg, rgba(139, 92, 246, .15), rgba(6, 182, 212, .08));
    color: #e9d5ff;
    font: 600 .72rem/1 'DM Mono', monospace;
    letter-spacing: .16em;
    text-transform: uppercase;
    animation: fade-in-scale 0.8s ease-out;
}
.hero-title {
    margin: 1rem 0 .7rem;
    font-size: clamp(2.8rem, 6vw, 4.8rem);
    line-height: 1;
    letter-spacing: -.06em;
    font-weight: 800;
    animation: slide-up 1s ease-out 0.1s both;
}
.hero-title span {
    background: linear-gradient(120deg, #a78bfa, #8b5cf6 35%, #06b6d4 65%, #ec4899);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    background-size: 200% 200%;
    animation: glow-pulse 3s ease-in-out infinite;
}
.hero-sub {
    max-width: 800px;
    color: #c8d5e8;
    font-size: 1.05rem;
    line-height: 1.75;
    margin: 0;
    animation: slide-up 1s ease-out 0.2s both;
}

/* Model pill */
.model-pill {
    display: inline-flex;
    align-items: center;
    gap: .6rem;
    margin-top: 1.2rem;
    padding: .6rem .9rem;
    border-radius: 10px;
    background: linear-gradient(135deg, rgba(139, 92, 246, .12), rgba(6, 182, 212, .08));
    border: 1.5px solid var(--border);
    color: #e9d5ff;
    font: 600 .7rem/1.1 'DM Mono', monospace;
    letter-spacing: .08em;
    transition: all 0.3s ease;
    animation: fade-in-scale 0.8s ease-out;
}
.model-pill:hover {
    border-color: var(--border-strong);
    background: linear-gradient(135deg, rgba(139, 92, 246, .18), rgba(6, 182, 212, .12));
}
.dot { 
    width: 8px; 
    height: 8px; 
    border-radius: 50%; 
    background: var(--success); 
    box-shadow: 0 0 16px rgba(16, 185, 129, .7), inset 0 0 8px rgba(16, 185, 129, .5);
    animation: glow-pulse 2s ease-in-out infinite;
}

/* Generic cards */
.card {
    background: linear-gradient(135deg, rgba(20, 12, 40, .5), rgba(15, 10, 28, .7));
    border: 1.5px solid var(--border);
    border-radius: 16px;
    padding: 1.4rem 1.5rem;
    backdrop-filter: blur(12px);
    transition: all 0.3s ease;
    animation: fade-in-scale 0.6s ease-out;
}
.card:hover {
    border-color: var(--border-strong);
    box-shadow: 0 8px 24px rgba(139, 92, 246, .1);
}
.card-title {
    color: #e9d5ff;
    font: 700 .74rem/1 'DM Mono', monospace;
    letter-spacing: .16em;
    text-transform: uppercase;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.card-title::before {
    content: '';
    display: inline-block;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: var(--accent);
}
.muted { color: var(--muted); }

/* Text input */
.stTextInput > div > div > input, .stTextArea textarea {
    background: linear-gradient(135deg, rgba(139, 92, 246, .08), rgba(6, 182, 212, .04)) !important;
    color: var(--text) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
    font-size: 1rem !important;
    font-family: 'Manrope', sans-serif !important;
    transition: all 0.3s ease !important;
    padding: 0.75rem 1rem !important;
}
.stTextInput > div > div > input:hover, .stTextArea textarea:hover {
    border-color: rgba(139, 92, 246, .3) !important;
    background: linear-gradient(135deg, rgba(139, 92, 246, .12), rgba(6, 182, 212, .08)) !important;
}
.stTextInput > div > div > input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    background: linear-gradient(135deg, rgba(139, 92, 246, .15), rgba(6, 182, 212, .1)) !important;
    box-shadow: 0 0 0 4px rgba(139, 92, 246, .15), 0 8px 24px rgba(139, 92, 246, .15) !important;
}

/* Buttons */
.stButton > button, .stDownloadButton > button {
    border-radius: 12px !important;
    border: 1.5px solid var(--border-strong) !important;
    background: linear-gradient(135deg, #8b5cf6, #06b6d4) !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    box-shadow: 0 8px 24px rgba(139, 92, 246, .28), 0 0 20px rgba(139, 92, 246, .15) !important;
    min-height: 3rem !important;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
    animation: fade-in-scale 0.6s ease-out;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: rgba(6, 182, 212, .8) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 16px 40px rgba(139, 92, 246, .4), 0 0 30px rgba(6, 182, 212, .25) !important;
}
.stButton > button:active, .stDownloadButton > button:active {
    transform: translateY(-1px) !important;
}

/* Secondary buttons */
button[kind="secondary"] {
    background: linear-gradient(135deg, rgba(139, 92, 246, .12), rgba(6, 182, 212, .08)) !important;
    border: 1.5px solid var(--border) !important;
    box-shadow: 0 4px 12px rgba(139, 92, 246, .1) !important;
    color: #e9d5ff !important;
}
button[kind="secondary"]:hover {
    background: linear-gradient(135deg, rgba(139, 92, 246, .2), rgba(6, 182, 212, .15)) !important;
    border-color: var(--border-strong) !important;
    transform: translateY(-2px) !important;
}

/* Status cards */
.step-card {
    position: relative;
    overflow: hidden;
    border: 1.5px solid var(--border);
    border-radius: 14px;
    padding: 1.15rem 1.2rem;
    background: rgba(139, 92, 246, .04);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    animation: step-enter 0.5s ease-out;
}
.step-card::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(139, 92, 246, .1), transparent);
    transition: left 0.6s ease;
}
.step-card.active { 
    border-color: var(--accent);
    background: linear-gradient(135deg, rgba(139, 92, 246, .12), rgba(139, 92, 246, .05));
    box-shadow: 0 0 30px rgba(139, 92, 246, .2), inset 0 0 20px rgba(139, 92, 246, .08);
}
.step-card.active::before { left: 100%; }
.step-card.done { 
    border-color: rgba(16, 185, 129, .45);
    background: linear-gradient(135deg, rgba(16, 185, 129, .08), rgba(16, 185, 129, .03));
    box-shadow: 0 0 25px rgba(16, 185, 129, .15);
}
.step-top { display: flex; align-items: center; gap: .8rem; }
.step-num {
    width: 36px; height: 36px; border-radius: 10px; display:flex; align-items:center; justify-content:center;
    font: 600 .75rem/1 'DM Mono', monospace; color:#e9d5ff; background: linear-gradient(135deg, rgba(139, 92, 246, .3), rgba(139, 92, 246, .15));
    border: 1px solid rgba(139, 92, 246, .3);
    transition: all 0.3s ease;
}
.step-card.active .step-num { 
    background: linear-gradient(135deg, rgba(139, 92, 246, .5), rgba(6, 182, 212, .3));
    box-shadow: 0 0 20px rgba(139, 92, 246, .4);
    animation: glow-pulse 2s ease-in-out infinite;
}
.step-card.done .step-num { 
    background: linear-gradient(135deg, rgba(16, 185, 129, .4), rgba(16, 185, 129, .2));
    color: var(--success);
}
.step-name { font-weight: 700; font-size: .96rem; color: #e9d5ff; }
.step-state { margin-left: auto; font: 600 .65rem/1 'DM Mono', monospace; letter-spacing: .1em; text-transform: uppercase; }
.waiting { color: #8b9dc3; }
.running { color: #8b5cf6; font-weight: 700; }
.done-state { color: var(--success); font-weight: 700; }
.step-desc { color: #a0afc0; font-size: .78rem; margin-top: .6rem; line-height: 1.5; }

/* Metric cards */
.metric {
    padding: 1.25rem;
    border-radius: 14px;
    border: 1.5px solid var(--border);
    background: linear-gradient(135deg, rgba(139, 92, 246, .06), rgba(6, 182, 212, .04));
    transition: all 0.3s ease;
    animation: fade-in-scale 0.6s ease-out;
}
.metric:hover {
    border-color: var(--border-strong);
    background: linear-gradient(135deg, rgba(139, 92, 246, .1), rgba(6, 182, 212, .08));
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(139, 92, 246, .12);
}
.metric-label { 
    color: #a0afc0; 
    font: 600 .64rem/1 'DM Mono', monospace; 
    letter-spacing: .15em; 
    text-transform: uppercase;
    opacity: 0.9;
}
.metric-value { 
    margin-top: .5rem; 
    font-size: 1.42rem; 
    font-weight: 800; 
    letter-spacing: -.02em;
    background: linear-gradient(120deg, #e9d5ff, #a78bfa, #06b6d4);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    animation: counter-up 0.8s ease-out;
}

/* Result boxes */
.result-box {
    border: 2px solid var(--border-strong);
    background: linear-gradient(135deg, rgba(30, 15, 50, .4), rgba(15, 10, 28, .6));
    border-radius: 16px;
    padding: 1.6rem;
    backdrop-filter: blur(8px);
    box-shadow: 0 8px 32px rgba(139, 92, 246, .1), inset 0 0 20px rgba(139, 92, 246, .05);
    animation: fade-in-scale 0.6s ease-out;
}
.result-label {
    color: #a78bfa;
    font: 700 .7rem/1 'DM Mono', monospace;
    letter-spacing: .16em;
    text-transform: uppercase;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.result-label::before {
    content: '';
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: linear-gradient(120deg, #8b5cf6, #06b6d4);
    animation: glow-pulse 2s ease-in-out infinite;
}

/* Streamlit tabs */
button[data-baseweb="tab"] { 
    color: #a0afc0 !important;
    font-weight: 600 !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.3s ease !important;
}
button[data-baseweb="tab"]:hover {
    color: #c8d5e8 !important;
    border-bottom-color: rgba(139, 92, 246, .3) !important;
}
button[data-baseweb="tab"][aria-selected="true"] { 
    color: #e9d5ff !important;
    border-bottom-color: var(--accent) !important;
}

/* Progress */
.stProgress > div > div > div > div { 
    background: linear-gradient(90deg, #8b5cf6, #06b6d4, #ec4899) !important;
    box-shadow: 0 0 20px rgba(139, 92, 246, .5) !important;
}

/* Alerts */
div[data-testid="stAlert"] { 
    border-radius: 13px !important;
    border: 1.5px solid var(--border-strong) !important;
    background: linear-gradient(135deg, rgba(139, 92, 246, .1), rgba(139, 92, 246, .05)) !important;
}

/* Footer */
.footer { 
    color: #8b9dc3; 
    text-align: center; 
    margin-top: 4rem; 
    font: 500 .68rem/1.8 'DM Mono', monospace; 
    letter-spacing: .08em;
    opacity: 0.8;
    animation: slide-up 1s ease-out 0.5s both;
}

@media (max-width: 900px) {
    .block-container { padding-left: 1rem; padding-right: 1rem; }
    .hero-wrap { padding: 1.6rem; border-radius: 20px; }
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Session state
# -----------------------------------------------------------------------------
def init_state():
    defaults = {
        "topic_input": "",
        "results": {},
        "timings": {},
        "pipeline_complete": False,
        "last_topic": "",
        "error": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()

# ✅ FIX 1: Sync pending_topic after init_state (example button click)
if "pending_topic" in st.session_state:
    st.session_state.topic_input = st.session_state.pending_topic
    del st.session_state.pending_topic

# ✅ FIX 3: Auto-trigger research if auto_research flag is set
auto_research = False
if "auto_research" in st.session_state and st.session_state.auto_research:
    auto_research = True
    st.session_state.auto_research = False

# ----------

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def step_html(num, name, state, desc):
    labels = {
        "waiting": ("WAITING", "waiting"),
        "running": ("● RUNNING", "running"),
        "done": ("✓ DONE", "done-state"),
    }
    label, cls = labels[state]
    card_cls = "active" if state == "running" else "done" if state == "done" else ""
    return f"""
    <div class="step-card {card_cls}">
      <div class="step-top">
        <div class="step-num">{num}</div>
        <div class="step-name">{name}</div>
        <div class="step-state {cls}">{label}</div>
      </div>
      <div class="step-desc">{desc}</div>
    </div>
    """


def render_pipeline(statuses, target):
    names = [
        ("01", "Search Agent", "Finds recent and relevant web evidence"),
        ("02", "Reader Agent", "Opens selected sources and extracts deeper context"),
        ("03", "Writer Chain", "Synthesizes the evidence into a readable report"),
        ("04", "Critic Chain", "Checks the final report and returns feedback"),
    ]
    with target.container():
        st.markdown('<div class="card-title">LIVE PIPELINE</div>', unsafe_allow_html=True)
        for key, (num, name, desc) in zip(["search", "reader", "writer", "critic"], names):
            st.markdown(step_html(num, name, statuses[key], desc), unsafe_allow_html=True)
            if key != "critic":
                st.write("")


def extract_urls(text):
    if not isinstance(text, str):
        return []
    urls = re.findall(r"https?://[^\s)\]\}>]+", text)
    cleaned = []
    for url in urls:
        url = url.rstrip(".,;\"'\n")
        if url not in cleaned:
            cleaned.append(url)
    return cleaned[:10]


def safe_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def run_chain(chain, payload):
    value = chain.invoke(payload)
    return safe_text(value)


def elapsed_label(seconds):
    return f"{seconds:.1f}s"


# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔬 ResearchMind")
    st.caption("Multi-agent research workspace")

    st.markdown("---")
    st.markdown("**AI runtime**")
    st.markdown(
        f"<div class='model-pill'><span class='dot'></span> Groq · <code>{GROQ_MODEL}</code></div>",
        unsafe_allow_html=True,
    )
    st.caption("Temperature 0 · reasoning effort low")

    st.markdown("---")
    st.markdown("**Architecture**")
    for label in [
        "🔎 Search agent",
        "📄 Reader agent",
        "✍️ Writer chain",
        "🧐 Critic chain",
    ]:
        st.markdown(f"<div class='muted' style='padding:.35rem 0;font-size:.82rem'>{label}</div>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("↺ Clear workspace", use_container_width=True, type="secondary"):
        st.session_state.results = {}
        st.session_state.timings = {}
        st.session_state.pipeline_complete = False
        st.session_state.last_topic = ""
        st.session_state.topic_input = ""
        st.session_state.error = None
        st.rerun()

# -----------------------------------------------------------------------------
# Hero
# -----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero-wrap">
      <div class="eyebrow">◉ MULTI-AGENT RESEARCH SYSTEM</div>
      <div class="hero-title">Research<span>Mind</span></div>
      <p class="hero-sub">
        Ask a research question and let specialized agents search the web, inspect sources,
        synthesize evidence, and critique the final answer in one workflow.
      </p>
      <div class="model-pill"><span class="dot"></span> Running on Groq · {GROQ_MODEL}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# -----------------------------------------------------------------------------
# Query composer + pipeline overview
# -----------------------------------------------------------------------------
left, right = st.columns([1.6, 1], gap="large")

with left:
    st.markdown('<div class="card-title">RESEARCH QUESTION</div>', unsafe_allow_html=True)
    topic = st.text_input(
        "Research topic",
        value=st.session_state.topic_input,
        key="topic_input",
        label_visibility="collapsed",
        placeholder="e.g. How is AI affecting entry-level jobs for freshers in India?",
    )
    
    # ✅ FIX 2: Sync topic from session state (critical for button click flow)
    topic = st.session_state.topic_input

    st.write("")
    st.markdown('<div class="card-title">TRY A QUERY</div>', unsafe_allow_html=True)
    examples = [
        "AI impact on fresher jobs in India",
        "Latest progress in fusion energy",
        "Future of multi-agent AI systems",
        "Cybersecurity risks from generative AI",
    ]
    example_cols = st.columns(2)
    for idx, ex in enumerate(examples):
        with example_cols[idx % 2]:
            if st.button(ex, key=f"example_{idx}", use_container_width=True, type="secondary"):
                # ✅ Option A: Two-click flow (current - safe, standard)
                st.session_state.pending_topic = ex
                st.rerun()
                
                # ✅ Option B: Uncomment below for single-click research
                # st.session_state.topic_input = ex
                # st.session_state.auto_research = True
                # st.rerun()

    st.write("")
    run_btn = st.button("🚀  Start research", use_container_width=True)

with right:
    # Always show a compact overview, then live-update it during execution.
    overview_placeholder = st.empty()
    initial_status = {k: "done" if k in st.session_state.results else "waiting" for k in ["search", "reader", "writer", "critic"]}
    render_pipeline(initial_status, overview_placeholder)

# -----------------------------------------------------------------------------
# Pipeline execution
# -----------------------------------------------------------------------------
if run_btn or auto_research:
    if not topic.strip():
        st.warning("Enter a research topic first.")
        st.stop()

    st.session_state.results = {}
    st.session_state.timings = {}
    st.session_state.pipeline_complete = False
    st.session_state.last_topic = topic.strip()
    st.session_state.error = None

    statuses = {"search": "waiting", "reader": "waiting", "writer": "waiting", "critic": "waiting"}
    progress_placeholder = st.empty()
    render_pipeline(statuses, overview_placeholder)

    started_at = time.perf_counter()
    results = {}

    try:
        # Step 1 — Search
        statuses["search"] = "running"
        render_pipeline(statuses, overview_placeholder)
        progress_placeholder.progress(0.08, text="Searching for recent and relevant evidence…")
        t0 = time.perf_counter()
        search_agent = build_search_agent()
        sr = search_agent.invoke({
            "messages": [
                (
                    "user",
                    f"Find recent, reliable and detailed information about: {topic.strip()}",
                )
            ]
        })
        results["search"] = safe_text(sr["messages"][-1].content)
        st.session_state.timings["search"] = time.perf_counter() - t0
        statuses["search"] = "done"
        render_pipeline(statuses, overview_placeholder)

        # Step 2 — Reader
        statuses["reader"] = "running"
        render_pipeline(statuses, overview_placeholder)
        progress_placeholder.progress(0.34, text="Reading the most relevant source in depth…")
        t0 = time.perf_counter()
        reader_agent = build_reader_agent()
        rr = reader_agent.invoke({
            "messages": [
                (
                    "user",
                    f"Based on the following search results about '{topic.strip()}', "
                    "pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{results['search']}",
                )
            ]
        })
        results["reader"] = safe_text(rr["messages"][-1].content)
        st.session_state.timings["reader"] = time.perf_counter() - t0
        statuses["reader"] = "done"
        render_pipeline(statuses, overview_placeholder)

        # Step 3 — Writer
        statuses["writer"] = "running"
        render_pipeline(statuses, overview_placeholder)
        progress_placeholder.progress(0.63, text="Synthesizing evidence into the research report…")
        t0 = time.perf_counter()
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        results["writer"] = run_chain(
            writer_chain,
            {"topic": topic.strip(), "research": research_combined},
        )
        st.session_state.timings["writer"] = time.perf_counter() - t0
        statuses["writer"] = "done"
        render_pipeline(statuses, overview_placeholder)

        # Step 4 — Critic
        statuses["critic"] = "running"
        render_pipeline(statuses, overview_placeholder)
        progress_placeholder.progress(0.84, text="Critiquing the report for gaps and quality…")
        t0 = time.perf_counter()
        results["critic"] = run_chain(critic_chain, {"report": results["writer"]})
        st.session_state.timings["critic"] = time.perf_counter() - t0
        statuses["critic"] = "done"
        render_pipeline(statuses, overview_placeholder)

        total = time.perf_counter() - started_at
        st.session_state.timings["total"] = total
        st.session_state.results = results
        st.session_state.pipeline_complete = True
        progress_placeholder.progress(1.0, text=f"Research complete · {elapsed_label(total)}")

    except Exception as exc:
        st.session_state.results = results
        st.session_state.error = str(exc)
        st.error("The pipeline stopped because one of the agents returned an error.")
        with st.expander("View technical error", expanded=True):
            st.code(str(exc), language="text")

# -----------------------------------------------------------------------------
# Results
# -----------------------------------------------------------------------------
r = st.session_state.results

if r:
    st.markdown("---")
    st.markdown("## Research workspace")

    # Metrics row
    metric_cols = st.columns(5)
    values = [
        ("Stages complete", f"{len(r)}/4"),
        ("Search", elapsed_label(st.session_state.timings.get("search", 0))),
        ("Reader", elapsed_label(st.session_state.timings.get("reader", 0))),
        ("Writer", elapsed_label(st.session_state.timings.get("writer", 0))),
        ("Total", elapsed_label(st.session_state.timings.get("total", 0))),
    ]
    for col, (label, value) in zip(metric_cols, values):
        with col:
            st.markdown(
                f"<div class='metric'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div></div>",
                unsafe_allow_html=True,
            )

    st.write("")

    tabs = st.tabs(["📝 Final Report", "🔍 Evidence", "🧐 Critic", "⚙ Agent Trace"])

    # Final report
    with tabs[0]:
        if "writer" in r:
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown('<div class="result-label">FINAL RESEARCH REPORT</div>', unsafe_allow_html=True)
            st.markdown(r["writer"])
            st.markdown('</div>', unsafe_allow_html=True)

            st.write("")
            c1, c2, c3 = st.columns(3)
            report_text = safe_text(r["writer"])
            report_md = report_text
            report_txt = re.sub(r"[#*_`>]", "", report_text)
            report_json = json.dumps(
                {
                    "topic": st.session_state.last_topic,
                    "model": GROQ_MODEL,
                    "timings": st.session_state.timings,
                    "report": report_text,
                    "critic": safe_text(r.get("critic", "")),
                },
                indent=2,
                ensure_ascii=False,
            )
            with c1:
                st.download_button("⬇ Download Markdown", report_md, file_name="research_report.md", mime="text/markdown", use_container_width=True)
            with c2:
                st.download_button("⬇ Download TXT", report_txt, file_name="research_report.txt", mime="text/plain", use_container_width=True)
            with c3:
                st.download_button("⬇ Download JSON", report_json, file_name="research_report.json", mime="application/json", use_container_width=True)
        else:
            st.info("The writer stage has not completed yet.")

    # Evidence
    with tabs[1]:
        if "search" in r:
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown('<div class="result-label">SEARCH AGENT OUTPUT</div>', unsafe_allow_html=True)
            st.markdown(r["search"])
            st.markdown('</div>', unsafe_allow_html=True)

            urls = extract_urls(r["search"])
            if urls:
                st.write("")
                st.markdown("**Detected sources**")
                for url in urls:
                    st.markdown(f"- [{url}]({url})")

        if "reader" in r:
            st.write("")
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown('<div class="result-label">READER AGENT · DEEPER SOURCE CONTENT</div>', unsafe_allow_html=True)
            st.markdown(r["reader"])
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("The reader stage has not completed yet.")

    # Critic
    with tabs[2]:
        if "critic" in r:
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown('<div class="result-label">CRITIC FEEDBACK</div>', unsafe_allow_html=True)
            st.markdown(r["critic"])
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("The critic stage has not completed yet.")

    # Agent trace
    with tabs[3]:
        st.markdown('<div class="card-title">PIPELINE TIMINGS</div>', unsafe_allow_html=True)
        trace_rows = []
        for key, label in [("search", "Search Agent"), ("reader", "Reader Agent"), ("writer", "Writer Chain"), ("critic", "Critic Chain")]:
            if key in st.session_state.timings:
                trace_rows.append(f"**{label}** — {elapsed_label(st.session_state.timings[key])}")
        for row in trace_rows:
            st.markdown(row)
        if not trace_rows:
            st.info("No timing data yet.")

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown(
    "<div class='footer'>ResearchMind · LangChain multi-agent pipeline · Streamlit UI · Groq runtime</div>",
    unsafe_allow_html=True,
)
