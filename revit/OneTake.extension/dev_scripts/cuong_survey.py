# Open the Cuong model in the background and list what sits on the paper sheets.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               ScheduleSheetInstance, View)
path = r'C:\Users\francis nguyen\Dropbox\2024\RESIDENTIAL\Cuong House\Cuong House ADU REV-2.rvt'
app = uiapp.Application
src = None
for d in app.Documents:
    try:
        if not d.IsLinked and d.PathName == path: src = d; break
    except Exception: pass
opened = False
if src is None:
    src = app.OpenDocumentFile(path)
    opened = True
WANT = ('A03', 'A04', 'A05', 'A06', 'A07', 'SD0', 'SD1', 'SD2', 'A01', 'A02')
L = ['opened=%s title=%s' % (opened, src.Title)]
for s in sorted(FEC(src).OfClass(ViewSheet), key=lambda z: z.SheetNumber):
    if s.SheetNumber not in WANT: continue
    items = []
    for vpid in s.GetAllViewports():
        vp = src.GetElement(vpid); v = src.GetElement(vp.ViewId)
        items.append('%s[%s|id %s]' % (v.Name[:36], str(v.ViewType), v.Id))
    for si in FEC(src, s.Id).OfClass(ScheduleSheetInstance):
        try:
            sc = src.GetElement(si.ScheduleId)
            items.append('%s[Schedule|id %s]' % (sc.Name[:36], sc.Id))
        except Exception: pass
    L.append('%-5s %-28s | %s' % (s.SheetNumber, s.Name[:28], '; '.join(items)))
result = '\n'.join(L)
