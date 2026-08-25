# Dump text notes on Keeler A01 (sheet + its drafting views).
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet, TextNote, Viewport
L = []
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A01': sh = s; break
def dump(viewid, tag):
    for t2 in FEC(doc, viewid).OfClass(TextNote):
        txt = (t2.Text or '').strip()
        if txt:
            L.append('[%s] %s' % (tag, txt.replace('\r', ' / ').replace('\n', ' / ')[:220]))
dump(sh.Id, 'sheet')
for vpid in sh.GetAllViewports():
    vp = doc.GetElement(vpid); v = doc.GetElement(vp.ViewId)
    dump(v.Id, v.Name[:14])
result = '\n'.join(L)
