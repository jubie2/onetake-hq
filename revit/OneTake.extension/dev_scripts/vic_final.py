# Clean re-place of the vicinity raster on A01 at native (DPI-driven) size.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, ImageInstance,
                               ImageType, ImageTypeOptions, ImageTypeSource,
                               ImagePlacementOptions, BoxPlacement, ElementId, XYZ as _XYZ,
                               TextNote)
from System.Collections.Generic import List
IMG = r'C:\dev\onetake-hq\revit\reference\keeler-vicinity.png'
CX, CY = 2.63, 1.07
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A01': sh = s; break
L = []
t = Transaction(doc, 'OneTake: vicinity final'); _prep(t); t.Start()
kill = []
for e in FEC(doc, sh.Id).OfClass(ImageInstance):
    kill.append(e.Id)
for tn in FEC(doc, sh.Id).OfClass(TextNote):
    if (tn.Text or '').strip() == 'NO SCALE' and abs(tn.Coord.X - CX) < 0.3:
        kill.append(tn.Id)
if kill: doc.Delete(List[ElementId](kill)); L.append('removed %d old' % len(kill))
# drop orphaned keeler-vicinity ImageTypes
old_t = []
for it in FEC(doc).OfClass(ImageType):
    try:
        if 'keeler-vicinity' in (it.get_Parameter(__import__('Autodesk.Revit.DB', fromlist=['BuiltInParameter']).BuiltInParameter.SYMBOL_NAME_PARAM).AsString() or ''): old_t.append(it.Id)
    except Exception: pass
if old_t:
    try: doc.Delete(List[ElementId](old_t)); L.append('purged %d image types' % len(old_t))
    except Exception as ex: L.append('type purge skipped: %s' % str(ex)[:40])
doc.Regenerate()
it = ImageType.Create(doc, ImageTypeOptions(IMG, False, ImageTypeSource.Import))
inst = ImageInstance.Create(doc, sh, it.Id,
                            ImagePlacementOptions(_XYZ(CX, CY, 0), BoxPlacement.Center))
doc.Regenerate()
b = inst.get_BoundingBox(sh)
L.append('placed at native size: (%.3f,%.3f)-(%.3f,%.3f)  w=%.3f ft' % (
    b.Min.X, b.Min.Y, b.Max.X, b.Max.Y, b.Max.X - b.Min.X))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
