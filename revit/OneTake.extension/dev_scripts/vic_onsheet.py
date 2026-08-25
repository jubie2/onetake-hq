# Put the vicinity map raster directly ON sheet A01 (the pattern CALGREEN uses).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewSheet, Viewport,
                               ImageInstance, ImageType, ImageTypeOptions, ImageTypeSource,
                               ImagePlacementOptions, BoxPlacement, ElementId, XYZ as _XYZ,
                               TextNote, TextNoteType, TextNoteOptions, HorizontalTextAlignment,
                               BuiltInParameter as BIP)
from System.Collections.Generic import List
IMG = r'C:\dev\onetake-hq\revit\reference\keeler-vicinity.png'
CX, CY, PW = 2.63, 1.07, 0.34
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A01': sh = s; break
vv = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == 'VINCINITY': vv = x; break
L = []
t = Transaction(doc, 'OneTake: vicinity on sheet'); _prep(t); t.Start()
# remove the viewport + the in-view image and note
for vpid in list(sh.GetAllViewports()):
    vp = doc.GetElement(vpid)
    if vp.ViewId == vv.Id:
        doc.Delete(vp.Id); L.append('removed VINCINITY viewport')
kill = [e.Id for e in FEC(doc, vv.Id).WhereElementIsNotElementType()
        if isinstance(e, (ImageInstance, TextNote))]
if kill: doc.Delete(List[ElementId](kill)); L.append('cleared %d in-view elements' % len(kill))
doc.Regenerate()
# place the raster on the sheet
it = ImageType.Create(doc, ImageTypeOptions(IMG, False, ImageTypeSource.Import))
inst = ImageInstance.Create(doc, sh, it.Id,
                            ImagePlacementOptions(_XYZ(CX, CY, 0), BoxPlacement.Center))
doc.Regenerate()
inst.Width = PW
doc.Regenerate()
b = inst.get_BoundingBox(sh)
L.append('image on sheet: (%.2f,%.2f)-(%.2f,%.2f)' % (b.Min.X, b.Min.Y, b.Max.X, b.Max.Y))
tt = None
for t2 in FEC(doc).OfClass(TextNoteType):
    if (t2.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == 'ARCH TEXT 12 1/8"':
        tt = t2; break
o = TextNoteOptions(tt.Id)
o.HorizontalAlignment = HorizontalTextAlignment.Center
TextNote.Create(doc, sh.Id, _XYZ(CX, b.Min.Y - 0.015, 0), 'NO SCALE', o)
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
