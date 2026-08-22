# Hide clutter categories in views + nudge viewport titles.
# args {"views":[..],"hide_cats":["Sections","Elevations"],"labels":[["ADU-1","ADU - 2nd Floor Plan",0,0.22]]}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewSheet,
                               BuiltInCategory as BIC, XYZ as _XYZ)
L = []
t = Transaction(doc, 'OneTake: tidy sheets'); _prep(t); t.Start()
cats = doc.Settings.Categories
for nm in args.get('views', []):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    if v is None: L.append('%s not found' % nm); continue
    for cn in args.get('hide_cats', []):
        try:
            c = cats.get_Item(cn)
            if c is None: L.append('  cat %s missing' % cn); continue
            if v.CanCategoryBeHidden(c.Id):
                v.SetCategoryHidden(c.Id, True)
                L.append('%-24s hid category %s' % (nm[:24], cn))
            else:
                L.append('%-24s cannot hide %s' % (nm[:24], cn))
        except Exception as ex:
            L.append('%-24s %s ERR %s' % (nm[:24], cn, str(ex)[:45]))
for sn, vn, dx, dy in args.get('labels', []):
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber != sn: continue
        for vpid in s.GetAllViewports():
            vp = doc.GetElement(vpid)
            if doc.GetElement(vp.ViewId).Name != vn: continue
            vp.LabelOffset = _XYZ(float(dx), float(dy), 0)
            L.append('%s / %s label offset -> (%.2f, %.2f)' % (sn, vn[:24], dx, dy))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
