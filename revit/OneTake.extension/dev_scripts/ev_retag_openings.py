# Re-tag the rebuilt door + 3 windows on the A101 1st-floor plan.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, FamilySymbol,
                               IndependentTag, Reference, TagOrientation,
                               ElementId, XYZ as _XYZ, BuiltInCategory as BIC,
                               BuiltInParameter as BIP)
V = 718579
JOBS = [(2246154, BIC.OST_DoorTags), (2246155, BIC.OST_WindowTags),
        (2246157, BIC.OST_WindowTags), (2246158, BIC.OST_WindowTags)]
dt = wt = None
for s in FEC(doc).OfClass(FamilySymbol).OfCategory(BIC.OST_DoorTags):
    dt = s; break
for s in FEC(doc).OfClass(FamilySymbol).OfCategory(BIC.OST_WindowTags):
    if 'Number' in s.Family.Name: wt = s; break
if wt is None:
    for s in FEC(doc).OfClass(FamilySymbol).OfCategory(BIC.OST_WindowTags):
        wt = s; break
v = doc.GetElement(ElementId(V))
L = ['door tag %s, window tag %s' % (dt.Family.Name, wt.Family.Name)]
t = Transaction(doc, 'OneTake: retag rebuilt openings'); _prep(t); t.Start()
for s in (dt, wt):
    if not s.IsActive: s.Activate()
doc.Regenerate()
for eid, cat in JOBS:
    e = doc.GetElement(ElementId(eid))
    if e is None: L.append('  %s MISSING' % eid); continue
    sym = dt if cat == BIC.OST_DoorTags else wt
    p = e.Location.Point
    try:
        IndependentTag.Create(doc, sym.Id, v.Id, Reference(e), False,
                              TagOrientation.Horizontal, _XYZ(p.X, p.Y, p.Z))
        mk = e.get_Parameter(BIP.ALL_MODEL_MARK)
        L.append('  tagged %s mark %s' % (eid, mk.AsString() if mk else '?'))
    except Exception as ex:
        L.append('  %s tag FAILED %s' % (eid, str(ex)[:50]))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
