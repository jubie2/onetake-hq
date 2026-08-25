# Close every view tab that is not an ADU sheet, then leave ADU-2 in front.
# args {"keep_prefix":"ADU-","focus":"ADU-2"}
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet
pref = args.get('keep_prefix', 'ADU-')
L = []
active_id = uidoc.ActiveView.Id
closed = []; kept = []
for uv in list(uidoc.GetOpenUIViews()):
    v = doc.GetElement(uv.ViewId)
    sn = getattr(v, 'SheetNumber', None) or ''
    label = '%s %s' % (sn or str(v.ViewType), v.Name)
    if sn.startswith(pref):
        kept.append(label); continue
    if uv.ViewId == active_id:
        L.append('SKIPPED (it is the active view): %s' % label); kept.append(label); continue
    try:
        uv.Close(); closed.append(label)
    except Exception as ex:
        L.append('could not close %s: %s' % (label, str(ex)[:45]))
L.append('closed %d: %s' % (len(closed), '; '.join(closed) or '-'))
L.append('kept %d: %s' % (len(kept), '; '.join(kept)))
tgt = args.get('focus')
if tgt:
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber == tgt:
            uidoc.RequestViewChange(s); L.append('focus requested -> %s' % tgt); break
result = '\n'.join(L)
