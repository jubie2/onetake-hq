# Gather everything needed to rebuild the deleted north wall + its door/windows:
# sibling wall constraints, the family symbols, and a surviving window's sill setup.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, Wall,
                               WallType, FamilySymbol, Level,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
L = []
sib = doc.GetElement(ElementId(2189094))          # surviving 1st-floor exterior wall
L.append('sibling wall %s type "%s"' % (sib.Id.Value, sib.Name))
for bip, nm in ((BIP.WALL_BASE_CONSTRAINT, 'base level'),
                (BIP.WALL_BASE_OFFSET, 'base offset'),
                (BIP.WALL_HEIGHT_TYPE, 'top constraint'),
                (BIP.WALL_USER_HEIGHT_PARAM, 'unconnected height'),
                (BIP.WALL_TOP_OFFSET, 'top offset'),
                (BIP.WALL_KEY_REF_PARAM, 'location line'),
                (BIP.PHASE_CREATED, 'phase')):
    p = sib.get_Parameter(bip)
    if p is None: L.append('   %-18s -' % nm); continue
    v = p.AsValueString()
    if p.StorageType.ToString() == 'ElementId':
        e2 = doc.GetElement(p.AsElementId())
        v = '%s (%s)' % (v, e2.Name if e2 else p.AsElementId().Value)
    L.append('   %-18s %s' % (nm, v))
bb = sib.get_BoundingBox(None)
L.append('   sibling z %.2f .. %.2f' % (bb.Min.Z, bb.Max.Z))
L.append('--- wall types ---')
for wt in FEC(doc).OfClass(WallType):
    n = wt.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or ''
    if 'NEW 2' in n or n.strip() == 'Generic - 6"':
        L.append('   %-9s %s' % (wt.Id.Value, n))
L.append('--- door / window symbols needed ---')
for cat in (BIC.OST_Doors, BIC.OST_Windows):
    for s in FEC(doc).OfClass(FamilySymbol).OfCategory(cat):
        fam = s.Family.Name
        if any(k in fam for k in ('Sliding-2', 'Gliding')):
            L.append('   %-9s %-26s :: %s' % (
                s.Id.Value, fam[:26],
                s.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString()))
L.append('--- a surviving window, for sill/params reference ---')
w2 = doc.GetElement(ElementId(2228035))           # Gliding 2x3 that survived
if w2 is not None:
    p2 = w2.Location.Point
    L.append('   %s at (%.2f,%.2f,%.2f) sym "%s" host %s' % (
        w2.Id.Value, p2.X, p2.Y, p2.Z, w2.Symbol.Family.Name[:22], w2.Host.Id.Value))
    for bip, nm in ((BIP.INSTANCE_SILL_HEIGHT_PARAM, 'sill height'),
                    (BIP.ALL_MODEL_MARK, 'mark'),
                    (BIP.ALL_MODEL_INSTANCE_COMMENTS, 'comments'),
                    (BIP.PHASE_CREATED, 'phase')):
        p3 = w2.get_Parameter(bip)
        L.append('     %-12s %s' % (nm, p3.AsValueString() if p3 else '-'))
L.append('--- levels ---')
for lv in FEC(doc).OfClass(Level):
    L.append('   %-9s %-22s %.2f' % (lv.Id.Value, lv.Name, lv.Elevation))
result = '\n'.join(L)
