# Site view info: crop extents, property line location, view id.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, CurveElement,
                               XYZ as _XYZ, BuiltInCategory as BIC)
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == 'Site': v = x; break
bb = v.CropBox
L = ['Site view id %s scale %s' % (v.Id.Value, v.Scale)]
L.append('crop min (%.1f,%.1f) max (%.1f,%.1f)' % (
    bb.Transform.OfPoint(bb.Min).X, bb.Transform.OfPoint(bb.Min).Y,
    bb.Transform.OfPoint(bb.Max).X, bb.Transform.OfPoint(bb.Max).Y))
try:
    for e in FEC(doc, v.Id).OfCategory(BIC.OST_SiteProperty).WhereElementIsNotElementType():
        b = e.get_BoundingBox(v)
        if b: L.append('PROP id %s (%.1f,%.1f)-(%.1f,%.1f)' % (
            e.Id.Value, b.Min.X, b.Min.Y, b.Max.X, b.Max.Y))
except Exception as ex:
    L.append('prop err %s' % str(ex)[:40])
# detail lines in the site view (PL is often drawn)
n = 0
xs = []; ys = []
for e in FEC(doc, v.Id).OfClass(CurveElement):
    try:
        c = e.GeometryCurve
        for p in (c.GetEndPoint(0), c.GetEndPoint(1)):
            xs.append(p.X); ys.append(p.Y)
        n += 1
    except Exception: pass
if xs:
    L.append('%d curves, extent (%.1f,%.1f)-(%.1f,%.1f)' % (
        n, min(xs), min(ys), max(xs), max(ys)))
result = '\n'.join(L)
