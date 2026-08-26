# Leftover loose notes/curves in ADU plan views + toilet locations per floor.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, TextNote,
                               CurveElement, BuiltInCategory as BIC, XYZ as _XYZ)
import re
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
L = []
for nm in ('ADU - 1st Floor Plan', 'ADU - 2nd Floor Plan'):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    L.append('--- %s ---' % nm)
    for e in FEC(doc, v.Id).WhereElementIsNotElementType():
        if isinstance(e, TextNote):
            txt = (e.Text or '').replace('\r', ' ').strip()
            if re.match(r'^\d{1,2}$', txt):
                p = e.Coord
                L.append('TXT id %s "%s" at (%.1f,%.1f)' % (e.Id.Value, txt, p.X, p.Y))
        elif isinstance(e, CurveElement):
            c = e.GeometryCurve
            L.append('CRV id %s %s len %.2f at (%.1f,%.1f)' % (
                e.Id.Value, c.GetType().Name, c.Length,
                c.GetEndPoint(0).X, c.GetEndPoint(0).Y))
for e in FEC(doc).OfCategory(BIC.OST_PlumbingFixtures).WhereElementIsNotElementType():
    try:
        b = e.get_BoundingBox(None)
        c = _XYZ((b.Min.X + b.Max.X) / 2, (b.Min.Y + b.Max.Y) / 2, (b.Min.Z + b.Max.Z) / 2)
        if not (X0 <= c.X <= X1 and Y0 <= c.Y <= Y1): continue
        L.append('PLUMB id %s [%s] (%.1f,%.1f) z%.1f' % (
            e.Id.Value, e.Symbol.Family.Name[:25], c.X, c.Y, c.Z))
    except Exception: pass
result = '\n'.join(L)
