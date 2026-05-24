# Speaker Text — Final Presentation

Main presentation: slides 1-21. Backup slides 22-28 are only for questions.

## Slide 1 — Title

Good afternoon. We are Erion Krasniqi and Denis Mustafa Xhabrahimi, and our project is about adaptive algorithms in continuous optimization.

The goal of the presentation is to compare classical stochastic gradient descent with adaptive first-order methods such as Adagrad, AdaGrad-Norm, RMSprop, and Adam.

We focus on both the theoretical intuition behind these methods and their empirical behavior on classification tasks.

## Slide 2 — Content

The presentation is structured in three parts.

First, we introduce the motivation and project goal. Then we summarize the related optimization methods. Finally, we explain our methodology and discuss the experimental results.

The backup slides contain additional sensitivity experiments and convergence plots, but I will only use them if questions come up.

## Slide 3 — Introduction & Motivation

We start with the motivation.

In many machine learning problems, we minimize an objective function using gradient-based updates. The main question is how large each update step should be.

A fixed learning rate can work, but it often requires careful tuning and may behave differently across datasets, features, and objective geometries.

## Slide 4 — Why Adaptive Step Sizes?

The basic gradient descent update is shown on the slide.

The issue with a fixed step size is that one value has to work in all directions. If the step size is too large, the method may oscillate or diverge. If it is too small, convergence becomes slow.

Adaptive methods try to use information from the gradient history to scale the update. This can help especially when different coordinates behave differently, or when the loss surface has an unfavorable geometry.

## Slide 5 — Project Goal

Our project compares adaptive first-order methods against stochastic gradient descent.

The adaptive methods we study are Adagrad, AdaGrad-Norm, RMSprop, and Adam. SGD is used as the baseline.

Experimentally, we use two datasets: A9a for binary classification and MNIST for multi-class classification.

We evaluate the required objectives from the project description: logistic regression, softmax cross-entropy for MNIST, and logistic regression with the non-convex regularizer from Reddi et al.

In addition, we include Rosenbrock as a controlled non-convex reference benchmark. This is not a third dataset experiment. It is used to isolate a geometry where Adam's advantage becomes easier to see.

## Slide 6 — Related Work

Next, we briefly introduce the optimization methods.

All methods are first-order methods, meaning that they only use gradients and do not require second-order information such as Hessians.

The main difference between them is how they use past gradients to choose the next step.

## Slide 7 — SGD

Stochastic gradient descent is the baseline.

At each iteration, we sample a mini-batch, compute a stochastic gradient, and move in the negative gradient direction using a fixed learning rate.

SGD is simple, cheap per iteration, and scales well to large datasets. The limitation is that it has no per-coordinate adaptation and depends strongly on the learning rate.

Under standard assumptions, SGD has a typical stochastic convergence rate of order one over square root T.

## Slide 8 — Adagrad

Adagrad improves on SGD by accumulating squared gradients for each coordinate.

Coordinates with large historical gradients get a smaller effective step size, while coordinates with small historical gradients get a larger effective step size.

This is useful for sparse data such as A9a, where different features may appear with very different frequencies.

The main limitation is that the accumulated gradient history only increases. Therefore the effective step sizes can become very small over time.

## Slide 9 — AdaGrad-Norm and RMSprop

AdaGrad-Norm is related to Adagrad, but instead of using one accumulator per coordinate, it uses a single scalar based on the gradient norm.

This makes the method simpler and gives strong convergence guarantees, including for non-convex landscapes, but it loses per-coordinate adaptation.

RMSprop uses an exponential moving average of squared gradients. This means it forgets old gradients and adapts more quickly to recent behavior.

In practice, RMSprop often works well, but it is more heuristic and does not have the same clean theoretical guarantees.

## Slide 10 — Adam

Adam combines two ideas.

First, it uses a first moment estimate, which is similar to momentum and averages past gradients.

Second, it uses a second moment estimate, similar to RMSprop, which adapts the step size based on squared gradients.

Both estimates are bias-corrected because they are initialized at zero.

This combination of momentum and adaptive scaling is the main reason why Adam is often strong in practice.

## Slide 11 — Comparison at a Glance

This table summarizes the main differences.

SGD has no momentum and no per-coordinate adaptation. Adagrad has per-coordinate scaling, but no forgetting. AdaGrad-Norm has strong theory but only one shared scalar step size.

RMSprop has per-coordinate adaptation and forgetting, but fewer formal guarantees.

Adam combines per-coordinate scaling, momentum, and forgetting. The convergence statement is more delicate, which is why AMSGrad and the Reddi et al. paper are relevant.

## Slide 12 — Methodology & Results

Now we move to the experimental part.

The goal is not only to compare final accuracies, but also to understand how quickly the methods reduce the objective and how stable they are across settings.

