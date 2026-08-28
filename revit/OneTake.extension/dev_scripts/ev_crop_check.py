# Check which views are on A101, and wall bboxes on 1st vs 2nd floor levels
# to know the right crop region for the 2nd floor plan.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               Wall, ElementId)
L = []
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A101':
        L.append('--- A101 viewports ---')
        for vp in FEC(doc, s.Id).OfClass(Viewport):
            v = doc.GetElement(vp.ViewId)
            c = vp.GetBoxCenter()
            L.append('  %s (id %s) center (%.2f,%.2f)' % (v.Name, v.Id.Value, c.X, c.Y))
# wall bboxes per level near the 1st-floor-plan crop
v1 = doc.GetElement(ElementId(718579))
v2 = doc.GetElement(ElementId(1715860))
for tag, v in [('1st view', v1), ('2nd view', v2)]:
    lvlp = v.GenLevel
    L.append('--- %s "%s" genlevel=%s ---' % (tag, v.Name, lvlp.Name if lvlp else '?'))
    xs = []; ys = []; n = 0
    for w in FEC(doc, v.Id).OfClass(Wall):
        bb = w.get_BoundingBox(None)
        if bb:
            xs += [bb.Min.X, bb.Max.X]; ys += [bb.Min.Y, bb.Max.Y]; n += 1
    if xs:
        L.append('  %d walls visible, bbox (%.1f,%.1f)-(%.1f,%.1f)' % (
            n, min(xs), min(ys), max(xs), max(ys)))
    else:
        L.append('  no walls visible in view')
    cb = v.CropBox
    L.append('  crop (%.1f,%.1f)-(%.1f,%.1f) active=%s' % (
        cb.Min.X, cb.Min.Y, cb.Max.X, cb.Max.Y, v.CropBoxActive))
# also: all walls whose base level is the 2nd floor level (1715859), full model
xs = []; ys = []; n = 0
for w in FEC(doc).OfClass(Wall):
    p = w.LookupParameter('Base Constraint')
    if p and p.AsElementId().Value == 1715859:
        bb = w.get_BoundingBox(None)
        if bb:
            xs += [bb.Min.X, bb.Max.X]; ys += [bb.Min.Y, bb.Max.Y]; n += 1
if xs:
    L.append('--- all walls based on 2nd FLoor Level: %d, bbox (%.1f,%.1f)-(%.1f,%.1f)' % (
        n, min(xs), min(ys), max(xs), max(ys)))
result = '\n'.join(L)
