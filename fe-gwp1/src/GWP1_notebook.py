# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Financial Econometrics — Group Work Project 1: Code Notebook
#
# This notebook holds all of the code behind the written report. The report
# itself contains the answers, derivations, tables and figures; this notebook
# produces every number and figure used there.
#
# **Data files.** Place the two course files in the `data/` folder next to
# this notebook before running:
#
# * `data/FE-GWP1_model_selection_1.csv` (Problem 3a)
# * `data/FE-GWP1_dataset_Prob5.csv` (Problem 5c)
#
# Run with *Kernel → Restart & Run All*. Every random step uses a fixed seed,
# so the output is reproducible.

# %%
import os, json, itertools, warnings
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan, acorr_ljungbox
from statsmodels.stats.stattools import jarque_bera
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.api import VAR
from statsmodels.tsa.vector_ar.vecm import coint_johansen, VECM, select_order
from statsmodels.tsa.arima_process import arma2ma, arma_acf, ArmaProcess
from statsmodels.tsa.stattools import acf

warnings.filterwarnings("ignore")
pd.set_option("display.float_format", lambda v: f"{v:,.4f}")
plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 200, "axes.grid": True,
                     "grid.alpha": 0.3, "axes.spines.top": False,
                     "axes.spines.right": False, "font.size": 10})

DATA_DIR = os.environ.get("GWP_DATA_DIR", "data")
OUT = os.environ.get("GWP_OUT_DIR", "outputs")
FIG, TAB = os.path.join(OUT, "figures"), os.path.join(OUT, "tables")
os.makedirs(FIG, exist_ok=True); os.makedirs(TAB, exist_ok=True)
RESULTS = {}  # key numbers used in the report

def savefig(name):
    plt.tight_layout()
    plt.savefig(os.path.join(FIG, name + ".png"), bbox_inches="tight")
    plt.show()

def savetab(df, name, floatfmt=".4f", index=True):
    """Save a table as pipe-markdown so the report can include it."""
    df.to_csv(os.path.join(TAB, name + ".csv"), index=index)
    shown = df.copy()
    for c in shown.columns:  # print whole numbers without decimals
        col = shown[c]
        if pd.api.types.is_numeric_dtype(col) and col.dropna().size and np.allclose(col.dropna() % 1, 0) \
                and col.dropna().abs().max() >= 1 and c not in ("rho",):
            shown[c] = col.map(lambda v: "–" if pd.isna(v) else f"{int(round(v)):,}")
    with open(os.path.join(TAB, name + ".md"), "w") as f:
        f.write(shown.to_markdown(floatfmt=floatfmt, index=index))
    return df

def ols(y, X):
    """Plain OLS with an intercept, via statsmodels."""
    return sm.OLS(y, sm.add_constant(X)).fit()

# %% [markdown]
# ---
# ## Problem 1 — Omitted variable bias
#
# Questions 1a to 1d are analytical and are answered in the report.
# Below is a small numerical check of the 1b/1c formulas, followed by the
# simulation study for 1e.
#
# ### Check of 1b and 1c
# We build x and w to be exactly orthogonal in the sample (after centring),
# generate y from the full model (1), estimate the short model (2), and
# compare the estimated γ with the closed-form expression from 1c.

# %%
rng = np.random.default_rng(101)
n = 400
x = rng.normal(size=n); x -= x.mean()
w = rng.normal(size=n); w -= w.mean()
w -= (w @ x) / (x @ x) * x              # make w exactly orthogonal to x
z = 0.8 * w - 0.4 * x + rng.normal(size=n)
alpha, beta, gamma, delta = 1.0, 2.0, -1.0, 1.5
y = alpha + beta * x + gamma * w + delta * z + rng.normal(size=n)

short = ols(y, np.column_stack([x, w]))
b_simple = np.sum((x - x.mean()) * (y - y.mean())) / np.sum((x - x.mean()) ** 2)
g_simple = np.sum((w - w.mean()) * (y - y.mean())) / np.sum((w - w.mean()) ** 2)
d_wz = np.sum((w - w.mean()) * (z - z.mean())) / np.sum((w - w.mean()) ** 2)
long_ = ols(y, np.column_stack([x, w, z]))
check1 = pd.DataFrame({
    "short-model OLS": short.params[1:3],
    "simple-regression formula (1b)": [b_simple, g_simple],
    "long-model OLS": long_.params[1:3],
}, index=["beta", "gamma"])
print(check1)
print("\nPredicted gamma-hat from 1c: gamma_hat_long + delta_hat * d_wz =",
      round(long_.params[2] + long_.params[3] * d_wz, 6))

# %% [markdown]
# ### 1e — Simulation of omitted variable bias
#
# **Design.** True model $Y_i = a + bX_i + cZ_i + e_i$ with
# $a = 1$, $b = 2$, $c = 3$.
#
# * $X_i \sim N(0,1)$
# * $Z_i = \rho X_i + u_i$, $u_i \sim N(0,1)$, so X and Z are correlated when $\rho \neq 0$.
# * $e_i \sim N(0,1)$, drawn independently of both X and Z.
#
# We fit the long regression (X and Z) and the short regression (X only).
# Theory says the short-regression slope converges to
# $b + c\,\mathrm{Cov}(X,Z)/\mathrm{Var}(X) = b + c\rho$.
# With $\rho = 0.6$ that is $2 + 3(0.6) = 3.8$.

# %%
a_true, b_true, c_true = 1.0, 2.0, 3.0

def simulate_once(n, rho, rng):
    X = rng.normal(size=n)
    Z = rho * X + rng.normal(size=n)
    e = rng.normal(size=n)
    Y = a_true + b_true * X + c_true * Z + e
    one = np.ones(n)
    b_long = np.linalg.lstsq(np.column_stack([one, X, Z]), Y, rcond=None)[0][1]
    b_short = np.linalg.lstsq(np.column_stack([one, X]), Y, rcond=None)[0][1]
    return b_long, b_short, np.corrcoef(X, Z)[0, 1]

