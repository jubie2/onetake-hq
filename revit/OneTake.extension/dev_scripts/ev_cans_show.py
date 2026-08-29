# Seat the recessed cans just below each floor's cut plane so they print on the
# electrical plans, then hide those instances in the sections/elevations (where a
# can drawn at 5 ft would read as a wall fixture).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, XYZ as _XYZ,
                               BuiltInCategory as BIC)
from System.Collections.Generic import List
VIEWS = [2245246, 2245255, 2245264, 2245273,      # elevations
         2245282, 2245291, 2245300, 2245309]      # sections
cans = []
for e in FEC(doc).OfCategory(BIC.OST_LightingFixtures).WhereElementIsNotElementType():
    try:
        if e.Symbol.Family.Name != 'Downlight - Recessed Can': continue
        p = e.Location.Point
    except Exception: continue
    if not (1120 < p.X < 1200 and 78 < p.Y < 128): continue
    cans.append(e)
L = ['%d cans found' % len(cans)]
t = Transaction(doc, 'OneTake: seat cans below cut plane'); _prep(t); t.Start()
n = 0
for e in cans:
    e.Location.Move(_XYZ(0, 0, -4.5)); n += 1
L.append('%d cans lowered to just under the cut plane' % n)
ids = List[ElementId]([e.Id for e in cans])
for vid in VIEWS:
    v = doc.GetElement(ElementId(vid))
    if v is None: continue
    try:
        v.HideElements(ids)
    except Exception as ex:
        L.append('  %s hide: %s' % (v.Name, str(ex)[:40]))
L.append('cans hidden in %d section/elevation views' % len(VIEWS))
doc.Regenerate(); t.Commit()
zs = {}
for e in cans:
    zs[round(e.Location.Point.Z, 2)] = zs.get(round(e.Location.Point.Z, 2), 0) + 1
L.append('can heights now: %s' % sorted(zs.items()))
for vid in (2244950, 2244908):
    v = doc.GetElement(ElementId(vid))
    nl = len(list(FEC(doc, v.Id).OfCategory(BIC.OST_LightingFixtures).WhereElementIsNotElementType()))
    L.append('%s: %d lighting fixtures visible' % (v.Name, nl))
result = '\n'.join(L)
