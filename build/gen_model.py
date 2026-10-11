"""Generates SalesPerformance.SemanticModel (TMDL) from dashboard.xlsx layout. Run: python -I build/gen_model.py"""
import os, json, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SM = os.path.join(ROOT, "SalesPerformance.SemanticModel")
DEF = os.path.join(SM, "definition")
TBL = os.path.join(DEF, "tables")
if os.path.isdir(SM):
    shutil.rmtree(SM)
os.makedirs(TBL)

def w(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)

w(os.path.join(SM, "definition.pbism"), json.dumps({
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
    "version": "4.2", "settings": {"qnaEnabled": True}}, indent=4))

w(os.path.join(DEF, "database.tmdl"),
  "database SalesPerformance\n\tcompatibilityLevel: 1702\n\tcompatibilityMode: powerBI\n\tlanguage: 1033\n")

XLSX = os.path.join(ROOT, "dashboard.xlsx")
w(os.path.join(DEF, "expressions.tmdl"),
  'expression SourcePath = "%s" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n'
  % XLSX)

T = "\t"

# ---------------------------------------------------------------- Sales table
# (source, name, dtype, format, summarize, hidden, sortBy, folder)
cols = [
    ("OrderID", "Order ID", "string", None, "none", False, None),
    ("Date", "Order Date", "dateTime", "dd-MMM-yyyy", "none", True, None),
    ("Month", "Month Name (Src)", "string", None, "none", True, None),
    ("MonthNumber", "Month Number (Src)", "int64", "0", "none", True, None),
    ("Region", "Region", "string", None, "none", False, None),
    ("ProductCategory", "Product Category", "string", None, "none", False, None),
    ("ProductSubcategory", "Product Subcategory", "string", None, "none", False, None),
    ("SalesAmount", "Sales Amount", "double", "$#,0.00", "none", False, None),
    ("Quantity", "Quantity", "int64", "#,0", "none", False, None),
    ("ProfitMargin", "Profit Margin Pct", "double", '0.0"%"', "none", False, None),
    ("CustomerAgeGroup", "Age Group", "string", None, "none", False, None),
    ("CustomerSegment", "Customer Segment", "string", None, "none", False, None),
    ("DiscountApplied", "Discount Pct", "double", '0.0"%"', "none", False, None),
    ("Target", "Target Amount", "double", "$#,0.00", "none", False, None),
    ("SalesStage", "Sales Stage", "string", None, "none", False, "Stage Order"),
    ("CategoryRank", "Category Rank", "int64", "0", "none", False, None),
    ("SalesDelta", "Sales Delta", "double", "$#,0.00", "none", False, None),
    ("Year", "Year (Src)", "int64", "0", "none", True, None),
    ("Quarter", "Quarter (Src)", "string", None, "none", True, None),
    ("BudgetAmount", "Budget Amount", "double", "$#,0.00", "none", False, None),
    ("Channel", "Channel", "string", None, "none", False, None),
    ("SquareFootage", "Store Sq Ft", "int64", "#,0", "none", False, None),
    ("CustSatScore", "Satisfaction Score", "int64", "0", "none", False, None),
    ("COGS", "COGS Amount", "double", "$#,0.00", "none", False, None),
    ("CustomerName", "Customer Name", "string", None, "none", False, None),
    ("SalesRep", "Sales Rep", "string", None, "none", False, None),
    ("Country", "Country", "string", None, "none", False, None),
    # added in Power Query
    ("TargetStatus", "Target Status", "string", None, "none", False, None),
    ("DiscountBand", "Discount Band", "string", None, "none", False, "Discount Band Order"),
    ("DiscountBandOrder", "Discount Band Order", "int64", "0", "none", True, None),
    ("StageOrder", "Stage Order", "int64", "0", "none", True, None),
]

m_types = {"string": "type text", "dateTime": "type date", "int64": "Int64.Type", "double": "type number"}
typed = ", ".join('{"%s", %s}' % (c[0], m_types[c[2]]) for c in cols[:27])

s = []
s.append("table Sales\n")

