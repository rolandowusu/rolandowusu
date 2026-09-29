# Financial Econometrics — Group Work Project 1

Solutions to GWP1 (Problems 1–6): a written report (answers, derivations, tables, figures, no code) and a Jupyter notebook that produces every number and figure in it.

## Layout

| Path | What it is |
|:--|:--|
| `src/GWP1_notebook.py` | Notebook source (jupytext "percent" format). `build.sh` turns it into `GWP1_notebook.ipynb`. |
| `report/report_template.md` | Report text. `{{...}}` placeholders are filled from `outputs/`. |
| `src/build_report.py` | Fills the template and writes `dist/GWP1_Report.docx`, `.html`, `.pdf`. |
| `src/render_pdf.js` | Prints HTML to PDF with KaTeX math and headless Chromium. |
| `data/` | Put the two course CSV files here (not included). |
| `outputs/` | Figures, tables and `results.json` written by the notebook. |
| `dist/` | Finished deliverables. |

## Status

All six problems are complete and the notebook runs end to end on the course data in `data/`.

Two notes on the data work:

- `FE-GWP1_dataset_Prob5.csv` wraps every row in one pair of quotes and starts with a byte-order mark; the notebook strips these before parsing.
- For the Johansen test in 5c the notebook implements the restricted-constant case itself (statsmodels does not offer it), checks the code against statsmodels on the cases it does offer, and simulates the critical values.

## Build

```bash
pip install numpy pandas scipy statsmodels matplotlib tabulate jupyter jupytext pypandoc_binary
npm install --prefix /some/dir katex playwright-core
NODE_MODULES=/some/dir/node_modules CHROMIUM=/path/to/chrome ./build.sh
```

Output in `dist/`: `GWP1_Report.pdf` and `GWP1_Report.docx` (the Word file has native equations, so the text can be pasted into the official Report Template), and `GWP1_code.zip`, which holds the executed notebook, its HTML and PDF copies, and the data.
