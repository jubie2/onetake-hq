# A103: realign the right keynote column with its bubbles.
# A105: give keynote 8 its missing bubble circle (copied from bubble 7).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, TextNote,
                               CurveElement, ElementTransformUtils, XYZ as _XYZ)
from System.Collections.Generic import List
L = []
t = Transaction(doc, 'OneTake: legend fixes'); _prep(t); t.Start()
# --- A103 right column ---
e = doc.GetElement(ElementId(1732114))
e.Text = ('2x4 STUDS @ 16" O.C. \r\r'
          'ROOF/FLR JOISTS PER PLAN \r\r'
          'R-15 BATT INSULATION\r\r'
          'R-30 BATT INSULATION\r\r'
          'FOOTING PER DETAIL ON SD1')
e.Coord = _XYZ(5.58, 7.58, 0)
L.append('A103 right column re-anchored at (5.58,7.58)')
# --- A105 bubble 8 ---
lv = doc.GetElement(ElementId(1143900))
cands = []
for ce in FEC(doc, lv.Id).OfClass(CurveElement):
    bb = ce.get_BoundingBox(lv)
    if bb is None: continue
    cx = (bb.Min.X + bb.Max.X) / 2.0; cy = (bb.Min.Y + bb.Max.Y) / 2.0
    w = bb.Max.X - bb.Min.X; h = bb.Max.Y - bb.Min.Y
    if w < 0.25 and h < 0.25 and 2.3 < cx < 2.7:
        cands.append((cy, ce.Id, cx, w, h))
cands.sort()
L.append('bubble curves found: %d  %s' % (
    len(cands), ['%.2f' % c[0] for c in cands]))
if cands:
    src = cands[0]                     # lowest existing bubble (keynote 7)
    dy = 5.645 - src[0]
    ids = List[ElementId](); ids.Add(src[1])
    new = ElementTransformUtils.CopyElements(lv, ids, lv, None, None)
    for nid in new:
        ElementTransformUtils.MoveElement(doc, nid, _XYZ(0, dy, 0))
    L.append('copied bubble from y=%.3f by dy=%.3f -> %d element(s)' % (
        src[0], dy, len(list(new))))
else:
    L.append('NO bubble curve found - circle may be a filled region')
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
