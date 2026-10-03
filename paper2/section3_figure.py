"""Figure 3.1 of the LaTeX draft: the equivalence chain, drawn for print (loop0008 item 09).

    python -m paper2.section3_figure          # writes figures/sec3_fig1_chain.{pdf,png}

The same content as `figures/equivalence_chain.dot` (section 3's working figure,
1,473 pt wide, every edge labelled with its Lean theorem), cut to what a
6.5 in column can carry at 7-8 pt: the relations and their status, not the
theorem names, which are in the draft's footnotes and in `equivalences.md`.
Two edges of the working figure are left out because they follow from the
others: `mns = θ` (from `mns = vs + 1`, `vs = pw` and `θ = pw + 1`) and
`ns = vs + 1` (from `ns = mns`). Section 3's thirteenth member is added in its
graph form: the minimum progressive pebbling number of Kirousis & Papadimitriou
(1986), `mpb(G) = pw(G) + 1` (`mpb_eq_pathwidth_add_one`, any nonempty graph);
Lengauer's `pbw` is stated on derived dags and is left to the text. Edge styles:
solid, exact and proved; dashed, a band, proved; dotted, LaPaugh's `es = pes`,
the one relation not proved (no row needs it); dark red with a cross, a
Table 1 claim that is false, with a counterexample family proved.
"""

from __future__ import annotations

from pathlib import Path

FIGS = Path(__file__).resolve().parent / "figures"
RED = "#8b1a1a"
WIDTH, HEIGHT = 6.4, 3.6   # inches

# name: (x, y, label, false-claim?)
NODES = {
    "PLA": (0.45, 3.0, "simple PLA\nfolding", True),
    "MF": (1.5, 3.0, "multiple\nfolding", False),
    "T": (2.6, 3.0, "$t(M)$\ngate matrix\nlayout", False),
    "Z": (3.75, 3.0, "$Z(M)$\nMOSP", False),
    "PB": (4.95, 3.0, r"$\mathrm{mpb}(G)$" "\nprogr. pebbling", False),
    "VSG": (6.15, 3.0, "VSG\nvertex game", False),
    "L": (0.45, 1.85, "tracks\none-dim.\nlogic", False),
    "TH": (1.75, 1.85, r"$\theta(G)$" "\ninterval\nthickness", False),
    "PW": (3.3, 1.85, r"$\mathrm{pw}(G)$" "\npathwidth", False),
    "VS": (4.85, 1.85, r"$\mathrm{vs}(G)$" "\nvertex\nseparation", False),
    "PES": (6.15, 1.85, r"$\mathrm{pes}(G)$" "\nprogressive\nedge search", False),
    "SB": (1.45, 0.65, r"$\mathrm{sb}(G)$" "\nsplit\nbandwidth", False),
    "NU": (2.6, 0.65, r"$\nu(G)$" "\nnarrowness", False),
    "CW": (3.75, 0.65, "cw, mcw\ncutwidth", True),
    "MNS": (4.95, 0.65, r"$\mathrm{mns}(G)$" "\nmonotone\nnode search", False),
    "ES": (6.15, 0.65, r"$\mathrm{es}(G)$" "\nedge search", False),
    "NS": (4.95, -0.4, r"$\mathrm{ns}(G)$" "\nnode search", False),
}

# (a, b, label, style, curvature[, label position from a along the visible edge])
EDGES = [
    ("MF", "T", r"$=t$", "exact", 0),
    ("T", "Z", r"$=Z$", "exact", 0),
    ("Z", "PW", r"$Z=\mathrm{pw}+1$", "exact", 0),
    ("PB", "PW", r"$=\mathrm{pw}+1$", "exact", 0),
    ("L", "TH", r"$=\theta(H)$", "exact", 0),
    ("TH", "PW", r"$\theta=\mathrm{pw}+1$", "exact", 0),
    ("VS", "PW", r"$\mathrm{vs}=\mathrm{pw}$", "exact", 0),
    ("NU", "PW", r"$\nu=\mathrm{pw}+1$", "exact", 0, 0.4),
    ("VSG", "VS", r"$=\max(1,\mathrm{vs})$", "exact", 0),
    ("MNS", "VS", r"$=\mathrm{vs}+1$", "exact", 0),
    ("NS", "MNS", r"$\mathrm{ns}=\mathrm{mns}$", "exact", 0),
    ("SB", "PW", r"$\mathrm{pw}\leq\mathrm{sb}\leq\mathrm{pw}+1$", "band", 0, 0.3),
    ("PES", "VS", r"$\leq\mathrm{vs}+2$", "band", 0),
    ("ES", "VS", r"$\leq\mathrm{vs}+2$", "band", 0),
    ("ES", "PES", r"$\mathrm{es}=\mathrm{pes}$?", "gap", 0),
    ("PLA", "T", "✗ gap unbounded", "false", -0.3),
    ("CW", "PW", "✗ unbounded\non stars", "false", 0),
]


