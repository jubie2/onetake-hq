"""v2 candidate specs. Metadata (status/facts/links) reused from the v1 research file; numbers restated as line items."""
import importlib.util, sys
spec = importlib.util.spec_from_file_location("v1", __import__("os").path.join(__import__("os").path.dirname(__file__), "..", "..", "2026-10-adu-flip", "model", "data.py"))
v1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v1)
META = {c["addr"]: c for c in v1.CANDIDATES}

def from_v1(addr, **over):
    c = META[addr]; kw = c["kw"]
    d = dict(addr=addr, area=c["area"], status=c["status"], plan=c["plan"], call=c["call"], risk=c["risk"],
             links=c["links"], facts=c["facts"], lot=c["lot"], zoning=c["zoning"], price=c["price"],
             resale=c["arv"], months=c["mo"], fin="flip", strategy="Flip", conf="M", flags=[])
    if c["kind"] == "flip":
        reno = kw.get("rehab", 0)
        d.update(renovation=reno, ae=0 if reno < 80_000 else 3_000, permits=2_000 if reno < 80_000 else 6_000)
        if kw.get("extra"): d["possession"] = kw["extra"]      # possession / tenant costs booked as site prep
    d.update(over)
    return d

C = []
add = C.append
# ---------- straight flips (from v1, line items restated) ----------
add(from_v1("3115 Natchez Ave (duplex)", strategy="Duplex flip", dead="SOLD $970,000 on 7/17/2026", price=970_000, resale=1_300_000, flags=["tenant", "unpermitted", "slope"]))
add(from_v1("3225 Logan Ave", conf="L", resale=735_000, renovation=1066*50, lot="~3,300–3,500 sf", zoning="RM-1-1 (Redfin) or R-4 (Compass)", status="Active $580K trust sale, no court approval (MLS 260020581, listed 8/21/2026); later status unconfirmed", flags=["unpermitted", "tenant"]))
add(from_v1("5800 Marengo Ave", dead="SOLD $801,550 on 8/31/2026 (14.5% over list)", price=801_550, resale=1_010_000, flags=["slope"]))
add(from_v1("2168 Leighton Ct", price=749_000, status="Active $749,000 (MLS PTP2604558, last updated 6/22/2026); the $649K probate price could not be confirmed", flags=["stale", "slope"]))
add(from_v1("9077 Covina St", dead="SOLD $1,050,000 on 7/23/2026 (16% over list)", price=1_050_000, resale=1_200_000, conf="M"))
add(from_v1("648 51st St", status="Active $600K, just reduced (early Oct 2026; MLS PTP2605868)", flags=["slope", "tenant"]))
add(from_v1("5789 Tex St", resale=880_000, status="Active $599K as of 9/21/2026 (cash only, trust-owned; raised from $499K)"))
add(from_v1("710 Eucalyptus St", conf="L", flags=["tenant", "unpermitted"]))
add(from_v1("805 51st St", flags=["auction", "stale"]))
add(from_v1("9371 Fermi Ave", dead="SOLD $830,000 on 9/28/2026", price=830_000, resale=945_000))
add(from_v1("4575 Dwight St", dead="SOLD $570,000 on 9/30/2026 after 67 days", price=570_000, resale=700_000))
add(from_v1("7265 Skyline Dr", dead="SOLD $500,000 on 8/12/2026, 13% UNDER its $575K list (probate fixer, 1,634 sf)", price=500_000, resale=800_000, renovation=1634*110, conf="M"))
add(from_v1("1854 Grove Rd", flags=["septic"]))
add(from_v1("2839 Emerald Dr", conf="L", flags=["stale"]))
add(from_v1("8474 Parkbrook St", flags=["tenant", "stale"]))
add(from_v1("4535 Bannock Ave", flags=["stale"]))
add(from_v1("6809 Ballinger Ave", flags=["stale"]))
add(from_v1("128 Old Oak Dr", flags=["stale"]))
add(from_v1("2987 Demeter Way"))
add(from_v1("3112 Luna Ave"))
add(from_v1("7443 Central Ave"))
add(from_v1("4627 Dwight St"))
add(from_v1("4858 Chateau Dr"))
add(from_v1("3106 Menlo Ave"))
add(from_v1("3041 Menlo Ave", flags=["slope"]))
add(from_v1("7059 Bullock Dr"))
add(from_v1("9035 Rohr", flags=["slope"]))
# ---------- existing house + new detached ADU (Strategy B) ----------
add(from_v1("1706 California St", strategy="House + ADU", renovation=912*110, build_adu=1000*325, ae=8_000, permits=52_000, conf="L", flags=["stale"]))
add(from_v1("6602 Crawford St", strategy="House + ADU", renovation=15_000, build_adu=800*335, ae=8_000, permits=42_000, flags=["stale"]))
add(from_v1("7205 Ballinger Ave", strategy="House + ADU", renovation=15_000, build_adu=1000*325, ae=8_000, permits=52_000, flags=["slope"]))
add(from_v1("5205 Tipton St", strategy="House + 2 ADUs", renovation=25_000, build_adu=175_000 + 1200*315, ae=12_000, permits=73_000, flags=["stale"]))
# ---------- land: build new and sell (Strategy A) ----------
L = dict(fin="land", strategy="Land → new build", conf="L")
add(from_v1("1105 Eucalyptus St", **L, price=600_000, status="Same parcel as 0 Clementine St: Active $600K (MLS 260005417SD). The $450K price (MLS 260022001) could not be confirmed", months=26, build_main=2400*450, build_adu=750*350, grading=200_000, ae=45_000, permits=150_000,
            flags=["slope", "retaining", "access", "utilities", "stale"], plan="New 2,400 sf house + 750 sf ADU on a hilltop pad"))
