# Electrical rework:
#  1. drop every recessed can 2.67 ft - they sat above their floor's view range,
#     so the 1st-floor cans were printing on the 2nd-floor plan
#  2. add the missing switches at doors + kitchen GFIs every ~2 ft along the counter
#  3. draw the switch-leg wires (curved) from each switch across to the fixture it runs
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, FamilySymbol, Wall,
                               ElementId, XYZ as _XYZ, Arc, GraphicsStyle,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
from Autodesk.Revit.DB.Structure import StructuralType
L = []
V1, V2 = 2244950, 2244908          # 1st / 2nd floor electrical views
def sym_of(cat, fam):
    for s in FEC(doc).OfClass(FamilySymbol).OfCategory(cat):
        if s.Family.Name == fam: return s
gfi = sym_of(BIC.OST_ElectricalFixtures, 'Outlet-GFI')
sw = sym_of(BIC.OST_ElectricalFixtures, 'Switch-Single')
walls = []
wallphase = None
for w in FEC(doc).OfClass(Wall):
    bb = w.get_BoundingBox(None)
    if bb is None: continue
    cx = (bb.Min.X + bb.Max.X) / 2.0; cy = (bb.Min.Y + bb.Max.Y) / 2.0
    if not (1120 < cx < 1200 and 78 < cy < 128): continue
    try:
        walls.append((w, w.Location.Curve, bb))
        if wallphase is None: wallphase = w.CreatedPhaseId
    except Exception: pass
def near_wall(x, y, z, maxd=4.0):
    best = None; bd = maxd
    for (w, c, bb) in walls:
        if not (bb.Min.Z - 0.5 < z < bb.Max.Z + 0.5): continue
        pr = c.Project(_XYZ(x, y, c.GetEndPoint(0).Z))
        if pr and pr.Distance < bd:
            bd = pr.Distance; best = (w, pr.XYZPoint)
    return best
lvl1 = doc.GetElement(ElementId(30)); lvl2 = doc.GetElement(ElementId(1715859))
# new devices: (symbol, level, z-offset, [(x,y)...])
NEW = [
 (sw,  lvl1, 3.80, [(1141.8, 105.6)]),                       # Bath-1 switch at its door
 (sw,  lvl2, 3.80, [(1141.6, 109.2)]),                       # Master Bed switch at its door
 (gfi, lvl1, 3.00, [(1166.0, 111.9), (1165.5, 113.9), (1165.0, 115.8)]),   # kitchen east leg
 (gfi, lvl2, 3.00, [(1169.7, 118.1), (1177.3, 118.4)]),                    # kitchen infill
]
# switch-leg wires: (switch xy) -> (fixture xy)
W1 = [((1140.9, 106.0), (1135.3, 106.7)), ((1141.5, 102.9), (1144.6, 106.3)),
      ((1142.5, 99.0), (1137.8, 91.3)),   ((1145.9, 99.9), (1146.7, 94.6)),
      ((1153.9, 92.8), (1152.6, 98.3)),   ((1154.9, 117.4), (1158.8, 112.2)),
      ((1176.9, 96.6), (1176.6, 114.5)),  ((1184.9, 98.6), (1181.5, 116.8)),
      ((1141.8, 105.6), (1141.8, 108.9))]
W2 = [((1142.4, 100.1), (1140.6, 92.9)),  ((1145.0, 102.8), (1148.6, 106.5)),
      ((1146.9, 103.3), (1155.7, 106.7)), ((1147.4, 99.4), (1147.7, 94.7)),
      ((1172.4, 95.5), (1163.7, 98.7)),   ((1178.0, 109.1), (1173.2, 110.0)),
      ((1141.6, 109.2), (1138.1, 107.4))]
dash = None
for g in FEC(doc).OfClass(GraphicsStyle):
    n = (g.Name or '').lower()
    if 'hidden' in n or 'dash' in n: dash = g; break
t = Transaction(doc, 'OneTake: electrical rework'); _prep(t); t.Start()
for s in (gfi, sw):
    if s is not None and not s.IsActive: s.Activate()
doc.Regenerate()
# --- 1. drop the recessed cans into their own floor's view range ---
nc = 0
for e in FEC(doc).OfCategory(BIC.OST_LightingFixtures).WhereElementIsNotElementType():
    try:
        if e.Symbol.Family.Name != 'Downlight - Recessed Can': continue
        p = e.Location.Point
    except Exception:
        continue
    if not (1120 < p.X < 1200 and 78 < p.Y < 128): continue
    e.Location.Move(_XYZ(0, 0, -2.67)); nc += 1
L.append('%d recessed cans lowered 2.67 ft' % nc)
# --- 2. new switches + kitchen GFIs ---
na = 0
for symb, lvl, zoff, pts in NEW:
    for (x, y) in pts:
        z = lvl.Elevation + zoff
        hit = near_wall(x, y, z)
        if hit is None:
            L.append('  no wall for (%.1f,%.1f) z%.1f' % (x, y, z)); continue
        w, pp = hit
        try:
            fi = doc.Create.NewFamilyInstance(_XYZ(pp.X, pp.Y, z), symb, w, lvl,
                                              StructuralType.NonStructural)
            try: fi.get_Parameter(BIP.PHASE_CREATED).Set(wallphase)
            except Exception: pass
            na += 1
        except Exception as ex:
            L.append('  place fail %s' % str(ex)[:40])
L.append('%d new switches / GFIs placed' % na)
doc.Regenerate()
# --- 3. switch-leg wires ---
for vid, wires in ((V1, W1), (V2, W2)):
    v = doc.GetElement(ElementId(vid))
    kill = []
    for e in FEC(doc, v.Id).OfCategory(BIC.OST_Lines).WhereElementIsNotElementType():
        if e.OwnerViewId == v.Id: kill.append(e.Id)
    if kill:
        from System.Collections.Generic import List as GList
        doc.Delete(GList[ElementId](kill))
    doc.Regenerate()
    n = 0
    for (a, b) in wires:
        ax, ay = a; bx, by = b
        mx, my = (ax + bx) / 2.0, (ay + by) / 2.0
        dx, dy = bx - ax, by - ay
        d = math.hypot(dx, dy) or 1.0
        # bow the wire out perpendicular to the run
        px, py = -dy / d, dx / d
        bulge = min(2.2, max(0.9, d * 0.16))
        try:
            arc = Arc.Create(_XYZ(ax, ay, 0), _XYZ(bx, by, 0),
                             _XYZ(mx + px * bulge, my + py * bulge, 0))
            ce = doc.Create.NewDetailCurve(v, arc)
            if dash:
                try: ce.LineStyle = dash
                except Exception: pass
            n += 1
        except Exception as ex:
            L.append('  wire fail %s' % str(ex)[:40])
    L.append('%s: %d switch legs drawn' % (v.Name, n))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
