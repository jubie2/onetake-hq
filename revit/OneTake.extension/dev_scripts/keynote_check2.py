# Where does the keynote value live for the elements the ADU section tags point at?
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, IndependentTag,
                               BuiltInParameter as BIP, ElementId, FamilySymbol)
L = []
def kn(e):
    out = []
    try:
        p = e.get_Parameter(BIP.KEYNOTE_PARAM)
        out.append('inst=%r' % (p.AsString() if p else None))
    except Exception: out.append('inst=err')
    try:
        t = doc.GetElement(e.GetTypeId())
        p = t.get_Parameter(BIP.KEYNOTE_PARAM) if t else None
        out.append('type=%r (%s)' % (p.AsString() if p else None, t.Name if t else '?'))
    except Exception: out.append('type=err')
    return ' '.join(out)
for nm in ('ADU - Section 1', 'Section 3'):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    L.append('=== %s' % nm)
    for t2 in list(FEC(doc, v.Id).OfClass(IndependentTag))[:8]:
        try: txt = t2.TagText
        except Exception: txt = '?'
        ids = list(t2.GetTaggedLocalElementIds())
        for hid in ids:
            e = doc.GetElement(hid)
            L.append('  tagtext=%-4r %-16s %s' % (txt, e.Category.Name if e.Category else '?', kn(e)))
L.append('=== keynote value on the ADU roof / wall types')
seen = set()
for nm in ('ADU - Section 1',):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    for e in FEC(doc, v.Id).WhereElementIsNotElementType():
        try:
            c = e.Category.Name if e.Category else ''
            if c not in ('Walls', 'Roofs', 'Floors', 'Ceilings'): continue
            t = doc.GetElement(e.GetTypeId())
            k = '%s / %s' % (c, t.Name)
            if k in seen: continue
            seen.add(k)
            p = t.get_Parameter(BIP.KEYNOTE_PARAM)
            L.append('  %-40s keynote=%r' % (k[:40], p.AsString() if p else None))
        except Exception: pass
result = '\n'.join(L)
