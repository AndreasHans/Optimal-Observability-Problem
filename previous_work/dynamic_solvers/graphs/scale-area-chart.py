import math
import plotly.graph_objects as go

# --- Input data ---
raw = {
    # "line": ("193", "15001"),
    "grid": ("15x15", "100x100"),
    "maze": ("49x25", "1049x525"),
}

def parse_dim(token):
    """Parse 'WxH' or a single number (treated as square area)."""
    s = token.strip().lower()
    if "x" in s:
        w, h = map(int, s.split("x"))
    else:
        length = int(s)
        w, h = length, 1
    return w, h

# --- Parse and compute areas ---
data = {}
for name, (small_tok, large_tok) in raw.items():
    small = parse_dim(small_tok)
    large = parse_dim(large_tok)
    data[name] = {
        "small": small,
        "large": large,
        "area_small": small[0] * small[1],
        "area_large": large[0] * large[1],
    }

# --- Layout settings ---
FIG_W, FIG_H = 1000, 1000
PADDING = 40
GAP_BETWEEN_GROUPS = 120

# --- Scaling ---
max_w = max(v["large"][0] for v in data.values())
max_h = max(v["large"][1] for v in data.values())
scale = min((FIG_W - 2 * PADDING) / (3 * max_w),
            (FIG_H - 2 * PADDING) / max_h)

# --- Distinct color schemes ---
world_colors = {
    "line": {"large": "rgba(255,99,71,0.4)",  "small": "rgba(220,20,60,0.9)"},   # reds
    "grid": {"large": "rgba(60,179,113,0.4)", "small": "rgba(0,100,0,0.9)"},     # greens
    "maze": {"large": "rgba(65,105,225,0.4)", "small": "rgba(25,25,112,0.9)"},   # blues
}

# --- Create figure ---
fig = go.Figure()
x_cursor = PADDING
y_base = PADDING

for name, vals in data.items():
    wL, hL = vals["large"]
    wS, hS = vals["small"]

    # Scaled sizes
    lw, lh = wL * scale, hL * scale
    sw, sh = wS * scale, hS * scale

    # Base positions (large rect)
    x0L, y0L = x_cursor, y_base
    x1L, y1L = x0L + lw, y0L + lh

    # Small rect: same corner (bottom-left anchored)
    x0S, y0S = x0L, y0L
    x1S, y1S = x0S + sw, y0S + sh

    colors = world_colors[name]

    # Large rectangle
    fig.add_shape(
        type="rect",
        x0=x0L, y0=y0L, x1=x1L, y1=y1L,
        line=dict(color=colors["large"].replace("0.4", "1"), width=2),
        fillcolor=colors["large"],
    )

    # Small rectangle (nested from same corner)
    fig.add_shape(
        type="rect",
        x0=x0S, y0=y0S, x1=x1S, y1=y1S,
        line=dict(color=colors["small"].replace("0.9", "1"), width=2),
        fillcolor=colors["small"],
    )

    # Label
    fig.add_annotation(
        x=(x0L + x1L) / 2,
        y=y1L + 20,
        text=f"<b>{name}</b><br>"
             f"Large: {wL}×{hL} (A={vals['area_large']:,})<br>"
             f"Small: {wS}×{hS} (A={vals['area_small']:,})",
        showarrow=False,
        font=dict(size=12),
        align="center",
    )

    # Invisible trace for autoscaling
    fig.add_trace(go.Scatter(
        x=[x0L, x1L],
        y=[y0L, y1L],
        mode="markers",
        marker_opacity=0,
        showlegend=False,
    ))

    # Move cursor for next world
    x_cursor += lw + GAP_BETWEEN_GROUPS

# --- Layout ---
fig.update_layout(
    title="Nested Rectangle Area Chart",
    xaxis=dict(showgrid=False, zeroline=False, visible=False),
    yaxis=dict(showgrid=False, zeroline=False, visible=False),
    width=FIG_W,
    height=FIG_H,
    margin=dict(l=20, r=20, t=80, b=20),
    plot_bgcolor="white",
)

fig.show()