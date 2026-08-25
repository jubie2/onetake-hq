# Open a list of sheets as view tabs. args {"sheets":["ADU-1",...],"focus":"ADU-1"}
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet
by = {}
for s in FEC(doc).OfClass(ViewSheet):
    by[s.SheetNumber] = s
already = set()
for uv in uidoc.GetOpenUIViews():
    v = doc.GetElement(uv.ViewId)
    sn = getattr(v, 'SheetNumber', None)
    if sn: already.add(sn)
L = []
opened = []
for sn in args['sheets']:
    s = by.get(sn)
    if s is None:
        L.append('%s NOT FOUND' % sn); continue
    if sn in already:
        L.append('%-7s already open' % sn); continue
    try:
        uidoc.RequestViewChange(s)      # opens the sheet as a tab
        opened.append(sn)
        L.append('%-7s opening  %s' % (sn, s.Name))
    except Exception as ex:
        L.append('%-7s FAIL %s' % (sn, str(ex)[:50]))
result = '\n'.join(L)
