"""Builds deliverables/SalesPerformance_Monthly.rdl (Power BI paginated report, RDL 2016 schema)."""
import os, sys
from xml.sax.saxutils import escape
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paginated_queries as pq

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "deliverables", "SalesPerformance_Monthly.rdl")
NAVY = "#1F3A5F"
def esc_q(s): return escape(s)

def dataset(name, fn, fields):
    q = fn("@Year", "@Region", "@Category")
    fl = "".join(f'<Field Name="{n}"><DataField>[{src}]</DataField></Field>' for n, src in fields)
    return f'''<DataSet Name="{name}"><Query><DataSourceName>SalesModel</DataSourceName>
<QueryParameters>
<QueryParameter Name="@Year"><Value>=Parameters!Year.Value</Value></QueryParameter>
<QueryParameter Name="@Region"><Value>=Parameters!Region.Value</Value></QueryParameter>
<QueryParameter Name="@Category"><Value>=Parameters!Category.Value</Value></QueryParameter>
</QueryParameters>
<CommandText>{esc_q(q)}</CommandText></Query><Fields>{fl}</Fields></DataSet>'''

DS = [
    ("KPI", pq.ds_kpi, [("TotalSales", "Total Sales"), ("TotalTarget", "Total Target"), ("Attainment", "Attainment"), ("GrossProfit", "Gross Profit"), ("Margin", "Margin"), ("Orders", "Orders"), ("AOV", "AOV")]),
    ("Category", pq.ds_category, [("Category", "Sales[Product Category]"), ("TotalSales", "Total Sales"), ("TotalTarget", "Total Target"), ("Attainment", "Attainment"), ("GrossProfit", "Gross Profit"), ("Margin", "Margin"), ("Orders", "Orders")]),
    ("Region", pq.ds_region, [("Region", "Sales[Region]"), ("TotalSales", "Total Sales"), ("TotalTarget", "Total Target"), ("Variance", "Variance"), ("Attainment", "Attainment"), ("Orders", "Orders")]),
    ("Quarter", pq.ds_quarter, [("Year", "Date[Year]"), ("Quarter", "Date[Quarter]"), ("TotalSales", "Total Sales"), ("TotalTarget", "Total Target")]),
]

def cell(expr, fmt=None, bold=False, color="#1B2A3B", bg=None, align="Left"):
    f = f"<Format>{fmt}</Format>" if fmt else ""
    b = "<FontWeight>Bold</FontWeight>" if bold else ""
    bgx = f"<BackgroundColor>{bg}</BackgroundColor>" if bg else ""
    return f'''<TablixCell><CellContents><Textbox Name="tb{abs(hash(expr+str(bold)+str(id(expr))))%10**8}"><CanGrow>true</CanGrow><KeepTogether>true</KeepTogether>
<Paragraphs><Paragraph><TextRuns><TextRun><Value>{escape(expr)}</Value><Style><FontFamily>Segoe UI</FontFamily><FontSize>9pt</FontSize>{b}<Color>{color}</Color>{f}</Style></TextRun></TextRuns><Style><TextAlign>{align}</TextAlign></Style></Paragraph></Paragraphs>
<Style><Border><Style>None</Style><Color>#DDE3EC</Color><Width>0.5pt</Width></Border><BottomBorder><Style>Solid</Style></BottomBorder>{bgx}<PaddingLeft>4pt</PaddingLeft><PaddingRight>4pt</PaddingRight><PaddingTop>3pt</PaddingTop><PaddingBottom>3pt</PaddingBottom></Style></Textbox></CellContents></TablixCell>'''

