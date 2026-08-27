# Family instances + drawn-symbol curves in a mech/elec plan view (ADU region).
# args {"view":"ADU - 1st Floor Mechanical Plan"}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, FamilyInstance,
                               CurveElement, XYZ as _XYZ)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
nm = args['view']
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == nm: v = x; break
L = ['view %s' % nm]
for e in FEC(doc, v.Id).WhereElementIsNotElementType():
    try:
        if isinstance(e, FamilyInstance):
            cn = e.Category.Name if e.Category else '?'
            if cn in ('Doors', 'Windows', 'Walls'): continue
            b = e.get_BoundingBox(v)
            if b is None: continue
            c = _XYZ((b.Min.X + b.Max.X) / 2, (b.Min.Y + b.Max.Y) / 2, 0)
            if not (X0 <= c.X <= X1 and Y0 <= c.Y <= Y1): continue
            L.append('%-22s id %s [%s] (%.1f,%.1f)' % (cn[:22], e.Id.Value,
                     e.Symbol.Family.Name[:28], c.X, c.Y))
        elif isinstance(e, CurveElement):
            c0 = e.GeometryCurve
            m = c0.Evaluate(0.5, True)
            L.append('CRV %-18s id %s len %.2f mid (%.1f,%.1f)' % (
                c0.GetType().Name, e.Id.Value, c0.Length, m.X, m.Y))
    except Exception: pass
result = '\n'.join(L)
