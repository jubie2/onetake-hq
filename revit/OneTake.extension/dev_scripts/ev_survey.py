# Survey the 6633 Electric Ave doc: title, levels, plan views + crop boxes, sheets.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewPlan, ViewSheet,
                               Level, View)
L = []
L.append('DOC: %s' % doc.Title)
L.append('--- LEVELS ---')
for lv in FEC(doc).OfClass(Level):
    L.append('  %s (id %s) elev %.2f' % (lv.Name, lv.Id.Value, lv.Elevation))
L.append('--- PLAN VIEWS ---')
for v in FEC(doc).OfClass(ViewPlan):
    if v.IsTemplate: continue
    try:
        cb = v.CropBox
        crop = 'cropActive=%s box=(%.1f,%.1f)-(%.1f,%.1f)' % (
            v.CropBoxActive, cb.Min.X, cb.Min.Y, cb.Max.X, cb.Max.Y)
    except Exception as ex:
        crop = 'crop? %s' % str(ex)[:40]
    L.append('  [%s] %s (id %s) %s' % (v.ViewType, v.Name, v.Id.Value, crop))
L.append('--- SHEETS ---')
for s in FEC(doc).OfClass(ViewSheet):
    L.append('  %s - %s (id %s)' % (s.SheetNumber, s.Name, s.Id.Value))
result = '\n'.join(L)