def tablix(name, dsname, top, cols):
    """cols: list of (header, field, format, width_in, align)"""
    widths = "".join(f"<TablixColumn><Width>{w}in</Width></TablixColumn>" for _, _, _, w, _ in cols)
    hdr = "".join(cell(h, bold=True, color="#FFFFFF", bg=NAVY, align=a) for h, _, _, _, a in cols)
    row = "".join(cell(f"=Fields!{f}.Value", fm, align=a) for _, f, fm, _, a in cols)
    tot = f"{sum(c[3] for c in cols)}in"
    return f'''<Tablix Name="{name}"><TablixBody><TablixColumns>{widths}</TablixColumns><TablixRows>
<TablixRow><Height>0.28in</Height><TablixCells>{hdr}</TablixCells></TablixRow>
<TablixRow><Height>0.26in</Height><TablixCells>{row}</TablixCells></TablixRow></TablixRows></TablixBody>
<TablixColumnHierarchy><TablixMembers>{"<TablixMember />" * len(cols)}</TablixMembers></TablixColumnHierarchy>
<TablixRowHierarchy><TablixMembers><TablixMember><KeepWithGroup>After</KeepWithGroup><RepeatOnNewPage>true</RepeatOnNewPage></TablixMember><TablixMember><Group Name="{name}Details" /></TablixMember></TablixMembers></TablixRowHierarchy>
<DataSetName>{dsname}</DataSetName><Top>{top}in</Top><Left>0in</Left><Height>0.54in</Height><Width>{tot}</Width></Tablix>'''

def label(name, text, top, size="12pt", bold=True, color=NAVY, width="7in", height="0.3in"):
    w = "<FontWeight>Bold</FontWeight>" if bold else ""
    return f'''<Textbox Name="{name}"><CanGrow>true</CanGrow><KeepTogether>true</KeepTogether><Paragraphs><Paragraph><TextRuns><TextRun><Value>{escape(text)}</Value><Style><FontFamily>Segoe UI</FontFamily><FontSize>{size}</FontSize>{w}<Color>{color}</Color></Style></TextRun></TextRuns></Paragraph></Paragraphs><Top>{top}in</Top><Left>0in</Left><Height>{height}</Height><Width>{width}</Width></Textbox>'''

chart = f'''<Chart Name="QuarterChart"><ChartCategoryHierarchy><ChartMembers><ChartMember><Group Name="QYQ"><GroupExpressions><GroupExpression>=Fields!Year.Value &amp; " " &amp; Fields!Quarter.Value</GroupExpression></GroupExpressions></Group><Label>=Fields!Year.Value &amp; " " &amp; Fields!Quarter.Value</Label></ChartMember></ChartMembers></ChartCategoryHierarchy>
<ChartSeriesHierarchy><ChartMembers><ChartMember><Label>Sales</Label></ChartMember><ChartMember><Label>Target</Label></ChartMember></ChartMembers></ChartSeriesHierarchy>
<ChartData><ChartSeriesCollection>
<ChartSeries Name="Sales"><ChartDataPoints><ChartDataPoint><ChartDataPointValues><Y>=Sum(Fields!TotalSales.Value)</Y></ChartDataPointValues></ChartDataPoint></ChartDataPoints><Type>Column</Type><Style><Color>{NAVY}</Color></Style></ChartSeries>
<ChartSeries Name="Target"><ChartDataPoints><ChartDataPoint><ChartDataPointValues><Y>=Sum(Fields!TotalTarget.Value)</Y></ChartDataPointValues></ChartDataPoint></ChartDataPoints><Type>Column</Type><Style><Color>#F4A261</Color></Style></ChartSeries>
</ChartSeriesCollection></ChartData>
<ChartAreas><ChartArea Name="Default"><ChartCategoryAxes><ChartAxis Name="Category"><Style><FontSize>8pt</FontSize></Style></ChartAxis></ChartCategoryAxes><ChartValueAxes><ChartAxis Name="Value"><Style><FontSize>8pt</FontSize><Format>$#,0</Format></Style></ChartAxis></ChartValueAxes></ChartArea></ChartAreas>
<ChartLegends><ChartLegend Name="Legend"><Style><FontSize>8pt</FontSize></Style></ChartLegend></ChartLegends>
<ChartTitles><ChartTitle Name="Title"><Caption>Sales vs target by quarter</Caption><Style><FontSize>10pt</FontSize><FontWeight>Bold</FontWeight><Color>{NAVY}</Color></Style></ChartTitle></ChartTitles>
<DataSetName>Quarter</DataSetName><Top>5.15in</Top><Left>0in</Left><Height>3in</Height><Width>7in</Width></Chart>'''

