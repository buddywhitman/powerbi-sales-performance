"""Generates PBIR pages, visuals, bookmarks, theme for SalesPerformance.Report.
Run: python -I build/gen_report.py   (deterministic ids; safe to re-run)"""
import os, json, shutil, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REP = os.path.join(ROOT, "SalesPerformance.Report")
DEF = os.path.join(REP, "definition")
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/"
VC = SCHEMA + "visualContainer/2.9.0/schema.json"
MOB = SCHEMA + "visualContainerMobileState/2.7.0/schema.json"

NAVY, TEAL, AMBER, ORANGE, RED, SLATE, PURPLE, SKY = "#1F3A5F", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51", "#6C7A89", "#7B5EA7", "#5DA9E9"
BG, INK = "#F4F6F9", "#1B2A3B"

def hid(s):
    return hashlib.sha1(s.encode()).hexdigest()[:20]

def wj(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2)

def L(v):  # literal expr
    return {"expr": {"Literal": {"Value": v}}}
def S(v): return L("'%s'" % v)
def B(v): return L("true" if v else "false")
def D(v): return L("%sD" % v)
def color(hexv): return {"solid": {"color": {"expr": {"Literal": {"Value": "'%s'" % hexv}}}}}

def col(t, c): return {"Column": {"Expression": {"SourceRef": {"Entity": t}}, "Property": c}}
def mea(t, m): return {"Measure": {"Expression": {"SourceRef": {"Entity": t}}, "Property": m}}
def hier(t, h, lvl):
    return {"HierarchyLevel": {"Expression": {"Hierarchy": {"Expression": {"SourceRef": {"Entity": t}}, "Hierarchy": h}}, "Level": lvl}}

def P(field, ref, native, active=None):
    d = {"field": field, "queryRef": ref, "nativeQueryRef": native}
    if active is not None:
        d["active"] = active
    return d
def PC(t, c, active=None): return P(col(t, c), f"{t}.{c}", c, active)
def PM(m, t="Sales"): return P(mea(t, m), f"{t}.{m}", m)
def PH(t, h, lvl, active): return P(hier(t, h, lvl), f"{t}.{h}.{lvl}", lvl, active)

def q(**roles):
    return {"queryState": {k: ({"projections": v} if isinstance(v, list) else v) for k, v in roles.items()}}

def title_vco(text=None, measure=None, size=12):
    t = {"show": B(True), "fontSize": D(size), "fontColor": color(NAVY), "bold": B(True), "alignment": S("left")}
    if measure:
        t["text"] = {"expr": mea("Sales", measure)}
    else:
        t["text"] = S(text)
    return t

class Page:
    def __init__(self, key, name, display, **kw):
        self.key, self.name, self.display, self.kw = key, name, display, kw
        self.visuals = []  # (name, dict, mobile or None)
        self.n = 0
    def add(self, kind, x, y, w, h, visual, vco=None, mobile=None, hidden=False, extra=None, top=None):
        self.n += 1
        name = hid(f"{self.key}-{kind}-{self.n}")
        v = {"$schema": VC, "name": name,
             "position": {"x": x, "y": y, "z": 1000 + self.n * 10, "height": h, "width": w, "tabOrder": 1000 + self.n * 10},
             "visual": visual}
        if vco:
            visual.setdefault("visualContainerObjects", {}).update(vco)
        if extra:
            visual.update(extra)
        if hidden:
            v["isHidden"] = True
        self.visuals.append((name, v, mobile))
        return name

PAGES = {
    "overview": ("a1b2c3d4e5f60718293a", "Sales Overview"),
    "product": ("b2c3d4e5f60718293a4b", "Product Analysis"),
    "customer": ("c3d4e5f60718293a4b5c", "Customer Analysis"),
    "geo": ("d4e5f60718293a4b5c6d", "Geographic Performance"),
    "scenario": ("e5f60718293a4b5c6d7e", "Scenario Planner"),
    "rep": ("f60718293a4b5c6d7e8f", "Sales Rep Detail"),
}
NAV = [("overview", "Overview"), ("product", "Products"), ("customer", "Customers"), ("geo", "Geography"), ("scenario", "Scenario")]

