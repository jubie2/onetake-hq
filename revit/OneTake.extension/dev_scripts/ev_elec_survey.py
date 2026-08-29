# Current electrical devices + counter runs + doors, per floor (no Rooms collector).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, BuiltInCategory as BIC,
                               XYZ as _XYZ, BuiltInParameter as BIP)
L = []
def zone(p): return (1120 < p.X < 1200 and 78 < p.Y < 128)
L.append('=== ELECTRICAL FIXTURES ===')
rows = []
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try: p = e.Location.Point
    except Exception: continue
    if p is None or not zone(p): continue
    fl = '1st' if p.Z < 10 else '2nd'
    rows.append((fl, p.X, '  %-3s %-9s (%.1f,%.1f,%5.2f)  %s' % (
        fl, e.Id.Value, p.X, p.Y, p.Z, e.Symbol.Family.Name)))
for r in sorted(rows): L.append(r[2])
L.append('=== LIGHTING ===')
rows = []
for e in FEC(doc).OfCategory(BIC.OST_LightingFixtures).WhereElementIsNotElementType():
    try: p = e.Location.Point
    except Exception: continue
    if p is None or not zone(p): continue
    fl = '1st' if p.Z < 10 else '2nd'
    rows.append((fl, p.X, '  %-3s %-9s (%.1f,%.1f,%5.2f)  %s' % (
        fl, e.Id.Value, p.X, p.Y, p.Z, e.Symbol.Family.Name[:26])))
for r in sorted(rows): L.append(r[2])
L.append('=== COUNTERS (bbox) ===')
for e in FEC(doc).OfCategory(BIC.OST_Casework).WhereElementIsNotElementType():
    bb = e.get_BoundingBox(None)
    if bb is None: continue
    c = _XYZ((bb.Min.X + bb.Max.X) / 2, (bb.Min.Y + bb.Max.Y) / 2, bb.Min.Z)
    if not zone(c): continue
    L.append('  %-9s z%5.2f (%.1f,%.1f)-(%.1f,%.1f)  %s' % (
        e.Id.Value, bb.Min.Z, bb.Min.X, bb.Min.Y, bb.Max.X, bb.Max.Y,
        e.Symbol.Family.Name[:24]))
L.append('=== DOORS (swing side from FacingOrientation) ===')
rows = []
for e in FEC(doc).OfCategory(BIC.OST_Doors).WhereElementIsNotElementType():
    try: p = e.Location.Point
    except Exception: continue
    if p is None or not zone(p): continue
    try: f = e.FacingOrientation; h = e.HandOrientation
    except Exception: f = h = _XYZ(0, 0, 0)
    w = 0.0
    try: w = e.Symbol.get_Parameter(BIP.DOOR_WIDTH).AsDouble()
    except Exception: pass
    fl = '1st' if p.Z < 10 else '2nd'
    rows.append((fl, p.X, '  %-3s %-9s (%.1f,%.1f) w%.1f face(%.2f,%.2f) hand(%.2f,%.2f) %s' % (
        fl, e.Id.Value, p.X, p.Y, w, f.X, f.Y, h.X, h.Y, e.Symbol.Family.Name[:18])))
for r in sorted(rows): L.append(r[2])
result = '\n'.join(L)
