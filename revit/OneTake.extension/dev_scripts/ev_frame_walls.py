# WALLS-ONLY building frame (no Rooms/Areas - those recurse and crash this model).
# u = along the 14.3 deg walls (bldg east), v = 104.3 deg (bldg north).
import math
from Autodesk.Revit.DB import FilteredElementCollector as FEC, Wall
A = math.radians(14.3)
ux, uy = math.cos(A), math.sin(A)
vx, vy = -math.sin(A), math.cos(A)
pts = []
for w in FEC(doc).OfClass(Wall):
    try:
        c = w.Location.Curve
    except Exception:
        continue
    a = c.GetEndPoint(0); b = c.GetEndPoint(1)
    for p in (a, b):
        if 1120 < p.X < 1200 and 78 < p.Y < 128:
            pts.append(p)
S = [p.X * ux + p.Y * uy for p in pts]
T = [p.X * vx + p.Y * vy for p in pts]
s0, s1, t0, t1 = min(S), max(S), min(T), max(T)
cs, ct = (s0 + s1) / 2.0, (t0 + t1) / 2.0
result = ('pts=%d\ns %.3f .. %.3f  (len %.2f)\nt %.3f .. %.3f  (len %.2f)\n'
          'center station s=%.4f t=%.4f\ncenter world (%.4f,%.4f)' % (
              len(pts), s0, s1, s1 - s0, t0, t1, t1 - t0, cs, ct,
              cs * ux + ct * vx, cs * uy + ct * vy))
