# Shrink over-wide elevation/section crops about their own centre. args {"prefix":"ADU - ","half":26,"max_w":60,"dry":true}
from Autodesk.Revit.DB import View, BoundingBoxXYZ, XYZ as _XYZ
HW = float(args.get('half', 26.0)); MX = float(args.get('max_w', 60.0))
L = []
t = None
if not args.get('dry', True):
    t = Transaction(doc, 'OneTake: shrink crops'); _prep(t); t.Start()
for v in FilteredElementCollector(doc).OfClass(View):
    try:
        if v.IsTemplate or not v.Name.startswith(args.get('prefix','ADU - ')): continue
        if str(v.ViewType) not in ('Elevation', 'Section'): continue
        bb = v.CropBox
        w = bb.Max.X - bb.Min.X
        if w <= MX:
            L.append('%-30s ok (%.0f ft)' % (v.Name[:30], w)); continue
        c = (bb.Min.X + bb.Max.X)/2.0
        nb = BoundingBoxXYZ(); nb.Transform = bb.Transform
        nb.Min = _XYZ(c - HW, bb.Min.Y, bb.Min.Z); nb.Max = _XYZ(c + HW, bb.Max.Y, bb.Max.Z)
        if not args.get('dry', True):
            v.CropBox = nb; v.CropBoxActive = True
        L.append('%-30s %.0f -> %.0f ft' % (v.Name[:30], w, nb.Max.X - nb.Min.X))
    except Exception as ex:
        L.append('err %s' % ex)
if t is not None:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)
