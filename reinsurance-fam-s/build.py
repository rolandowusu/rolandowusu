"""Build "Reinsurance for FAM-S" study guide PDF.

Every numerical answer in the guide is computed in this script (see the
`calc_*` blocks), so the worked solutions cannot drift from the arithmetic.

Run:  python3 build.py   ->  Reinsurance-for-FAM-S.pdf
"""

import math
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table,
    TableStyle, PageBreak, KeepTogether, CondPageBreak,
)
from reportlab.platypus.tableofcontents import TableOfContents

HERE = Path(__file__).resolve().parent
OUT = HERE / "Reinsurance-for-FAM-S.pdf"

# ---------------------------------------------------------------- fonts
DJ = "/usr/share/fonts/truetype/dejavu/"
LB = "/usr/share/fonts/truetype/liberation/"
pdfmetrics.registerFont(TTFont("Body", DJ + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Body-Bold", DJ + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Body-Italic", LB + "LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Body-BoldItalic", LB + "LiberationSans-BoldItalic.ttf"))
pdfmetrics.registerFont(TTFont("Mono", DJ + "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-Bold",
                              italic="Body-Italic", boldItalic="Body-BoldItalic")

# ---------------------------------------------------------------- palette
NAVY = colors.HexColor("#1F3A5F")
TEAL = colors.HexColor("#2A7F7F")
ORANGE = colors.HexColor("#C8641E")
RED = colors.HexColor("#B03A2E")
GREY = colors.HexColor("#5A5A5A")
LIGHT_BLUE = colors.HexColor("#E8F0F8")
LIGHT_TEAL = colors.HexColor("#E3F2F0")
LIGHT_ORANGE = colors.HexColor("#FCEFE3")
LIGHT_RED = colors.HexColor("#F8E5E3")
LIGHT_GREY = colors.HexColor("#F2F2F2")
C_INSURER = colors.HexColor("#4A7FB5")
C_REINS = colors.HexColor("#E08A3C")
C_ABOVE = colors.HexColor("#9DB4C8")

# ---------------------------------------------------------------- styles
base = ParagraphStyle("base", fontName="Body", fontSize=10.2, leading=14.6,
                      spaceAfter=6, textColor=colors.black)
S = {
    "body": base,
    "title": ParagraphStyle("title", parent=base, fontName="Body-Bold",
                            fontSize=28, leading=34, textColor=NAVY,
                            alignment=TA_CENTER, spaceAfter=10),
    "subtitle": ParagraphStyle("subtitle", parent=base, fontSize=13,
                               leading=18, textColor=TEAL,
                               alignment=TA_CENTER, spaceAfter=6),
    "h1": ParagraphStyle("h1", parent=base, fontName="Body-Bold", fontSize=18,
                         leading=23, textColor=NAVY, spaceBefore=4,
                         spaceAfter=10),
    "h2": ParagraphStyle("h2", parent=base, fontName="Body-Bold",
                         fontSize=13.2, leading=17, textColor=TEAL,
                         spaceBefore=10, spaceAfter=5),
    "h3": ParagraphStyle("h3", parent=base, fontName="Body-Bold", fontSize=11,
                         leading=15, textColor=NAVY, spaceBefore=6,
                         spaceAfter=3),
    "bullet": ParagraphStyle("bullet", parent=base, leftIndent=16,
                             bulletIndent=5, spaceAfter=3),
    "box": ParagraphStyle("box", parent=base, spaceAfter=3),
    "boxtitle": ParagraphStyle("boxtitle", parent=base, fontName="Body-Bold",
                               spaceAfter=3),
    "formula": ParagraphStyle("formula", parent=base, fontSize=10.8,
                              leading=16, alignment=TA_CENTER, spaceAfter=4),
    "q": ParagraphStyle("q", parent=base, spaceAfter=4),
    "choice": ParagraphStyle("choice", parent=base, leftIndent=18,
                             spaceAfter=1),
    "step": ParagraphStyle("step", parent=base, leftIndent=14, spaceAfter=3),
    "small": ParagraphStyle("small", parent=base, fontSize=8.6, leading=11,
                            textColor=GREY),
    "cell": ParagraphStyle("cell", parent=base, fontSize=9.2, leading=12,
                           spaceAfter=0),
    "cellb": ParagraphStyle("cellb", parent=base, fontName="Body-Bold",
                            fontSize=9.2, leading=12, spaceAfter=0,
                            textColor=colors.white),
    "toc1": ParagraphStyle("toc1", parent=base, fontName="Body-Bold",
                           fontSize=11, leading=17, leftIndent=10),
    "toc2": ParagraphStyle("toc2", parent=base, fontSize=9.6, leading=13,
                           leftIndent=28, textColor=GREY),
}


# ---------------------------------------------------------------- helpers
def money(x, dp=0):
    s = f"{abs(x):,.{dp}f}"
    return ("−" if x < 0 else "") + s


def num(x, dp=4):
    return f"{x:,.{dp}f}"


story = []


def P(text, style="body"):
    story.append(Paragraph(text, S[style]))


def H1(text):
    story.append(PageBreak())
    p = Paragraph(text, S["h1"])
    p._toc = (0, text)
    story.append(p)


def H2(text, toc=True):
    story.append(CondPageBreak(1.3 * inch))
    p = Paragraph(text, S["h2"])
    if toc:
        p._toc = (1, text)
    story.append(p)


def H3(text):
    story.append(CondPageBreak(0.9 * inch))
    P(text, "h3")


def bullets(items, style="bullet"):
    for it in items:
        story.append(Paragraph(it, S[style], bulletText="•"))


def box(title, lines, fill, edge, width=6.5 * inch):
    """Coloured call-out box. `lines` is a list of paragraph strings."""
    content = []
    if title:
        content.append(Paragraph(f'<font color="#{edge.hexval()[2:]}">{title}</font>',
                                 S["boxtitle"]))
    for ln in lines:
        if isinstance(ln, str):
            content.append(Paragraph(ln, S["box"]))
        else:
            content.append(ln)
    t = Table([[content]], colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), fill),
        ("LINEBEFORE", (0, 0), (0, -1), 3.5, edge),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(Spacer(1, 3))
    story.append(t)
    story.append(Spacer(1, 7))


def idea(lines, title="Key idea"):
    box(title, lines, LIGHT_BLUE, NAVY)


def formula(lines, title="Formula"):
    # runs of spaces separate items on one line; keep them visible
    lines = [re.sub(r" {3,}", " &nbsp;&nbsp;&nbsp;&nbsp; ", l) for l in lines]
    box(title, [Paragraph(l, S["formula"]) for l in lines], LIGHT_TEAL, TEAL)


def trap(lines, title="Exam trap"):
    box(title, lines, LIGHT_RED, RED)


def analogy(lines, title="Everyday analogy"):
    box(title, lines, LIGHT_ORANGE, ORANGE)


