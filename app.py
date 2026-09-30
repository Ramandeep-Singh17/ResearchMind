import json
import os
import re
import time
from pathlib import Path

import streamlit as st

from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ============================================================================
# App Configuration
# ============================================================================
GROQ_MODEL = "openai/gpt-oss-120b"
APP_NAME = "ResearchMind"

st.set_page_config(
    page_title=f"{APP_NAME} · Multi-Agent Research",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# Modern Professional Styling
# ============================================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg-dark: #0a0e27;
    --bg-darker: #050812;
    --surface: #13172d;
    --surface-light: #1a1f3a;
    --border-color: #252d47;
    --border-accent: #ff9500;
    --text-primary: #ffffff;
    --text-secondary: #b3bcc8;
    --text-muted: #7a8494;
    --accent-saffron: #ff9500;
    --accent-blue: #3b82f6;
    --success: #10b981;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.stApp {
    color: var(--text-primary);
    background: linear-gradient(180deg, var(--bg-dark) 0%, var(--bg-darker) 100%);
    background-attachment: fixed;
}

#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; }
.block-container { 
    max-width: 1440px; 
    padding: 2rem 2.5rem 5rem; 
}

/* ========== SIDEBAR ========== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(5, 8, 18, 0.8), rgba(10, 14, 39, 0.9));
    border-right: 1px solid var(--border-color);
}
section[data-testid="stSidebar"] .block-container { 
    padding: 2rem 1.5rem;
}

/* ========== HERO SECTION ========== */
.hero-wrap {
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 3rem 3.5rem;
    background: linear-gradient(135deg, rgba(19, 23, 45, 0.8), rgba(26, 31, 58, 0.6));
    backdrop-filter: blur(8px);
    animation: slide-in-up 0.6s ease-out;
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border: 1px solid var(--border-color);
    border-radius: 20px;
    background: rgba(19, 23, 45, 0.6);
    color: var(--text-secondary);
    font: 600 0.7rem/1 'Inter', monospace;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.hero-title {
    margin: 1.2rem 0 0.8rem;
    font-size: clamp(3rem, 7vw, 5rem);
    line-height: 1.1;
    letter-spacing: -0.02em;
    font-weight: 800;
}

.hero-title-white { color: #ffffff; }
.hero-title-saffron { color: var(--accent-saffron); }

.hero-sub {
    max-width: 900px;
    color: var(--text-secondary);
    font-size: 1.1rem;
    line-height: 1.7;
    margin: 1rem 0 0;
    font-weight: 400;
}

.model-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    margin-top: 1.5rem;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    font: 500 0.75rem/1 'Inter', monospace;
    letter-spacing: 0.08em;
}

.status-dot { 
    width: 8px; 
    height: 8px; 
    border-radius: 50%; 
    background: var(--success);
}

/* ========== CARDS & CONTAINERS ========== */
.card {
    background: var(--surface);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 1.5rem;
    backdrop-filter: blur(4px);
    transition: all 0.2s ease;
}

.card:hover {
    border-color: var(--border-accent);
    background: var(--surface-light);
}

.card-title {
    color: var(--text-secondary);
    font: 700 0.75rem/1 'Inter', monospace;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.card-title::before {
    content: '';
    width: 3px;
    height: 3px;
    border-radius: 50%;
    background: var(--accent-saffron);
}

/* ========== INPUTS ========== */
.stTextInput > div > div > input,
.stTextArea textarea {
    background: var(--surface) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    font-size: 1rem !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.8rem 1rem !important;
    transition: all 0.2s ease !important;
}

.stTextInput > div > div > input:hover,
.stTextArea textarea:hover {
    border-color: var(--border-accent) !important;
    background: var(--surface-light) !important;
}

.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: var(--accent-saffron) !important;
    background: var(--surface-light) !important;
    box-shadow: 0 0 0 3px rgba(255, 149, 0, 0.1) !important;
}

/* ========== BUTTONS ========== */
.stButton > button,
.stDownloadButton > button {
    border-radius: 8px !important;
    border: 1px solid var(--border-color) !important;
    background: linear-gradient(135deg, var(--accent-saffron), #ff8c00) !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    min-height: 2.8rem !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: var(--accent-saffron) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(255, 149, 0, 0.25) !important;
}

button[kind="secondary"] {
    background: var(--surface) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-secondary) !important;
    box-shadow: none !important;
}

button[kind="secondary"]:hover {
    border-color: var(--accent-saffron) !important;
    background: var(--surface-light) !important;
    color: var(--text-primary) !important;
}

/* ========== PIPELINE STEPS ========== */
.step-card {
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 1.2rem;
    background: var(--surface);
    transition: all 0.3s ease;
    animation: slide-in-up 0.4s ease-out;
}

.step-card.active {
    border-color: var(--accent-saffron);
    background: linear-gradient(135deg, rgba(255, 149, 0, 0.05), rgba(255, 149, 0, 0.02));
}

.step-card.done {
    border-color: var(--success);
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.02));
}

.step-top {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.step-num {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font: 600 0.75rem/1 'Inter', monospace;
    color: var(--accent-saffron);
    background: rgba(255, 149, 0, 0.1);
    border: 1px solid rgba(255, 149, 0, 0.2);
}

.step-card.done .step-num {
    color: var(--success);
    background: rgba(16, 185, 129, 0.1);
    border-color: rgba(16, 185, 129, 0.2);
}

.step-name {
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--text-primary);
}

