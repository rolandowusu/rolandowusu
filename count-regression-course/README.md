# Logistic, Poisson and Count Regression with Mixed Models

A 141-page plain-English, code-first guide in R.

**Read the book:** [`Count-Regression-and-Mixed-Models-in-R.pdf`](Count-Regression-and-Mixed-Models-in-R.pdf)

Every code block, output and figure in the PDF was produced by actually executing
the code — the book is written in `knitr` and compiled from source, so nothing in
it is transcribed by hand.

## Contents

| Ch | Topic |
|----|-------|
| 1 | The big picture: choosing a model for your outcome |
| 2 | The anatomy of a GLM: family, linear predictor, link |
| 3–4 | Logistic regression: odds ratios, ROC/AUC, calibration, separation, grouped binomial |
| 5–6 | Poisson regression: rate ratios, offsets and exposure |
| 7 | Overdispersion: causes, consequences, five ways to detect it |
| 8 | Quasi-Poisson and robust (sandwich) standard errors |
| 9 | Negative binomial regression (NB1 and NB2) |
| 10 | Zero-inflated and hurdle models |
| 11 | Truncation, underdispersion, beta-binomial, ordinal, GAMs |
| 12 | Model checking: randomised quantile residuals, rootograms |
| 13 | LRT, Wald, score, AIC/BIC, Vuong, cross-validation |
| 14–15 | Mixed models and GLMMs, including OLRE and zero-inflated GLMMs |
| 16 | Conditional vs marginal effects, and GEE |
| 17 | Convergence problems and how to fix them |
| 18 | A complete worked analysis, end to end |
| 19 | Cheat sheets, glossary and further reading |

## Building it yourself

Requires R with `MASS`, `lme4`, `glmmTMB`, `pscl`, `AER`, `lmtest`, `sandwich`,
`car`, `emmeans`, `geepack`, `mgcv`, `knitr`, plus a LaTeX installation.

```sh
./build.sh
```

This knits `main.Rnw` (which pulls in `parts/ch*.Rnw`) to `main.tex` and runs
`pdflatex` twice.

## Datasets

All examples use data that ships with R or with one of the packages above
(`birthwt`, `cbpp`, `quine`, `warpbreaks`, `bioChemists`, `RecreationDemand`,
`epil`, `grouseticks`, `sleepstudy`, `housing`), plus a few simulated datasets
where knowing the true answer makes the point clearer.
