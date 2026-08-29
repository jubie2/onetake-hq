# Select every device sitting on the outside face of its wall, so Francis can flip
# the whole lot in one go (spacebar / the flip arrows).
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, XYZ as _XYZ,
                               BuiltInCategory as BIC)
from System.Collections.Generic import List
CENX, CENY = 1157.520, 104.867
def inward_ok(e):
    p = e.Location.Point
    f = e.FacingOrientation
    try:
        c = e.Host.Location.Curve
        a0 = c.GetEndPoint(0); b0 = c.GetEndPoint(1)
        dx, dy = b0.X - a0.X, b0.Y - a0.Y
        m = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / m, dx / m
        if nx * (CENX - p.X) + ny * (CENY - p.Y) < 0: nx, ny = -nx, -ny
    except Exception:
        nx, ny = CENX - p.X, CENY - p.Y
        m = math.hypot(nx, ny) or 1.0
        nx, ny = nx / m, ny / m
    return (f.X * nx + f.Y * ny) >= 0
out = []
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try: p = e.Location.Point
    except Exception: continue
    if p is None or not (1120 < p.X < 1200 and 78 < p.Y < 128): continue
    if not inward_ok(e): out.append(e)
ids = List[ElementId]([e.Id for e in out])
uidoc.Selection.SetElementIds(ids)
by = {}
for e in out:
    fl = '1st floor' if e.Location.Point.Z < 10 else '2nd floor'
    k = (fl, e.Symbol.Family.Name)
    by[k] = by.get(k, 0) + 1
L = ['SELECTED %d devices that face outward:' % len(out)]
for k in sorted(by): L.append('   %-10s %-15s x%d' % (k[0], k[1], by[k]))
L.append('ids: %s' % ','.join(str(e.Id.Value) for e in out))
result = '\n'.join(L)