M = "$#,0"
body_items = [
    label("tbSub", '="Year: " & Parameters!Year.Value & "   |   Region: " & Parameters!Region.Value & "   |   Category: " & Parameters!Category.Value & "   |   Prepared for: " & Parameters!Recipient.Value', 0.0, "9pt", False, "#6C7A89"),
    label("lblKpi", "Headline metrics", 0.35),
    tablix("KpiTable", "KPI", 0.7, [("Sales", "TotalSales", M, 1.0, "Right"), ("Target", "TotalTarget", M, 1.0, "Right"), ("Attainment", "Attainment", "0.0%", 0.9, "Right"), ("Gross profit", "GrossProfit", M, 1.0, "Right"), ("Margin", "Margin", "0.0%", 0.8, "Right"), ("Orders", "Orders", "#,0", 0.7, "Right"), ("Avg order", "AOV", M, 0.9, "Right")]),
    label("lblCat", "Performance by product category", 1.5),
    tablix("CategoryTable", "Category", 1.85, [("Category", "Category", None, 1.5, "Left"), ("Sales", "TotalSales", M, 1.0, "Right"), ("Target", "TotalTarget", M, 1.0, "Right"), ("Attainment", "Attainment", "0.0%", 0.9, "Right"), ("Gross profit", "GrossProfit", M, 1.0, "Right"), ("Margin", "Margin", "0.0%", 0.8, "Right"), ("Orders", "Orders", "#,0", 0.8, "Right")]),
    label("lblReg", "Performance by region", 2.95),
    tablix("RegionTable", "Region", 3.3, [("Region", "Region", None, 1.5, "Left"), ("Sales", "TotalSales", M, 1.2, "Right"), ("Target", "TotalTarget", M, 1.2, "Right"), ("Variance", "Variance", "$#,0;-$#,0", 1.2, "Right"), ("Attainment", "Attainment", "0.0%", 1.0, "Right"), ("Orders", "Orders", "#,0", 0.9, "Right")]),
    label("lblTrend", "Quarterly trend", 4.8),
]

def param(name, prompt, values, default):
    vs = "".join(f"<ParameterValue><Value>{v}</Value><Label>{v}</Label></ParameterValue>" for v in values)
    return f'<ReportParameter Name="{name}"><DataType>String</DataType><DefaultValue><Values><Value>{default}</Value></Values></DefaultValue><Prompt>{prompt}</Prompt><ValidValues><ParameterValues>{vs}</ParameterValues></ValidValues></ReportParameter>'

params = (param("Year", "Year", ["All", "2022", "2023", "2024"], "All") +
          param("Region", "Region", ["All", "Central", "East", "North", "South", "West"], "All") +
          param("Category", "Product category", ["All", "Clothing", "Electronics", "Home", "Sports"], "All") +
          '<ReportParameter Name="Recipient"><DataType>String</DataType><DefaultValue><Values><Value>Executive Leadership</Value></Values></DefaultValue><Prompt>Prepared for</Prompt></ReportParameter>')

def hf(name, text, top, h, extra=""):
    return f'<Textbox Name="{name}"><CanGrow>true</CanGrow><KeepTogether>true</KeepTogether><Paragraphs><Paragraph><TextRuns><TextRun><Value>{escape(text)}</Value><Style><FontFamily>Segoe UI</FontFamily><FontSize>9pt</FontSize><Color>#FFFFFF</Color>{extra}</Style></TextRun></TextRuns></Paragraph></Paragraphs><Top>{top}in</Top><Left>0.1in</Left><Height>{h}in</Height><Width>6.8in</Width></Textbox>'

