# Adaptive Algorithms — CO Project 2026

**Team:** Erion Krasniqi, Denis Mustafa Xhabrahimi (Team in slot 20.05.2026)

## Goal
Survey & empirical comparison of adaptive first-order methods (Adam, Adagrad, AdaGrad-Norm, RMSprop) vs. SGD on two classification datasets.

## Structure
```
Project/
├── README.md
├── data/                 # downloaded datasets (gitignored)
├── src/
│   ├── optimizers.py     # all optimizer implementations
│   ├── losses.py         # logistic loss + non-convex reg
│   └── datasets.py       # loaders for libsvm format
├── experiments.ipynb     # main notebook (reproducible)
├── figures/              # generated plots and Rosenbrock animation
├── report/               # NeurIPS LaTeX template
├── slides/               # presentation scripts and speaker text
└── Continous_Optimization_Project_Final_Presentation.pptx
```

## Datasets
- **A9a** (binary, ~32K): https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/a9a
- **MNIST** (multi-class): https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/multiclass/mnist.bz2

## Losses
1. Logistic regression:  L(w) = (1/n) Σ log(1 + exp(-y_i ⟨w, x_i⟩))
2. Logistic regression + non-convex regularizer r(w) = λ Σ (α w_j²)/(1 + α w_j²)
   (see https://arxiv.org/pdf/1603.06159.pdf page 9)
3. Synthetic non-convex reference benchmark: 2D Rosenbrock objective
   f(x,y) = (1 - x)² + 100(y - x²)², a curved valley benchmark with global minimum at (1,1).

The Rosenbrock benchmark is a controlled reference objective used to illustrate optimizer behavior on curved non-convex geometry. It is not an additional dataset experiment.

## Milestones
| Date | Milestone |
|---|---|
| 30.04 | Literature done, datasets downloaded |
| 07.05 | All optimizers implemented + tested |
| 14.05 | Experiments done, plots generated, slides draft |
| 19.05 | Slides finalized + rehearsed |
| **20.05** | **In-class presentation** |
| 21.07 | Report + recorded video submitted |

## Task split
- **Erion**: SGD, Adam, AdaGrad-Norm, dataset loaders, plots
- **Denis**: Adagrad, RMSprop, losses (incl. non-convex reg), report intro + related work

## Running
```powershell
# activate venv (already set up)
& "..\..\..\.venv\Scripts\Activate.ps1"
pip install numpy scipy scikit-learn matplotlib jupyter
jupyter notebook experiments.ipynb
```

## Presentation
- Final deck: `Continous_Optimization_Project_Final_Presentation.pptx`
- Speaker text: `slides/speaker_text_final.md`
- Rosenbrock animation generator: `slides/generate_rosenbrock_animation.py`
