"""Full-batch quasi-Newton reference baselines.

These helpers intentionally live outside ``optimizers.py`` because L-BFGS is
not a stochastic first-order method with a ``step(w, grad)`` interface.  It uses
full objective and gradient evaluations through ``scipy.optimize.minimize`` and
is therefore best interpreted as a deterministic reference baseline.
"""
from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Callable

import numpy as np
from scipy.optimize import minimize


Objective = Callable[[np.ndarray], float]
Gradient = Callable[[np.ndarray], np.ndarray]


@dataclass
class LBFGSResult:
    name: str
    x: np.ndarray
    fun: float
    nit: int
    nfev: int
    njev: int
    success: bool
    message: str
    history: np.ndarray
    times: np.ndarray


def run_lbfgs(
    objective: Objective,
    gradient: Gradient,
    x0: np.ndarray,
    *,
    maxiter: int = 200,
    name: str = "L-BFGS",
) -> LBFGSResult:
    """Run SciPy L-BFGS-B and record objective values per callback.

    The callback is called once per accepted L-BFGS iteration, so the resulting
    history is not directly comparable to mini-batch iteration counts.  We use it
    as a full-batch reference for final objective value and convergence shape.
    """
    x0 = np.asarray(x0, dtype=float)
    history = [float(objective(x0))]
    times = [0.0]
    start = time.perf_counter()

    def callback(xk):
        history.append(float(objective(np.asarray(xk, dtype=float))))
        times.append(time.perf_counter() - start)

    result = minimize(
        objective,
        x0,
        jac=gradient,
        method="L-BFGS-B",
        callback=callback,
        options={"maxiter": maxiter, "ftol": 1e-12, "gtol": 1e-8},
    )

    if len(history) == 1 or history[-1] != float(result.fun):
        history.append(float(result.fun))
        times.append(time.perf_counter() - start)

    return LBFGSResult(
        name=name,
        x=np.asarray(result.x, dtype=float),
        fun=float(result.fun),
        nit=int(result.nit),
        nfev=int(result.nfev),
        njev=int(result.njev),
        success=bool(result.success),
        message=str(result.message),
        history=np.asarray(history, dtype=float),
        times=np.asarray(times, dtype=float),
    )