add(from_v1("2721 Lomita St (lot)", **L, months=24, build_main=2400*450, build_adu=750*350, grading=75_000, ae=35_000, permits=110_000, flags=["slope", "stale"]))
add(from_v1("216 Pajama Dr (lot)", **L, months=30, build_main=2*1800*400, build_adu=2*750*350, grading=60_000, ae=50_000, permits=200_000, flags=["permitting", "stale"]))
add(from_v1("0 Lake Murray Blvd (lot)", **L, months=26, build_main=2000*400, grading=100_000, ae=35_000, permits=85_000, flags=["slope", "utilities", "access"]))
add(from_v1("0 Dwight St (lot)", **L, resale=1_150_000, months=24, build_main=2000*400, grading=25_000, ae=30_000, permits=120_000, flags=["utilities"]))
add(from_v1("3195 Buena Vista Ave (burned shell)", **L, months=24, demo=45_000, build_main=1800*400, grading=25_000, ae=30_000, permits=85_000))
add(from_v1("2055 Riviera Dr (\"Vista Riviera\")", **L, months=26, build_main=1495*400, build_adu=1200*315, grading=60_000, ae=40_000, permits=190_000, flags=["septic", "utilities"]))
add(from_v1("8840 Leigh Ave (4.67 ac)", **L, months=36, build_main=1_440_000, ae=250_000, permits=500_000, flags=["permitting", "utilities"]))
add(from_v1("1822 Amalfi St", **L, months=30, build_main=4200*650, grading=350_000, build_adu=750*450, ae=120_000, permits=175_000,
            flags=["slope", "retaining", "permitting"]))

# ---------- new from land sweep (2026-10-21) ----------
def new(addr, area, status, price, resale, months, plan, links, facts, lot, zoning, fin="land", strategy="Land → new build", conf="L", flags=(), **items):
    d = dict(addr=addr, area=area, status=status, price=price, resale=resale, months=months, plan=plan, links=links,
             facts=facts, lot=lot, zoning=zoning, fin=fin, strategy=strategy, conf=conf, flags=list(flags), call="", risk="")
    d.update(items); return d

