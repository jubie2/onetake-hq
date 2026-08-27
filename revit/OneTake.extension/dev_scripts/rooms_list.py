# Rooms in the ADU region with level + center; plus available fan-ish families.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, FamilySymbol,
                               BuiltInCategory as BIC, XYZ as _XYZ,
                               BuiltInParameter as BIP)
from Autodesk.Revit.DB import SpatialElement
from Autodesk.Revit.DB.Architecture import Room
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
L = []
for e in [r for r in FEC(doc).OfClass(SpatialElement) if isinstance(r, Room)]:
    try:
        if e.Area <= 0: continue
        p = e.Location.Point
        if not (X0 <= p.X <= X1 and Y0 <= p.Y <= Y1): continue
        lvl = doc.GetElement(e.LevelId)
        L.append('ROOM id %s "%s" (%.1f,%.1f) lvl %s area %.0f' % (
            e.Id.Value, e.get_Parameter(BIP.ROOM_NAME).AsString(), p.X, p.Y,
            lvl.Name if lvl else '?', e.Area))
    except Exception: pass
L.append('--- fan/access/register families ---')
seen = set()
for s in FEC(doc).OfClass(FamilySymbol):
    try:
        fn = s.Family.Name
        low = fn.lower()
        if any(k in low for k in ('fan', 'exhaust', 'attic', 'access', 'register',
                                  'diffuser', 'grille')):
            key = '%s : %s' % (fn, s.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString())
            if key not in seen:
                seen.add(key)
                L.append('%s | %s' % (s.Category.Name, key))
    except Exception: pass
result = '\n'.join(L)
