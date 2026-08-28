# Room areas of the new ADU building (world x 1110-1210, y 55-135) by level,
# plus the text notes inside the VINCINITY drafting view (325160).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, TextNote,
                               SpatialElement, BuiltInCategory as BIC)
L = []
tot = {}
for r in FEC(doc).OfCategory(BIC.OST_Rooms):
    try:
        loc = r.Location
        if loc is None: continue
        p = loc.Point
        if not (1110 < p.X < 1210 and 55 < p.Y < 135): continue
        lvl = doc.GetElement(r.LevelId).Name
        nmp = r.get_Parameter(__import__('Autodesk').Revit.DB.BuiltInParameter.ROOM_NAME)
        nm = nmp.AsString() if nmp else '?'
        a = r.Area
        tot[lvl] = tot.get(lvl, 0) + a
        L.append('ROOM [%s] %s %.0f sf' % (lvl, nm, a))
    except Exception as ex:
        L.append('err %s' % str(ex)[:40])
for k in tot: L.append('TOTAL %s = %.0f sf' % (k, tot[k]))
v = doc.GetElement(ElementId(325160))
for e in FEC(doc, v.Id).OfClass(TextNote):
    c = e.Coord
    L.append('VIC TEXT %s (%.2f,%.2f): %s' % (
        e.Id.Value, c.X, c.Y, (e.Text or '').replace('\n', '|')[:50]))
result = '\n'.join(L)