# One sample of n = 200, printed in full
rng = np.random.default_rng(2024)
n = 200
X = rng.normal(size=n); Z = 0.6 * X + rng.normal(size=n); e = rng.normal(size=n)
Y = a_true + b_true * X + c_true * Z + e
m_long = ols(Y, pd.DataFrame({"X": X, "Z": Z}))
m_short = ols(Y, pd.DataFrame({"X": X}))
print(m_long.summary().tables[1]); print(m_short.summary().tables[1])
one_run = pd.DataFrame({
    "Estimate": [m_long.params["X"], m_short.params["X"]],
    "Std. error": [m_long.bse["X"], m_short.bse["X"]],
    "95% CI low": [m_long.conf_int().loc["X", 0], m_short.conf_int().loc["X", 0]],
    "95% CI high": [m_long.conf_int().loc["X", 1], m_short.conf_int().loc["X", 1]],
    "R-squared": [m_long.rsquared, m_short.rsquared],
}, index=["Long model (X, Z)", "Short model (X only)"])
savetab(one_run, "p1e_one_run")
RESULTS["p1e_corrXZ"] = float(np.corrcoef(X, Z)[0, 1])
one_run

# %% [markdown]
# **Monte Carlo over sample sizes.** For each sample size we repeat the
# experiment many times and record the mean and standard deviation of
# $\hat b$ from both regressions. We run it for correlated regressors
# ($\rho = 0.6$) and, as a control, for independent regressors ($\rho = 0$).

# %%
rng = np.random.default_rng(7)
sizes = [30, 100, 1_000, 10_000, 100_000]
reps = {30: 2000, 100: 2000, 1_000: 2000, 10_000: 1000, 100_000: 200}
rows, draws = [], {}
for rho in [0.6, 0.0]:
    for n in sizes:
        sims = np.array([simulate_once(n, rho, rng) for _ in range(reps[n])])
        draws[(rho, n)] = sims
        rows.append({"rho": rho, "n": n, "replications": reps[n],
                     "mean b_hat (long)": sims[:, 0].mean(),
                     "sd b_hat (long)": sims[:, 0].std(ddof=1),
                     "mean b_hat (short)": sims[:, 1].mean(),
                     "sd b_hat (short)": sims[:, 1].std(ddof=1),
                     "theory plim (short)": b_true + c_true * rho})
mc = pd.DataFrame(rows)
savetab(mc, "p1e_montecarlo", index=False)
mc

# %%
fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=False)
for ax, n in zip(axes, [100, 10_000]):
    s = draws[(0.6, n)]
    ax.hist(s[:, 0], bins=40, alpha=0.7, label=r"long model (X, Z)", color="#2a6f97")
    ax.hist(s[:, 1], bins=40, alpha=0.7, label=r"short model (X only)", color="#c8553d")
    ax.axvline(b_true, color="k", ls="--", lw=1, label="true b = 2")
    ax.axvline(b_true + c_true * 0.6, color="#c8553d", ls=":", lw=1.2, label="b + c·ρ = 3.8")
    ax.set_title(f"Sampling distribution of $\\hat b$, n = {n:,}")
    ax.set_xlabel(r"$\hat b$")
axes[0].legend(fontsize=8)
savefig("p1e_hist")

# %%
fig, ax = plt.subplots(figsize=(7, 3.6))
sub = mc[mc.rho == 0.6]
ax.errorbar(sub.n, sub["mean b_hat (long)"], yerr=sub["sd b_hat (long)"], fmt="o-",
            capsize=3, label="long model", color="#2a6f97")
ax.errorbar(sub.n, sub["mean b_hat (short)"], yerr=sub["sd b_hat (short)"], fmt="s-",
            capsize=3, label="short model", color="#c8553d")
ax.axhline(2, color="k", ls="--", lw=1); ax.axhline(3.8, color="#c8553d", ls=":", lw=1)
ax.set_xscale("log"); ax.set_xlabel("sample size n (log scale)")
ax.set_ylabel(r"mean of $\hat b$  ± 1 sd")
ax.set_title(r"Estimates of b as n grows ($\rho$ = 0.6)")
ax.legend()
savefig("p1e_by_n")

# %% [markdown]
# ---
# ## Problem 2 — Outliers
#
# ### 2b — Simulation
#
# **Design.**
# 1. Baseline ("clean") data: $n = 50$, $x_i \sim U(0,10)$,
#    $y_i = 2 + 1.5x_i + \varepsilon_i$, $\varepsilon_i \sim N(0,1)$, seed 11.
# 2. We then create four contaminated copies of the same 50 points:
#    * **B. Vertical outlier:** add one point at the centre of the x-range, $(5,\; 2+1.5\cdot5+25)$.
#    * **C. Bad leverage point:** add one point far to the right, $(25,\; 2)$, well below the true line (which gives 39.5 at x = 25).
#    * **D. Good leverage point:** add one point at $x = 25$ that lies on the true line (plus normal noise).
#    * **E. Cluster of outliers:** shift the y-values of 5 randomly chosen points (10% of the sample) up by 15.
# 3. Each data set is fitted by OLS. We record the intercept, slope, slope standard
#    error, residual standard error and $R^2$, and the leverage and Cook's distance of
#    the added point. As a reference we also fit a Huber M-estimator (robust regression).
# 4. Finally we move a single added point's y-value across a grid, at a central x and at
#    an extreme x, to show how the slope responds.

# %%
rng = np.random.default_rng(11)
n0 = 50
x0 = rng.uniform(0, 10, n0)
y0 = 2 + 1.5 * x0 + rng.normal(0, 1, n0)

scen = {"A. Clean data": (x0, y0, None)}
scen["B. Vertical outlier (x=5)"] = (np.append(x0, 5.0), np.append(y0, 2 + 1.5 * 5 + 25), n0)
scen["C. Bad leverage point (x=25, y=2)"] = (np.append(x0, 25.0), np.append(y0, 2.0), n0)
scen["D. Good leverage point (x=25, on line)"] = (np.append(x0, 25.0), np.append(y0, 2 + 1.5 * 25 + rng.normal()), n0)
idx = rng.choice(n0, 5, replace=False)
yE = y0.copy(); yE[idx] += 15
scen["E. 10% of points shifted up by 15"] = (x0, yE, idx)

