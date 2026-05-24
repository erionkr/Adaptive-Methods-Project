from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path("/Users/erionkrasniqi/Desktop/Project 2")
FIGURES = ROOT / "figures"
sys.path.insert(0, str(ROOT / "src"))

import datasets
from losses import (
    logistic_grad,
    logistic_loss,
    logistic_nonconvex_grad,
    logistic_nonconvex_loss,
    rosenbrock_grad,
    rosenbrock_loss,
)
from optimizers import Adam, SGD
from quasi_newton import run_lbfgs


COLORS = {
    "SGD": "#4C78A8",
    "Adam": "#8A3FFC",
    "L-BFGS": "#0F766E",
}


def binary_accuracy(w, X, y):
    return float(np.mean(np.sign(X @ w) == y))


def run_stochastic_final(make_opt, X, y, loss_fn, grad_fn, *, n_epochs=10, batch_size=128, seeds=(0, 1, 2)):
    final_losses = []
    final_accs = []
    n, d = X.shape
    for seed in seeds:
        rng = np.random.default_rng(seed)
        w = np.zeros(d)
        opt = make_opt()
        for _ in range(n_epochs):
            perm = rng.permutation(n)
            for start in range(0, n, batch_size):
                idx = perm[start:start + batch_size]
                w = opt.step(w, grad_fn(w, X[idx], y[idx]))
        final_losses.append(loss_fn(w))
        final_accs.append(binary_accuracy(w, X, y))
    return float(np.mean(final_losses)), float(np.std(final_losses)), float(np.mean(final_accs))


def run_rosenbrock_path(make_opt, w0, steps):
    opt = make_opt()
    w = w0.astype(float).copy()
    values = [rosenbrock_loss(w)]
    for _ in range(steps):
        w = opt.step(w, rosenbrock_grad(w))
        values.append(rosenbrock_loss(w))
    return np.asarray(values)


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    Xtr, ytr, Xte, yte = datasets.load_a9a()
    d = Xtr.shape[1]
    w0 = np.zeros(d)

    lam = 1e-2
    alpha = 1.0
    objectives = [
        (
            "A9a logistic",
            lambda w: logistic_loss(w, Xtr, ytr),
            lambda w: logistic_grad(w, Xtr, ytr),
            lambda w, Xb, yb: logistic_grad(w, Xb, yb),
        ),
        (
            "A9a logistic + non-convex reg.",
            lambda w: logistic_nonconvex_loss(w, Xtr, ytr, lam=lam, alpha=alpha),
            lambda w: logistic_nonconvex_grad(w, Xtr, ytr, lam=lam, alpha=alpha),
            lambda w, Xb, yb: logistic_nonconvex_grad(w, Xb, yb, lam=lam, alpha=alpha),
        ),
    ]

    a9a_rows = []
    for label, full_loss, full_grad, batch_grad in objectives:
        sgd_loss, sgd_std, sgd_acc = run_stochastic_final(
            lambda: SGD(lr=1e-1), Xtr, ytr, full_loss, batch_grad
        )
        adam_loss, adam_std, adam_acc = run_stochastic_final(
            lambda: Adam(lr=5e-3), Xtr, ytr, full_loss, batch_grad
        )
        lbfgs = run_lbfgs(full_loss, full_grad, w0, maxiter=400, name="L-BFGS")
        lbfgs_acc = binary_accuracy(lbfgs.x, Xte, yte)
        a9a_rows.append({
            "objective": label,
            "SGD": (sgd_loss, sgd_std, sgd_acc, None),
            "Adam": (adam_loss, adam_std, adam_acc, None),
            "L-BFGS": (lbfgs.fun, 0.0, lbfgs_acc, lbfgs.nit),
        })
        print(
            f"{label}: L-BFGS loss={lbfgs.fun:.4f}, test acc={lbfgs_acc:.4f}, "
            f"nit={lbfgs.nit}, success={lbfgs.success}"
        )

    w0_rosen = np.array([-1.0, 1.0])
    rb_sgd = run_rosenbrock_path(lambda: SGD(lr=2e-4), w0_rosen, steps=5000)
    rb_adam = run_rosenbrock_path(lambda: Adam(lr=0.005), w0_rosen, steps=5000)
    rb_lbfgs = run_lbfgs(rosenbrock_loss, rosenbrock_grad, w0_rosen, maxiter=80, name="L-BFGS")
    print(
        f"Rosenbrock: L-BFGS f={rb_lbfgs.fun:.3e}, nit={rb_lbfgs.nit}, "
        f"success={rb_lbfgs.success}"
    )

    fig, axes = plt.subplots(1, 2, figsize=(12.8, 4.8))

    ax = axes[0]
    x = np.arange(len(a9a_rows))
    width = 0.23
    for offset, name in zip([-width, 0.0, width], ["SGD", "Adam", "L-BFGS"]):
        vals = [row[name][0] for row in a9a_rows]
        errs = [row[name][1] for row in a9a_rows]
        bars = ax.bar(x + offset, vals, width, label=name, color=COLORS[name], alpha=0.9)
        if name != "L-BFGS":
            ax.errorbar(x + offset, vals, yerr=errs, fmt="none", ecolor="#333333", capsize=3, lw=0.8)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, val + 0.002, f"{val:.3f}",
                    ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(["convex", "non-convex reg."])
    ax.set_ylabel("final training loss")
    ax.set_title("A9a: stochastic methods vs full-batch L-BFGS")
    ax.grid(axis="y", alpha=0.22)
    ax.legend(frameon=True, fontsize=8.5)

    ax = axes[1]
    rb_sgd_idx = np.arange(len(rb_sgd))
    rb_adam_idx = np.arange(len(rb_adam))
    floor = 1e-10
    ax.plot(rb_sgd_idx, np.maximum(np.minimum.accumulate(rb_sgd), floor),
            color=COLORS["SGD"], lw=1.7, label="SGD")
    ax.plot(rb_adam_idx, np.maximum(np.minimum.accumulate(rb_adam), floor),
            color=COLORS["Adam"], lw=2.0, label="Adam")
    ax.plot(np.arange(len(rb_lbfgs.history)), np.maximum(np.minimum.accumulate(rb_lbfgs.history), floor),
            color=COLORS["L-BFGS"],
            lw=2.2, label=f"L-BFGS ({rb_lbfgs.nit} full-batch iters)")
    ax.set_yscale("log")
    ax.set_xlabel("optimizer iteration")
    ax.set_ylabel("best Rosenbrock objective so far")
    ax.set_title("Rosenbrock: quasi-Newton reference")
    ax.grid(alpha=0.22)
    ax.legend(frameon=True, fontsize=8.5)
    ax.set_xlim(0, 5000)
    ax.set_ylim(floor, 1e1)

    fig.suptitle("Quasi-Newton reference: L-BFGS is a strong full-batch baseline", fontsize=13, fontweight="bold")
    fig.text(
        0.5,
        0.01,
        "Interpretation: L-BFGS uses full-batch gradients and curvature information, so it is a reference baseline rather than a mini-batch optimizer.",
        ha="center",
        fontsize=9.5,
        color="#444444",
    )
    fig.tight_layout(rect=[0, 0.06, 1, 0.92])
    out = FIGURES / "fig19_lbfgs_quasi_newton_reference.png"
    fig.savefig(out, dpi=180, facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
