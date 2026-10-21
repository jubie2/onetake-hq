"""ADU size test: same house, ADU of 499 / 750 / 1,000 / 1,200 sf. Flip result vs no ADU, plus hold yield."""
from model import proforma
SIZES = [  # detached ADUs; conversions follow
    (400, "Garage conversion ADU ~400 sf", 300, 25_000, 4, 90_000, 1_900),
    (450, "JADU inside the house ~450 sf", 130, 12_000, 3, 50_000, 1_700),  # sf, label, $/sf build (GC), soft (A&E + permits/fees/utility), extra months, base premium (mid-tier), rent/mo
    (499, "1bd 499 sf", 425, 36_000, 6, 130_000, 2_200),
    (750, "2bd 750 sf", 375, 48_000, 7, 175_000, 2_650),
    (1000, "2bd/2ba 1,000 sf", 350, 70_000, 7, 200_000, 2_900),
    (1200, "3bd 1,200 sf", 340, 85_000, 8, 215_000, 3_300),
]
def test(d, tier=1.0, owner_builder=False):
    base = proforma(d)["profit"]; out = []
    for sf, label, psf, soft, xm, prem, rent in SIZES:
        psf_used = psf * (0.82 if owner_builder else 1.0)
        dd = dict(d, build_adu=d.get("build_adu", 0) + sf * psf_used, permits=d.get("permits", 0) + soft,
                  resale=d["resale"] + prem * tier, months=d["months"] + xm)
        p = proforma(dd)["profit"]
        adu_cost = sf * psf_used * 1.10 + soft
        out.append(dict(sf=sf, label=label, flip=p, delta=p - base, adu_cost=adu_cost, premium=prem * tier,
                        rent=rent * tier, gross_yield=rent * tier * 12 / adu_cost))
    return base, out

LOW = ("92105", "92113", "92114", "92139", "El Cajon", "Lemon Grove", "Chula Vista", "91945", "91977", "92020", "92021", "91910", "91911")
HIGH = ("92119", "92120", "91942", "Bay Park", "92117", "92110", "Carlsbad", "Oceanside 92054")
def tier(area):
    if any(t in area for t in HIGH): return 1.15
    if any(t in area for t in LOW): return 0.80
    return 1.0
