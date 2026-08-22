from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, BuiltInCategory as BIC,
                               ElementId)
L = []
for nm in args['views']:
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    if v is None: continue
    L.append('=== %s  discipline=%s' % (nm, v.Discipline))
    try:
        fs = v.GetFilters()
        L.append('   filters: %d' % len(list(fs)))
        for fid in fs:
            f = doc.GetElement(fid)
            try: vis = v.GetFilterVisibility(fid)
            except Exception: vis = '?'
            L.append('     %s  visible=%s' % (f.Name, vis))
    except Exception as ex:
        L.append('   filters err %s' % str(ex)[:50])
    c = doc.Settings.Categories.get_Item('Lighting Fixtures')
    L.append('   Lighting Fixtures: catHidden=%s canHide=%s' % (
        v.GetCategoryHidden(c.Id), v.CanCategoryBeHidden(c.Id)))
    for sub in c.SubCategories:
        try:
            L.append('     sub %-24s hidden=%s' % (sub.Name, v.GetCategoryHidden(sub.Id)))
        except Exception: pass
result = '\n'.join(L)
