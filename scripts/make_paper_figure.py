#!/usr/bin/env python3
"""Build the paper figures from the canonical values in reports/v3/ALL_RESULTS.md.

Every number below is transcribed from the canonical synthesis and must not be
edited independently of it.

Outputs:
- manuscript/figures/main_effects.pdf        (Results, full width)
- manuscript/figures/transition_matrices.pdf (Results, full width)
- manuscript/figures/point_size_means.pdf    (Appendix, full width)
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

MODELS = [
    "Qwen3.5\n27B",
    "Qwen3.6\n27B",
    "Qwen3.8\n27B",
    "Qwen3-VL\n32B",
    "Mistral\n24B",
    "Gemini\nFlash",
]

DIRECT = {
    "image": [14.86, 23.06, 8.33, 32.64, 26.25, 9.44],
    "text": [4.86, 2.78, 4.31, 4.72, 8.61, 6.11],
    "joint": [14.44, 15.42, 14.86, 32.92, 24.58, 24.58],
}
MISLEADING = {
    "image": [6.39, 6.11, 6.11, 9.86, 10.14, 6.67],
    "text": [3.75, 2.08, 3.47, 3.75, 2.78, 5.97],
    "joint": [7.64, 7.50, 7.08, 9.44, 11.53, 10.83],
}
BENIGN = {
    "image": [1.25, 1.94, 1.81, 1.39, 2.50, 2.08],
    "text": [0.56, 0.14, 0.14, 0.56, 0.56, 1.67],
    "joint": [1.53, 1.81, 1.53, 1.53, 2.92, 2.22],
}

# Okabe-Ito, print-safe and colorblind-friendly.
CHANNELS = ["image", "text", "joint"]
COLORS = {"image": "#0072B2", "text": "#E69F00", "joint": "#D55E00"}
LABELS = {"image": "Image", "text": "Text", "joint": "Joint"}

SERIF = ["Times New Roman", "Nimbus Roman", "DejaVu Serif"]


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": SERIF,
            "pdf.fonttype": 42,
            "text.usetex": False,
            "axes.linewidth": 0.7,
        }
    )


def tidy(ax) -> None:
    ax.yaxis.grid(True, color="0.88", linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("0.45")
        ax.spines[side].set_linewidth(0.7)


def draw_panel(ax, data, title) -> None:
    """Stack the matched-benign base and the attributable effect in one bar.

    The pale base is the modality-matched benign control rate; the saturated
    segment above it is the paired malicious-minus-benign effect. Total bar
    height is the full-cohort malicious downward rate.
    """
    width = 0.26
    idx = np.arange(len(MODELS))

    for j, ch in enumerate(CHANNELS):
        offset = (j - 1) * width
        base = np.asarray(BENIGN[ch], dtype=float)
        total = np.asarray(data[ch], dtype=float)

        ax.bar(
            idx + offset,
            base,
            width * 0.90,
            color=COLORS[ch],
            alpha=0.28,
            edgecolor="none",
            zorder=3,
        )
        ax.bar(
            idx + offset,
            total - base,
            width * 0.90,
            bottom=base,
            color=COLORS[ch],
            edgecolor="0.20",
            linewidth=0.4,
            zorder=4,
        )
        for i, value in enumerate(total):
            ax.text(
                idx[i] + offset,
                value + 0.55,
                f"{value:.1f}",
                ha="center",
                va="bottom",
                fontsize=5.6,
                color="0.28",
                zorder=6,
            )

    ax.set_xticks(idx)
    ax.set_xticklabels(MODELS, fontsize=7.5)
    ax.tick_params(axis="x", pad=2, length=0)
    ax.set_ylim(0, 38)
    ax.set_yticks(range(0, 36, 10))
    ax.tick_params(axis="y", labelsize=8, length=2.5, color="0.4")
    ax.set_title(title, fontsize=9, loc="left", pad=6)
    tidy(ax)


def write_main_effects(out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(6.75, 2.52), sharey=True)
    draw_panel(axes[0], DIRECT, "(a) Direct instruction")
    draw_panel(axes[1], MISLEADING, "(b) Misleading claim")
    axes[0].set_ylabel("Downward success  (% of 720)", fontsize=8.5)

    handles = [
        mpatches.Patch(facecolor=COLORS[ch], edgecolor="0.20", linewidth=0.4, label=LABELS[ch])
        for ch in CHANNELS
    ]
    handles.append(
        mpatches.Patch(
            facecolor="0.62", alpha=0.45, edgecolor="none", label="Matched benign control"
        )
    )
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=4,
        fontsize=8,
        frameon=False,
        bbox_to_anchor=(0.5, -0.03),
        handlelength=1.5,
        columnspacing=1.7,
    )

    fig.tight_layout(rect=(0, 0.10, 1, 1))
    out_path = out_dir / "main_effects.pdf"
    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    print(f"wrote {out_path}")


def write_transition_figure(out_dir: Path) -> None:
    """Six-model mean clean-to-attacked 3x3 matrices, coloured by direction."""
    matrices = {
        "Direct image": [[99.87, 0.13, 0.00], [71.11, 24.72, 4.17], [40.95, 1.86, 57.19]],
        "Direct text": [[99.64, 0.36, 0.00], [26.55, 71.40, 2.05], [2.20, 2.09, 95.72]],
        "Direct joint": [[99.53, 0.47, 0.00], [71.69, 24.76, 3.55], [48.10, 2.16, 49.74]],
        "Misleading image": [[99.41, 0.59, 0.00], [30.21, 69.12, 0.68], [2.78, 11.39, 85.83]],
        "Misleading text": [[99.34, 0.66, 0.00], [16.63, 82.95, 0.42], [0.54, 5.35, 94.12]],
        "Misleading joint": [[99.68, 0.32, 0.00], [35.61, 63.77, 0.62], [3.39, 14.20, 82.41]],
    }
    labels = ["Little/no", "Mild", "Severe"]

    downward = plt.get_cmap("Reds")
    upward = plt.get_cmap("Blues")
    unchanged = plt.get_cmap("Greys")

    def cell_colour(row: int, col: int, value: float):
        # Compress the ramp so that small but non-trivial rates stay visible.
        shade = 0.10 + 0.62 * (value / 100.0) ** 0.55
        if col < row:
            return downward(shade), ("white" if shade > 0.52 else "#3d0d0d")
        if col > row:
            return upward(shade), ("white" if shade > 0.52 else "#0d2340")
        return unchanged(0.06 + 0.30 * (value / 100.0)), "#1b1b1b"

    fig, axes = plt.subplots(2, 3, figsize=(6.75, 3.30))
    for ax, (title, values) in zip(axes.flat, matrices.items()):
        values = np.asarray(values, dtype=float)
        for row in range(3):
            for col in range(3):
                face, text_colour = cell_colour(row, col, values[row, col])
                ax.add_patch(
                    mpatches.Rectangle(
                        (col - 0.5, row - 0.5),
                        1,
                        1,
                        facecolor=face,
                        edgecolor="white",
                        linewidth=1.1,
                    )
                )
                ax.text(
                    col,
                    row,
                    f"{values[row, col]:.1f}",
                    ha="center",
                    va="center",
                    fontsize=7.0,
                    color=text_colour,
                )
        ax.set_xlim(-0.5, 2.5)
        ax.set_ylim(2.5, -0.5)
        ax.set_aspect("equal")
        ax.set_title(title, fontsize=8.5, pad=4)
        ax.set_xticks(range(3))
        ax.set_yticks(range(3))
        ax.tick_params(length=0, pad=1.5)
        for spine in ax.spines.values():
            spine.set_visible(False)

    for row_index in range(2):
        for col_index in range(3):
            ax = axes[row_index, col_index]
            if row_index == 1:
                ax.set_xticklabels(labels, fontsize=6.8)
                ax.set_xlabel("Attacked prediction", fontsize=7.5, labelpad=3)
            else:
                ax.set_xticklabels([])
            if col_index == 0:
                ax.set_yticklabels(labels, fontsize=6.8)
                ax.set_ylabel("Clean-correct label", fontsize=7.5, labelpad=3)
            else:
                ax.set_yticklabels([])

    legend_handles = [
        mpatches.Patch(facecolor=downward(0.55), edgecolor="white", label="Downward (under-triage)"),
        mpatches.Patch(facecolor=unchanged(0.22), edgecolor="white", label="Unchanged"),
        mpatches.Patch(facecolor=upward(0.55), edgecolor="white", label="Upward"),
    ]
    fig.legend(
        handles=legend_handles,
        loc="lower center",
        ncol=3,
        fontsize=7.8,
        frameon=False,
        bbox_to_anchor=(0.5, -0.015),
        handlelength=1.4,
        columnspacing=2.0,
    )

    fig.tight_layout(rect=(0, 0.055, 1, 1))
    out_path = out_dir / "transition_matrices.pdf"
    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    print(f"wrote {out_path}")


def write_pointsize_figure(out_dir: Path) -> None:
    """Per-model traces behind the unweighted mean, to show heterogeneity."""
    pts = [3, 6, 9, 12, 15]
    per_model = {
        "direct": {
            "Qwen3.5 27B": [5.00, 5.00, 8.33, 11.67, 13.33],
            "Qwen3.6 27B": [1.67, 3.33, 8.33, 13.33, 16.67],
            "Qwen3.8 27B": [0.00, 1.67, 6.67, 11.67, 11.67],
            "Qwen3-VL 32B": [3.33, 1.67, 8.33, 21.67, 26.67],
            "Mistral 24B": [0.00, 0.00, 1.67, 11.67, 11.67],
            "Gemini Flash": [0.00, 1.67, 1.67, 1.67, 1.67],
        },
        "misleading": {
            "Qwen3.5 27B": [3.33, 5.00, 8.33, 6.67, 8.33],
            "Qwen3.6 27B": [1.67, 3.33, 6.67, 8.33, 6.67],
            "Qwen3.8 27B": [0.00, 3.33, 8.33, 8.33, 8.33],
            "Qwen3-VL 32B": [3.33, 3.33, 6.67, 11.67, 11.67],
            "Mistral 24B": [0.00, 0.00, 1.67, 3.33, 3.33],
            "Gemini Flash": [0.00, 1.67, 3.33, 5.00, 3.33],
        },
    }
    means = {
        "direct": [1.67, 2.22, 5.83, 11.94, 13.61],
        "misleading": [1.39, 2.78, 5.83, 7.22, 6.94],
    }
    titles = {"direct": "(a) Direct instruction", "misleading": "(b) Misleading claim"}
    mean_colour = {"direct": "#0072B2", "misleading": "#D55E00"}
    annotate = {"direct": ["Qwen3-VL 32B", "Gemini Flash"], "misleading": ["Qwen3-VL 32B", "Mistral 24B"]}

    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.45), sharey=True)
    for ax, family in zip(axes, ["direct", "misleading"]):
        for name, series in per_model[family].items():
            ax.plot(pts, series, color="0.72", linewidth=0.8, zorder=2)
        for name in annotate[family]:
            series = per_model[family][name]
            ax.annotate(
                name,
                xy=(pts[-1], series[-1]),
                xytext=(2.4, 0),
                textcoords="offset points",
                fontsize=6.0,
                color="0.42",
                va="center",
            )
        ax.plot(
            pts,
            means[family],
            color=mean_colour[family],
            linewidth=1.9,
            marker="o",
            markersize=4.6,
            markeredgecolor="white",
            markeredgewidth=0.6,
            zorder=4,
            label="Six-model mean",
        )
        ax.set_xticks(pts)
        ax.set_xlim(2.2, 18.6)
        ax.set_ylim(0, 29)
        ax.set_yticks(range(0, 29, 7))
        ax.set_xlabel("Nominal size (pt $=$ px at 72 PPI)", fontsize=8)
        ax.set_title(titles[family], fontsize=9, loc="left", pad=5)
        ax.tick_params(labelsize=8, length=2.5, color="0.4")
        ax.legend(frameon=False, fontsize=7.5, loc="upper left", handlelength=1.4)
        tidy(ax)

    axes[0].set_ylabel("Downward success  (% of 60)", fontsize=8.5)
    fig.text(
        0.5,
        -0.045,
        "Grey traces are the six individual models. No within-model adjacent-size contrast is Holm-significant (0/48).",
        ha="center",
        fontsize=7.2,
        color="0.35",
    )
    fig.tight_layout()
    out_path = out_dir / "point_size_means.pdf"
    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    print(f"wrote {out_path}")


def main() -> None:
    set_style()
    out_dir = Path(__file__).resolve().parents[1] / "manuscript" / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_main_effects(out_dir)
    write_transition_figure(out_dir)
    write_pointsize_figure(out_dir)


if __name__ == "__main__":
    main()
