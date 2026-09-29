// Render an HTML file (math in \( \) and \[ \]) to PDF with KaTeX + headless Chromium.
// usage: node render_pdf.js in.html out.pdf <node_modules dir> <chromium executable>
const fs = require('fs'), path = require('path');
const [,, inHtml, outPdf, nm, chrome, mode] = process.argv;
const notebook = mode === 'notebook';
const { chromium } = require(path.join(nm, 'playwright-core'));
const k = path.join(nm, 'katex', 'dist');
(async () => {
  let html = fs.readFileSync(inHtml, 'utf8');
  const inject = `
<link rel="stylesheet" href="file://${k}/katex.min.css">
<script src="file://${k}/katex.min.js"></script>
<script src="file://${k}/contrib/auto-render.min.js"></script>` + (notebook ? `
<style>
  pre, .highlight pre, .jp-RenderedText pre, .CodeMirror pre { white-space: pre-wrap !important; word-break: break-word !important; }
  body, .jp-Notebook { max-width: 100% !important; }
  .jp-Cell, .jp-OutputArea-output img { page-break-inside: avoid; }
  .jp-OutputArea-output img { max-width: 100% !important; height: auto !important; }
</style>` : '');
  html = html.replace('</head>', inject + '\n</head>');
  const tmp = inHtml.replace(/\.html$/, '.print.html');
  fs.writeFileSync(tmp, html);
  const browser = await chromium.launch({ executablePath: chrome, args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(tmp), { waitUntil: 'load' });
  await page.evaluate(() => renderMathInElement(document.body, {
    delimiters: [{left: '$$', right: '$$', display: true}, {left: '\\[', right: '\\]', display: true},
                 {left: '\\(', right: '\\)', display: false}, {left: '$', right: '$', display: false}],
    ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code', 'option'],
    ignoredClasses: ['jp-OutputArea', 'jp-InputArea-editor', 'output_area'],
    throwOnError: false }));
  const errs = await page.evaluate(() => Array.from(document.querySelectorAll('.katex-error')).map(e => e.title || e.textContent));
  if (errs.length) console.error('KaTeX errors:\n' + errs.join('\n'));
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: outPdf, format: 'A4', printBackground: true,
    margin: { top: '20mm', bottom: '20mm', left: '18mm', right: '18mm' },
    displayHeaderFooter: true,
    headerTemplate: '<div style="font-size:8px;width:100%;text-align:right;padding-right:18mm;color:#777">Financial Econometrics · Group Work Project 1' + (notebook ? ' · Notebook' : '') + '</div>',
    footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#777"><span class="pageNumber"></span> / <span class="totalPages"></span></div>' });
  await browser.close();
  fs.unlinkSync(tmp);
})();
