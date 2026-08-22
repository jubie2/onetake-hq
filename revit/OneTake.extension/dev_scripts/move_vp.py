# Move specific viewports. args {"items":[{"sheet":"ADU-1","view":"Floor Plan Notes","at":[1.6,0.36]}]}
from Autodesk.Revit.DB import Viewport, ViewSheet, XYZ as _XYZ
L = []
t = Transaction(doc, 'OneTake: move viewports'); _prep(t); t.Start()
for it in args['items']:
    done = False
    for sh in FilteredElementCollector(doc).OfClass(ViewSheet):
        if sh.SheetNumber != it['sheet']: continue
        for vp in FilteredElementCollector(doc, sh.Id).OfClass(Viewport):
            v = doc.GetElement(vp.ViewId)
            if v.Name != it['view']: continue
            vp.SetBoxCenter(_XYZ(float(it['at'][0]), float(it['at'][1]), 0))
            o = vp.GetBoxOutline()
            L.append('%s / %-26s -> (%.2f, %.2f)  size %.2f x %.2f' %
                     (it['sheet'], v.Name[:26], it['at'][0], it['at'][1],
                      o.MaximumPoint.X-o.MinimumPoint.X, o.MaximumPoint.Y-o.MinimumPoint.Y))
            done = True
    if not done: L.append('%s / %s NOT FOUND' % (it['sheet'], it['view']))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
