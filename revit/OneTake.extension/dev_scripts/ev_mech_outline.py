# Diagnose the huge outline: category hiding + annotation crop on mech view.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               ElementId, XYZ as _XYZ, Category,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
v = doc.GetElement(ElementId(2244930))
L = []
t = Transaction(doc, 'OneTake: mech outline'); _prep(t); t.Start()
for bic in [BIC.OST_Sections, BIC.OST_Elev, BIC.OST_Grids, BIC.OST_CLines,
            BIC.OST_ReferenceLines]:
    try:
        c = Category.GetCategory(doc, bic)
        v.SetCategoryHidden(c.Id, True)
        L.append('%s hidden' % c.Name)
    except Exception as ex:
        L.append('FAIL %s %s' % (bic, str(ex)[:40]))
p = v.get_Parameter(BIP.VIEWER_ANNOTATION_CROP_ACTIVE)
if p and not p.IsReadOnly:
    p.Set(1); L.append('annotation crop on')
doc.Regenerate()
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A200':
        for vp in FEC(doc, s.Id).OfClass(Viewport):
            if vp.ViewId.Value == 2244930:
                vp.SetBoxCenter(_XYZ(2.36, 1.42, 0))
                doc.Regenerate()
                ol = vp.GetBoxOutline()
                L.append('vp (%.2f,%.2f)-(%.2f,%.2f)' % (
                    ol.MinimumPoint.X, ol.MinimumPoint.Y,
                    ol.MaximumPoint.X, ol.MaximumPoint.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
