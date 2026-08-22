from Autodesk.Revit.DB import (FilteredElementCollector as FEC, FamilySymbol, View, ViewSection,
                               BuiltInCategory as BIC, BuiltInParameter as BIP, ViewFamilyType,
                               ViewFamily)
L = ['=== tag families available']
for bic, nm in ((BIC.OST_DoorTags, 'Door Tags'), (BIC.OST_WindowTags, 'Window Tags')):
    for s in FEC(doc).OfClass(FamilySymbol):
        try:
            if s.Category is None or s.Category.Id.IntegerValue != int(bic): continue
            L.append('  [%s] %s : %s' % (nm, s.Family.Name[:34],
                                         s.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString()))
        except Exception: pass
L.append('=== ADU + main sections: origin / direction')
for v in FEC(doc).OfClass(ViewSection):
    try:
        if v.IsTemplate: continue
        if not (v.Name.startswith('ADU - Section') or v.Name in ('Section 1','Section 2','Section 3','Section 4')): continue
        o = v.Origin; d = v.ViewDirection; r = v.RightDirection
        L.append('  %-20s origin (%.1f,%.1f,%.1f) dir (%.2f,%.2f,%.2f) right (%.2f,%.2f,%.2f) typeId %s' % (
            v.Name[:20], o.X, o.Y, o.Z, d.X, d.Y, d.Z, r.X, r.Y, r.Z, v.GetTypeId()))
    except Exception: pass
L.append('=== section view family types')
for t in FEC(doc).OfClass(ViewFamilyType):
    try:
        if str(t.ViewFamily) != 'Section': continue
        L.append('  %s : %s' % (t.Id, t.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString()))
    except Exception: pass
result = '\n'.join(L)
