# What did Francis just draw for Bed-2, and which way do the outlets face?
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ElementId, Arc,
                               Line, XYZ as _XYZ, BuiltInCategory as BIC,
                               BuiltInParameter as BIP)
L = []
NEWEST = 2244990          # anything above this id was made after my last batch
L.append('=== recent detail curves / annotations, any view ===')
for v in FEC(doc).OfClass(View):
    if v.IsTemplate: continue
    try:
        curves = list(FEC(doc, v.Id).OfCategory(BIC.OST_Lines).WhereElementIsNotElementType())
    except Exception:
        continue
    rows = []
    for e in curves:
        if e.Id.Value < NEWEST: continue
        if e.OwnerViewId != v.Id: continue
        try:
            c = e.GeometryCurve
            a = c.GetEndPoint(0); b = c.GetEndPoint(1)
            kind = 'ARC' if isinstance(c, Arc) else 'LINE'
            st = e.LineStyle.Name if e.LineStyle else '?'
            rows.append('   %-9s %-4s (%.1f,%.1f)->(%.1f,%.1f) style=%s' % (
                e.Id.Value, kind, a.X, a.Y, b.X, b.Y, st))
        except Exception: pass
    if rows:
        L.append(' VIEW %s (id %s)' % (v.Name, v.Id.Value))
        L += rows
L.append('=== electrical fixtures near Bed-2 (1137.8,91.3) 1st floor ===')
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try: p = e.Location.Point
    except Exception: continue
    if p is None or p.Z > 10: continue
    if math.hypot(p.X - 1137.8, p.Y - 91.3) > 12: continue
    try: f = e.FacingOrientation
    except Exception: f = _XYZ(0, 0, 0)
    try: host = e.Host.Id.Value
    except Exception: host = '?'
    L.append('  %-9s (%.1f,%.1f,%5.2f) face(%.2f,%.2f) host %s  %s' % (
        e.Id.Value, p.X, p.Y, p.Z, f.X, f.Y, host, e.Symbol.Family.Name))
L.append('=== ALL outlets: facing vs. building centre (out = wrong side) ===')
CENX, CENY = 1157.520, 104.867
nout = nin = 0
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try:
        p = e.Location.Point
        f = e.FacingOrientation
    except Exception: continue
    if p is None or not (1120 < p.X < 1200 and 78 < p.Y < 128): continue
    dx, dy = CENX - p.X, CENY - p.Y
    m = math.hypot(dx, dy) or 1.0
    dot = (f.X * dx + f.Y * dy) / m           # >0 = faces inward
    if dot < 0: nout += 1
    else: nin += 1
L.append('  faces inward: %d    faces OUTWARD (wrong): %d' % (nin, nout))
result = '\n'.join(L)
