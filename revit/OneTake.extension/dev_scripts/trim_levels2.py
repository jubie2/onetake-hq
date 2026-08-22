# Trim level datums to the crop using the datum's own Z. args {"prefix":"ADU - ","pad":1.5,"hide_fallback":true,"dry":true}
from Autodesk.Revit.DB import (View, Level, DatumExtentType, DatumEnds, Line, XYZ as _XYZ,
                               FilteredElementCollector as FEC)
pad = float(args.get('pad', 1.5))
L = []
t = None
if not args.get('dry', True):
    t = Transaction(doc, 'OneTake: trim datums'); _prep(t); t.Start()
for v in FEC(doc).OfClass(View):
    try:
        if v.IsTemplate or not v.Name.startswith(args.get('prefix', 'ADU - ')): continue
        if str(v.ViewType) not in ('Section', 'Elevation'): continue
        bb = v.CropBox; tf = bb.Transform; inv = tf.Inverse
        wL = tf.OfPoint(_XYZ(bb.Min.X - pad, 0, 0))
        wR = tf.OfPoint(_XYZ(bb.Max.X + pad, 0, 0))
        ok, hid, errs = 0, 0, []
        for lv in FEC(doc, v.Id).OfClass(Level):
            try:
                cs = lv.GetCurvesInView(DatumExtentType.ViewSpecific, v)
                if cs is None or cs.Count == 0:
                    cs = lv.GetCurvesInView(DatumExtentType.Model, v)
                if cs is None or cs.Count == 0:
                    continue
                c = list(cs)[0]
                z = c.GetEndPoint(0).Z
                p0 = _XYZ(wL.X, wL.Y, z); p1 = _XYZ(wR.X, wR.Y, z)
                if p0.DistanceTo(p1) < 1.0: continue
                if not args.get('dry', True):
                    lv.SetDatumExtentType(DatumEnds.End0, v, DatumExtentType.ViewSpecific)
                    lv.SetDatumExtentType(DatumEnds.End1, v, DatumExtentType.ViewSpecific)
                    lv.SetCurveInView(DatumExtentType.ViewSpecific, v, Line.CreateBound(p0, p1))
                ok += 1
            except Exception as ex:
                errs.append('%s: %s' % (lv.Name[:14], str(ex)[:38]))
                if args.get('hide_fallback') and not args.get('dry', True):
                    try:
                        v.HideElements(__import__('System').Collections.Generic.List[
                            __import__('Autodesk').Revit.DB.ElementId]([lv.Id]))
                        hid += 1
                    except Exception: pass
        if not args.get('dry', True): doc.Regenerate()
        L.append('%-24s trimmed=%d hidden=%d %s' % (v.Name[:24], ok, hid, ('| ' + errs[0]) if errs else ''))
    except Exception as ex:
        L.append('err %s' % str(ex)[:60])
if t is not None:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)
