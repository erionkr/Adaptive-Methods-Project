"""
Generate a synthetic non-convex optimizer reference plot.

The classification losses in the main experiments are mostly convex or only
weakly non-convex. This script adds a standard Rosenbrock benchmark to make the
benefit of Adam's momentum + per-coordinate adaptation visible on a curved
non-convex objective.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
sys.path.insert(0, str(ROOT))

from src.optimizers import SGD, Adagrad, AdagradNorm, RMSprop, Adam
from src.losses import rosenbrock_loss, rosenbrock_grad


def run_optimizer(make_opt, w0, steps=3000):
    opt = make_opt()
    w = w0.astype(float).copy()
    values = [rosenbrock_loss(w)]
    path = [w.copy()]
    for _ in range(steps):
        w = opt.step(w, rosenbrock_grad(w))
        values.append(rosenbrock_loss(w))
        path.append(w.copy())
    return np.array(values), np.array(path)


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    w0 = np.array([-1.0, 1.0])
    steps = 2000
    configs = [
        ("SGD", lambda: SGD(lr=2e-4), "#4C78A8"),
        ("Adagrad", lambda: Adagrad(lr=0.08), "#F58518"),
        ("AdaGrad-Norm", lambda: AdagradNorm(lr=0.08, b0=0.1), "#54A24B"),
        ("RMSprop", lambda: RMSprop(lr=0.001, rho=0.99), "#E45756"),
        ("Adam", lambda: Adam(lr=0.005, beta1=0.9, beta2=0.999), "#8A3FFC"),
    ]

    snapshot_step = 240
    xs = np.linspace(-1.5, 1.5, 420)
    ys = np.linspace(-0.5, 2.0, 420)
    X, Y = np.meshgrid(xs, ys)
    Z = (1 - X) ** 2 + 100 * (Y - X * X) ** 2
    Z_plot = np.log10(Z + 1e-2)

    results = []
    for name, make_opt, color in configs:
        values, path = run_optimizer(make_opt, w0, steps)
        results.append((name, values, path, color))

    fig, ax = plt.subplots(figsize=(8.7, 4.55))
    levels = np.linspace(Z_plot.min(), Z_plot.max(), 42)
    ax.contour(X, Y, Z_plot, levels=levels, cmap="viridis", linewidths=0.75, alpha=0.95)
    valley_x = np.linspace(-1.5, 1.5, 260)
    ax.plot(valley_x, valley_x ** 2, color="white", lw=2.6, alpha=0.92)
    ax.scatter([1.0], [1.0], marker="*", s=150, color="#C23B4A",
               edgecolor="white", linewidth=0.8, label="Minimum (1, 1)", zorder=7)

    styles = {
        "SGD": "-",
        "Adagrad": "--",
        "AdaGrad-Norm": "-.",
        "RMSprop": (0, (4, 2)),
        "Adam": "-",
    }
    for name, values, path, color in results:
        shown = path[:snapshot_step + 1]
        ax.plot(
            shown[:, 0],
            shown[:, 1],
            color=color,
            lw=2.35 if name == "Adam" else 1.7,
            linestyle=styles[name],
            label=name,
            alpha=0.96,
            zorder=5 if name == "Adam" else 4,
        )
        ax.scatter(shown[-1, 0], shown[-1, 1], color=color, s=38,
                   edgecolor="white", linewidth=0.6, zorder=6)

    ax.set_title(f"Optimizer trajectories on Rosenbrock (step {snapshot_step}/{steps})",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("$w_1$")
    ax.set_ylabel("$w_2$")
    ax.set_xlim(xs.min(), xs.max())
    ax.set_ylim(ys.min(), ys.max())
    ax.grid(alpha=0.12)
    ax.legend(loc="upper left", frameon=True, facecolor="white",
              edgecolor="#DDDDDD", framealpha=0.9, fontsize=8.5)
    fig.tight_layout()
    for name in ("fig18_rosenbrock_nonconvex_reference.png", "fig18_rosenbrock_nonconvex_reference_ppt.png"):
        out = FIGURES / name
        fig.savefig(out, dpi=190, bbox_inches="tight", facecolor="white")
        print(f"Saved: {out}")
    plt.close(fig)


if __name__ == "__main__":
    main()
