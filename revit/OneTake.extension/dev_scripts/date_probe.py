from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet, BuiltInCategory as BIC, StorageType
L = []
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber != 'ADU-1': continue
    for e in FEC(doc, s.Id).OfCategory(BIC.OST_TitleBlocks):
        for grp in (e, doc.GetElement(e.GetTypeId())):
            tag = 'inst' if grp is e else 'type'
            for p in grp.Parameters:
                try:
                    if p.StorageType != StorageType.String: continue
                    v = p.AsString() or ''
                    if '08.16' in v or 'Date' in p.Definition.Name:
                        L.append('%s %-28s = %r  ro=%s' % (tag, p.Definition.Name, v, p.IsReadOnly))
                except Exception: pass
result = '\n'.join(L)
