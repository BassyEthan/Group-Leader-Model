
from pyvis.network import Network
import tempfile
import os
import streamlit.components.v1 as components
from logic.dynamics import get_node_size

# ═══════════════════════════════════════════════════════════════════════════
#  GRAPH VISUALIZATION
# ═══════════════════════════════════════════════════════════════════════════

def render_graph(people, nodes, edges, influence):
    net = Network(
        height="500px", width="100%", directed=True,
        bgcolor="#FFFFFF", font_color="#000000",
    )
    net.set_options("""
    {
        "physics": {
            "enabled": true,
            "barnesHut": {
                "gravitationalConstant": -4000,
                "centralGravity": 0.5,
                "springLength": 160,
                "springConstant": 0.1,
                "damping": 0.85,
                "avoidOverlap": 0.3
            },
            "stabilization": {
                "enabled": true,
                "iterations": 200,
                "updateInterval": 25
            },
            "maxVelocity": 15,
            "minVelocity": 0.75
        },
        "interaction": {
            "hover": true,
            "zoomView": true,
            "dragView": true
        }
    }
    """)

    for person in people:
        node = nodes[person]
        pct = influence.get(person, 0)
        vis_size = get_node_size(pct)
        net.add_node(
            person,
            label=f"{person}\n{pct:.0f}%",
            size=vis_size,
            color={
                "background": "#FFFFFF",
                "border": "#000000",
                "highlight": {"background": "#F8F9FA", "border": "#000000"},
                "hover": {"background": "#F8F9FA", "border": "#000000"},
            },
            borderWidth=2,
            borderWidthSelected=3,
            font={"size": 14, "color": "#000000", "face": "Inter, Helvetica, sans-serif", "multi": True},
            shape="dot",
            title=(
                f"{person}\n"
                f"Influence: {pct:.1f}%\n"
                f"Raw Score: {node['raw_score']:.0f}\n"
                f"Statements: {node['statements']}\n"
                f"Hesitations: {node['hesitations']}"
            ),
        )

    for (src, dst), count in edges.items():
        net.add_edge(
            src, dst,
            value=count,
            width=2 + count,
            color={"color": "#FF3333", "highlight": "#FF3333", "hover": "#FF3333"},
            arrows={"to": {"enabled": True, "scaleFactor": 0.8}},
            label=str(count),
            font={"color": "#FF3333", "size": 11, "face": "Roboto Mono, monospace"},
            title=f"{src} interrupted {dst}: {count}x",
            smooth={"type": "curvedCW", "roundness": 0.15},
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w") as f:
        net.save_graph(f.name)
        f.seek(0)
        html_content = open(f.name, "r").read()
        os.unlink(f.name)

    html_content = html_content.replace(
        "<body>",
        '<body style="background:#FFFFFF; margin:0; border:1px solid #212529;">',
    )
    components.html(html_content, height=520, scrolling=False)
