# Create ADU - Section 4: a second transverse cut, parallel to Section 1, moved west.
# args {"dx":-8.4,"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewSection,
                               ViewDuplicateOption, ElementTransformUtils, XYZ as _XYZ)
dx = float(args.get('dx', -8.4))
dry = args.get('dry', True)
L = []
src = None; existing = None
for v in FEC(doc).OfClass(ViewSection):
    if v.IsTemplate: continue
    if v.Name == 'ADU - Section 1': src = v
    if v.Name == 'ADU - Section 4': existing = v
L.append('source %s, existing %s, dx %.2f' % (src.Id if src else None,
                                              existing.Id if existing else None, dx))
if src:
    o = src.Origin
    L.append('  Section 1 origin (%.1f,%.1f)  -> Section 4 at X %.1f' % (o.X, o.Y, o.X + dx))
if not dry and existing is None and src is not None:
    t = Transaction(doc, 'OneTake: ADU Section 4'); _prep(t); t.Start()
    nid = src.Duplicate(ViewDuplicateOption.Duplicate)   # no detailing - retag fresh
    nv = doc.GetElement(nid)
    nv.Name = 'ADU - Section 4'
    doc.Regenerate()
    ElementTransformUtils.MoveElement(doc, nv.Id, _XYZ(dx, 0, 0))
    doc.Regenerate()
    o2 = nv.Origin
    L.append('  created %s at origin (%.1f,%.1f,%.1f)' % (nv.Id, o2.X, o2.Y, o2.Z))
    t.Commit()
result = '\n'.join(L)
