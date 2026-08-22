# Tag ADU doors/windows, build ADU door+window schedules, keep them out of the main ones.
# args {"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, BuiltInCategory as BIC,
                               BuiltInParameter as BIP, ViewSchedule, ViewDuplicateOption,
                               ScheduleFilter, ScheduleFilterType)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
dry = args.get('dry', True)
TAG = 'ADU'
L = []
def inadu(e):
    b = e.get_BoundingBox(None)
    if b is None: return False
    cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
    return X0 <= cx <= X1 and Y0 <= cy <= Y1

adu = []
for bic in (BIC.OST_Doors, BIC.OST_Windows):
    for e in FEC(doc).OfCategory(bic).WhereElementIsNotElementType():
        if inadu(e): adu.append(e)
L.append('ADU doors+windows to tag: %d' % len(adu))

t = None
if not dry:
    t = Transaction(doc, 'OneTake: ADU schedules'); _prep(t); t.Start()
    n = 0
    for e in adu:
        p = e.get_Parameter(BIP.ALL_MODEL_INSTANCE_COMMENTS)
        if p and not p.IsReadOnly and (p.AsString() or '') != TAG:
            p.Set(TAG); n += 1
    L.append('  tagged Comments="%s" on %d' % (TAG, n))

def comments_field(d):
    for i in range(d.GetFieldCount()):
        f = d.GetField(i)
        if f.GetName() == 'Comments': return f.FieldId
    return None

for src_name, new_name in (('DOOR SCHEDULE', 'ADU DOOR SCHEDULE'),
                           ('WINDOWS SCHEDULE', 'ADU WINDOW SCHEDULE')):
    src = None
    for s in FEC(doc).OfClass(ViewSchedule):
        if s.Name == src_name: src = s
        if s.Name == new_name:
            L.append('  %s already exists (%s)' % (new_name, s.Id)); src = src or None
    if src is None:
        L.append('  %s NOT FOUND' % src_name); continue
    exists = [s for s in FEC(doc).OfClass(ViewSchedule) if s.Name == new_name]
    L.append('  %s -> %s  (exists: %s)' % (src_name, new_name, bool(exists)))
    if dry or exists: continue
    nid = src.Duplicate(ViewDuplicateOption.Duplicate)
    nv = doc.GetElement(nid)
    nv.Name = new_name
    d = nv.Definition
    fid = comments_field(d)
    if fid is None:
        L.append('     no Comments field - cannot filter'); continue
    d.AddFilter(ScheduleFilter(fid, ScheduleFilterType.Equal, TAG))
    L.append('     created %s, filter Comments = %s' % (nv.Id, TAG))
    # keep the ADU out of the original schedule
    od = src.Definition
    ofid = comments_field(od)
    have = False
    for i in range(od.GetFilterCount()):
        f = od.GetFilter(i)
        try:
            if f.FieldId == ofid and f.GetStringValue() == TAG: have = True
        except Exception: pass
    if ofid is not None and not have:
        od.AddFilter(ScheduleFilter(ofid, ScheduleFilterType.NotEqual, TAG))
        L.append('     %s now excludes Comments = %s' % (src_name, TAG))
if t is not None:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)
