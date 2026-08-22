# Trim level datum lines to the crop in section/elevation views (fixes oversized viewports).
# args {"prefix":"ADU - ","pad":1.0,"dry":true}
from Autodesk.Revit.DB import (View, Level, DatumExtentType, Line, XYZ as _XYZ,
                               FilteredElementCollector as FEC)
pad = float(args.get('pad', 1.0))
L = []
t = None
if not args.get('dry', True):
    t = Transaction(doc, 'OneTake: trim level extents'); _prep(t); t.Start()
levels = list(FEC(doc).OfClass(Level))
for v in FEC(doc).OfClass(View):
    try:
        if v.IsTemplate or not v.Name.startswith(args.get('prefix', 'ADU - ')): continue
        if str(v.ViewType) not in ('Section', 'Elevation'): continue
        bb = v.CropBox; tf = bb.Transform
        n = 0
        for lv in levels:
            try:
                curves = lv.GetCurvesInView(DatumExtentType.ViewSpecific, v)
                if curves is None or curves.Count == 0:
                    curves = lv.GetCurvesInView(DatumExtentType.Model, v)
                if curves is None or curves.Count == 0: continue
                c0 = list(curves)[0]
                z = c0.GetEndPoint(0).Z
                p0 = tf.OfPoint(_XYZ(bb.Min.X - pad, 0, 0))
                p1 = tf.OfPoint(_XYZ(bb.Max.X + pad, 0, 0))
                ln = Line.CreateBound(_XYZ(p0.X, p0.Y, z), _XYZ(p1.X, p1.Y, z))
                if not args.get('dry', True):
                    lv.SetDatumExtentType(DatumExtentType.ViewSpecific, v, True)
                    lv.SetCurveInView(DatumExtentType.ViewSpecific, v, ln)
                n += 1
            except Exception:
                pass
        if not args.get('dry', True):
            doc.Regenerate()
        L.append('%-24s levels trimmed=%d' % (v.Name[:24], n))
    except Exception as ex:
        L.append('err %s' % str(ex)[:60])
if t is not None:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)
