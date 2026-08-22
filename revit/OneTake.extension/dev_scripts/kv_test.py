from Autodesk.Revit.DB import FilteredElementCollector as FEC, View, IndependentTag
L = []
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == 'ADU - Section 1': v = x; break
tags = list(FEC(doc, v.Id).OfClass(IndependentTag))
L.append('tags in view: %d' % len(tags))
if tags:
    t2 = tags[0]
    for pn in ('Key Value', 'Key Source'):
        p = t2.LookupParameter(pn)
        L.append('  %-11s exists=%s readonly=%s value=%r' % (
            pn, p is not None, p.IsReadOnly if p else None, p.AsString() if p else None))
    p = t2.LookupParameter('Key Value')
    if p is not None and not p.IsReadOnly:
        t = Transaction(doc, 'OneTake: key value test'); _prep(t); t.Start()
        try:
            p.Set('9')
            doc.Regenerate()
            L.append('  after Set("9"): TagText=%r  KeyValue=%r' % (t2.TagText, p.AsString()))
        except Exception as ex:
            L.append('  Set failed: %s' % str(ex)[:70])
        t.Commit()
result = '\n'.join(L)