def measure(name, expr, fmt, folder, desc=None):
    out = ""
    if desc:
        out += f"{T}/// {desc}\n"
    q = f"'{name}'" if any(ch in name for ch in " -%#/()") else name
    if "\n" in expr:
        out += f"{T}measure {q} = ```\n"
        for ln in expr.split("\n"):
            out += f"{T*3}{ln}\n"
        out += f"{T*3}```\n"
    else:
        out += f"{T}measure {q} = {expr}\n"
    if fmt != "@":
        out += f"{T*2}formatString: {fmt}\n"
    out += f"{T*2}displayFolder: {folder}\n\n"
    return out

M = []
def add(name, expr, fmt, folder, desc=None):
    M.append(measure(name, expr, fmt, folder, desc))

# Core
add("Total Sales", "SUM(Sales[Sales Amount])", "$#,0", "1 Core", "Sum of order sales amount")
add("Total Target", "SUM(Sales[Target Amount])", "$#,0", "1 Core")
add("Total Budget", "SUM(Sales[Budget Amount])", "$#,0", "1 Core")
add("Total COGS", "SUM(Sales[COGS Amount])", "$#,0", "1 Core")
add("Gross Profit", "[Total Sales] - [Total COGS]", "$#,0", "1 Core", "Sales minus cost of goods sold")
add("Gross Margin %", "DIVIDE([Gross Profit], [Total Sales])", "0.0%", "1 Core")
add("Orders", "DISTINCTCOUNT(Sales[Order ID])", "#,0", "1 Core")
add("Units Sold", "SUM(Sales[Quantity])", "#,0", "1 Core")
add("Avg Order Value", "DIVIDE([Total Sales], [Orders])", "$#,0", "1 Core")
add("Customers", "DISTINCTCOUNT(Sales[Customer Name])", "#,0", "1 Core")
add("Avg Satisfaction", "AVERAGE(Sales[Satisfaction Score])", "0.0", "1 Core")
add("Avg Discount %", "DIVIDE(AVERAGE(Sales[Discount Pct]), 100)", "0.0%", "1 Core")
add("Avg Profit Margin %", "DIVIDE(AVERAGE(Sales[Profit Margin Pct]), 100)", "0.0%", "1 Core", "Order-level margin as reported in the source data")
# Performance vs plan
add("Target Attainment %", "DIVIDE([Total Sales], [Total Target])", "0.0%", "2 Performance")
add("Variance to Target", "[Total Sales] - [Total Target]", "$#,0;-$#,0", "2 Performance")
add("Variance to Budget", "[Total Sales] - [Total Budget]", "$#,0;-$#,0", "2 Performance")
add("Budget Attainment %", "DIVIDE([Total Sales], [Total Budget])", "0.0%", "2 Performance")
add("Orders On Track %", "DIVIDE(CALCULATE([Orders], Sales[Target Status] = \"On Track\"), [Orders])", "0.0%", "2 Performance", "Share of orders reaching at least 75% of their target")
add("Closed Sales", "CALCULATE([Total Sales], Sales[Sales Stage] = \"Closed\")", "$#,0", "2 Performance")
add("Close Rate %", "DIVIDE(CALCULATE([Orders], Sales[Sales Stage] = \"Closed\"), [Orders])", "0.0%", "2 Performance")
add("Target Status Color", "IF([Target Attainment %] >= 1, \"#2E7D32\", IF([Target Attainment %] >= 0.9, \"#F9A825\", \"#C62828\"))", "@", "2 Performance", "Hex color driven by attainment, used for conditional formatting")
# Time intelligence
add("Sales PY", "CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date]))", "$#,0", "3 Time Intelligence")
add("Sales YoY %", "DIVIDE([Total Sales] - [Sales PY], [Sales PY])", "+0.0%;-0.0%;0.0%", "3 Time Intelligence")
add("Sales YTD", "TOTALYTD([Total Sales], 'Date'[Date])", "$#,0", "3 Time Intelligence")
add("Sales Rolling 3M", "CALCULATE([Total Sales], DATESINPERIOD('Date'[Date], MAX('Date'[Date]), -3, MONTH))", "$#,0", "3 Time Intelligence")
# Dynamic text
add("Selection Context", """VAR r = IF(ISFILTERED(Sales[Region]), CONCATENATEX(VALUES(Sales[Region]), Sales[Region], ", "), "All regions")
VAR y = IF(ISFILTERED('Date'[Year]), CONCATENATEX(VALUES('Date'[Year]), 'Date'[Year], ", "), "2022-2024")
VAR c = IF(ISFILTERED(Sales[Product Category]), CONCATENATEX(VALUES(Sales[Product Category]), Sales[Product Category], ", "), "All categories")
RETURN y & "  |  " & r & "  |  " & c""", "@", "4 Dynamic Text", "Subtitle that echoes the active slicer context")
add("Title Sales Trend", """"Sales vs Target and Budget - " & IF(ISFILTERED('Date'[Year]), CONCATENATEX(VALUES('Date'[Year]), 'Date'[Year], ", "), "all years")""", "@", "4 Dynamic Text")
add("Title Top Performer", """VAR t = TOPN(1, ALLSELECTED(Sales[Region]), [Total Sales])
RETURN "Top region: " & MAXX(t, Sales[Region]) & " (" & FORMAT(CALCULATE([Total Sales], t), "$#,0") & ")" """.rstrip(), "@", "4 Dynamic Text")
add("Title Explorer", """SWITCH(SELECTEDVALUE('Metric Selector'[Metric Selector Order], 0), 0, "Sales", 1, "Gross Profit", 2, "Orders", 3, "Units Sold", 4, "Avg Order Value", 5, "Target Attainment", "Sales") & " by " & SWITCH(SELECTEDVALUE('View By'[View By Order], 0), 0, "Region", 1, "Product Category", 2, "Customer Segment", 3, "Channel", 4, "Age Group", 5, "Sales Stage", "Region")""", "@", "4 Dynamic Text", "Title that follows both field parameters")
add("Title Scenario", """"Scenario: price " & FORMAT([Price Change Value], "+0%;-0%;0%") & ", volume " & FORMAT([Volume Change Value], "+0%;-0%;0%") & ", cost inflation " & FORMAT([Cost Inflation Value], "+0%;-0%;0%")""", "@", "4 Dynamic Text")
add("Rep Detail Title", """"Sales rep profile: " & SELECTEDVALUE(Sales[Sales Rep], "All reps")""", "@", "4 Dynamic Text")
# Scenario
add("Scenario Sales", "[Total Sales] * (1 + [Price Change Value]) * (1 + [Volume Change Value])", "$#,0", "5 Scenario")
add("Scenario COGS", "[Total COGS] * (1 + [Volume Change Value]) * (1 + [Cost Inflation Value])", "$#,0", "5 Scenario")
add("Scenario Profit", "[Scenario Sales] - [Scenario COGS]", "$#,0", "5 Scenario")
add("Scenario Margin %", "DIVIDE([Scenario Profit], [Scenario Sales])", "0.0%", "5 Scenario")
add("Scenario Sales Impact", "[Scenario Sales] - [Total Sales]", "$#,0;-$#,0", "5 Scenario")
add("Scenario Profit Impact", "[Scenario Profit] - [Gross Profit]", "$#,0;-$#,0", "5 Scenario")
add("Scenario Target Attainment %", "DIVIDE([Scenario Sales], [Total Target])", "0.0%", "5 Scenario")