.step-state {
    margin-left: auto;
    font: 600 0.65rem/1 'Inter', monospace;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.waiting { color: var(--text-muted); }
.running { color: var(--accent-saffron); }
.done-state { color: var(--success); }

.step-desc {
    color: var(--text-muted);
    font-size: 0.8rem;
    margin-top: 0.7rem;
    line-height: 1.5;
}

/* ========== METRICS ========== */
.metric {
    padding: 1.2rem;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    background: var(--surface);
    transition: all 0.2s ease;
}

.metric:hover {
    border-color: var(--accent-saffron);
    background: var(--surface-light);
}

.metric-label {
    color: var(--text-muted);
    font: 600 0.7rem/1 'Inter', monospace;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.metric-value {
    margin-top: 0.6rem;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--accent-saffron);
    letter-spacing: -0.01em;
}

/* ========== RESULT BOXES ========== */
.result-box {
    border: 1px solid var(--border-color);
    background: var(--surface);
    border-radius: 10px;
    padding: 1.8rem;
    backdrop-filter: blur(4px);
}

.result-label {
    color: var(--accent-saffron);
    font: 700 0.75rem/1 'Inter', monospace;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

.result-label::before {
    content: '';
    width: 3px;
    height: 3px;
    border-radius: 50%;
    background: var(--accent-saffron);
}

/* ========== TABS ========== */
button[data-baseweb="tab"] {
    color: var(--text-muted) !important;
    font-weight: 500 !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.2s ease !important;
}

button[data-baseweb="tab"]:hover {
    color: var(--text-secondary) !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent-saffron) !important;
    border-bottom-color: var(--accent-saffron) !important;
}

/* ========== PROGRESS ========== */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--accent-saffron), #ff8c00) !important;
}

/* ========== ALERTS ========== */
div[data-testid="stAlert"] {
    border-radius: 8px !important;
    border: 1px solid var(--border-color) !important;
    background: var(--surface) !important;
}

/* ========== FOOTER ========== */
.footer {
    color: var(--text-muted);
    text-align: center;
    margin-top: 4rem;
    font: 500 0.75rem/1.8 'Inter', monospace;
    letter-spacing: 0.08em;
}

/* ========== ANIMATIONS ========== */
@keyframes slide-in-up {
    from {
        opacity: 0;
        transform: translateY(16px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* ========== RESPONSIVE ========== */
@media (max-width: 900px) {
    .block-container { 
        padding: 1.5rem 1.5rem 4rem;
    }
    .hero-wrap { 
        padding: 2rem 1.5rem;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================================
# Session State
# ============================================================================
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

if "pending_topic" in st.session_state:
    st.session_state.topic_input = st.session_state.pending_topic
    del st.session_state.pending_topic

auto_research = False
if "auto_research" in st.session_state and st.session_state.auto_research:
    auto_research = True
    st.session_state.auto_research = False

# ============================================================================
# Helpers
# ============================================================================
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


# ============================================================================
# Sidebar
# ============================================================================
with st.sidebar:
    st.markdown("### 🔬 ResearchMind")
    st.caption("Multi-agent research workspace")

    st.markdown("---")
    st.markdown("**AI Runtime**")
    st.markdown(
        f"<div class='model-pill'><span class='status-dot'></span> Groq · <code>{GROQ_MODEL}</code></div>",
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
        st.markdown(f"<div style='padding:.35rem 0;font-size:.82rem;color:var(--text-muted)'>{label}</div>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("↺ Clear workspace", use_container_width=True, type="secondary"):
        st.session_state.results = {}
        st.session_state.timings = {}
        st.session_state.pipeline_complete = False
        st.session_state.last_topic = ""
        st.session_state.topic_input = ""
        st.session_state.error = None
        st.rerun()

# ============================================================================
# Hero Section
# ============================================================================
st.markdown(
    """
    <div class="hero-wrap">
      <div class="eyebrow">◉ MULTI-AGENT RESEARCH SYSTEM</div>
      <div class="hero-title"><span class="hero-title-white">Research</span><span class="hero-title-saffron">Mind</span></div>
      <p class="hero-sub">
        Ask a research question and let specialized agents search the web, inspect sources,
        synthesize evidence, and critique the final answer in one workflow.
      </p>
      <div class="model-pill"><span class="status-dot"></span> Running on Groq · <code style="color: var(--text-secondary);">""" + GROQ_MODEL + """</code></div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# ============================================================================
# Query Composer + Pipeline
# ============================================================================
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
                st.session_state.pending_topic = ex
                st.rerun()

    st.write("")
    run_btn = st.button("🚀  Start research", use_container_width=True)

with right:
    overview_placeholder = st.empty()
    initial_status = {k: "done" if k in st.session_state.results else "waiting" for k in ["search", "reader", "writer", "critic"]}
    render_pipeline(initial_status, overview_placeholder)

# ============================================================================
# Pipeline Execution
# ============================================================================
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

# ============================================================================
# Results
# ============================================================================
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

# ============================================================================
# Footer
# ============================================================================
st.markdown(
    "<div class='footer'>ResearchMind · LangChain multi-agent pipeline · Streamlit UI · Groq runtime</div>",
    unsafe_allow_html=True,
)
