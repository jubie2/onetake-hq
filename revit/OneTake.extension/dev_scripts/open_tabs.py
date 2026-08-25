# What view windows (tabs) are open, and what documents are loaded.
L = []
try:
    docs = []
    for d in uiapp.Application.Documents:
        try:
            if d.IsLinked: continue
            docs.append('%s%s' % (d.Title, '  [ACTIVE]' if d.Title == doc.Title else ''))
        except Exception: pass
    L.append('documents open: %d' % len(docs))
    for s in docs: L.append('   %s' % s)
except Exception as ex:
    L.append('doc list err %s' % str(ex)[:60])
try:
    uiviews = list(uidoc.GetOpenUIViews())
    L.append('view tabs open in this document: %d' % len(uiviews))
    for uv in uiviews:
        v = doc.GetElement(uv.ViewId)
        sn = getattr(v, 'SheetNumber', None)
        L.append('   %-10s %s' % (sn or str(v.ViewType), v.Name))
except Exception as ex:
    L.append('uiview err %s' % str(ex)[:60])
try:
    L.append('active view: %s' % uidoc.ActiveView.Name)
except Exception: pass
result = '\n'.join(L)
