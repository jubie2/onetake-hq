# What do the keynote tags in the ADU sections actually show?
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, IndependentTag,
                               BuiltInCategory as BIC, BuiltInParameter as BIP, ElementId)
L = []
for nm in ('ADU - Section 1', 'ADU - Section 2', 'ADU - Section 3', 'ADU - Section 4',
           'Section 1', 'Section 3'):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    if v is None: continue
    tags = list(FEC(doc, v.Id).OfClass(IndependentTag))
    L.append('%-18s %d tag(s)' % (nm, len(tags)))
    for t2 in tags:
        try:
            txt = t2.TagText
        except Exception:
            txt = '?'
        try:
            tt = doc.GetElement(t2.GetTypeId())
            tn = tt.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString()
            fam = tt.Family.Name
        except Exception:
            tn = fam = '?'
        host = ''
        try:
            for hid in t2.GetTaggedLocalElementIds():
                e = doc.GetElement(hid)
                kp = e.get_Parameter(BIP.KEYNOTE_PARAM) if e else None
                if kp is None and e is not None:
                    kp = e.Symbol.get_Parameter(BIP.KEYNOTE_PARAM) if hasattr(e, 'Symbol') else None
                host = '%s %s keynote=%r' % (e.Category.Name if e and e.Category else '?',
                                             hid, kp.AsString() if kp else None)
        except Exception as ex:
            host = 'host err %s' % str(ex)[:30]
        L.append('    text=%r  type=%s : %s  <- %s' % (txt, fam, tn, host))
result = '\n'.join(L)
