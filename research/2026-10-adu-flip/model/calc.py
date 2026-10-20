"""Uniform underwriting (corrected 2026 assumptions) + scenario + solver."""
RATE, TAX, SELL, CLOSE, INS_UTIL = 0.11, 0.012, 0.065, 0.015, 600

def uw(price, arv, mo, rehab=0.0, hard=0.0, soft=0.0, extra=0.0, ltv=0.85, pts=0.02, cont=0.10):
    c = cont * (rehab + hard)
    build = rehab + hard + soft + extra
    points = pts * (ltv * price + build)
    interest = RATE * mo / 12 * (ltv * price + 0.5 * build)
    hold = TAX * price * mo / 12 + INS_UTIL * mo
    sell = SELL * arv
    allin = price * (1 + CLOSE) + build + c + points + interest + hold + sell
    profit = arv - allin
    cash = (1 - ltv) * price + CLOSE * price + c + points + interest + hold
    return dict(allin=allin, profit=profit, roi=profit / allin, cash=cash, coc=profit / cash,
                build=build + c, carry=points + interest + hold, sell=sell)

def solve_price(target, arv, mo, **kw):
    lo, hi = 0.0, 2e7
    if uw(price=0, arv=arv, mo=mo, **kw)["profit"] < target:
        return None
    for _ in range(80):
        mid = (lo + hi) / 2
        if uw(price=mid, arv=arv, mo=mo, **kw)["profit"] > target: lo = mid
        else: hi = mid
    return lo

def scen(c, which):
    kw = dict(c["kw"]); land = c["kind"] == "land"
    if which == "low":
        arv, mo, f = c["arv"] * 0.94, c["mo"] + (6 if land else 2), 1.20
    else:
        arv, mo, f = c["arv"] * 1.05, max(3, c["mo"] - (4 if land else 1)), 0.90
    for k in ("rehab", "hard"):
        if k in kw: kw[k] = kw[k] * f
    return uw(price=c["price"], arv=arv, mo=mo, **kw)["profit"]

def run(cands):
    rows = []
    for c in cands:
        b = uw(price=c["price"], arv=c["arv"], mo=c["mo"], **c["kw"])
        rows.append(dict(c, **b, low=scen(c, "low"), high=scen(c, "high"),
                         ceiling=solve_price(100_000, c["arv"], c["mo"], **c["kw"]),
                         breakeven=solve_price(0, c["arv"], c["mo"], **c["kw"])))
    rows.sort(key=lambda r: -r["profit"])
    for i, r in enumerate(rows, 1): r["rank"] = i
    return rows

def adu_penalty(c, sqft=750, premium=250_000):
    """Same deal with a detached ADU added: +7 months, ARV + premium (observed SD range $150–300k)."""
    base = uw(price=c["price"], arv=c["arv"], mo=c["mo"], **c["kw"])["profit"]
    kw = dict(c["kw"]); kw["hard"] = kw.get("hard", 0) + sqft * 375; kw["soft"] = kw.get("soft", 0) + (45_000 if sqft <= 750 else 60_000)
    w = uw(price=c["price"], arv=c["arv"] + premium, mo=c["mo"] + 7, **kw)
    adu_cost = sqft * 375 * 1.10 + (45_000 if sqft <= 750 else 60_000)
    return dict(addr=c["addr"], base=base, with_adu=w["profit"], delta=w["profit"] - base, adu_cost=adu_cost, premium=premium)
