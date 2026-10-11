"""DAX datasets shared by the RDL generator and the sample-PDF generator. {Y}/{R}/{C} are filled with literals for testing; RDL uses @Year/@Region/@Category."""
FILTERS = '''FILTER(ALL('Date'[Year]), {Y} = "All" || 'Date'[Year] = VALUE({Y})),
    FILTER(ALL(Sales[Region]), {R} = "All" || Sales[Region] = {R}),
    FILTER(ALL(Sales[Product Category]), {C} = "All" || Sales[Product Category] = {C})'''

def f(y, r, c):
    return FILTERS.format(Y=y, R=r, C=c)

def ds_kpi(y, r, c):
    return f'''EVALUATE
SUMMARIZECOLUMNS(
    {f(y, r, c)},
    "Total Sales", [Total Sales], "Total Target", [Total Target], "Attainment", [Target Attainment %],
    "Gross Profit", [Gross Profit], "Margin", [Gross Margin %], "Orders", [Orders], "AOV", [Avg Order Value])'''

def ds_category(y, r, c):
    return f'''EVALUATE
SUMMARIZECOLUMNS(
    Sales[Product Category],
    {f(y, r, c)},
    "Total Sales", [Total Sales], "Total Target", [Total Target], "Attainment", [Target Attainment %],
    "Gross Profit", [Gross Profit], "Margin", [Gross Margin %], "Orders", [Orders])
ORDER BY [Total Sales] DESC'''

def ds_region(y, r, c):
    return f'''EVALUATE
SUMMARIZECOLUMNS(
    Sales[Region],
    {f(y, r, c)},
    "Total Sales", [Total Sales], "Total Target", [Total Target], "Variance", [Variance to Target],
    "Attainment", [Target Attainment %], "Orders", [Orders])
ORDER BY [Total Sales] DESC'''

def ds_quarter(y, r, c):
    return f'''EVALUATE
SUMMARIZECOLUMNS(
    'Date'[Year], 'Date'[Quarter],
    {f(y, r, c)},
    "Total Sales", [Total Sales], "Total Target", [Total Target])
ORDER BY 'Date'[Year], 'Date'[Quarter]'''

DATASETS = [("KPI", ds_kpi), ("Category", ds_category), ("Region", ds_region), ("Quarter", ds_quarter)]
