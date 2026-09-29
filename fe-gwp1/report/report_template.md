# Financial Econometrics — Group Work Project 1

**Report**

::: cover
*Replace this page with the first page of the official Report Template and fill in the required fields.*

| Group Number | |
|:--|:--|

| Full Legal Name | Location (Country) | E-Mail Address | Non-Contributing Member (X) |
|:--|:--|:--|:--:|
| | | | |
| | | | |
| | | | |
:::

**Note on this report.** All code is in the accompanying Jupyter notebook (`GWP1_notebook.ipynb`). This report shows only the answers, derivations, tables and figures, so a reader never needs to open the notebook. Every random step in the notebook uses a fixed seed; running it again reproduces every number shown here.

{{PAGEBREAK}}

# Problem 1 — Omitted variable bias

The true model is
$$y_i=\alpha+\beta x_i+\gamma w_i+\delta z_i+\varepsilon_i \qquad (1)$$
but the analyst estimates
$$y_i=\alpha+\beta x_i+\gamma w_i+\mu_i . \qquad (2)$$

Notation used throughout: a tilde denotes a deviation from the sample mean ($\tilde x_i = x_i-\bar x$), and $S_{ab}=\sum_{i=1}^n \tilde a_i\tilde b_i$ is a centred cross-product, so $S_{xx}=\sum_i (x_i-\bar x)^2$ and $S_{xy}=\sum_i (x_i-\bar x)(y_i-\bar y)$.

## Question 1a

*If the errors $\varepsilon_i$ satisfy the standard assumptions, do the errors $\mu_i$ satisfy them too?*

**No, not in general.** Setting (1) against (2), the error of the short model is whatever the analyst left out:
$$\mu_i=\delta z_i+\varepsilon_i .$$

The standard assumptions for $\varepsilon$ are: (A1) $E[\varepsilon_i\mid x,w,z]=0$; (A2) $\operatorname{Var}(\varepsilon_i\mid x,w,z)=\sigma^2$; (A3) $\operatorname{Cov}(\varepsilon_i,\varepsilon_j\mid x,w,z)=0$ for $i\neq j$; and, for exact inference, (A4) $\varepsilon_i$ normal. We check each one for $\mu$, conditioning on the regressors the analyst actually uses, $x$ and $w$.

**Zero conditional mean (exogeneity).** By the law of iterated expectations $E[\varepsilon_i\mid x,w]=E\big[E[\varepsilon_i\mid x,w,z]\mid x,w\big]=0$, so
$$E[\mu_i\mid x,w]=\delta\,E[z_i\mid x,w].$$
This is zero only if $\delta=0$ or $E[z_i\mid x,w]=0$. If $E[z_i\mid x,w]$ equals a constant $c$, the intercept simply absorbs $\delta c$ and nothing else goes wrong. But if $E[z_i\mid x,w]$ moves with $x$ or $w$, the error is correlated with the regressors:
$$\operatorname{Cov}(x_i,\mu_i)=\delta\operatorname{Cov}(x_i,z_i),\qquad \operatorname{Cov}(w_i,\mu_i)=\delta\operatorname{Cov}(w_i,z_i),$$
which breaks A1. This is the serious failure: OLS on (2) becomes biased and inconsistent (see 1c).

**Constant variance.** Since $E[\varepsilon_i\mid x,w,z]=0$ implies $\operatorname{Cov}(z_i,\varepsilon_i\mid x,w)=0$,
$$\operatorname{Var}(\mu_i\mid x,w)=\delta^2\operatorname{Var}(z_i\mid x,w)+\sigma^2 .$$
This is larger than $\sigma^2$, and it is constant only if $\operatorname{Var}(z_i\mid x,w)$ does not depend on $x$ or $w$. If, say, $z$ is more dispersed for large values of $x$, then $\mu$ is heteroskedastic even though $\varepsilon$ is not.

**No autocorrelation.** For $i\neq j$,
$$\operatorname{Cov}(\mu_i,\mu_j\mid x,w)=\delta^2\operatorname{Cov}(z_i,z_j\mid x,w).$$
If $z$ is persistent, which is typical for time-series variables such as an interest rate or a business-cycle indicator, then $\mu$ is autocorrelated even though $\varepsilon$ is not.

**Normality.** $\mu_i$ is normal only if $z_i$ is (conditionally) normal as well.

**Conclusion.** The good behaviour of $\varepsilon$ does not carry over to $\mu$. The properties of $\mu$ depend on the omitted term $\delta z$. They carry over fully only when $\delta=0$, or when $z$ behaves like an extra i.i.d. shock that is independent of $x$ and $w$ (in that case $\mu$ is well behaved but noisier, with variance $\delta^2\sigma_z^2+\sigma^2$, and the intercept absorbs $\delta E[z]$).

## Question 1b

*Assume we estimate (2) and that $x$ and $w$ are orthogonal. What are $\hat\beta$ and $\hat\gamma$?*

OLS minimises $\sum_i (y_i-a-bx_i-cw_i)^2$. The first-order condition for the intercept gives $\hat\alpha=\bar y-\hat\beta\bar x-\hat\gamma\bar w$. Substituting this back, the two remaining normal equations in deviation form are
$$S_{xy}=\hat\beta S_{xx}+\hat\gamma S_{xw},\qquad S_{wy}=\hat\beta S_{xw}+\hat\gamma S_{ww},$$
with general solution
$$\hat\beta=\frac{S_{xy}S_{ww}-S_{wy}S_{xw}}{S_{xx}S_{ww}-S_{xw}^2},\qquad
\hat\gamma=\frac{S_{wy}S_{xx}-S_{xy}S_{xw}}{S_{xx}S_{ww}-S_{xw}^2}.$$

"Orthogonal" here means the centred regressors are orthogonal, $S_{xw}=\sum_i(x_i-\bar x)(w_i-\bar w)=0$ (zero sample covariance). The cross terms then vanish, and

$$\boxed{\;\hat\beta=\frac{S_{xy}}{S_{xx}}=\frac{\sum_i(x_i-\bar x)(y_i-\bar y)}{\sum_i(x_i-\bar x)^2},\qquad
\hat\gamma=\frac{S_{wy}}{S_{ww}}=\frac{\sum_i(w_i-\bar w)(y_i-\bar y)}{\sum_i(w_i-\bar w)^2}\;}$$
$$\boxed{\;\hat\alpha=\bar y-\hat\beta\bar x-\hat\gamma\bar w\;}$$

In matrix form, with centred regressors $X=[\mathbf 1,\tilde x,\tilde w]$, the matrix $X'X=\operatorname{diag}(n,S_{xx},S_{ww})$ is diagonal, so $(X'X)^{-1}X'y$ splits into separate pieces. Each slope is exactly the slope of a simple regression of $y$ on that single regressor. The notebook confirms this numerically: with exactly orthogonal $x$ and $w$, the two-regressor OLS slopes and the simple-regression formulas agree to machine precision.

## Question 1c

*Find the bias of $\hat\gamma$ from (2), using the true model (1).*

Take deviations from means in (1): $\tilde y_i=\beta\tilde x_i+\gamma\tilde w_i+\delta\tilde z_i+\tilde\varepsilon_i$. Multiply by $\tilde w_i$ and sum:
$$S_{wy}=\beta S_{xw}+\gamma S_{ww}+\delta S_{wz}+\textstyle\sum_i\tilde w_i\varepsilon_i .$$
With $S_{xw}=0$ and the result of 1b,
$$\hat\gamma=\frac{S_{wy}}{S_{ww}}=\gamma+\delta\,\frac{S_{wz}}{S_{ww}}+\frac{\sum_i\tilde w_i\varepsilon_i}{S_{ww}}.$$
Conditional on the regressors, the last term has expectation zero, so
$$E[\hat\gamma\mid x,w,z]=\gamma+\delta\,\frac{S_{wz}}{S_{ww}},\qquad
\boxed{\;\operatorname{Bias}(\hat\gamma)=\delta\,\frac{\sum_i(w_i-\bar w)(z_i-\bar z)}{\sum_i(w_i-\bar w)^2}=\delta\,\hat d_w\;}$$

Here $\hat d_w$ is the slope from the auxiliary regression of the omitted variable $z$ on $w$. Because $x\perp w$, it is also the coefficient on $w$ in a regression of $z$ on both $x$ and $w$. In population terms,
$$\operatorname{plim}\hat\gamma=\gamma+\delta\,\frac{\operatorname{Cov}(w,z)}{\operatorname{Var}(w)} .$$

