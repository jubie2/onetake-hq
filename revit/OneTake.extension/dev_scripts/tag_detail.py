# Full parameter dump of TAG LABEL generic annotations in a view.
# args {"view":"ADU - West Elevation"}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, FamilyInstance,
                               BuiltInCategory as BIC, StorageType)
import math
nm = args.get('view')
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == nm: v = x; break
L = ['view %s' % nm]
for e in FEC(doc, v.Id).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
    try:
        fam = e.Symbol.Family.Name
        if fam != 'TAG LABEL': continue
        lp = e.Location
        pt = lp.Point
        try: rot = lp.Rotation
        except Exception: rot = None
        pars = []
        for p in e.Parameters:
            try:
                st = p.StorageType
                if st == StorageType.String:
                    val = p.AsString()
                elif st == StorageType.Double:
                    val = '%.3f' % p.AsDouble()
                elif st == StorageType.Integer:
                    val = str(p.AsInteger())
                else:
                    val = p.AsValueString()
                if val not in (None, ''):
                    pars.append('%s=%s' % (p.Definition.Name, val))
            except Exception: pass
        L.append('id %s at (%.2f,%.2f,%.2f) rot %s | %s' % (
            e.Id.Value, pt.X, pt.Y, pt.Z,
            '%.1fdeg' % math.degrees(rot) if rot is not None else '?',
            '; '.join(sorted(pars))))
    except Exception as ex:
        L.append('ERR %s' % str(ex)[:60])
result = '\n'.join(L)
