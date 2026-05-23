"""
Generate supplementary visuals for the CO presentation:
  1. Pipeline graphic (Project Goal slide)
  2. Optimizer family tree (Related Work slide)
  3. MNIST sample digits strip (Experimental Setup slide)
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import os

FIGURES = os.path.join(os.path.dirname(__file__), '..', 'figures')
TEAL = '#A0C4B8'
TEAL_DARK = '#6B9E8A'
LIGHT_BG = '#F0F8F5'
BLACK = '#000000'

# ─────────────────────────────────────────────────────────────────
# 1. Pipeline graphic
# ─────────────────────────────────────────────────────────────────

def make_pipeline():
    fig, ax = plt.subplots(figsize=(11, 3.5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 3.5)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    boxes = [
        (0.5,  "Datasets",    ["A9a (binary, 32K×123)", "MNIST (10-class, 60K×780)"]),
        (3.0,  "Optimizers",  ["SGD", "Adagrad · AdaGrad-Norm", "RMSprop · Adam"]),
        (5.5,  "Losses",      ["Logistic (convex)", "Logistic + non-convex reg."]),
        (8.0,  "Metrics",     ["Training loss", "Test accuracy", "Gradient norms"]),
    ]

    box_w = 2.2
    box_h = 2.4
    y_center = 1.75

    for x, title, items in boxes:
        # Box
        rect = FancyBboxPatch((x, y_center - box_h/2), box_w, box_h,
                               boxstyle="round,pad=0.1",
                               facecolor=LIGHT_BG, edgecolor=TEAL_DARK, linewidth=2)
        ax.add_patch(rect)
        # Title bar
        title_rect = FancyBboxPatch((x, y_center + box_h/2 - 0.55), box_w, 0.55,
                                     boxstyle="round,pad=0.05",
                                     facecolor=TEAL, edgecolor=TEAL_DARK, linewidth=1.5)
        ax.add_patch(title_rect)
        ax.text(x + box_w/2, y_center + box_h/2 - 0.27, title,
                ha='center', va='center', fontsize=13, fontweight='bold',
                fontfamily='serif', color=BLACK)
        # Items
        for i, item in enumerate(items):
            ax.text(x + box_w/2, y_center + box_h/2 - 0.85 - i*0.45, item,
                    ha='center', va='center', fontsize=9.5,
                    fontfamily='serif', color='#333333')

    # Arrows between boxes
    arrow_style = "Simple,tail_width=6,head_width=16,head_length=10"
    for i in range(len(boxes) - 1):
        x1 = boxes[i][0] + box_w
        x2 = boxes[i+1][0]
        arr = FancyArrowPatch((x1 + 0.05, y_center), (x2 - 0.05, y_center),
                               arrowstyle=arrow_style,
                               color=TEAL_DARK, mutation_scale=1)
        ax.add_patch(arr)

    # Final question at bottom
    ax.text(5.5, 0.15, "→  Which method converges fastest and most robustly?",
            ha='center', va='center', fontsize=12, fontweight='bold',
            fontfamily='serif', color=TEAL_DARK, style='italic')

    plt.tight_layout()
    path = os.path.join(FIGURES, 'visual_pipeline.png')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  ✓ {path}")


# ─────────────────────────────────────────────────────────────────
# 2. Optimizer family tree
# ─────────────────────────────────────────────────────────────────

def make_optimizer_tree():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    def draw_box(x, y, text, w=2.0, h=0.6, color=LIGHT_BG, edge=TEAL_DARK, fontsize=11, bold=False):
        rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                               boxstyle="round,pad=0.08",
                               facecolor=color, edgecolor=edge, linewidth=1.8)
        ax.add_patch(rect)
        ax.text(x, y, text, ha='center', va='center', fontsize=fontsize,
                fontweight='bold' if bold else 'normal', fontfamily='serif', color=BLACK)
        return (x, y)

    def draw_line(x1, y1, x2, y2, style='-'):
        ax.plot([x1, x2], [y1, y2], color=TEAL_DARK, linewidth=1.5, linestyle=style)

    # Root
    draw_box(5, 4.5, "Gradient Methods", w=2.8, h=0.6, color=TEAL, bold=True, fontsize=13)

    # Level 1 - categories
    cats = [
        (1.8, 3.3, "Fixed step size"),
        (5.0, 3.3, "Accumulate\ngradients"),
        (8.2, 3.3, "Momentum +\nadaptivity"),
    ]
    for x, y, t in cats:
        draw_box(x, y, t, w=2.2, h=0.7, color='#D6EBE1', fontsize=10, bold=True)
        draw_line(5, 4.5 - 0.3, x, y + 0.35)

    # Level 2 - add EMA category between accumulate and momentum
    # SGD under fixed step
    draw_box(1.8, 2.0, "SGD", w=1.6, h=0.55, fontsize=11, bold=True)
    draw_line(1.8, 3.3 - 0.35, 1.8, 2.0 + 0.28)

    # Adagrad, AdaGrad-Norm under accumulate
    draw_box(4.0, 2.0, "Adagrad", w=1.6, h=0.55, fontsize=11, bold=True)
    draw_box(6.0, 2.0, "AdaGrad-Norm", w=2.0, h=0.55, fontsize=10, bold=True)
    draw_line(5.0, 3.3 - 0.35, 4.0, 2.0 + 0.28)
    draw_line(5.0, 3.3 - 0.35, 6.0, 2.0 + 0.28)

    # RMSprop - child of Adagrad concept (exponential averaging)
    draw_box(4.0, 0.9, "RMSprop", w=1.8, h=0.55, color='#E8F0EC', fontsize=11, bold=True)
    draw_line(4.0, 2.0 - 0.28, 4.0, 0.9 + 0.28)
    ax.text(3.0, 1.45, "replace sum\nwith EMA", ha='center', va='center',
            fontsize=8, fontfamily='serif', color=TEAL_DARK, style='italic')

    # Adam under momentum + adaptivity
    draw_box(8.2, 2.0, "Adam", w=1.6, h=0.55, fontsize=11, bold=True)
    draw_line(8.2, 3.3 - 0.35, 8.2, 2.0 + 0.28)

    # Dashed line from RMSprop to Adam (RMSprop is a component of Adam)
    draw_line(4.0 + 0.9, 0.9, 8.2 - 0.8, 2.0 - 0.15, style='--')
    ax.text(6.5, 1.25, "+ momentum", ha='center', va='center',
            fontsize=9, fontfamily='serif', color=TEAL_DARK, style='italic')

    # Annotations for key properties
    props = [
        (1.8, 1.45, "O(1/√T)", "#666666"),
        (4.0, 1.45, "per-coord", "#666666"),
        (6.0, 1.45, "scalar", "#666666"),
        (4.0, 0.35, "forgetting", "#666666"),
        (8.2, 1.45, "all combined", "#666666"),
    ]
    for x, y, text, color in props:
        ax.text(x, y, text, ha='center', va='center', fontsize=8,
                fontfamily='serif', color=color, style='italic')

    plt.tight_layout()
    path = os.path.join(FIGURES, 'visual_optimizer_tree.png')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  ✓ {path}")


# ─────────────────────────────────────────────────────────────────
# 3. MNIST sample digits strip
# ─────────────────────────────────────────────────────────────────

def make_mnist_samples():
    """Load actual digit images and show 10 sample digits (0-9)."""
    from sklearn.datasets import load_digits
    digits = load_digits()
    fig, axes = plt.subplots(1, 10, figsize=(12, 1.8))
    fig.patch.set_facecolor('white')
    for digit in range(10):
        idx = np.where(digits.target == digit)[0][0]
        axes[digit].imshow(digits.images[idx], cmap='gray_r', interpolation='nearest')
        axes[digit].set_title(str(digit), fontsize=14, fontfamily='serif', fontweight='bold')
        axes[digit].axis('off')
    plt.tight_layout(pad=0.3)
    path = os.path.join(FIGURES, 'visual_mnist_samples.png')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  ✓ {path}")


# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Generating presentation visuals...")
    make_pipeline()
    make_optimizer_tree()
    make_mnist_samples()
    print("Done!")