rows = []
fits = {}
for name, (xs, ys, k) in scen.items():
    f = ols(ys, xs)
    fits[name] = f
    infl = f.get_influence()
    rlm = sm.RLM(ys, sm.add_constant(xs), M=sm.robust.norms.HuberT()).fit()
    lev = cook = np.nan
    if isinstance(k, (int, np.integer)):
        lev = infl.hat_matrix_diag[k]; cook = infl.cooks_distance[0][k]
    rows.append({"Scenario": name, "n": len(xs), "alpha_hat": f.params[0], "beta_hat": f.params[1],
                 "SE(beta_hat)": f.bse[1], "resid. SE": np.sqrt(f.scale), "R2": f.rsquared,
                 "leverage h (added pt)": lev, "Cook's D (added pt)": cook,
                 "Huber beta_hat": rlm.params[1]})
p2b = pd.DataFrame(rows).set_index("Scenario")
savetab(p2b, "p2b_scenarios", floatfmt=".3f")
p2b

# %%
fig, axes = plt.subplots(2, 2, figsize=(10, 7.2), sharex=True, sharey=True)
grid = np.linspace(0, 26, 100)
fA = fits["A. Clean data"]
for ax, name in zip(axes.ravel(), list(scen)[1:]):
    xs, ys, k = scen[name]
    f = fits[name]
    mask = np.zeros(len(xs), bool)
    if isinstance(k, (int, np.integer)): mask[k] = True
    else: mask[k] = True
    ax.scatter(xs[~mask], ys[~mask], s=14, color="0.45", label="data")
    ax.scatter(xs[mask], ys[mask], s=45, color="#c8553d", marker="D", label="outlier(s)")
    ax.plot(grid, 2 + 1.5 * grid, "k--", lw=1, label="true line")
    ax.plot(grid, fA.params[0] + fA.params[1] * grid, color="#2a6f97", lw=1.5, label="OLS, clean data")
    ax.plot(grid, f.params[0] + f.params[1] * grid, color="#c8553d", lw=1.8, label="OLS, contaminated")
    ax.set_title(f"{name}\nslope {fA.params[1]:.3f} → {f.params[1]:.3f}", fontsize=9)
axes[0, 0].legend(fontsize=7, loc="upper left")
for ax in axes[1]: ax.set_xlabel("x")
for ax in axes[:, 0]: ax.set_ylabel("y")
savefig("p2b_scenarios")

# %%
# Sensitivity curve: add one point (x*, y*), move y* over a grid, record the slope
ygrid = np.linspace(-40, 80, 121)
fig, ax = plt.subplots(figsize=(7, 3.8))
sens = {}
for xstar, col in [(5.0, "#2a6f97"), (15.0, "#e09f3e"), (25.0, "#c8553d")]:
    slopes = [ols(np.append(y0, ys_), np.append(x0, xstar)).params[1] for ys_ in ygrid]
    sens[xstar] = slopes
    ax.plot(ygrid, slopes, color=col, label=f"added point at x = {xstar:g}")
ax.axhline(fA.params[1], color="k", ls="--", lw=1, label="slope, clean data")
ax.set_xlabel("y-value of the added point"); ax.set_ylabel(r"OLS slope $\hat\beta$")
ax.set_title("Slope as a function of one added observation")
ax.legend(fontsize=8)
savefig("p2b_sensitivity")
RESULTS["p2b_sens_range_x5"] = [float(min(sens[5.0])), float(max(sens[5.0]))]
RESULTS["p2b_sens_range_x25"] = [float(min(sens[25.0])), float(max(sens[25.0]))]

# %% [markdown]
# ### 2c — Numerical check of the limit result
# $n-1 = 20$ points lie on $y = 0$ at $x = 0, 0.5, \dots, 9.5$. A single point
# $(x_n, y_n)$ is added. We use two cases: $y_n = 0.5\,x_n$ (so $y_n/x_n = 0.5$),
# and a fixed $y_n = 10$ (so $y_n/x_n \to 0$).

# %%
xb = np.arange(0, 10, 0.5); yb = np.zeros_like(xb)
rows = []
for xn in [10, 20, 50, 100, 1_000, 10_000, 100_000]:
    for label, yn in [("y_n = 0.5 x_n", 0.5 * xn), ("y_n = 10", 10.0)]:
        f = ols(np.append(yb, yn), np.append(xb, xn))
        h = f.get_influence().hat_matrix_diag[-1]
        rows.append({"case": label, "x_n": xn, "y_n": yn, "y_n/x_n": yn / xn,
                     "OLS slope": f.params[1], "slope / (y_n/x_n)": f.params[1] / (yn / xn),
                     "leverage h_nn": h})
p2c = pd.DataFrame(rows)
savetab(p2c, "p2c_check", floatfmt=".5g", index=False)
p2c

# %% [markdown]
# ---
# ## Problem 3 — Model selection
# ### 3a — Data set `FE-GWP1_model_selection_1.csv`

# %%
ms_path = os.path.join(DATA_DIR, "FE-GWP1_model_selection_1.csv")
ms = pd.read_csv(ms_path)
ms.columns = [c.strip() for c in ms.columns]
ms = ms.rename(columns={c: c.lower() for c in ms.columns})
ms = ms[[c for c in ms.columns if c in ["y", "x1", "x2", "x3", "x4", "x5"]]].dropna()
PRED = ["x1", "x2", "x3", "x4", "x5"]
print(ms.shape)
desc = ms.describe().T
savetab(desc, "p3_describe", floatfmt=".3f")
RESULTS["p3_n"] = int(len(ms))
desc

# %%
corr = ms.corr()
savetab(corr, "p3_corr", floatfmt=".3f")
Xv = sm.add_constant(ms[PRED])
vif = pd.DataFrame({"VIF": [variance_inflation_factor(Xv.values, i) for i in range(1, Xv.shape[1])]},
                   index=PRED)
savetab(vif, "p3_vif", floatfmt=".2f")
display(corr); display(vif)

# %%
fig, axes = plt.subplots(1, 5, figsize=(13, 2.8), sharey=True)
for ax, v in zip(axes, PRED):
    ax.scatter(ms[v], ms["y"], s=8, alpha=0.6, color="#2a6f97")
    ax.set_xlabel(v)
axes[0].set_ylabel("y")
fig.suptitle("y against each candidate predictor", y=1.02)
savefig("p3_scatter")

