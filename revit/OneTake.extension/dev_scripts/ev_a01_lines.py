# List curve-ish elements on A01 near the project data block.
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet
L = []
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A01': sh = s
for e in FEC(doc, sh.Id).WhereElementIsNotElementType():
    try:
        bb = e.get_BoundingBox(sh)
        if bb is None: continue
        if bb.Min.X > 1.2 and bb.Max.X < 1.9 and bb.Min.Y > 0.2 and bb.Max.Y < 0.9:
            cat = e.Category.Name if e.Category else '?'
            L.append('%s [%s] (%.2f,%.2f)-(%.2f,%.2f)' % (e.Id.Value, cat,
                     bb.Min.X, bb.Min.Y, bb.Max.X, bb.Max.Y))
    except Exception: pass
result = '\n'.join(L)
