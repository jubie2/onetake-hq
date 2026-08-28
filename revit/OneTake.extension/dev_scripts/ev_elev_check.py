# Report origin/direction/crop of the 4 new elevation sections.
from Autodesk.Revit.DB import ElementId
L = []
for vid in [2244567, 2244576, 2244585, 2244594]:
    v = doc.GetElement(ElementId(vid))
    o = v.Origin; d = v.ViewDirection; r = v.RightDirection
    cb = v.CropBox
    fc = v.get_Parameter(__import__('Autodesk').Revit.DB.BuiltInParameter.VIEWER_BOUND_OFFSET_FAR)
    L.append('%s: origin(%.0f,%.0f,%.0f) dir(%.0f,%.0f,%.0f) right(%.0f,%.0f,%.0f) crop z %.1f..%.1f far=%s' % (
        v.Name, o.X, o.Y, o.Z, d.X, d.Y, d.Z, r.X, r.Y, r.Z,
        cb.Min.Z, cb.Max.Z, fc.AsDouble() if fc else -1))
result = '\n'.join(L)