for mm in M:
    s.append(mm)

# columns
for src, name, dt, fmt, summ, hidden, sortby in cols:
    q = f"'{name}'" if any(ch in name for ch in " -%#/()") else name
    s.append(f"{T}column {q}\n{T*2}dataType: {dt}\n")
    if fmt:
        s.append(f"{T*2}formatString: {fmt}\n")
    if hidden:
        s.append(f"{T*2}isHidden\n")
    if sortby:
        s.append(f"{T*2}sortByColumn: '{sortby}'\n")
    s.append(f"{T*2}summarizeBy: {summ}\n{T*2}sourceColumn: {src}\n\n")

# hierarchies
s.append(f"{T}hierarchy 'Product Hierarchy'\n\n{T*2}level 'Product Category'\n{T*3}column: 'Product Category'\n\n{T*2}level 'Product Subcategory'\n{T*3}column: 'Product Subcategory'\n\n")
s.append(f"{T}hierarchy 'Geography Hierarchy'\n\n{T*2}level Region\n{T*3}column: Region\n\n{T*2}level Country\n{T*3}column: Country\n\n")
s.append(f"{T}hierarchy 'Customer Hierarchy'\n\n{T*2}level 'Customer Segment'\n{T*3}column: 'Customer Segment'\n\n{T*2}level 'Age Group'\n{T*3}column: 'Age Group'\n\n{T*2}level 'Customer Name'\n{T*3}column: 'Customer Name'\n\n")