# ------------------------------------------------------------------ helpers
def textbox(page, x, y, w, h, text, size, bold=False, colr="#FFFFFF", align="left"):
    style = {"fontFamily": "Segoe UI Semibold" if bold else "Segoe UI", "fontSize": f"{size}px", "color": colr}
    page.add("tb", x, y, w, h, {
        "visualType": "textbox",
        "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": text, "textStyle": style}], "horizontalTextAlignment": align}]}}]},
        "visualContainerObjects": {"background": [{"properties": {"show": B(False)}}], "border": [{"properties": {"show": B(False)}}], "padding": [{"properties": {"top": D(0), "bottom": D(0), "left": D(0), "right": D(0)}}]}})

def header(page, title, subtitle, active):
    page.add("hdr", 0, 0, 1280, 64, {
        "visualType": "basicShape",
        "objects": {"fill": [{"properties": {"fillColor": color(NAVY), "transparency": D(0)}}]},
        "visualContainerObjects": {"background": [{"properties": {"show": B(False)}}], "border": [{"properties": {"show": B(False)}}], "padding": [{"properties": {"top": D(0), "bottom": D(0), "left": D(0), "right": D(0)}}]}})
    textbox(page, 24, 4, 470, 36, title, 22, True)
    page.add("sub", 24, 38, 470, 22, {
        "visualType": "textbox",
        "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": {"propertyIdentifier": {"objectName": "values", "propertyName": "expr"}, "selector": {"id": "Value 1"}}, "textStyle": {"fontFamily": "Segoe UI", "fontSize": "11px", "color": "#B8C7DB"}}], "horizontalTextAlignment": "left"}]}}],
                    "values": [{"properties": {"expr": {"expr": mea("Sales", "Selection Context")}}, "selector": {"id": "Value 1"}}]},
        "visualContainerObjects": {"background": [{"properties": {"show": B(False)}}], "border": [{"properties": {"show": B(False)}}], "padding": [{"properties": {"top": D(0), "bottom": D(0), "left": D(0), "right": D(0)}}]}}) if False else None
    # static subtitle (dynamic context is shown in chart titles)
    textbox(page, 24, 40, 470, 22, subtitle, 11, False, "#B8C7DB")
    x = 540
    for key, label in NAV:
        btn(page, x, 10, 138, 44, label, "page", PAGES[key][0], fill=TEAL if key == active else "#2C4F7C")
        x += 146

def btn(page, x, y, w, h, label, kind, target, fill="#2C4F7C", size=11, fontc="#FFFFFF", tooltip=None):
    link = {"show": B(True), "type": S({"page": "PageNavigation", "bookmark": "Bookmark", "back": "Back"}[kind])}
    if kind == "page":
        link["navigationSection"] = S(target)
    elif kind == "bookmark":
        link["bookmark"] = S(target)
    link["tooltip"] = S(tooltip or label)
    page.add("btn", x, y, w, h, {
        "visualType": "actionButton",
        "objects": {
            "text": [{"properties": {"show": B(True)}},
                     {"properties": {"text": S(label), "fontSize": D(size), "fontColor": color(fontc), "horizontalAlignment": S("center")}, "selector": {"id": "default"}}],
            "icon": [{"properties": {"show": B(False)}},
                     {"properties": {"shapeType": S("rightArrow"), "placement": S("left")}, "selector": {"id": "default"}}],
            "fill": [{"properties": {"show": B(True)}},
                     {"properties": {"fillColor": color(fill)}, "selector": {"id": "default"}}],
            "outline": [{"properties": {"show": B(False)}}],
            "shape": [{"properties": {"tileShape": S("rectangleRounded"), "roundEdge": L("6L")}},
                      {"properties": {"tileShape": S("rectangleRounded")}, "selector": {"id": "default"}}]},
        "visualContainerObjects": {"background": [{"properties": {"show": B(False)}}], "border": [{"properties": {"show": B(False)}}],
                                   "padding": [{"properties": {"top": D(0), "bottom": D(0), "left": D(0), "right": D(0)}}],
                                   "visualLink": [{"properties": link}]},
        "drillFilterOtherVisuals": True}, extra=None)
    return page.visuals[-1][0]

