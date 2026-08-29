# Do the OLD Outlet-GFI / Outlet-Duplex instances carry FacingFlipped=True?
# (Evidence that the flip is achievable on this family, just not from the API
#  while the project is not the active document.)
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, BuiltInCategory as BIC)
pdoc = None
for d in doc.Application.Documents:
    if not d.IsFamilyDocument and 'Electric Ave' in d.Title: pdoc = d; break
tally = {}
for e in FEC(pdoc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try: p = e.Location.Point
    except Exception: continue
    if p is None: continue
    old = 940 < p.X < 1030 and -160 < p.Y < -80
    new = 1120 < p.X < 1200 and 78 < p.Y < 128
    if not (old or new): continue
    fam = e.Symbol.Family.Name
    key = ('OLD' if old else 'NEW', fam)
    d2 = tally.setdefault(key, {'flip': 0, 'noflip': 0})
    if e.FacingFlipped: d2['flip'] += 1
    else: d2['noflip'] += 1
L = []
for k in sorted(tally):
    L.append('  %-4s %-16s flipped=%-3d  not flipped=%d' % (
        k[0], k[1], tally[k]['flip'], tally[k]['noflip']))
result = '\n'.join(L)
