import subprocess, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paginated_queries as pq
out = {}
for name, fn in pq.DATASETS:
    q = fn('"2024"', '"All"', '"All"')
    q = " ".join(q.split())
    p = subprocess.run(["pbi", "--json", "dax", "execute", q], capture_output=True, text=True, shell=True)
    try:
        out[name] = json.loads(p.stdout)
    except Exception:
        out[name] = {"error": (p.stdout + p.stderr)[:600]}
    print(name, "rows:", len(out[name].get("rows", [])), out[name].get("error", ""))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data.json"), "w"), indent=1)
