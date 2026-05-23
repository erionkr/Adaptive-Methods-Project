from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np

ROOT = Path('/Users/erionkrasniqi/Desktop/Project 2')
FIGURES = ROOT / 'figures'
sys.path.insert(0, str(ROOT / 'src'))

from optimizers import SGD, Adagrad, AdagradNorm, RMSprop, Adam
from losses import rosenbrock_loss, rosenbrock_grad


def run_optimizer(make_opt, w0, steps=2000):
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
    steps = 50000
    configs = [
        ('SGD', lambda: SGD(lr=2e-4), '#4C78A8', '-'),
        ('Adagrad', lambda: Adagrad(lr=0.08), '#F58518', '--'),
        ('AdaGrad-Norm', lambda: AdagradNorm(lr=0.08, b0=0.1), '#54A24B', '-.'),
        ('RMSprop', lambda: RMSprop(lr=0.001, rho=0.99), '#E45756', (0, (4, 2))),
        ('Adam', lambda: Adam(lr=0.005, beta1=0.9, beta2=0.999), '#8A3FFC', '-'),
    ]
    results = []
    for name, make_opt, color, style in configs:
        values, path = run_optimizer(make_opt, w0, steps)
        results.append((name, values, path, color, style))

    xs = np.linspace(-1.5, 1.5, 420)
    ys = np.linspace(-0.5, 2.0, 420)
    X, Y = np.meshgrid(xs, ys)
    Z = (1 - X) ** 2 + 100 * (Y - X * X) ** 2
    Z_plot = np.log10(Z + 1e-2)

    fig, ax = plt.subplots(figsize=(8.7, 4.7))
    levels = np.linspace(Z_plot.min(), Z_plot.max(), 42)
    ax.contour(X, Y, Z_plot, levels=levels, cmap='viridis', linewidths=0.75, alpha=0.95)
    valley_x = np.linspace(-1.5, 1.5, 260)
    ax.plot(valley_x, valley_x ** 2, color='white', lw=2.6, alpha=0.92)
    ax.scatter([w0[0]], [w0[1]], marker='o', s=54, color='black',
               edgecolor='white', linewidth=0.8, zorder=8)
    ax.scatter([1.0], [1.0], marker='*', s=150, color='#C23B4A',
               edgecolor='white', linewidth=0.8, label='Minimum (1, 1)', zorder=7)

    lines = {}
    dots = {}
    for name, values, path, color, style in results:
        (line,) = ax.plot([], [], color=color, lw=2.35 if name == 'Adam' else 1.7,
                          linestyle=style, label=name, alpha=0.96,
                          zorder=5 if name == 'Adam' else 4)
        dot = ax.scatter([], [], color=color, s=38, edgecolor='white', linewidth=0.6, zorder=6)
        lines[name] = line
        dots[name] = dot

    title = ax.set_title('', fontsize=12.5, fontweight='bold', pad=14)
    ax.set_xlabel('$w_1$')
    ax.set_ylabel('$w_2$')
    ax.set_xlim(xs.min(), xs.max())
    ax.set_ylim(ys.min(), ys.max())
    ax.grid(alpha=0.12)
    ax.legend(loc='lower left', frameon=True, facecolor='white',
              edgecolor='#DDDDDD', framealpha=0.9, fontsize=8.5)
    fig.subplots_adjust(left=0.10, right=0.985, bottom=0.13, top=0.86)

    early = np.linspace(0, 3000, 65)
    late = np.linspace(3200, steps, 75)
    frame_steps = np.unique(np.round(np.r_[early, late]).astype(int))

    def update(frame_idx):
        t = int(frame_steps[frame_idx])
        title.set_text(f'Optimizer trajectories on Rosenbrock (step {t}/{steps})')
        for name, values, path, color, style in results:
            # Hide the first few tiny overlapping transients in the drawn trail.
            # The shared start is shown once as a marker, which reads cleaner.
            start_idx = 30 if t > 60 else 0
            shown = path[start_idx:t + 1]
            stride = max(1, len(shown) // 1600)
            lines[name].set_data(shown[::stride, 0], shown[::stride, 1])
            current = path[t]
            dots[name].set_offsets([current])
        return [title, *lines.values(), *dots.values()]

    anim = FuncAnimation(fig, update, frames=len(frame_steps), interval=80, blit=False)
    gif_path = FIGURES / 'fig18_rosenbrock_trajectories_animation.gif'
    anim.save(gif_path, writer=PillowWriter(fps=12))
    update(len(frame_steps) - 1)
    png_path = FIGURES / 'fig18_rosenbrock_trajectories_animation_final.png'
    fig.savefig(png_path, dpi=190, facecolor='white')
    plt.close(fig)
    print(f'Saved: {gif_path}')
    print(f'Saved: {png_path}')


if __name__ == '__main__':
    main()
