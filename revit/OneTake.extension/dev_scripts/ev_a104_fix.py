# A104: remove old roof viewports, place Roof Deck Level as the roof plan,
# list sheet texts for cleanup.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               ElementId, XYZ as _XYZ, TextNote,
                               BuiltInParameter as BIP)
from System.Collections.Generic import List
L = []
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A104': sh = s
for e in FEC(doc, sh.Id).OfClass(TextNote):
    c = e.Coord
    L.append('TEXT %s (%.2f,%.2f): %s' % (e.Id.Value, c.X, c.Y,
             (e.Text or '').replace('\r', '|').replace('\n', '|')[:70]))
old = []
for vp in FEC(doc, sh.Id).OfClass(Viewport):
    v = doc.GetElement(vp.ViewId)
    if v.Name in ('Roof Plan', 'Roof Framing Plan'): old.append(vp.Id)
t = Transaction(doc, 'OneTake: A104 roof deck'); _prep(t); t.Start()
if old: doc.Delete(List[ElementId](old)); L.append('removed %d old roof vps' % len(old))
doc.Regenerate()
v = doc.GetElement(ElementId(2218677))
v.Scale = 64
p = v.get_Parameter(BIP.VIEW_DESCRIPTION)
if p and not p.IsReadOnly: p.Set('Roof Plan')
vp = Viewport.Create(doc, sh.Id, ElementId(2218677), _XYZ(1.30, 1.25, 0))
doc.Regenerate()
try: vp.LabelOffset = _XYZ(0.06, -0.045, 0)
except Exception: pass
ol = vp.GetBoxOutline()
L.append('roof deck vp box (%.2f,%.2f)-(%.2f,%.2f)' % (
    ol.MinimumPoint.X, ol.MinimumPoint.Y, ol.MaximumPoint.X, ol.MaximumPoint.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