def table(rows, widths, header=True, zebra=True):
    data = []
    for i, r in enumerate(rows):
        st = S["cellb"] if (header and i == 0) else S["cell"]
        data.append([Paragraph(str(c), st) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    if zebra:
        for i in range(1 if header else 0, len(rows)):
            if i % 2 == 0:
                style.append(("BACKGROUND", (0, i), (-1, i), LIGHT_GREY))
    t.setStyle(TableStyle(style))
    story.append(Spacer(1, 2))
    story.append(t)
    story.append(Spacer(1, 8))


def steps(lines):
    for i, ln in enumerate(lines, 1):
        story.append(Paragraph(f"<b>Step {i}.</b> {ln}", S["step"]))


def answer(text):
    box(None, [f"<b>Answer:</b> {text}"], colors.HexColor("#E6F4EA"),
        colors.HexColor("#2E7D32"))


def question(label, text, choices=None):
    parts = [Paragraph(f"<b>{label}</b>  {text}", S["q"])]
    if choices:
        for letter_, ch in zip("ABCDE", choices):
            parts.append(Paragraph(f"({letter_})  {ch}", S["choice"]))
    story.append(CondPageBreak(1.6 * inch))
    t = Table([[parts]], colWidths=[6.5 * inch])
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, NAVY),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(t)
    story.append(Spacer(1, 6))


def fig(drawing, caption):
    story.append(KeepTogether([drawing, Paragraph(caption, S["small"]),
                               Spacer(1, 8)]))


# ---------------------------------------------------------------- diagrams
def flow_diagram():
    d = Drawing(6.5 * inch, 1.35 * inch)
    w, h, y = 104, 46, 34
    xs = [4, 134, 264, 394]
    labels = [("Policyholder", "buys insurance"),
              ("Insurer", "= cedent / ceding co."),
              ("Reinsurer", "= assuming company"),
              ("Retrocessionaire", "reinsurer's reinsurer")]
    fills = [LIGHT_GREY, C_INSURER, C_REINS, C_ABOVE]
    for x, (a, b), f in zip(xs, labels, fills):
        d.add(Rect(x, y, w, h, fillColor=f, strokeColor=NAVY, rx=6, ry=6))
        tc = colors.white if f in (C_INSURER, C_REINS) else colors.black
        d.add(String(x + w / 2, y + 27, a, fontName="Body-Bold", fontSize=9.5,
                     textAnchor="middle", fillColor=tc))
        d.add(String(x + w / 2, y + 12, b, fontName="Body", fontSize=7.4,
                     textAnchor="middle", fillColor=tc))
    arrows = ["premium →", "ceded premium →", "retro premium →"]
    for i, lab in enumerate(arrows):
        x0, x1 = xs[i] + w, xs[i + 1]
        d.add(Line(x0 + 2, y + h - 10, x1 - 4, y + h - 10, strokeColor=NAVY))
        d.add(Polygon([x1 - 4, y + h - 7, x1 - 4, y + h - 13, x1 + 1, y + h - 10],
                      fillColor=NAVY, strokeColor=NAVY))
        d.add(Line(x0 + 4, y + 10, x1 - 2, y + 10, strokeColor=ORANGE))
        d.add(Polygon([x0 + 4, y + 7, x0 + 4, y + 13, x0 - 1, y + 10],
                      fillColor=ORANGE, strokeColor=ORANGE))
        d.add(String((x0 + x1) / 2, y + h + 2, lab, fontName="Body",
                     fontSize=6.6, textAnchor="middle", fillColor=NAVY))
        d.add(String((x0 + x1) / 2, y - 3, "← claim money", fontName="Body",
                     fontSize=6.6, textAnchor="middle", fillColor=ORANGE))
    d.add(String(4, 6, "Premiums flow right; claim payments flow back left. "
                 "The policyholder only ever deals with the insurer.",
                 fontName="Body", fontSize=7.8, fillColor=GREY))
    return d


def bar_chart(bars, top, title, legend):
    """bars: list of (label, [(amount, colour), ...]) stacked bottom-up."""
    W, H = 6.5 * inch, 2.45 * inch
    d = Drawing(W, H)
    x0, y0, ph = 52, 30, H - 62
    scale = ph / top
    bw, gap = 62, 40
    d.add(Line(x0, y0, x0, y0 + ph + 4, strokeColor=GREY))
    d.add(Line(x0, y0, x0 + len(bars) * (bw + gap) + 10, y0, strokeColor=GREY))
    step = top / 4
    for k in range(5):
        v = k * step
        yy = y0 + v * scale
        d.add(Line(x0 - 3, yy, x0, yy, strokeColor=GREY))
        d.add(String(x0 - 5, yy - 3, f"{v / 1000:,.0f}k", fontName="Body",
                     fontSize=7, textAnchor="end", fillColor=GREY))
    for i, (lab, segs) in enumerate(bars):
        x = x0 + 18 + i * (bw + gap)
        yy = y0
        for amt, col in segs:
            if amt <= 0:
                continue
            hh = amt * scale
            d.add(Rect(x, yy, bw, hh, fillColor=col, strokeColor=colors.white,
                       strokeWidth=0.8))
            if hh > 11:
                d.add(String(x + bw / 2, yy + hh / 2 - 3, f"{amt / 1000:,.0f}k",
                             fontName="Body-Bold", fontSize=7.4,
                             textAnchor="middle", fillColor=colors.white))
            yy += hh
        d.add(String(x + bw / 2, y0 - 12, lab, fontName="Body", fontSize=7.6,
                     textAnchor="middle"))
    d.add(String(x0, H - 14, title, fontName="Body-Bold", fontSize=9,
                 fillColor=NAVY))
    lx = x0 + len(bars) * (bw + gap) + 18
    for j, (txt, col) in enumerate(legend):
        ly = y0 + ph - 14 - j * 16
        d.add(Rect(lx, ly, 10, 10, fillColor=col, strokeColor=col))
        d.add(String(lx + 14, ly + 2, txt, fontName="Body", fontSize=7.6))
    return d


def layer_cake():
    W, H = 6.5 * inch, 2.6 * inch
    d = Drawing(W, H)
    x, y, w = 70, 18, 170
    layers = [(0, 1, C_INSURER, "Retention (insurer keeps)", "0 to 1M"),
              (1, 4, C_REINS, "1st layer: 4M xs 1M", "1M to 5M"),
              (4, 10, colors.HexColor("#D9A066"), "2nd layer: 10M xs 5M", "5M to 15M"),
              (10, 12, C_ABOVE, "Above all layers (back to insurer)", "15M +")]
    sc = 13.5
    for lo, hi, col, name, rng in layers:
        d.add(Rect(x, y + lo * sc, w, (hi - lo) * sc, fillColor=col,
                   strokeColor=colors.white))
        d.add(String(x + w + 10, y + (lo + hi) / 2 * sc - 3, name,
                     fontName="Body-Bold", fontSize=8, fillColor=NAVY))
        d.add(String(x - 6, y + (lo + hi) / 2 * sc - 3, rng, fontName="Body",
                     fontSize=7.2, textAnchor="end", fillColor=GREY))
    return d


# ---------------------------------------------------------------- calculations
def exp_lev(theta, d):          # E[X ∧ d], exponential mean theta
    return theta * (1 - math.exp(-d / theta))


def par_lev(alpha, theta, d):   # E[X ∧ d], two-parameter Pareto
    return theta / (alpha - 1) * (1 - (theta / (theta + d)) ** (alpha - 1))


def unif_lev(b, d):             # E[X ∧ d], X ~ U(0, b)
    return d - d * d / (2 * b)


def unif_lev2(b, d):            # E[(X ∧ d)^2], X ~ U(0, b)
    return d * d - 2 * d ** 3 / (3 * b)


# ================================================================ CONTENT
# ---------------------------------------------------------------- cover
story.append(Spacer(1, 1.6 * inch))
P("Reinsurance for Exam FAM-S", "title")
P("A from-zero explanation, the formulas you actually need, "
  "and fully worked exam-style questions", "subtitle")
story.append(Spacer(1, 0.35 * inch))
fig(flow_diagram(), "")
story.append(Spacer(1, 0.2 * inch))
box("How to use this guide", [
    "1. Read Part 1 slowly. It contains <b>no maths</b>: it builds the picture "
    "of what reinsurance is. Most people who 'understand nothing' are missing "
    "this picture, not the algebra.",
    "2. Parts 2 and 3 cover the two families of reinsurance (proportional and "
    "non-proportional), each with small numeric examples.",
    "3. Part 4 connects reinsurance to the Loss Models tools you already know "
    "from FAM-S (limited expected values, stop-loss, compound distributions).",
    "4. Part 5 has 16 exam-style questions solved step by step; Part 6 has 12 "
    "more for you to try, with answers and short solutions at the end.",
    "5. Part 7 is a one-page cheat sheet for the night before the exam.",
], LIGHT_GREY, NAVY)
P("Scope: the reinsurance material in the short-term (FAM-S) syllabus: types "
  "of reinsurance, why insurers buy it, and the calculations that apply "
  "coverage-modification and aggregate-loss tools to reinsurance contracts. "
  "Check the current SOA syllabus for the exact readings in your sitting. "
  "Every number in the solutions was calculated by the script that built this "
  "PDF.", "small")

# ---------------------------------------------------------------- TOC
story.append(PageBreak())
P("Contents", "h1")
toc = TableOfContents()
toc.levelStyles = [S["toc1"], S["toc2"]]
story.append(toc)

# ================================================================ PART 1
H1("Part 1. What reinsurance is, in plain words")
H2("1.1 The one-sentence definition")
idea(["<b>Reinsurance is insurance bought by an insurance company.</b> "
      "The insurer passes (\"cedes\") part of the risk it has accepted from its "
      "customers to another company, the reinsurer, and pays it a premium for "
      "doing so."])
P("You already know how ordinary insurance works: a homeowner pays a premium "
  "and, in exchange, the insurer pays for losses. But the insurer now holds a lot "
  "of risk. If one huge factory burns down, or a hurricane hits 20,000 of its "
  "homeowners at once, the insurer itself could be ruined. So the insurer does "
  "exactly what its customers did: it buys protection. That protection is "
  "reinsurance.")
analogy(["Imagine you lend money to many friends. Most pay you back, but one "
         "large loan could bankrupt you if it goes bad. You ask a richer cousin: "
         "<i>\"I'll give you a small fee each month; if any single loan loses more "
         "than $1,000, you cover the rest.\"</i> You have just bought reinsurance. "
         "Your friends never know about your cousin; they still owe <i>you</i>."])

H2("1.2 The vocabulary (learn these words; questions use them without explaining)")
table([
    ["Term", "Meaning"],
    ["Cedent / ceding company / primary insurer / direct writer",
     "The insurer that sold the original policies and is buying reinsurance."],
    ["Reinsurer / assuming company", "The company that accepts the risk."],
    ["Cede / cession", "To pass risk to a reinsurer / the amount passed."],
    ["Retention", "The part of the risk the cedent keeps for itself."],
    ["Ceded premium", "Premium the cedent pays the reinsurer."],
    ["Ceding commission", "Money the reinsurer pays back to the cedent (mainly in "
     "proportional deals) to cover the cedent's costs of selling and running the "
     "policies."],
    ["Retrocession", "Reinsurance bought by a reinsurer. The seller is the "
     "<b>retrocessionaire</b>."],
    ["Treaty", "One contract that automatically covers a whole <b>class</b> of "
     "policies (e.g. all homeowners policies written in 2026)."],
    ["Facultative (\"fac\")", "Reinsurance negotiated <b>one policy at a time</b>; "
     "each risk can be accepted or declined by the reinsurer."],
    ["Layer, attachment point, limit", "In excess-of-loss: the reinsurer pays losses "
     "above the <b>attachment point</b> (retention), up to the <b>limit</b>. "
     "\"4M xs 1M\" means the layer from 1M up to 5M."],
    ["Gross / net", "<b>Gross</b> = before reinsurance. <b>Net</b> = after "
     "reinsurance (what the cedent actually keeps)."],
], [2.3 * inch, 4.2 * inch])
trap(["The policyholder has <b>no contract with the reinsurer</b>. If the "
      "reinsurer fails to pay, the insurer must still pay its policyholder in "
      "full. This risk for the insurer is called <b>credit risk</b> (or "
      "counterparty risk) of the reinsurer."])

H2("1.3 Why do insurers buy reinsurance?")
P("Exams love \"which of the following is NOT a reason to buy reinsurance\" "
  "questions. There are five or six classic reasons; learn the logic, not just "
  "the list.")
table([
    ["Reason", "What it means", "Tiny example"],
    ["1. Increase capacity",
     "Lets the insurer write bigger policies (or more of them) than its own "
     "capital could support.",
     "A small insurer can insure a $50M building because a reinsurer takes $45M."],
    ["2. Stabilise results (reduce volatility)",
     "Smooths year-to-year profits by capping big or unusual losses.",
     "Excess-of-loss caps any single claim at $1M net."],
    ["3. Catastrophe protection",
     "Protects against one event (hurricane, earthquake) causing many claims at "
     "once.",
     "Cat XL pays when one storm costs more than $20M in total."],
    ["4. Surplus relief / financing",
     "Ceding commissions immediately reimburse up-front expenses, which "
     "strengthens the insurer's surplus (capital) when it is growing fast.",
     "A 30% ceding commission refunds acquisition costs on a quota share."],
    ["5. Expertise / services",
     "Reinsurers see data from many insurers and help with pricing, underwriting "
     "and claims in new lines.",
     "An insurer entering cyber insurance uses the reinsurer's pricing models."],
    ["6. Exit a line / transfer a portfolio",
     "Hand an entire book of business (including old claims) to a reinsurer.",
     "Portfolio transfer or loss portfolio transfer when closing a line."],
], [1.45 * inch, 2.75 * inch, 2.3 * inch])
idea(["Notice what is <b>not</b> on the list: reinsurance does <b>not</b> reduce "
      "the insurer's <i>expected</i> cost for free. The reinsurer charges a premium "
      "that is (on average) <b>larger</b> than the expected losses it pays, because "
      "it needs to cover its own expenses and profit. The insurer is paying to "
      "reduce <b>variability</b>, not expected losses."],
     title="Key idea: you pay for less risk, not for lower expected cost")

H2("1.4 The two big families: proportional vs non-proportional")
P("Every reinsurance contract answers one question: <b>for a given loss, how is "
  "it split between the insurer and the reinsurer?</b> There are only two kinds "
  "of answer.")
table([
    ["", "Proportional (pro rata)", "Non-proportional (excess of loss)"],
    ["How losses are split",
     "By a <b>percentage</b>. The reinsurer pays a share of <b>every</b> loss.",
     "By <b>amount</b>. The reinsurer pays only the part of a loss <b>above</b> "
     "a retention (up to a limit)."],
    ["Premium", "Same percentage of the premium is ceded (minus a ceding commission).",
     "Priced separately (the reinsurer's own rate), usually much smaller than for "
     "a proportional deal."],
    ["Small losses", "Shared.", "Insurer keeps them entirely."],
    ["Main examples", "Quota share; surplus share.",
     "Per-risk XL; per-occurrence (catastrophe) XL; aggregate stop-loss."],
    ["Best at", "Capacity, surplus relief, sharing a whole book.",
     "Cutting off large losses: volatility and catastrophe protection."],
], [1.3 * inch, 2.6 * inch, 2.6 * inch])
P("And, separately, every contract is either <b>treaty</b> (automatic, a whole "
  "class of business) or <b>facultative</b> (one risk at a time). These are two "
  "independent choices: you can have facultative excess-of-loss, treaty quota "
  "share, and so on.")
table([
    ["", "Treaty", "Facultative"],
    ["Scope", "All policies in a defined class", "One specific policy/risk"],
    ["Reinsurer can refuse a single policy?", "No (obligatory once signed)",
     "Yes, each risk is underwritten separately"],
    ["Admin cost per risk", "Low", "High"],
    ["Typical use", "Day-to-day protection of the whole book",
     "Unusual, very large or hazardous risks that fall outside the treaty"],
], [2.1 * inch, 2.2 * inch, 2.2 * inch])

# ================================================================ PART 2
H1("Part 2. Proportional reinsurance")
H2("2.1 Quota share: the same percentage of everything")
P("In a <b>quota share</b> the reinsurer takes a fixed percentage, say "
  "<b>a</b>, of <b>every</b> policy in the treaty: a share of the premiums and "
  "the same share of every loss. If the quota share is 40%, the reinsurer "
  "receives 40% of premiums and pays 40% of every claim, large or small.")
formula(["Reinsurer pays  =  a · X          Insurer keeps  =  (1 − a) · X",
         "E[retained] = (1 − a) E[X]          Var(retained) = (1 − a)<super>2</super> Var(X)"])
qs_bars = [(f"Loss {L // 1000}k", [(0.6 * L, C_INSURER), (0.4 * L, C_REINS)])
           for L in (50_000, 250_000, 700_000)]
fig(bar_chart(qs_bars, 800_000, "40% quota share: every loss is split 60/40",
              [("Insurer keeps 60%", C_INSURER), ("Reinsurer pays 40%", C_REINS)]),
    "Figure 2.1. In a quota share the split is the same percentage whatever "
    "the loss size, so even tiny claims are shared.")
H3("Ceding commission")
P("The insurer spent money to sell those policies (agent commissions, "
  "underwriting, admin). If it simply handed 40% of the premium to the reinsurer, "
  "it would be paying all those expenses but only keeping 60% of the premium. "
  "So the reinsurer pays back a <b>ceding commission</b>, a percentage of the "
  "<b>ceded premium</b>.")
formula(["Net cash paid to reinsurer  =  ceded premium × (1 − ceding commission rate)"])
P("A quota share with a decent ceding commission is the classic tool for "
  "<b>surplus relief</b>: a fast-growing insurer gets cash back immediately for "
  "expenses it has already paid.")
trap(["The ceding commission is a percentage of the <b>ceded</b> premium, not of the "
      "insurer's total (gross) premium.",
      "A quota share does <b>not</b> cap large losses. If the gross loss is "
      "$100M, a 40% quota share still leaves the insurer with $60M. That is why "
      "quota share is weak at catastrophe protection."])

H2("2.2 Surplus share: the percentage depends on the policy size")
P("A quota share cedes the same 40% of a $10,000 policy and a $10,000,000 policy, "
  "which is wasteful: the insurer did not need help with the small one. "
  "<b>Surplus share</b> fixes this. The insurer chooses a <b>retention line</b> "
  "(the amount of insurance it is happy to keep on any one policy) and cedes "
  "only the part of each policy's amount of insurance that is <b>above</b> that "
  "line. The reinsurer's capacity is expressed as a number of <b>lines</b>: "
  "a \"4-line surplus\" with a $100,000 line means the reinsurer accepts up to "
  "4 × 100,000 = $400,000 on any one policy.")
P("The key step: the split is decided <b>per policy, using the policy's amount of "
  "insurance (its limit)</b>, not the loss. Once the percentage for that policy "
  "is fixed, it is applied to <b>every</b> loss on that policy, like a quota "
  "share for that policy alone.")
formula([
    "Ceded amount of insurance = min( max(L − R, 0) ,  n·R )",
    "Ceded fraction  c = (ceded amount of insurance) / L",
    "Reinsurer pays c · X ;   insurer keeps (1 − c) · X",
    "<font size=8.6>L = policy limit (amount of insurance), R = retention line, "
    "n = number of lines, X = the loss</font>"])

# example for figure
R_, n_ = 100_000, 4
pols = [80_000, 300_000, 700_000]
ss_rows = [["Policy limit L", "Ceded insurance", "Ceded fraction c",
            "Loss of 150k: reinsurer pays", "Insurer keeps"]]
ss_bars = []
for Lp in pols:
    ceded_ins = min(max(Lp - R_, 0), n_ * R_)
    c = ceded_ins / Lp
    ss_rows.append([money(Lp), money(ceded_ins), f"{c:.4f}",
                    money(c * 150_000, 2), money((1 - c) * 150_000, 2)])
    ss_bars.append((f"Policy {Lp // 1000}k",
                    [(Lp - ceded_ins, C_INSURER), (ceded_ins, C_REINS)]))
P("<b>Example.</b> Retention line R = 100,000 and a 4-line surplus (reinsurer "
  "capacity 400,000). Three policies each have a loss of 150,000:")
table(ss_rows, [1.15 * inch, 1.2 * inch, 1.2 * inch, 1.65 * inch, 1.3 * inch])
fig(bar_chart(ss_bars, 800_000, "Surplus share: how each policy's AMOUNT OF INSURANCE is split",
              [("Insurer's share", C_INSURER), ("Reinsurer's share", C_REINS)]),
    "Figure 2.2. The 80k policy is under the line, so it is fully retained. For "
    "the 700k policy the reinsurer is full at 400k, so the insurer keeps "
    "100k + the 200k beyond capacity = 300k of the 700k.")
trap(["Do <b>not</b> apply the retention to the <b>loss</b>. A 150,000 loss on "
      "a 300,000 policy is split 1/3 : 2/3, not \"insurer pays 100,000, reinsurer "
      "pays 50,000\". Subtracting the retention from the loss is excess of loss, "
      "a completely different contract.",
      "If L exceeds (n + 1)·R, the part above the treaty's capacity comes back to "
      "the insurer (or is placed facultatively). The ceded fraction is then "
      "nR / L, not (L − R)/L."])

# ================================================================ PART 3
H1("Part 3. Non-proportional (excess of loss) reinsurance")
H2("3.1 Per-risk excess of loss: \"y xs d\"")
P("Now the split is by <b>amount</b>. The insurer keeps every loss up to the "
  "<b>retention</b> (attachment point) d. The reinsurer pays the part of the "
  "loss above d, up to a <b>limit</b> y. The notation is <b>\"y xs d\"</b> "
  "(read \"y excess of d\"). The layer covers losses between d and d + y.")
formula(["Reinsurer pays  =  min( max(X − d, 0) ,  y )  =  (X ∧ (d + y)) − (X ∧ d)",
         "Insurer keeps  =  X − reinsurer's payment  =  (X ∧ d) + (X − d − y)<sub>+</sub>"])
d_, y_ = 100_000, 400_000
xl_bars = []
for L in (50_000, 250_000, 700_000):
    in_layer = min(max(L - d_, 0), y_)
    below = min(L, d_)
    above = max(L - d_ - y_, 0)
    xl_bars.append((f"Loss {L // 1000}k", [(below, C_INSURER), (in_layer, C_REINS),
                                          (above, C_ABOVE)]))
fig(bar_chart(xl_bars, 800_000, "Per-risk XL: 400k xs 100k",
              [("Insurer: retention", C_INSURER), ("Reinsurer: layer", C_REINS),
               ("Insurer: above limit", C_ABOVE)]),
    "Figure 3.1. A 50k loss is fully retained. A 250k loss: insurer 100k, "
    "reinsurer 150k. A 700k loss: insurer 100k + 200k above the layer, reinsurer "
    "400k (its limit).")
idea(["This is <b>exactly</b> the deductible and policy-limit maths from Loss "
      "Models, seen from a different seat. For the reinsurer, the retention d "
      "acts like an <b>ordinary deductible</b> and d + y acts like the "
      "<b>maximum covered loss</b> u. Everything you know about "
      "E[X ∧ u] − E[X ∧ d] carries over."])

H2("3.2 Per-occurrence (catastrophe) excess of loss")
P("Same idea, but the retention applies to the <b>total of all losses from one "
  "event</b> (one hurricane, one earthquake), adding up claims across many "
  "policies. A per-risk XL is useless against a hurricane that causes 5,000 "
  "claims of $40,000 each, because no single claim exceeds the retention. A cat "
  "XL looks at the sum.")
P("Cat programmes are often built from several stacked layers, sold to "
  "different reinsurers:")
fig(layer_cake(), "Figure 3.2. A layered catastrophe programme: each layer pays only "
    "the slice of an event's total loss that falls inside it. A 12M event: insurer "
    "1M, layer 1 pays 4M, layer 2 pays 7M. A 20M event: layer 2 is exhausted "
    "(10M), and 5M above 15M comes back to the insurer.")
P("<b>Reinstatements.</b> Once a cat layer has paid out, its limit can be "
  "\"reinstated\" (restored) for the rest of the year, often for an extra premium "
  "proportional to the amount used. You need the idea; detailed reinstatement "
  "premium calculations are rarely the focus at FAM-S.")

H2("3.3 Aggregate excess of loss / stop-loss")
P("Here the retention applies to the <b>total losses for the whole year</b> (or "
  "the whole portfolio), S = X<sub>1</sub> + ... + X<sub>N</sub>. It is often "
  "written in terms of the <b>loss ratio</b>: e.g. \"the reinsurer pays losses "
  "between an 80% and a 100% loss ratio\".")
formula(["Stop-loss reinsurer pays (S − d)<sub>+</sub>,   "
         "E[(S − d)<sub>+</sub>] = E[S] − E[S ∧ d]",
         "Net stop-loss premium = E[(S − d)<sub>+</sub>]"])
P("This is the \"stop-loss insurance\" of the aggregate-loss chapter of Loss "
  "Models. The <b>net stop-loss premium</b> means the expected payment, with no "
  "loading for expenses or profit.")

H2("3.4 Combining contracts: order matters")
P("Insurers usually have several contracts at once. The treaty wording says "
  "which applies first: a contract \"<b>inures to the benefit</b>\" of another "
  "if its recoveries are taken off before the other is applied. Typical order:")
bullets(["Facultative first (on that specific risk),",
         "then per-risk XL / surplus share,",
         "then quota share on what is left (if the quota share is \"on net\"),",
         "and catastrophe XL last, on the net losses after everything else."])
P("Always read which comes first: you get <b>different</b> answers otherwise "
  "(see Question 12 in Part 5).")

H2("3.5 Proportional vs XL: which reduces risk more?")
P("A famous result (and a favourite exam question): <b>for the same expected "
  "ceded loss</b>, an excess-of-loss (stop-loss) contract leaves the insurer with "
  "<b>lower variance</b> than a quota share, and is in fact optimal among all "
  "contracts with that expected cession. Intuition: XL removes the extreme "
  "outcomes, which are exactly what drives variance; quota share shrinks every "
  "outcome evenly, wasting reinsurance on small losses that were never a "
  "threat. Question 7 shows the numbers.")

# ================================================================ PART 4
H1("Part 4. The Loss Models toolkit applied to reinsurance")
P("Almost every calculation question reduces to one of a few formulas. Here they "
  "are in one place, with the standard distributions from the exam tables.")
H2("4.1 The building blocks")
formula([
    "(X − d)<sub>+</sub> = max(X − d, 0)          X ∧ d = min(X, d)          "
    "X = (X ∧ d) + (X − d)<sub>+</sub>",
    "E[(X − d)<sub>+</sub>] = E[X] − E[X ∧ d] = ∫<sub>d</sub><super>∞</super> S(x) dx",
    "Layer from d to u:  E[payment per loss] = E[X ∧ u] − E[X ∧ d]",
    "Per payment (given the layer is hit):  [E[X ∧ u] − E[X ∧ d]] / S(d)",
], title="Formulas you must know cold")
table([
    ["Distribution", "E[X]", "E[X ∧ d]"],
    ["Exponential (mean θ)", "θ", "θ (1 − e<super>−d/θ</super>)"],
    ["Pareto (α, θ)", "θ / (α − 1)",
     "θ/(α − 1) · [1 − (θ/(θ + d))<super>α−1</super>]"],
    ["Uniform (0, b)", "b / 2", "d − d<super>2</super>/(2b)   for 0 ≤ d ≤ b"],
    ["Discrete", "Σ x p(x)", "Σ<sub>x&lt;d</sub> x p(x) + d · P(X ≥ d)"],
], [1.7 * inch, 1.3 * inch, 3.5 * inch])
idea(["Two handy facts: (1) for the <b>exponential</b>, the memoryless property "
      "means the reinsurer's payment <b>per payment</b> above any retention is "
      "again exponential with the same mean θ. (2) For the <b>Pareto</b>, the excess "
      "over d, given X &gt; d, is Pareto with α unchanged and θ replaced by θ + d."],
     title="Shortcuts")

H2("4.2 Frequency: how many times is the reinsurer hit?")
P("If losses arrive with frequency N and each loss exceeds the retention with "
  "probability v = S(d), the number of losses that reach the reinsurer is "
  "N' = number of those. For the usual families, N' stays in the same family:")
table([
    ["N (number of losses)", "N' (losses reaching the reinsurer)"],
    ["Poisson(λ)", "Poisson(λ v)"],
    ["Binomial(m, q)", "Binomial(m, q v)"],
    ["Negative binomial(r, β)", "Negative binomial(r, β v)"],
], [3.0 * inch, 3.5 * inch])
formula(["Expected annual reinsurer cost = E[N] · E[payment per loss] = E[N'] · E[payment per payment]"])

H2("4.3 Inflation")
P("If all losses grow by a factor (1 + r), replace X by (1 + r)X. For a scale "
  "distribution, just multiply θ by (1 + r). <b>The retention does not "
  "inflate</b> (it is a fixed number in the contract), so the reinsurer's share "
  "grows <b>faster</b> than the inflation rate. This is called the "
  "<b>leveraged</b> effect of inflation on excess layers.")
formula(["E[((1 + r)X − d)<sub>+</sub>] = (1 + r) · E[(X − d/(1 + r))<sub>+</sub>]"])

H2("4.4 Aggregate stop-loss with a discrete S")
P("When S takes values on a grid (0, h, 2h, ...), compute E[S ∧ d] directly from "
  "the probabilities, then subtract from E[S]. If the retention d lies "
  "<b>between</b> two possible values of S, the stop-loss premium is a straight "
  "line between them, so you can interpolate:")
formula(["If S has no mass strictly between a and b, and a ≤ d ≤ b:",
         "E[(S − d)<sub>+</sub>] = ((b − d)/(b − a)) · E[(S − a)<sub>+</sub>] + "
         "((d − a)/(b − a)) · E[(S − b)<sub>+</sub>]"])
P("For a compound Poisson S with discrete severity, the recursion (Panjer) gives "
  "the first few probabilities: P(S = 0) = e<super>−λ</super>, and for "
  "severity on {1, 2, ...}: P(S = k) = (λ/k) Σ<sub>j</sub> j f(j) P(S = k − j).")

# ================================================================ PART 5
H1("Part 5. Exam-style questions, fully solved")
P("The questions get harder as you go. For each one: try it yourself for five "
  "minutes, then read the solution.")

# ---- Q1
qs_a, qs_loss, qs_prem, qs_cc = 0.40, 250_000, 10_000_000, 0.30
q1_ceded = qs_a * qs_loss
q1_cprem = qs_a * qs_prem
q1_comm = qs_cc * q1_cprem
question("Question 1 (quota share basics).",
         f"An insurer has a 40% quota share treaty. Gross written premium is "
         f"{money(qs_prem)}, and the reinsurer pays a 30% ceding commission. A "
         f"single claim of {money(qs_loss)} occurs. Calculate (a) the reinsurer's "
         f"share of the claim, (b) the insurer's net retained claim, and (c) the "
         f"net premium cash the insurer pays the reinsurer.")
steps([f"Reinsurer's share = 40% × {money(qs_loss)} = <b>{money(q1_ceded)}</b>.",
       f"Insurer retains 60% × {money(qs_loss)} = <b>{money(qs_loss - q1_ceded)}</b>.",
       f"Ceded premium = 40% × {money(qs_prem)} = {money(q1_cprem)}. Ceding "
       f"commission = 30% × {money(q1_cprem)} = {money(q1_comm)} (a % of the "
       f"<i>ceded</i> premium). Net cash = {money(q1_cprem)} − {money(q1_comm)} = "
       f"<b>{money(q1_cprem - q1_comm)}</b>."])
answer(f"(a) {money(q1_ceded)}   (b) {money(qs_loss - q1_ceded)}   "
       f"(c) {money(q1_cprem - q1_comm)}")

# ---- Q2
q2_rows = ss_rows
question("Question 2 (surplus share).",
         "A property insurer has a 4-line surplus treaty with a retention line of "
         "100,000. It writes three buildings with amounts of insurance 80,000, "
         "300,000 and 700,000. Each building suffers a loss of 150,000. "
         "Calculate the reinsurer's payment on each.")
c2 = [min(max(Lp - 100_000, 0), 400_000) / Lp for Lp in pols]
steps(["Reinsurer capacity = 4 lines × 100,000 = 400,000 per building.",
       "80,000 building: below the retention line, so nothing is ceded. "
       "c = 0, reinsurer pays <b>0</b>.",
       f"300,000 building: ceded insurance = 300,000 − 100,000 = 200,000 "
       f"(≤ 400,000). c = 200,000/300,000 = {c2[1]:.4f}. Reinsurer pays "
       f"{c2[1]:.4f} × 150,000 = <b>{money(c2[1] * 150_000)}</b>.",
       f"700,000 building: 700,000 − 100,000 = 600,000 &gt; 400,000, so ceded "
       f"insurance is capped at 400,000. c = 400,000/700,000 = {c2[2]:.4f}. "
       f"Reinsurer pays <b>{money(c2[2] * 150_000, 2)}</b>; the insurer keeps "
       f"{money((1 - c2[2]) * 150_000, 2)}."])
answer(f"0;  {money(c2[1] * 150_000)};  {money(c2[2] * 150_000, 2)}")

# ---- Q3
question("Question 3 (per-risk XL).",
         "An insurer buys a per-risk excess of loss treaty \"400,000 xs 100,000\". "
         "During the year it has three losses: 50,000, 250,000 and 700,000. "
         "Calculate the total amount paid by the reinsurer and the total net "
         "retained loss.",
         ["400,000", "550,000", "600,000", "850,000", "1,000,000"])
q3_l = [50_000, 250_000, 700_000]
q3_re = [min(max(L - 100_000, 0), 400_000) for L in q3_l]
steps(["The layer runs from 100,000 to 500,000. For each loss, the reinsurer "
       "pays the slice of the loss inside that band.",
       f"50,000: entirely below 100,000, reinsurer pays {money(q3_re[0])}.",
       f"250,000: slice from 100,000 to 250,000, reinsurer pays {money(q3_re[1])}.",
       f"700,000: slice from 100,000 to 500,000 (the full limit), reinsurer pays "
       f"{money(q3_re[2])}; the 200,000 above 500,000 is back with the insurer.",
       f"Total ceded = {money(sum(q3_re))}. Total gross = {money(sum(q3_l))}, so "
       f"net retained = {money(sum(q3_l) - sum(q3_re))}."])
answer(f"<b>(B)</b> reinsurer pays {money(sum(q3_re))}; insurer retains "
       f"{money(sum(q3_l) - sum(q3_re))}.")

# ---- Q4
th4, d4, r4 = 2000, 1000, 0.10
q4_a = th4 * math.exp(-d4 / th4)
q4_b = th4 - q4_a
th4i = th4 * (1 + r4)
q4_c = th4i * math.exp(-d4 / th4i)
q4_inc = q4_c / q4_a - 1
question("Question 4 (XL with exponential losses and inflation).",
         "Individual losses follow an exponential distribution with mean 2,000. "
         "The insurer buys excess of loss reinsurance with retention 1,000 and no "
         "upper limit. (a) Calculate the reinsurer's expected payment per loss. "
         "(b) Calculate the insurer's expected retained amount per loss. (c) Next "
         "year all losses increase by 10%, the retention stays at 1,000. Calculate "
         "the percentage increase in the reinsurer's expected payment per loss.")
steps([f"(a) E[(X − 1000)<sub>+</sub>] = E[X] − E[X ∧ 1000]. For the exponential "
       f"this simplifies to θ e<super>−d/θ</super> = 2000 e<super>−0.5</super> = "
       f"<b>{num(q4_a, 2)}</b>.",
       f"(b) Retained = E[X ∧ 1000] = 2000(1 − e<super>−0.5</super>) = "
       f"<b>{num(q4_b, 2)}</b>. Check: {num(q4_a, 2)} + {num(q4_b, 2)} = 2000 = E[X].",
       f"(c) Inflated losses are exponential with θ = 2200. New payment = "
       f"2200 e<super>−1000/2200</super> = {num(q4_c, 2)}. Increase = "
       f"{num(q4_c, 2)}/{num(q4_a, 2)} − 1 = <b>{q4_inc * 100:.2f}%</b>."])
answer(f"(a) {num(q4_a, 2)}  (b) {num(q4_b, 2)}  (c) {q4_inc * 100:.2f}%, "
       f"more than the 10% inflation: excess layers are leveraged.")

# ---- Q5
a5, t5, d5, u5 = 3, 2000, 500, 1500
l5_d = par_lev(a5, t5, d5)
l5_u = par_lev(a5, t5, u5)
q5_pl = l5_u - l5_d
s5 = (t5 / (t5 + d5)) ** a5
q5_pp = q5_pl / s5
question("Question 5 (a layer with Pareto losses).",
         "Losses follow a Pareto distribution with α = 3 and θ = 2,000. A reinsurer "
         "writes the layer \"1,000 xs 500\". Calculate (a) the expected reinsurer "
         "payment per loss and (b) the expected reinsurer payment per payment "
         "(i.e. given the layer is hit).",
         ["(a) 313  (b) 425", "(a) 313  (b) 612", "(a) 360  (b) 612",
          "(a) 673  (b) 1,315", "(a) 640  (b) 1,250"])
steps(["The layer runs from d = 500 to u = 1,500. Per loss: E[X ∧ 1500] − E[X ∧ 500].",
       f"E[X ∧ 500] = 2000/2 · [1 − (2000/2500)<super>2</super>] = 1000(1 − 0.64) = "
       f"{num(l5_d, 2)}.",
       f"E[X ∧ 1500] = 1000 · [1 − (2000/3500)<super>2</super>] = {num(l5_u, 2)}.",
       f"(a) Per loss = {num(l5_u, 2)} − {num(l5_d, 2)} = <b>{num(q5_pl, 2)}</b>.",
       f"(b) The layer is hit only if X &gt; 500. S(500) = (2000/2500)<super>3</super> "
       f"= {s5:.3f}. Per payment = {num(q5_pl, 2)}/{s5:.3f} = <b>{num(q5_pp, 2)}</b>."])
answer(f"<b>(B)</b>  per loss {num(q5_pl, 2)}; per payment {num(q5_pp, 2)}.")

# ---- Q6
lam6 = 1.5
f6 = {1: 2 / 3, 2: 1 / 3}
p = [math.exp(-lam6)]
for k in range(1, 3):
    p.append(lam6 / k * sum(j * f6.get(j, 0) * p[k - j] for j in range(1, k + 1)))
ES6 = lam6 * (1 * 2 / 3 + 2 * 1 / 3)
lev2 = 0 * p[0] + 1 * p[1] + 2 * (1 - p[0] - p[1])
q6 = ES6 - lev2
lev1 = 1 - p[0]
q6_1 = ES6 - lev1
q6_15 = 0.5 * q6_1 + 0.5 * q6
question("Question 6 (aggregate stop-loss, compound Poisson).",
         "The number of claims in a year is Poisson with mean 1.5. Claim sizes (in "
         "millions) are 1 with probability 2/3 and 2 with probability 1/3, "
         "independent of the number of claims. A stop-loss treaty pays the aggregate "
         "losses in excess of 2 (million). (a) Calculate the net stop-loss premium. "
         "(b) The reinsurer charges its net premium plus a 25% loading. Calculate "
         "the premium charged. (c) Calculate the net stop-loss premium if the "
         "retention were 1.5 instead.")
steps([f"E[X] = 1(2/3) + 2(1/3) = 4/3, so E[S] = 1.5 × 4/3 = {ES6:.4f}.",
       f"Need P(S = 0) and P(S = 1). P(S = 0) = e<super>−1.5</super> = {p[0]:.5f}. "
       f"S = 1 means exactly one claim of size 1: P(S = 1) = 1.5 e<super>−1.5</super> "
       f"× 2/3 = {p[1]:.5f}.",
       f"E[S ∧ 2] = 0·P(S=0) + 1·P(S=1) + 2·P(S ≥ 2) = {p[1]:.5f} + 2(1 − {p[0]:.5f} − "
       f"{p[1]:.5f}) = {lev2:.5f}.",
       f"(a) E[(S − 2)<sub>+</sub>] = {ES6:.4f} − {lev2:.5f} = <b>{q6:.4f}</b> million.",
       f"(b) Loaded premium = 1.25 × {q6:.4f} = <b>{1.25 * q6:.4f}</b> million.",
       f"(c) S has no mass between 1 and 2, so interpolate. E[(S − 1)<sub>+</sub>] = "
       f"E[S] − E[S ∧ 1] = {ES6:.4f} − (1 − {p[0]:.5f}) = {q6_1:.4f}. Halfway between: "
       f"(<font size=9>{q6_1:.4f} + {q6:.4f}</font>)/2 = <b>{q6_15:.4f}</b> million."])
answer(f"(a) {q6:.4f}M  (b) {1.25 * q6:.4f}M  (c) {q6_15:.4f}M")

# ---- Q7
b7, a7 = 1000, 0.5
EX7, VX7 = b7 / 2, b7 ** 2 / 12
target7 = a7 * EX7
d7 = b7 - math.sqrt(2 * b7 * target7)
lev7 = unif_lev(b7, d7)
var_qs7 = (1 - a7) ** 2 * VX7
var_xl7 = unif_lev2(b7, d7) - lev7 ** 2
question("Question 7 (quota share vs XL: which reduces variance more?).",
         "A loss X is uniformly distributed on (0, 1000). The insurer considers "
         "(i) a 50% quota share, or (ii) an excess of loss treaty with retention d "
         "chosen so that the reinsurer's expected payment equals that under (i). "
         "Calculate d and the variance of the insurer's retained loss under each "
         "option.")
steps([f"Quota share expected cession = 0.5 × E[X] = 0.5 × 500 = {target7:,.0f}.",
       f"For U(0, 1000): E[(X − d)<sub>+</sub>] = (1000 − d)<super>2</super>/2000. Set "
       f"= 250: (1000 − d)<super>2</super> = 500,000, so d = 1000 − √500,000 = "
       f"<b>{d7:.2f}</b>.",
       f"(i) Var(0.5X) = 0.25 × 1000<super>2</super>/12 = <b>{var_qs7:,.1f}</b>.",
       f"(ii) Retained = X ∧ d. E[X ∧ d] = d − d<super>2</super>/2000 = {lev7:.2f} "
       f"(as it must: 500 − 250). E[(X ∧ d)<super>2</super>] = d<super>2</super> − "
       f"d<super>3</super>/1500 = {unif_lev2(b7, d7):,.1f}. Var = "
       f"{unif_lev2(b7, d7):,.1f} − {lev7:.2f}<super>2</super> = <b>{var_xl7:,.1f}</b>."])
answer(f"d = {d7:.2f}. Var under quota share = {var_qs7:,.1f}; under XL = "
       f"{var_xl7:,.1f}. Same expected cession, but the retained variance under XL "
       f"is about {(1 - var_xl7 / var_qs7) * 100:.0f}% lower, as the theory in 3.5 "
       f"predicts.")

# ---- Q8
prem8, att8, lim8 = 10_000_000, 0.80, 0.20
q8_losses = [7_500_000, 9_300_000, 11_000_000]
q8_pay = [min(max(L - att8 * prem8, 0), lim8 * prem8) for L in q8_losses]
question("Question 8 (aggregate stop-loss on a loss ratio).",
         "Subject premium is 10,000,000. An aggregate stop-loss treaty pays losses "
         "in excess of an 80% loss ratio, up to a further 20% of premium. Calculate "
         "the reinsurer's payment if aggregate losses for the year are (a) 7.5M, "
         "(b) 9.3M, (c) 11M. In (c), what is the insurer's net loss ratio?")
steps(["Convert ratios to money: attachment = 80% × 10M = 8M; limit = 20% × 10M = 2M. "
       "So the treaty is \"2M xs 8M\" on the <i>annual total</i>.",
       f"(a) 7.5M &lt; 8M: pays <b>{money(q8_pay[0])}</b>.",
       f"(b) 9.3M − 8M = 1.3M (≤ 2M): pays <b>{money(q8_pay[1])}</b>.",
       f"(c) 11M − 8M = 3M, capped at 2M: pays <b>{money(q8_pay[2])}</b>. Net losses = "
       f"11M − 2M = 9M, net loss ratio = 9M/10M = <b>90%</b> (ignoring the cost of the "
       f"treaty)."])
answer(f"(a) 0  (b) {money(q8_pay[1])}  (c) {money(q8_pay[2])}; net loss ratio 90%.")

# ---- Q9
n9, sz9 = 30, 200_000
tot9 = n9 * sz9
q9_risk = n9 * min(max(sz9 - 500_000, 0), 500_000)
q9_cat = min(max(tot9 - q9_risk - 5_000_000, 0), 10_000_000)
question("Question 9 (per-risk vs catastrophe XL).",
         "A windstorm damages 30 insured homes, each with a loss of 200,000 (total "
         "6,000,000). The insurer has a per-risk XL \"500,000 xs 500,000\" and a "
         "catastrophe XL \"10,000,000 xs 5,000,000\" per occurrence, which applies "
         "after the per-risk treaty. Calculate the recovery from each treaty and "
         "the insurer's net loss.")
steps([f"Per-risk XL: each home's loss is 200,000 &lt; 500,000, so recovery = "
       f"<b>{money(q9_risk)}</b>. Per-risk cover cannot see that many risks were "
       f"hit at once.",
       f"Cat XL looks at the event total after per-risk recoveries: 6,000,000 − 0 = "
       f"6,000,000. Excess over 5,000,000 = <b>{money(q9_cat)}</b> (within the 10M limit).",
       f"Net loss = 6,000,000 − {money(q9_risk)} − {money(q9_cat)} = "
       f"<b>{money(tot9 - q9_risk - q9_cat)}</b>."])
answer(f"Per-risk: {money(q9_risk)}; cat: {money(q9_cat)}; net: "
       f"{money(tot9 - q9_risk - q9_cat)}. This is exactly why insurers need both.")

# ---- Q10
question("Question 10 (concepts: treaty vs facultative).",
         "Which of the following statements is true?",
         ["Under a facultative treaty the reinsurer must accept every policy in "
          "the class.",
          "Facultative reinsurance is negotiated separately for each individual "
          "risk.",
          "Quota share is an example of non-proportional reinsurance.",
          "The policyholder can claim directly from the reinsurer if the insurer "
          "becomes insolvent (in the absence of a special cut-through clause).",
          "Treaty reinsurance has a higher administrative cost per risk than "
          "facultative."])
steps(["(A) wrong: <i>facultative</i> means the reinsurer has the 'faculty' (option) "
       "to accept or reject each risk; 'automatic for the whole class' describes a "
       "treaty.",
       "(B) correct by definition.",
       "(C) wrong: quota share is proportional.",
       "(D) wrong: the policyholder's contract is only with the insurer.",
       "(E) wrong: it is the reverse; fac is costly because each risk is "
       "underwritten individually."])
answer("<b>(B)</b>")

# ---- Q11
question("Question 11 (concepts: reasons for reinsurance).",
         "Which of the following is <b>least</b> likely to be a reason for an "
         "insurer to purchase reinsurance?",
         ["To increase the size of policies it can write",
          "To reduce the volatility of its annual results",
          "To protect against a single catastrophic event",
          "To lower the long-run expected total cost of its claims plus reinsurance "
          "premiums",
          "To obtain surplus relief through ceding commissions"])
steps(["(A), (B), (C), (E) are the classic reasons: capacity, stabilisation, "
       "catastrophe protection, surplus relief.",
       "(D): the reinsurer's premium includes its expenses and profit, so on "
       "average the insurer pays <i>more</i> in reinsurance premium than it recovers. "
       "Reinsurance raises expected cost in exchange for lower risk."])
answer("<b>(D)</b>")

# ---- Q12
L12, a12, d12, y12 = 400_000, 0.25, 100_000, 200_000
qs12 = a12 * L12
xl12_a = min(max((L12 - qs12) - d12, 0), y12)
net12_a = L12 - qs12 - xl12_a
xl12_b = min(max(L12 - d12, 0), y12)
qs12_b = a12 * (L12 - xl12_b)
net12_b = L12 - xl12_b - qs12_b
question("Question 12 (two treaties: order of application).",
         "An insurer has a 25% quota share and a per-risk XL \"200,000 xs "
         "100,000\". A single loss of 400,000 occurs. Calculate the insurer's net "
         "retained loss if (a) the quota share applies first and the XL protects "
         "the insurer's retained share, (b) the XL applies first and the quota "
         "share applies to the loss net of the XL recovery.")
steps([f"(a) QS first: QS pays 25% × 400,000 = {money(qs12)}; retained = "
       f"{money(L12 - qs12)}. XL on that: min(max({money(L12 - qs12)} − 100,000, 0), "
       f"200,000) = {money(xl12_a)}. Net = {money(L12 - qs12)} − {money(xl12_a)} = "
       f"<b>{money(net12_a)}</b>.",
       f"(b) XL first on the gross loss: min(400,000 − 100,000, 200,000) = "
       f"{money(xl12_b)}; remaining {money(L12 - xl12_b)}. QS takes 25%: "
       f"{money(qs12_b)}. Net = {money(L12 - xl12_b)} − {money(qs12_b)} = "
       f"<b>{money(net12_b)}</b>."])
answer(f"(a) {money(net12_a)}  (b) {money(net12_b)}. Same contracts, different "
       f"order, different answer: always check which treaty inures to which.")

# ---- Q13
lam13, th13, d13 = 5, 2000, 1000
v13 = math.exp(-d13 / th13)
q13_n = lam13 * v13
q13_pl = th13 * v13
q13_tot = lam13 * q13_pl
question("Question 13 (frequency of reinsurance payments).",
         "Losses occur according to a Poisson process with mean 5 per year; sizes "
         "are exponential with mean 2,000. An XL treaty has retention 1,000 and no "
         "limit. Calculate (a) the expected number of losses the reinsurer pays "
         "per year, (b) the expected amount per reinsurance payment, (c) the "
         "expected total annual reinsurance recovery.")
steps([f"(a) P(X &gt; 1000) = e<super>−0.5</super> = {v13:.5f}. The count of "
       f"reinsurer payments is Poisson(5 × {v13:.5f}) with mean <b>{q13_n:.4f}</b>.",
       "(b) Memoryless: given X &gt; 1000, X − 1000 is exponential with mean 2000. So "
       "the expected payment per payment is <b>2,000</b>.",
       f"(c) Total = {q13_n:.4f} × 2000 = <b>{num(q13_tot, 2)}</b>. Check via "
       f"per-loss: 5 × 2000 e<super>−0.5</super> = 5 × {num(q13_pl, 2)} = "
       f"{num(q13_tot, 2)}. ✓"])
answer(f"(a) {q13_n:.4f}  (b) 2,000  (c) {num(q13_tot, 2)}")

# ---- Q14
gp14, gl14, ge14, a14, cc14 = 1000, 650, 300, 0.5, 0.32
np14 = (1 - a14) * gp14
nl14 = (1 - a14) * gl14
comm14 = cc14 * a14 * gp14
ne14 = ge14 - comm14
question("Question 14 (quota share and the insurer's ratios).",
         "Gross premium 1,000, gross losses 650, the insurer's expenses 300 (all "
         "paid up front). The insurer enters a 50% quota share with a 32% ceding "
         "commission. Calculate the insurer's gross and net (a) loss ratio and "
         "(b) underwriting profit, and explain the effect on surplus.")
steps([f"Gross: loss ratio 650/1000 = 65%. Profit = 1000 − 650 − 300 = "
       f"{gp14 - gl14 - ge14}.",
       f"Net premium = {np14:,.0f}; net losses = {nl14:,.0f}; ceding commission = "
       f"32% × 500 = {comm14:,.0f}, which offsets expenses: net expenses = "
       f"300 − {comm14:,.0f} = {ne14:,.0f}.",
       f"Net loss ratio = {nl14:,.0f}/{np14:,.0f} = <b>{nl14 / np14 * 100:.0f}%</b> "
       f"(a quota share does not change the loss ratio). Net profit = "
       f"{np14:,.0f} − {nl14:,.0f} − {ne14:,.0f} = <b>{np14 - nl14 - ne14:,.0f}</b>.",
       f"Surplus effect: the insurer paid 300 of expenses but now gets {comm14:,.0f} "
       f"back <i>immediately</i>, while giving up premium that is earned over time. "
       f"That immediate cash is the surplus relief."])
answer(f"Loss ratio 65% gross and net. Profit {gp14 - gl14 - ge14} gross, "
       f"{np14 - nl14 - ne14:,.0f} net (the reinsurer earns 500 − 325 − 160 = 15).")

# ---- Q15
th15, d15, u15 = 1000, 500, 1500
lam15 = 3
q15_pl = exp_lev(th15, u15) - exp_lev(th15, d15)
q15_tot = lam15 * q15_pl
question("Question 15 (layer with a compound Poisson portfolio).",
         "Claims occur at a Poisson rate of 3 per year with exponential severity, "
         "mean 1,000. The reinsurer writes \"1,000 xs 500\" per claim. Calculate "
         "the reinsurer's expected annual payments.",
         ["1,030", "1,150", "1,213", "1,820", "3,000"])
steps(["Per loss: E[X ∧ 1500] − E[X ∧ 500] = 1000(1 − e<super>−1.5</super>) − "
       "1000(1 − e<super>−0.5</super>) = 1000(e<super>−0.5</super> − e<super>−1.5</super>).",
       f"= 1000({math.exp(-0.5):.5f} − {math.exp(-1.5):.5f}) = {num(q15_pl, 2)}.",
       f"Annual = 3 × {num(q15_pl, 2)} = <b>{num(q15_tot, 2)}</b>."])
answer(f"<b>(B)</b> {num(q15_tot, 2)}")

# ---- Q16
a16, t16, d16, r16 = 2, 3000, 2000, 0.05
pre16 = t16 / (a16 - 1) - par_lev(a16, t16, d16)
post16 = t16 * (1 + r16) / (a16 - 1) - par_lev(a16, t16 * (1 + r16), d16)
ins_pre = par_lev(a16, t16, d16)
ins_post = par_lev(a16, t16 * (1 + r16), d16)
question("Question 16 (inflation splits unevenly).",
         "Losses are Pareto with α = 2, θ = 3,000. An XL treaty has retention 2,000 "
         "and no limit. Losses inflate uniformly by 5%; the retention is unchanged. "
         "Calculate the percentage change in (a) the insurer's expected retained "
         "loss and (b) the reinsurer's expected payment, per loss.")
steps([f"Before: E[X] = 3000. E[X ∧ 2000] = 3000[1 − 3000/5000] = {num(ins_pre, 2)} "
       f"(insurer). Reinsurer = 3000 − {num(ins_pre, 2)} = {num(pre16, 2)}.",
       f"After: θ = 3150, E[X] = 3150. E[X ∧ 2000] = 3150[1 − 3150/5150] = "
       f"{num(ins_post, 2)}. Reinsurer = 3150 − {num(ins_post, 2)} = {num(post16, 2)}.",
       f"(a) Insurer: {num(ins_post, 2)}/{num(ins_pre, 2)} − 1 = "
       f"<b>{(ins_post / ins_pre - 1) * 100:.2f}%</b>.  (b) Reinsurer: "
       f"{num(post16, 2)}/{num(pre16, 2)} − 1 = <b>{(post16 / pre16 - 1) * 100:.2f}%</b>."])
answer(f"Total losses grow 5%. The retained part grows only "
       f"{(ins_post / ins_pre - 1) * 100:.2f}% while the excess part grows "
       f"{(post16 / pre16 - 1) * 100:.2f}%.")

# ================================================================ PART 6
H1("Part 6. Practice questions (answers at the end)")
P("Try all of these before checking. Each one mirrors a solved question in Part 5.")
practice = [
    ("A 30% quota share applies. A loss of 80,000 occurs. How much does the "
     "reinsurer pay?"),
    ("A surplus treaty has a retention line of 50,000 and 9 lines. A policy has an "
     "amount of insurance of 400,000 and a loss of 120,000. How much does the "
     "reinsurer pay?"),
    ("A surplus treaty has a retention line of 50,000 and 5 lines. A policy has an "
     "amount of insurance of 500,000 and a loss of 200,000. Split the loss between "
     "insurer and reinsurer."),
    ("Per-risk XL \"750,000 xs 250,000\". A loss of 1,200,000 occurs. How much does "
     "each party pay?"),
    ("Losses are exponential with mean 5,000; XL retention 2,000, no limit. "
     "Find the reinsurer's expected payment per loss and per payment."),
    ("Losses are Pareto with α = 2, θ = 3,000. Find the expected payment per loss "
     "for (a) unlimited XL above 1,000 and (b) the layer \"4,000 xs 1,000\"."),
    ("Aggregate losses S take values 0, 1, 2, 3, 4 with probabilities 0.50, 0.20, "
     "0.15, 0.10, 0.05. Find E[(S − 2)<sub>+</sub>] and E[(S − 2.5)<sub>+</sub>]."),
    ("A 40% quota share applies first, then an XL \"300,000 xs 200,000\" on the "
     "insurer's retention. A loss of 1,000,000 occurs. Find the insurer's net loss."),
    ("X ~ U(0, 2000). Compare the variance of the insurer's retained loss under a "
     "25% quota share and under an XL with the same expected cession."),
    ("True or false: (i) a stop-loss treaty applies its retention to each claim "
     "separately; (ii) a retrocession is reinsurance bought by a reinsurer; (iii) "
     "under a quota share the insurer's net loss ratio equals its gross loss ratio."),
    ("Claims are Poisson with mean 3 per year, exponential severity mean 1,000 "
     "(same as Q15). Find the expected number of claims that reach the layer "
     "\"1,000 xs 500\" per year."),
    ("Gross premium is 2,000,000. A 60% quota share has a 35% ceding commission. "
     "Find the net cash the insurer pays the reinsurer."),
]
for i, qtxt in enumerate(practice, 1):
    question(f"P{i}.", qtxt)

# practice answers (computed)
pa = {}
pa[1] = f"0.30 × 80,000 = <b>{money(0.3 * 80_000)}</b>."
c_p2 = min(max(400_000 - 50_000, 0), 9 * 50_000) / 400_000
pa[2] = (f"Ceded insurance = min(350,000, 450,000) = 350,000; c = 0.875; reinsurer "
         f"pays <b>{money(c_p2 * 120_000)}</b>.")
c_p3 = min(max(500_000 - 50_000, 0), 5 * 50_000) / 500_000
pa[3] = (f"Capacity 250,000 &lt; 450,000, so c = 250,000/500,000 = {c_p3:.2f}. Reinsurer "
         f"<b>{money(c_p3 * 200_000)}</b>, insurer <b>{money((1 - c_p3) * 200_000)}</b>.")
re_p4 = min(max(1_200_000 - 250_000, 0), 750_000)
pa[4] = (f"Reinsurer {money(re_p4)} (full limit); insurer 250,000 + 200,000 = "
         f"<b>{money(1_200_000 - re_p4)}</b>.")
pa[5] = (f"Per loss 5000 e<super>−0.4</super> = <b>{num(5000 * math.exp(-0.4), 2)}</b>; "
         f"per payment <b>5,000</b> (memoryless).")
p6a = 3000 - par_lev(2, 3000, 1000)
p6b = par_lev(2, 3000, 5000) - par_lev(2, 3000, 1000)
pa[6] = (f"E[X] = 3000, E[X ∧ 1000] = {num(par_lev(2, 3000, 1000), 0)}, "
         f"E[X ∧ 5000] = {num(par_lev(2, 3000, 5000), 0)}. (a) <b>{num(p6a, 0)}</b> "
         f"(b) <b>{num(p6b, 0)}</b>.")
probs7 = {0: 0.5, 1: 0.2, 2: 0.15, 3: 0.1, 4: 0.05}
sl = lambda dd: sum(max(s - dd, 0) * pr for s, pr in probs7.items())
pa[7] = (f"E[(S−2)<sub>+</sub>] = 1(0.10) + 2(0.05) = <b>{sl(2):.3f}</b>; "
         f"E[(S−2.5)<sub>+</sub>] = 0.5(0.10) + 1.5(0.05) = <b>{sl(2.5):.3f}</b> "
         f"(same as interpolating between {sl(2):.3f} and {sl(3):.3f}).")
ret8 = 0.6 * 1_000_000
xl8 = min(max(ret8 - 200_000, 0), 300_000)
pa[8] = (f"QS cedes 400,000, retained {money(ret8)}; XL pays min(400,000, 300,000) = "
         f"{money(xl8)}; net <b>{money(ret8 - xl8)}</b>.")
d9 = 2000 - math.sqrt(2 * 2000 * 250)
v9_qs = 0.75 ** 2 * 2000 ** 2 / 12
v9_xl = unif_lev2(2000, d9) - unif_lev(2000, d9) ** 2
pa[9] = (f"Expected cession 250, so (2000 − d)<super>2</super>/4000 = 250, d = "
         f"{d9:,.0f}. Var(QS) = 0.5625 × 2000<super>2</super>/12 = <b>{v9_qs:,.0f}</b>; "
         f"Var(X ∧ 1000) = {unif_lev2(2000, d9):,.1f} − {unif_lev(2000, d9):,.0f}"
         f"<super>2</super> = <b>{v9_xl:,.1f}</b>. XL is lower.")
pa[10] = ("(i) False: stop-loss applies to the <i>aggregate</i>. (ii) True. (iii) True "
          "(premium and losses are cut by the same %; only expenses change via the "
          "ceding commission).")
pa[11] = (f"Poisson thinning: 3 × P(X &gt; 500) = 3e<super>−0.5</super> = "
          f"<b>{3 * math.exp(-0.5):.4f}</b>.")
pa[12] = (f"Ceded premium 1,200,000; commission 35% × 1,200,000 = 420,000; net "
          f"<b>{money(1_200_000 - 420_000)}</b>.")

story.append(PageBreak())
P("Answers to the practice questions", "h2")
for i in range(1, len(practice) + 1):
    P(f"<b>P{i}.</b> {pa[i]}", "step")

# ================================================================ PART 7
H1("Part 7. One-page cheat sheet")
table([
    ["Contract", "Who pays what on a loss X", "Remember"],
    ["Quota share a", "Reinsurer aX; insurer (1 − a)X",
     "Same % of premium and every loss; Var ↓ by (1 − a)<super>2</super>; no cap "
     "on big losses; good for capacity / surplus relief."],
    ["Surplus share (line R, n lines)",
     "c = min(max(L − R, 0), nR)/L; reinsurer cX",
     "Split by policy <b>limit</b>, applied to every loss on that policy."],
    ["Per-risk XL \"y xs d\"", "min((X − d)<sub>+</sub>, y); mean "
     "E[X ∧ (d+y)] − E[X ∧ d]",
     "Retention = deductible for the reinsurer; above d + y goes back to insurer."],
    ["Cat XL (per occurrence)", "Same formula on the <b>event total</b>",
     "Protects against many small claims from one event."],
    ["Stop-loss / aggregate XL", "(S − d)<sub>+</sub>; E = E[S] − E[S ∧ d]",
     "Retention on the <b>annual total</b>, often as a loss ratio. "
     "Interpolate between mass points."],
], [1.45 * inch, 2.35 * inch, 2.7 * inch])
formula([
    "E[(X − d)<sub>+</sub>] = E[X] − E[X ∧ d]       per payment: divide by S(d)",
    "Exponential: E[(X − d)<sub>+</sub>] = θe<super>−d/θ</super>;  per payment = θ",
    "Pareto: E[X ∧ d] = θ/(α−1)·[1 − (θ/(θ+d))<super>α−1</super>]",
    "Poisson(λ) losses → Poisson(λ·S(d)) reinsurance payments",
    "Inflation (1+r): scale θ by (1+r), keep d fixed → layer grows faster than r",
], title="Formulas")
table([
    ["Word", "Means"],
    ["Retention", "What the cedent keeps (or the attachment point in XL)"],
    ["Ceding commission", "% of <b>ceded</b> premium paid back to the cedent"],
    ["Treaty / facultative", "Whole class automatically / one risk at a time"],
    ["Inures to the benefit of", "Applies first; its recovery is removed before the other treaty"],
], [1.8 * inch, 4.7 * inch])
trap(["(1) Surplus share: never subtract the retention from the <b>loss</b>. "
      "(2) Ceding commission × <b>ceded</b> premium, not gross premium. "
      "(3) \"Per payment\" means divide by P(X &gt; d). (4) The retention does not "
      "inflate. (5) Check the order of treaties. (6) Reinsurance lowers risk, not "
      "expected cost."], title="Six traps to avoid")


# ---------------------------------------------------------------- doc
class Doc(BaseDocTemplate):
    def __init__(self, fn, **kw):
        super().__init__(fn, **kw)
        frame = Frame(self.leftMargin, self.bottomMargin, self.width,
                      self.height, id="f")
        self.addPageTemplates([PageTemplate("p", [frame], onPage=self.deco)])

    def deco(self, canv, doc):
        if doc.page == 1:
            return
        canv.saveState()
        canv.setFont("Body", 8)
        canv.setFillColor(GREY)
        canv.drawString(doc.leftMargin, 0.5 * inch, "Reinsurance for Exam FAM-S")
        canv.drawRightString(doc.leftMargin + doc.width, 0.5 * inch,
                             f"Page {doc.page}")
        canv.setStrokeColor(colors.HexColor("#CCCCCC"))
        canv.line(doc.leftMargin, 0.65 * inch, doc.leftMargin + doc.width,
                  0.65 * inch)
        canv.restoreState()

    def afterFlowable(self, flowable):
        if hasattr(flowable, "_toc"):
            level, text = flowable._toc
            key = f"h{id(flowable)}"
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text, key, level=level, closed=level > 0)
            self.notify("TOCEntry", (level, text, self.page, key))


def build():
    doc = Doc(str(OUT), pagesize=letter, leftMargin=inch, rightMargin=inch,
              topMargin=0.85 * inch, bottomMargin=0.9 * inch,
              title="Reinsurance for Exam FAM-S", author="Study guide",
              subject="Reinsurance: concepts, formulas and worked exam questions")
    doc.multiBuild(story)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
