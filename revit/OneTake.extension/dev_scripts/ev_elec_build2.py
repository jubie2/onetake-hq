# Retry missed hosted placements using z-range wall matching.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, FamilySymbol, Wall,
                               ElementId, XYZ as _XYZ, BuiltInCategory as BIC,
                               BuiltInParameter as BIP)
from Autodesk.Revit.DB.Structure import StructuralType
L = []
def sym_of(cat, fam):
    for s in FEC(doc).OfClass(FamilySymbol).OfCategory(cat):
        if s.Family.Name == fam: return s
dup = sym_of(BIC.OST_ElectricalFixtures, 'Outlet-Duplex')
gfi = sym_of(BIC.OST_ElectricalFixtures, 'Outlet-GFI')
sw = sym_of(BIC.OST_ElectricalFixtures, 'Switch-Single')
walls = []
wallphase = None
for w in FEC(doc).OfClass(Wall):
    bb = w.get_BoundingBox(None)
    if bb and 1120 < (bb.Min.X + bb.Max.X) / 2 < 1200 and 80 < (bb.Min.Y + bb.Max.Y) / 2 < 128:
        try:
            c = w.Location.Curve
            walls.append((w, c, bb))
            if wallphase is None: wallphase = w.CreatedPhaseId
        except Exception: pass
def near_wall_z(x, y, z, maxd=3.5):
    best = None; bd = maxd
    for (w, c, bb) in walls:
        if not (bb.Min.Z - 0.5 < z < bb.Max.Z + 0.5): continue
        pr = c.Project(_XYZ(x, y, c.GetEndPoint(0).Z))
        if pr and pr.Distance < bd:
            bd = pr.Distance; best = (w, pr.XYZPoint)
    return best
lvl1 = doc.GetElement(ElementId(30)); lvl2 = doc.GetElement(ElementId(1715859))
JOBS = [
 (gfi, 3.0, lvl1, [(1181.5, 113.0)]),
 (gfi, 3.0, lvl2, [(1172.0, 116.8), (1174.0, 116.8), (1176.0, 116.8), (1178.0, 116.8),
                   (1144.5, 112.5), (1146.5, 96.3)]),
 (dup, 1.5, lvl1, [(1156.0, 96.8)]),
 (dup, 1.5, lvl2, [(1131.0, 104.0), (1136.0, 111.5), (1132.5, 90.5), (1140.0, 89.7),
                   (1153.0, 96.5), (1163.0, 96.5), (1157.0, 110.5)]),
 (sw, 3.8, lvl2, [(1172.0, 97.2), (1147.5, 99.2), (1144.0, 100.5), (1146.6, 104.6),
                  (1145.1, 102.5), (1177.5, 109.0)]),
]
t = Transaction(doc, 'OneTake: ADU elec 2'); _prep(t); t.Start()
n = 0; miss = 0
for (symb, zoff, lvl, pts) in JOBS:
    for (x, y) in pts:
        z = lvl.Elevation + zoff
        hit = near_wall_z(x, y, z)
        if hit is None:
            miss += 1; L.append('MISS (%.1f,%.1f) z%.1f' % (x, y, z)); continue
        w, pp = hit
        try:
            fi = doc.Create.NewFamilyInstance(_XYZ(pp.X, pp.Y, z), symb, w, lvl,
                                              StructuralType.NonStructural)
            try: fi.get_Parameter(BIP.PHASE_CREATED).Set(wallphase)
            except Exception: pass
            n += 1
        except Exception as ex:
            L.append('fail %s' % str(ex)[:50])
t.Commit()
L.append('placed %d, missed %d' % (n, miss))
result = '\n'.join(L)
