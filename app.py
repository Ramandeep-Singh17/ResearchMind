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
    --bg: #070a10;
    --panel: rgba(17, 22, 32, 0.78);
    --panel-2: rgba(12, 16, 24, 0.92);
    --border: rgba(255,255,255,.08);
    --border-strong: rgba(112, 148, 255, .34);
    --text: #eff3f8;
    --muted: #8f9aac;
    --accent: #7295ff;
    --accent-2: #9b7bff;
    --success: #51d88a;
    --warning: #ffb454;
    --danger: #ff7272;
}

html, body, [class*="css"] {
    font-family: 'Manrope', sans-serif;
}

.stApp {
    color: var(--text);
    background:
        radial-gradient(900px 500px at 8% -8%, rgba(93, 122, 255, .18), transparent 60%),
        radial-gradient(760px 480px at 94% 8%, rgba(155, 123, 255, .11), transparent 58%),
        radial-gradient(900px 560px at 50% 110%, rgba(58, 178, 155, .07), transparent 62%),
        var(--bg);
}

#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; }
.block-container { max-width: 1380px; padding: 1.25rem 2rem 4rem; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(10,13,20,.98), rgba(8,11,17,.98));
    border-right: 1px solid rgba(255,255,255,.06);
}
section[data-testid="stSidebar"] .block-container { padding: 1.5rem 1.1rem; }

/* Hero */
.hero-wrap {
    position: relative;
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: 28px;
    padding: 2.4rem 2.7rem 2.3rem;
    background: linear-gradient(135deg, rgba(20,26,39,.92), rgba(11,15,23,.86));
    box-shadow: 0 24px 70px rgba(0,0,0,.24);
}
.hero-wrap::after {
    content: '';
    position: absolute;
    width: 260px;
    height: 260px;
    right: -80px;
    top: -90px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(114,149,255,.27), transparent 68%);
    pointer-events: none;
}
.eyebrow {
    display: inline-flex;
    align-items: center;
    gap: .45rem;
    padding: .38rem .72rem;
    border: 1px solid rgba(114,149,255,.28);
    border-radius: 999px;
    background: rgba(114,149,255,.08);
    color: #b9c7ff;
    font: 500 .68rem/1 'DM Mono', monospace;
    letter-spacing: .14em;
    text-transform: uppercase;
}
.hero-title {
    margin: .9rem 0 .6rem;
    font-size: clamp(2.5rem, 5vw, 4.55rem);
    line-height: .98;
    letter-spacing: -.055em;
    font-weight: 800;
}
.hero-title span {
    background: linear-gradient(90deg, #dbe4ff, #8d9fff 52%, #b59dff);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}
.hero-sub {
    max-width: 790px;
    color: var(--muted);
    font-size: 1rem;
    line-height: 1.7;
    margin: 0;
}

/* Model pill */
.model-pill {
    display: inline-flex;
    align-items: center;
    gap: .55rem;
    margin-top: 1.15rem;
    padding: .55rem .8rem;
    border-radius: 11px;
    background: rgba(255,255,255,.035);
    border: 1px solid rgba(255,255,255,.07);
    color: #c8d0dc;
    font: 500 .68rem/1.1 'DM Mono', monospace;
}
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--success); box-shadow: 0 0 14px rgba(81,216,138,.65); }

/* Generic cards */
.card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.2rem 1.25rem;
    backdrop-filter: blur(14px);
}
.card-title {
    color: #c7d0de;
    font: 500 .69rem/1 'DM Mono', monospace;
    letter-spacing: .14em;
    text-transform: uppercase;
    margin-bottom: .85rem;
}
.muted { color: var(--muted); }

/* Text input */
.stTextInput > div > div > input, .stTextArea textarea {
    background: rgba(255,255,255,.035) !important;
    color: var(--text) !important;
    border: 1px solid rgba(255,255,255,.09) !important;
    border-radius: 13px !important;
    font-size: 1rem !important;
}
.stTextInput > div > div > input:focus, .stTextArea textarea:focus {
    border-color: rgba(114,149,255,.75) !important;
    box-shadow: 0 0 0 3px rgba(114,149,255,.11) !important;
}

/* Buttons */
.stButton > button, .stDownloadButton > button {
    border-radius: 12px !important;
    border: 1px solid rgba(114,149,255,.34) !important;
    background: linear-gradient(135deg, #6f8fff, #8f70f4) !important;
    color: white !important;
    font-weight: 700 !important;
    box-shadow: 0 10px 28px rgba(90, 111, 235, .18) !important;
    min-height: 2.8rem !important;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: rgba(255,255,255,.48) !important;
    transform: translateY(-1px);
}

/* Secondary buttons */
button[kind="secondary"] {
    background: rgba(255,255,255,.035) !important;
    box-shadow: none !important;
}

/* Status cards */
.step-card {
    position: relative;
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1rem 1.05rem;
    background: rgba(255,255,255,.022);
    transition: .2s ease;
}
.step-card.active { border-color: rgba(114,149,255,.42); background: rgba(114,149,255,.055); }
.step-card.done { border-color: rgba(81,216,138,.28); background: rgba(81,216,138,.035); }
.step-top { display: flex; align-items: center; gap: .7rem; }
.step-num {
    width: 30px; height: 30px; border-radius: 9px; display:flex; align-items:center; justify-content:center;
    font: 500 .69rem/1 'DM Mono', monospace; color:#b8c6ff; background: rgba(114,149,255,.12);
}
.step-name { font-weight: 700; font-size: .92rem; }
.step-state { margin-left: auto; font: 500 .62rem/1 'DM Mono', monospace; letter-spacing: .08em; }
.waiting { color: #667080; }
.running { color: #9db0ff; }
.done-state { color: var(--success); }
.step-desc { color: #737e8e; font-size: .76rem; margin-top: .48rem; line-height: 1.45; }

/* Metric cards */
.metric {
    padding: 1rem;
    border-radius: 16px;
    border: 1px solid var(--border);
    background: rgba(255,255,255,.022);
}
.metric-label { color:#7f8a9a; font: 500 .61rem/1 'DM Mono',monospace; letter-spacing:.12em; text-transform:uppercase; }
.metric-value { margin-top:.35rem; font-size:1.28rem; font-weight:800; letter-spacing:-.03em; }

/* Result boxes */
.result-box {
    border: 1px solid var(--border);
    background: rgba(9,12,18,.6);
    border-radius: 16px;
    padding: 1.2rem 1.3rem;
}
.result-label {
    color: #9fb0ff;
    font: 500 .66rem/1 'DM Mono', monospace;
    letter-spacing: .14em;
    text-transform: uppercase;
    margin-bottom: .8rem;
}

/* Streamlit tabs */
button[data-baseweb="tab"] { color: #8d98a8 !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #dfe6ff !important; }

/* Progress */
.stProgress > div > div > div > div { background: linear-gradient(90deg, #6f8fff, #9b7bff) !important; }

/* Alerts */
div[data-testid="stAlert"] { border-radius: 13px !important; }

/* Footer */
.footer { color:#626c79; text-align:center; margin-top:3rem; font: 400 .64rem/1.7 'DM Mono',monospace; letter-spacing:.05em; }

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
            st.markdown('<div class="result-label">SEARCH AGENT OUTPUT</div>', unsafe_have_html=True)
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
