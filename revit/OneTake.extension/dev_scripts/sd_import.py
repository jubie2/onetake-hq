# Put the approved-set structural content onto SD0/SD1/SD2: wipe stub viewports +
# old imports, import the prepared PDFs (Draw Layer foreground), park SD3.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               ImageInstance, ImageType, ImageTypeOptions,
                               ImageTypeSource, ImagePlacementOptions, BoxPlacement,
                               ElementId, XYZ as _XYZ, BuiltInParameter as BIP)
from System.Collections.Generic import List
JOBS = {
 'SD0': 'C:/dev/onetake-hq/revit/reference/sd0-import5.pdf',
 'SD1': 'C:/dev/onetake-hq/revit/reference/sd1-import5.pdf',
 'SD2': 'C:/dev/onetake-hq/revit/reference/sd2-import5.pdf',
}
CX, CY = 1.42 - 0.085, 0.92 - 0.085
L = []
t = Transaction(doc, 'OneTake: SD imports'); _prep(t); t.Start()
for s in FEC(doc).OfClass(ViewSheet):
    num = s.SheetNumber
    if num in JOBS:
        kill = [vp.Id for vp in FEC(doc, s.Id).OfClass(Viewport)]
        kill += [im.Id for im in FEC(doc, s.Id).OfClass(ImageInstance)]
        if kill: doc.Delete(List[ElementId](kill))
        doc.Regenerate()
        it = ImageType.Create(doc, ImageTypeOptions(JOBS[num], False, ImageTypeSource.Import))
        inst = ImageInstance.Create(doc, s, it.Id,
                                    ImagePlacementOptions(_XYZ(CX, CY, 0), BoxPlacement.Center))
        doc.Regenerate()
        p = inst.LookupParameter('Draw Layer')
        if p and not p.IsReadOnly: p.Set(0)
        b = inst.get_BoundingBox(s)
        L.append('%s: wiped %d, placed %.2fx%.2f ft' % (
            num, len(kill), b.Max.X - b.Min.X, b.Max.Y - b.Min.Y))
    elif num == 'SD3':
        s.SheetNumber = 'X-SD3'
        p = s.get_Parameter(BIP.SHEET_SCHEDULED)
        if p and not p.IsReadOnly: p.Set(0)
        L.append('SD3 parked')
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
