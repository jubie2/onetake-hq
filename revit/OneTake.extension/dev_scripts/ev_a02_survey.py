# A02: list text notes, revision clouds, images, generic annotations with ids.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, TextNote,
                               RevisionCloud, ImageInstance, FamilyInstance)
L = []
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber != 'A02': continue
    for e in FEC(doc, s.Id).OfClass(TextNote):
        c = e.Coord
        L.append('TEXT %s (%.2f,%.2f): %s' % (e.Id.Value, c.X, c.Y,
                 (e.Text or '').replace('\r', '|').replace('\n', '|')[:80]))
    for e in FEC(doc, s.Id).OfClass(RevisionCloud):
        bb = e.get_BoundingBox(s)
        L.append('CLOUD %s (%.2f,%.2f)-(%.2f,%.2f)' % (e.Id.Value,
                 bb.Min.X, bb.Min.Y, bb.Max.X, bb.Max.Y))
    for e in FEC(doc, s.Id).OfClass(ImageInstance):
        bb = e.get_BoundingBox(s)
        L.append('IMAGE %s (%.2f,%.2f)-(%.2f,%.2f)' % (e.Id.Value,
                 bb.Min.X, bb.Min.Y, bb.Max.X, bb.Max.Y))
    for e in FEC(doc, s.Id).OfClass(FamilyInstance):
        bb = e.get_BoundingBox(s)
        if bb:
            L.append('FAM %s "%s" (%.2f,%.2f)' % (e.Id.Value, e.Symbol.Family.Name,
                     (bb.Min.X + bb.Max.X) / 2, (bb.Min.Y + bb.Max.Y) / 2))
result = '\n'.join(L)
