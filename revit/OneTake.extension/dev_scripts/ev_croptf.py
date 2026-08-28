# Compare crop transforms of 718579 vs the new independent views; report world windows.
from Autodesk.Revit.DB import ElementId, XYZ as _XYZ
L = []
for vid in [718579, 2244950, 2244930, 32]:
    v = doc.GetElement(ElementId(vid))
    cb = v.CropBox; T = cb.Transform
    a = T.OfPoint(_XYZ(cb.Min.X, cb.Min.Y, 0))
    b = T.OfPoint(_XYZ(cb.Max.X, cb.Max.Y, 0))
    L.append('%s (%s): basisX (%.3f,%.3f) origin (%.1f,%.1f) local (%.1f,%.1f)-(%.1f,%.1f) world (%.1f,%.1f)-(%.1f,%.1f)' % (
        vid, v.Name, T.BasisX.X, T.BasisX.Y, T.Origin.X, T.Origin.Y,
        cb.Min.X, cb.Min.Y, cb.Max.X, cb.Max.Y,
        min(a.X, b.X), min(a.Y, b.Y), max(a.X, b.X), max(a.Y, b.Y)))
result = '\n'.join(L)
