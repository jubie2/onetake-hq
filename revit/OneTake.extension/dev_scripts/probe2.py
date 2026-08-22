from Autodesk.Revit.DB import (FilteredElementCollector as FEC, BuiltInCategory as BIC,
                               BuiltInParameter as BIP, ViewSchedule, ViewSheet, View,
                               FamilyInstance, FamilySymbol)
L = []
L.append('=== schedule filter values')
for nm in ('DOOR SCHEDULE', 'WINDOWS SCHEDULE'):
    for s in FEC(doc).OfClass(ViewSchedule):
        if s.Name != nm: continue
        d = s.Definition
        for i in range(d.GetFilterCount()):
            f = d.GetFilter(i)
            try: v = f.GetStringValue()
            except Exception:
                try: v = f.GetDoubleValue()
                except Exception: v = '?'
            L.append('  %s: field %s %s value %r' % (nm, d.GetField(f.FieldId).GetName(), f.FilterType, v))
L.append('=== "Appears In Sheet List" per sheet')
on = []; off = []
for s in sorted(FEC(doc).OfClass(ViewSheet), key=lambda z: z.SheetNumber):
    p = s.get_Parameter(BIP.SHEET_SCHEDULED)
    (on if (p and p.AsInteger() == 1) else off).append(s.SheetNumber)
L.append('  ON  (%d): %s' % (len(on), ', '.join(on)))
L.append('  OFF (%d): %s' % (len(off), ', '.join(off)))
L.append('=== existing Comments on ADU doors/windows')
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
vals = {}
for bic in (BIC.OST_Doors, BIC.OST_Windows):
    for e in FEC(doc).OfCategory(bic).WhereElementIsNotElementType():
        b = e.get_BoundingBox(None)
        if b is None: continue
        cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
        tag = 'ADU' if (X0 <= cx <= X1 and Y0 <= cy <= Y1) else 'main'
        p = e.get_Parameter(BIP.ALL_MODEL_INSTANCE_COMMENTS)
        v = (p.AsString() or '') if p else '(no param)'
        vals['%s:%r' % (tag, v)] = vals.get('%s:%r' % (tag, v), 0) + 1
for k in sorted(vals): L.append('  %-40s %d' % (k, vals[k]))
L.append('=== device families in the model (types actually placed)')
for label, bic in (('Lighting Fixtures', BIC.OST_LightingFixtures),
                   ('Lighting Devices', BIC.OST_LightingDevices),
                   ('Electrical Fixtures', BIC.OST_ElectricalFixtures),
                   ('Electrical Equipment', BIC.OST_ElectricalEquipment),
                   ('Fire Alarm Devices', BIC.OST_FireAlarmDevices),
                   ('Communication Devices', BIC.OST_CommunicationDevices),
                   ('Mechanical Equipment', BIC.OST_MechanicalEquipment),
                   ('Air Terminals', BIC.OST_DuctTerminal),
                   ('Plumbing Fixtures', BIC.OST_PlumbingFixtures),
                   ('Generic Models', BIC.OST_GenericModel)):
    cnt = {}
    for e in FEC(doc).OfCategory(bic).WhereElementIsNotElementType():
        try:
            k = '%s : %s' % (e.Symbol.Family.Name, e.Symbol.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString())
        except Exception: continue
        cnt[k] = cnt.get(k, 0) + 1
    if not cnt: continue
    L.append('  -- %s' % label)
    for k in sorted(cnt, key=lambda z: -cnt[z])[:14]:
        L.append('     %-58s x%d' % (k[:58], cnt[k]))
result = '\n'.join(L)
