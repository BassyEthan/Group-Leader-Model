
import streamlit as st
import random
import io
import wave
import struct
import numpy as np

try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    RESEMBLYZER_AVAILABLE = True
except ImportError:
    RESEMBLYZER_AVAILABLE = False
    VoiceEncoder = None
    preprocess_wav = None

# ═══════════════════════════════════════════════════════════════════════════
#  ENROLLMENT SCRIPTS
# ═══════════════════════════════════════════════════════════════════════════
ENROLLMENT_SCRIPTS = [
    (
        "The sun dipped below the horizon, painting the sky in shades of amber "
        "and violet. A cool breeze swept through the valley, carrying the faint "
        "scent of pine. Somewhere in the distance, a bell chimed softly, marking "
        "the end of another quiet afternoon."
    ),
    (
        "Every morning the baker opens his shop before dawn, carefully measuring "
        "flour and water for the day's bread. The oven glows with a steady warmth "
        "as loaves rise slowly on the wooden rack. Neighbors gather at the counter, "
        "trading stories over fresh coffee and warm pastry."
    ),
    (
        "The library sat at the corner of Maple Street, its tall windows glowing "
        "with golden light. Inside, rows of leather-bound books lined the shelves "
        "from floor to ceiling. A grandfather clock ticked steadily near the entrance, "
        "keeping time for the readers lost in other worlds."
    ),
    (
        "Rain tapped gently against the window as the old cat stretched across the "
        "armchair. The fireplace crackled with a low, even flame, casting dancing "
        "shadows on the walls. A cup of tea sat cooling on the side table, its steam "
        "curling upward in thin wisps."
    ),
    (
        "The market square was alive with color and sound. Vendors called out prices "
        "for ripe tomatoes and bundles of fresh herbs. A musician played an accordion "
        "near the fountain, drawing a small crowd of children who clapped along to "
        "the cheerful melody."
    ),
]


def get_enrollment_script():
    return random.choice(ENROLLMENT_SCRIPTS)


# ═══════════════════════════════════════════════════════════════════════════
#  VOICE ENCODER
# ═══════════════════════════════════════════════════════════════════════════
@st.cache_resource
def load_voice_encoder():
    if RESEMBLYZER_AVAILABLE:
        return VoiceEncoder("cpu")
    return None


def audio_to_numpy(audio_data):
    """Convert SpeechRecognition AudioData to numpy array for Resemblyzer."""
    wav_bytes = audio_data.get_wav_data(convert_rate=16000, convert_width=2)
    with io.BytesIO(wav_bytes) as buf:
        with wave.open(buf, "rb") as wf:
            n_frames = wf.getnframes()
            raw = wf.readframes(n_frames)
            samples = struct.unpack(f"<{n_frames}h", raw)
            return np.array(samples, dtype=np.float32) / 32768.0


def identify_speaker(embedding, profiles, threshold=0.65):
    """Identify speaker from voice embedding against profiles."""
    if not profiles:
        return None, 0.0
    best_name = None
    best_score = 0.0
    for name, profile_emb in profiles.items():
        dot = np.dot(embedding, profile_emb)
        norm = np.linalg.norm(embedding) * np.linalg.norm(profile_emb)
        if norm == 0:
            continue
        score = dot / norm
        if score > best_score:
            best_score = score
            best_name = name
    if best_score >= threshold:
        return best_name, float(best_score)
    return None, 0.0