Remarks:

- The bias is the product of two things: how much $z$ matters for $y$ ($\delta$), and how strongly $z$ co-moves with $w$ ($\hat d_w$). If both have the same sign, $\hat\gamma$ is biased upwards; if the signs differ, it is biased downwards.
- The bias does not shrink as $n$ grows, so $\hat\gamma$ is inconsistent.
- Because $x$ and $w$ are orthogonal, the relation between $x$ and $z$ plays no part in the bias of $\hat\gamma$. It only contaminates $\hat\beta$, whose bias is $\delta S_{xz}/S_{xx}$ by the same argument.

## Question 1d

*When would the estimates from (2) be the same as those from (1)?*

Model (2) produces no estimate of $\delta$ (it implicitly fixes $\delta=0$), so we read the question as asking about $\alpha$, $\beta$ and $\gamma$, with $\delta$ entering through the condition.

Estimate (1) by OLS to get $\hat\alpha_L,\hat\beta_L,\hat\gamma_L,\hat\delta_L$, and run the auxiliary regression $z_i=\hat d_0+\hat d_x x_i+\hat d_w w_i+\text{residual}$. A standard algebraic identity (the sample version of the omitted-variable formula) links the short and long coefficients exactly:
$$\hat\beta_S=\hat\beta_L+\hat\delta_L\hat d_x,\qquad \hat\gamma_S=\hat\gamma_L+\hat\delta_L\hat d_w,\qquad \hat\alpha_S=\hat\alpha_L+\hat\delta_L\hat d_0 .$$
So the estimates coincide exactly when $\hat\delta_L\hat d=0$, which happens in one of two cases:

