# Q&A Cheatsheet — Adaptive Algorithms Presentation
## Continuous Optimization · 20.05.2026

Based on observed Q&A patterns from Prof. Lucchi's sessions.

---

## 1. Mathematical Definitions (Lucchi's favorite opener)

### Q: "What does it mean for a function to be convex?"

A function f is convex if for all x, y and λ ∈ [0,1]:
f(λx + (1−λ)y) ≤ λf(x) + (1−λ)f(y).
Geometrically: the line segment between any two points on the graph lies above the function. Equivalently, if f is twice differentiable, the Hessian ∇²f is positive semidefinite everywhere.

### Q: "Why is logistic loss convex?"

The Hessian of logistic loss is ∇²f = XᵀDX, where D is a diagonal matrix with entries Dᵢᵢ = σᵢ(1−σᵢ). Since σᵢ ∈ (0,1), all diagonal entries are positive, so D is positive definite. XᵀDX is then positive semidefinite for any X, which means the loss is convex.

### Q: "What makes your non-convex regularizer non-convex?"

The regularizer is r(w) = Σⱼ αwⱼ² / (1 + αwⱼ²). Its second derivative changes sign: for small wⱼ it behaves like αwⱼ² (convex), but as wⱼ grows, the term saturates at 1 and the curvature becomes negative. So the overall objective — convex logistic loss plus this regularizer — is non-convex. We use λ = 0.01 and α = 1 following Reddi et al. (2016).

### Q: "What does O(1/√T) convergence mean?"

It means the suboptimality — the gap f(wₜ) − f* — decreases at a rate proportional to 1/√T. After T iterations, we are at most c/√T away from optimal. Concretely: to halve the error, you need 4× more iterations. This is sublinear convergence, typical for stochastic first-order methods.

### Q: "Is O(1/√T) linear convergence?"

No. Linear convergence means the error decreases exponentially: f(wₜ) − f* ≤ ρᵀ for some ρ < 1. On a log-scale plot, linear convergence is a straight line going down. O(1/√T) is sublinear — it flattens out. SGD on strongly convex problems can achieve linear convergence with a decreasing step size, but in the stochastic non-convex setting, O(1/√T) is the standard rate.

### Q: "What is the difference between convergence rate and convergence guarantee?"

The rate tells you how fast you approach optimality — e.g. O(1/√T). The guarantee specifies under what conditions this rate holds — e.g. bounded gradients, Lipschitz smoothness, unbiased gradient estimates. RMSprop has no formal convergence guarantee, meaning no proven rate under standard assumptions.

---

## 2. Optimizer-Specific Questions

### Q: "What is the difference between Adagrad and AdaGrad-Norm?"

Adagrad maintains a per-coordinate accumulator Gⱼⱼ = Σₜ gₜ,ⱼ². Each coordinate gets its own effective learning rate η/√Gⱼⱼ. AdaGrad-Norm uses a single scalar: Gₜ = Σₜ ‖gₜ‖². All coordinates share the same scaling η/√Gₜ. Adagrad is better when features have heterogeneous scales (e.g., sparse data). AdaGrad-Norm is simpler and has the same O(1/√T) convergence rate.

### Q: "Why does Adagrad's step size shrink to zero?"

Because the accumulator Gⱼⱼ grows monotonically — it sums squared gradients without forgetting. After many iterations, √Gⱼⱼ becomes very large and the effective step size η/√Gⱼⱼ → 0. This is actually the desired behavior for convex problems — you want the step size to decrease to converge. But for non-convex problems or long training runs, it can cause premature convergence.

### Q: "Why does Adam sometimes not converge?"

Reddi et al. (2018) showed a concrete counterexample where Adam diverges. The issue is exponential forgetting in the second moment estimate v̂ₜ. Old gradient information is discarded, and if a rare but large gradient appears, the denominator can become very small, causing the step size to blow up. The fix is AMSGrad, which takes v̂ₜ = max(v̂ₜ₋₁, vₜ), ensuring the denominator never shrinks.

### Q: "Why does RMSprop work so well despite having no convergence guarantee?"

RMSprop uses exponential forgetting — it only remembers recent gradients. This makes it very adaptive to changes in the loss landscape during training. In practice, this works extremely well, especially in non-stationary settings. The lack of formal guarantees means we can't prove a worst-case rate, but empirically it's consistently among the fastest methods. That said, it can diverge at large learning rates — we show this in our learning rate sweep.

### Q: "Is Adagrad always better than SGD?"

No. Adagrad's advantage comes from per-coordinate scaling, which matters most when features have very different scales or are sparse. On problems with dense, uniformly-scaled features, the benefit is small. Also, for very long training runs, Adagrad's monotonically decreasing step size can be a disadvantage compared to SGD with a tuned schedule.

---

## 3. Setup & Methodology Questions

### Q: "What model are you using? Is it a neural network?"

No, we use linear models. For A9a: logistic regression — a linear classifier with sigmoid output. For MNIST: softmax regression — a linear multi-class classifier. No hidden layers, no activation functions between layers. We chose linear models deliberately because the focus of this project is on comparing optimizers, not model architectures. Linear models give us a clean, controlled setting where we can isolate the effect of the optimization algorithm.

### Q: "Why linear models and not neural networks?"

