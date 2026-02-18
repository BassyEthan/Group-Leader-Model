
import re

# ═══════════════════════════════════════════════════════════════════════════
#  SPEECH CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════
HESITATION_PATTERNS = re.compile(
    r"\b(um+|uh+|er+|ah+|like|i guess|i think|maybe|sort of|kind of|you know|i mean)\b",
    re.IGNORECASE,
)
DEFINITIVE_PATTERNS = re.compile(
    r"\b(absolutely|definitely|certainly|always|never|clearly|obviously|"
    r"without a doubt|no question|proven|undeniable|guaranteed|must be|"
    r"i know for a fact|there is no way|i am sure|i am certain)\b",
    re.IGNORECASE,
)


def detect_hesitation(text):
    return bool(HESITATION_PATTERNS.search(text))


def detect_definitive(text):
    return bool(DEFINITIVE_PATTERNS.search(text))


def classify_speech(text):
    has_def = detect_definitive(text)
    has_hes = detect_hesitation(text)
    if has_def and not has_hes:
        return "definitive"
    if has_hes and not has_def:
        return "hesitation"
    if has_def and has_hes:
        d_count = len(DEFINITIVE_PATTERNS.findall(text))
        h_count = len(HESITATION_PATTERNS.findall(text))
        return "definitive" if d_count >= h_count else "hesitation"
    return "neutral"
