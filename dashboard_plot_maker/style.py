from __future__ import annotations

from typing import Dict, Iterable, Tuple


# Matches `dashboard/src/pages/GlobePage.tsx` cluster palette
CLUSTER_COLORS: Dict[int, str] = {
    0: "#e63946",
    1: "#2563eb",
    2: "#facc15",
    3: "#22c55e",
    4: "#a855f7",
    5: "#f97316",
}

# Dashboard placeholder frame (`.mplImageFrame`) is a dark translucent layer.
# Matplotlib needs an opaque color, so we approximate the on-screen result.
BG = "#14141a"
FG = "#ffffff"
# Approximate dashboard opacities using hex equivalents.
MUTED = "#a6a6a6"  # 0.65 alpha over white
GRID = "#ffffff"
SPINE = "#2e2e2e"  # ~0.18 alpha over white
GRID_ALPHA = 0.10


def cluster_color(cluster_id: int) -> str:
    """
    Cluster colors consistent with globe pins.
    We treat clusters 6 & 7 as "white" (they show up as 5 and 6 under 0..K-1 indexing).
    """

    if cluster_id in (5, 6):
        return "#ffffff"
    return CLUSTER_COLORS.get(cluster_id, "#ffffff")


def apply_dashboard_style() -> None:
    import matplotlib as mpl

    mpl.rcParams["font.family"] = "sans-serif"
    mpl.rcParams["font.sans-serif"] = [
        "Inter",
        "SF Pro Display",
        "SF Pro Text",
        "Segoe UI Variable",
        "Segoe UI",
        "Helvetica Neue",
        "Arial",
        "DejaVu Sans",
    ]

    mpl.rcParams.update(
        {
            "figure.facecolor": BG,
            "savefig.facecolor": BG,
            "axes.facecolor": BG,
            "axes.edgecolor": SPINE,
            "axes.labelcolor": MUTED,
            "axes.titlecolor": FG,
            "xtick.labelsize": 12,
            "ytick.labelsize": 12,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "grid.color": GRID,
            "grid.alpha": GRID_ALPHA,
            "axes.grid": True,
            "axes.grid.axis": "both",
            "axes.titleweight": 600,
            "axes.titlesize": 17,
            "axes.labelsize": 14,
            "legend.facecolor": "#0f1428",
            "legend.edgecolor": SPINE,
            "legend.framealpha": 0.95,
            "legend.fontsize": 12,
            "lines.linewidth": 2.2,
            "lines.antialiased": True,
            "figure.dpi": 200,
        }
    )


def style_axes(ax) -> None:
    # Make sure grid and spines are consistent even if rcParams get overridden.
    ax.grid(True, alpha=0.35, linewidth=0.8)
    for spine in ax.spines.values():
        spine.set_color(SPINE)
        spine.set_alpha(1.0)