fields = ",".join(['"%s"' % c[0] for c in cols[:27]])
m_expr = f'''let
	Source = Excel.Workbook(File.Contents(SourcePath), null, true),
	DataSheet = Source{{[Item="Data", Kind="Sheet"]}}[Data],
	Promoted = Table.PromoteHeaders(DataSheet, [PromoteAllScalars=true]),
	Typed = Table.TransformColumnTypes(Promoted, {{{typed}}}),
	WithStatus = Table.AddColumn(Typed, "TargetStatus", each if [SalesAmount] >= 0.75 * [Target] then "On Track" else "At Risk", type text),
	WithBand = Table.AddColumn(WithStatus, "DiscountBand", each if [DiscountApplied] < 10 then "Low (<10%)" else if [DiscountApplied] < 20 then "Medium (10-20%)" else "High (20%+)", type text),
	WithBandOrder = Table.AddColumn(WithBand, "DiscountBandOrder", each if [DiscountApplied] < 10 then 1 else if [DiscountApplied] < 20 then 2 else 3, Int64.Type),
	WithStage = Table.AddColumn(WithBandOrder, "StageOrder", each if [SalesStage] = "Lead" then 1 else if [SalesStage] = "Qualified" then 2 else if [SalesStage] = "Proposal" then 3 else if [SalesStage] = "Negotiation" then 4 else 5, Int64.Type)
in
	WithStage'''
s.append(f"{T}partition Sales = m\n{T*2}mode: import\n{T*2}source =\n")
for ln in m_expr.split("\n"):
    s.append(f"{T*3}{ln}\n")
w(os.path.join(TBL, "Sales.tmdl"), "".join(s))

# ---------------------------------------------------------------- Date table
date_m = '''let
	StartDate = #date(2022, 1, 1),
	EndDate = #date(2024, 12, 31),
	Days = List.Dates(StartDate, Duration.Days(EndDate - StartDate) + 1, #duration(1, 0, 0, 0)),
	AsTable = Table.FromList(Days, Splitter.SplitByNothing(), {"Date"}, null, ExtraValues.Error),
	Typed = Table.TransformColumnTypes(AsTable, {{"Date", type date}}),
	WithYear = Table.AddColumn(Typed, "Year", each Date.Year([Date]), Int64.Type),
	WithQuarter = Table.AddColumn(WithYear, "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
	WithMonthNum = Table.AddColumn(WithQuarter, "Month Number", each Date.Month([Date]), Int64.Type),
	WithMonth = Table.AddColumn(WithMonthNum, "Month", each Date.ToText([Date], "MMM"), type text),
	WithYM = Table.AddColumn(WithMonth, "Year-Month", each Date.ToText([Date], "yyyy-MM"), type text)
in
	WithYM'''
d = ["table Date\n\tdataCategory: Time\n\n"]
d.append("\tcolumn Date\n\t\tdataType: dateTime\n\t\tisKey\n\t\tformatString: dd-MMM-yyyy\n\t\tsummarizeBy: none\n\t\tsourceColumn: Date\n\n")
d.append("\tcolumn Year\n\t\tdataType: int64\n\t\tformatString: 0\n\t\tsummarizeBy: none\n\t\tsourceColumn: Year\n\n")
d.append("\tcolumn Quarter\n\t\tdataType: string\n\t\tsummarizeBy: none\n\t\tsourceColumn: Quarter\n\n")
d.append("\tcolumn 'Month Number'\n\t\tdataType: int64\n\t\tisHidden\n\t\tformatString: 0\n\t\tsummarizeBy: none\n\t\tsourceColumn: Month Number\n\n")
d.append("\tcolumn Month\n\t\tdataType: string\n\t\tsortByColumn: 'Month Number'\n\t\tsummarizeBy: none\n\t\tsourceColumn: Month\n\n")
d.append("\tcolumn 'Year-Month'\n\t\tdataType: string\n\t\tsummarizeBy: none\n\t\tsourceColumn: Year-Month\n\n")
d.append("\thierarchy 'Date Hierarchy'\n\n\t\tlevel Year\n\t\t\tcolumn: Year\n\n\t\tlevel Quarter\n\t\t\tcolumn: Quarter\n\n\t\tlevel Month\n\t\t\tcolumn: Month\n\n")
d.append("\tpartition Date = m\n\t\tmode: import\n\t\tsource =\n")
for ln in date_m.split("\n"):
    d.append(f"\t\t\t{ln}\n")
