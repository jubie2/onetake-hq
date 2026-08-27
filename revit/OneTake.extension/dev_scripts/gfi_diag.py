# Diagnose selectability of GFI outlets: design option, host, workset.
from Autodesk.Revit.DB import ElementId, BuiltInParameter as BIP
IDS = [2194327, 2194352, 2196439, 2196440, 2196441, 2196442, 2196443, 2186763]
L = []
for i in IDS:
    e = doc.GetElement(ElementId(i))
    if e is None: L.append('%s GONE' % i); continue
    do = e.DesignOption
    host = ''
    try: host = '%s(%s)' % (e.Host.GetType().Name, e.Host.Id.Value)
    except Exception: host = 'none'
    ws = ''
    try: ws = str(e.WorksetId.IntegerValue)
    except Exception: pass
    lvl = e.get_Parameter(BIP.FAMILY_LEVEL_PARAM)
    lvln = doc.GetElement(lvl.AsElementId()).Name if lvl and lvl.AsElementId() != ElementId.InvalidElementId else '?'
    L.append('id %s opt=%s host=%s ws=%s lvl=%s pinned=%s' % (
        i, do.Name if do else '-', host, ws, lvln, e.Pinned))
result = '\n'.join(L)
