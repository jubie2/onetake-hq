"""Financing comparison for one deal: (1) hard money, own cash; (2) JV partner funds equity; (3) owner-occupied FHA 203(k) duplex hold-then-sell."""
from model import proforma

def pmt(principal, rate, years=30):
    r = rate / 12; n = years * 12
    return principal * r / (1 - (1 + r) ** -n)

def compare(d, price):
    b = proforma(d, price)
    hm = dict(name="Hard money, your cash", equity=b["equity"], profit=b["profit"], yours=b["profit"], coc=b["profit"] / b["equity"], months=b["months"])
    jv_split = dict(name="JV: partner funds 100% of equity, 10%/yr pref, then 50/50", equity=0, profit=b["profit"], yours=b["jv_sponsor"],
                    partner=b["jv_partner"], months=b["months"])
    return b, hm, jv_split

def fha_duplex(price, rehab, resale, rent_other, rate=0.069, years_held=2, appreciation=0.0):
    """Owner-occupant FHA Standard 203(k) on a 2-unit: 3.5% down, UFMIP 1.75% financed, MIP 0.55%/yr."""
    base = price + rehab
    down = 0.035 * base
    loan = (base - down) * 1.0175
    close = 0.025 * price
    p_i = pmt(loan, rate)
    mip = (0.0075 if loan > 726_200 else 0.0055) * loan / 12
    tax = 0.012 * price / 12
    ins = 250
    piti = p_i + mip + tax + ins
    net_housing = piti - rent_other
    reserves = 3 * piti
    # balance after N years
    r = rate / 12; n = 360; k = years_held * 12
    bal = loan * ((1 + r) ** n - (1 + r) ** k) / ((1 + r) ** n - 1)
    sale = resale * (1 + appreciation) ** years_held
    proceeds = sale * (1 - 0.065) - bal
    cash_in = down + close
    cash_needed = cash_in + reserves
    gain_after_housing = proceeds - cash_in - net_housing * 12 * years_held
    return dict(base=base, down=down, close=close, cash_in=cash_in, reserves=reserves, cash_needed=cash_needed, loan=loan, piti=piti, rent=rent_other, net_housing=net_housing,
                income_needed=(piti - 0.75 * rent_other) / 0.47 * 12, sale=sale, payoff=bal, proceeds=proceeds, gain=gain_after_housing)