def default_filter(table, column, value):
    return {"filter": {"Version": 2, "From": [{"Name": "p", "Entity": table, "Type": 0}],
            "Where": [{"Condition": {"In": {"Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "p"}}, "Property": column}}],
                                            "Values": [[{"Literal": {"Value": "'" + value + "'"}}]]}}}]}}

def slicer(page, x, y, w, entity, column, label, mode="Dropdown", sync=None, fieldq=None, default=None):
    vis = {
        "visualType": "slicer",
        "query": q(Values=[fieldq or PC(entity, column)]),
        "objects": {"data": [{"properties": {"mode": S(mode)}}],
                    "header": [{"properties": {"show": B(True), "text": S(label), "textSize": D(10), "fontColor": color(SLATE), "bold": B(True)}}]},
        "visualContainerObjects": {
            "background": [{"properties": {"show": B(True), "color": color("#FFFFFF"), "transparency": D(0)}}],
            "border": [{"properties": {"show": B(True), "color": color("#DDE3EC"), "radius": D(6)}}],
            "padding": [{"properties": {"top": D(0), "bottom": D(0), "left": D(8), "right": D(8)}}]}}
    if default:
        vis["objects"]["general"] = [{"properties": {"filter": default_filter(entity, column, default)}}]
        vis["objects"]["selection"] = [{"properties": {"singleSelect": B(True), "selectAllCheckboxEnabled": B(False)}}]
    if sync:
        vis["syncGroup"] = {"groupName": sync, "fieldChanges": True, "filterChanges": True}
    return page.add("slc", x, y, w, 76, vis)

def slicer_row(page, specs, y=70):
    n = len(specs)
    gap = 12
    w = (1232 - gap * (n - 1)) // n
    x = 24
    for s in specs:
        slicer(page, x, y, w, *s[:3], **(s[3] if len(s) > 3 else {}))
        x += w + gap

def kpi(page, x, y, w, h, measures, mobile=None):
    return page.add("kpi", x, y, w, h, {
        "visualType": "cardVisual",
        "query": q(Data=[PM(m) for m in measures]),
        "objects": {"value": [{"properties": {"fontSize": D(24), "fontColor": color(NAVY), "bold": B(True), "labelDisplayUnits": L("1D"), "labelPrecision": D(0)}, "selector": {"id": "default"}}],
                    "label": [{"properties": {"fontSize": D(11), "fontColor": color(SLATE)}, "selector": {"id": "default"}}],
                    "layout": [{"properties": {"paddingUniform": D(0)}, "selector": {"id": "default"}}]},
        "visualContainerObjects": {"padding": [{"properties": {"top": D(10), "bottom": D(10), "left": D(14), "right": D(14)}}]}}, mobile=mobile)

def chart(page, vtype, x, y, w, h, roles, title=None, tmeasure=None, objects=None, mobile=None, extra_q=None, hidden=False, sort=None):
    qs = q(**roles)
    if sort:
        qs["sortDefinition"] = {"sort": [{"field": sort, "direction": "Descending"}], "isDefaultSort": False}
    vis = {"visualType": vtype, "query": qs}
    if objects:
        vis["objects"] = objects
    return page.add(vtype, x, y, w, h, vis, vco={"title": [{"properties": title_vco(title, tmeasure)}]}, mobile=mobile, hidden=hidden)

def legend_bottom():
    return {"legend": [{"properties": {"show": B(True), "position": S("Bottom")}}]}

def labels_on(size=9):
    return {"labels": [{"properties": {"show": B(True), "fontSize": D(size)}}]}

# =================================================================== PAGES
pages = {k: Page(k, *PAGES[k]) for k in PAGES}

# ------------------------------------------------------------ 1 OVERVIEW
p = pages["overview"]
header(p, "Sales Performance", "Executive overview of sales vs target and budget", "overview")
slicer_row(p, [("Date", "Year", "Year", {"sync": "Year"}), ("Sales", "Region", "Region", {"sync": "Region"}),
               ("Sales", "Product Category", "Product Category"), ("Sales", "Channel", "Channel"),
               ("Sales", "Customer Segment", "Customer Segment")])
kpi_o = kpi(p, 24, 152, 1232, 92, ["Total Sales", "Target Attainment %", "Gross Margin %", "Orders", "Avg Order Value"],
            mobile={"position": {"x": 8, "y": 8, "width": 344, "height": 150}})
