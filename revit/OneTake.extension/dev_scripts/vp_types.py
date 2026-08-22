# List viewport types and what the existing sheets use. args {"sheet":"A101"}
from Autodesk.Revit.DB import Viewport, ViewSheet, ElementType, BuiltInParameter, FilteredElementCollector as FEC
L = ['VIEWPORT TYPES:']
for t in FEC(doc).OfClass(ElementType):
    try:
        if t.FamilyName != 'Viewport': continue
        L.append('   %-9s %s' % (t.Id.Value, t.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()))
    except Exception: pass
L.append('USED ON SHEETS:')
use = {}
for vp in FEC(doc).OfClass(Viewport):
    sh = doc.GetElement(vp.SheetId)
    if sh is None: continue
    tid = vp.GetTypeId().Value
    use.setdefault((sh.SheetNumber, tid), 0)
    use[(sh.SheetNumber, tid)] += 1
for (sn, tid), n in sorted(use.items())[:26]:
    tp = doc.GetElement(ElementId(long(tid)))
    nm = tp.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString() if tp else '?'
    L.append('   %-8s type %-9s %-28s x%d' % (sn, tid, nm, n))
result = '\n'.join(L)
