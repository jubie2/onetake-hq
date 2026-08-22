from Autodesk.Revit.DB import View
import math
L = []
for v in FilteredElementCollector(doc).OfClass(View):
    if v.IsTemplate: continue
    try:
        lvl = v.GenLevel
        if lvl is None or '2nd' not in lvl.Name: continue
        bb = v.CropBox; tf = bb.Transform
        p0 = tf.OfPoint(bb.Min); p1 = tf.OfPoint(bb.Max)
        ang = math.degrees(math.atan2(tf.BasisX.Y, tf.BasisX.X))
        L.append('%s %-26s %-9s %-16s rot=%6.2f  x %8.1f..%8.1f  y %8.1f..%8.1f  (%5.1f x %5.1f)' %
                 ('CROP-ON ' if v.CropBoxActive else 'crop-off', v.Name[:26], v.Id.Value, str(v.ViewType),
                  ang, min(p0.X,p1.X), max(p0.X,p1.X), min(p0.Y,p1.Y), max(p0.Y,p1.Y),
                  abs(bb.Max.X-bb.Min.X), abs(bb.Max.Y-bb.Min.Y)))
    except Exception as ex:
        L.append('err %s %s' % (v.Name, ex))
result = '\n'.join(sorted(L))