# %% [markdown]
# **Full model.** Start with all five predictors to see the individual t-tests.

# %%
full = smf.ols("y ~ " + " + ".join(PRED), data=ms).fit()
print(full.summary())
full_tab = pd.DataFrame({"coef": full.params, "std err": full.bse, "t": full.tvalues, "p-value": full.pvalues})
savetab(full_tab, "p3_full", floatfmt=".4f")
RESULTS["p3_full_r2"] = full.rsquared; RESULTS["p3_full_adjr2"] = full.rsquared_adj

# %% [markdown]
# **Approach 1 — all-subsets search with adjusted R², AIC and BIC.**
# With five predictors there are only $2^5 - 1 = 31$ non-empty models (plus the
# intercept-only model), so we can fit every one of them and rank them on each
# criterion. For a linear model with Gaussian errors and $k$ estimated mean
# parameters (intercept included), statsmodels reports
# $\mathrm{AIC} = -2\ln L + 2k$ and $\mathrm{BIC} = -2\ln L + k\ln n$.

# %%
def fit_formula(vars_):
    rhs = " + ".join(vars_) if vars_ else "1"
    return smf.ols(f"y ~ {rhs}", data=ms).fit()

rows = []
for k in range(0, 6):
    for comb in itertools.combinations(PRED, k):
        f = fit_formula(list(comb))
        rows.append({"model": " + ".join(comb) if comb else "(intercept only)", "k": k,
                     "R2": f.rsquared, "adj R2": f.rsquared_adj, "AIC": f.aic, "BIC": f.bic})
allsub = pd.DataFrame(rows)
best = {"adj R2": allsub.loc[allsub["adj R2"].idxmax(), "model"],
        "AIC": allsub.loc[allsub["AIC"].idxmin(), "model"],
        "BIC": allsub.loc[allsub["BIC"].idxmin(), "model"]}
print("Best model by criterion:", best)
RESULTS["p3_best_allsub"] = best

# best model of each size, for the table in the report
best_by_k = allsub.loc[allsub.groupby("k")["R2"].idxmax()].set_index("k")
savetab(best_by_k, "p3_best_by_size", floatfmt=".4f")
top = pd.concat({crit: allsub.sort_values(crit, ascending=(crit != "adj R2")).head(5)
                 .reset_index(drop=True)[["model", crit]] for crit in ["adj R2", "AIC", "BIC"]}, axis=1)
top.columns = [f"{a}: model" if b == "model" else f"{a}: value" for a, b in top.columns]
top.index = [f"#{i+1}" for i in range(len(top))]
savetab(top, "p3_top5", floatfmt=".4f")
savetab(allsub.sort_values("BIC").reset_index(drop=True), "p3_allsubsets", floatfmt=".4f", index=False)
display(best_by_k); display(top)

# %%
fig, axes = plt.subplots(1, 3, figsize=(12, 3.3))
for ax, crit in zip(axes, ["adj R2", "AIC", "BIC"]):
    ax.scatter(allsub.k, allsub[crit], s=14, color="0.6")
    ax.plot(best_by_k.index, best_by_k[crit], "o-", color="#2a6f97", label="best model of each size")
    ax.set_xlabel("number of predictors"); ax.set_title(crit)
axes[0].legend(fontsize=8)
savefig("p3_criteria_by_size")

# %% [markdown]
# **Approach 2 — forward stepwise selection with AIC.**
# Start from the intercept-only model. At each step add the predictor that gives the
# largest fall in AIC; stop when no addition lowers AIC.

# %%
def stepwise_forward(crit="aic"):
    chosen, remaining, path = [], PRED.copy(), []
    current = getattr(fit_formula(chosen), crit)
    path.append({"step": 0, "action": "start (intercept only)", "model": "(intercept only)", crit.upper(): current})
    step = 0
    while remaining:
        scores = {v: getattr(fit_formula(chosen + [v]), crit) for v in remaining}
        v_best = min(scores, key=scores.get)
        if scores[v_best] >= current:
            path.append({"step": step + 1, "action": f"stop: best addition ({v_best}) would give {scores[v_best]:.3f}",
                         "model": " + ".join(chosen), crit.upper(): current})
            break
        step += 1
        chosen.append(v_best); remaining.remove(v_best); current = scores[v_best]
        path.append({"step": step, "action": f"add {v_best}", "model": " + ".join(chosen), crit.upper(): current})
    return chosen, pd.DataFrame(path)

fwd_vars, fwd_path = stepwise_forward("aic")
savetab(fwd_path, "p3_forward_aic", floatfmt=".3f", index=False)
RESULTS["p3_forward_aic"] = fwd_vars
fwd_path

# %% [markdown]
# **Approach 3 — backward elimination.**
# (i) With BIC: start from the full model and drop the predictor whose removal lowers
# BIC the most; stop when no removal lowers BIC.
# (ii) With t-tests: drop the least significant predictor while its p-value exceeds 0.05.

# %%
def stepwise_backward_crit(crit="bic"):
    chosen = PRED.copy()
    current = getattr(fit_formula(chosen), crit)
    path = [{"step": 0, "action": "start (full model)", "model": " + ".join(chosen), crit.upper(): current}]
    step = 0
    while chosen:
        scores = {v: getattr(fit_formula([c for c in chosen if c != v]), crit) for v in chosen}
        v_drop = min(scores, key=scores.get)
        if scores[v_drop] >= current:
            path.append({"step": step + 1, "action": f"stop: best removal ({v_drop}) would give {scores[v_drop]:.3f}",
                         "model": " + ".join(chosen), crit.upper(): current})
            break
        step += 1
        chosen.remove(v_drop); current = scores[v_drop]
        path.append({"step": step, "action": f"drop {v_drop}", "model": " + ".join(chosen) or "(intercept only)", crit.upper(): current})
    return chosen, pd.DataFrame(path)

bwd_vars, bwd_path = stepwise_backward_crit("bic")
savetab(bwd_path, "p3_backward_bic", floatfmt=".3f", index=False)
RESULTS["p3_backward_bic"] = bwd_vars

