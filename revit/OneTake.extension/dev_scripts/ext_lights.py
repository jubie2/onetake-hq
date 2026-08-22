# Place exterior wall lights on the ADU (none existed) so elevation keynote 5 has something real.
# args {"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, Wall, Level, FamilySymbol,
                               BuiltInParameter as BIP, BuiltInCategory as BIC, XYZ as _XYZ)
from Autodesk.Revit.DB.Structure import StructuralType
dry = args.get('dry', True)
L = []
sym = None
for s in FEC(doc).OfClass(FamilySymbol):
    try:
        if s.Category is None or s.Category.Id.IntegerValue != int(BIC.OST_LightingFixtures): continue
        if s.Family.Name == 'Antique_Doorwall_lamp_10251': sym = s; break
    except Exception: pass
L.append('symbol: %s' % (sym.Id if sym else 'NOT FOUND'))
# the ADU perimeter walls, per level
WANT = [(1186.5, -138.4, 'east wall by the entry door'),
        (1157.9, -145.0, 'west wall by the stair')]
lv = {}
for l in FEC(doc).OfClass(Level):
    if l.Name in ('1st Floor Level', '2nd FLoor Plan'): lv[l.Name] = l
jobs = []
for lname in ('1st Floor Level', '2nd FLoor Plan'):
    lev = lv[lname]
    for wx, wy, why in WANT:
        host = None; bestd = 99
        for w in FEC(doc).OfClass(Wall):
            try:
                if doc.GetElement(w.LevelId).Name != lname: continue
                if str(w.WallType.Function) != 'Exterior': continue
                c = w.Location.Curve
                p = c.Project(_XYZ(wx, wy, c.GetEndPoint(0).Z)).XYZPoint
                d = ((p.X - wx) ** 2 + (p.Y - wy) ** 2) ** 0.5
                if d < bestd: bestd = d; host = w
            except Exception: pass
        if host is None: continue
        jobs.append((lev, host, _XYZ(wx, wy, lev.Elevation + 6.5), lname, why, bestd))
for lev, host, p, lname, why, d in jobs:
    L.append('  %-16s %-32s at (%.1f, %.1f, %.1f)  wall %s (%.2f ft off)' % (
        lname, why, p.X, p.Y, p.Z, host.Id, d))
if not dry and sym:
    t = Transaction(doc, 'OneTake: ADU exterior lights'); _prep(t); t.Start()
    if not sym.IsActive: sym.Activate()
    doc.Regenerate()
    n = 0
    for lev, host, p, lname, why, d in jobs:
        try:
            doc.Create.NewFamilyInstance(p, sym, host, lev, StructuralType.NonStructural); n += 1
        except Exception as ex:
            L.append('    fail %s' % str(ex)[:60])
    doc.Regenerate(); t.Commit()
    L.append('placed %d exterior lights' % n)
result = '\n'.join(L)
