from Autodesk.Revit.DB import FilteredElementCollector as FEC, View, ElementId
L = []
for nm in args['views']:
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    if v is None: continue
    tid = v.ViewTemplateId
    tpl = doc.GetElement(tid).Name if tid and tid.IntegerValue > 0 else '(none)'
    L.append('%-24s template=%-22s detail=%s displayStyle=%s' % (
        nm, tpl, v.DetailLevel, v.DisplayStyle))
if args.get('set_detail'):
    t = Transaction(doc, 'OneTake: detail level'); _prep(t); t.Start()
    from Autodesk.Revit.DB import ViewDetailLevel
    for nm in args['views']:
        for x in FEC(doc).OfClass(View):
            if x.IsTemplate or x.Name != nm: continue
            try:
                x.DetailLevel = ViewDetailLevel.Fine
                L.append('  %s -> Fine' % nm)
            except Exception as ex:
                L.append('  %s detail fail %s' % (nm, str(ex)[:50]))
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)