add(new("0 Cushman Ave #32", "Bay Park 92110", "Active $799K (listed 6/2/2026)", 799_000, 2_380_000, 24,
        "New 2,800 sf view house (resale at $850/sf)",
        [("Land listing", "https://www.landbrokermls.com/property/613055082/land-for-sale-in-san-diego-california"),
         ("Pending new build: 1826 Galveston $822/sf", "https://about.mlslistings.com/property/SD260009583")],
        ["Listing claims 7,000+ sf and a City preliminary review with no discretionary permit needed",
         "Bay Park new builds: 1826 Galveston (2024, 3,400 sf) PENDING $2.795M = $822/sf; 1860 Illion asking $3.0–3.25M. No closed new-build sale found",
         "Bay Park remodel sales: 2537 Grandview $1.85M (6/29/26), 2851 Grandview $1.65M (6/26/26)"],
        "7,000+ sf (claim)", "Unverified", build_main=2800*425, grading=100_000, ae=40_000, permits=110_000, flags=["slope"]))
add(new("4269 Hillside Dr", "Olde Carlsbad 92008", "Active $995K (MLS 260013644SD, listed 6/5/2026; likely relist of 4275 Hillside at $1.275M)", 995_000, 2_500_000, 24,
        "One new 3,200 sf house (resale at ~$780/sf). Lot-split upside not modeled",
        [("Listing", "https://obyrneteam.com/properties/4269-hillside-drive-unit-1-carlsbad-ca-us-92008-260013644"),
         ("Prior listing 4275 Hillside", "https://theboutiquere.com/properties/retsPdf/NDP2506068/4275-Hillside-Drive")],
        ["~0.79 ac (~34,400 sf), R-1; agent claims water, sewer and power on site",
         "Carlsbad sold data: KB townhome 2528 Delphinium $644/sf (5/2026); 1968 house 3245 Valley St $885/sf (1/2026). No closed new detached sale found"],
        "~34,400 sf", "R-1 (listing)", build_main=3200*425, grading=120_000, ae=45_000, permits=120_000, flags=["slope"]))
add(new("910 Windward Way", "Oceanside 92054 (west of I-5)", "Active $499K as of 5/12/2026 (58 days on market; status stale)", 499_000, 2_170_000, 24,
        "New 2,400 sf house ($780/sf) + 750 sf ADU (+$300K)",
        [("MLS record", "https://www.mlslistings.com/property/CRSB26058223"),
         ("Oceanside new build sold $745/sf: 2309 Loker Way", "https://www.coldwellbanker.com/ca/oceanside/2309-loker-way/lid-P00800000Gy0lTMVP8hHTkXAo5zjmIrFj9w1jQ7j")],
        ["6,910 sf; listing claims 3–4 units possible (zoning unverified)", "Cheapest coastal-side lot found at ~$72/sf; long market time hints at a problem",
         "Oceanside new builds: 2309 Loker Way SOLD $745/sf (12/2025); South O 1714 California asking $866/sf, 1716 California pending $778/sf"],
        "6,910 sf", "Unverified", build_main=2400*425, build_adu=750*350, grading=60_000, ae=40_000, permits=140_000, flags=["stale"]))
add(new("0 Pahvant St", "Loma Alta, Oceanside 92054", "Active $350K as of 5/20/2026 (MLS NDP2604708)", 350_000, 1_650_000, 26,
        "New 2,400 sf house (resale at $690/sf)",
        [("Listing", "https://www.houzeo.com/homes/0-pahvant-st-oceanside-ca-92054/hzid_9639038f")],
        ["7,100 sf, R-1, listing says sloping and set back from the street (possible flag lot)"],
        "7,100 sf", "R-1", build_main=2400*425, grading=180_000, ae=45_000, permits=110_000, flags=["slope", "retaining", "access", "stale"]))
add(new("1432 Buena St", "Oceanside 92058", "Active $650K (MLS NDP2602025)", 650_000, 1_450_000, 22,
        "New 2,200 sf house (resale at $660/sf)",
        [("MLS record", "https://www.mlslistings.com/property/CRNDP2602025")],
        ["4,756 sf, level, street + alley access; buyer to verify zoning and utilities", "Inland Oceanside new builds ask ~$440/sf (107 Metz Way); South O ~$780–866/sf"],
        "4,756 sf", "Unverified", build_main=2200*400, grading=25_000, ae=35_000, permits=100_000))
