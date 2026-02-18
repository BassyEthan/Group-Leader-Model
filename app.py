
import streamlit as st
import threading
import queue
import time
import random
import json

# Local Modules
from logic.dynamics import (
    BASE_SCORE,
    apply_decay,
    apply_definitive,
    apply_hesitation,
    apply_interruption,
    get_influence,
    DEFINITIVE_GAIN,
    HESITATION_PENALTY,
    INTERRUPT_TRANSFER,
)
from logic.analysis import classify_speech
from ui.components import load_css, render_header
from ui.graphs import render_graph
from audio_modules.voice import (
    load_voice_encoder,
    get_enrollment_script,
    audio_to_numpy,
    preprocess_wav,
    RESEMBLYZER_AVAILABLE,
)
from audio_modules.listener import AudioListener
import speech_recognition as sr # Needed for enrollment button inside app.py

# ═══════════════════════════════════════════════════════════════════════════
#  CONFIG & CSS
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Conversational Power Dynamics — Behavioral Lab",
    layout="wide",
)
load_css()
render_header()

# ═══════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════
for key, default in [
    ("people", []),
    ("nodes", {}),
    ("edges", {}),
    ("log", []),
    ("transcript", []),
    ("audio_queue", queue.Queue()),
    ("listener", None),
    ("listening", False),
    ("voice_profiles", {}),
    ("enrollment_scripts", {}),
]:
    if key not in st.session_state:
        st.session_state[key] = default

try:
    import speech_recognition as sr_check
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════
#  COMPUTED METRICS
# ═══════════════════════════════════════════════════════════════════════════
total_people = len(st.session_state.people)
total_statements = sum(n["statements"] for n in st.session_state.nodes.values())
total_hesitations = sum(n["hesitations"] for n in st.session_state.nodes.values())
total_interruptions = sum(st.session_state.edges.values())
enrolled_count = sum(
    1 for p in st.session_state.people if p in st.session_state.voice_profiles
)
influence = get_influence(st.session_state.nodes)