def draw() -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "font.family": "DejaVu Sans",
                         "mathtext.fontset": "dejavusans"})

    fig = plt.figure(figsize=(WIDTH, HEIGHT))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, 6.75)
    ax.set_ylim(-0.75, 3.55)
    ax.axis("off")

    boxes = {}
    for name, (x, y, label, false) in NODES.items():
        hub = name == "PW"
        boxes[name] = ax.text(
            x, y, label, ha="center", va="center", fontsize=8 if hub else 7.5,
            fontweight="bold" if hub else "normal", color=RED if false else "0.05",
            linespacing=1.15, zorder=3,
            bbox=dict(boxstyle="round,pad=0.3", fc="0.9" if hub else "white",
                      ec=RED if false else "0.15", lw=1.0 if hub else 0.6))
    fig.canvas.draw()

    styles = {"exact": ("-", "0.15"), "band": ((0, (4, 2)), "0.15"),
              "gap": ((0, (1, 2)), "0.35"), "false": ("-", RED)}
    inv = ax.transData.inverted()

    def border(name, towards):
        """Where the segment from a node's centre towards a point leaves its box."""
        bb = boxes[name].get_bbox_patch().get_window_extent()
        (x0, y0), (x1, y1) = inv.transform((bb.x0, bb.y0)), inv.transform((bb.x1, bb.y1))
        cx, cy = NODES[name][:2]
        dx, dy = towards[0] - cx, towards[1] - cy
        f = min(((x1 - x0) / 2) / abs(dx) if dx else 1e9, ((y1 - y0) / 2) / abs(dy) if dy else 1e9)
        return cx + f * dx, cy + f * dy

    for a, b, label, kind, rad, *at in EDGES:
        t = at[0] if at else 0.5
        ls, colour = styles[kind]
        ax.annotate("", xy=NODES[b][:2], xytext=NODES[a][:2],
                    arrowprops=dict(arrowstyle="-", ls=ls, color=colour, lw=0.8,
                                    patchA=boxes[a].get_bbox_patch(),
                                    patchB=boxes[b].get_bbox_patch(),
                                    shrinkA=0, shrinkB=0,
                                    connectionstyle=f"arc3,rad={rad}"), zorder=1)
        if not label:
            continue
        (xa, ya), (xb, yb) = NODES[a][:2], NODES[b][:2]
        if rad:   # the arc's apex: half the control point's offset from the chord
            x, y = (xa + xb) / 2 + rad * (yb - ya) / 2, (ya + yb) / 2 - rad * (xb - xa) / 2 + 0.08
            va, ha = "bottom", "center"
        else:
            pa, pb = border(a, (xb, yb)), border(b, (xa, ya))
            x, y = pa[0] + t * (pb[0] - pa[0]), pa[1] + t * (pb[1] - pa[1])
            if abs(yb - ya) < 0.05:   # horizontal: above the line
                y, va, ha = y + 0.03, "bottom", "center"
            elif abs(xb - xa) < 0.05:  # vertical: right of the line
                x, va, ha = x + 0.05, "center", "left"
            else:
                va, ha = "center", "center"
        ax.text(x, y, label, ha=ha, va=va, fontsize=7, color=colour, linespacing=1.05,
                zorder=2, bbox=dict(boxstyle="square,pad=0.06", fc="white", ec="none"))

    FIGS.mkdir(exist_ok=True)
    out = FIGS / "sec3_fig1_chain.pdf"
    fig.savefig(out, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(FIGS / "sec3_fig1_chain.png", dpi=200, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    return out


if __name__ == "__main__":
    print(draw())
