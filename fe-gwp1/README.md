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

Problems 1, 2, 3b, 4, 5a, 5b and 6 are complete. **3a and 5c need the course data files**, which were not available when this was built:

- `data/FE-GWP1_model_selection_1.csv`
- `data/FE-GWP1_dataset_Prob5.csv`

The code for both is written and was tested end to end on stand-in data (not committed). Until the real files are added, those two sections of the report show a "results pending" note. The `[[P3_...]]` / `[[P5_...]]` markers in the template are where the written interpretation of those results goes once the real output exists; the build refuses to run while any are left.

## Build

```bash
pip install numpy pandas scipy statsmodels matplotlib tabulate jupyter jupytext pypandoc_binary
npm install --prefix /some/dir katex playwright-core
NODE_MODULES=/some/dir/node_modules CHROMIUM=/path/to/chrome ./build.sh
```

Output in `dist/`: `GWP1_Report.pdf` and `GWP1_Report.docx` (the Word file has native equations, so the text can be pasted into the official Report Template), and `GWP1_code.zip`, which holds the executed notebook, its HTML and PDF copies, and the data.
