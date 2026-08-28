# A02: narrow the existing-residence plumbing note; find the signature squiggle.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, ElementId,
                               CurveElement, Group)
L = []
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A02': sh = s
for e in FEC(doc, sh.Id).OfClass(CurveElement):
    bb = e.get_BoundingBox(sh)
    if bb:
        L.append('CURVE %s (%.2f,%.2f)-(%.2f,%.2f)' % (e.Id.Value,
                 bb.Min.X, bb.Min.Y, bb.Max.X, bb.Max.Y))
for e in FEC(doc, sh.Id).OfClass(Group):
    bb = e.get_BoundingBox(sh)
    if bb:
        L.append('GROUP %s (%.2f,%.2f)-(%.2f,%.2f)' % (e.Id.Value,
                 bb.Min.X, bb.Min.Y, bb.Max.X, bb.Max.Y))
t = Transaction(doc, 'OneTake: A02 plumb narrow'); _prep(t); t.Start()
e = doc.GetElement(ElementId(2148238))
e.Text = ('TOTAL PLUMBING FIXTURE CALCULATION\r\r'
          'EXISTING RESIDENCE (2-STORY):\r'
          '\tEXISTING FIXTURES\r'
          '\tTO REMAIN\r'
          '\t(NO CHANGE)')
doc.Regenerate(); t.Commit()
L.append('plumb note narrowed')
result = '\n'.join(L)
