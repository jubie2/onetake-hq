# Exact face classification (via FacingOrientation) + footprint extent at each
# section cut station.  Walls + family instances only - no Rooms/Areas.
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, Wall, FamilyInstance,
                               BuiltInCategory as BIC, XYZ as _XYZ)
A = math.radians(14.3)
UX, UY = math.cos(A), math.sin(A)
VX, VY = -math.sin(A), math.cos(A)
CX, CY = 1161.1251, 98.8210
def st(x, y):
    dx, dy = x - CX, y - CY
    return (dx * UX + dy * UY, dx * VX + dy * VY)
L = ['=== EXTERIOR WALL SEGMENTS (s,t) ===']
segs = []
for w in FEC(doc).OfClass(Wall):
    try:
        c = w.Location.Curve
        a = c.GetEndPoint(0); b = c.GetEndPoint(1)
    except Exception:
        continue
    if not (1120 < a.X < 1200 and 78 < a.Y < 128): continue
    nm = ''
    try: nm = w.WallType.get_Parameter(
        __import__('Autodesk').Revit.DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString() or ''
    except Exception: pass
    if 'ext' not in nm.lower(): continue
    s0, t0 = st(a.X, a.Y); s1, t1 = st(b.X, b.Y)
    segs.append((s0, t0, s1, t1))
    L.append('  (%6.1f,%6.1f) -> (%6.1f,%6.1f)  %s' % (s0, t0, s1, t1, nm[:22]))
L.append('=== FOOTPRINT EXTENT AT EACH CUT ===')
def perp_range_at_s(cut):
    ts = []
    for (s0, t0, s1, t1) in segs:
        if (s0 - cut) * (s1 - cut) <= 0 and abs(s1 - s0) > 0.01:
            f = (cut - s0) / (s1 - s0)
            ts.append(t0 + f * (t1 - t0))
    return (min(ts), max(ts)) if ts else None
def perp_range_at_t(cut):
    ss = []
    for (s0, t0, s1, t1) in segs:
        if (t0 - cut) * (t1 - cut) <= 0 and abs(t1 - t0) > 0.01:
            f = (cut - t0) / (t1 - t0)
            ss.append(s0 + f * (s1 - s0))
    return (min(ss), max(ss)) if ss else None
for cut in (-20.0, 14.0):
    r = perp_range_at_s(cut)
    L.append('  section cut s=%.1f  -> t %s' % (cut, ('%.1f .. %.1f' % r) if r else 'NONE'))
for cut in (11.0, -3.0):
    r = perp_range_at_t(cut)
    L.append('  section cut t=%.1f  -> s %s' % (cut, ('%.1f .. %.1f' % r) if r else 'NONE'))
L.append('=== OPENINGS / LIGHTS BY FACE ===')
rows = []
for cat, tagc in ((BIC.OST_Doors, 'DOOR'), (BIC.OST_Windows, 'WIN'),
                  (BIC.OST_LightingFixtures, 'LIGHT')):
    for e in FEC(doc).OfCategory(cat).WhereElementIsNotElementType():
        try: p = e.Location.Point
        except Exception: continue
        if p is None: continue
        if not (1120 < p.X < 1200 and 78 < p.Y < 128): continue
        try: f = e.FacingOrientation
        except Exception: f = _XYZ(0, 0, 0)
        du = f.X * UX + f.Y * UY
        dv = f.X * VX + f.Y * VY
        face = '?'
        if dv > 0.7: face = 'N'
        elif dv < -0.7: face = 'S'
        elif du > 0.7: face = 'E'
        elif du < -0.7: face = 'W'
        s, t = st(p.X, p.Y)
        rows.append((face, s, '  %-5s %-9s face=%s s=%7.2f t=%7.2f z=%5.2f  world(%.1f,%.1f)  %s' % (
            tagc, e.Id.Value, face, s, t, p.Z, p.X, p.Y, e.Symbol.Family.Name[:20])))
for face in ('N', 'S', 'E', 'W', '?'):
    for f2, s, line in sorted([r for r in rows if r[0] == face], key=lambda z: z[1]):
        L.append(line)
result = '\n'.join(L)