# view-toggle buttons (bookmarks added below)
BM_BTN_Y = 252
trend_name = None
trend_roles = dict(Category=[PH("Date", "Date Hierarchy", "Year", True), PH("Date", "Date Hierarchy", "Quarter", False), PH("Date", "Date Hierarchy", "Month", False)],
                   Y=[PM("Total Sales"), PM("Total Target"), PM("Total Budget")])
trend_objs = {**legend_bottom(),
              "dataPoint": [
                  {"properties": {"fill": color(NAVY)}, "selector": {"metadata": "Sales.Total Sales"}},
                  {"properties": {"fill": color(ORANGE)}, "selector": {"metadata": "Sales.Total Target"}},
                  {"properties": {"fill": color(SLATE)}, "selector": {"metadata": "Sales.Total Budget"}}]}
trend_name = chart(p, "lineChart", 24, 300, 620, 404, trend_roles, tmeasure="Title Sales Trend", objects=trend_objs,
                   mobile={"position": {"x": 8, "y": 166, "width": 344, "height": 260}})
table_name = p.add("tbl", 24, 300, 620, 404, {
    "visualType": "tableEx",
    "query": q(Values=[PC("Date", "Year"), PC("Date", "Quarter"), PM("Total Sales"), PM("Total Target"), PM("Target Attainment %"), PM("Sales YoY %")]),
    "objects": {"columnHeaders": [{"properties": {"fontColor": color("#FFFFFF"), "backColor": color(NAVY), "bold": B(True)}}]}},
    vco={"title": [{"properties": title_vco("Sales detail by period")}]}, hidden=True)
cat_name = chart(p, "clusteredColumnChart", 656, 300, 600, 196,
      dict(Category=[PH("Sales", "Product Hierarchy", "Product Category", True), PH("Sales", "Product Hierarchy", "Product Subcategory", False)],
           Y=[PM("Total Sales"), PM("Total Target")]),
      title="Sales vs Target by product (drill down for subcategory)",
      objects={**legend_bottom(), "dataPoint": [{"properties": {"fill": color(NAVY)}, "selector": {"metadata": "Sales.Total Sales"}}, {"properties": {"fill": color(ORANGE)}, "selector": {"metadata": "Sales.Total Target"}}]},
      mobile={"position": {"x": 8, "y": 434, "width": 344, "height": 240}})
wf_name = chart(p, "waterfallChart", 656, 504, 600, 200,
      dict(Category=[PC("Sales", "Region")], Y=[PM("Variance to Target")]),
      title="Variance to target by region", objects={"labels": [{"properties": {"show": B(True), "fontSize": D(9)}}]})

# ------------------------------------------------------------ 2 PRODUCT
p = pages["product"]
header(p, "Product Analysis", "What sells, at what margin and discount", "product")
slicer_row(p, [("Sales", "Product Category", "Product Category"), ("Sales", "Product Subcategory", "Subcategory"),
               ("Sales", "Channel", "Channel"), ("Metric Selector", "Metric Selector", "Metric (field parameter)", {"default": "Sales"}),
               ("View By", "View By", "View by (field parameter)", {"default": "Region"})])
kpi(p, 24, 152, 1232, 92, ["Total Sales", "Gross Profit", "Gross Margin %", "Units Sold", "Avg Discount %"])
# field-parameter explorer
view_cols = ["Region", "Product Category", "Customer Segment", "Channel", "Age Group", "Sales Stage"]
metrics = ["Total Sales", "Gross Profit", "Orders", "Units Sold", "Avg Order Value", "Target Attainment %"]
cat_proj = [PC("Sales", c) for c in view_cols]
y_proj = [PM(m) for m in metrics]
chart(p, "clusteredBarChart", 24, 252, 620, 236,
      {"Category": {"projections": cat_proj, "fieldParameters": [{"parameterExpr": col("View By", "View By"), "index": 0, "length": 6}]},
       "Y": {"projections": y_proj, "fieldParameters": [{"parameterExpr": col("Metric Selector", "Metric Selector"), "index": 0, "length": 6}]}},
      tmeasure="Title Explorer", objects={"labels": [{"properties": {"show": B(True), "fontSize": D(9)}}], "dataPoint": [{"properties": {"defaultColor": color(TEAL)}}]})
