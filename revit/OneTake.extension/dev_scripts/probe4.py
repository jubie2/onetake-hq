from Autodesk.Revit.DB import (FilteredElementCollector as FEC, BuiltInCategory as BIC,
                               BuiltInParameter as BIP, View, FamilyInstance, FamilySymbol,
                               Wall, Level)
L = []
L.append('=== generic annotations used in 1st Floor Electrical Plan')
for v in FEC(doc).OfClass(View):
    if v.IsTemplate or v.Name != '1st Floor Electrical Plan': continue
    cnt = {}
    for e in FEC(doc, v.Id).OfCategory(BIC.OST_GenericAnnotation):
        try:
            k = '%s : %s' % (e.Symbol.Family.Name, e.Symbol.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString())
        except Exception: k = '?'
        cnt[k] = cnt.get(k, 0) + 1
    for k in sorted(cnt, key=lambda z: -cnt[z]): L.append('   %-52s x%d' % (k[:52], cnt[k]))
    L.append('   -- specialty equipment in that view')
    for e in FEC(doc, v.Id).OfCategory(BIC.OST_SpecialityEquipment):
        try: L.append('      %s : %s' % (e.Symbol.Family.Name, e.Symbol.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString()))
        except Exception: pass
L.append('=== how existing electrical fixtures are placed (first 6)')
n = 0
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    if n >= 6: break
    try:
        h = e.Host
        hn = ('%s %s' % (h.Category.Name, h.Id)) if h else 'none'
        lv = doc.GetElement(e.LevelId).Name if e.LevelId and e.LevelId.IntegerValue > 0 else '?'
        loc = e.Location.Point if hasattr(e.Location, 'Point') else None
        off = e.get_Parameter(BIP.INSTANCE_ELEVATION_PARAM)
        L.append('   %-22s host %-18s lvl %-16s at (%.1f,%.1f,%.1f) elev %s' % (
            e.Symbol.Family.Name[:22], hn, lv,
            loc.X if loc else 0, loc.Y if loc else 0, loc.Z if loc else 0,
            off.AsDouble() if off and off.HasValue else '-'))
        n += 1
    except Exception as ex:
        L.append('   err %s' % str(ex)[:50]); n += 1
L.append('=== symbol placement flavour')
for fam in ('Outlet-Duplex', 'Switch-Single', 'Outlet-GFI', 'Antique_Doorwall_lamp_10251',
            'Water Heater', 'Supply Register-Floor 2 way'):
    for s in FEC(doc).OfClass(FamilySymbol):
        try:
            if s.Family.Name != fam: continue
            f = s.Family
            L.append('   %-30s hostable=%s placement=%s cat=%s' % (
                fam, f.IsInPlace is False, str(f.FamilyPlacementType), s.Category.Name))
            break
        except Exception: pass
L.append('=== levels')
for lv in FEC(doc).OfClass(Level):
    L.append('   %-20s elev %.2f' % (lv.Name, lv.Elevation))
result = '\n'.join(L)
