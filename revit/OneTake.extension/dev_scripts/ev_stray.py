# Find elements visible in the new mech/elec views near the NE corner region.
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ElementId
L = []
for vid in [2244930, 2244950]:
    v = doc.GetElement(ElementId(vid))
    L.append('--- %s ---' % v.Name)
    for e in FEC(doc, v.Id).WhereElementIsNotElementType():
        try:
            bb = e.get_BoundingBox(v)
            if bb is None: continue
            w = bb.Max.X - bb.Min.X; h = bb.Max.Y - bb.Min.Y
            # long, thin, near/beyond NE of the building
            if bb.Max.X > 1190 and bb.Max.Y > 120 and (w > 20 or h > 20):
                cat = e.Category.Name if e.Category else '?'
                L.append('%s [%s] (%.0f,%.0f)-(%.0f,%.0f) owner=%s' % (
                    e.Id.Value, cat, bb.Min.X, bb.Min.Y, bb.Max.X, bb.Max.Y,
                    e.OwnerViewId.Value))
        except Exception: pass
result = '\n'.join(L)
