# A101 cleanup: list sheet-level annotations (north arrows, stale notes) with ids.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, TextNote,
                               FamilyInstance)
L = []
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber != 'A101': continue
    for e in FEC(doc, s.Id).OfClass(TextNote):
        txt = (e.Text or '').replace('\r', ' ').replace('\n', ' ')
        c = e.Coord
        L.append('TEXT id %s at (%.2f,%.2f): %s' % (e.Id.Value, c.X, c.Y, txt[:70]))
    for e in FEC(doc, s.Id).OfClass(FamilyInstance):
        try: fam = e.Symbol.Family.Name
        except Exception: fam = '?'
        bb = e.get_BoundingBox(s)
        if bb:
            L.append('FAMINST id %s "%s" at (%.2f,%.2f)' % (
                e.Id.Value, fam, (bb.Min.X + bb.Max.X) / 2, (bb.Min.Y + bb.Max.Y) / 2))
result = '\n'.join(L)