rdl = f'''<?xml version="1.0" encoding="utf-8"?>
<Report xmlns="http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition" xmlns:rd="http://schemas.microsoft.com/SQLServer/reporting/reportdesigner">
<AutoRefresh>0</AutoRefresh>
<DataSources><DataSource Name="SalesModel"><ConnectionProperties><DataProvider>PBIDATASET</DataProvider><ConnectString>Data Source=pbiazure://api.powerbi.com;Identity Provider="https://login.microsoftonline.com/common, https://analysis.windows.net/powerbi/api, 929d0ec0-7a41-4b1e-b4d4-f5c1f2f2b6c5";Initial Catalog=SalesPerformance</ConnectString></ConnectionProperties><rd:SecurityType>None</rd:SecurityType></DataSource></DataSources>
<DataSets>{"".join(dataset(*d) for d in DS)}</DataSets>
<ReportSections><ReportSection>
<Body><ReportItems>{"".join(body_items)}{chart}</ReportItems><Height>8.3in</Height><Style><BackgroundColor>#FFFFFF</BackgroundColor></Style></Body>
<Width>7in</Width>
<Page>
<PageHeader><Height>0.6in</Height><PrintOnFirstPage>true</PrintOnFirstPage><PrintOnLastPage>true</PrintOnLastPage><ReportItems>
<Rectangle Name="HdrBand"><ReportItems>{hf("tbTitle", "Monthly Sales Performance Report", 0.06, 0.3, "<FontSize>16pt</FontSize><FontWeight>Bold</FontWeight>")}{hf("tbConf", "Confidential - for internal distribution", 0.36, 0.2, "<FontSize>8pt</FontSize>")}</ReportItems><Top>0in</Top><Left>0in</Left><Height>0.6in</Height><Width>7in</Width><Style><BackgroundColor>{NAVY}</BackgroundColor></Style></Rectangle>
</ReportItems><Style><Border><Style>None</Style></Border></Style></PageHeader>
<PageFooter><Height>0.4in</Height><PrintOnFirstPage>true</PrintOnFirstPage><PrintOnLastPage>true</PrintOnLastPage><ReportItems>
<Textbox Name="tbPage"><CanGrow>true</CanGrow><KeepTogether>true</KeepTogether><Paragraphs><Paragraph><TextRuns><TextRun><Value>="Page " &amp; Globals!PageNumber &amp; " of " &amp; Globals!TotalPages &amp; "     Generated " &amp; Format(Globals!ExecutionTime, "dd MMM yyyy HH:mm")</Value><Style><FontFamily>Segoe UI</FontFamily><FontSize>8pt</FontSize><Color>#6C7A89</Color></Style></TextRun></TextRuns><Style><TextAlign>Right</TextAlign></Style></Paragraph></Paragraphs><Top>0.1in</Top><Left>0in</Left><Height>0.25in</Height><Width>7in</Width></Textbox>
</ReportItems><Style><Border><TopBorder><Style>Solid</Style><Color>#DDE3EC</Color></TopBorder></Border></Style></PageFooter>
<PageHeight>11in</PageHeight><PageWidth>8.5in</PageWidth><LeftMargin>0.75in</LeftMargin><RightMargin>0.75in</RightMargin><TopMargin>0.5in</TopMargin><BottomMargin>0.5in</BottomMargin><ColumnSpacing>0.5in</ColumnSpacing>
</Page></ReportSection></ReportSections>
<ReportParameters>{params}</ReportParameters>
<Language>en-US</Language>
</Report>'''
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(rdl)
import xml.dom.minidom
xml.dom.minidom.parseString(rdl.encode("utf-8"))
print("rdl written + well-formed:", OUT, len(rdl))
