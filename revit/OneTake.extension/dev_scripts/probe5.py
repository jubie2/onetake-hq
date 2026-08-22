from Autodesk.Revit.DB import (FilteredElementCollector as FEC, FamilySymbol,
                               BuiltInParameter as BIP, BuiltInCategory as BIC)
L = ['=== ALL Generic Annotation symbols']
for s in FEC(doc).OfClass(FamilySymbol):
    try:
        if s.Category is None or s.Category.Id.IntegerValue != int(BIC.OST_GenericAnnotation): continue
        L.append('   %-40s : %s' % (s.Family.Name[:40], s.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString()))
    except Exception: pass
L.append('=== symbols whose family name hints at devices')
KEY = ('smoke', 'carbon', 'monoxide', 'exhaust', 'fan', 'light', 'lamp', 'detector',
       'alarm', 'ceiling', 'recess', 'furnace', 'heater', 'register', 'grille', 'vent')
for s in FEC(doc).OfClass(FamilySymbol):
    try:
        f = s.Family.Name; n = s.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or ''
        low = (f + ' ' + n).lower()
        if any(k in low for k in KEY):
            L.append('   [%s] %s : %s' % (s.Category.Name if s.Category else '?', f[:38], n[:28]))
    except Exception: pass
result = '\n'.join(L)
