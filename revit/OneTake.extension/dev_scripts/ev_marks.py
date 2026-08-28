# Renumber ADU doors/windows per approved convention; set Comments=ADU;
# filter both A102 schedules to Comments=ADU.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSchedule,
                               ElementId, BuiltInParameter as BIP,
                               ScheduleFilter, ScheduleFilterType, ScheduleFieldType)
DOORS = {2197513: '101', 2189633: '102', 2189543: '103', 2191960: '104',
         2192776: '105', 2196306: '106', 2196038: '107', 2228224: '108',
         2228133: '109', 2193676: '110', 2194343: '111', 2194315: '112',
         2193646: '113', 2195558: '114',
         2205462: '201', 2207390: '202', 2210839: '203', 2241317: '204',
         2209836: '205', 2209389: '206', 2205800: '207', 2204703: '208',
         2211038: '209', 2206764: '210'}
WINS = {2218270: '01', 2228264: '02', 2228011: '03', 2227911: '04',
        2239336: '05', 2227947: '06', 2228035: '07',
        2217448: '21', 2227413: '22', 2227489: '23', 2227685: '24',
        2227546: '25', 2227712: '26', 2217328: '27', 2228563: '28',
        2227776: '29', 2217381: '30', 2217295: '31', 2239155: '32',
        2217254: '33'}
L = []
t = Transaction(doc, 'OneTake: ADU marks'); _prep(t); t.Start()
n = 0
for table in [DOORS, WINS]:
    for eid, mk in table.items():
        e = doc.GetElement(ElementId(eid))
        if e is None: L.append('%s missing' % eid); continue
        p = e.get_Parameter(BIP.ALL_MODEL_MARK)
        if p and not p.IsReadOnly: p.Set(mk)
        c = e.get_Parameter(BIP.ALL_MODEL_INSTANCE_COMMENTS)
        if c and not c.IsReadOnly: c.Set('ADU')
        n += 1
L.append('%d marks set' % n)
for vs in FEC(doc).OfClass(ViewSchedule):
    if vs.Name not in ('DOOR SCHEDULE', 'WINDOWS SCHEDULE'): continue
    sd = vs.Definition
    fid = None
    for i in range(sd.GetFieldCount()):
        f = sd.GetField(i)
        if f.GetName() in ('Comments',): fid = f.FieldId
    if fid is None:
        for sf in sd.GetSchedulableFields():
            try:
                if sf.GetName(doc) == 'Comments':
                    fld = sd.AddField(sf)
                    fld.IsHidden = True
                    fid = fld.FieldId
                    break
            except Exception: pass
    if fid is None:
        L.append('%s: no Comments field' % vs.Name); continue
    have = False
    for i in range(sd.GetFilterCount()):
        if sd.GetFilter(i).FieldId == fid: have = True
    if not have:
        sd.AddFilter(ScheduleFilter(fid, ScheduleFilterType.Equal, 'ADU'))
        L.append('%s: ADU filter added' % vs.Name)
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