chart(p, "treemap", 24, 496, 620, 208,
      dict(Group=[PH("Sales", "Product Hierarchy", "Product Category", True)], Values=[PM("Total Sales")]),
      title="Sales mix: category share")
chart(p, "decompositionTreeVisual", 656, 252, 600, 452,
      dict(Analyze=[PM("Gross Profit")], ExplainBy=[PC("Sales", "Product Category"), PC("Sales", "Channel"), PC("Sales", "Customer Segment"), PC("Sales", "Region")]),
      title="What drives gross profit? (decomposition tree)")

# ------------------------------------------------------------ 3 CUSTOMER
p = pages["customer"]
header(p, "Customer Analysis", "Who buys, how satisfied they are, and what drives hitting target", "customer")
slicer_row(p, [("Date", "Year", "Year", {"sync": "Year"}), ("Sales", "Customer Segment", "Segment"), ("Sales", "Age Group", "Age group"),
               ("Sales", "Sales Stage", "Sales stage"), ("Sales", "Country", "Country")])
kpi(p, 24, 152, 1232, 92, ["Customers", "Orders", "Avg Order Value", "Avg Satisfaction", "Close Rate %"])
chart(p, "donutChart", 24, 252, 300, 214, dict(Category=[PC("Sales", "Customer Segment")], Y=[PM("Total Sales")]), title="Sales by segment", objects=legend_bottom())
chart(p, "funnel", 336, 252, 300, 214, dict(Category=[PC("Sales", "Sales Stage")], Y=[PM("Orders")]), title="Pipeline by sales stage")
chart(p, "scatterChart", 648, 252, 608, 214,
      dict(Category=[PC("Sales", "Sales Rep")], X=[PM("Avg Satisfaction")], Y=[PM("Gross Margin %")], Size=[PM("Total Sales")]),
      title="Reps: satisfaction vs margin (size = sales)")
chart(p, "keyDriversVisual", 24, 474, 620, 230,
      dict(Target=[PC("Sales", "Target Status")],  ExplainBy=[PC("Sales", "Customer Segment"), PC("Sales", "Age Group"), PC("Sales", "Channel"), PC("Sales", "Region"), PC("Sales", "Product Category"), PC("Sales", "Discount Band")]),
      title="Key influencers: what drives orders being on track (>=75% of target)? (AI)")
chart(p, "tableEx", 656, 474, 600, 230,
      dict(Values=[PC("Sales", "Sales Rep"), PM("Total Sales"), PM("Target Attainment %"), PM("Avg Satisfaction")]),
      title="Sales reps - right-click a rep to drill through",
      objects={"columnHeaders": [{"properties": {"fontColor": color("#FFFFFF"), "backColor": color(NAVY), "bold": B(True)}}]},
      sort=mea("Sales", "Total Sales"))

# ------------------------------------------------------------ 4 GEO
p = pages["geo"]
header(p, "Geographic Performance", "Regions and countries: where we win and where we lag", "geo")
slicer_row(p, [("Date", "Year", "Year", {"sync": "Year"}), ("Sales", "Region", "Region", {"sync": "Region"}),
               ("Sales", "Country", "Country"), ("Sales", "Product Category", "Product Category"), ("Sales", "Channel", "Channel")])
kpi(p, 24, 152, 1232, 92, ["Total Sales", "Total Target", "Variance to Target", "Target Attainment %", "Gross Margin %"])
chart(p, "treemap", 24, 252, 620, 452, dict(Group=[PH("Sales", "Geography Hierarchy", "Country", True)], Details=[PH("Sales", "Geography Hierarchy", "Region", True)], Values=[PM("Total Sales")]), title="Sales footprint: country and region")
chart(p, "clusteredBarChart", 656, 252, 600, 222,
      dict(Category=[PH("Sales", "Geography Hierarchy", "Region", True), PH("Sales", "Geography Hierarchy", "Country", False)],
           Y=[PM("Total Sales"), PM("Total Target")]),
      title="Sales vs target (drill down region to country)",
      objects={**legend_bottom(), "dataPoint": [{"properties": {"fill": color(NAVY)}, "selector": {"metadata": "Sales.Total Sales"}}, {"properties": {"fill": color(ORANGE)}, "selector": {"metadata": "Sales.Total Target"}}]})
