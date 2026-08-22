# Report crop regions of all plan views (model-space bounds + rotation), so we can pick the right one.
from Autodesk.Revit.DB import View, ViewPlan, ViewType
import math
L = []
for v in FilteredElementCollector(doc).OfClass(View):
    if v.IsTemplate:
        continue
    vt = str(v.ViewType)
    if vt not in ('FloorPlan', 'AreaPlan', 'CeilingPlan', 'EngineeringPlan'):
        continue
    try:
        bb = v.CropBox; tf = bb.Transform
        p0 = tf.OfPoint(bb.Min); p1 = tf.OfPoint(bb.Max)
        ang = math.degrees(math.atan2(tf.BasisX.Y, tf.BasisX.X))
        w = abs(bb.Max.X - bb.Min.X); h = abs(bb.Max.Y - bb.Min.Y)
        lvl = v.GenLevel.Name if v.GenLevel else '-'
        L.append((v.CropBoxActive, '%-1s %-26s %-9s %-14s lvl=%-16s rot=%6.2f  x %8.1f..%8.1f  y %8.1f..%8.1f  (%5.1f x %5.1f)' %
                  ('*' if v.CropBoxActive else ' ', v.Name[:26], v.Id.Value, vt, lvl[:16], ang,
                   min(p0.X, p1.X), max(p0.X, p1.X), min(p0.Y, p1.Y), max(p0.Y, p1.Y), w, h)))
    except Exception as ex:
        L.append((False, '%s: %s' % (v.Name, ex)))
L.sort(key=lambda t: (not t[0],))
result = '\n'.join(s for _, s in L[:45])
