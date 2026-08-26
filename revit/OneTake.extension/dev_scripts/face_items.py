# List tag-worthy elements on one face of the ADU (by wall plane).
# args {"face":"south"}  faces: south y=-150.3, north y=-125.7, east x=1186.5, west x=1157.9
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, XYZ as _XYZ,
                               BuiltInCategory as BIC)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
face = args.get('face', 'south')
PLANES = {'south': ('y', -150.3), 'north': ('y', -125.7),
          'east': ('x', 1186.5), 'west': ('x', 1157.9)}
axis, val = PLANES[face]
L = ['%s face (%s=%.1f)' % (face, axis, val)]
cats = [BIC.OST_Windows, BIC.OST_Doors, BIC.OST_GenericModel,
        BIC.OST_LightingFixtures]
for bic in cats:
    for e in FEC(doc).OfCategory(bic).WhereElementIsNotElementType():
        try:
            b = e.get_BoundingBox(None)
            if b is None: continue
            c = _XYZ((b.Min.X + b.Max.X) / 2.0, (b.Min.Y + b.Max.Y) / 2.0,
                     (b.Min.Z + b.Max.Z) / 2.0)
            if not (X0 <= c.X <= X1 and Y0 <= c.Y <= Y1): continue
            d = abs(c.Y - val) if axis == 'y' else abs(c.X - val)
            if d > 1.5: continue
            fam = ''
            try: fam = e.Symbol.Family.Name
            except Exception: pass
            L.append('%s id %s [%s] c(%.1f,%.1f,%.1f) w%.1f h%.1f' % (
                e.Category.Name[:9], e.Id.Value, fam, c.X, c.Y, c.Z,
                max(b.Max.X - b.Min.X, b.Max.Y - b.Min.Y), b.Max.Z - b.Min.Z))
        except Exception: pass
result = '\n'.join(L)
