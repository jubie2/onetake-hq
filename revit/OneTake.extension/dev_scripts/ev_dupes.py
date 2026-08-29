# Find electrical devices stacked on top of each other (within 0.6 ft, same floor).
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, BuiltInCategory as BIC)
items = []
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try: p = e.Location.Point
    except Exception: continue
    if p is None or not (1120 < p.X < 1200 and 78 < p.Y < 128): continue
    items.append((e, p))
L = []
seen = set()
for i in range(len(items)):
    for j in range(i + 1, len(items)):
        e1, p1 = items[i]; e2, p2 = items[j]
        if abs(p1.Z - p2.Z) > 2.0: continue
        d = math.hypot(p1.X - p2.X, p1.Y - p2.Y)
        if d < 0.6:
            L.append('  %s %-14s and %s %-14s  %.2f ft apart at (%.1f,%.1f,%.1f)' % (
                e1.Id.Value, e1.Symbol.Family.Name[:14],
                e2.Id.Value, e2.Symbol.Family.Name[:14], d, p1.X, p1.Y, p1.Z))
            seen.add(e1.Id.Value); seen.add(e2.Id.Value)
out = ['%d overlapping pairs' % len(L)]
out += L
n1 = len([1 for (e, p) in items if p.Z < 10])
n2 = len(items) - n1
out.append('totals: %d 1st, %d 2nd' % (n1, n2))
result = '\n'.join(out)
