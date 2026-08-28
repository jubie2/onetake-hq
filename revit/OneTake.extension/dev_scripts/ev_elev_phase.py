# Copy phase + phase filter from 1st Floor Plan (718579) to the 4 new elevations.
from Autodesk.Revit.DB import ElementId, BuiltInParameter as BIP
src = doc.GetElement(ElementId(718579))
ph = src.get_Parameter(BIP.VIEW_PHASE).AsElementId()
pf = src.get_Parameter(BIP.VIEW_PHASE_FILTER).AsElementId()
L = ['src phase %s filter %s' % (ph.Value, pf.Value)]
t = Transaction(doc, 'OneTake: elev phases'); _prep(t); t.Start()
for vid in [2244567, 2244576, 2244585, 2244594]:
    v = doc.GetElement(ElementId(vid))
    p1 = v.get_Parameter(BIP.VIEW_PHASE)
    p2 = v.get_Parameter(BIP.VIEW_PHASE_FILTER)
    old = p1.AsElementId().Value
    if not p1.IsReadOnly: p1.Set(ph)
    if not p2.IsReadOnly: p2.Set(pf)
    L.append('%s: phase %s -> %s' % (v.Name, old, ph.Value))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
