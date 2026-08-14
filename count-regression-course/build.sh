#!/bin/bash
# Build the book: knit main.Rnw -> main.tex, then run pdflatex twice for the TOC.
set -e
cd "$(dirname "$0")"
Rscript -e 'library(knitr); knit("main.Rnw", quiet = FALSE)' 2>&1 | tail -40
pdflatex -interaction=nonstopmode -halt-on-error main.tex > /tmp/tex1.log 2>&1 || {
  echo "=== pdflatex FAILED ==="; grep -n -A4 "^!" /tmp/tex1.log | head -60; exit 1; }
pdflatex -interaction=nonstopmode -halt-on-error main.tex > /tmp/tex2.log 2>&1 || {
  echo "=== pdflatex pass 2 FAILED ==="; grep -n -A4 "^!" /tmp/tex2.log | head -60; exit 1; }
echo "=== OK ==="
pdfinfo main.pdf 2>/dev/null | grep -E "Pages|File size" || \
  Rscript -e 'cat("pages:", length(pdftools::pdf_info("main.pdf")$pages), "\n")' 2>/dev/null || true
ls -lh main.pdf
