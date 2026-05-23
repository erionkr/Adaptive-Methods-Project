"""Adaptive optimizer implementations (from scratch, numpy).

All optimizers follow the same interface:
    step(w, grad) -> new_w
with internal state stored on the object.

Conventions:
- w: numpy array of parameters
- grad: numpy array, same shape as w
"""
from __future__ import annotations
import numpy as np


class Optimizer:
    name = "base"

    def __init__(self, lr: float):
        self.lr = lr

    def step(self, w: np.ndarray, grad: np.ndarray) -> np.ndarray:
        raise NotImplementedError


class SGD(Optimizer):
    name = "SGD"

    def step(self, w, grad):
        return w - self.lr * grad


class Adagrad(Optimizer):
    """Duchi et al. 2011. Per-coordinate adaptive step size.
    Update: G_t += g_t^2;  w_{t+1} = w_t - lr * g_t / (sqrt(G_t) + eps)
    """
    name = "Adagrad"

    def __init__(self, lr=1e-2, eps=1e-8):
        super().__init__(lr)
        self.eps = eps
        self.G = None  # accumulator of squared gradients

    def step(self, w, grad):
        if self.G is None:
            self.G = np.zeros_like(w)
        self.G += grad * grad
        return w - self.lr * grad / (np.sqrt(self.G) + self.eps)


class AdagradNorm(Optimizer):
    """Ward, Wu, Bottou 2020. Scalar adaptive step size using ||g||^2.
    Update: b_t^2 += ||g_t||^2;  w_{t+1} = w_t - lr * g_t / (b_t + eps)
    """
    name = "AdaGrad-Norm"

    def __init__(self, lr=1.0, eps=1e-8, b0=1e-3):
        super().__init__(lr)
        self.eps = eps
        self.b2 = b0 * b0  # scalar accumulator

    def step(self, w, grad):
        self.b2 += float(grad @ grad)
        return w - self.lr * grad / (np.sqrt(self.b2) + self.eps)


class RMSprop(Optimizer):
    """Tieleman & Hinton 2012. Exponential moving average of g^2.
    v_t = rho * v_{t-1} + (1-rho) * g_t^2
    w_{t+1} = w_t - lr * g_t / (sqrt(v_t) + eps)
    """
    name = "RMSprop"

    def __init__(self, lr=1e-3, rho=0.9, eps=1e-8):
        super().__init__(lr)
        self.rho = rho
        self.eps = eps
        self.v = None

    def step(self, w, grad):
        if self.v is None:
            self.v = np.zeros_like(w)
        self.v = self.rho * self.v + (1 - self.rho) * grad * grad
        return w - self.lr * grad / (np.sqrt(self.v) + self.eps)


class Adam(Optimizer):
    """Kingma & Ba 2014. Momentum + per-coord adaptive step.
    m_t = b1 * m_{t-1} + (1-b1) * g_t
    v_t = b2 * v_{t-1} + (1-b2) * g_t^2
    m_hat = m_t / (1 - b1^t);  v_hat = v_t / (1 - b2^t)
    w_{t+1} = w_t - lr * m_hat / (sqrt(v_hat) + eps)
    """
    name = "Adam"

    def __init__(self, lr=1e-3, beta1=0.9, beta2=0.999, eps=1e-8):
        super().__init__(lr)
        self.b1, self.b2, self.eps = beta1, beta2, eps
        self.m = None
        self.v = None
        self.t = 0

    def step(self, w, grad):
        if self.m is None:
            self.m = np.zeros_like(w)
            self.v = np.zeros_like(w)
        self.t += 1
        self.m = self.b1 * self.m + (1 - self.b1) * grad
        self.v = self.b2 * self.v + (1 - self.b2) * grad * grad
        m_hat = self.m / (1 - self.b1 ** self.t)
        v_hat = self.v / (1 - self.b2 ** self.t)
        return w - self.lr * m_hat / (np.sqrt(v_hat) + self.eps)