def backward_pvalue(alpha_=0.05):
    chosen, path = PRED.copy(), []
    while chosen:
        f = fit_formula(chosen)
        p = f.pvalues.drop("Intercept")
        worst = p.idxmax()
        path.append({"model": " + ".join(chosen), "least significant": worst, "p-value": p[worst],
                     "action": f"drop {worst}" if p[worst] > alpha_ else "stop (all p < 0.05)"})
        if p[worst] <= alpha_:
            break
        chosen.remove(worst)
    return chosen, pd.DataFrame(path)

bwp_vars, bwp_path = backward_pvalue()
savetab(bwp_path, "p3_backward_p", floatfmt=".4f", index=False)
RESULTS["p3_backward_p"] = bwp_vars
display(bwd_path); display(bwp_path)

# %% [markdown]
# **Out-of-sample check.** 10-fold cross-validated mean squared error for the
# candidate models picked above and for the full model (fixed fold split, seed 3).

# %%
def cv_mse(vars_, k=10, seed=3):
    idx = np.random.default_rng(seed).permutation(len(ms))
    folds = np.array_split(idx, k)
    err = []
    for f_ in folds:
        tr = ms.drop(ms.index[f_]); te = ms.iloc[f_]
        rhs = " + ".join(vars_) if vars_ else "1"
        m = smf.ols(f"y ~ {rhs}", data=tr).fit()
        err.append(((te["y"] - m.predict(te)) ** 2).mean())
    return float(np.mean(err))

cands = {"adj R2 best": best["adj R2"], "AIC best": best["AIC"], "BIC best": best["BIC"],
         "forward AIC": " + ".join(fwd_vars), "backward BIC": " + ".join(bwd_vars),
         "backward p-value": " + ".join(bwp_vars), "full model": " + ".join(PRED)}
cv = pd.DataFrame([{"selected by": k, "model": v,
                    "k": len(v.split(" + ")) if v and v != "(intercept only)" else 0,
                    "10-fold CV MSE": cv_mse(v.split(" + ") if v and v != "(intercept only)" else [])}
                   for k, v in cands.items()])
savetab(cv, "p3_cv", floatfmt=".4f", index=False)
cv

# %% [markdown]
# **Final model and diagnostics.** The final model is the one chosen by BIC (see the
# report for the reasoning). We check the residuals for non-normality,
# heteroskedasticity and non-linearity.

# %%
final_vars = best["BIC"].split(" + ") if best["BIC"] != "(intercept only)" else []
final = fit_formula(final_vars)
print(final.summary())
final_tab = pd.DataFrame({"coef": final.params, "std err": final.bse, "t": final.tvalues,
                          "p-value": final.pvalues, "95% low": final.conf_int()[0], "95% high": final.conf_int()[1]})
savetab(final_tab, "p3_final", floatfmt=".4f")
jb = jarque_bera(final.resid)
bp = het_breuschpagan(final.resid, final.model.exog)
reset = sm.stats.diagnostic.linear_reset(final, power=2, use_f=True)
diag = pd.DataFrame({"statistic": [jb[0], bp[0], float(reset.fvalue)],
                     "p-value": [jb[1], bp[1], float(reset.pvalue)]},
                    index=["Jarque-Bera (normality)", "Breusch-Pagan (heteroskedasticity)", "RESET (functional form)"])
savetab(diag, "p3_diag", floatfmt=".4f")
RESULTS.update({"p3_final": final_vars, "p3_final_r2": final.rsquared, "p3_final_adjr2": final.rsquared_adj,
                "p3_final_aic": final.aic, "p3_final_bic": final.bic})
diag

# %%
fig, axes = plt.subplots(1, 3, figsize=(12, 3.4))
axes[0].scatter(final.fittedvalues, final.resid, s=10, color="#2a6f97")
axes[0].axhline(0, color="k", lw=0.8); axes[0].set_xlabel("fitted values"); axes[0].set_ylabel("residuals")
axes[0].set_title("Residuals vs fitted")
sm.qqplot(final.resid, line="s", ax=axes[1], markersize=3); axes[1].set_title("Normal Q-Q plot")
axes[2].hist(final.resid, bins=25, color="#2a6f97", alpha=0.8); axes[2].set_title("Residual histogram")
savefig("p3_final_diag")

# %% [markdown]
# ### 3b — AIC versus BIC: simulation that supports the proof in the report
#
# True model $y_i = 1 + 2x_i + \varepsilon_i$. The candidate "big" model also includes
# an irrelevant regressor $z_i$ (independent of x and ε). For each n we count how often
# each criterion prefers the big (wrong) model. Theory: for AIC this rate tends to
# $P(\chi^2_1 > 2) \approx 0.157$; for BIC it tends to 0.

# %%
rng = np.random.default_rng(99)
R = 2000
rows = []
for n in [25, 50, 100, 500, 1_000, 5_000, 20_000]:
    pick_aic = pick_bic = 0
    for _ in range(R):
        x_ = rng.normal(size=n); z_ = rng.normal(size=n)
        y_ = 1 + 2 * x_ + rng.normal(size=n)
        X1 = np.column_stack([np.ones(n), x_]); X2 = np.column_stack([X1, z_])
        rss1 = np.sum((y_ - X1 @ np.linalg.lstsq(X1, y_, rcond=None)[0]) ** 2)
        rss2 = np.sum((y_ - X2 @ np.linalg.lstsq(X2, y_, rcond=None)[0]) ** 2)
        lr = n * np.log(rss1 / rss2)
        pick_aic += lr > 2; pick_bic += lr > np.log(n)
    rows.append({"n": n, "P(AIC picks wrong model)": pick_aic / R,
                 "P(BIC picks wrong model)": pick_bic / R,
                 "asymptotic AIC rate": stats.chi2.sf(2, 1),
                 "P(chi2_1 > ln n)": stats.chi2.sf(np.log(n), 1)})
p3b = pd.DataFrame(rows)
savetab(p3b, "p3b_sim", floatfmt=".4f", index=False)
RESULTS["p3b_chi2_sf2"] = float(stats.chi2.sf(2, 1))
p3b

