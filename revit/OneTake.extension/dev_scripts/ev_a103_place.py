# A103: swap old Logan sections for the 4 new ADU sections; hide section marks.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               ElementId, XYZ as _XYZ, Category,
                               BuiltInCategory as BIC)
from System.Collections.Generic import List
NEW = [
 (2244668, (0.62, 1.42)),  # Section 1 top-left
 (2244677, (1.85, 1.42)),  # Section 2 top-right
 (2244686, (0.62, 0.42)),  # Section 3 bottom-left
 (2244695, (1.85, 0.42)),  # Section 4 bottom-right
]
L = []
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A103': sh = s
old = []
for vp in FEC(doc, sh.Id).OfClass(Viewport):
    v = doc.GetElement(vp.ViewId)
    if v.Name.startswith('Section '): old.append(vp.Id)
t = Transaction(doc, 'OneTake: A103 new sections'); _prep(t); t.Start()
if old: doc.Delete(List[ElementId](old)); L.append('removed %d old vps' % len(old))
doc.Regenerate()
seccat = Category.GetCategory(doc, BIC.OST_Sections)
for vid, (cx, cy) in NEW:
    v = doc.GetElement(ElementId(vid))
    try: v.SetCategoryHidden(seccat.Id, True)
    except Exception: pass
    vp = Viewport.Create(doc, sh.Id, ElementId(vid), _XYZ(cx, cy, 0))
    doc.Regenerate()
    try: vp.LabelOffset = _XYZ(0.06, -0.045, 0)
    except Exception: pass
    ol = vp.GetBoxOutline()
    L.append('%s box (%.2f,%.2f)-(%.2f,%.2f)' % (
        v.Name, ol.MinimumPoint.X, ol.MinimumPoint.Y,
        ol.MaximumPoint.X, ol.MaximumPoint.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
