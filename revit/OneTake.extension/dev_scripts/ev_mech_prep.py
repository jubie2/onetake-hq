# Room centers of the new ADU + device family symbols available in the doc.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, FamilySymbol,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
L = []
for r in FEC(doc).OfCategory(BIC.OST_Rooms):
    try:
        p = r.Location.Point
        if not (1110 < p.X < 1210 and 55 < p.Y < 135): continue
        lvl = doc.GetElement(r.LevelId).Name
        nm = r.get_Parameter(BIP.ROOM_NAME).AsString()
        L.append('ROOM [%s] %s (%.1f,%.1f)' % (lvl, nm, p.X, p.Y))
    except Exception: pass
seen = set()
for cat in [BIC.OST_MechanicalEquipment, BIC.OST_DuctTerminal,
            BIC.OST_ElectricalFixtures, BIC.OST_ElectricalEquipment,
            BIC.OST_GenericModel, BIC.OST_SpecialityEquipment]:
    for s in FEC(doc).OfClass(FamilySymbol).OfCategory(cat):
        key = '%s :: %s' % (s.Family.Name, s.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString())
        if key in seen: continue
        seen.add(key)
        L.append('SYM [%s] %s' % (s.Category.Name, key))
result = '\n'.join(L)
