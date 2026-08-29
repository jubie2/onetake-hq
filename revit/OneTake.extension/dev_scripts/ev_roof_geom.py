# Roof-deck footprint in the building frame, from the roof-deck level walls/floors.
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, Wall, Floor, ElementId,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
A = math.radians(14.3)
UX, UY = math.cos(A), math.sin(A)
VX, VY = -math.sin(A), math.cos(A)
BX, BY = 1161.1251, 98.8210
def st(x, y):
    dx, dy = x - BX, y - BY
    return (dx * UX + dy * UY, dx * VX + dy * VY)
L = []
# floors near the roof deck level (z ~ 22.7) and the 2nd floor (z ~ 11.7)
for f in FEC(doc).OfCategory(BIC.OST_Floors).WhereElementIsNotElementType():
    bb = f.get_BoundingBox(None)
    if bb is None: continue
    cx = (bb.Min.X + bb.Max.X) / 2.0; cy = (bb.Min.Y + bb.Max.Y) / 2.0
    if not (1120 < cx < 1200 and 78 < cy < 128): continue
    s0, t0 = st(bb.Min.X, bb.Min.Y); s1, t1 = st(bb.Max.X, bb.Max.Y)
    try: lvl = doc.GetElement(f.LevelId).Name
    except Exception: lvl = '?'
    L.append('FLOOR %-9s z %5.2f..%5.2f  lvl %-18s world (%.1f,%.1f)-(%.1f,%.1f)' % (
        f.Id.Value, bb.Min.Z, bb.Max.Z, lvl, bb.Min.X, bb.Min.Y, bb.Max.X, bb.Max.Y))
# walls whose top is at/above the roof deck (parapets) - gives the deck outline
pts = []
for w in FEC(doc).OfClass(Wall):
    bb = w.get_BoundingBox(None)
    if bb is None: continue
    cx = (bb.Min.X + bb.Max.X) / 2.0; cy = (bb.Min.Y + bb.Max.Y) / 2.0
    if not (1120 < cx < 1200 and 78 < cy < 128): continue
    if bb.Max.Z < 20.0: continue
    try:
        c = w.Location.Curve
        a = c.GetEndPoint(0); b = c.GetEndPoint(1)
    except Exception:
        continue
    sa, ta = st(a.X, a.Y); sb, tb = st(b.X, b.Y)
    pts += [(sa, ta), (sb, tb)]
    L.append('PARAPET %-9s z %5.2f..%5.2f  (s%6.1f,t%6.1f)->(s%6.1f,t%6.1f)' % (
        w.Id.Value, bb.Min.Z, bb.Max.Z, sa, ta, sb, tb))
if pts:
    L.append('DECK EXTENT  s %.1f .. %.1f   t %.1f .. %.1f' % (
        min(p[0] for p in pts), max(p[0] for p in pts),
        min(p[1] for p in pts), max(p[1] for p in pts)))
result = '\n'.join(L)