# %%
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.plot(p3b.n, p3b["P(AIC picks wrong model)"], "o-", color="#c8553d", label="AIC (simulated)")
ax.plot(p3b.n, p3b["P(BIC picks wrong model)"], "s-", color="#2a6f97", label="BIC (simulated)")
ax.axhline(stats.chi2.sf(2, 1), color="#c8553d", ls=":", label=r"$P(\chi^2_1>2)=0.157$")
ax.plot(p3b.n, p3b["P(chi2_1 > ln n)"], "--", color="#2a6f97", lw=1, label=r"$P(\chi^2_1>\ln n)$")
ax.set_xscale("log"); ax.set_xlabel("n (log scale)"); ax.set_ylabel("share of samples")
ax.set_title("How often each criterion adds an irrelevant regressor")
ax.legend(fontsize=8)
savefig("p3b_sim")

# %% [markdown]
# ---
# ## Problem 4 — Interpreting the wage regression
# All numbers below come from the coefficient table given in the assignment.

# %%
coef = pd.DataFrame({"coef": [0.85, 0.08, -0.15, 0.19, -0.002, 0.22],
                     "se": [0.12, 0.01, 0.10, 0.06, 0.0003, 0.04]},
                    index=["intercept", "educ", "gender", "age", "age^2", "degree"])
n_obs, k_par = 2000, 6
df_res = n_obs - k_par
coef["t"] = coef.coef / coef.se
coef["p (two-sided)"] = 2 * stats.t.sf(coef.t.abs(), df_res)
tcrit = stats.t.ppf(0.975, df_res)
coef["95% low"] = coef.coef - tcrit * coef.se
coef["95% high"] = coef.coef + tcrit * coef.se
coef["exact % effect 100(e^b - 1)"] = 100 * (np.exp(coef.coef) - 1)
coef.loc[["intercept", "age", "age^2"], "exact % effect 100(e^b - 1)"] = np.nan
savetab(coef, "p4_table", floatfmt=".4f")
coef

# %%
b = coef.coef
peak = -b["age"] / (2 * b["age^2"])
p_gender_one_sided = stats.t.cdf(coef.loc["gender", "t"], df_res)
kennedy = 100 * (np.exp(b["degree"] - 0.5 * coef.loc["degree", "se"] ** 2) - 1)
ci_deg = 100 * (np.exp(coef.loc["degree", ["95% low", "95% high"]].values) - 1)
ci_gen = 100 * (np.exp(coef.loc["gender", ["95% low", "95% high"]].values) - 1)
RESULTS.update({"p4_peak": float(peak), "p4_gender_p2": float(coef.loc["gender", "p (two-sided)"]),
                "p4_gender_p1": float(p_gender_one_sided), "p4_degree_pct": float(100 * (np.exp(b["degree"]) - 1)),
                "p4_degree_kennedy": float(kennedy), "p4_degree_ci": [float(v) for v in ci_deg],
                "p4_gender_ci": [float(v) for v in ci_gen], "p4_gender_pct": float(100 * (np.exp(b["gender"]) - 1)),
                "p4_educ_pct": float(100 * (np.exp(b["educ"]) - 1)), "p4_tcrit": float(tcrit)})
print(f"Peak age: {peak:.2f} years")
print(f"Gender: two-sided p = {coef.loc['gender', 'p (two-sided)']:.4f}, one-sided p = {p_gender_one_sided:.4f}")
print(f"Degree premium: {100*(np.exp(b['degree'])-1):.2f}% (Kennedy-corrected {kennedy:.2f}%), 95% CI {ci_deg.round(2)}")

# %%
ages = np.linspace(20, 70, 200)
profile = b["age"] * ages + b["age^2"] * ages ** 2
profile -= profile.max()
fig, ax = plt.subplots(figsize=(7, 3.4))
ax.plot(ages, 100 * (np.exp(profile) - 1), color="#2a6f97")
ax.axvline(peak, color="#c8553d", ls="--", lw=1)
ax.annotate(f"peak at {peak:.1f} years", (peak, 0), xytext=(peak + 3, -12), color="#c8553d")
ax.set_xlabel("age (years)"); ax.set_ylabel("% difference from peak wage")
ax.set_title("Estimated age–wage profile (other variables held fixed)")
savefig("p4_age_profile")

# %% [markdown]
# ---
# ## Problem 5 — Non-stationary series and cointegration
#
# ### 5a/5b — Illustration with our own simulation
# We simulate the model in the question (T = 500, all shocks N(0,1)) to see that
# X, Y and Z wander, while the combinations X − 2Y and X + Z do not.

# %%
rng = np.random.default_rng(5)
T = 500
eps = rng.normal(size=T); eps[0] = 0.0      # w(0) = 0
wt = np.cumsum(eps)
Xs = 1.0 * wt + rng.normal(size=T); Ys = 0.5 * wt + rng.normal(size=T); Zs = -1.0 * wt + rng.normal(size=T)
fig, axes = plt.subplots(1, 2, figsize=(11, 3.4))
axes[0].plot(Xs, label="X"); axes[0].plot(Ys, label="Y"); axes[0].plot(Zs, label="Z")
axes[0].set_title("Simulated X, Y, Z (share one random walk)"); axes[0].legend(fontsize=8)
axes[1].plot(Xs - 2 * Ys, label="X − 2Y", alpha=0.85); axes[1].plot(Xs + Zs, label="X + Z", alpha=0.85)
axes[1].set_title("Cointegrating combinations"); axes[1].legend(fontsize=8)
for ax in axes: ax.set_xlabel("t")
savefig("p5ab_sim")
print("ADF p-values -> X:", round(adfuller(Xs)[1], 4), " X-2Y:", round(adfuller(Xs - 2 * Ys)[1], 4),
      " X+Z:", round(adfuller(Xs + Zs)[1], 4))

# %% [markdown]
# ### 5c — Data set `FE-GWP1_dataset_Prob5.csv`
# **Step 1: load and inspect.**

# %%
p5_path = os.path.join(DATA_DIR, "FE-GWP1_dataset_Prob5.csv")
raw5 = pd.read_csv(p5_path)
print(raw5.head()); print(raw5.shape)
cols = {c: c.strip().upper() for c in raw5.columns}
d5 = raw5.rename(columns=cols)
date_col = [c for c in d5.columns if c not in ["X", "Y", "Z"]]
if date_col:
    try:
        d5.index = pd.to_datetime(d5[date_col[0]]);
    except Exception:
        d5.index = d5[date_col[0]]
