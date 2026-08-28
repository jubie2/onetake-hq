# Hide section/elevation marks in the two ADU mech plans, re-center viewports.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewSheet,
                               Viewport, Category, BuiltInCategory as BIC,
                               XYZ as _XYZ)
def getview(nm):
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: return x
L = []
t = Transaction(doc, 'OneTake: mech hide sections'); _prep(t); t.Start()
for cat in [BIC.OST_Sections, BIC.OST_Elev]:
    c = Category.GetCategory(doc, cat)
    for nm in ['ADU 1st Floor Mech Plan', 'ADU 2nd Floor Mech Plan']:
        v = getview(nm)
        try: v.SetCategoryHidden(c.Id, True)
        except Exception as ex: L.append('%s %s' % (nm, str(ex)[:30]))
doc.Regenerate()
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A200': sh = s
for vp in FEC(doc, sh.Id).OfClass(Viewport):
    v = doc.GetElement(vp.ViewId)
    if v.Name == 'ADU 1st Floor Mech Plan':
        vp.SetBoxCenter(_XYZ(2.36, 1.42, 0))
    elif v.Name == 'ADU 2nd Floor Mech Plan':
        vp.SetBoxCenter(_XYZ(1.30, 1.42, 0))
doc.Regenerate()
for vp in FEC(doc, sh.Id).OfClass(Viewport):
    v = doc.GetElement(vp.ViewId)
    if v.Name.startswith('ADU '):
        ol = vp.GetBoxOutline()
        L.append('%s (%.2f,%.2f)-(%.2f,%.2f)' % (v.Name, ol.MinimumPoint.X,
                 ol.MinimumPoint.Y, ol.MaximumPoint.X, ol.MaximumPoint.Y))
t.Commit()
result = '\n'.join(L)
