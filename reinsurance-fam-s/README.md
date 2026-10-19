# Reinsurance for Exam FAM-S

A 24-page study guide that starts from zero and builds up to exam-level questions.

**Read the guide:** [`Reinsurance-for-FAM-S.pdf`](Reinsurance-for-FAM-S.pdf)

Every number in the worked solutions is computed by `build.py`, the script that
generates the PDF, so none of the answers were worked out by hand.

## Contents

| Part | Topic |
|------|-------|
| 1 | What reinsurance is in plain words: vocabulary, why insurers buy it, proportional vs non-proportional, treaty vs facultative |
| 2 | Proportional: quota share, ceding commission, surplus share (lines) |
| 3 | Non-proportional: per-risk XL, catastrophe XL and layers, aggregate stop-loss, order of treaties, quota share vs XL |
| 4 | The Loss Models toolkit: limited expected values, per loss vs per payment, frequency thinning, inflation, discrete stop-loss |
| 5 | 16 exam-style questions, solved step by step |
| 6 | 12 practice questions with answers |
| 7 | One-page cheat sheet |

## Rebuild

```
python3 build.py   # needs reportlab and the DejaVu / Liberation fonts
```