chart(p, "pivotTable", 656, 482, 600, 222,
      dict(Rows=[PC("Sales", "Region")], Columns=[PC("Sales", "Product Category")], Values=[PM("Total Sales")]),
      title="Region x category sales matrix")

# ------------------------------------------------------------ 5 SCENARIO
p = pages["scenario"]
header(p, "Scenario Planner", "What-if: price, volume and cost inflation", "scenario")
slicer_row(p, [("Price Change", "Price Change", "Price change (what-if)"), ("Volume Change", "Volume Change", "Volume change (what-if)"),
               ("Cost Inflation", "Cost Inflation", "Cost inflation (what-if)"),
               ("Date", "Year", "Year", {"sync": "Year"}), ("Sales", "Region", "Region", {"sync": "Region"})])
textbox(p, 24, 148, 1232, 24, "", 1)  # placeholder removed below
p.visuals.pop()
p.add("scn", 24, 150, 1232, 26, {
    "visualType": "textbox",
    "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": {"propertyIdentifier": {"objectName": "values", "propertyName": "expr"}, "selector": {"id": "Value 1"}}, "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "13px", "color": NAVY}}], "horizontalTextAlignment": "left"}]}}],
                "values": [{"properties": {"expr": {"expr": mea("Sales", "Title Scenario")}}, "selector": {"id": "Value 1"}}]},
    "visualContainerObjects": {"background": [{"properties": {"show": B(False)}}], "border": [{"properties": {"show": B(False)}}], "padding": [{"properties": {"top": D(0), "bottom": D(0), "left": D(0), "right": D(0)}}]}})
kpi(p, 24, 182, 1232, 92, ["Scenario Sales", "Scenario Profit", "Scenario Margin %", "Scenario Sales Impact", "Scenario Profit Impact"])
chart(p, "clusteredColumnChart", 24, 284, 620, 420,
      dict(Category=[PC("Sales", "Product Category")], Y=[PM("Total Sales"), PM("Scenario Sales")]),
      title="Baseline vs scenario sales by category",
      objects={**legend_bottom(), "dataPoint": [{"properties": {"fill": color(SLATE)}, "selector": {"metadata": "Sales.Total Sales"}}, {"properties": {"fill": color(TEAL)}, "selector": {"metadata": "Sales.Scenario Sales"}}]})
chart(p, "clusteredBarChart", 656, 284, 600, 270,
      dict(Category=[PC("Sales", "Region")], Y=[PM("Gross Profit"), PM("Scenario Profit")]),
      title="Baseline vs scenario profit by region",
      objects={**legend_bottom(), "dataPoint": [{"properties": {"fill": color(SLATE)}, "selector": {"metadata": "Sales.Gross Profit"}}, {"properties": {"fill": color(TEAL)}, "selector": {"metadata": "Sales.Scenario Profit"}}]})
chart(p, "gauge", 656, 562, 600, 142, dict(Y=[PM("Scenario Target Attainment %")], TargetValue=[P(mea("Sales", "Total Target"), "Sales.Total Target", "Total Target")]) if False else dict(Y=[PM("Scenario Target Attainment %")]),
      title="Scenario attainment vs target (100% = on target)")

# ------------------------------------------------------------ 6 REP DETAIL (drillthrough)
p = pages["rep"]
p.kw["drill"] = True
p.add("hdr", 0, 0, 1280, 64, {"visualType": "basicShape",
      "objects": {"fill": [{"properties": {"fillColor": color(NAVY), "transparency": D(0)}}]},
      "visualContainerObjects": {"background": [{"properties": {"show": B(False)}}], "border": [{"properties": {"show": B(False)}}], "padding": [{"properties": {"top": D(0), "bottom": D(0), "left": D(0), "right": D(0)}}]}})
