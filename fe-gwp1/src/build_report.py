"""Fill the report template with notebook outputs and render DOCX / HTML / PDF.

Usage: python src/build_report.py [--out-dir outputs] [--dist dist]

Placeholders in report/report_template.md
  {{TAB|name}}                 -> outputs/tables/name.md
  {{FIG|name|caption}}         -> figure outputs/figures/name.png with a caption
  {{CSV|name|row|col|fmt}}     -> one cell of outputs/tables/name.csv (row = index label or #pos)
  {{VAL|key|fmt}}              -> value from outputs/results.json
  {{PAGEBREAK}}                -> page break
  {{IFDATA|tag}} ... {{ENDIF}} -> kept only if the data-driven outputs for `tag` exist,
                                  otherwise replaced by a "results pending" notice
"""
import argparse, json, os, re, subprocess, sys, shutil
import pandas as pd
import pypandoc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--out-dir", default=os.path.join(ROOT, "outputs"))
ap.add_argument("--dist", default=os.path.join(ROOT, "dist"))
ap.add_argument("--node-modules", default=os.environ.get("NODE_MODULES", ""))
ap.add_argument("--chromium", default="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
args = ap.parse_args()

OUT, DIST = args.out_dir, args.dist
os.makedirs(DIST, exist_ok=True)
tpl = open(os.path.join(ROOT, "report", "report_template.md"), encoding="utf-8").read()
results = json.load(open(os.path.join(OUT, "results.json")))

DATA_TAGS = {"3a": "p3_final", "5c": "p5c_johansen"}
def has_data(tag):
    return os.path.exists(os.path.join(OUT, "tables", DATA_TAGS[tag] + ".csv"))

PENDING = ("> **Results pending.** The data file for this question was not available when this "
           "version of the report was built. The method is described above; the tables, figures "
           "and conclusions are generated once the notebook is run on the course data.\n")

def ifdata(m):
    return m.group(2) if has_data(m.group(1)) else PENDING
tpl = re.sub(r"\{\{IFDATA\|(\w+)\}\}(.*?)\{\{ENDIF\}\}", ifdata, tpl, flags=re.S)

def tab(m):
    path = os.path.join(OUT, "tables", m.group(1) + ".md")
    return open(path, encoding="utf-8").read().replace("nan", "–") + "\n"

def fig(m):
    return f"![{m.group(2)}]({os.path.join(OUT, 'figures', m.group(1) + '.png')})\n"

def csv(m):
    name, row, col, fmt = m.group(1), m.group(2), m.group(3), m.group(4)
    df = pd.read_csv(os.path.join(OUT, "tables", name + ".csv"), index_col=0)
    if row.startswith("#"):
        df = pd.read_csv(os.path.join(OUT, "tables", name + ".csv"))
        v = df.iloc[int(row[1:])][col]
    else:
        v = df.loc[row, col]
    return format(float(v), fmt)

def val(m):
    keys, fmt = m.group(1).split("."), m.group(2)
    v = results
    for k in keys:
        v = v[int(k)] if isinstance(v, list) else v[k]
    if isinstance(v, list):
        return " + ".join(v) if v and isinstance(v[0], str) else str(v)
    return format(v, fmt) if fmt else str(v)

tpl = re.sub(r"\{\{TAB\|([\w]+)\}\}", tab, tpl)
tpl = re.sub(r"\{\{FIG\|([\w]+)\|([^}]*)\}\}", fig, tpl)
tpl = re.sub(r"\{\{CSV\|([\w]+)\|([^|]+)\|([^|]+)\|([^}]*)\}\}", csv, tpl)
tpl = re.sub(r"\{\{VAL\|([\w.]+)\|([^}]*)\}\}", val, tpl)
left = re.findall(r"\{\{(?!PAGEBREAK)[^}]*\}\}", tpl)
left += re.findall(r"\[\[[A-Z0-9_]+\]\]", tpl)
if left:
    sys.exit(f"Unfilled placeholders: {left}")

# ---------- DOCX (editable, equations become native Word equations) ----------
md_docx = tpl.replace("{{PAGEBREAK}}", '```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```')
ref = os.path.join(ROOT, "report", "reference.docx")
extra = ["--resource-path", ROOT] + (["--reference-doc", ref] if os.path.exists(ref) else [])
pypandoc.convert_text(md_docx, "docx", format="markdown", outputfile=os.path.join(DIST, "GWP1_Report.docx"),
                      extra_args=extra)

# ---------- HTML -> PDF via Chromium with KaTeX ----------
md_html = tpl.replace("{{PAGEBREAK}}", '<div class="pagebreak"></div>')
body = pypandoc.convert_text(md_html, "html5", format="markdown",
                             extra_args=["--mathjax", "--resource-path", ROOT, "--embed-resources", "--standalone",
                                         "--metadata", "title=GWP1 Report",
                                         "--template", os.path.join(ROOT, "report", "template.html")])
html_path = os.path.join(DIST, "GWP1_Report.html")
open(html_path, "w", encoding="utf-8").write(body)
nm = args.node_modules
if nm:
    render = os.path.join(ROOT, "src", "render_pdf.js")
    subprocess.run(["node", render, html_path, os.path.join(DIST, "GWP1_Report.pdf"), nm, args.chromium], check=True)
print("Built:", os.listdir(DIST))
