# Report / set the vertical crop range of elevation & section views. args {"prefix":"ADU - ","ymin":-4,"ymax":31,"dry":true}
from Autodesk.Revit.DB import View, BoundingBoxXYZ, XYZ as _XYZ
L = []
t = None
if not args.get('dry', True):
    t = Transaction(doc, 'OneTake: crop height'); _prep(t); t.Start()
for v in FilteredElementCollector(doc).OfClass(View):
    try:
        if v.IsTemplate or not v.Name.startswith(args.get('prefix', 'ADU - ')): continue
        if str(v.ViewType) not in ('Elevation', 'Section'): continue
        bb = v.CropBox
        # local Y is height above the view origin; find the world elevation of the crop top/bottom
        tf = bb.Transform
        wlo = tf.OfPoint(_XYZ(bb.Min.X, bb.Min.Y, 0)).Z
        whi = tf.OfPoint(_XYZ(bb.Min.X, bb.Max.Y, 0)).Z
        info = 'local Y %.1f..%.1f -> world Z %.1f..%.1f' % (bb.Min.Y, bb.Max.Y, wlo, whi)
        if not args.get('dry', True):
            dy_lo = float(args['ymin']) - wlo
            dy_hi = float(args['ymax']) - whi
            nb = BoundingBoxXYZ(); nb.Transform = tf
            nb.Min = _XYZ(bb.Min.X, bb.Min.Y + dy_lo, bb.Min.Z)
            nb.Max = _XYZ(bb.Max.X, bb.Max.Y + dy_hi, bb.Max.Z)
            v.CropBox = nb; v.CropBoxActive = True
            bb2 = v.CropBox
            info += '  ->  world Z %.1f..%.1f' % (tf.OfPoint(_XYZ(bb2.Min.X, bb2.Min.Y, 0)).Z,
                                                 tf.OfPoint(_XYZ(bb2.Min.X, bb2.Max.Y, 0)).Z)
        L.append('%-24s %s' % (v.Name[:24], info))
    except Exception as ex:
        L.append('err %s: %s' % (v.Name, str(ex)[:50]))
if t is not None:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)
