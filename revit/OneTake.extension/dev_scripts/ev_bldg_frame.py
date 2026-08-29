# Express the ADU in its OWN frame: u = along 14.3 deg walls (bldg east),
# v = along 104.3 deg walls (bldg north). Report oriented bbox + room stations.
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, Wall, XYZ as _XYZ,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
A = math.radians(14.3)
ux, uy = math.cos(A), math.sin(A)
vx, vy = -math.sin(A), math.cos(A)
pts = []
for w in FEC(doc).OfClass(Wall):
    bb = w.get_BoundingBox(None)
    if bb is None: continue
    cx = (bb.Min.X + bb.Max.X) / 2.0; cy = (bb.Min.Y + bb.Max.Y) / 2.0
    if not (1120 < cx < 1200 and 78 < cy < 128): continue
    try:
        c = w.Location.Curve
        pts.append(c.GetEndPoint(0)); pts.append(c.GetEndPoint(1))
    except Exception: pass
S = [p.X * ux + p.Y * uy for p in pts]
T = [p.X * vx + p.Y * vy for p in pts]
s0, s1, t0, t1 = min(S), max(S), min(T), max(T)
# world center of the oriented box
cs, ct = (s0 + s1) / 2.0, (t0 + t1) / 2.0
CX = cs * ux + ct * vx
CY = cs * uy + ct * vy
out = ['u = (%.5f,%.5f)  v = (%.5f,%.5f)' % (ux, uy, vx, vy),
       'oriented bbox: s %.2f..%.2f (%.1f ft)   t %.2f..%.2f (%.1f ft)' % (
           s0, s1, s1 - s0, t0, t1, t1 - t0),
       'center world (%.3f,%.3f)  center station s=%.3f t=%.3f' % (CX, CY, cs, ct),
       '--- rooms in building frame (s,t relative to center) ---']
rows = []
for r in FEC(doc).OfCategory(BIC.OST_Rooms):
    try:
        p = r.Location.Point
    except Exception:
        continue
    if p is None: continue
    if not (1120 < p.X < 1200 and 78 < p.Y < 128): continue
    s = p.X * ux + p.Y * uy - cs
    t = p.X * vx + p.Y * vy - ct
    lvl = doc.GetElement(r.LevelId).Name
    nm = r.get_Parameter(BIP.ROOM_NAME).AsString()
    rows.append((s, '  %-18s %-18s s=%7.2f t=%7.2f' % (nm, lvl, s, t)))
for s, line in sorted(rows):
    out.append(line)
out.append('half extents: s +/- %.2f   t +/- %.2f' % ((s1 - s0) / 2.0, (t1 - t0) / 2.0))
result = '\n'.join(out)
