from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ImageInstance, ViewSheet,
                               Viewport, TextNote)
L = []
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == 'VINCINITY': v = x; break
for e in FEC(doc, v.Id).WhereElementIsNotElementType():
    b = e.get_BoundingBox(v)
    bs = '(%.1f,%.1f)-(%.1f,%.1f)' % (b.Min.X, b.Min.Y, b.Max.X, b.Max.Y) if b else 'None'
    L.append('%-14s %-10s bbox %s' % (e.Category.Name if e.Category else type(e).__name__, e.Id, bs))
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber != 'A01': continue
    for vpid in s.GetAllViewports():
        vp = doc.GetElement(vpid)
        vv = doc.GetElement(vp.ViewId)
        if vv.Id == v.Id:
            ol = vp.GetBoxOutline(); c = vp.GetBoxCenter()
            L.append('viewport box %.2f x %.2f at (%.2f, %.2f)' % (
                ol.MaximumPoint.X - ol.MinimumPoint.X, ol.MaximumPoint.Y - ol.MinimumPoint.Y, c.X, c.Y))
result = '\n'.join(L)
