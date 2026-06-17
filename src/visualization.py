"""
Result visualization.

The original project's README claimed graphs were available in
`results/`, but nothing in the code actually generated them — the files
there were manually created samples. This module generates a real
error-rate comparison chart from whatever scenarios were actually run,
and saves it to disk (no GUI required, so it also works headlessly/in CI).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import matplotlib

matplotlib.use("Agg")  # headless-safe backend; must be set before pyplot import
import matplotlib.pyplot as plt


def plot_error_rate_comparison(results: Dict[str, float], output_path: str | Path) -> Path:
    """
    Save a bar chart comparing QBER across named scenarios.

    Args:
        results: mapping of scenario label -> error rate, e.g.
            {"No Attack": 0.0, "Attack": 0.25}.
        output_path: where to save the PNG.

    Returns:
        The resolved Path the chart was written to.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    labels = list(results.keys())
    values = list(results.values())

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, values, color=["#2e7d32", "#c62828"][: len(labels)])
    ax.axhline(0.11, color="gray", linestyle="--", linewidth=1, label="Detection threshold (0.11)")
    ax.set_ylabel("Quantum Bit Error Rate (QBER)")
    ax.set_title("Error Rate Comparison: Normal vs. Attack Scenario")
    ax.set_ylim(0, max(0.3, max(values) * 1.2 if values else 0.3))
    ax.legend()

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{value:.2f}",
            ha="center",
            va="bottom",
        )

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path
