# Copy the missing kitchen-counter GFI outlets from 1st to 2nd floor (+11 ft),
# fix Phase Created, verify visibility in the 2nd floor electrical view.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ElementId,
                               ElementTransformUtils, XYZ as _XYZ,
                               BuiltInParameter as BIP)
from System.Collections.Generic import List
IDS = [2194242, 2194262, 2194311, 2194327, 2194352]
src = doc.GetElement(ElementId(IDS[0]))
phid = src.get_Parameter(BIP.PHASE_CREATED).AsElementId()
t = Transaction(doc, 'OneTake: kitchen GFI 2nd floor'); _prep(t); t.Start()
new = list(ElementTransformUtils.CopyElements(
    doc, List[ElementId]([ElementId(i) for i in IDS]), _XYZ(0, 0, 11.0)))
for nid in new:
    e = doc.GetElement(nid)
    p = e.get_Parameter(BIP.PHASE_CREATED)
    if p and not p.IsReadOnly and p.AsElementId() != phid:
        p.Set(phid)
doc.Regenerate(); t.Commit()
L = ['copied %d' % len(new)]
for nid in new:
    e = doc.GetElement(nid)
    b = e.get_BoundingBox(None)
    L.append('new id %s z %.1f-%.1f' % (nid.Value, b.Min.Z, b.Max.Z))
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == 'ADU - 2nd Floor Electrical Plan': v = x; break
vis = [e.Id.Value for e in FEC(doc, v.Id).WhereElementIsNotElementType()
       if e.Id in new]
L.append('visible in 2nd elec view: %d of %d' % (len(vis), len(new)))
result = '\n'.join(L)
