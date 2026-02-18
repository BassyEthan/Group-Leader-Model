
# ═══════════════════════════════════════════════════════════════════════════
#  POWER ENGINE
# ═══════════════════════════════════════════════════════════════════════════
BASE_SCORE = 100
FLOOR = 10
DECAY_RATE = 0.95          # 5% silence penalty
DEFINITIVE_GAIN = 15
HESITATION_PENALTY = 10
INTERRUPT_TRANSFER = 15
VISUAL_MULTIPLIER = 180    # scales influence % → pyvis node size

def apply_decay(nodes):
    """Apply 5% silence penalty to every subject. Called before each action."""
    for name in nodes:
        nodes[name]["raw_score"] = max(FLOOR, nodes[name]["raw_score"] * DECAY_RATE)


def apply_definitive(nodes, person):
    """Definitive statement: decay all, then +15 to speaker."""
    apply_decay(nodes)
    nodes[person]["raw_score"] += DEFINITIVE_GAIN
    nodes[person]["statements"] += 1


def apply_hesitation(nodes, person):
    """Hesitation: decay all, then -10 to speaker."""
    apply_decay(nodes)
    nodes[person]["raw_score"] = max(FLOOR, nodes[person]["raw_score"] - HESITATION_PENALTY)
    nodes[person]["hesitations"] += 1


def apply_interruption(nodes, interrupter, interrupted):
    """ELO steal: decay all, then +15 to interrupter, -15 to interrupted."""
    apply_decay(nodes)
    nodes[interrupter]["raw_score"] += INTERRUPT_TRANSFER
    nodes[interrupted]["raw_score"] = max(FLOOR, nodes[interrupted]["raw_score"] - INTERRUPT_TRANSFER)


def get_influence(nodes):
    """Zero-sum normalization. Returns {name: percentage} (0-100)."""
    total = sum(n["raw_score"] for n in nodes.values())
    if total == 0:
        count = len(nodes) or 1
        return {name: 100.0 / count for name in nodes}
    return {name: (n["raw_score"] / total) * 100 for name, n in nodes.items()}


def get_node_size(influence_pct):
    """Convert influence % → Pyvis node pixel size."""
    return max(8, (influence_pct / 100) * VISUAL_MULTIPLIER)
