# Current facing state per device, judged against the room it serves.
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId,
                               BuiltInCategory as BIC)
ROOMS1 = [('Bed-1', 1135.3, 106.7), ('Bath-1', 1141.8, 108.9), ('Closet', 1134.4, 99.6),
          ('Closet', 1134.8, 98.0), ('Bed-2', 1137.8, 91.3), ('Bath-2', 1146.7, 94.6),
          ('Family', 1148.6, 102.3), ('Kitchen', 1160.8, 114.2),
          ('Garage', 1176.6, 114.5), ('Garage', 1181.5, 116.8)]
ROOMS2 = [('Master Bed', 1138.1, 107.4), ('Master Bath', 1145.6, 111.0),
          ('W-I Closet', 1148.6, 106.5), ('Closet', 1135.8, 98.9),
          ('Bed-2', 1140.6, 92.9), ('Bath-2', 1147.7, 94.7),
          ('Family', 1159.7, 102.7), ('Kitchen', 1175.2, 111.5), ('Deck', 1184.4, 99.1)]
L = []
stat = {'1st ok': 0, '1st bad': 0, '2nd ok': 0, '2nd bad': 0}
walls = {}
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try:
        p = e.Location.Point
        f = e.FacingOrientation
    except Exception:
        continue
    if p is None or not (1120 < p.X < 1200 and 78 < p.Y < 128): continue
    fl = '1st' if p.Z < 10 else '2nd'
    rooms = ROOMS1 if p.Z < 10 else ROOMS2
    best = None; bd = 1e9
    for (nm, rx, ry) in rooms:
        d = math.hypot(rx - p.X, ry - p.Y)
        if d < bd: bd = d; best = (nm, rx, ry)
    vx, vy = best[1] - p.X, best[2] - p.Y
    m = math.hypot(vx, vy) or 1.0
    dot = (f.X * vx + f.Y * vy) / m
    bad = dot < -0.35
    stat['%s %s' % (fl, 'bad' if bad else 'ok')] += 1
    if bad:
        try: hid = e.Host.Id.Value
        except Exception: hid = 0
        walls.setdefault(hid, []).append(e.Id.Value)
        L.append('  %s %-9s %-14s (%.1f,%.1f) %-11s flipped=%-5s host %s' % (
            fl, e.Id.Value, e.Symbol.Family.Name[:14], p.X, p.Y, best[0],
            e.FacingFlipped, hid))
out = ['%s' % stat, 'still wrong:']
out += L
out.append('--- hosts involved ---')
for hid, ids in sorted(walls.items()):
    w = doc.GetElement(ElementId(hid))
    nm = w.Name if w else '?'
    tot = 0
    for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
        try:
            if e.Host and e.Host.Id.Value == hid: tot += 1
        except Exception: pass
    out.append('  wall %-9s %-22s bad %d of %d hosted' % (hid, nm[:22], len(ids), tot))
result = '\n'.join(out)
