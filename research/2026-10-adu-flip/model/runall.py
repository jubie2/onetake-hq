import json, sys
sys.path.insert(0, sys.argv[1])
from data import CANDIDATES, SOLD_BENCHMARKS
from calc import run, adu_penalty
rows = run(CANDIDATES)
k = lambda x: "—" if x is None else f"{x/1e3:,.0f}k"
for r in rows:
    print(f"{r['rank']:>2} {r['call']:5} {r['kind']:4} {r['addr'][:34]:34} {k(r['price']):>7} {k(r['arv']):>7} net {k(r['profit']):>7} [{k(r['low'])}..{k(r['high'])}] roi {r['roi']*100:5.1f}% cash {k(r['cash']):>6} ceil {k(r['ceiling']):>6} be {k(r['breakeven'])}")
by = {c["addr"]: c for c in CANDIDATES}
pen = [adu_penalty(by[a], s, p) for a, s, p in [("5789 Tex St", 750, 250_000), ("9371 Fermi Ave", 750, 225_000),
       ("5800 Marengo Ave", 750, 250_000), ("9035 Rohr", 800, 250_000), ("648 51st St", 750, 200_000), ("3225 Logan Ave", 750, 200_000)]]
for p in pen: print(p["addr"], k(p["base"]), "->", k(p["with_adu"]), "delta", k(p["delta"]), "adu cost", k(p["adu_cost"]))
json.dump(dict(rows=rows, adu=pen, sold=SOLD_BENCHMARKS), open(sys.argv[1] + "/results.json", "w"), indent=1, default=str)
