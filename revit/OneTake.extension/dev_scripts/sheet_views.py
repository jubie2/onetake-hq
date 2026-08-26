# List viewports + their views on a sheet, and dump TextNotes of a named view.
# args {"sheet":"ADU-3","dumptext":"KEYNOTES SECTION"}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               View, TextNote)
L = []
sn = args.get('sheet')
if sn:
    sh = None
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber == sn: sh = s; break
    L.append('sheet %s %s' % (sn, sh.Name))
    for vpid in sh.GetAllViewports():
        vp = doc.GetElement(vpid)
        v = doc.GetElement(vp.ViewId)
        c = vp.GetBoxCenter(); o = vp.GetBoxOutline()
        L.append('  vp %-32s center (%.2f,%.2f) box %.2fx%.2f' % (
            v.Name, c.X, c.Y,
            o.MaximumPoint.X - o.MinimumPoint.X, o.MaximumPoint.Y - o.MinimumPoint.Y))
nm = args.get('dumptext')
if nm:
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    if v is None:
        L.append('view %s not found' % nm)
    else:
        L.append('--- text in %s ---' % nm)
        items = []
        for e in FEC(doc, v.Id).OfClass(TextNote):
            p = e.Coord
            items.append((-p.Y, p.X, (e.Text or '').replace('\r', ' / ')))
        items.sort()
        for y, x, txt in items:
            L.append('(%.1f,%.1f) %s' % (x, -y, txt[:110]))
result = '\n'.join(L)