if total_people > 0:
    st.markdown(f"""
    <div class="data-strip">
        <div class="cell">
            <div class="lbl">Subjects</div>
            <div class="val">{total_people}</div>
        </div>
        <div class="cell">
            <div class="lbl">Definitive</div>
            <div class="val">{total_statements}</div>
        </div>
        <div class="cell">
            <div class="lbl">Hesitations</div>
            <div class="val">{total_hesitations}</div>
        </div>
        <div class="cell">
            <div class="lbl">Interruptions</div>
            <div class="val int-val">{total_interruptions}</div>
        </div>
        <div class="cell">
            <div class="lbl">Enrolled</div>
            <div class="val">{enrolled_count}/{total_people}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════

st.sidebar.markdown("## Subjects")

new_person = st.sidebar.text_input(
    "Name", placeholder="Enter subject name...", label_visibility="collapsed",
)
if st.sidebar.button("Add Subject", use_container_width=True) and new_person.strip():
    name = new_person.strip()
    if name not in st.session_state.nodes:
        st.session_state.people.append(name)
        st.session_state.nodes[name] = {
            "raw_score": BASE_SCORE,
            "statements": 0,
            "hesitations": 0,
        }
        st.rerun()
    else:
        st.sidebar.warning(f"'{name}' already exists.")

for person in st.session_state.people:
    node = st.session_state.nodes[person]
    pct = influence.get(person, 0)
    is_enrolled = person in st.session_state.voice_profiles
    status_cls = "enrolled" if is_enrolled else "pending"
    status_txt = "ENROLLED" if is_enrolled else "NOT ENROLLED"
    st.sidebar.markdown(
        f'<div class="sb-person">'
        f'<span class="sb-name">{person}</span>'
        f'<span class="sb-status {status_cls}">{status_txt}</span>'
        f'<br><span class="sb-influence">{pct:.1f}%</span>'
        f'<div class="sb-meta">'
        f'RAW:{node["raw_score"]:.0f}  S:{node["statements"]}  H:{node["hesitations"]}'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Voice Enrollment ──
if SR_AVAILABLE and RESEMBLYZER_AVAILABLE and st.session_state.people:
    st.sidebar.markdown("## Voice Enrollment")
    unenrolled = [
        p for p in st.session_state.people
        if p not in st.session_state.voice_profiles
    ]
    if not unenrolled:
        st.sidebar.markdown(
            '<span style="font-family:Roboto Mono,monospace; font-size:0.7rem; '
            'color:#212529; letter-spacing:0.06em;">ALL SUBJECTS ENROLLED</span>',
            unsafe_allow_html=True,
        )
    else:
        encoder = load_voice_encoder()
        for person in unenrolled:
            if person not in st.session_state.enrollment_scripts:
                st.session_state.enrollment_scripts[person] = get_enrollment_script()
            script = st.session_state.enrollment_scripts[person]
            st.sidebar.markdown(
                f'<div class="enroll-script">'
                f'<div class="enroll-label">Read aloud — {person}</div>'
                f'{script}'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.sidebar.button(
                f"Record {person} — 10 sec",
                key=f"enroll_{person}",
                use_container_width=True,
            ):
                with st.sidebar:
                    with st.spinner(f"Recording {person}..."):
                        try:
                            recognizer = sr.Recognizer()
                            mic = sr.Microphone()
                            with mic as source:
                                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                                audio = recognizer.record(source, duration=10)
                            wav_np = audio_to_numpy(audio)
                            processed = preprocess_wav(wav_np, source_sr=16000)
                            embedding = encoder.embed_utterance(processed)
                            st.session_state.voice_profiles[person] = embedding
                            st.session_state.enrollment_scripts.pop(person, None)
                            st.rerun()
                        except Exception as e:
                            st.sidebar.error(f"Failed: {e}")

elif not RESEMBLYZER_AVAILABLE and SR_AVAILABLE and st.session_state.people:
    st.sidebar.markdown("## Voice Enrollment")
    st.sidebar.markdown(
        '<span style="font-family:Roboto Mono,monospace; font-size:0.7rem; color:#6c757d;">'
        'pip install resemblyzer</span>',
        unsafe_allow_html=True,
    )

# ── Listening ──
st.sidebar.markdown("## Recording")

if not SR_AVAILABLE:
    st.sidebar.error("pip install SpeechRecognition pyaudio")

if SR_AVAILABLE and st.session_state.people:
    all_enrolled = all(
        p in st.session_state.voice_profiles for p in st.session_state.people
    )
    if not all_enrolled:
        st.sidebar.selectbox(
            "Fallback speaker", st.session_state.people, key="active_speaker",
        )
    if not st.session_state.listening:
        if st.sidebar.button("Start Recording", use_container_width=True, type="primary"):
            enc = load_voice_encoder() if RESEMBLYZER_AVAILABLE else None
            listener = AudioListener(
                st.session_state.audio_queue, enc, st.session_state.voice_profiles,
            )
            listener.start()
            st.session_state.listener = listener
            st.session_state.listening = True
            st.rerun()
    else:
        st.sidebar.markdown(
            '<div class="listen-indicator">'
            '<span class="listen-dot"></span> REC</div>',
            unsafe_allow_html=True,
        )
        if st.sidebar.button("Stop Recording", use_container_width=True):
            if st.session_state.listener:
                st.session_state.listener.stop()
            st.session_state.listening = False
            st.rerun()
elif SR_AVAILABLE:
    st.sidebar.markdown(
        '<span style="font-family:Roboto Mono,monospace; font-size:0.7rem; '
        'color:#adb5bd;">Add subjects to begin</span>',
        unsafe_allow_html=True,
    )

# ── Export Session ──
st.sidebar.markdown("## Export")

def build_export_json():
    inf = get_influence(st.session_state.nodes)
    subjects = []
    for name in st.session_state.people:
        node = st.session_state.nodes[name]
        subjects.append({
            "name": name,
            "raw_score": round(node["raw_score"], 2),
            "influence_pct": round(inf.get(name, 0), 2),
            "statements": node["statements"],
            "hesitations": node["hesitations"],
        })
    edges = []
    for (src, dst), count in st.session_state.edges.items():
        edges.append({
            "interrupter": src,
            "interrupted": dst,
            "count": count,
        })
    transcript = []
    for entry in st.session_state.transcript:
        if isinstance(entry, dict):
            t = {
                "time": entry.get("time", ""),
                "speaker": entry.get("speaker", ""),
                "text": entry.get("text", ""),
                "classification": entry.get("classification", ""),
            }
            if entry.get("confidence"):
                t["confidence"] = entry["confidence"].strip()
            if entry.get("interrupted"):
                t["interrupted"] = entry["interrupted"]
            transcript.append(t)
        else:
            transcript.append({"raw": str(entry)})
    return json.dumps({
        "exported_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "subjects": subjects,
        "transcript": transcript,
        "interaction_graph": edges,
        "event_log": list(st.session_state.log),
    }, indent=2)

if st.session_state.people:
    st.sidebar.download_button(
        label="Export Session (JSON)",
        data=build_export_json(),
        file_name=f"session_{time.strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True,
    )
else:
    st.sidebar.markdown(
        '<span style="font-family:Roboto Mono,monospace; font-size:0.7rem; '
        'color:#adb5bd;">No data to export</span>',
        unsafe_allow_html=True,
    )

# ── Reset ──
st.sidebar.markdown("---")
if st.sidebar.button("Reset Session", use_container_width=True):
    if st.session_state.listener and st.session_state.listener.running:
        st.session_state.listener.stop()
    for key in [
        "people", "nodes", "edges", "log", "transcript",
        "listening", "voice_profiles", "enrollment_scripts",
    ]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.audio_queue = queue.Queue()
    st.session_state.listener = None
    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
#  PROCESS AUDIO QUEUE
# ═══════════════════════════════════════════════════════════════════════════
if st.session_state.listening:
    processed = False
    fallback_speaker = st.session_state.get("active_speaker", None)
    while not st.session_state.audio_queue.empty():
        try:
            result = st.session_state.audio_queue.get_nowait()
        except queue.Empty:
            break
        if isinstance(result, str):
            text = result
            speaker = fallback_speaker
            confidence = 0.0
            interrupted_person = None
        else:
            text = result["text"]
            speaker = result["speaker"]
            confidence = result["confidence"]
            interrupted_person = result["interrupted"]
        
        if text.startswith("[STT ERROR") or text.startswith("[AUDIO ERROR"):
            st.session_state.log.append(text)
            continue
        
        if speaker is None:
            speaker = fallback_speaker
        
        conf_str = f" {confidence:.0%}" if confidence > 0 else ""
        classification = classify_speech(text)
        
        st.session_state.transcript.append({
            "speaker": speaker or "UNKNOWN",
            "confidence": conf_str,
            "text": text,
            "classification": classification,
            "interrupted": interrupted_person,
            "time": time.strftime("%H:%M:%S"),
        })
        
        if speaker and speaker in st.session_state.nodes:
            if classification == "definitive":
                apply_definitive(st.session_state.nodes, speaker)
                st.session_state.log.append(
                    f'{time.strftime("%H:%M:%S")}  {speaker}  DEFINITIVE  +{DEFINITIVE_GAIN}  "{text}"'
                )
                processed = True
            elif classification == "hesitation":
                apply_hesitation(st.session_state.nodes, speaker)
                st.session_state.log.append(
                    f'{time.strftime("%H:%M:%S")}  {speaker}  HESITATION  -{HESITATION_PENALTY}  "{text}"'
                )
                processed = True
            else:
                # Neutral still triggers decay (silence penalty to everyone)
                apply_decay(st.session_state.nodes)
                st.session_state.log.append(
                    f'{time.strftime("%H:%M:%S")}  {speaker}  NEUTRAL     ~decay  "{text}"'
                )
                processed = True
        
        if interrupted_person and speaker and interrupted_person != speaker:
            if (
                interrupted_person in st.session_state.nodes
                and speaker in st.session_state.nodes
            ):
                apply_interruption(
                    st.session_state.nodes, speaker, interrupted_person,
                )
                edge_key = (speaker, interrupted_person)
                st.session_state.edges[edge_key] = (
                    st.session_state.edges.get(edge_key, 0) + 1
                )
                st.session_state.log.append(
                    f'{time.strftime("%H:%M:%S")}  {speaker} -> {interrupted_person}  '
                    f'INTERRUPTION  +/-{INTERRUPT_TRANSFER}'
                )
                processed = True
    
    if processed:
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════
if st.session_state.people:

    # Recompute influence after any queue processing
    influence = get_influence(st.session_state.nodes)

    # ── Leaderboard ─────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Influence Leaderboard</div>', unsafe_allow_html=True)
    
    ranked = sorted(influence.items(), key=lambda x: x[1], reverse=True)
    lb_html = '<div class="leaderboard">'
    for rank, (name, pct) in enumerate(ranked, 1):
        raw = st.session_state.nodes[name]["raw_score"]
        lb_html += (
            f'<div class="lb-row">'
            f'<span class="lb-rank">{str(rank).zfill(2)}</span>'
            f'<span class="lb-name">{name}</span>'
            f'<div class="lb-bar-wrap"><div class="lb-bar" style="width:{pct:.1f}%"></div></div>'
            f'<span class="lb-pct">{pct:.1f}%</span>'
            f'</div>'
        )
    lb_html += '</div>'
    st.markdown(lb_html, unsafe_allow_html=True)

    st.divider()

    # ── Manual Controls ─────────────────────────────────────────────────
    st.markdown('<div class="section-label">Manual Controls</div>', unsafe_allow_html=True)

    cols = st.columns(len(st.session_state.people))
    for i, person in enumerate(st.session_state.people):
        with cols[i]:
            idx = str(i + 1).zfill(2)
            pct = influence.get(person, 0)
            raw = st.session_state.nodes[person]["raw_score"]
            st.markdown(
                f'<div class="subject-card">'
                f'<div class="id">Subject {idx}</div>'
                f'<div class="name">{person}</div>'
                f'<div class="influence">{pct:.1f}%</div>'
                f'<div class="raw">RAW {raw:.0f}</div>'
                f'<div class="inf-bar-wrap"><div class="inf-bar" style="width:{pct:.1f}%"></div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Definitive", key=f"def_{person}", use_container_width=True):
                    apply_definitive(st.session_state.nodes, person)
                    st.session_state.log.append(
                        f'{time.strftime("%H:%M:%S")}  {person}  DEFINITIVE  +{DEFINITIVE_GAIN}  (manual)'
                    )
                    st.rerun()
            with c2:
                if st.button("Hesitation", key=f"hes_{person}", use_container_width=True):
                    apply_hesitation(st.session_state.nodes, person)
                    st.session_state.log.append(
                        f'{time.strftime("%H:%M:%S")}  {person}  HESITATION  -{HESITATION_PENALTY}  (manual)'
                    )
                    st.rerun()

    st.divider()

    # ── Interruption ────────────────────────────────────────────────────
    if len(st.session_state.people) >= 2:
        st.markdown('<div class="section-label">Log Interruption</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            interrupter = st.selectbox(
                "Interrupter", st.session_state.people, key="int_from",
                label_visibility="collapsed",
            )
        with col2:
            st.markdown(
                '<div class="int-arrow">INTERRUPTS &#8594;</div>',
                unsafe_allow_html=True,
            )
        with col3:
            interrupted_sel = st.selectbox(
                "Interrupted", st.session_state.people, key="int_to",
                label_visibility="collapsed",
            )
        if st.button("Log Interruption", use_container_width=True):
            if interrupter == interrupted_sel:
                st.warning("A subject cannot interrupt themselves.")
            else:
                apply_interruption(
                    st.session_state.nodes, interrupter, interrupted_sel,
                )
                edge_key = (interrupter, interrupted_sel)
                st.session_state.edges[edge_key] = (
                    st.session_state.edges.get(edge_key, 0) + 1
                )
                st.session_state.log.append(
                    f'{time.strftime("%H:%M:%S")}  {interrupter} -> {interrupted_sel}  '
                    f'INTERRUPTION  +/-{INTERRUPT_TRANSFER}  (manual)'
                )
                st.rerun()
        st.divider()

    # ── Graph ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Interaction Graph</div>', unsafe_allow_html=True)
    render_graph(st.session_state.people, st.session_state.nodes, st.session_state.edges, influence)

    st.divider()

    # ── Live Transcript ─────────────────────────────────────────────────
    if st.session_state.transcript:
        with st.expander("Live Transcript", expanded=st.session_state.listening):
            for entry in reversed(st.session_state.transcript[-50:]):
                if isinstance(entry, dict):
                    cls = entry["classification"]
                    spk = entry["speaker"]
                    conf = entry["confidence"]
                    txt = entry["text"]
                    ts = entry.get("time", "")
                    interrupted = entry.get("interrupted")
                    if cls == "definitive":
                        cls_span = '<span class="cls-def">[DEFINITIVE]</span>'
                    elif cls == "hesitation":
                        cls_span = '<span class="cls-hes">[HESITATION]</span>'
                    else:
                        cls_span = '<span class="cls-neu">[NEUTRAL]</span>'
                    line = (
                        f'<div class="tx-entry">'
                        f'<span class="ts">{ts}</span>'
                        f'<span class="spk">{spk}{conf}</span> '
                        f'{cls_span} {txt}'
                    )
                    if interrupted:
                        line += (
                            f' <span class="int-flag">'
                            f'[INTERRUPTED {interrupted.upper()}]</span>'
                        )
                    line += "</div>"
                    st.markdown(line, unsafe_allow_html=True)
                else:
                    st.text(entry)

    # ── Event Log ───────────────────────────────────────────────────────
    with st.expander("Event Log", expanded=False):
        if st.session_state.log:
            for entry in reversed(st.session_state.log):
                st.markdown(
                    f'<div class="log-entry">{entry}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="log-entry">No events recorded.</div>',
                unsafe_allow_html=True,
            )

    # ── Auto-refresh ────────────────────────────────────────────────────
    if st.session_state.listening:
        time.sleep(2)
        st.rerun()

else:
    st.markdown("""
    <div class="empty-state">
        <div class="mark">+</div>
        <div class="msg">Add subjects in the sidebar to begin observation.</div>
    </div>
    """, unsafe_allow_html=True)