d5 = d5[["X", "Y", "Z"]].astype(float).dropna()
RESULTS["p5_T"] = int(len(d5))
savetab(d5.describe().T, "p5_describe", floatfmt=".3f")
d5.describe().T

# %%
fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
for c, col in zip(["X", "Y", "Z"], ["#2a6f97", "#e09f3e", "#c8553d"]):
    axes[0].plot(d5.index, d5[c], label=c, color=col, lw=1)
    axes[1].plot(d5.index, d5[c].diff(), label=f"Δ{c}", color=col, lw=0.8, alpha=0.8)
axes[0].set_title("Levels"); axes[1].set_title("First differences")
axes[0].legend(fontsize=8); axes[1].legend(fontsize=8)
savefig("p5c_levels")

# %%
fig, axes = plt.subplots(2, 3, figsize=(12, 5.4))
for j, c in enumerate(["X", "Y", "Z"]):
    ac = acf(d5[c], nlags=30)
    axes[0, j].bar(range(31), ac, color="#2a6f97"); axes[0, j].set_title(f"ACF of {c} (levels)")
    ac2 = acf(d5[c].diff().dropna(), nlags=30)
    axes[1, j].bar(range(31), ac2, color="#c8553d"); axes[1, j].set_title(f"ACF of Δ{c}")
    for ax in axes[:, j]:
        ax.axhline(1.96 / np.sqrt(len(d5)), color="k", ls=":", lw=0.8)
        ax.axhline(-1.96 / np.sqrt(len(d5)), color="k", ls=":", lw=0.8)
savefig("p5c_acf")

# %%
fig, axes = plt.subplots(1, 3, figsize=(12, 3.4))
for ax, (a_, b_) in zip(axes, [("X", "Y"), ("X", "Z"), ("Y", "Z")]):
    ax.scatter(d5[a_], d5[b_], s=6, alpha=0.6, color="#2a6f97")
    ax.set_xlabel(a_); ax.set_ylabel(b_); ax.set_title(f"{b_} vs {a_}  (corr = {d5[a_].corr(d5[b_]):.3f})")
savefig("p5c_scatter")

# %% [markdown]
# **Step 2: unit-root tests.** ADF (null: unit root) with a constant, lag length chosen
# by AIC, on levels and first differences. KPSS (null: level stationarity) is run as a
# cross-check, because the two tests have opposite null hypotheses.

# %%
rows = []
for c in ["X", "Y", "Z"]:
    for lab, s in [("level", d5[c]), ("first difference", d5[c].diff().dropna())]:
        adf_c = adfuller(s, regression="c", autolag="AIC")
        adf_ct = adfuller(s, regression="ct", autolag="AIC")
        kp = kpss(s, regression="c", nlags="auto")
        rows.append({"series": c, "form": lab,
                     "ADF(c) stat": adf_c[0], "ADF(c) p": adf_c[1], "lags": adf_c[2],
                     "ADF(ct) stat": adf_ct[0], "ADF(ct) p": adf_ct[1],
                     "KPSS stat": kp[0], "KPSS p": kp[1]})
ur = pd.DataFrame(rows)
savetab(ur, "p5c_unitroot", floatfmt=".4f", index=False)
ur

# %% [markdown]
# **Step 3: lag order.** Choose the VAR lag length in levels with information criteria;
# the VECM then uses $k_{ar\_diff} = p - 1$ lagged differences.

# %%
sel = VAR(d5).select_order(maxlags=10, trend="c")
print(sel.summary())
ic_tab = pd.DataFrame({ic: [sel.ics[ic][i] for i in range(len(sel.ics[ic]))] for ic in ["aic", "bic", "hqic"]})
ic_tab.index.name = "p"
savetab(ic_tab, "p5c_lagselect", floatfmt=".4f")
p_bic = int(sel.selected_orders["bic"]); p_aic = int(sel.selected_orders["aic"])
p_var = max(p_bic, 1)
k_diff = max(p_var - 1, 1) if p_var > 1 else 1
RESULTS.update({"p5_p_aic": p_aic, "p5_p_bic": p_bic, "p5_kdiff": k_diff})
print("VAR lag chosen by BIC:", p_bic, " by AIC:", p_aic, " -> k_ar_diff used:", k_diff)

# %% [markdown]
# **Step 4: Johansen test.** Deterministic term: unrestricted constant (`det_order = 0`),
# which matches series with no visible trend in the levels. We read the trace test
# sequentially (r = 0, then r ≤ 1, ...) and stop at the first null not rejected; the
# maximum-eigenvalue test is read the same way.

# %%
def johansen_table(det_order, k):
    jo = coint_johansen(d5, det_order, k)
    rows = []
    for i in range(3):
        rows.append({"H0": f"r = {i}" if i == 0 else f"r ≤ {i}", "eigenvalue": jo.eig[i],
                     "trace stat": jo.lr1[i], "trace 90%": jo.cvt[i, 0], "trace 95%": jo.cvt[i, 1], "trace 99%": jo.cvt[i, 2],
                     "max-eig stat": jo.lr2[i], "max-eig 90%": jo.cvm[i, 0], "max-eig 95%": jo.cvm[i, 1], "max-eig 99%": jo.cvm[i, 2]})
    tab = pd.DataFrame(rows)
    r_tr = next((i for i in range(3) if jo.lr1[i] < jo.cvt[i, 1]), 3)
    r_me = next((i for i in range(3) if jo.lr2[i] < jo.cvm[i, 1]), 3)
    return jo, tab, r_tr, r_me

jo, jtab, r_trace, r_maxeig = johansen_table(0, k_diff)
savetab(jtab, "p5c_johansen", floatfmt=".3f", index=False)
savetab(jtab[["H0", "eigenvalue", "trace stat", "trace 90%", "trace 95%", "trace 99%"]], "p5c_johansen_trace", floatfmt=".3f", index=False)
savetab(jtab[["H0", "eigenvalue", "max-eig stat", "max-eig 90%", "max-eig 95%", "max-eig 99%"]], "p5c_johansen_maxeig", floatfmt=".3f", index=False)
RESULTS.update({"p5_r_trace": r_trace, "p5_r_maxeig": r_maxeig})
print("Rank at 5% — trace:", r_trace, " max-eig:", r_maxeig)
jtab

