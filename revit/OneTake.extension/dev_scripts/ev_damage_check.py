# Did the curve-reversal experiment damage the north kitchen wall / its inserts?
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, Wall,
                               BuiltInCategory as BIC)
L = []
for wid in (2189148, 2189094, 2189181, 2194765, 2200152):
    w = doc.GetElement(ElementId(wid))
    L.append('wall %-9s %s' % (wid, 'MISSING' if w is None else w.Name[:26]))
L.append('--- walls near the north kitchen run (y 108..122, x 1127..1166) ---')
for w in FEC(doc).OfClass(Wall):
    try: c = w.Location.Curve
    except Exception: continue
    a = c.GetEndPoint(0); b = c.GetEndPoint(1)
    if not (1120 < (a.X + b.X) / 2 < 1200 and 78 < (a.Y + b.Y) / 2 < 128): continue
    if abs((a.Y + b.Y) / 2 - 115) > 9: continue
    L.append('  %-9s (%.2f,%.2f)->(%.2f,%.2f) orient(%.2f,%.2f) %s' % (
        w.Id.Value, a.X, a.Y, b.X, b.Y, w.Orientation.X, w.Orientation.Y, w.Name[:20]))
L.append('--- inserts that were in 2189148 ---')
for i in (2196306, 2227911, 2228011, 2228264):
    e = doc.GetElement(ElementId(i))
    if e is None:
        L.append('  %s MISSING' % i)
    else:
        try: h = e.Host.Id.Value
        except Exception: h = '?'
        p = e.Location.Point
        L.append('  %s %s at (%.1f,%.1f) host %s' % (
            i, e.Category.Name, p.X, p.Y, h))
n1 = n2 = 0
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try: p = e.Location.Point
    except Exception: continue
    if p is None or not (1120 < p.X < 1200 and 78 < p.Y < 128): continue
    if p.Z < 10: n1 += 1
    else: n2 += 1
L.append('devices now: %d 1st, %d 2nd' % (n1, n2))
result = '\n'.join(L)
