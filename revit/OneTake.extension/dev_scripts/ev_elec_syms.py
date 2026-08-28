# Lighting + device symbols, and sample old-building elec instances (family, host).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, FamilySymbol,
                               FamilyInstance, BuiltInCategory as BIC,
                               BuiltInParameter as BIP)
L = []
for cat in [BIC.OST_LightingFixtures, BIC.OST_LightingDevices]:
    for s in FEC(doc).OfClass(FamilySymbol).OfCategory(cat):
        L.append('SYM [%s] %s :: %s' % (s.Category.Name, s.Family.Name,
                 s.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString()))
n = 0
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    bb = e.get_BoundingBox(None)
    if bb is None: continue
    cx = (bb.Min.X + bb.Max.X) / 2; cy = (bb.Min.Y + bb.Max.Y) / 2
    if 940 < cx < 1030 and -160 < cy < -80:
        host = ''
        try: host = e.Host.Category.Name if e.Host else 'none'
        except Exception: host = '?'
        L.append('OLD %s host=%s z=%.1f' % (e.Symbol.Family.Name, host, bb.Min.Z))
        n += 1
        if n >= 8: break
result = '\n'.join(L)
