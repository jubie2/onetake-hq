# Trim level datum lines to each view's crop (fixes oversized viewport boxes).
# args {"prefix":"ADU - ","pad":1.5,"hide_cameras":true,"dry":true}
from Autodesk.Revit.DB import (View, Level, DatumExtentType, DatumEnds, Line, XYZ as _XYZ, BuiltInCategory,
                               FilteredElementCollector as FEC, ElementId as EId)
pad = float(args.get('pad', 1.5))
L = []
t = None
if not args.get('dry', True):
    t = Transaction(doc, 'OneTake: trim level extents'); _prep(t); t.Start()
levels = list(FEC(doc).OfClass(Level))
for v in FEC(doc).OfClass(View):
    try:
        if v.IsTemplate or not v.Name.startswith(args.get('prefix', 'ADU - ')): continue
        if str(v.ViewType) not in ('Section', 'Elevation'): continue
        bb = v.CropBox; tf = bb.Transform; inv = tf.Inverse
        n, errs = 0, []
        for lv in levels:
            try:
                # local Y of this level's elevation, on the view plane
                bx = tf.BasisX; by = tf.BasisY
                if abs(by.Z) < 1e-6: continue
                base = tf.Origin + by * ((lv.Elevation - tf.Origin.Z) / by.Z)   # on the view plane, at level height
                ly = inv.OfPoint(base).Y
                if ly < bb.Min.Y - 6 or ly > bb.Max.Y + 6:
                    continue                      # level not in this view's height range
                p0 = base + bx * (bb.Min.X - pad)
                p1 = base + bx * (bb.Max.X + pad)
                if not args.get('dry', True):
                    lv.SetDatumExtentType(DatumEnds.End0, v, DatumExtentType.ViewSpecific)
                    lv.SetDatumExtentType(DatumEnds.End1, v, DatumExtentType.ViewSpecific)
                    lv.SetCurveInView(DatumExtentType.ViewSpecific, v, Line.CreateBound(p0, p1))
                n += 1
            except Exception as ex:
                errs.append('%s:%s' % (lv.Name[:12], str(ex)[:40]))
        if args.get('hide_cameras') and not args.get('dry', True):
            try:
                v.SetCategoryHidden(EId(BuiltInCategory.OST_Cameras), True)
            except Exception as ex:
                errs.append('cam:%s' % str(ex)[:30])
        if not args.get('dry', True):
            doc.Regenerate()
        L.append('%-24s levels set=%d %s' % (v.Name[:24], n, ('| ' + errs[0]) if errs else ''))
    except Exception as ex:
        L.append('err %s' % str(ex)[:60])
if t is not None:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)
