# Copy the 5 ADU floor supply registers from 1st to 2nd floor (+11.0 ft),
# then report what the 2nd floor mech view sees.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ElementId,
                               ElementTransformUtils, XYZ as _XYZ,
                               BuiltInCategory as BIC)
from System.Collections.Generic import List
IDS = [2186781, 2186782, 2186783, 2186784, 2186785]
t = Transaction(doc, 'OneTake: copy registers up'); _prep(t); t.Start()
new = ElementTransformUtils.CopyElements(
    doc, List[ElementId]([ElementId(i) for i in IDS]), _XYZ(0, 0, 11.0))
doc.Regenerate(); t.Commit()
L = ['copied %d' % len(list(new))]
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == 'ADU - 2nd Floor Mechanical Plan': v = x; break
n = 0
for e in FEC(doc, v.Id).OfCategory(BIC.OST_MechanicalEquipment).WhereElementIsNotElementType():
    b = e.get_BoundingBox(None)
    c = ((b.Min.X + b.Max.X) / 2, (b.Min.Y + b.Max.Y) / 2, (b.Min.Z + b.Max.Z) / 2)
    L.append('visible: id %s (%.1f,%.1f) z%.1f' % (e.Id.Value, c[0], c[1], c[2]))
    n += 1
L.append('%d registers visible in 2nd floor view' % n)
result = '\n'.join(L)