# %%
# Robustness: does the rank depend on the number of lagged differences?
rows = []
for k in sorted(set([1, 2, 3, 4, k_diff])):
    _, _, rt, rm = johansen_table(0, k)
    rows.append({"k_ar_diff": k, "rank (trace, 5%)": rt, "rank (max-eig, 5%)": rm})
jrob = pd.DataFrame(rows)
savetab(jrob, "p5c_johansen_robust", index=False)
jrob

# %% [markdown]
# **Step 5: VECM.** Estimated with the rank found above, the same lag length, and the
# constant restricted to the cointegration relations (`deterministic="ci"`), since the
# series show no drift. statsmodels normalises β so that its top $r \times r$ block is the
# identity.

# %%
r_use = r_trace if r_trace in (1, 2) else max(min(r_trace, 2), 1)
RESULTS["p5_r_use"] = int(r_use)
vecm = VECM(d5, k_ar_diff=k_diff, coint_rank=r_use, deterministic="ci").fit()
print(vecm.summary())

# %%
names = ["X", "Y", "Z"]
beta_tab = pd.DataFrame(vecm.beta, index=names, columns=[f"coint. vector {i+1}" for i in range(r_use)])
if vecm.det_coef_coint.size:
    beta_tab.loc["const"] = vecm.det_coef_coint.ravel()[:r_use]
alpha_tab = pd.DataFrame(vecm.alpha, index=[f"Δ{c}" for c in names], columns=[f"ECT {i+1}" for i in range(r_use)])
alpha_se = pd.DataFrame(vecm.stderr_alpha, index=alpha_tab.index, columns=alpha_tab.columns)
alpha_t = alpha_tab / alpha_se
alpha_out = pd.concat({"alpha": alpha_tab, "std err": alpha_se, "t": alpha_t}, axis=1)
alpha_out.columns = [f"{a} ({b})" for a, b in alpha_out.columns]
gamma_rows = {}
for lag in range(k_diff):
    G = vecm.gamma[:, lag * 3:(lag + 1) * 3]
    for i, eq in enumerate(names):
        gamma_rows[(f"Δ{eq}", f"lag {lag+1}")] = G[i]
gamma_tab = pd.DataFrame(gamma_rows, index=[f"coef. on Δ{c}" for c in names]).T
gamma_tab.index = [f"{eq} eq., {l}" for eq, l in gamma_tab.index]
savetab(beta_tab, "p5c_beta", floatfmt=".4f")
savetab(alpha_out, "p5c_alpha", floatfmt=".4f")
savetab(gamma_tab, "p5c_gamma", floatfmt=".4f")
display(beta_tab); display(alpha_out); display(gamma_tab)

# %%
# Theoretical cointegrating vectors in the same normalisation, for comparison
if r_use == 2:
    theory = pd.DataFrame([[1, 0], [0, 1], [1, 0.5]], index=names, columns=beta_tab.columns[:2])
elif r_use == 1:
    theory = None
print(theory)
# Estimated error-correction terms
ect = d5.values @ vecm.beta
fig, ax = plt.subplots(figsize=(10, 3.2))
for i in range(r_use):
    ax.plot(d5.index, ect[:, i] - ect[:, i].mean(), lw=0.9, label=f"β{i+1}'y(t) (demeaned)")
ax.set_title("Estimated cointegrating relations"); ax.legend(fontsize=8)
savefig("p5c_ect")

# %%
res = pd.DataFrame(vecm.resid, columns=names)
lb = pd.DataFrame({c: acorr_ljungbox(res[c], lags=[10], return_df=True).iloc[0] for c in names}).T
lb.columns = ["Ljung-Box Q(10)", "p-value"]
wt = vecm.test_whiteness(nlags=10)
lb.loc["Portmanteau (system, 10 lags)"] = [wt.test_statistic, wt.pvalue]
savetab(lb, "p5c_resid", floatfmt=".4f")
lb

# %% [markdown]
# ---
# ## Problem 6 — ARMA representations
# ### 6a — ψ-weights of AR(1) with φ = 0.5
# Numerical check of the hand derivation: ψ_j = 0.5^j.

# %%
psi = arma2ma(np.array([1, -0.5]), np.array([1]), lags=6)
p6a = pd.DataFrame({"j": range(6), "psi_j (statsmodels)": psi, "0.5^j": 0.5 ** np.arange(6)})
savetab(p6a, "p6a_psi", floatfmt=".5f", index=False)
p6a

# %% [markdown]
# ### 6b — ACF of AR(2) with φ1 = 0.6, φ2 = 0.2
# Theoretical ACF from statsmodels and the sample ACF of a long simulated path
# (T = 200,000, seed 6) against the Yule–Walker results ρ1 = 0.75, ρ2 = 0.65.

# %%
ar2 = ArmaProcess(ar=[1, -0.6, -0.2], ma=[1])
print("Stationary:", ar2.isstationary, " roots:", np.round(ar2.arroots, 4))
theo = arma_acf([1, -0.6, -0.2], [1], lags=6)
sim = ar2.generate_sample(nsample=200_000, distrvs=np.random.default_rng(6).standard_normal, burnin=1000)
samp = acf(sim, nlags=5)
p6b = pd.DataFrame({"lag": range(6), "Yule-Walker recursion": [1, 0.75, 0.65, 0.6 * 0.65 + 0.2 * 0.75,
                                                               0.6 * (0.6 * 0.65 + 0.2 * 0.75) + 0.2 * 0.65, np.nan],
                    "statsmodels arma_acf": theo, "sample ACF (simulated)": samp})
p6b.loc[5, "Yule-Walker recursion"] = 0.6 * p6b.loc[4, "Yule-Walker recursion"] + 0.2 * p6b.loc[3, "Yule-Walker recursion"]
savetab(p6b, "p6b_acf", floatfmt=".4f", index=False)
RESULTS["p6_roots"] = [float(r) for r in np.real(ar2.arroots)]
p6b

# %%
def _clean(o):
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, dict): return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [_clean(v) for v in o]
    return o
with open(os.path.join(OUT, "results.json"), "w") as f:
    json.dump(_clean(RESULTS), f, indent=2)
print(json.dumps(_clean(RESULTS), indent=2))
