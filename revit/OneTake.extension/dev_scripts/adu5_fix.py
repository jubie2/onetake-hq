from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewSheet, Viewport,
                               XYZ as _XYZ)
L = []
t = Transaction(doc, 'OneTake: adu5 fix + notes move'); _prep(t); t.Start()
# 1. re-activate the 2nd floor mech crop and re-center its viewport
v2 = None
for v in FEC(doc).OfClass(View):
    if not v.IsTemplate and v.Name == 'ADU - 2nd Floor Mechanical Plan': v2 = v; break
if not v2.CropBoxActive:
    v2.CropBoxActive = True
    v2.CropBoxVisible = False
    L.append('2nd floor mech: crop re-activated')
doc.Regenerate()
sh5 = sh7 = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'ADU-5': sh5 = s
    if s.SheetNumber == 'ADU-7': sh7 = s
for vp in FEC(doc, sh5.Id).OfClass(Viewport):
    if vp.ViewId == v2.Id:
        vp.SetBoxCenter(_XYZ(1.45, 1.32, 0))
        doc.Regenerate()
        ol = vp.GetBoxOutline()
        L.append('2nd floor mech viewport: %.2f x %.2f at (1.45,1.32)' % (
            ol.MaximumPoint.X - ol.MinimumPoint.X, ol.MaximumPoint.Y - ol.MinimumPoint.Y))
# 2. move MECH GENERAL NOTES viewport from ADU-5 to ADU-7
nv = None
for v in FEC(doc).OfClass(View):
    if not v.IsTemplate and v.Name == 'ADU - MECH GENERAL NOTES': nv = v; break
for vp in list(FEC(doc, sh5.Id).OfClass(Viewport)):
    if vp.ViewId == nv.Id:
        doc.Delete(vp.Id); L.append('removed notes viewport from ADU-5')
doc.Regenerate()
if Viewport.CanAddViewToSheet(doc, sh7.Id, nv.Id):
    vp = Viewport.Create(doc, sh7.Id, nv.Id, _XYZ(2.40, 0.58, 0))
    vp.LabelOffset = _XYZ(0, 0, 0)
    doc.Regenerate()
    ol = vp.GetBoxOutline()
    L.append('placed on ADU-7: (%.2f,%.2f)-(%.2f,%.2f)' % (
        ol.MinimumPoint.X, ol.MinimumPoint.Y, ol.MaximumPoint.X, ol.MaximumPoint.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