## Slide 13 — Experimental Setup

Our experiments use A9a and MNIST.

For A9a, we use logistic regression for binary classification. For MNIST, we use softmax regression for the ten classes.

We also evaluate logistic regression with the non-convex regularizer from Reddi et al.

Finally, Rosenbrock is added as a reference objective. It is a controlled two-dimensional non-convex benchmark, not an additional dataset experiment.

All stochastic optimizers are implemented from scratch in NumPy. For the dataset experiments, we use mini-batches and average the results over three random seeds.

In addition, we include L-BFGS as a quasi-Newton reference on selected full-batch objectives, following the quasi-Newton framework surveyed by Xu and Zhang. We interpret it separately, because unlike the mini-batch methods, it uses full gradients and curvature information.

The metrics are training loss, test accuracy, gradient norms, and for Rosenbrock the optimizer trajectories.

## Slide 14 — A9a Logistic Loss

This slide shows the A9a results for the convex logistic loss.

On the left, we see that adaptive methods reduce the training loss faster than SGD in the early iterations. RMSprop and Adagrad are especially fast here.

On the right, all methods reach roughly the same test accuracy, around 85 percent.

The main interpretation is that adaptive methods improve optimization speed, but they do not necessarily improve the final generalization performance on this task.

## Slide 15 — MNIST Softmax Cross-Entropy

For MNIST, the pattern is similar but more pronounced.

Adagrad achieves the fastest loss decrease, while RMSprop and Adam are close behind. SGD is slower and needs more iterations to reach comparable loss values.

Again, the final test accuracies are close, but the adaptive methods reach good performance earlier.

This supports the idea that per-coordinate adaptation is useful in higher-dimensional classification problems.

## Slide 16 — Gradient Norms

The gradient norm plots help explain why adaptive methods are useful.

At the beginning, gradients can be relatively large or unstable. Adaptive methods normalize the update using gradient history, which helps control the step size.

On MNIST in particular, the adaptive methods reduce the gradient norm faster than SGD.

So these plots show the optimization mechanism behind the faster loss decrease.

## Slide 17 — Non-convex Reference: Rosenbrock

To better illustrate behavior on a truly non-convex objective, we add the two-dimensional Rosenbrock function as a reference benchmark.

Rosenbrock has a narrow curved valley with the minimum at the point (1, 1). This geometry is difficult because the optimizer has to follow the valley instead of moving in a straight direction.

In the animation, all methods start from the same point and we run them for 50,000 iterations.

Adam reaches the region around the minimum fastest, after roughly 1,200 iterations. Adagrad and RMSprop also follow the valley and improve clearly, but they need more iterations and are less direct than Adam.

AdaGrad-Norm improves as well, but because it uses only one shared scalar step size, it adapts less precisely to the curved geometry.

SGD is the slowest method here. It eventually moves toward the minimum, but it needs tens of thousands of iterations to get close.

This benchmark complements our classification experiments by isolating a non-convex geometry where Adam's combination of momentum and adaptive scaling becomes clearly useful.

## Slide 18 — Key Takeaways

The first takeaway is speed. Adaptive methods reduce the loss much faster in early iterations.

The second takeaway is accuracy. Final classification accuracy differences are small, so the main benefit is optimization efficiency rather than final model quality.

The third takeaway is non-convex geometry. The Rosenbrock reference shows a setting where Adam's momentum and adaptive scaling are clearly helpful.

Finally, the non-convex regularizer on A9a has only limited impact at moderate lambda values.

## Slide 19 — Final Discussion

We also ran additional analyses, which are included in the backup slides.

The learning-rate sensitivity experiment shows that Adagrad and AdaGrad-Norm are relatively robust, while RMSprop becomes sensitive at large learning rates.

The wall-clock comparison shows that adaptive methods have more overhead per step, but often reach low loss faster.

The lambda sweep shows that the non-convex regularizer only becomes dominant for larger lambda values.

We also include L-BFGS as a quasi-Newton reference, based on the BFGS-type quasi-Newton framework surveyed by Xu and Zhang. It is a strong full-batch baseline, but not directly comparable to mini-batch adaptive methods because its iterations use more global information.

Overall, the Rosenbrock benchmark complements the dataset results by showing a controlled non-convex geometry where Adam's advantages are more visible.

## Slide 20 — References

These are the main references we used.

Kingma and Ba introduce Adam. Duchi, Hazan, and Singer introduce Adagrad. Ward, Wu, and Bottou analyze AdaGrad-Norm.

We also use RMSprop from the Tieleman and Hinton lecture, Reddi et al. for the Adam convergence discussion and the non-convex regularizer, Rosenbrock for the reference objective, and Xu and Zhang for the quasi-Newton reference baseline.

## Slide 21 — Thank You

Thank you for listening.

We are happy to answer questions.
