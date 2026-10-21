"""Evaluate all candidates (model v3); houses get ADU/conversion variants; keep best plan; split sold/dead."""
import json, sys
sys.path.insert(0, sys.argv[1])
from data2 import C
from model import evaluate
from adu_size import SIZES, tier
out = []
for d in C:
    variants = [("No ADU (straight plan)", d)]
    if d["fin"] == "flip" and not d.get("build_adu"):
        t = tier(d["area"])
        for sf, label, psf, soft, xm, prem, rent in SIZES:
            v = dict(d, build_adu=sf * psf, permits=d.get("permits", 0) + soft, resale=d["resale"] + prem * t,
                     months=d["months"] + xm, plan=d["plan"] + f" + {label}", strategy="House + ADU")
            variants.append((label, v))
    scored = [(lab, evaluate(v)) for lab, v in variants]
    best_lab, best = max(scored, key=lambda x: x[1]["sc"]["base"]["profit"])
    best["variants"] = [dict(label=lab, profit=r["sc"]["base"]["profit"], months=r["sc"]["base"]["months"],
                             equity=r["sc"]["base"]["equity"]) for lab, r in scored]
    best["best_variant"] = best_lab
    out.append(best)
live = sorted([r for r in out if not r.get("dead")], key=lambda r: -r["sc"]["base"]["profit"])
dead = [r for r in out if r.get("dead")]
for i, r in enumerate(live, 1): r["rank"] = i
json.dump(dict(live=live, dead=dead), open(sys.argv[2], "w"), indent=1, default=str)
k = lambda x: "—" if x is None else f"{x/1e3:,.0f}k"
for r in live:
    b = r["sc"]["base"]
    print(f"{r['rank']:>2} {r['addr'][:30]:30} {r['best_variant'][:14]:14} net {k(b['profit']):>7} cons {k(r['sc']['cons']['profit']):>7} opt {k(r['sc']['opt']['profit']):>7} EV {k(r['ev']):>7} eq {k(b['equity']):>6} {b['months']:>2}mo offer {k(r['offer']):>6} m150 {k(r['max150']):>6} fit {r['fits']}")
print("DEAD:")
for r in dead:
    b = r["sc"]["base"]; print("  ", r["addr"], r["dead"], "net at sold price", k(b["profit"]))
