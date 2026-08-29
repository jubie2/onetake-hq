# Measure the true wall directions of the new ADU so sections/elevations can be
# cut square to the building instead of to world X/Y.
import math
from Autodesk.Revit.DB import FilteredElementCollector as FEC, Wall, XYZ as _XYZ
bins = {}
walls = []
for w in FEC(doc).OfClass(Wall):
    bb = w.get_BoundingBox(None)
    if bb is None: continue
    cx = (bb.Min.X + bb.Max.X) / 2.0; cy = (bb.Min.Y + bb.Max.Y) / 2.0
    if not (1120 < cx < 1200 and 78 < cy < 128): continue
    try:
        c = w.Location.Curve
        a = c.GetEndPoint(0); b = c.GetEndPoint(1)
    except Exception:
        continue
    L = math.hypot(b.X - a.X, b.Y - a.Y)
    if L < 2.0: continue
    ang = math.degrees(math.atan2(b.Y - a.Y, b.X - a.X)) % 180.0
    key = round(ang, 1)
    bins[key] = bins.get(key, 0) + L
    walls.append((L, ang, a, b, w.Id.Value))
out = ['--- wall direction histogram (total length ft by angle deg) ---']
for k in sorted(bins, key=lambda z: -bins[z])[:12]:
    out.append('  %6.1f deg : %7.1f ft' % (k, bins[k]))
out.append('--- 12 longest walls ---')
for (L, ang, a, b, wid) in sorted(walls, reverse=True)[:12]:
    out.append('  %s len %5.1f ang %6.1f  (%.1f,%.1f)->(%.1f,%.1f)' % (
        wid, L, ang, a.X, a.Y, b.X, b.Y))
result = '\n'.join(out)
