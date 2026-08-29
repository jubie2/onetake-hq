# Target the PROJECT doc explicitly (the active doc may be a family editor).
# Find what Francis drew for Bed-2, and check which side of the wall the outlets sit on.
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ElementId, Arc,
                               XYZ as _XYZ, BuiltInCategory as BIC)
pdoc = None
for d in doc.Application.Documents:
    if not d.IsFamilyDocument and 'Electric Ave' in d.Title: pdoc = d; break
L = ['project doc: %s' % (pdoc.Title if pdoc else 'NOT FOUND')]
NEWEST = 2244990
L.append('=== detail curves created after my last batch ===')
for v in FEC(pdoc).OfClass(View):
    if v.IsTemplate: continue
    rows = []
    try:
        for e in FEC(pdoc, v.Id).OfCategory(BIC.OST_Lines).WhereElementIsNotElementType():
            if e.Id.Value < NEWEST or e.OwnerViewId != v.Id: continue
            c = e.GeometryCurve
            a = c.GetEndPoint(0); b = c.GetEndPoint(1)
            st = e.LineStyle.Name if e.LineStyle else '?'
            rows.append('   %-9s %-4s (%.1f,%.1f)->(%.1f,%.1f) len%.1f style=%s' % (
                e.Id.Value, 'ARC' if isinstance(c, Arc) else 'LINE',
                a.X, a.Y, b.X, b.Y, c.Length, st))
    except Exception: pass
    if rows:
        L.append(' VIEW %s (id %s)' % (v.Name, v.Id.Value))
        L += rows
L.append('=== elec fixtures created after my last batch ===')
for e in FEC(pdoc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    if e.Id.Value < NEWEST: continue
    try: p = e.Location.Point
    except Exception: continue
    L.append('  %-9s (%.1f,%.1f,%5.2f)  %s' % (e.Id.Value, p.X, p.Y, p.Z,
                                               e.Symbol.Family.Name))
L.append('=== outlet facing: does it point into the building? ===')
CENX, CENY = 1157.520, 104.867
bad = []
nin = 0
for e in FEC(pdoc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try:
        p = e.Location.Point
        f = e.FacingOrientation
    except Exception:
        continue
    if p is None or not (1120 < p.X < 1200 and 78 < p.Y < 128): continue
    dx, dy = CENX - p.X, CENY - p.Y
    m = math.hypot(dx, dy) or 1.0
    dot = (f.X * dx + f.Y * dy) / m
    if dot < 0:
        bad.append('  OUT %-9s (%.1f,%.1f) face(%.2f,%.2f) dot%.2f %s' % (
            e.Id.Value, p.X, p.Y, f.X, f.Y, dot, e.Symbol.Family.Name))
    else:
        nin += 1
L.append('  inward %d, outward %d' % (nin, len(bad)))
L += bad[:40]
result = '\n'.join(L)
