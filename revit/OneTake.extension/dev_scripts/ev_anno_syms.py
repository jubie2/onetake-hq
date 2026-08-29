# All generic-annotation + detail-item symbols (the office draws mech devices as 2D symbols).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, FamilySymbol,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
L = []
for name, cat in (('GenericAnno', BIC.OST_GenericAnnotation),
                  ('DetailItem', BIC.OST_DetailComponents)):
    rows = set()
    for s in FEC(doc).OfClass(FamilySymbol).OfCategory(cat):
        rows.add('%s :: %s  [id %s]' % (
            s.Family.Name, s.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '',
            s.Id.Value))
    L.append('--- %s (%d) ---' % (name, len(rows)))
    for r in sorted(rows): L.append('  ' + r)
result = '\n'.join(L)