add(new("0 Vale Terrace", "Vista 92084", "Active $364,950 (MLS NDP2505605; on market since 6/2025, cut from $383,500)", 364_950, 1_400_000, 24,
        "New 2,600 sf house (resale at $540/sf)",
        [("MLS record", "https://about.mlslistings.com/property/CRNDP2505605")],
        ["0.54 ac rough-graded pad; agent claims utilities at the driveway", "Vista new build 763 Michael Ct sold 3/2026 at $450–532/sf (sources conflict)"],
        "23,522 sf", "Unverified", build_main=2600*400, grading=40_000, ae=35_000, permits=110_000, flags=["utilities"]))
add(new("0 Harness St (2 lots)", "Spring Valley 91977 (County)", "Active $425K (listed 8/6/2026)", 425_000, 1_800_000, 26,
        "Two new 2,000 sf houses (resale at $450/sf)",
        [("Listing", "https://www.weichert.com/137307376/"), ("Sold land comp: 8619 Tyler $254K", "https://contentcodes3.realgeeks.com/property/260014452/")],
        ["2 contiguous lots, 0.65 ac total, R1, corner of Harness St and Sweetwater Rd", "Spring Valley new builds ask $344–728/sf; no closed new-build sale found"],
        "0.65 ac", "R1", build_main=2*2000*400, grading=60_000, ae=50_000, permits=190_000, flags=["utilities"]))
add(new("1668 Ocala Ave", "Chula Vista 91911", "Active $650K as of 6/4/2026 (MLS SD260013409)", 650_000, 800_000, 6,
        "Medium rehab flip of the 1,028 sf house (ADU/SB 9 upside not modeled)",
        [("MLS record", "https://www.mlslistings.com/property/SD260013409")],
        ["1967 house, 3 bd / 1.5 ba, 1,028 sf on 0.29 ac (~12,600 sf), 2-car garage; first sale in ~30 years", "No Chula Vista sold comps pulled; resale is a low-confidence estimate"],
        "~12,600 sf", "Unverified", fin="flip", strategy="Flip", renovation=1028*110, ae=3_000, permits=6_000, flags=["stale"]))

# ---------- named leads round 2 ----------
add(new("Trenton Ave lot (1 of 8)", "Bay Park 92117", "Stale: marketing dates to Aug 2025 (MLS PTP2506586); lots asked $224K–$499K each; seller prefers 4 or 8 together; package asks conflict ($700K vs $2.999M)", 274_000, 1_500_000, 26,
        "One ~1,800 sf multi-level house on a ~3,000 sf lot + share of a new driveway",
        [("Listing (APN 425-042-24 to -31)", "https://www.showcase.com/0-trenton-avenue-san-diego-ca-92117/37460648/"),
         ("Coldwell Banker", "https://www.coldwellbanker.com/ca/san-diego/trenton-ave/lid-P00800000GxbnFxFSP1N9kPXYhZ7uxFmKQYEjYRg")],
        ["8 lots, ~3,000 sf each (24,283 sf total), APNs 425-042-24 to -31", "Access only from Ticonderoga St via a driveway that 'will be' built; Trenton is likely an unimproved paper street",
         "Bay Park new builds sit unsold: 1850 Illion (3,008 sf) asking $2.85–3.25M; Tonopah townhomes cut to $1.94M"],
        "~3,000 sf", "R-1 per aggregator (city zone unverified)", build_main=1800*475, grading=180_000, ae=45_000, permits=150_000,
        flags=["slope", "retaining", "access", "utilities", "permitting", "stale"]))
add(new("0 Madrigal St", "Rancho Peñasquitos 92129", "Active $549K (MLS PTP2603772, listed 5/15/2026)", 549_000, 1_600_000, 24,
        "New 2,299 sf two-story house (seller's proposed plans)",
        [("Listing", "https://www.houzeo.com/homes/0-madrigal-st-san-diego-ca-92129/hzid_37e24de5")],
        ["5,248 sf, no HOA, Poway Unified schools", "Listing notes a 'private water source', which is unusual inside the City: confirm water and sewer service",
         "PQ sold: 12930 Salmon River Rd $1.441M (light update); remodels asking $1.25–1.27M; no new-build sale found"],
        "5,248 sf", "Unverified", build_main=2299*400, grading=40_000, ae=35_000, permits=110_000, flags=["utilities"]))
