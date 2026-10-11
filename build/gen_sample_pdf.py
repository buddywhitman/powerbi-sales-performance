"""Sample PDF of the paginated report: same layout/queries as the RDL, rendered with reportlab from live model data (Year=2024, Region=All, Category=All)."""
import json, os, datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend

B = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(B, "sample_data.json")))
OUT = os.path.join(os.path.dirname(B), "deliverables", "SalesPerformance_Monthly_sample.pdf")
NAVY = colors.HexColor("#1F3A5F")
W, H = letter
def n(v): return float(v)
def rows(name): return D[name]["rows"]
def money(v): return "${:,.0f}".format(n(v))
def sg(v): return ("-" if n(v) < 0 else "") + "${:,.0f}".format(abs(n(v)))
def pct(v): return "{:.1f}%".format(n(v) * 100)
def num(v): return "{:,.0f}".format(n(v))
def key(r, k):
    for kk in r:
        if kk.endswith(k + "]") or kk == k:
            return r[kk]
    raise KeyError(k)

def style(ncols):
    return TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                       ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                       ("ALIGN", (1, 0), (-1, -1), "RIGHT"), ("LINEBELOW", (0, 1), (-1, -1), 0.4, colors.HexColor("#DDE3EC")),
                       ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F6F9")]),
                       ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)])

def table(c, x, y, data, widths):
    t = Table(data, colWidths=[w * inch for w in widths])
    t.setStyle(style(len(widths)))
    w, h = t.wrapOn(c, W, H)
    t.drawOn(c, x, y - h)
    return y - h

page = [0]
TOTAL = 2
def frame(c, params):
    c.setFillColor(NAVY); c.rect(0, H - 0.9 * inch, W, 0.9 * inch, stroke=0, fill=1)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 17); c.drawString(0.75 * inch, H - 0.5 * inch, "Monthly Sales Performance Report")
    c.setFont("Helvetica", 8.5); c.drawString(0.75 * inch, H - 0.72 * inch, "Confidential - for internal distribution")
    c.setFillColor(colors.HexColor("#6C7A89")); c.setFont("Helvetica", 8.5)
    c.drawString(0.75 * inch, H - 1.15 * inch, params)
    c.setStrokeColor(colors.HexColor("#DDE3EC")); c.line(0.75 * inch, 0.6 * inch, W - 0.75 * inch, 0.6 * inch)
    page[0] += 1
    c.drawRightString(W - 0.75 * inch, 0.4 * inch, "Page %d of %d     Generated %s" % (page[0], TOTAL, datetime.date.today().strftime("%d %b %Y")))
    c.setFillColor(NAVY)

def h2(c, y, t):
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 12); c.drawString(0.75 * inch, y, t)

c = canvas.Canvas(OUT, pagesize=letter)
c.setTitle("Monthly Sales Performance Report (sample)")
params = "Year: 2024   |   Region: All   |   Category: All   |   Prepared for: Executive Leadership"
# ---- page 1
frame(c, params)
k = rows("KPI")[0]
h2(c, H - 1.5 * inch, "Headline metrics")
y = table(c, 0.75 * inch, H - 1.62 * inch,
          [["Sales", "Target", "Attainment", "Gross profit", "Margin", "Orders", "Avg order"],
           [money(key(k, "Total Sales")), money(key(k, "Total Target")), pct(key(k, "Attainment")), money(key(k, "Gross Profit")), pct(key(k, "Margin")), num(key(k, "Orders")), money(key(k, "AOV"))]],
          [1, 1, 0.9, 1, 0.8, 0.7, 0.9])
h2(c, y - 0.35 * inch, "Performance by product category")
cat = rows("Category")
y = table(c, 0.75 * inch, y - 0.45 * inch, [["Category", "Sales", "Target", "Attainment", "Gross profit", "Margin", "Orders"]] +
          [[key(r, "Product Category"), money(key(r, "Total Sales")), money(key(r, "Total Target")), pct(key(r, "Attainment")), money(key(r, "Gross Profit")), pct(key(r, "Margin")), num(key(r, "Orders"))] for r in cat],
          [1.5, 1, 1, 0.9, 1, 0.8, 0.8])
h2(c, y - 0.35 * inch, "Performance by region")
reg = rows("Region")
y = table(c, 0.75 * inch, y - 0.45 * inch, [["Region", "Sales", "Target", "Variance", "Attainment", "Orders"]] +
          [[key(r, "Region"), money(key(r, "Total Sales")), money(key(r, "Total Target")), sg(key(r, "Variance")), pct(key(r, "Attainment")), num(key(r, "Orders"))] for r in reg],
          [1.5, 1.2, 1.2, 1.2, 1, 0.9])
c.showPage()
# ---- page 2
frame(c, params)
h2(c, H - 1.5 * inch, "Quarterly trend")
q = rows("Quarter")
d = Drawing(6.9 * inch, 3.4 * inch)
ch = VerticalBarChart(); ch.x, ch.y, ch.width, ch.height = 55, 40, 440, 220
ch.data = [[n(key(r, "Total Sales")) for r in q], [n(key(r, "Total Target")) for r in q]]
ch.categoryAxis.categoryNames = ["%s %s" % (key(r, "Year"), key(r, "Quarter")) for r in q]
ch.bars[0].fillColor = NAVY; ch.bars[1].fillColor = colors.HexColor("#F4A261")
ch.valueAxis.labelTextFormat = lambda v: "${:,.0f}K".format(v / 1000); ch.valueAxis.valueMin = 0
ch.categoryAxis.labels.fontSize = 8; ch.valueAxis.labels.fontSize = 8
d.add(ch)
lg = Legend(); lg.x, lg.y = 200, 8; lg.fontSize = 8; lg.alignment = "right"; lg.colorNamePairs = [(NAVY, "Sales"), (colors.HexColor("#F4A261"), "Target")]
d.add(lg)
d.drawOn(c, 0.75 * inch, H - 5.2 * inch)
c.setFillColor(colors.HexColor("#6C7A89")); c.setFont("Helvetica-Oblique", 8)
c.drawString(0.75 * inch, H - 5.95 * inch, "Sample rendering produced from the semantic model with the same DAX datasets as SalesPerformance_Monthly.rdl (Year = 2024).")
c.showPage(); c.save()
print("sample pdf", OUT)
