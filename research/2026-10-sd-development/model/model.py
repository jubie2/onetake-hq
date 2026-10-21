"""Pro forma model v3 (2026-10-21, after skeptic review): first-timer lender terms, 15-20% contingency,
missing cost lines, possession as soft cost, land interest only after permits, cost-adder risk flags,
capital gate, disciplined max offer."""
CLOSE_BUY, TAX = 0.015, 0.012
SCEN = {  # resale mult (flip, land), cost mult, extra months (flip, land), rate, selling %
    "cons": dict(resale=(0.93, 0.87), cost=1.15, mo=(2, 6), rate=0.125, sell=0.08),
    "base": dict(resale=(1.00, 1.00), cost=1.00, mo=(0, 0), rate=0.115, sell=0.065),
    "opt":  dict(resale=(1.05, 1.05), cost=(0.95, 0.97), mo=(-1, 0), rate=0.11, sell=0.06),
    "pro":  dict(resale=(1.00, 1.00), cost=0.95, mo=(0, 0), rate=0.10, sell=0.055, pts=0.015, cont_mult=0.67),  # experienced operator, base resale
}
COST_KEYS = ("demo", "grading", "build_main", "build_adu", "renovation", "ae", "permits", "possession")
HARD_KEYS = ("demo", "grading", "build_main", "build_adu", "renovation")
FLAG_ADDERS = {"slope": (25_000, 1), "tenant": (15_000, 3), "septic": (40_000, 1)}   # flips only: $ soft adder, months
CAP = 150_000

def proforma(d, price=None, scen="base"):
    s = SCEN[scen]; land = d["fin"] == "land"; li = 1 if land else 0
    p = d["price"] if price is None else price
    cm = s["cost"][li] if isinstance(s["cost"], tuple) else s["cost"]
    items = {k: d.get(k, 0) * cm for k in COST_KEYS}
    mo = d["months"] + s["mo"][li]
    if not land:
        items["renovation"] += 15_000 * cm                     # sewer lateral, panel, lead/asbestos, termite, engineering
        for f, (adder, extra) in FLAG_ADDERS.items():
            if f in d.get("flags", []): items["possession"] += adder * cm; mo += extra
        if "auction" in d.get("flags", []): items = {k: v * 1.10 for k, v in items.items()}
    if land and d.get("build_main"):
        items["permits"] += 6 * d.get("main_sf", d["build_main"] / 400) * cm   # fire sprinklers ~$6/sf
    mo = max(3, mo)
    resale = d["resale"] * s["resale"][li]
    hard = sum(items[k] for k in HARD_KEYS)
    cont = d.get("cont", (0.20 if "slope" in d.get("flags", []) else 0.15) if land else 0.15) * hard * s.get("cont_mult", 1.0)
    build = sum(items.values()) + cont
    close = CLOSE_BUY * p
    if land:   # first-timer ground-up: realistically JV / experienced-GC guarantor only
        loan = min(0.50 * p + 0.85 * build, 0.70 * (p + build), 0.60 * resale); pts = s.get("pts", 0.025)
        acq = min(loan, 0.50 * p); bld = loan - acq
        ent = d.get("entitle_mo", 8)
        interest = s["rate"] / 12 * (acq * mo + 0.5 * bld * max(0, mo - ent))
        ins = max(350, 0.007 * hard / 12) * max(0, mo - ent) + 150 * min(mo, ent)
        supp_tax = TAX * 0.5 * hard * max(0, mo - ent) / 12
    else:
        loan = min(0.85 * p + build, 0.70 * resale) if "pts" not in s else min(0.85 * p + build, 0.75 * resale); pts = s.get("pts", 0.025)
        acq = min(loan, 0.85 * p); bld = loan - acq
        interest = s["rate"] * mo / 12 * (acq + 0.5 * bld)
        ins = max(350, 0.007 * hard / 12) * mo
        supp_tax = 0
    points = pts * loan + 2_500 + 250 * max(1, mo // 2)            # points + appraisal/underwriting + draw fees
    hold = TAX * p * mo / 12 + supp_tax + ins + 250 * mo
    sell = s["sell"] * resale
    total = p + close + build + points + interest + hold + sell
    profit = resale - total
    equity = (p + close + build + points + interest + hold) - loan
    pref = 0.08 * equity * mo / 12                                   # JV: partner funds all equity, 8% pref, then 70/30 (partner/you)
    sponsor = 0.30 * max(0.0, profit - pref)
    return dict(price=p, months=mo, resale=resale, items=items, cont=cont, build=build, close=close, loan=loan,
                points=points, interest=interest, hold=hold, sell=sell, total=total, profit=profit,
                margin=profit / resale, roc=profit / total, equity=equity, coc=profit / equity if equity > 0 else None,
                jv_sponsor=sponsor, jv_partner=profit - sponsor)

def max_price(d, target, scen="base"):
    if proforma(d, 0, scen)["profit"] < target: return None
    lo, hi = 0.0, 3e7
    for _ in range(70):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if proforma(d, mid, scen)["profit"] > target else (lo, mid)
    return lo

RISK_FLAGS = ("slope", "retaining", "access", "septic", "utilities", "permitting", "tenant", "auction", "unpermitted")
def evaluate(d):
    r = {k: proforma(d, scen=k) for k in SCEN}  # includes "pro" (not used in EV)
    flags = list(d.get("flags", []))
    if d.get("conf", "L") == "L" and "resale_low" not in flags: flags.append("resale_low")
    n = sum(1 for f in flags if f in RISK_FLAGS) + (1 if "resale_low" in flags else 0)
    pc = min(0.65, 0.30 + 0.07 * n); po = max(0.05, 0.20 - 0.03 * n); pb = 1 - pc - po
    ev = pc * r["cons"]["profit"] + pb * r["base"]["profit"] + po * r["opt"]["profit"]
    t150 = max_price(d, 150_000); be_cons = max_price(d, 0, "cons")
    disciplined = None if t150 is None or be_cons is None else min(t150, be_cons)
    fits = r["base"]["equity"] <= CAP
    return dict(d, sc=r, flags=flags, ev=ev, probs=(pc, pb, po), fits=fits,
                max150=t150, max250=max_price(d, 250_000), max500=max_price(d, 500_000),
                breakeven=max_price(d, 0), be_cons=be_cons, offer=disciplined)
