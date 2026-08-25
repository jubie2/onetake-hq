# Final vicinity placement: delete old, place PDF image foreground with margin compensation.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, ImageInstance,
                               ImageType, ImageTypeOptions, ImageTypeSource,
                               ImagePlacementOptions, BoxPlacement, ElementId, XYZ as _XYZ)
from System.Collections.Generic import List
PDF = r'C:\dev\onetake-hq\revit\reference\keeler-vicinity.pdf'
# target drawn centre (2.63, 0.845); raster draws at +0.085,+0.085 -> place at:
CX, CY = 2.63 - 0.085, 0.845 - 0.085
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A01': sh = s; break
L = []
t = Transaction(doc, 'OneTake: vicinity place final'); _prep(t); t.Start()
kill = []
for e in FEC(doc, sh.Id).OfClass(ImageInstance):
    try:
        if 'vicinity' in (e.Name or '').lower(): kill.append(e.Id)
    except Exception: pass
if kill: doc.Delete(List[ElementId](kill)); L.append('removed %d' % len(kill))
doc.Regenerate()
it = ImageType.Create(doc, ImageTypeOptions(PDF, False, ImageTypeSource.Import))
inst = ImageInstance.Create(doc, sh, it.Id,
                            ImagePlacementOptions(_XYZ(CX, CY, 0), BoxPlacement.Center))
doc.Regenerate()
p = inst.LookupParameter('Draw Layer')
if p and not p.IsReadOnly: p.Set(0)
doc.Regenerate()
b = inst.get_BoundingBox(sh)
L.append('placed (%.3f,%.3f)-(%.3f,%.3f) w=%.3f h=%.3f -> draws at +0.085' % (
    b.Min.X, b.Min.Y, b.Max.X, b.Max.Y, b.Max.X - b.Min.X, b.Max.Y - b.Min.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
