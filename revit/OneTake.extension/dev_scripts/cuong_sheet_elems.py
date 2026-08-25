# What sits DIRECTLY on the paper sheets (raster images, text) in both models.
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet
path = r'C:\Users\francis nguyen\Dropbox\2024\RESIDENTIAL\Cuong House\Cuong House ADU REV-2.rvt'
app = uiapp.Application
src = None
for d in app.Documents:
    try:
        if not d.IsLinked and d.PathName == path: src = d; break
    except Exception: pass
L = []
def dump(dc, tag, nums):
    for s in sorted(FEC(dc).OfClass(ViewSheet), key=lambda z: z.SheetNumber):
        if s.SheetNumber not in nums: continue
        cnt = {}
        for e in FEC(dc, s.Id):
            k = e.Category.Name if e.Category else type(e).__name__
            cnt[k] = cnt.get(k, 0) + 1
        L.append('%s %-5s %-26s | %s' % (tag, s.SheetNumber, s.Name[:26],
                 ', '.join('%s:%d' % (k, cnt[k]) for k in sorted(cnt))))
dump(src, 'CUONG ', ('A04', 'A06', 'A07', 'SD0'))
dump(doc, 'KEELER', ('A04', 'A05', 'A06', 'SD0', 'SD3', 'AD1'))
result = '\n'.join(L)
