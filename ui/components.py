
import streamlit as st

# ═══════════════════════════════════════════════════════════════════════════
#  CLINICAL CSS
# ═══════════════════════════════════════════════════════════════════════════
def load_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto+Mono:wght@400;500&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    color: #212529;
}
.stApp, .main .block-container { background-color: #FFFFFF !important; }
section[data-testid="stSidebar"] {
    background-color: #F8F9FA !important;
    border-right: 1px solid #212529 !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    background-color: #F8F9FA !important;
}
#MainMenu, footer, header { visibility: hidden; }

/* Lab header */
.lab-header {
    border-bottom: 2px solid #212529;
    padding: 1.8rem 0 1.2rem;
    margin-bottom: 2rem;
}
.lab-header .lab-tag {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.65rem; font-weight: 500;
    letter-spacing: 0.18em; text-transform: uppercase; color: #6c757d;
    margin-bottom: 0.3rem;
}
.lab-header h1 {
    font-size: 1.6rem; font-weight: 700; color: #000000;
    margin: 0; letter-spacing: -0.03em; line-height: 1.2;
}
.lab-header .sub {
    font-size: 0.82rem; color: #6c757d; margin-top: 0.3rem; font-weight: 400;
}

/* Data strip */
.data-strip {
    display: flex;
    border-top: 1px solid #212529;
    border-bottom: 1px solid #212529;
    margin-bottom: 2rem;
}
.data-strip .cell {
    flex: 1; padding: 0.9rem 1.2rem;
    border-right: 1px solid #dee2e6; text-align: center;
}
.data-strip .cell:last-child { border-right: none; }
.data-strip .cell .lbl {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.6rem; font-weight: 500;
    letter-spacing: 0.12em; text-transform: uppercase; color: #6c757d;
    margin-bottom: 0.15rem;
}
.data-strip .cell .val {
    font-size: 1.5rem; font-weight: 700; color: #000000;
    font-variant-numeric: tabular-nums;
}
.data-strip .cell .val.int-val { color: #FF3333; }

/* Section label */
.section-label {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.65rem; font-weight: 500;
    letter-spacing: 0.15em; text-transform: uppercase; color: #6c757d;
    margin-bottom: 0.8rem; padding-bottom: 0.4rem;
    border-bottom: 1px solid #dee2e6;
}

/* Subject card */
.subject-card {
    border: 1px solid #212529; padding: 1rem;
    text-align: center; margin-bottom: 0.5rem; background: #FFFFFF;
}
.subject-card .id {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.6rem; letter-spacing: 0.12em;
    text-transform: uppercase; color: #6c757d; margin-bottom: 0.2rem;
}
.subject-card .name {
    font-size: 1rem; font-weight: 600; color: #000000;
    margin-bottom: 0.2rem;
}
.subject-card .influence {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.3rem; font-weight: 700; color: #000000;
    margin-bottom: 0.15rem;
}
.subject-card .raw {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.6rem; color: #adb5bd;
}

/* Influence bar */
.inf-bar-wrap {
    width: 100%; height: 4px; background: #e9ecef;
    margin-top: 0.4rem;
}
.inf-bar {
    height: 4px; background: #000000;
    transition: width 0.3s ease;
}

/* Interruption arrow */
.int-arrow {
    text-align: center; padding-top: 0.5rem;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.75rem; font-weight: 500;
    color: #FF3333; letter-spacing: 0.05em;
}

/* Transcript */
.tx-entry {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.78rem; line-height: 1.65;
    padding: 0.45rem 0; border-bottom: 1px solid #f0f0f0; color: #212529;
}
.tx-entry .ts { color: #adb5bd; margin-right: 0.6rem; }
.tx-entry .spk { font-weight: 600; color: #000000; }
.tx-entry .cls-def { color: #000000; font-weight: 500; }
.tx-entry .cls-hes { color: #6c757d; font-weight: 400; font-style: italic; }
.tx-entry .cls-neu { color: #adb5bd; }
.tx-entry .int-flag { color: #FF3333; font-weight: 600; }

/* Event log */
.log-entry {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.72rem; color: #6c757d; line-height: 1.6;
    padding: 0.2rem 0; border-bottom: 1px solid #f8f9fa;
}

/* Sidebar */
section[data-testid="stSidebar"] .stMarkdown h2 {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.6rem !important; font-weight: 500 !important;
    letter-spacing: 0.15em !important; text-transform: uppercase !important;
    color: #6c757d !important;
    border-bottom: 1px solid #dee2e6; padding-bottom: 0.4rem;
    margin-top: 1.5rem !important; margin-bottom: 0.8rem !important;
}
.sb-person {
    padding: 0.5rem 0; border-bottom: 1px solid #e9ecef;
}
.sb-person .sb-name { font-weight: 600; font-size: 0.88rem; color: #000000; }
.sb-person .sb-status {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.6rem; letter-spacing: 0.06em;
    text-transform: uppercase; margin-left: 0.5rem;
}
.sb-person .sb-status.enrolled { color: #212529; }
.sb-person .sb-status.pending  { color: #FF3333; }
.sb-person .sb-meta {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.65rem; color: #adb5bd; margin-top: 0.1rem;
}
.sb-person .sb-influence {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.75rem; font-weight: 700; color: #000000;
}

/* Enrollment */
.enroll-script {
    border: 1px solid #212529; padding: 0.8rem 1rem;
    margin: 0.5rem 0; background: #FFFFFF;
    font-size: 0.82rem; line-height: 1.65; color: #212529;
}
.enroll-script .enroll-label {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.55rem; letter-spacing: 0.12em;
    text-transform: uppercase; color: #6c757d;
    margin-bottom: 0.4rem; font-weight: 500;
}

/* Listening */
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }
.listen-indicator {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.7rem; font-weight: 500;
    letter-spacing: 0.08em; text-transform: uppercase; color: #000000;
    display: inline-flex; align-items: center; gap: 0.5rem;
    border: 1px solid #212529; padding: 0.3rem 0.7rem; margin-top: 0.3rem;
}
.listen-dot {
    width: 6px; height: 6px; background: #FF3333;
    border-radius: 0; animation: blink 1.2s step-end infinite;
}

/* Buttons */
.stButton > button {
    border-radius: 0 !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important; font-size: 0.8rem !important;
    letter-spacing: 0.02em !important;
    border: 1px solid #212529 !important;
    background: #FFFFFF !important; color: #212529 !important;
    transition: background 0.1s ease, color 0.1s ease;
}
.stButton > button:hover {
    background: #212529 !important; color: #FFFFFF !important;
}
.stButton > button[kind="primary"] {
    background: #000000 !important; color: #FFFFFF !important;
    border-color: #000000 !important;
}
.stButton > button[kind="primary"]:hover { background: #333333 !important; }

.stSelectbox > div > div,
.stTextInput > div > div > input {
    border-radius: 0 !important; border-color: #212529 !important;
    font-size: 0.85rem !important;
}
.streamlit-expanderHeader {
    font-family: 'Roboto Mono', monospace !important;
    font-size: 0.7rem !important; font-weight: 500 !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
    color: #6c757d !important; border-bottom: 1px solid #dee2e6;
}

/* Leaderboard */
.leaderboard {
    border: 1px solid #212529;
    margin-bottom: 1rem;
}
.lb-row {
    display: flex; align-items: center;
    padding: 0.6rem 1rem;
    border-bottom: 1px solid #e9ecef;
}
.lb-row:last-child { border-bottom: none; }
.lb-rank {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.65rem; color: #adb5bd;
    width: 2rem; flex-shrink: 0;
}
.lb-name {
    font-weight: 600; font-size: 0.88rem; color: #000000;
    flex: 1;
}
.lb-pct {
    font-family: 'Roboto Mono', monospace;
    font-size: 1rem; font-weight: 700; color: #000000;
    width: 4.5rem; text-align: right; flex-shrink: 0;
}
.lb-bar-wrap {
    flex: 1; height: 3px; background: #e9ecef;
    margin: 0 1rem;
}
.lb-bar { height: 3px; background: #000000; }

/* Empty */
.empty-state { text-align: center; padding: 5rem 2rem; color: #adb5bd; }
.empty-state .mark {
    font-family: 'Roboto Mono', monospace; font-size: 2rem;
    color: #dee2e6; margin-bottom: 1rem;
}
.empty-state .msg { font-size: 0.85rem; color: #6c757d; }
</style>
    """, unsafe_allow_html=True)


def render_header():
    st.markdown("""
<div class="lab-header">
    <div class="lab-tag">Behavioral Analysis Laboratory</div>
    <h1>Conversational Power Dynamics</h1>
    <div class="sub">Attention-economy model — zero-sum ELO transfer with action-based decay</div>
</div>
""", unsafe_allow_html=True)