add(new("333 S Euclid Ave", "Valencia Park 92114", "Fixer asking $649,999 (date unverified). Possible mix-up with the '3724–30 Euclid' lead, which could not be found", 649_999, 760_000, 6,
        "Medium rehab flip of a 3 bd / 1 ba house (ADU possible per listing)",
        [("Listing", "https://www.neighborhoods.com/ca/san-diego/333-s-euclid-ave/property/40686821")],
        ["3 bd / 1 ba fixer, 'ADU possible' (claim); size and lot unverified", "92114 remodel sales: 5454 Roswell $730K, 5533 Roswell $750K (spring 2026)"],
        "Unverified", "Unverified", fin="flip", strategy="Flip", renovation=1200*110, ae=3_000, permits=6_000, flags=["stale"]))

# ---------- Strategy B buy-box finds (2026-10-21 sweep) ----------
def house(addr, area, status, price, resale, months, plan, links, facts, lot, zoning, reno, conf="L", flags=("stale",), **kw):
    return new(addr, area, status, price, resale, months, plan, links, facts, lot, zoning, fin="flip", strategy="Flip",
               conf=conf, flags=flags, renovation=reno, ae=0 if reno < 80_000 else 3_000, permits=2_000 if reno < 80_000 else 6_000, **kw)
add(house("6511 Wunderlin Ave", "Encanto 92114", "Active $764,900 (MLS NDP2608910, 7 days on market as of 9/24/2026)", 764_900, 790_000, 6,
    "Medium rehab flip", [("Listing", "https://www.rubyhome.com/idx/6511-wunderlin-ave-san-diego-ca-92114/420632808_spid/")],
    ["3 bd / 2 ba, 1,133 sf, built 1935, ~0.2 ac (~8,700 sf, unconfirmed)", "Assumable VA loan at 5.5% (owner-occupant angle)",
     "92114 remodel sales $730–750K (5454 / 5533 Roswell); house + ADU ceiling ~$0.9–1.1M"], "~8,700 sf", "Unverified", 1133*110, flags=["slope"]))
add(house("2462 44th St", "City Heights 92105", "$659K 'For Sale' (MLS 260015904SD, ~early Oct); relisted after $739K → $699K → $639K snapshots", 659_000, 705_000, 5,
    "Cosmetic flip", [("MLS record (earlier)", "https://www.mlslistings.com/property/SD260012985"), ("Listing", "https://www.neighborhoods.com/ca/san-diego/2462-44th-st/property/82821")],
    ["2 bd / 1 ba, 837 sf, built 1957, 7,115 sf lot, 'canyon setting'", "Already has an updated kitchen and dual-pane windows",
     "Comp: 4417 Dwight remodeled 2/2 809 sf sold $720K (3/2026)"], "7,115 sf", "Unverified", 837*50, flags=["slope"]))
add(house("296 Southern Rd", "El Cajon 92020", "$650K (MLS SW26070260); status unverified", 650_000, 690_000, 5,
    "Cosmetic flip", [("Listing", "https://jamesoutland.net/ca/el-cajon/el-cajon/296-southern-rd")],
    ["2 bd / 1 ba, 819 sf, built 1951, 7,000 sf lot, 'well-maintained'", "No El Cajon renovated or ADU sold comps pulled"], "7,000 sf", "Unverified", 819*50))
add(house("5436 Division St", "Valencia Park 92114", "$725K (MLS 260015257SD, 9 days on market 6/23/2026); likely stale", 725_000, 770_000, 5,
    "Cosmetic flip", [("Listing", "https://www.rubyhome.com/idx/5436-division-st-san-diego-ca-92114/1803972911_spid/")],
    ["3 bd / 2 ba, 1,095 sf, built 1953, 5,800 sf lot, R-1, side access for parking", "Flooring and baths already upgraded"], "5,800 sf", "R-1 (listing)", 1095*50))
