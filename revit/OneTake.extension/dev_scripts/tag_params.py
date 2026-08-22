from Autodesk.Revit.DB import FilteredElementCollector as FEC, View, IndependentTag, StorageType
L = []
def dump(t2, label):
    L.append('--- %s  (tag %s)' % (label, t2.Id))
    try: L.append('    TagText=%r' % t2.TagText)
    except Exception: pass
    for p in t2.Parameters:
        try:
            if p.StorageType == StorageType.String:
                v = p.AsString()
            elif p.StorageType == StorageType.Integer:
                v = p.AsInteger()
            elif p.StorageType == StorageType.Double:
                v = p.AsDouble()
            else:
                v = str(p.AsValueString())
            if v in (None, '', 0): continue
            L.append('    %-32s = %r  %s' % (p.Definition.Name, v,
                                             'READONLY' if p.IsReadOnly else 'writable'))
        except Exception: pass
for nm, lim in (('Section 3', 2), ('ADU - Section 1', 2)):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    n = 0
    for t2 in FEC(doc, v.Id).OfClass(IndependentTag):
        if n >= lim: break
        dump(t2, nm); n += 1
result = '\n'.join(L)
