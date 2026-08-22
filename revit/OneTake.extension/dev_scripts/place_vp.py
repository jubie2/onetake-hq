# Add a view to a sheet at a point. args {"items":[{"sheet":"ADU-6","view":"...","at":[1.6,1.2]}]}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, View, Viewport,
                               XYZ as _XYZ)
L = []
t = Transaction(doc, 'OneTake: place viewports'); _prep(t); t.Start()
for it in args['items']:
    sh = None
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber == it['sheet']: sh = s; break
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == it['view']: v = x; break
    if sh is None or v is None:
        L.append('%s / %s NOT FOUND' % (it['sheet'], it['view'])); continue
    already = None
    for vp in FEC(doc, sh.Id).OfClass(Viewport):
        if vp.ViewId == v.Id: already = vp; break
    p = _XYZ(it['at'][0], it['at'][1], 0)
    if already:
        already.SetBoxCenter(p); vp = already; L.append('moved  %s / %s' % (it['sheet'], it['view'][:30]))
    elif Viewport.CanAddViewToSheet(doc, sh.Id, v.Id):
        vp = Viewport.Create(doc, sh.Id, v.Id, p); L.append('placed %s / %s' % (it['sheet'], it['view'][:30]))
    else:
        L.append('CANNOT add %s to %s' % (it['view'][:30], it['sheet'])); continue
    doc.Regenerate()
    try:
        vp.LabelOffset = _XYZ(0, 0, 0)
        ol = vp.GetBoxOutline()
        L.append('   at (%.2f,%.2f) box %.2f x %.2f' % (
            p.X, p.Y, ol.MaximumPoint.X - ol.MinimumPoint.X, ol.MaximumPoint.Y - ol.MinimumPoint.Y))
    except Exception: pass
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
