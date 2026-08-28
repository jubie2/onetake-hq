# Build ADU electrical plans: duplicate floor plans, place cans/outlets/switches/GFI,
# room-tag, swap onto A201; hide elec cats in non-elec plan views.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewSheet,
                               Viewport, ViewDuplicateOption, ElementId, XYZ as _XYZ,
                               UV, LinkElementId, FamilySymbol, Wall, Category,
                               BoundingBoxXYZ, BuiltInCategory as BIC,
                               BuiltInParameter as BIP, Line)
from Autodesk.Revit.DB.Structure import StructuralType
from System.Collections.Generic import List
L = []
def getview(nm):
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: return x
def sym_of(cat, fam, typ=None):
    for s in FEC(doc).OfClass(FamilySymbol).OfCategory(cat):
        if s.Family.Name == fam:
            if typ is None: return s
            if s.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() == typ: return s
    return None
can = sym_of(BIC.OST_LightingFixtures, 'Downlight - Recessed Can', '6" Incandescent - 120V')
dup = sym_of(BIC.OST_ElectricalFixtures, 'Outlet-Duplex')
gfi = sym_of(BIC.OST_ElectricalFixtures, 'Outlet-GFI')
sw = sym_of(BIC.OST_ElectricalFixtures, 'Switch-Single')
walls = []
for w in FEC(doc).OfClass(Wall):
    bb = w.get_BoundingBox(None)
    if bb and 1120 < (bb.Min.X + bb.Max.X) / 2 < 1200 and 80 < (bb.Min.Y + bb.Max.Y) / 2 < 128:
        try:
            c = w.Location.Curve
            walls.append((w, c))
        except Exception: pass
def near_wall(x, y, lvlid, maxd=3.5):
    best = None; bd = maxd
    for (w, c) in walls:
        try:
            if w.LookupParameter('Base Constraint').AsElementId() != lvlid: continue
        except Exception: pass
        pr = c.Project(_XYZ(x, y, 0))
        if pr and pr.Distance < bd:
            bd = pr.Distance; best = (w, pr.XYZPoint)
    return best
CANS1 = [(1135.3,106.7),(1137.8,91.3),(1144.6,98.3),(1144.6,106.3),(1152.6,98.3),
         (1152.6,106.3),(1158.8,112.2),(1162.8,116.2),(1141.8,108.9),(1146.7,94.6),
         (1176.6,114.5),(1181.5,116.8)]
CANS2 = [(1138.1,107.4),(1140.6,92.9),(1155.7,98.7),(1155.7,106.7),(1163.7,98.7),
         (1163.7,106.7),(1173.2,110.0),(1177.2,113.5),(1145.6,111.0),(1147.7,94.7),
         (1148.6,106.5)]
GFI1 = [(1156.5,118.3),(1158.5,118.3),(1160.5,118.3),(1162.5,118.3),(1164.5,118.3),
        (1140.3,110.5),(1145.2,96.3),(1176.6,111.0),(1181.5,113.0)]
GFI2 = [(1172.0,116.8),(1174.0,116.8),(1176.0,116.8),(1178.0,116.8),
        (1144.5,112.5),(1146.5,96.3)]
DUP1 = [(1129.7,104.5),(1134.0,110.2),(1129.7,92.5),(1135.0,89.5),(1146.0,92.7),
        (1156.0,96.8),(1149.0,110.0)]
DUP2 = [(1131.0,104.0),(1136.0,111.5),(1132.5,90.5),(1140.0,89.7),(1153.0,96.5),
        (1163.0,96.5),(1157.0,110.5)]
SW1 = [(1154.0,92.6),(1142.5,98.8),(1141.5,102.7),(1145.9,99.7),(1142.3,106.4),
       (1155.0,117.0),(1176.5,98.0),(1184.5,100.2)]
SW2 = [(1172.0,97.2),(1147.5,99.2),(1144.0,100.5),(1146.6,104.6),(1145.1,102.5),
       (1177.5,109.0)]
lvl1 = doc.GetElement(ElementId(30)); lvl2 = doc.GetElement(ElementId(1715859))
t = Transaction(doc, 'OneTake: ADU elec'); _prep(t); t.Start()
for s in [can, dup, gfi, sw]:
    if s and not s.IsActive: s.Activate()
doc.Regenerate()
wallphase = None
for (w, c) in walls:
    wallphase = w.CreatedPhaseId; break
stats = {'can': 0, 'gfi': 0, 'dup': 0, 'sw': 0, 'miss': 0}
def place_host(symb, pts, lvl, zoff, key):
    for (x, y) in pts:
        hit = near_wall(x, y, lvl.Id)
        if hit is None:
            stats['miss'] += 1; L.append('miss %s (%.1f,%.1f)' % (key, x, y)); continue
        w, pp = hit
        try:
            fi = doc.Create.NewFamilyInstance(
                _XYZ(pp.X, pp.Y, lvl.Elevation + zoff), symb, w, lvl,
                StructuralType.NonStructural)
            try: fi.get_Parameter(BIP.PHASE_CREATED).Set(wallphase)
            except Exception: pass
            stats[key] += 1
        except Exception as ex:
            L.append('fail %s %s' % (key, str(ex)[:40]))
for (pts, lvl) in [(CANS1, lvl1), (CANS2, lvl2)]:
    for (x, y) in pts:
        try:
            fi = doc.Create.NewFamilyInstance(_XYZ(x, y, lvl.Elevation + 8.5), can,
                                              lvl, StructuralType.NonStructural)
            try: fi.get_Parameter(BIP.PHASE_CREATED).Set(wallphase)
            except Exception: pass
            stats['can'] += 1
        except Exception as ex:
            L.append('can fail %s' % str(ex)[:40])
place_host(gfi, GFI1, lvl1, 3.0, 'gfi'); place_host(gfi, GFI2, lvl2, 3.0, 'gfi')
place_host(dup, DUP1, lvl1, 1.5, 'dup'); place_host(dup, DUP2, lvl2, 1.5, 'dup')
place_host(sw, SW1, lvl1, 3.8, 'sw'); place_host(sw, SW2, lvl2, 3.8, 'sw')
doc.Regenerate()
L.append('placed %s' % stats)
t.Commit()
result = '\n'.join(L)
