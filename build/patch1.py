import re
p = r"D:\OneDrive\Documents\repos\powerbi\build\gen_report.py"
c = open(p, encoding="utf-8").read()

def rep(a, b):
    global c
    assert a in c, a[:60]
    c = c.replace(a, b, 1)

rep('"border": [{"properties": {"show": B(False)}}],\n                                   "visualLink"',
    '"border": [{"properties": {"show": B(False)}}],\n                                   "padding": [{"properties": {"top": D(0), "bottom": D(0), "left": D(0), "right": D(0)}}],\n                                   "visualLink"')
rep('btn(page, x, 12, 138, 40, label,', 'btn(page, x, 10, 138, 44, label,')
rep('"fontColor": color(NAVY), "bold": B(True)}, "selector": {"id": "default"}}],\n                    "label"',
    '"fontColor": color(NAVY), "bold": B(True), "labelDisplayUnits": L("1D"), "labelPrecision": D(0)}, "selector": {"id": "default"}}],\n                    "label"')
rep('dict(Target=[PC("Sales", "Target Status")],', 'dict(Target=[PC("Sales", "Target Status")], Details=[PC("Sales", "Order ID")],')
rep('chart(p, "azureMap", 24, 252, 620, 452, dict(Category=[PC("Sales", "Country")], Size=[PM("Total Sales")]), title="Sales by country")',
    'chart(p, "treemap", 24, 252, 620, 452, dict(Group=[PH("Sales", "Geography Hierarchy", "Country", True)], Details=[PH("Sales", "Geography Hierarchy", "Region", True)], Values=[PM("Total Sales")]), title="Sales footprint: country and region")')
rep('def slicer(page, x, y, w, entity, column, label, mode="Dropdown", sync=None, fieldq=None):',
    '''def default_filter(table, column, value):
    return {"filter": {"Version": 2, "From": [{"Name": "p", "Entity": table, "Type": 0}],
            "Where": [{"Condition": {"In": {"Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "p"}}, "Property": column}}],
                                            "Values": [[{"Literal": {"Value": "'" + value + "'"}}]]}}}]}}

def slicer(page, x, y, w, entity, column, label, mode="Dropdown", sync=None, fieldq=None, default=None):''')
rep('    if sync:\n        vis["syncGroup"]',
    '''    if default:
        vis["objects"]["general"] = [{"properties": {"filter": default_filter(entity, column, default)}}]
        vis["objects"]["selection"] = [{"properties": {"singleSelect": B(True), "selectAllCheckboxEnabled": B(False)}}]
    if sync:
        vis["syncGroup"]''')
rep('("Metric Selector", "Metric Selector", "Metric (field parameter)")', '("Metric Selector", "Metric Selector", "Metric (field parameter)", {"default": "Sales"})')
rep('("View By", "View By", "View by (field parameter)")', '("View By", "View By", "View by (field parameter)", {"default": "Region"})')
open(p, "w", encoding="utf-8").write(c)
print("ok")
