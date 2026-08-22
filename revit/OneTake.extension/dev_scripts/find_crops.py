# Views whose crop sits inside a given area. args {"area":[x0,y0,x1,y1]}
from Autodesk.Revit.DB import View, BuiltInParameter
import math
a = args['area']
L = []
for v in FilteredElementCollector(doc).OfClass(View):
    if v.IsTemplate: continue
    try:
        bb = v.CropBox; tf = bb.Transform
        p0 = tf.OfPoint(bb.Min); p1 = tf.OfPoint(bb.Max)
        cx, cy = (p0.X+p1.X)/2.0, (p0.Y+p1.Y)/2.0
        if not (a[0] <= cx <= a[2] and a[1] <= cy <= a[3]): continue
        try: sn = v.get_Parameter(BuiltInParameter.VIEWER_SHEET_NUMBER).AsString() or '-'
        except Exception: sn = '-'
        lvl = v.GenLevel.Name if v.GenLevel else '-'
        L.append('%-13s %-9s %-34s lvl=%-16s sheet=%-6s crop%s  x %7.1f..%7.1f y %7.1f..%7.1f (%.0fx%.0f)' %
                 (str(v.ViewType), v.Id.Value, v.Name[:34], lvl[:16], sn,
                  'ON ' if v.CropBoxActive else 'off',
                  min(p0.X,p1.X), max(p0.X,p1.X), min(p0.Y,p1.Y), max(p0.Y,p1.Y),
                  abs(bb.Max.X-bb.Min.X), abs(bb.Max.Y-bb.Min.Y)))
    except Exception: pass
result = '\n'.join(sorted(L))
