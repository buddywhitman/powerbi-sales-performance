d = r"D:\OneDrive\Documents\repos\powerbi\build\\"
def patch(fn, pairs):
    c = open(d + fn, encoding="utf-8").read()
    for a, b in pairs:
        assert a in c, a[:50]
        c = c.replace(a, b)
    open(d + fn, "w", encoding="utf-8").write(c)
patch("gen_model.py", [
    ('if [SalesAmount] >= [Target] then "Met Target" else "Below Target"', 'if [SalesAmount] >= 0.75 * [Target] then "On Track" else "At Risk"'),
    ('add("Orders Meeting Target %", "DIVIDE(CALCULATE([Orders], Sales[Target Status] = \\"Met Target\\"), [Orders])", "0.0%", "2 Performance")',
     'add("Orders On Track %", "DIVIDE(CALCULATE([Orders], Sales[Target Status] = \\"On Track\\"), [Orders])", "0.0%", "2 Performance", "Share of orders reaching at least 75% of their target")'),
])
patch("gen_report.py", [('Details=[PC("Sales", "Order ID")],', ''),
                        ("what drives meeting target? (AI)", "what drives orders being on track (>=75% of target)? (AI)")])
print("ok")
