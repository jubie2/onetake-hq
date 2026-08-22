# Delete and re-create a viewport (clears stale outlines). args {"items":[{"sheet":"ADU-2","view":"ADU - North Elevation","at":[1.45,1.40]}]}
from Autodesk.Revit.DB import Viewport, ViewSheet, XYZ as _XYZ, ElementId as EId
L = []
t = Transaction(doc, 'OneTake: replace viewports'); _prep(t); t.Start()
for it in args['items']:
    for sh in FilteredElementCollector(doc).OfClass(ViewSheet):
        if sh.SheetNumber != it['sheet']: continue
        vid = None
        for vp in list(FilteredElementCollector(doc, sh.Id).OfClass(Viewport)):
            v = doc.GetElement(vp.ViewId)
            if v.Name == it['view']:
                vid = vp.ViewId
                doc.Delete(vp.Id)
                break
        doc.Regenerate()
        if vid is not None:
            nvp = Viewport.Create(doc, sh.Id, vid, _XYZ(float(it['at'][0]), float(it['at'][1]), 0))
            doc.Regenerate()
            try: nvp.LabelLineLength = 0.9
            except Exception: pass
            o = nvp.GetBoxOutline()
            L.append('%s / %-26s recreated  box %.2f x %.2f' %
                     (it['sheet'], it['view'][:26], o.MaximumPoint.X-o.MinimumPoint.X,
                      o.MaximumPoint.Y-o.MinimumPoint.Y))
        else:
            L.append('%s / %s not found' % (it['sheet'], it['view']))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