Three reasons: First, logistic loss on a linear model is convex, so convergence guarantees from the papers apply directly. Second, it isolates the optimizer effect — with a neural network, architecture choices would confound the comparison. Third, the original papers (Duchi et al. 2011, Ward et al. 2020) also use linear models in their experiments. For the final report, we may add a small neural network experiment.

### Q: "Why these two datasets?"

A9a has 123 sparse features and 32K samples — it's a standard binary classification benchmark where per-coordinate scaling matters due to feature heterogeneity. MNIST has 784 dense features and 60K samples — a higher-dimensional multi-class problem. Together they test adaptive methods in two different regimes: sparse vs. dense features, low vs. high dimensionality.

### Q: "How did you choose the learning rates?"

We ran a grid search over η ∈ {10⁻⁴, 3×10⁻⁴, 10⁻³, ..., 1} — 9 values on a log scale. For each optimizer we picked the η that gave the best final training loss. Our backup slide shows the full sweep. Key finding: Adagrad is very robust across the entire range, while RMSprop diverges at η = 1.

### Q: "How many epochs? What batch size?"

10–15 epochs, mini-batch size 128 for A9a and 256 for MNIST. All results are averaged over 3 random seeds to reduce noise.

### Q: "Did you implement everything from scratch?"

Yes, all five optimizers are implemented from scratch in NumPy. No PyTorch, no TensorFlow. The loss functions and gradient computations are also our own code. We handle both dense and sparse matrices (scipy.sparse for A9a).

---

## 4. Results Interpretation

### Q: "In your A9a plot — is Adagrad converging faster than the theoretical rate?"

Yes, significantly. The theoretical worst-case for Adagrad is O(log T / √T), but empirically on A9a we see much faster convergence — the loss drops below 10⁻⁷ suboptimality. This is expected because worst-case bounds hold for arbitrary convex functions. Our logistic loss has additional structure — it's smooth, and the data matrix has bounded spectral norm — which allows faster convergence in practice.

### Q: "Why are the final accuracies so similar across optimizers?"

Because all optimizers are minimizing the same convex objective and they all converge to the same global minimum — just at different speeds. The final model is essentially the same regardless of which optimizer found it. The practical difference is in training efficiency, not final quality. This is actually a key insight: adaptive methods are about speed, not better solutions.

### Q: "Why does the non-convex regularizer not change the ranking?"

At λ = 0.01, the regularizer term is small relative to the logistic loss. The objective is "mildly" non-convex — the convex part still dominates. In our λ sweep, we show that at λ = 0.1 or higher, the effect becomes significant and accuracy drops. The optimizer ranking stays similar because all methods handle this mild non-convexity similarly.

### Q: "Your gradient norm plot — what does it mean when the norm goes to zero?"

It means we've reached a stationary point where ∇f(w) ≈ 0. For convex problems, this is the global minimum. For non-convex problems, it could also be a saddle point or local minimum. The interesting observation is that adaptive methods bring the gradient norm down faster — they effectively normalize the step size, preventing overshooting when gradients are large in early iterations.

---

## 5. Theory vs. Practice

### Q: "Do your empirical results match the theoretical convergence rates?"

Our backup slide 27 shows this comparison. All methods converge faster than the worst-case bounds predict. This is typical — the bounds are for adversarial functions, while our problems have nice structure. Qualitatively, the ranking is consistent: Adagrad converges fastest (matching its O(log T / √T) being a better constant in practice), and SGD is slowest.

### Q: "What assumptions do you need for SGD's O(1/√T) rate?"

Standard assumptions: (1) L-Lipschitz continuous gradients, (2) unbiased stochastic gradients (𝔼[gₜ] = ∇f(wₜ)), (3) bounded variance of the gradient estimates. Under these, SGD with step size η = c/√T achieves E[‖∇f(w)‖²] ≤ O(1/√T) for non-convex objectives.

### Q: "Why do we care about convergence rates if all methods reach the same solution?"

In practice, compute budget is limited. If method A reaches 90% accuracy in 100 iterations and method B needs 1000, that's a 10× difference in training time. For large-scale problems (millions of parameters, billions of data points), this translates to days vs. weeks of training. Convergence rates tell us which method uses compute most efficiently.

---

## 6. Quick-Fire Definitions (be ready to answer in one sentence)

| Term | One-line answer |
|---|---|
| **Positive definite** | All eigenvalues are strictly positive; equivalently, xᵀAx > 0 for all x ≠ 0 |
| **Lipschitz continuous gradient** | ‖∇f(x) − ∇f(y)‖ ≤ L‖x − y‖ — the gradient doesn't change too fast |
| **Unbiased estimator** | 𝔼[gₜ] = ∇f(wₜ) — on average, the stochastic gradient equals the true gradient |
| **Momentum** | Accumulates a running average of past gradients to smooth updates and accelerate convergence |
| **Bias correction (Adam)** | Divides by (1 − βᵗ) to compensate for initialization at zero in the first few steps |
| **Sublinear convergence** | Error → 0 but slower than any geometric sequence. Example: O(1/√T) |
| **Linear convergence** | Error decreases by a constant factor each step: eₜ ≤ ρᵗe₀ with ρ < 1 |
| **Superlinear convergence** | Faster than linear; the ratio eₜ₊₁/eₜ → 0. Example: Newton's method |
