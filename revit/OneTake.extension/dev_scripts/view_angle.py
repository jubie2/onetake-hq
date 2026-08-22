from Autodesk.Revit.DB import View, ViewPlan, BuiltInParameter, ProjectLocation, Transform
import math
names = args.get('views') or ['1st Floor Plan', '2nd FLoor Level']
L = []
for nm in names:
    vs = [v for v in FilteredElementCollector(doc).OfClass(View) if not v.IsTemplate and v.Name == nm]
    for v in vs:
        try:
            tf = v.CropBox.Transform
            bx = tf.BasisX
            ang = math.degrees(math.atan2(bx.Y, bx.X))
            L.append('%-22s id=%-9s type=%-10s cropRot=%7.3f deg  origin=(%.2f,%.2f)' %
                     (v.Name, v.Id.Value, v.ViewType, ang, tf.Origin.X, tf.Origin.Y))
        except Exception as ex:
            L.append('%s: %s' % (nm, ex))
# project north / true north
try:
    pp = doc.ActiveProjectLocation.GetProjectPosition(XYZ(0, 0, 0))
    L.append('ProjectPosition: EW=%.3f NS=%.3f Angle=%.4f deg' % (pp.EastWest, pp.NorthSouth, math.degrees(pp.Angle)))
except Exception as ex:
    L.append('projpos err %s' % ex)
# a sample existing wall direction, to see what the building is aligned to
from Autodesk.Revit.DB import Wall
angs = {}
for w in FilteredElementCollector(doc).OfClass(Wall):
    try:
        c = w.Location.Curve
        d = (c.GetEndPoint(1) - c.GetEndPoint(0)).Normalize()
        a = round(math.degrees(math.atan2(d.Y, d.X)) % 90.0, 1)
        angs[a] = angs.get(a, 0) + 1
    except Exception:
        pass
top = sorted(angs.items(), key=lambda kv: -kv[1])[:6]
L.append('existing wall angles (mod 90): %s' % top)
result = '\n'.join(L)
