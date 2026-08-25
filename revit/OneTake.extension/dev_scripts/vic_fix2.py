from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ImageInstance, ViewSheet,
                               Viewport, ImportInstance, ElementId, XYZ as _XYZ)
from System.Collections.Generic import List
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == 'VINCINITY': v = x; break
L = []
t = Transaction(doc, 'OneTake: vicinity cleanup'); _prep(t); t.Start()
kill = [e.Id for e in FEC(doc, v.Id).OfClass(ImportInstance)]
if kill:
    doc.Delete(List[ElementId](kill)); L.append('deleted %d dwg import(s)' % len(kill))
for e in FEC(doc, v.Id).OfClass(ImageInstance):
    e.Width = 0.34 * v.Scale
    L.append('image width -> %.1f model ft (0.34 ft paper)' % (0.34 * v.Scale))
doc.Regenerate()
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber != 'A01': continue
    for vpid in s.GetAllViewports():
        vp = doc.GetElement(vpid)
        if doc.GetElement(vp.ViewId).Id == v.Id:
            vp.SetBoxCenter(_XYZ(2.62, 1.06, 0))
            doc.Regenerate()
            ol = vp.GetBoxOutline()
            L.append('viewport now %.2f x %.2f at (2.62, 1.06)' % (
                ol.MaximumPoint.X - ol.MinimumPoint.X, ol.MaximumPoint.Y - ol.MinimumPoint.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
