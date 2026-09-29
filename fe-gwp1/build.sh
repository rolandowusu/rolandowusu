#!/usr/bin/env bash
# Build every deliverable from source.
#   1. src/GWP1_notebook.py  -> GWP1_notebook.ipynb (executed)
#   2. notebook              -> HTML and PDF copies with outputs
#   3. outputs/ + report/report_template.md -> dist/GWP1_Report.{pdf,docx}
#   4. zip of the notebook, its HTML/PDF copies and the data
# Needs: python (numpy pandas scipy statsmodels matplotlib tabulate jupyter jupytext pypandoc_binary),
#        node with `katex` and `playwright-core` in $NODE_MODULES, and a Chromium binary in $CHROMIUM.
set -euo pipefail
cd "$(dirname "$0")"
NODE_MODULES=${NODE_MODULES:?set NODE_MODULES to a node_modules dir containing katex and playwright-core}
CHROMIUM=${CHROMIUM:-/opt/pw-browsers/chromium-1194/chrome-linux/chrome}

for f in data/FE-GWP1_model_selection_1.csv data/FE-GWP1_dataset_Prob5.csv; do
  [ -f "$f" ] || { echo "Missing $f — copy the course data files into data/ first." >&2; exit 1; }
done

mkdir -p dist
jupytext --to ipynb src/GWP1_notebook.py -o GWP1_notebook.ipynb -q
jupyter nbconvert --to notebook --execute --inplace GWP1_notebook.ipynb --ExecutePreprocessor.timeout=1800
jupyter nbconvert --to html GWP1_notebook.ipynb --output-dir dist --output GWP1_notebook
node src/render_pdf.js dist/GWP1_notebook.html dist/GWP1_notebook.pdf "$NODE_MODULES" "$CHROMIUM" notebook
python src/build_report.py --node-modules "$NODE_MODULES" --chromium "$CHROMIUM"

rm -rf dist/GWP1_code && mkdir -p dist/GWP1_code/data
cp GWP1_notebook.ipynb dist/GWP1_code/
cp dist/GWP1_notebook.html dist/GWP1_notebook.pdf dist/GWP1_code/
cp data/*.csv dist/GWP1_code/data/
(cd dist && rm -f GWP1_code.zip && zip -qr GWP1_code.zip GWP1_code)
echo "Deliverables in dist/: GWP1_Report.pdf, GWP1_Report.docx, GWP1_code.zip"
