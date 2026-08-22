from Autodesk.Revit.DB import (KeynoteTable, FilteredElementCollector as FEC, KeyBasedTreeEntries,
                               BuiltInParameter as BIP, IndependentTag, View, ExternalFileReference)
L = []
try:
    kt = KeynoteTable.GetKeynoteTable(doc)
    L.append('keynote table element: %s' % kt.Id)
    try:
        r = kt.GetExternalFileReference()
        L.append('  file loaded: %s' % (r.GetAbsolutePath() if r else None))
        try: L.append('  path type: %s  valid: %s' % (r.PathType, kt.IsValidObject))
        except Exception: pass
    except Exception as ex:
        L.append('  no external file reference (%s)' % str(ex)[:60])
    try:
        ents = kt.GetKeyBasedTreeEntries()
        L.append('  entries: %d' % ents.Size)
        n = 0
        for e in ents:
            if n >= 20: break
            L.append('    key=%r  parent=%r  text=%r' % (e.Key, e.ParentKey, e.KeynoteText[:40]))
            n += 1
    except Exception as ex:
        L.append('  cannot read entries: %s' % str(ex)[:70])
except Exception as ex:
    L.append('KeynoteTable error: %s' % str(ex)[:80])
L.append('=== a working tag from the main set, in detail')
for v in FEC(doc).OfClass(View):
    if v.IsTemplate or v.Name != 'Section 3': continue
    for t2 in list(FEC(doc, v.Id).OfClass(IndependentTag))[:4]:
        try:
            L.append('  tagtext=%r  hasLeader=%s' % (t2.TagText, t2.HasLeader))
            for hid in t2.GetTaggedLocalElementIds():
                e = doc.GetElement(hid)
                tt = doc.GetElement(e.GetTypeId())
                p = tt.get_Parameter(BIP.KEYNOTE_PARAM) if tt else None
                pi = e.get_Parameter(BIP.KEYNOTE_PARAM)
                L.append('      host %s  typeKeynote=%r  instKeynote=%r' % (
                    e.Category.Name if e.Category else '?',
                    p.AsString() if p else None, pi.AsString() if pi else None))
        except Exception as ex:
            L.append('  err %s' % str(ex)[:50])
result = '\n'.join(L)