btn(p, 24, 12, 110, 40, "< Back", "back", None, fill=TEAL, tooltip="Return to previous page")
p.add("ttl", 150, 10, 800, 44, {
    "visualType": "textbox",
    "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": {"propertyIdentifier": {"objectName": "values", "propertyName": "expr"}, "selector": {"id": "Value 1"}}, "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "22px", "color": "#FFFFFF"}}], "horizontalTextAlignment": "left"}]}}],
                "values": [{"properties": {"expr": {"expr": mea("Sales", "Rep Detail Title")}}, "selector": {"id": "Value 1"}}]},
    "visualContainerObjects": {"background": [{"properties": {"show": B(False)}}], "border": [{"properties": {"show": B(False)}}], "padding": [{"properties": {"top": D(0), "bottom": D(0), "left": D(0), "right": D(0)}}]}})
kpi(p, 24, 80, 1232, 92, ["Total Sales", "Target Attainment %", "Gross Margin %", "Orders", "Avg Satisfaction"])
chart(p, "columnChart", 24, 184, 620, 250, dict(Category=[PH("Date", "Date Hierarchy", "Year", True), PH("Date", "Date Hierarchy", "Quarter", False)], Y=[PM("Total Sales"), PM("Total Target")]),
      title="Rep sales vs target over time", objects={**legend_bottom(), "dataPoint": [{"properties": {"fill": color(NAVY)}, "selector": {"metadata": "Sales.Total Sales"}}, {"properties": {"fill": color(ORANGE)}, "selector": {"metadata": "Sales.Total Target"}}]})
chart(p, "donutChart", 656, 184, 600, 250, dict(Category=[PC("Sales", "Product Category")], Y=[PM("Total Sales")]), title="Rep sales by category", objects=legend_bottom())
chart(p, "tableEx", 24, 446, 1232, 258,
      dict(Values=[PC("Sales", "Order ID"), PC("Sales", "Order Date"), PC("Sales", "Customer Name"), PC("Sales", "Product Category"), PC("Sales", "Sales Stage"), PC("Sales", "Sales Amount"), PC("Sales", "Target Amount")]),
      title="Order detail", objects={"columnHeaders": [{"properties": {"fontColor": color("#FFFFFF"), "backColor": color(NAVY), "bold": B(True)}}]})

# ------------------------------------------------------------ bookmark buttons on overview
ov = pages["overview"]
bm = {"chart": hid("bm-chart"), "table": hid("bm-table"), "reset": hid("bm-reset")}
btn(ov, 24, BM_BTN_Y, 120, 40, "Chart view", "bookmark", bm["chart"], fill=NAVY, size=10)
btn(ov, 152, BM_BTN_Y, 120, 40, "Table view", "bookmark", bm["table"], fill=NAVY, size=10)
btn(ov, 280, BM_BTN_Y, 140, 40, "Reset filters", "bookmark", bm["reset"], fill=SLATE, size=10)

# =================================================================== WRITE
if os.path.isdir(os.path.join(DEF, "pages")):
    shutil.rmtree(os.path.join(DEF, "pages"))
if os.path.isdir(os.path.join(DEF, "bookmarks")):
    shutil.rmtree(os.path.join(DEF, "bookmarks"))

order = ["overview", "product", "customer", "geo", "scenario", "rep"]
wj(os.path.join(DEF, "pages", "pages.json"), {"$schema": SCHEMA + "pagesMetadata/1.1.0/schema.json",
                                              "pageOrder": [PAGES[k][0] for k in order], "activePageName": PAGES["overview"][0]})
for k in order:
    pg = pages[k]
    pj = {"$schema": SCHEMA + "page/2.1.0/schema.json", "name": pg.name, "displayName": pg.display,
          "displayOption": "FitToPage", "height": 720, "width": 1280,
          "objects": {"background": [{"properties": {"color": color(BG), "transparency": D(0)}}],
                      "outspace": [{"properties": {"color": color(BG)}}]}}
    if pg.kw.get("drill"):
        fid = "Filter" + hid("rep-filter") + "abcd"
        fexpr = col("Sales", "Sales Rep")
        pj["filterConfig"] = {"filters": [{"name": fid, "field": fexpr, "type": "Categorical", "howCreated": "Drillthrough"}]}
        pj["pageBinding"] = {"name": "Pod", "type": "Drillthrough",
                             "parameters": [{"name": "Param_" + fid, "boundFilter": fid, "fieldExpr": fexpr}]}
    wj(os.path.join(DEF, "pages", pg.name, "page.json"), pj)
    for name, v, mob in pg.visuals:
        wj(os.path.join(DEF, "pages", pg.name, "visuals", name, "visual.json"), v)
        if mob:
            m = {"$schema": MOB, "position": dict(mob["position"], z=v["position"]["z"], tabOrder=v["position"]["tabOrder"])}
            wj(os.path.join(DEF, "pages", pg.name, "visuals", name, "mobile.json"), m)

