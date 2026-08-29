# Flag a device only when its symbol points AWAY from the room it serves.
# Room centres are the ones surveyed earlier (the Rooms collector crashes this model).
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId,
                               BuiltInCategory as BIC)
from System.Collections.Generic import List
ROOMS1 = [('Bed-1', 1135.3, 106.7), ('Bath-1', 1141.8, 108.9), ('Closet', 1134.4, 99.6),
          ('Closet', 1134.8, 98.0), ('Bed-2', 1137.8, 91.3), ('Bath-2', 1146.7, 94.6),
          ('Family', 1148.6, 102.3), ('Kitchen', 1160.8, 114.2),
          ('Garage', 1176.6, 114.5), ('Garage', 1181.5, 116.8)]
ROOMS2 = [('Master Bed', 1138.1, 107.4), ('Master Bath', 1145.6, 111.0),
          ('W-I Closet', 1148.6, 106.5), ('Closet', 1135.8, 98.9),
          ('Bed-2', 1140.6, 92.9), ('Bath-2', 1147.7, 94.7),
          ('Family', 1159.7, 102.7), ('Kitchen', 1175.2, 111.5), ('Deck', 1184.4, 99.1)]
bad = []
good = 0
L = []
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
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
    dot = (f.X * vx + f.Y * vy) / m
    if dot < 0:
        bad.append(e)
        L.append('  WRONG %-9s %-14s (%.1f,%.1f) serves %-11s dot%.2f' % (
            e.Id.Value, e.Symbol.Family.Name[:14], p.X, p.Y, best[0], dot))
    else:
        good += 1
ids = List[ElementId]([e.Id for e in bad])
uidoc.Selection.SetElementIds(ids)
out = ['%d devices point away from the room they serve; %d are fine' % (len(bad), good)]
out += L
out.append('ids: %s' % ','.join(str(e.Id.Value) for e in bad))
result = '\n'.join(out)
