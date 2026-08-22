# Force named levels to span the crop in a view, keeping the line collinear with the
# existing datum curve (model space) so Revit accepts it.
# args {"view":"West Elev.","levels":["..."],"pad":1.5,"dry":false}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, Level, ElementId,
                               DatumExtentType, DatumEnds, Line, XYZ as _XYZ)
from System.Collections.Generic import List
name = args['view']; pad = float(args.get('pad', 1.5))
want = set(args.get('levels', [])); dry = args.get('dry', False)
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == name: v = x; break
L = ['view %s' % name]
bb = v.CropBox; tf = bb.Transform
corners = []
for x in (bb.Min.X, bb.Max.X):
    for y in (bb.Min.Y, bb.Max.Y):
        corners.append(tf.OfPoint(_XYZ(x, y, 0.0)))
t = None
if not dry:
    t = Transaction(doc, 'OneTake: set datums'); _prep(t); t.Start()
for l in FEC(doc).OfClass(Level):
    if l.Name not in want: continue
    try:
        if not dry and l.IsHidden(v):
            v.UnhideElements(List[ElementId]([l.Id]))
        for e in (DatumEnds.End0, DatumEnds.End1):
            if not dry: l.SetDatumExtentType(e, v, DatumExtentType.ViewSpecific)
        cs = list(l.GetCurvesInView(DatumExtentType.ViewSpecific, v))
        if not cs:
            cs = list(l.GetCurvesInView(DatumExtentType.Model, v))
        if not cs:
            L.append('  %-20s no curve in view' % l.Name[:20]); continue
        c = cs[0]
        p0 = c.GetEndPoint(0); d = (c.GetEndPoint(1) - p0).Normalize()
        ts = [(p - p0).DotProduct(d) for p in corners]
        a = p0 + d * (min(ts) - pad)
        b = p0 + d * (max(ts) + pad)
        L.append('  %-20s span %.1f -> %.1f ft' % (
            l.Name[:20], c.Length, (max(ts) + pad) - (min(ts) - pad)))
        if not dry:
            l.SetCurveInView(DatumExtentType.ViewSpecific, v, Line.CreateBound(a, b))
    except Exception as ex:
        L.append('  %-20s FAIL %s' % (l.Name[:20], str(ex)[:70]))
if not dry:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)