1. **$z$ is uncorrelated in the sample with the included regressors**, $S_{xz}=S_{wz}=0$, so $\hat d_x=\hat d_w=0$. Then $\hat\beta$ and $\hat\gamma$ are identical in both models. (With all three centred regressors mutually orthogonal, $X'X$ is diagonal in both models and every slope is a simple-regression slope.) The intercept also agrees only if $\hat d_0=\bar z=0$, i.e. $z$ has mean zero. Otherwise the short intercept absorbs $\hat\delta_L\bar z$.
2. **The long regression gives $\hat\delta_L=0$**, meaning $z$ adds nothing once $x$ and $w$ are included. This is also the only case in which "$\delta$ from model (2)", which is zero by construction, agrees with (1).

In expectation, the corresponding population condition is $\operatorname{Cov}(x,z)=\operatorname{Cov}(w,z)=0$ (or $\delta=0$) for $\beta$ and $\gamma$, plus $E[z]=0$ for $\alpha$. Even when these hold, leaving $z$ out still inflates the error variance, from $\sigma^2$ to $\sigma^2+\delta^2\operatorname{Var}(z)$, so the short model gives the same point estimates with larger standard errors.

## Question 1e

*Simulation: estimate a known two-predictor model with and without one of the predictors.*

**Set-up.** We generate data from $Y_i=a+bX_i+cZ_i+e_i$ with $a=1$, $b=2$, $c=3$. The predictors are $X_i\sim N(0,1)$ and $Z_i=\rho X_i+u_i$ with $u_i\sim N(0,1)$, so $\operatorname{Cov}(X,Z)=\rho$. The error $e_i\sim N(0,1)$ is drawn independently of $X$ and $Z$, as the question requires. We use $\rho=0.6$ and run $\rho=0$ as a control. For each sample we fit the long regression ($Y$ on $X$ and $Z$) and the short regression ($Y$ on $X$ only), and we record $\hat b$ from both. From 1c, the short-regression slope should settle at
$$\operatorname{plim}\hat b_{short}=b+c\,\frac{\operatorname{Cov}(X,Z)}{\operatorname{Var}(X)}=2+3(0.6)=3.8 .$$

**One sample, $n=200$.** Table 1.1 shows a single draw.

*Table 1.1 — Estimates of $b$ in one simulated sample ($n=200$, $\rho=0.6$; true $b=2$).*

{{TAB|p1e_one_run}}

The long model recovers $b$ well ({{CSV|p1e_one_run|Long model (X, Z)|Estimate|.3f}}, with 2 inside its confidence interval). Dropping $Z$ pushes the estimate to {{CSV|p1e_one_run|Short model (X only)|Estimate|.3f}}, and its 95% interval does not contain the true value 2. The short regression is not "noisier around 2". It is centred on the wrong number: $X$ takes credit for part of $Z$'s effect, because the two move together.

**Monte Carlo over sample sizes.** Table 1.2 repeats the experiment many times for each $n$.

*Table 1.2 — Mean and standard deviation of $\hat b$ across replications.*

{{TAB|p1e_montecarlo}}

{{FIG|p1e_hist|Figure 1.1 — Sampling distributions of $\hat b$ with and without Z (ρ = 0.6), for n = 100 and n = 10,000.}}

{{FIG|p1e_by_n|Figure 1.2 — Mean of $\hat b$ ± one standard deviation as the sample size grows (ρ = 0.6).}}

**What we notice.**

- With correlated predictors ($\rho=0.6$), the long model is centred on the true value $b=2$ at every sample size. The short model is centred near 3.8, exactly $b+c\rho$. The bias of about 1.8 is almost 90% of the true coefficient.
- **Increasing $n$ does not fix the problem.** As $n$ goes from 30 to 100,000, the spread of $\hat b_{short}$ falls roughly like $1/\sqrt n$ (from about {{CSV|p1e_montecarlo|#0|sd b_hat (short)|.2f}} to {{CSV|p1e_montecarlo|#4|sd b_hat (short)|.3f}}), but its mean stays at 3.8. A large sample only makes us more confident in the wrong answer: omitted variable bias is an inconsistency, not a small-sample effect.
- In the control case $\rho=0$, both regressions are centred on 2, because an omitted variable that is uncorrelated with $X$ causes no bias (case 1 of 1d). The price is precision. The omitted $cZ$ goes into the error, whose variance rises from 1 to $1+c^2=10$, so the short-model standard deviation is about $\sqrt{10}\approx3.2$ times larger at every $n$.

{{PAGEBREAK}}

# Problem 2 — Outliers

## Question 2a

*Sensitivity of regression models to outliers.*

OLS chooses the coefficients that minimise the **sum of squared residuals**. Squaring is what makes it fragile. A residual of 10 counts one hundred times as much as a residual of 1, so a single point far from the others can pull the whole fitted line towards itself. Put more formally, the influence of one observation on the OLS estimate is unbounded: moving one $y_i$ far enough can push $\hat\beta$ to any value. The breakdown point of OLS, the share of contaminated observations it can tolerate before the estimate can be pushed arbitrarily far, is $1/n$, which tends to zero. The median, by comparison, has a breakdown point of 50%.

It helps to separate three kinds of unusual point:

- **Outliers in $y$ (vertical outliers)** have large residuals but ordinary $x$-values. Near the centre of the data they change the slope little, but they shift the intercept and inflate the residual variance $\hat\sigma^2$. That widens every standard error, lowers $t$-statistics and $R^2$, and can hide effects that are really there.
- **High-leverage points** have unusual $x$-values. Leverage is measured by the hat value $h_{ii}=x_i'(X'X)^{-1}x_i$; in simple regression, $h_{ii}=1/n+(x_i-\bar x)^2/S_{xx}$. A high-leverage point that lies on the pattern of the rest ("good leverage") does little harm and even makes the slope more precise.
- **Influential points** are high-leverage points that are also off the pattern ("bad leverage"). These are the dangerous ones: the fitted line bends to pass close to them, so their own residual looks small and ordinary residual plots can fail to flag them. Cook's distance combines residual size and leverage to measure how much the fitted values change when a point is deleted.

Outliers also damage inference. Heavy-tailed errors violate normality, so small-sample $t$ and $F$ tests lose their exact justification. Several outliers can mask each other (each one hides the others, so deleting one at a time finds nothing) or swamp good points (make ordinary observations look unusual). In finance this is not a side issue: returns have fat tails, and crash days, earnings surprises and data errors (a misplaced decimal point, an unadjusted stock split) all produce extreme observations.

The usual workflow has three steps. First, **detect**: look at studentised residuals (values beyond about $\pm3$), leverage (above about $2k/n$), Cook's distance (above about $4/n$), and DFBETAS for the effect on each coefficient. Second, **investigate** before acting. An outlier may be a data error to correct, or a genuine event that carries information, and deleting real observations to improve the fit is poor practice. Third, **make the analysis robust** where needed. Options include estimators that down-weight large residuals (Huber or Tukey M-estimation, least absolute deviations, least trimmed squares), transformations such as logs that pull in long tails, winsorising, dummy variables for known events, and heteroskedasticity-robust standard errors for inference. A good habit is to report the OLS and robust results side by side: if they tell different stories, a handful of points is driving the conclusion.

## Question 2b

*Illustrate with a simulation how outliers change the estimated parameters.*

**How the simulation was built.**

1. **Clean baseline.** We draw $n=50$ values $x_i\sim U(0,10)$ and set $y_i=2+1.5x_i+\varepsilon_i$ with $\varepsilon_i\sim N(0,1)$ (seed 11). The true intercept and slope are therefore 2 and 1.5.
2. **Four contaminated copies** of the same 50 points, each changing one thing so its effect can be isolated:
    - **B. Vertical outlier.** One extra point at the centre of the $x$-range, $x=5$, placed 25 units above the true line.
    - **C. Bad leverage point.** One extra point far to the right, $(25,\,2)$. The true line gives 39.5 at $x=25$, so this point is both far out in $x$ and far off the line.
    - **D. Good leverage point.** One extra point at the same $x=25$, but lying on the true line (plus ordinary noise).
    - **E. Cluster of outliers.** Five of the original points (10% of the sample), chosen at random, have 15 added to their $y$-value.
3. **Estimation.** Each data set is fitted by OLS. We record $\hat\alpha$, $\hat\beta$, the standard error of $\hat\beta$, the residual standard error and $R^2$, plus the leverage and Cook's distance of the added point in B to D. As a benchmark we also fit a Huber M-estimator, a standard robust regression.
4. **Sensitivity curve.** Finally we add a single point at a chosen $x^*$, move its $y$-value across a grid from −40 to 80, and refit OLS each time. We do this at $x^*=5$ (centre), $x^*=15$ and $x^*=25$ (extreme).

**Results.**

*Table 2.1 — OLS estimates under each scenario (true α = 2, β = 1.5).*

{{TAB|p2b_scenarios}}

{{FIG|p2b_scenarios|Figure 2.1 — Clean-data OLS fit (blue), contaminated fit (red) and true line (dashed) for scenarios B to E.}}

- **B (vertical outlier at the centre).** The slope barely moves ({{CSV|p2b_scenarios|A. Clean data|beta_hat|.3f}} → {{CSV|p2b_scenarios|B. Vertical outlier (x=5)|beta_hat|.3f}}) because a point at the middle of the $x$-range has almost no leverage (h = {{CSV|p2b_scenarios|B. Vertical outlier (x=5)|leverage h (added pt)|.3f}}). But the damage shows elsewhere: the intercept rises, the residual standard error almost quadruples ({{CSV|p2b_scenarios|A. Clean data|resid. SE|.2f}} → {{CSV|p2b_scenarios|B. Vertical outlier (x=5)|resid. SE|.2f}}), the standard error of the slope grows by a similar factor, and $R^2$ falls from {{CSV|p2b_scenarios|A. Clean data|R2|.2f}} to {{CSV|p2b_scenarios|B. Vertical outlier (x=5)|R2|.2f}}. One bad point out of 51 makes a very precise relationship look much weaker.
- **C (bad leverage).** This single point is the most harmful. The slope collapses from {{CSV|p2b_scenarios|A. Clean data|beta_hat|.3f}} to {{CSV|p2b_scenarios|C. Bad leverage point (x=25, y=2)|beta_hat|.3f}}, less than half its true value, the intercept nearly triples, and $R^2$ drops to {{CSV|p2b_scenarios|C. Bad leverage point (x=25, y=2)|R2|.2f}}. The point's leverage is {{CSV|p2b_scenarios|C. Bad leverage point (x=25, y=2)|leverage h (added pt)|.2f}} (about half the total leverage of the sample, $\sum h_{ii}=2$), and its Cook's distance is {{CSV|p2b_scenarios|C. Bad leverage point (x=25, y=2)|Cook's D (added pt)|.1f}}, far above the usual $4/n\approx0.08$ warning level.
- **D (good leverage).** Same leverage as C, but the point follows the pattern. The estimates barely change, and the slope's standard error actually falls ({{CSV|p2b_scenarios|A. Clean data|SE(beta_hat)|.3f}} → {{CSV|p2b_scenarios|D. Good leverage point (x=25, on line)|SE(beta_hat)|.3f}}), because the point widens the $x$-range. Unusual $x$-values are not a problem in themselves; the problem is unusual $x$ combined with a $y$ that breaks the pattern.
- **E (10% contamination).** Several moderate outliers shift the slope to {{CSV|p2b_scenarios|E. 10% of points shifted up by 15|beta_hat|.3f}} and the intercept to {{CSV|p2b_scenarios|E. 10% of points shifted up by 15|alpha_hat|.2f}}, and they cut $R^2$ to {{CSV|p2b_scenarios|E. 10% of points shifted up by 15|R2|.2f}}. The direction of the slope change depends on where along the $x$-axis the contaminated points happen to sit.
- **Robust benchmark.** The Huber estimator stays close to 1.5 in every scenario (last column). The large gap between OLS and Huber in scenario C is exactly the kind of warning sign a practitioner should look for.

{{FIG|p2b_sensitivity|Figure 2.2 — OLS slope as one added observation's y-value moves from −40 to 80, at three x-positions.}}

Figure 2.2 shows the same mechanism continuously. At $x^*=5$ the slope stays between {{VAL|p2b_sens_range_x5.0|.2f}} and {{VAL|p2b_sens_range_x5.1|.2f}} however extreme the point is. At $x^*=25$ it ranges from {{VAL|p2b_sens_range_x25.0|.2f}} to {{VAL|p2b_sens_range_x25.1|.2f}}, and the lines are straight: the slope responds linearly and without limit to the $y$-value, with a sensitivity proportional to $(x^*-\bar x)$. This is the unbounded influence described in 2a, and it leads directly to 2c.

## Question 2c

*$n-1$ points lie on $y=0$ and one point $(x_n,y_n)$ has $x_n\to\infty$. Show that the OLS slope is driven by $y_n/x_n$.*

**Set-up.** Let $y_i=0$ for $i=1,\dots,n-1$, and write the mean and spread of the first $n-1$ $x$-values as
$$m=\frac1{n-1}\sum_{i=1}^{n-1}x_i,\qquad S_m=\sum_{i=1}^{n-1}(x_i-m)^2 .$$
These are fixed numbers that do not depend on $x_n$.

**Step 1: the pieces of $\hat\beta$.** The overall mean is $\bar x=\frac{(n-1)m+x_n}{n}$, so
$$x_n-\bar x=\frac{n-1}{n}(x_n-m),\qquad x_i-\bar x=(x_i-m)-\frac{x_n-m}{n}\quad(i<n).$$
The sum of squares splits as follows (the cross term vanishes because $\sum_{i<n}(x_i-m)=0$):
$$\begin{aligned}S_{xx}&=\sum_{i<n}(x_i-\bar x)^2+(x_n-\bar x)^2=S_m+(n-1)\frac{(x_n-m)^2}{n^2}+\frac{(n-1)^2(x_n-m)^2}{n^2}\\&=S_m+\frac{n-1}{n}(x_n-m)^2 .\end{aligned}$$
Since $\sum_i(x_i-\bar x)\bar y=0$ and $y_i=0$ for $i<n$, the cross-product has only one term:
$$S_{xy}=\sum_{i=1}^{n}(x_i-\bar x)y_i=(x_n-\bar x)\,y_n=\frac{n-1}{n}(x_n-m)\,y_n .$$

**Step 2: exact expression for the slope.**
$$\hat\beta=\frac{S_{xy}}{S_{xx}}=\frac{\frac{n-1}{n}(x_n-m)\,y_n}{S_m+\frac{n-1}{n}(x_n-m)^2}
=\frac{y_n}{x_n-m}\cdot\frac{1}{1+\dfrac{n\,S_m}{(n-1)(x_n-m)^2}} .$$

**Step 3: the limit.** Divide by $y_n/x_n$ (for $y_n\neq0$):
$$\frac{\hat\beta}{y_n/x_n}=\underbrace{\frac{x_n}{x_n-m}}_{\to\,1}\cdot\underbrace{\frac{1}{1+\dfrac{n\,S_m}{(n-1)(x_n-m)^2}}}_{\to\,1}\;\longrightarrow\;1\qquad\text{as }x_n\to\infty .$$
Hence $\hat\beta=\dfrac{y_n}{x_n}\big(1+O(1/x_n)\big)$. In particular, if the outlier moves out along a ray $y_n=kx_n$, then $\hat\beta\to k$; and whenever $y_n/x_n$ stays bounded, $\hat\beta-y_n/x_n\to0$. $\blacksquare$

**Interpretation.** The other $n-1$ observations enter the slope only through $m$ and $S_m$, and their contribution dies out at rates $1/x_n$ and $1/x_n^2$. It makes no difference that those $n-1$ points lie perfectly on a line with slope 0, or how many of them there are: for fixed $n$, one point far enough out decides the slope.

The same conclusion shows up in the leverage and residual of the outlier. Its hat value is
$$h_{nn}=\frac1n+\frac{(x_n-\bar x)^2}{S_{xx}}=\frac1n+\frac{\left(\frac{n-1}{n}\right)^2(x_n-m)^2}{S_m+\frac{n-1}{n}(x_n-m)^2}\;\longrightarrow\;\frac1n+\frac{n-1}{n}=1 .$$
Deleting point $n$ leaves a perfect fit to $y=0$, so its leave-one-out prediction error is $y_n$. The identity $e_n=(1-h_{nn})\,e_{(n)}$ then gives $e_n=(1-h_{nn})\,y_n$. Because $1-h_{nn}=O(1/x_n^2)$, the residual of the outlier goes to zero: the fitted line passes right through it, and a residual plot would never flag it.

*Table 2.2 — Numerical check with 20 points on y = 0 at x = 0, 0.5, …, 9.5.*

{{TAB|p2c_check}}

The ratio $\hat\beta/(y_n/x_n)$ approaches 1 and $h_{nn}$ approaches 1 in both cases, whether $y_n$ grows with $x_n$ or stays fixed at 10.

{{PAGEBREAK}}

# Problem 3 — Model selection

## Question 3a

*Find the best regression model for y in terms of x1 to x5 using at least two approaches.*

**Plan.** We use three complementary approaches and then check that they agree:

1. **All-subsets search.** With five candidate predictors there are only $2^5=32$ possible models (including the intercept-only one), so we can fit every one and rank them by adjusted $R^2$, AIC and BIC. Because nothing is left unexamined, this avoids the path-dependence of stepwise methods.
2. **Forward stepwise selection with AIC.** Start from the intercept-only model and at each step add the variable that lowers AIC the most. Stop when no addition lowers it.
3. **Backward elimination**, done two ways: (i) with BIC, dropping at each step the variable whose removal lowers BIC the most; and (ii) with $t$-tests, dropping the least significant variable while its $p$-value exceeds 5%.

The criteria penalise complexity in different ways. For a Gaussian linear model with $k$ estimated coefficients and residual sum of squares RSS,
$$\bar R^2=1-\frac{RSS/(n-k)}{TSS/(n-1)},$$
$$\mathrm{AIC}=n\ln\frac{RSS}{n}+2k+\text{const},\qquad \mathrm{BIC}=n\ln\frac{RSS}{n}+k\ln n+\text{const}.$$
The penalty per extra parameter is lightest for $\bar R^2$ (a variable is kept whenever its $|t|>1$), then AIC (roughly $|t|>\sqrt2$), then BIC (roughly $|t|>\sqrt{\ln n}$). So when the criteria disagree, we expect $\bar R^2$ to pick the largest model and BIC the smallest. Finally, we check the chosen model's out-of-sample fit with 10-fold cross-validation and examine its residuals.

{{IFDATA|3a}}
**Step 1: the data.** The data set has {{VAL|p3_n|}} observations.

*Table 3.1 — Descriptive statistics.*

{{TAB|p3_describe}}

*Table 3.2 — Correlation matrix.*

{{TAB|p3_corr}}

*Table 3.3 — Variance inflation factors in the full model.*

{{TAB|p3_vif}}

{{FIG|p3_scatter|Figure 3.1 — y against each candidate predictor.}}

All five predictors have means close to zero and similar spreads (standard deviations from 0.48 for x1 to about 1.08 for x4 and x5), so their coefficients can be compared directly. The correlations with y point to x4 (0.54), x2 (−0.42) and x3 (0.41) as the strongest candidates, x5 (−0.28) as weaker, and x1 (−0.06) as essentially unrelated to y.

The predictors are almost uncorrelated with each other. The largest correlation between two of them is −0.18 (x3 and x5), and every VIF is below 1.1, so multicollinearity is not a concern. This matters for selection: with nearly orthogonal predictors, coefficients barely change when variables are added or dropped, and the search methods are not pulled in different directions by redundant variables. The scatter plots show no curvature and no extreme points that would call for a transformation or special treatment.

**Step 2: the full model.**

*Table 3.4 — OLS with all five predictors.*

{{TAB|p3_full}}

In the full model x2, x3 and x4 are highly significant (|t| > 6), x5 is significant at 5% (t = −2.33, p = 0.022), and x1 is clearly not (t = −0.15, p = 0.88). $R^2=0.649$ and $\bar R^2=0.630$. The $t$-tests already suggest that x1 does not belong, but a set of individual $t$-tests is not a selection procedure, so we now compare the candidate models systematically.

**Step 3: all-subsets search.**

*Table 3.5 — Best model of each size (highest $R^2$ for that number of predictors).*

{{TAB|p3_best_by_size}}

*Table 3.6 — Top five models under each criterion.*

{{TAB|p3_top5}}

{{FIG|p3_criteria_by_size|Figure 3.2 — Adjusted R², AIC and BIC for all 32 models; the line joins the best model of each size.}}

All three criteria choose the same model: **x2 + x3 + x4 + x5** has the highest adjusted $R^2$ (0.634), the lowest AIC (260.62) and the lowest BIC (273.64) of all 32 models. Table 3.5 shows why. $R^2$ climbs steeply as x4, x3 and x2 enter (0.29, 0.48, 0.63), rises a little further with x5 (0.649), and does not move at all when x1 is added (0.6488 in both cases). The fifth variable adds nothing, so every criterion penalises it.

The case for x5 is weaker than for the others. Under BIC the four-variable model beats the best three-variable model (x2 + x3 + x4) by only 1.07 points (273.64 against 274.71); under AIC the gap is 3.67. This fits the thresholds described in the plan: x5's $|t|$ of 2.36 is well above AIC's $\sqrt2\approx1.41$ but only just above BIC's $\sqrt{\ln 100}\approx2.15$.

**Step 4: stepwise procedures.**

*Table 3.7 — Forward selection path (AIC).*

{{TAB|p3_forward_aic}}

*Table 3.8 — Backward elimination path (BIC).*

{{TAB|p3_backward_bic}}

*Table 3.9 — Backward elimination path ($t$-test, 5%).*

{{TAB|p3_backward_p}}

The stepwise searches reach the same model by different routes. Forward selection with AIC adds x4, x3, x2 and then x5, and stops because adding x1 would raise AIC from 260.62 to 262.59. Backward elimination with BIC removes x1 in its first step (BIC falls from 278.22 to 273.64), and stops because removing x5 next would raise BIC to 274.71. Backward elimination by $t$-tests also drops x1 first ($p=0.88$), then stops because x5 is significant ($p=0.021$). Because the predictors are nearly uncorrelated, the forward and backward paths agree; with correlated predictors they can end in different places, which is one reason we also ran the exhaustive search.

**Step 5: out-of-sample check.**

*Table 3.10 — 10-fold cross-validated mean squared error.*

{{TAB|p3_cv}}

Every procedure chose the same model, so cross-validation compares it with the full model and with the best three-variable model. The full model predicts slightly worse out of sample (MSE 0.865 against 0.854), as expected when an irrelevant variable is included. The three-variable model x2 + x3 + x4 does marginally better (0.846), but the difference, {{VAL|p3_cv_diff|.4f}}, is tiny next to its fold-to-fold standard error of {{VAL|p3_cv_diff_se|.3f}}. Cross-validation therefore cannot tell these two models apart; it only confirms that x5 is the least certain of the four variables.

**Step 6: final model and diagnostics.**

*Table 3.11 — Final model.*

{{TAB|p3_final}}

*Table 3.12 — Residual diagnostics for the final model.*

{{TAB|p3_diag}}

{{FIG|p3_final_diag|Figure 3.3 — Residual diagnostics for the final model.}}

The fitted final model is
$$\hat y=1.189-0.586\,x_2+0.559\,x_3+0.711\,x_4-0.197\,x_5$$
with $R^2=0.649$, $\bar R^2=0.634$ and $n=100$.
The coefficients are almost identical to those in the full model, which is what near-orthogonal predictors lead us to expect. The residual checks raise no concerns: the Jarque–Bera test does not reject normality ($p=0.14$), Breusch–Pagan finds no heteroskedasticity ($p=0.65$), RESET finds no missing non-linearity ($p=0.95$), and the residual plots show no pattern.

**Conclusion.** The best model for y uses **x2, x3, x4 and x5**. We did not pick it by trial and error. Five separate procedures (all-subsets search under adjusted $R^2$, AIC and BIC; forward selection with AIC; backward elimination with BIC; and backward elimination with $t$-tests) all arrive at it, and it passes the diagnostic checks. Every method rejects x1, which has no explanatory power. Every formal criterion keeps x5, but it is the weakest of the four; an analyst who wanted the most parsimonious model could defend x2 + x3 + x4 at almost no cost in predictive accuracy. One caution: the $p$-values in Table 3.11 come from the same data that were used to choose the model, so they are somewhat optimistic.
{{ENDIF}}

## Question 3b

*Which criterion is more reliable in general, BIC or AIC?*

**Short answer for a client:** if the goal is to find the true model, **BIC**. BIC is *consistent*: when the true model is among the candidates, the probability that BIC selects it tends to one as the sample grows. AIC does not have this property. Even with unlimited data, AIC keeps adding an irrelevant variable about 16% of the time. The proof follows.

**Set-up.** The true model is $M_1:\ y_i=\alpha+\beta x_i+\varepsilon_i$ with $k_1=2$ coefficients. The rival is $M_2:\ y_i=\alpha+\beta x_i+\gamma z_i+\mu_i$ with $k_2=3$, where $z$ is not needed ($\gamma=0$). With Gaussian errors, the maximised log-likelihood is $\ln\hat L_j=-\tfrac n2\big[\ln(2\pi)+1+\ln(RSS_j/n)\big]$, so, up to a common constant,
$$\mathrm{AIC}_j=n\ln\frac{RSS_j}{n}+2k_j,\qquad \mathrm{BIC}_j=n\ln\frac{RSS_j}{n}+k_j\ln n .$$
Define the likelihood-ratio statistic $LR_n=n\ln(RSS_1/RSS_2)\ge0$. Because $k_2-k_1=1$,
$$\text{AIC chooses }M_2\iff LR_n>2,\qquad \text{BIC chooses }M_2\iff LR_n>\ln n .$$

**Case 1: $M_1$ is true ($\gamma=0$).** We need the distribution of $LR_n$. The drop in RSS from adding $z$ satisfies $(RSS_1-RSS_2)/\sigma^2\sim\chi^2_1$ (exactly under normal errors, and in the limit otherwise), while $RSS_2/n\to\sigma^2$ in probability. Since $(RSS_1-RSS_2)/RSS_2=O_p(1/n)$ and $\ln(1+u)=u+o(u)$,
$$LR_n=n\ln\!\Big(1+\frac{RSS_1-RSS_2}{RSS_2}\Big)=\frac{RSS_1-RSS_2}{RSS_2/n}+o_p(1)\;\xrightarrow{d}\;\chi^2_1 .$$
($LR_n$ is asymptotically the squared $t$-statistic of $\hat\gamma$.) Therefore:

- **AIC:** $P(\text{AIC picks }M_2)=P(LR_n>2)\to P(\chi^2_1>2)=0.157$. The probability of choosing the wrong, over-fitted model does **not** go to zero, so AIC is not consistent.
- **BIC:** $P(\text{BIC picks }M_2)=P(LR_n>\ln n)$. $LR_n$ stays bounded in probability while $\ln n\to\infty$. For any fixed $K$, once $\ln n>K$ we have $P(LR_n>\ln n)\le P(LR_n>K)\to P(\chi^2_1>K)$, and this can be made as small as we like by choosing $K$ large. Hence $P(\text{BIC picks }M_2)\to0$.

**Case 2: $M_2$ is true ($\gamma\neq0$).** We also need to check that BIC does not *under*-fit. Now $RSS_1/n\to\sigma^2+\gamma^2\sigma^2_{z\cdot x}$, where $\sigma^2_{z\cdot x}>0$ is the variance of $z$ not explained by $x$, while $RSS_2/n\to\sigma^2$. So
$$\frac{LR_n}{n}\to\ln\!\Big(1+\frac{\gamma^2\sigma^2_{z\cdot x}}{\sigma^2}\Big)=c>0,$$
meaning $LR_n$ grows like $cn$, much faster than $\ln n$. Therefore $P(\text{BIC picks }M_2)\to1$ (and the same holds for AIC).

**Conclusion.** In both cases the probability that BIC selects the true model tends to 1, so **BIC is consistent and AIC is not**. The general rule is that a penalty $c_n$ per parameter gives consistent selection when $c_n\to\infty$ (so irrelevant variables, whose $LR$ stays bounded, are eventually rejected) and $c_n/n\to0$ (so relevant variables, whose $LR$ grows like $n$, are always kept). BIC's $c_n=\ln n$ meets both conditions; AIC's constant $c_n=2$ fails the first.

**Simulation check.** We simulated the set-up above (true $y=1+2x+\varepsilon$, irrelevant $z$, 2,000 replications per $n$).

*Table 3.13 — Share of samples in which each criterion picks the over-fitted model.*

{{TAB|p3b_sim}}

{{FIG|p3b_sim|Figure 3.4 — AIC's error rate levels off near 0.157; BIC's falls towards zero.}}

The AIC error rate settles near the theoretical 0.157 (it is a little higher in the smallest samples) and does not fall as $n$ grows, while the BIC error rate follows $P(\chi^2_1>\ln n)$ down towards zero.

**A fair caveat for the client.** AIC was built for a different goal: choosing the model with the best expected predictive accuracy (smallest Kullback–Leibler divergence). If the true model is not among the candidates, or the sample is small and prediction is the goal, AIC can forecast better, because a slightly over-fitted model costs little in prediction. But the question asked here, which criterion reliably finds the correct model as data accumulate, has a definite answer: BIC.

{{PAGEBREAK}}

# Problem 4 — Interpreting a wage regression

$$\ln(\text{wage})=\beta_0+\beta_1\,\text{educ}+\beta_2\,\text{gender}+\beta_3\,\text{age}+\beta_4\,\text{age}^2+\beta_5\,\text{degree}+\varepsilon$$

*Table 4.1 — Estimates given in the assignment, with the implied p-values, 95% confidence intervals (t with 1,994 d.f.) and exact percentage effects.*

{{TAB|p4_table}}

The reported $t$-statistics are consistent with coef/SE for every row.

## Question 4a

*Why is age² in the regression?*

Wages do not rise with age in a straight line. They grow quickly early in a career, as people gain skills and experience, then level off, and often fall a little near retirement. Adding $\text{age}^2$ lets the model capture this inverted-U shape. The effect of one more year of age becomes $\partial\ln(\text{wage})/\partial\,\text{age}=\beta_3+2\beta_4\,\text{age}$, which changes with age: positive when young and shrinking as age rises, as long as $\beta_4<0$. Without the squared term, the model would force the same percentage raise for every extra year at 25 and at 60.

## Question 4b

*Why use ln(wage) rather than wage as the dependent variable?*

Wages are strictly positive and strongly right-skewed: most people earn moderate amounts and a few earn a great deal. Taking logs makes the distribution much closer to symmetric (roughly normal), reduces heteroskedasticity (in levels, the spread of wages grows with their level), and limits the pull of the very highest earners on the estimates. It also turns multiplicative effects into additive ones, so each coefficient reads as an approximate percentage change in the wage, and fitted wages, $e^{\widehat{\ln w}}$, can never be negative.

## Question 4c

*Why use ln(wage) instead of wage? (the non-mathematical reason)*

Because that is how people actually think about pay: in percentages. Raises, pay gaps and returns to education are discussed as "3% a year" or "women earn 14% less", not as a fixed number of dollars. A year of extra schooling plausibly raises a cashier's and a surgeon's pay by a similar *percentage*, but certainly not by the same number of dollars, and a model in levels would force exactly that. Percentage effects are also comparable across countries, currencies and years, so they do not depend on the unit of pay or on inflation.

## Question 4d

*Interpret $\beta_1=0.08$.*

Holding gender, age and degree status fixed, each additional year of schooling is associated with an hourly wage about **8% higher** on average. The exact figure from the log model is $100(e^{0.08}-1)={{VAL|p4_educ_pct|.2f}}\%$. The effect is very precisely estimated ($t=8$, 95% CI 6.0% to 10.0% in log points). Two cautions apply. Because the degree dummy is held fixed, this is the return to a year of schooling that does *not* change degree status. And it is an association: part of it may reflect unobserved ability, which is correlated with schooling.

## Question 4e

*Is there a gender gap?*

The point estimate says women earn about 15 log points less than men with the same education, age and degree status, which is $100(e^{-0.15}-1)={{VAL|p4_gender_pct|.1f}}\%$. That is a large gap in economic terms. **But it is not statistically significant at conventional levels.** The $t$-statistic is −1.50, with a two-sided $p$-value of {{VAL|p4_gender_p2|.3f}}, and the 95% confidence interval for $\beta_2$ runs from −0.346 to +0.046 (roughly −29% to +5%) and includes zero. A one-sided test against $H_1:\beta_2<0$ gives $p={{VAL|p4_gender_p1|.3f}}$, significant at 10% but not at 5%.

So the honest answer is: **the data point to a gap of roughly 14% but cannot rule out zero at the 5% level.** This is not evidence that there is no gap. The standard error (0.10) is large, perhaps because of few women in the sample or variation the model does not capture, and the interval is consistent with anything from no gap to a very large one. Note also that this is the gap *conditional* on education and degree. If women face barriers in obtaining degrees, controlling for degree removes part of the overall gap from $\beta_2$.

## Question 4f

*At what age is the hourly wage highest?*

Differentiate the log wage with respect to age and set the result to zero:
$$\frac{\partial\ln(\text{wage})}{\partial\,\text{age}}=\hat\beta_3+2\hat\beta_4\,\text{age}=0\;\Longrightarrow\;\text{age}^*=-\frac{\hat\beta_3}{2\hat\beta_4}=-\frac{0.19}{2(-0.002)}=\mathbf{47.5\ years}.$$
The second derivative $2\hat\beta_4=-0.004<0$ confirms a maximum. Because the logarithm is increasing, the age that maximises ln(wage) also maximises the wage itself. Other variables do not affect this age, since they enter additively. Before 47.5 each extra year raises the wage by a shrinking amount (about 11% a year at 20, 3% a year at 40), and after 47.5 the wage declines slowly.

{{FIG|p4_age_profile|Figure 4.1 — Implied age–wage profile relative to the peak, other variables held fixed.}}

## Question 4g

*Average impact of holding an advanced degree on the hourly wage?*

Holding education, gender and age fixed, a Master's degree or higher is associated with a wage about **22 log points higher**, i.e. $100(e^{0.22}-1)={{VAL|p4_degree_pct|.1f}}\%$ higher. (With Kennedy's small-sample correction, $100(e^{\hat\beta_5-\frac12\widehat{SE}^2}-1)={{VAL|p4_degree_kennedy|.1f}}\%$, practically the same.) The effect is highly significant ($t=5.5$), and the 95% confidence interval for the premium is {{VAL|p4_degree_ci.0|.1f}}% to {{VAL|p4_degree_ci.1|.1f}}%. This premium comes on top of the return to the years of schooling the degree requires, so it measures the value of the credential itself. In money terms the impact depends on the wage level: roughly 25% of whatever the person would otherwise earn.

## Question 4h

*Could we use two dummies, "male" and "female", instead of "gender"?*

Not together with an intercept. Every person is either male or female, so $\text{male}_i+\text{female}_i=1$ for every observation, which is exactly the intercept column. The regressors would be perfectly collinear, $X'X$ would be singular, and OLS could not separate the coefficients. This is the **dummy variable trap**. With $m$ categories we include $m-1$ dummies; the omitted category (here men) is the reference, and the included dummy's coefficient measures the difference from it. We *could* include both dummies if we dropped the intercept. The two coefficients would then be group-specific intercepts, their difference would equal $\beta_2$, and the fit would be identical, so nothing is gained.

{{PAGEBREAK}}

# Problem 5 — Non-stationary series and cointegration

The three observed series are driven by one common random walk:
$$X_t=1.0\,w_t+\eta_t,\qquad Y_t=0.5\,w_t+\theta_t,\qquad Z_t=-1.0\,w_t+\chi_t,\qquad w_t=w_{t-1}+\varepsilon_t,$$
where $\eta,\theta,\chi$ (and $\varepsilon$) are I(0) white-noise terms, taken to be mutually independent with variances $\sigma^2_\eta,\sigma^2_\theta,\sigma^2_\chi,\sigma^2_\varepsilon$.

## Question 5a

*With $w_0=0$, prove $X_t=\sum_{i=0}^{t}\varepsilon_i+\eta_t$. Is X stationary? What about Y and Z?*

**Proof (by induction).** Claim: $w_t=\sum_{i=1}^{t}\varepsilon_i$. For $t=1$: $w_1=w_0+\varepsilon_1=\varepsilon_1$. If the claim holds for $t-1$, then $w_t=w_{t-1}+\varepsilon_t=\sum_{i=1}^{t-1}\varepsilon_i+\varepsilon_t=\sum_{i=1}^{t}\varepsilon_i$. Writing the sum from $i=0$, as in the question, changes nothing, because the $i=0$ term is the initial condition $w_0=0$ (equivalently, set $\varepsilon_0\equiv w_0=0$). Substituting into the equation for $X$:
$$X_t=w_t+\eta_t=\sum_{i=0}^{t}\varepsilon_i+\eta_t.\qquad\blacksquare$$

**Is X stationary? No, it is I(1).** Its mean is constant ($E[X_t]=0$), but its variance and autocovariances depend on time:
$$\operatorname{Var}(X_t)=t\,\sigma^2_\varepsilon+\sigma^2_\eta,\qquad \operatorname{Cov}(X_t,X_{t+h})=t\,\sigma^2_\varepsilon\quad(h\ge1).$$
The variance grows without bound, which violates covariance stationarity. Moreover $\operatorname{Corr}(X_t,X_{t+h})=t\sigma^2_\varepsilon/\sqrt{(t\sigma^2_\varepsilon+\sigma^2_\eta)((t+h)\sigma^2_\varepsilon+\sigma^2_\eta)}\to1$ as $t\to\infty$: shocks never die out. The first difference, however, is stationary:
$$\Delta X_t=\varepsilon_t+\eta_t-\eta_{t-1},$$
with mean 0, variance $\sigma^2_\varepsilon+2\sigma^2_\eta$, first-order autocovariance $-\sigma^2_\eta$, and zero autocovariance beyond lag 1 (an MA(1)-type process). One difference makes X stationary, so **X is integrated of order one, I(1)**.

**Y and Z.** The same argument gives $Y_t=0.5\sum_{i=0}^{t}\varepsilon_i+\theta_t$ and $Z_t=-\sum_{i=0}^{t}\varepsilon_i+\chi_t$, with $\operatorname{Var}(Y_t)=0.25\,t\,\sigma^2_\varepsilon+\sigma^2_\theta$ and $\operatorname{Var}(Z_t)=t\,\sigma^2_\varepsilon+\sigma^2_\chi$, both growing with $t$, while $\Delta Y_t=0.5\varepsilon_t+\Delta\theta_t$ and $\Delta Z_t=-\varepsilon_t+\Delta\chi_t$ are stationary. **Y and Z are also I(1).** Any series with a non-zero loading on the random walk $w$ inherits its unit root.

## Question 5b

*How many cointegrating vectors are there? Identify them.*

A vector $b=(b_1,b_2,b_3)'$ is cointegrating if $b'(X_t,Y_t,Z_t)'$ is stationary. Substituting the model,
$$b_1X_t+b_2Y_t+b_3Z_t=\underbrace{(b_1+0.5\,b_2-b_3)}_{\text{loading on }w_t}\,w_t+\underbrace{(b_1\eta_t+b_2\theta_t+b_3\chi_t)}_{\text{stationary}} .$$
The combination is stationary exactly when the random walk cancels:
$$b_1+0.5\,b_2-b_3=0\quad\Longleftrightarrow\quad b'a=0,\qquad a=(1,\;0.5,\;-1)' .$$
The set of such $b$ is the plane orthogonal to $a$, which has dimension $3-1=2$. Equivalently, there are $n=3$ variables and one common stochastic trend, so the cointegration rank is $r=n-(\text{number of common trends})=3-1=$ **2**.

A convenient basis for the cointegration space is
$$b^{(1)}=(1,\,-2,\,0)':\quad X_t-2Y_t=\eta_t-2\theta_t,\qquad b^{(2)}=(1,\,0,\,1)':\quad X_t+Z_t=\eta_t+\chi_t .$$
Both combinations are stationary white-noise mixtures. Other valid vectors, for example $(0,2,1)'$ giving $2Y_t+Z_t=2\theta_t+\chi_t$, are linear combinations of these two ($(0,2,1)'=b^{(2)}-b^{(1)}$), so they add no new independent relation. The individual vectors are unique only up to scaling and rotation; what is unique is the two-dimensional space they span. In the normalisation used by the Johansen/VECM software (identity in the first two rows), the same space is spanned by
$$\beta=\begin{pmatrix}1&0\\0&1\\1&0.5\end{pmatrix}:\qquad X_t+Z_t\ \text{ and }\ Y_t+0.5Z_t,$$
which is what the estimates in 5c should resemble. The rank cannot be 3, because that would require every series to be stationary on its own.

{{FIG|p5ab_sim|Figure 5.1 — Our own simulation of the model: the levels wander together (left) while X − 2Y and X + Z fluctuate around zero (right).}}

## Question 5c

*Using `dataset_Prob5.csv`: visual inspection, unit-root tests, Johansen trace and maximum-eigenvalue tests, cointegration rank, and VECM estimation.*

**Approach.** (1) Plot the levels, first differences, autocorrelation functions and pairwise scatter plots. (2) Test each series for a unit root with the augmented Dickey–Fuller (ADF) test (null: unit root; lag length by AIC; with constant, and with constant and trend) and cross-check with KPSS (null: stationarity), on levels and on first differences. (3) Choose the VAR lag length $p$ in levels by information criteria; the VECM then has $p-1$ lagged differences. (4) Run the Johansen procedure with a constant restricted to the cointegrating relations (the case that fits series with no trend) and read the trace and maximum-eigenvalue statistics sequentially, starting from $r=0$ and stopping at the first null that is not rejected at 5%. (5) Estimate the VECM
$$\Delta \mathbf y_t=\alpha\,(\beta'\mathbf y_{t-1}+\mathbf c)+\sum_{j=1}^{p-1}\Gamma_j\,\Delta\mathbf y_{t-j}+\mathbf u_t,$$
where $\beta$ holds the cointegrating vectors, $\mathbf c$ their constants, and $\alpha$ the adjustment speeds. (6) Compare $\hat\beta$ with the theory in 5b and check the residuals.

{{IFDATA|5c}}
**1. Visual inspection.** The data set has {{VAL|p5_T|}} observations.

{{FIG|p5c_levels|Figure 5.2 — The three series in levels (top) and first differences (bottom).}}

{{FIG|p5c_acf|Figure 5.3 — Sample ACFs of levels (top) and first differences (bottom); dotted lines are ±1.96/√T bands.}}

{{FIG|p5c_scatter|Figure 5.4 — Pairwise scatter plots of the levels.}}

*Table 5.1 — Descriptive statistics.*

{{TAB|p5_describe}}

All three series wander far from their starting values and do not return to a fixed mean. X, for instance, starts near zero, falls to about −14 around period 105, comes back close to zero between periods 210 and 260, and then falls again. There is no steady upward or downward trend, so no deterministic time trend is needed. X and Z are close to mirror images, and Y follows X with smaller swings. This is exactly what one shared random walk with loadings 1, 0.5 and −1 produces.

The first differences, by contrast, fluctuate around zero with a stable spread. The ACFs of the levels decay very slowly (still about 0.4 at lag 30), the classic sign of a unit root. The ACFs of the differences show a single negative spike at lag 1 and nothing after it. 5a predicts this: $\Delta X_t=\varepsilon_t+\eta_t-\eta_{t-1}$ is an MA(1) with first-order autocorrelation $-\sigma^2_\eta/(\sigma^2_\varepsilon+2\sigma^2_\eta)<0$. The scatter plots show very tight linear relations between the levels (correlations 0.961, −0.989 and −0.961), which already hints at cointegration.

**2. Unit-root tests.**

*Table 5.2 — ADF (constant; constant + trend) and KPSS (level) tests on levels and first differences.*

{{TAB|p5c_unitroot}}

For all three series in levels, ADF cannot reject a unit root ($p$ between 0.12 and 0.30 with a constant, between 0.21 and 0.35 with a constant and trend), and KPSS rejects stationarity at 1%. (statsmodels reports KPSS $p$-values only within 0.01–0.10, so 0.0100 means $p<0.01$ and 0.1000 means $p>0.10$.) In first differences the picture reverses: ADF rejects a unit root with $p<0.001$, and KPSS does not reject stationarity. The two tests have opposite null hypotheses and agree here, so **X, Y and Z are each I(1)**, as derived in 5a. This is the condition that makes a cointegration analysis meaningful.

**3. Lag length.**

*Table 5.3 — VAR lag-order selection in levels.*

{{TAB|p5c_lagselect}}

AIC, BIC and HQ all choose $p=1$, so the VECM has $p-1=0$ lagged differences. The residuals of that VECM show no remaining autocorrelation (Table 5.11), which supports the choice. Versions with one and two lagged differences are reported as robustness checks.

**4. Johansen cointegration test.**

*Deterministic terms.* The series drift without a trend and the model in the question has no deterministic terms. The standard choice for such data is a constant **restricted to the cointegrating relations** (Johansen's "case 2"). Each long-run relation may then have a non-zero mean, but the levels have no trend. This also matches the VECM estimated in step 5. statsmodels' `coint_johansen` does not offer this case, so the notebook computes the test directly by reduced-rank regression. As a check, the same code reproduces statsmodels' statistics exactly for the two cases statsmodels does offer (no deterministic terms, and unrestricted constant). The critical values for case 2 were simulated (20,000 replications of $n-r$ independent random walks of length 500) and agree closely with the published Osterwald-Lenum (1992) tables; the same simulations give the $p$-values.

*Table 5.4 — Simulated critical values for the restricted-constant case.*

{{TAB|p5c_cv_sim}}

*Table 5.5 — Johansen trace and maximum-eigenvalue tests (restricted constant, 0 lagged differences).*

{{TAB|p5c_johansen}}

Reading the trace test in sequence: $r=0$ is rejected (435.8 against a 5% critical value of 35.4), $r\le1$ is rejected (203.3 against 20.3), and $r\le2$ is **not** rejected (4.66 against 9.11, $p=${{VAL|p5_trace_r2_p|.2f}}). The maximum-eigenvalue test gives the same sequence. **Both tests give a cointegration rank of $r=2$**: two cointegrating vectors and one common stochastic trend, exactly as derived in 5b. The eigenvalues tell the same story, with two large values (0.54 and 0.49) and a third close to zero (0.015).

*Table 5.6 — Rank chosen at 5% under other specifications.*

{{TAB|p5c_johansen_robust}}

*Table 5.7 — Johansen statistics from statsmodels for its two built-in specifications (0 lagged differences).*

{{TAB|p5c_johansen_sm}}

The rank of 2 holds for every lag length from 0 to 4 and for the no-constant and unrestricted-constant versions. Only one combination disagrees: an unrestricted constant together with one lagged difference. There the $r\le2$ trace statistic is {{VAL|p5_uc_k1_r2_stat|.2f}} against a 5% critical value of {{VAL|p5_uc_k1_r2_cv95|.2f}}, which would give rank 3 at 5% (though not at 1%, where the critical value is {{VAL|p5_uc_k1_r2_cv99|.2f}}). We do not accept that result, for three reasons. A rank of 3 would mean every series is stationary, which the unit-root tests clearly reject. That specification allows a linear trend in the levels, which the data do not show. And the rejection is borderline and disappears under every other specification.

**5. VECM estimates.** With $r=2$, a constant restricted to the cointegrating relations and no lagged differences, the model is
$$\Delta\mathbf y_t=\alpha\,(\beta'\mathbf y_{t-1}+\mathbf c)+\mathbf u_t,\qquad \mathbf y_t=(X_t,Y_t,Z_t)' .$$

*Table 5.8 — Cointegrating vectors $\hat\beta$ (normalised so the top block is the identity) and their constants.*

{{TAB|p5c_beta}}

*Table 5.9 — Adjustment coefficients $\hat\alpha$.*

{{TAB|p5c_alpha}}

Written out, the estimated system is
$$\begin{aligned}
\Delta X_t&=-0.471\,\text{ect}_{1,t-1}+0.261\,\text{ect}_{2,t-1}+u_{X,t}\\
\Delta Y_t&=\phantom{-}0.149\,\text{ect}_{1,t-1}-0.934\,\text{ect}_{2,t-1}+u_{Y,t}\\
\Delta Z_t&=-0.533\,\text{ect}_{1,t-1}-0.257\,\text{ect}_{2,t-1}+u_{Z,t}
\end{aligned}
\qquad
\begin{aligned}
\text{ect}_{1,t}&=X_t+1.008\,Z_t-0.090\\
\text{ect}_{2,t}&=Y_t+0.416\,Z_t-0.154
\end{aligned}$$

*Long-run relations.* The theory in 5b says the cointegration space is spanned by $X+Z$ and $Y+0.5Z$ in this normalisation. The estimates are $X+1.008Z$ (standard error on Z 0.009, $t=${{VAL|p5_bz1_t|.2f}} against the theoretical value 1) and $Y+0.416Z$ (standard error 0.065, $t=${{VAL|p5_bz2_t|.2f}} against 0.5). Neither differs significantly from theory, so the data support the relations derived in 5b. Eliminating Z between the two relations gives $X-2.42\,Y$, against the $X-2Y$ of 5b. The ratio 1.008/0.416 carries the larger sampling error of the second vector (a delta-method standard error of about 0.38), so this is also consistent with theory. The constants ($-0.09$ and $-0.15$) are small relative to the scale of the series.

*Adjustment.* When $X+Z$ is above its long-run level, X and Z both fall in the next period (α = −0.47 and −0.53, $|t|\approx5$), which pulls the sum back; the two variables share the correction about equally. Deviations in the second relation are corrected almost entirely by Y (α = −0.93, $t=-13.2$), which removes about 93% of a deviation within one period. The remaining loadings are smaller, with $|t|$ between 2.1 and 2.7. Such fast adjustment fits the data-generating process: the deviations from the long-run relations are combinations of white-noise terms (for example $\eta_t+\chi_t$), so they do not persist.

*Table 5.10 — The long-run coefficients with 0, 1 and 2 lagged differences.*

{{TAB|p5c_beta_robust}}

Adding lagged differences leaves the long-run coefficients essentially unchanged (1.006–1.008 and 0.415–0.416). A likelihood-ratio test would add one lag (LR = {{VAL|p5_lr_k1|.1f}}, $p=${{VAL|p5_lr_k1_p|.3f}}) even though all three information criteria prefer none. Since the extra lag only captures some short-run dynamics and changes none of the conclusions, we keep the specification the criteria choose.

{{FIG|p5c_ect|Figure 5.5 — Estimated cointegrating relations $\hat\beta'\mathbf y_t$ (demeaned): both fluctuate around zero with no persistence.}}

*Table 5.11 — Residual autocorrelation tests for the VECM.*

{{TAB|p5c_resid}}

The Ljung–Box tests on each equation ($p$ = 0.37, 0.96 and 0.49) and the system portmanteau test ($p=0.69$) find no remaining autocorrelation, so the model captures the dynamics adequately.

**Summary of 5c.** Visual inspection and unit-root tests show that X, Y and Z are each I(1). The Johansen trace and maximum-eigenvalue tests both give a cointegration rank of 2. The estimated VECM recovers long-run relations that match the theoretical cointegrating vectors from 5b, with fast and significant error correction.
{{ENDIF}}

{{PAGEBREAK}}

# Problem 6 — AR and MA representations

## Question 6a

*Write the first four terms of the MA(∞) representation of $Y_t=0.5\,Y_{t-1}+\varepsilon_t$.*

**Step 1: substitute backwards.** Apply the model to $Y_{t-1}$, then $Y_{t-2}$, and so on:
$$\begin{aligned}
Y_t&=\varepsilon_t+0.5\,Y_{t-1}\\
&=\varepsilon_t+0.5\,(\varepsilon_{t-1}+0.5\,Y_{t-2})=\varepsilon_t+0.5\,\varepsilon_{t-1}+0.5^2\,Y_{t-2}\\
&=\varepsilon_t+0.5\,\varepsilon_{t-1}+0.5^2(\varepsilon_{t-2}+0.5\,Y_{t-3})=\varepsilon_t+0.5\,\varepsilon_{t-1}+0.5^2\,\varepsilon_{t-2}+0.5^3\,Y_{t-3}\\
&\;\;\vdots\\
&=\sum_{j=0}^{k-1}0.5^j\,\varepsilon_{t-j}+0.5^k\,Y_{t-k}.
\end{aligned}$$

**Step 2: the remainder vanishes.** Because $|0.5|<1$ the process is stationary, with finite variance $\operatorname{Var}(Y)$, so
$$E\big[(0.5^kY_{t-k})^2\big]=0.25^k\operatorname{Var}(Y)\to0\quad(k\to\infty).$$
The remainder goes to zero in mean square, and
$$Y_t=\sum_{j=0}^{\infty}0.5^j\,\varepsilon_{t-j},\qquad \psi_j=0.5^j .$$

**Step 3 (check with the lag operator).** Writing the model as $(1-0.5L)Y_t=\varepsilon_t$ and inverting with the geometric series (valid since $|0.5|<1$):
$$Y_t=(1-0.5L)^{-1}\varepsilon_t=(1+0.5L+0.5^2L^2+0.5^3L^3+\cdots)\,\varepsilon_t .$$
Matching coefficients in $(1-0.5L)(\psi_0+\psi_1L+\psi_2L^2+\cdots)=1$ gives $\psi_0=1$ and $\psi_j-0.5\,\psi_{j-1}=0$, so $\psi_j=0.5^j$, the same answer.

**First four terms:**
$$\boxed{\;Y_t=\varepsilon_t+0.5\,\varepsilon_{t-1}+0.25\,\varepsilon_{t-2}+0.125\,\varepsilon_{t-3}+\cdots\;}$$

As a by-product, $\operatorname{Var}(Y_t)=\sigma^2\sum_j0.25^j=\sigma^2/(1-0.25)=\tfrac43\sigma^2$. Table 6.1 confirms the weights numerically.

*Table 6.1 — ψ-weights from statsmodels versus 0.5^j.*

{{TAB|p6a_psi}}

## Question 6b

*Find the autocorrelations of order 1 and 2 for $Z_t=0.6\,Z_{t-1}+0.2\,Z_{t-2}+\varepsilon_t$.*

**Stationarity first.** The characteristic equation $1-0.6x-0.2x^2=0$ has roots $x=\frac{-0.6\pm\sqrt{0.36+0.8}}{0.4}$, i.e. $x\approx1.193$ and $x\approx-4.193$. Both lie outside the unit circle, so the process is stationary. (Equivalently: $\phi_1+\phi_2=0.8<1$, $\phi_2-\phi_1=-0.4<1$, $|\phi_2|=0.2<1$.) The autocorrelations are therefore well defined and do not depend on $t$.

**Yule–Walker equations.** Multiply both sides by $Z_{t-k}$ ($k\ge1$) and take expectations. Since $Z_{t-k}$ depends only on shocks up to time $t-k$, $E[\varepsilon_tZ_{t-k}]=0$, so
$$\gamma_k=0.6\,\gamma_{k-1}+0.2\,\gamma_{k-2}\quad\Longrightarrow\quad \rho_k=0.6\,\rho_{k-1}+0.2\,\rho_{k-2}\qquad(\text{dividing by }\gamma_0).$$

**Order 1** ($k=1$, using $\rho_0=1$ and $\rho_{-1}=\rho_1$):
$$\rho_1=0.6+0.2\,\rho_1\;\Longrightarrow\;0.8\,\rho_1=0.6\;\Longrightarrow\;\boxed{\rho_1=\frac{0.6}{0.8}=0.75}$$

**Order 2** ($k=2$):
$$\boxed{\rho_2=0.6\,\rho_1+0.2\,\rho_0=0.6(0.75)+0.2=0.65}$$

For completeness, the variance follows from multiplying the model by $Z_t$: $\gamma_0=0.6\gamma_1+0.2\gamma_2+\sigma^2$, so $\gamma_0=\sigma^2/(1-0.6\rho_1-0.2\rho_2)=\sigma^2/0.42\approx2.38\,\sigma^2$. Higher-order autocorrelations follow from the same recursion ($\rho_3=0.54$, $\rho_4=0.454$, …) and decay geometrically.

*Table 6.2 — Autocorrelations: hand recursion, statsmodels, and a simulated path of 200,000 observations.*

{{TAB|p6b_acf}}

All three columns agree: $\rho_1=0.75$ and $\rho_2=0.65$.