add(house("2463 Rancho Dr", "Paradise Hills 92139", "$720K (MLS PTP2604718, updated 6/22/2026); likely stale", 720_000, 830_000, 6,
    "Medium rehab flip", [("Listing", "https://www.rubyhome.com/idx/2463-rancho-dr-san-diego-ca-92139/420173400_spid/")],
    ["3 bd / 2 ba, 1,185 sf, built 1948, 'sweat equity' fixer, 'expansive' lot (street avg ~7,074 sf)", "Agent claims R-2 zoning",
     "Comp: 3107 Mt Miguel Dr 4/2 1,712 sf sold $835K (6/2026); Paradise Hills median ~$750K"], "~7,000 sf (unconfirmed)", "R-2 (claim)", 1185*110))
add(house("7060 Glenroy St", "Allied Gardens / Del Cerro 92120", "Active $790K after a $9K cut, 28 days on market", 790_000, 900_000, 5,
    "Cosmetic flip (attached garage could become a conversion ADU)", [("Listing", "https://contentcodes3.realgeeks.com/property/260019104/")],
    ["2 bd / 1 ba, 910 sf, built 1956, 2-car attached garage; lot unknown", "92120 fixer comp: 4633 Rainier Ave sold $850K (7/6/2026); 92120 sales $865–975K",
     "7173 Eldridge (house + new 2-bed ADU) sold $1.5M (12/31/2025)"], "Unverified", "Unverified", 910*50, conf="M", flags=["slope"]))
add(house("2424 Washington St", "Lemon Grove 91945", "$839K (page updated 9/29/2026)", 839_000, 900_000, 5,
    "Light refresh; has pre-approved plans for a 1,200 sf ADU", [("Listing", "https://www.rubyhome.com/idx/2424-washington-st-lemon-grove-ca-91945/1808833014_spid/")],
    ["3 bd / 2.5 ba, 1,972 sf, built 1949, paid-off solar, 200A panel", "Pre-approved plans for a 1,200 sf ADU (claim)"], "Unverified", "Unverified", 1972*30))

# ---------- SB 1123 small-lot subdivision plays (vacant SF-zoned lot <= 1.5 ac, up to 10 for-sale homes, ministerial 60-day map) ----------
add(new("4269 Hillside Dr — SB 1123 (8 homes)", "Olde Carlsbad 92008", "Active $995K (MLS 260013644SD, listed 6/5/2026). Same lot as the single-house row",
        995_000, 8 * 1_090_000, 32,
        "SB 1123 small-lot subdivision: 8 detached ~1,600 sf homes (avg must stay ≤1,750 sf), sold individually at ~$1.09M (~$680/sf)",
        [("Listing", "https://obyrneteam.com/properties/4269-hillside-drive-unit-1-carlsbad-ca-us-92008-260013644"),
         ("City of SD IB 414 (SB 684/1123 maps)", "https://www.sandiego.gov/development-services/forms-publications/information-bulletins/414")],
        ["Verified comps: new 3-bed townhomes next door on Delphinium Ln sold $998K–$1.10M ($591–632/sf, May–Jul 2026); the same builder still has unsold homes at ~$1.0–1.15M",
         "Red flags from verification: likely inside the Coastal Zone (adjacent house needed CDP 99-24); tax records reference an unrecorded lot split of a 1.68-ac parcel with a 1946 house, so the legal lot may exceed SB 1123's 1.5-ac cap; lot has been marketed since 2022 ($1.025M → $1.275M → $995K)",
         "0.79 ac R-1 lot → eligible size for SB 1123 (≤1.5 ac). Must be 'substantially surrounded' by urban uses and outside the state Very High fire zone",
         "Carlsbad's own SB 1123 process and Coastal Zone status not verified; resale of small-lot new homes in 92008 has no sold comp (Carlsbad KB townhome sold $644/sf; Encinitas small-lot detached sold $1,056–1,148/sf)",
         "Equity need is far beyond $150K: this is a JV / Strategy D project"],
        "~34,400 sf", "R-1 (listing)", build_main=8*1600*375, grading=150_000, demo=480_000, ae=300_000, permits=8*75_000, main_sf=8*1600, entitle_mo=10,
        flags=["slope", "permitting", "resale_low", "unpermitted"]))
