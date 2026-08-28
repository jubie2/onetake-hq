# Why are new sections empty? Collect walls visible in each, check worksets,
# category hidden, crop, discipline.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, Wall, ElementId,
                               Category, BuiltInCategory as BIC)
L = ['workshared=%s' % doc.IsWorkshared]
for vid in [2244567, 2244576, 718579]:
    v = doc.GetElement(ElementId(vid))
    ws = [w for w in FEC(doc, v.Id).OfClass(Wall)]
    L.append('%s: %d walls in view; cropActive=%s discipline=%s detail=%s' % (
        v.Name, len(ws), v.CropBoxActive,
        v.Discipline if hasattr(v, 'Discipline') else '?', v.DetailLevel))
    cat = Category.GetCategory(doc, BIC.OST_Walls)
    try:
        L.append('  walls hidden=%s' % v.GetCategoryHidden(cat.Id))
    except Exception as ex:
        L.append('  cat check %s' % str(ex)[:40])
    if ws:
        bb = ws[0].get_BoundingBox(v)
        if bb:
            L.append('  wall0 bbox in view (%.1f,%.1f,%.1f)-(%.1f,%.1f,%.1f)' % (
                bb.Min.X, bb.Min.Y, bb.Min.Z, bb.Max.X, bb.Max.Y, bb.Max.Z))
result = '\n'.join(L)