w(os.path.join(TBL, "Date.tmdl"), "".join(d))

# ---------------------------------------------------------------- Field parameters
def field_param(name, items):
    tuples = ",\n".join('\t\t\t\t\t("%s", NAMEOF(%s), %d)' % (lbl, ref, i) for i, (lbl, ref) in enumerate(items))
    q = f"'{name}'"
    return f"""table {q}

	column {q}
		dataType: string
		summarizeBy: none
		sourceColumn: [Value1]
		sortByColumn: '{name} Order'

		relatedColumnDetails
			groupByColumn: '{name} Fields'

	column '{name} Fields'
		dataType: string
		isHidden
		summarizeBy: none
		sourceColumn: [Value2]
		sortByColumn: '{name} Order'

		extendedProperty ParameterMetadata =
				{{
				  "version": 3,
				  "kind": 2
				}}

	column '{name} Order'
		dataType: int64
		isHidden
		formatString: 0
		summarizeBy: sum
		sourceColumn: [Value3]

	partition {q} = calculated
		mode: import
		source =
				{{
{tuples}
				}}
"""

w(os.path.join(TBL, "Metric Selector.tmdl"), field_param("Metric Selector", [
    ("Sales", "Sales[Total Sales]"), ("Gross Profit", "Sales[Gross Profit]"),
    ("Orders", "Sales[Orders]"), ("Units Sold", "Sales[Units Sold]"),
    ("Avg Order Value", "Sales[Avg Order Value]"), ("Target Attainment", "Sales[Target Attainment %]")]))
w(os.path.join(TBL, "View By.tmdl"), field_param("View By", [
    ("Region", "Sales[Region]"), ("Product Category", "Sales[Product Category]"),
    ("Customer Segment", "Sales[Customer Segment]"), ("Channel", "Sales[Channel]"),
    ("Age Group", "Sales[Age Group]"), ("Sales Stage", "Sales[Sales Stage]")]))

# ---------------------------------------------------------------- What-if parameters
def whatif(name, col, lo, hi, step, default, folder_desc):
    return f"""table '{name}'

	/// {folder_desc}
	measure '{col} Value' = SELECTEDVALUE('{name}'[{col}], {default})
		formatString: 0%
		displayFolder: What-If

	column '{col}'
		dataType: double
		formatString: 0%
		summarizeBy: none
		sourceColumn: [Value]

		extendedProperty ParameterMetadata =
				{{
				  "version": 0
				}}

	partition '{name}' = calculated
		mode: import
		source = GENERATESERIES({lo}, {hi}, {step})
"""

w(os.path.join(TBL, "Price Change.tmdl"), whatif("Price Change", "Price Change", -0.15, 0.15, 0.01, 0, "What-if: percentage change applied to selling prices"))
w(os.path.join(TBL, "Volume Change.tmdl"), whatif("Volume Change", "Volume Change", -0.25, 0.25, 0.01, 0, "What-if: percentage change in units sold"))
w(os.path.join(TBL, "Cost Inflation.tmdl"), whatif("Cost Inflation", "Cost Inflation", 0, 0.2, 0.01, 0, "What-if: percentage increase in cost of goods sold"))

# ---------------------------------------------------------------- relationships, model
w(os.path.join(DEF, "relationships.tmdl"),
  "relationship SalesToDate\n\tfromColumn: Sales.'Order Date'\n\ttoColumn: Date.Date\n")

tables = ["Sales", "Date", "'Metric Selector'", "'View By'", "'Price Change'", "'Volume Change'", "'Cost Inflation'"]
model = "model Model\n\tculture: en-US\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tsourceQueryCulture: en-US\n\n"
model += "ref expression SourcePath\n" if False else ""
model += "".join(f"ref table {t}\n" for t in tables)
w(os.path.join(DEF, "model.tmdl"), model)
print("model written", SM)
