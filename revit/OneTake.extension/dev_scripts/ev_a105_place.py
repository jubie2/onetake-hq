# A105: swap old Logan elevations for the 4 new ADU elevations.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               ElementId, XYZ as _XYZ, Category,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
from System.Collections.Generic import List
NEW = [
 (2244612, 'South Elev.', (0.62, 1.42)),
 (2244603, 'North Elev.', (1.85, 1.42)),
 (2244630, 'West Elev.',  (0.62, 0.42)),
 (2244621, 'East Elev.',  (1.85, 0.42)),
]
L = []
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A105': sh = s
old = []
for vp in FEC(doc, sh.Id).OfClass(Viewport):
    v = doc.GetElement(vp.ViewId)
    if 'Elev' in v.Name: old.append(vp.Id)
t = Transaction(doc, 'OneTake: A105 new elevations'); _prep(t); t.Start()
if old: doc.Delete(List[ElementId](old)); L.append('removed %d old vps' % len(old))
doc.Regenerate()
seccat = Category.GetCategory(doc, BIC.OST_Sections)
for vid, title, (cx, cy) in NEW:
    v = doc.GetElement(ElementId(vid))
    try: v.SetCategoryHidden(seccat.Id, True)
    except Exception as ex: L.append('seccat %s' % str(ex)[:30])
    p = v.get_Parameter(BIP.VIEW_DESCRIPTION)
    if p and not p.IsReadOnly: p.Set(title)
    vp = Viewport.Create(doc, sh.Id, ElementId(vid), _XYZ(cx, cy, 0))
    doc.Regenerate()
    try: vp.LabelOffset = _XYZ(0.06, -0.045, 0)
    except Exception: pass
    ol = vp.GetBoxOutline()
    L.append('%s at (%.2f,%.2f) box (%.2f,%.2f)-(%.2f,%.2f)' % (
        title, cx, cy, ol.MinimumPoint.X, ol.MinimumPoint.Y,
        ol.MaximumPoint.X, ol.MaximumPoint.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
