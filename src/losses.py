"""Loss functions and their (stochastic) gradients.

All functions take:
- w: (d,) or (d, K) parameter vector / matrix
- X: (n, d) design matrix (dense or sparse)
- y: (n,) labels (+/-1 for binary, or 0..K-1 for multi-class)

Returns scalar loss and grad with shape matching w.
"""
from __future__ import annotations
import numpy as np
import scipy.sparse as sp


# ---------- Binary logistic regression (labels in {-1,+1}) ----------

def logistic_loss(w: np.ndarray, X, y: np.ndarray) -> float:
    z = X @ w                       # (n,)
    # log(1 + exp(-y*z)) stably:
    yz = y * z
    return float(np.mean(np.logaddexp(0.0, -yz)))


def logistic_grad(w: np.ndarray, X, y: np.ndarray) -> np.ndarray:
    n = X.shape[0]
    z = X @ w
    s = -y / (1.0 + np.exp(y * z))            # sigmoid-like weights
    if sp.issparse(X):
        g = (X.T @ s) / n
    else:
        g = X.T @ s / n
    return np.asarray(g).ravel()


def logistic_stoch_grad(w, X, y, idx) -> np.ndarray:
    """Mini-batch gradient at indices `idx`."""
    Xb = X[idx]
    yb = y[idx]
    return logistic_grad(w, Xb, yb)


# ---------- Non-convex regularizer (Reddi et al. 2016, p.9) ----------
# r(w) = lambda * sum_j (alpha * w_j^2) / (1 + alpha * w_j^2)

def noncvx_reg(w, lam=1e-4, alpha=1.0):
    return float(lam * np.sum((alpha * w * w) / (1.0 + alpha * w * w)))


def noncvx_reg_grad(w, lam=1e-4, alpha=1.0):
    denom = (1.0 + alpha * w * w)
    return lam * (2.0 * alpha * w) / (denom * denom)


def logistic_nonconvex_loss(w, X, y, lam=1e-4, alpha=1.0):
    return logistic_loss(w, X, y) + noncvx_reg(w, lam, alpha)


def logistic_nonconvex_grad(w, X, y, lam=1e-4, alpha=1.0):
    return logistic_grad(w, X, y) + noncvx_reg_grad(w, lam, alpha)


# ---------- Multi-class softmax cross-entropy (MNIST) ----------

def softmax_loss(W, X, y, K):
    """W: (d, K); y: (n,) with labels in {0, ..., K-1}."""
    scores = X @ W                   # (n, K)
    scores -= scores.max(axis=1, keepdims=True)
    logZ = np.log(np.exp(scores).sum(axis=1))
    correct = scores[np.arange(len(y)), y]
    return float(np.mean(logZ - correct))


def softmax_grad(W, X, y, K):
    n = X.shape[0]
    scores = X @ W
    scores -= scores.max(axis=1, keepdims=True)
    P = np.exp(scores)
    P /= P.sum(axis=1, keepdims=True)       # (n, K)
    P[np.arange(n), y] -= 1.0
    if sp.issparse(X):
        G = (X.T @ P) / n
    else:
        G = X.T @ P / n
    return np.asarray(G)


# ---------- Synthetic non-convex benchmark: Rastrigin ----------
# Standard 2D objective with many local minima. Useful as a reference
# landscape where adaptive methods and momentum can show clearer benefits
# than on the convex logistic objectives above.

def rastrigin_loss(w: np.ndarray, A: float = 10.0) -> float:
    w = np.asarray(w, dtype=float)
    return float(A * w.size + np.sum(w * w - A * np.cos(2.0 * np.pi * w)))


def rastrigin_grad(w: np.ndarray, A: float = 10.0) -> np.ndarray:
    w = np.asarray(w, dtype=float)
    return 2.0 * w + 2.0 * np.pi * A * np.sin(2.0 * np.pi * w)


# ---------- Synthetic non-convex benchmark: Rosenbrock ----------
# Standard non-convex objective with a narrow curved valley. It is useful as
# a reference landscape where momentum and adaptive scaling can be evaluated
# independently of the classification experiments.

def rosenbrock_loss(w: np.ndarray, a: float = 1.0, b: float = 100.0) -> float:
    w = np.asarray(w, dtype=float)
    x, y = w[0], w[1]
    return float((a - x) ** 2 + b * (y - x * x) ** 2)


def rosenbrock_grad(w: np.ndarray, a: float = 1.0, b: float = 100.0) -> np.ndarray:
    w = np.asarray(w, dtype=float)
    x, y = w[0], w[1]
    return np.array([
        -2.0 * (a - x) - 4.0 * b * x * (y - x * x),
        2.0 * b * (y - x * x),
    ])
