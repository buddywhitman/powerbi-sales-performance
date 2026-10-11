"""Model-level test suite. Writes deliverables/test_results.json. Uses python -I; talks to Desktop via pbi CLI."""
import subprocess, json, time, os, sys
import openpyxl
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = list(openpyxl.load_workbook(os.path.join(ROOT, "dashboard.xlsx"), read_only=True)["Data"].iter_rows(values_only=True))
hdr, data = rows[0], rows[1:]
ix = {h: i for i, h in enumerate(hdr)}
def xl(col, f=lambda r: True): return sum(r[ix[col]] for r in data if f(r))

def dax(q):
    t = time.perf_counter()
    p = subprocess.run(["pbi", "--json", "dax", "execute", " ".join(q.split())], capture_output=True, text=True, shell=True)
    ms = (time.perf_counter() - t) * 1000
    try:
        j = json.loads(p.stdout)
        return j["rows"], ms
    except Exception:
        return None, ms

def val(q):
    r, ms = dax(q)
    if not r: return None, ms
    return float(list(r[0].values())[0]), ms

results = []
def check(name, area, actual, expected, ms, tol=0.01):
    ok = actual is not None and abs(actual - expected) <= tol * max(1, abs(expected)) * (1 if tol >= 1 else 1) if False else (actual is not None and abs(actual - expected) <= max(tol, 1e-6))
    results.append({"test": name, "area": area, "expected": expected, "actual": actual, "pass": bool(ok), "ms": round(ms)})
    print(("PASS" if ok else "FAIL"), name, actual, expected, round(ms), "ms")

a, ms = val('EVALUATE ROW("v",[Total Sales])'); check("Total Sales reconciles to Excel", "Functionality", a, xl("SalesAmount"), ms, 0.01)
a, ms = val('EVALUATE ROW("v",[Total Target])'); check("Total Target reconciles to Excel", "Functionality", a, xl("Target"), ms, 0.01)
a, ms = val('EVALUATE ROW("v",[Orders])'); check("Distinct orders = 500", "Functionality", a, 500, ms, 0)
a, ms = val('EVALUATE ROW("v",[Total Sales] - [Total COGS] - [Gross Profit])'); check("Gross Profit = Sales - COGS", "Functionality", a, 0, ms, 0.01)
a, ms = val('EVALUATE ROW("v",CALCULATE([Total Sales], Sales[Region]="South"))'); check("Region filter (South) vs Excel", "Cross-filtering", a, xl("SalesAmount", lambda r: r[ix["Region"]] == "South"), ms, 0.01)
a, ms = val('EVALUATE ROW("v",CALCULATE([Total Sales], \'Date\'[Year]=2024))'); check("Year filter via Date table (2024) vs Excel", "Cross-filtering", a, xl("SalesAmount", lambda r: r[ix["Year"]] == 2024), ms, 0.01)
a, ms = val('EVALUATE ROW("v",SUMX(VALUES(Sales[Product Category]),[Total Sales]) - [Total Sales])'); check("Category totals add to grand total", "Cross-filtering", a, 0, ms, 0.01)
a, ms = val('EVALUATE ROW("v",CALCULATE([Total Sales], \'Date\'[Year]=2023) - CALCULATE([Sales PY], \'Date\'[Year]=2024))'); check("Sales PY (2024) equals 2023 sales", "Functionality", a, 0, ms, 0.01)
a, ms = val('EVALUATE ROW("v",CALCULATE([Scenario Sales], Sales[Region]="East") - CALCULATE([Total Sales], Sales[Region]="East"))'); check("Scenario at defaults equals baseline", "Parameters", a, 0, ms, 0.01)
a, ms = val('EVALUATE ROW("v",COUNTROWS(\'Price Change\'))'); check("Price Change what-if has 31 steps (-15%..+15%)", "Parameters", a, 31, ms, 0)
a, ms = val('EVALUATE ROW("v",COUNTROWS(\'Metric Selector\'))'); check("Metric Selector field parameter has 6 fields", "Parameters", a, 6, ms, 0)
a, ms = val('EVALUATE ROW("v",COUNTROWS(\'View By\'))'); check("View By field parameter has 6 fields", "Parameters", a, 6, ms, 0)
# scenario math with explicit override: +10% price, 0 volume, 0 inflation => sales*1.1
q = "EVALUATE ROW(\"v\", CALCULATE([Scenario Sales], FILTER(VALUES('Price Change'[Price Change]), ABS('Price Change'[Price Change] - 0.1) < 0.0001)) - [Total Sales]*1.1)"
a, ms = val(q); check("What-if math: +10% price => sales x1.10", "Parameters", a, 0, ms, 0.01)
a, ms = val('EVALUATE ROW("v",COUNTROWS(FILTER(VALUES(Sales[Sales Rep]), CALCULATE([Total Sales])>0)))'); check("Drill-through key (Sales Rep) resolves for every rep", "Drill-through", a, len(set(r[ix["SalesRep"]] for r in data)), ms, 0)
r, ms = dax('EVALUATE ROW("t",[Title Top Performer],"e",[Title Explorer],"s",[Title Scenario],"r",[Rep Detail Title],"c",[Selection Context])')
results.append({"test": "Dynamic title measures evaluate to text", "area": "Parameters", "expected": "5 non-empty strings", "actual": r[0] if r else None, "pass": bool(r and all(v for v in r[0].values())), "ms": round(ms)})
print("dynamic:", r)
# performance: 5 reps of the heaviest page query pattern
heavy = 'EVALUATE SUMMARIZECOLUMNS(\'Date\'[Year],\'Date\'[Quarter],Sales[Region],Sales[Product Category],"s",[Total Sales],"t",[Total Target],"y",[Sales YoY %],"g",[Gross Margin %])'
times = []
for _ in range(5):
    _, ms = dax(heavy); times.append(ms)
perf = {"heavy_query_ms": [round(t) for t in times], "median_ms": round(sorted(times)[2])}
print(perf)
json.dump({"results": results, "perf": perf}, open(os.path.join(ROOT, "deliverables", "test_results.json"), "w"), indent=1, default=str)
print(sum(r["pass"] for r in results), "/", len(results), "passed")
