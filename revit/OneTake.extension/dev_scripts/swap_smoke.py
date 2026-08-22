# Swap the two 'Smoke' annotation types on the ADU instances. args {"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, BuiltInCategory as BIC,
                               BuiltInParameter as BIP, FamilySymbol, View, ElementId)
A = 'Smoke%20Detector[1]'; B = 'CARBONMONOXIDE'
syms = {}
for s in FEC(doc).OfClass(FamilySymbol):
    try:
        if s.Family.Name != 'Smoke': continue
        syms[s.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString()] = s
    except Exception: pass
L = ['Smoke family types: %s' % sorted(syms.keys())]
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == 'ADU - Electrical Plan': v = x; break
targets = []
for e in FEC(doc, v.Id).OfCategory(BIC.OST_GenericAnnotation):
    try:
        if e.Symbol.Family.Name != 'Smoke': continue
        tn = e.Symbol.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString()
        p = e.Location.Point
        targets.append((e, tn, p))
        L.append('  %s  %s at (%.1f, %.1f)' % (e.Id, tn, p.X, p.Y))
    except Exception: pass
if not args.get('dry', True):
    t = Transaction(doc, 'OneTake: swap smoke/CO'); _prep(t); t.Start()
    n = 0
    for e, tn, p in targets:
        other = B if tn == A else A
        if other in syms:
            if not syms[other].IsActive: syms[other].Activate()
            e.Symbol = syms[other]; n += 1
    doc.Regenerate(); t.Commit()
    L.append('swapped %d' % n)
result = '\n'.join(L)
