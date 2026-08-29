# Final selection: devices clearly pointing away from the room they serve.
# Skips Francis's own switch and any near-perpendicular (ambiguous) case.
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId,
                               BuiltInCategory as BIC)
from System.Collections.Generic import List
SKIP = set([2245614])                  # Francis placed / flipped this one himself
ROOMS1 = [('Bed-1', 1135.3, 106.7), ('Bath-1', 1141.8, 108.9), ('Closet', 1134.4, 99.6),
          ('Closet', 1134.8, 98.0), ('Bed-2', 1137.8, 91.3), ('Bath-2', 1146.7, 94.6),
          ('Family', 1148.6, 102.3), ('Kitchen', 1160.8, 114.2),
          ('Garage', 1176.6, 114.5), ('Garage', 1181.5, 116.8)]
ROOMS2 = [('Master Bed', 1138.1, 107.4), ('Master Bath', 1145.6, 111.0),
          ('W-I Closet', 1148.6, 106.5), ('Closet', 1135.8, 98.9),
          ('Bed-2', 1140.6, 92.9), ('Bath-2', 1147.7, 94.7),
          ('Family', 1159.7, 102.7), ('Kitchen', 1175.2, 111.5), ('Deck', 1184.4, 99.1)]
bad = []
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    if e.Id.Value in SKIP: continue
    try:
        p = e.Location.Point
        f = e.FacingOrientation
    except Exception:
        continue
    if p is None or not (1120 < p.X < 1200 and 78 < p.Y < 128): continue
    rooms = ROOMS1 if p.Z < 10 else ROOMS2
    best = None; bd = 1e9
    for (nm, rx, ry) in rooms:
        d = math.hypot(rx - p.X, ry - p.Y)
        if d < bd: bd = d; best = (nm, rx, ry)
    vx, vy = best[1] - p.X, best[2] - p.Y
    m = math.hypot(vx, vy) or 1.0
    if (f.X * vx + f.Y * vy) / m < -0.35:
        bad.append((e, best[0]))
ids = List[ElementId]([e.Id for (e, r) in bad])
uidoc.Selection.SetElementIds(ids)
by = {}
for (e, r) in bad:
    fl = '1st' if e.Location.Point.Z < 10 else '2nd'
    by[(fl, r)] = by.get((fl, r), 0) + 1
L = ['SELECTED %d devices to flip:' % len(bad)]
for k in sorted(by): L.append('   %s floor  %-12s x%d' % (k[0], k[1], by[k]))
result = '\n'.join(L)
