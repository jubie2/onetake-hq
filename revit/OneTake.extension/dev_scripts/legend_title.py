# Shorten legend viewport title lines + report crop visibility. args {"items":[["ADU-2","ELEVATION KEYNOTES",0.45]]}
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet, View
L = []
t = Transaction(doc, 'OneTake: legend titles'); _prep(t); t.Start()
for sn, vn, ln in args.get('items', []):
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber != sn: continue
        for vpid in s.GetAllViewports():
            vp = doc.GetElement(vpid); v = doc.GetElement(vp.ViewId)
            if v.Name != vn: continue
            try:
                vp.LabelLineLength = float(ln)
                ol = vp.GetBoxOutline()
                L.append('%s / %s  line -> %.2f  box %.2f' % (
                    sn, vn[:22], float(ln), ol.MaximumPoint.X - ol.MinimumPoint.X))
            except Exception as ex:
                L.append('%s / %s ERR %s' % (sn, vn[:22], str(ex)[:50]))
doc.Regenerate(); t.Commit()
for nm in args.get('check', []):
    for v in FEC(doc).OfClass(View):
        if not v.IsTemplate and v.Name == nm:
            L.append('%s cropVisible=%s annoCropVisible=%s' % (
                nm, v.CropBoxVisible, getattr(v, 'AreAnnotationCategoriesHidden', 'n/a')))
result = '\n'.join(L)