# bookmarks: toggle chart/table, reset
opage = PAGES["overview"][0]
def bookmark(key, display, trend_vis, table_vis, data):
    targets = [trend_name, table_name]
    return {"$schema": SCHEMA + "bookmark/2.1.0/schema.json", "displayName": display, "name": bm[key],
            "options": {"targetVisualNames": targets, "suppressData": not data, "suppressDisplay": False,
                        "suppressActiveSection": True, "applyOnlyToTargetVisuals": False},
            "explorationState": {"version": "1.3", "activeSection": opage, "sections": {opage: {"visualContainers": {
                trend_name: {"singleVisual": {} if trend_vis else {"display": {"mode": "hidden"}}},
                table_name: {"singleVisual": {} if table_vis else {"display": {"mode": "hidden"}}}}}}}}
for key, disp, tv, tb, data in [("chart", "Chart view", True, False, False), ("table", "Table view", False, True, False), ("reset", "Reset filters", True, False, True)]:
    wj(os.path.join(DEF, "bookmarks", bm[key] + ".bookmark.json"), bookmark(key, disp, tv, tb, data))
wj(os.path.join(DEF, "bookmarks", "bookmarks.json"), {"$schema": SCHEMA + "bookmarksMetadata/1.0.0/schema.json", "items": [{"name": bm[k]} for k in ("chart", "table", "reset")]})

# ------------------------------------------------------------ theme
THEME_NAME = "SalesTheme-7c1d2e3f.json"
rr = os.path.join(REP, "StaticResources", "RegisteredResources")
os.makedirs(rr, exist_ok=True)
def vs(**kw): return kw
theme = {
    "name": THEME_NAME,
    "dataColors": [NAVY, TEAL, ORANGE, PURPLE, SKY, AMBER, RED, SLATE],
    "background": "#FFFFFF", "foreground": INK, "tableAccent": NAVY,
    "good": "#2E7D32", "neutral": "#F9A825", "bad": "#C62828", "maximum": NAVY, "center": "#F9A825", "minimum": "#E3E8EF",
    "textClasses": {
        "callout": {"fontSize": 24, "fontFace": "Segoe UI Semibold", "color": NAVY},
        "title": {"fontSize": 12, "fontFace": "Segoe UI Semibold", "color": NAVY},
        "header": {"fontSize": 11, "fontFace": "Segoe UI Semibold", "color": NAVY},
        "label": {"fontSize": 10, "fontFace": "Segoe UI", "color": SLATE}},
    "visualStyles": {"*": {"*": {
        "background": [{"show": True, "color": {"solid": {"color": "#FFFFFF"}}, "transparency": 0}],
        "border": [{"show": True, "color": {"solid": {"color": "#DDE3EC"}}, "radius": 6}],
        "padding": [{"top": 8, "bottom": 8, "left": 8, "right": 8}]}}}}
wj(os.path.join(rr, THEME_NAME), theme)

rp = os.path.join(DEF, "report.json")
rj = json.load(open(rp, encoding="utf-8"))
rj["themeCollection"]["customTheme"] = {"name": THEME_NAME, "reportVersionAtImport": {"visual": "2.11.0", "report": "3.4.0", "page": "2.3.1"}, "type": "RegisteredResources"}
rj["resourcePackages"] = [x for x in rj["resourcePackages"] if x["name"] != "RegisteredResources"]
rj["resourcePackages"].append({"name": "RegisteredResources", "type": "RegisteredResources", "items": [{"name": THEME_NAME, "path": THEME_NAME, "type": "CustomTheme"}]})
wj(rp, rj)
print("pages:", {k: len(v.visuals) for k, v in pages.items()})
