# Tag ADU doors/windows on the A101 plan views (718579 1st, 1715860 2nd).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, FamilySymbol,
                               IndependentTag, Reference, TagMode, TagOrientation,
                               ElementId, XYZ as _XYZ, BuiltInCategory as BIC,
                               BuiltInParameter as BIP)
L = []
dt = wt = None
for s in FEC(doc).OfClass(FamilySymbol).OfCategory(BIC.OST_DoorTags):
    dt = s
    break
for s in FEC(doc).OfClass(FamilySymbol).OfCategory(BIC.OST_WindowTags):
    if 'Number' in s.Family.Name: wt = s; break
if wt is None:
    for s in FEC(doc).OfClass(FamilySymbol).OfCategory(BIC.OST_WindowTags):
        wt = s
        break
L.append('door tag %s, window tag %s' % (dt.Family.Name if dt else None,
                                         wt.Family.Name if wt else None))
DOORS = [2197513, 2189633, 2189543, 2191960, 2192776, 2196306, 2196038, 2228224,
         2228133, 2193676, 2194343, 2194315, 2193646, 2195558,
         2205462, 2207390, 2210839, 2241317, 2209836, 2209389, 2205800, 2204703,
         2211038, 2206764]
WINS = [2218270, 2228264, 2228011, 2227911, 2239336, 2227947, 2228035,
        2217448, 2227413, 2227489, 2227685, 2227546, 2227712, 2217328, 2228563,
        2227776, 2217381, 2217295, 2239155, 2217254]
v1 = doc.GetElement(ElementId(718579))
v2 = doc.GetElement(ElementId(1715860))
t = Transaction(doc, 'OneTake: door window tags'); _prep(t); t.Start()
for s in [dt, wt]:
    if s and not s.IsActive: s.Activate()
doc.Regenerate()
n = 0; fail = 0
for eid, sym in [(i, dt) for i in DOORS] + [(i, wt) for i in WINS]:
    e = doc.GetElement(ElementId(eid))
    try:
        p = e.Location.Point
        z = p.Z
        v = v1 if z < 10 else v2
        tag = IndependentTag.Create(doc, sym.Id, v.Id, Reference(e), False,
                                    TagOrientation.Horizontal,
                                    _XYZ(p.X, p.Y, p.Z))
        n += 1
    except Exception as ex:
        fail += 1
        L.append('fail %s %s' % (eid, str(ex)[:40]))
doc.Regenerate(); t.Commit()
L.append('placed %d tags, %d fails' % (n, fail))
result = '\n'.join(L)
