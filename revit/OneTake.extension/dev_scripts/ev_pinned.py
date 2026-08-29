# Are the devices / walls PINNED? Pinned elements silently refuse flips and moves.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId,
                               BuiltInCategory as BIC)
L = []
np_ = p_ = 0
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try: pt = e.Location.Point
    except Exception: continue
    if pt is None or not (1120 < pt.X < 1200 and 78 < pt.Y < 128): continue
    if e.Pinned: p_ += 1
    else: np_ += 1
L.append('devices: pinned %d, not pinned %d' % (p_, np_))
for wid in (2189094, 2189148, 2189181, 2194765, 2200152):
    w = doc.GetElement(ElementId(wid))
    L.append('  wall %s pinned=%s  groupId=%s' % (
        wid, w.Pinned, w.GroupId.Value if w.GroupId else 'none'))
d = doc.GetElement(ElementId(2244856))
L.append('sample device %s pinned=%s groupId=%s' % (
    d.Id.Value, d.Pinned, d.GroupId.Value if d.GroupId else 'none'))
# and check design option / workset style blockers
try:
    L.append('  design option: %s' % (d.DesignOption.Name if d.DesignOption else 'MAIN'))
except Exception: pass
result = '\n'.join(L)
