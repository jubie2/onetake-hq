# List ADU mech-equipment instances with z + host; args {"delete":[ids], "place_on_2nd":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, Floor,
                               XYZ as _XYZ, BuiltInCategory as BIC)
from Autodesk.Revit.DB.Structure import StructuralType
from System.Collections.Generic import List
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
L = []
regs = []
for e in FEC(doc).OfCategory(BIC.OST_MechanicalEquipment).WhereElementIsNotElementType():
    try:
        b = e.get_BoundingBox(None)
        if b is None: continue
        c = _XYZ((b.Min.X + b.Max.X) / 2, (b.Min.Y + b.Max.Y) / 2, (b.Min.Z + b.Max.Z) / 2)
        if not (X0 <= c.X <= X1 and Y0 <= c.Y <= Y1): continue
        h = ''
        try: h = '%s %s' % (e.Host.GetType().Name, e.Host.Id.Value)
        except Exception: pass
        regs.append((e, c))
        L.append('id %s (%.1f,%.1f) z%.2f host %s' % (e.Id.Value, c.X, c.Y, c.Z, h))
    except Exception: pass
if args.get('delete'):
    t = Transaction(doc, 'OneTake: cleanup registers'); _prep(t); t.Start()
    doc.Delete(List[ElementId]([ElementId(i) for i in args['delete']]))
    t.Commit()
    L.append('deleted %d' % len(args['delete']))
if args.get('place_on_2nd'):
    # find the 2nd floor slab
    host = None
    for f in FEC(doc).OfClass(Floor):
        b = f.get_BoundingBox(None)
        if b is None: continue
        cx = (b.Min.X + b.Max.X) / 2; cy = (b.Min.Y + b.Max.Y) / 2
        if X0 <= cx <= X1 and Y0 <= cy <= Y1 and 10.0 < b.Max.Z < 13.0:
            host = f; break
    L.append('2nd slab: %s (z %.2f-%.2f)' % (host.Id.Value if host else 'NONE',
             host.get_BoundingBox(None).Min.Z if host else 0,
             host.get_BoundingBox(None).Max.Z if host else 0))
    src = doc.GetElement(ElementId(2186781))
    sym = src.Symbol
    PTS = [(1181.6, -131.8), (1179.6, -145.3), (1170.7, -136.7),
           (1168.6, -147.0), (1161.6, -136.4)]
    t = Transaction(doc, 'OneTake: registers on 2nd'); _prep(t); t.Start()
    n = 0
    for x, y in PTS:
        try:
            fi = doc.Create.NewFamilyInstance(_XYZ(x, y, 11.67), sym, host,
                                              StructuralType.NonStructural)
            n += 1
        except Exception as ex:
            L.append('place FAIL %s' % str(ex)[:60])
    doc.Regenerate(); t.Commit()
    L.append('placed %d on 2nd' % n)
result = '\n'.join(L)
