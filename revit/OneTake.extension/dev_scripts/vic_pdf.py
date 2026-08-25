# Place the vicinity map as a PDF image (the pattern that provably renders on A04).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, ImageInstance,
                               ImageType, ImageTypeOptions, ImageTypeSource,
                               ImagePlacementOptions, BoxPlacement, ElementId, XYZ as _XYZ)
from System.Collections.Generic import List
PDF = r'C:\dev\onetake-hq\revit\reference\keeler-vicinity.pdf'
CX, CY = 2.63, 1.07
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A01': sh = s; break
L = []
t = Transaction(doc, 'OneTake: vicinity as PDF'); _prep(t); t.Start()
kill = [e.Id for e in FEC(doc, sh.Id).OfClass(ImageInstance)
        if 'keeler' in (doc.GetElement(e.GetTypeId()).Category.Name + str(e.Name)).lower()
        or 'keeler' in str(e.Name).lower()]
if not kill:
    kill = [e.Id for e in FEC(doc, sh.Id).OfClass(ImageInstance)
            if 'vicinity' in str(e.Name).lower()]
if kill: doc.Delete(List[ElementId](kill)); L.append('removed %d png instance(s)' % len(kill))
doc.Regenerate()
opt = ImageTypeOptions(PDF, False, ImageTypeSource.Import)
try: opt.PageNumber = 1
except Exception: pass
it = ImageType.Create(doc, opt)
inst = ImageInstance.Create(doc, sh, it.Id,
                            ImagePlacementOptions(_XYZ(CX, CY, 0), BoxPlacement.Center))
doc.Regenerate()
b = inst.get_BoundingBox(sh)
L.append('pdf image: (%.3f,%.3f)-(%.3f,%.3f) w=%.3f' % (
    b.Min.X, b.Min.Y, b.Max.X, b.Max.Y, b.Max.X - b.Min.X))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
