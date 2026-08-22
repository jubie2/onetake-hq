# Unhide levels in a view, then trim them by re-parameterising their OWN curve (stays on the datum plane).
# args {"views":["ADU - North Elevation","ADU - Section 2"],"pad":1.5,"dry":true}
from Autodesk.Revit.DB import (View, Level, DatumExtentType, DatumEnds, Line, XYZ as _XYZ,
                               FilteredElementCollector as FEC, ElementId as EId)
from System.Collections.Generic import List
pad = float(args.get('pad', 1.5))
L = []
t = None
if not args.get('dry', True):
    t = Transaction(doc, 'OneTake: fix datums'); _prep(t); t.Start()
for nm in args['views']:
    vs = [x for x in FEC(doc).OfClass(View) if not x.IsTemplate and x.Name == nm]
    if not vs:
        L.append('%s: not found' % nm); continue
    v = vs[0]
    bb = v.CropBox; tf = bb.Transform
    wL = tf.OfPoint(_XYZ(bb.Min.X - pad, 0, 0)); wR = tf.OfPoint(_XYZ(bb.Max.X + pad, 0, 0))
    done, errs = 0, []
    for lv in FEC(doc).OfClass(Level):
        try:
            if not args.get('dry', True):
                try:
                    ids = List[EId](); ids.Add(lv.Id)
                    v.UnhideElements(ids)
                except Exception: pass
                lv.SetDatumExtentType(DatumEnds.End0, v, DatumExtentType.ViewSpecific)
                lv.SetDatumExtentType(DatumEnds.End1, v, DatumExtentType.ViewSpecific)
                doc.Regenerate()
            cs = lv.GetCurvesInView(DatumExtentType.ViewSpecific, v)
            if cs is None or cs.Count == 0: continue
            c = list(cs)[0]
            p0 = c.GetEndPoint(0); p1 = c.GetEndPoint(1)
            d = (p1 - p0).Normalize()
            tL = (wL - p0).DotProduct(d); tR = (wR - p0).DotProduct(d)
            lo, hi = min(tL, tR), max(tL, tR)
            n0 = _XYZ((p0 + d * lo).X, (p0 + d * lo).Y, lv.Elevation)
            n1 = _XYZ((p0 + d * hi).X, (p0 + d * hi).Y, lv.Elevation)
            if n0.DistanceTo(n1) < 1.0: continue
            if not args.get('dry', True):
                lv.SetCurveInView(DatumExtentType.ViewSpecific, v, Line.CreateBound(n0, n1))
            done += 1
        except Exception as ex:
            errs.append('%s:%s' % (lv.Name[:12], str(ex)[:34]))
    if not args.get('dry', True): doc.Regenerate()
    L.append('%-24s datums fixed=%d %s' % (nm[:24], done, ('| ' + errs[0]) if errs else ''))
if t is not None:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)
