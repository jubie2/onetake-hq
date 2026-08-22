# Crop ADU views tightly. args {"prefix":"ADU - ","region":[x0,y0,x1,y1],"half_width":26,"dry":true}
from Autodesk.Revit.DB import View, BoundingBoxXYZ, XYZ as _XYZ
reg = args['region']; HW = float(args.get('half_width', 26.0))
cx, cy = (reg[0]+reg[2])/2.0, (reg[1]+reg[3])/2.0
L = []
t = None
if not args.get('dry', True):
    t = Transaction(doc, 'OneTake: crop ADU views'); _prep(t); t.Start()
for v in FilteredElementCollector(doc).OfClass(View):
    try:
        if v.IsTemplate or not v.Name.startswith(args.get('prefix', 'ADU - ')): continue
        vt = str(v.ViewType); bb = v.CropBox; tf = bb.Transform; inv = tf.Inverse
        before = (round(bb.Max.X-bb.Min.X,1), round(bb.Max.Y-bb.Min.Y,1))
        if vt in ('FloorPlan', 'CeilingPlan', 'EngineeringPlan'):
            pts = [inv.OfPoint(_XYZ(reg[0], reg[1], 0)), inv.OfPoint(_XYZ(reg[2], reg[3], 0))]
            xs = [p.X for p in pts]; ys = [p.Y for p in pts]
            nb = BoundingBoxXYZ(); nb.Transform = tf
            nb.Min = _XYZ(min(xs), min(ys), bb.Min.Z); nb.Max = _XYZ(max(xs), max(ys), bb.Max.Z)
        else:                                   # elevation / section: centre horizontally on the ADU
            c = inv.OfPoint(_XYZ(cx, cy, 0))
            nb = BoundingBoxXYZ(); nb.Transform = tf
            nb.Min = _XYZ(c.X - HW, bb.Min.Y, bb.Min.Z)
            nb.Max = _XYZ(c.X + HW, bb.Max.Y, bb.Max.Z)
        if not args.get('dry', True):
            v.CropBox = nb; v.CropBoxActive = True; v.CropBoxVisible = False
        L.append('%-30s %-12s  %sx%s ft -> %.0fx%.0f ft' %
                 (v.Name[:30], vt, before[0], before[1],
                  nb.Max.X-nb.Min.X, nb.Max.Y-nb.Min.Y))
    except Exception as ex:
        L.append('err %s: %s' % (v.Name, ex))
if t is not None:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)
