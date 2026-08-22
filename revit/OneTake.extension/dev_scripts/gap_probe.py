# Does the ADU have doors/windows/framing? Does the Drawing List include the ADU sheets?
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, BuiltInCategory as BIC,
                               ViewSchedule, ViewSheet, FamilyInstance)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
L = []
def inadu(e):
    try:
        b = e.get_BoundingBox(None)
        if b is None: return False
        cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
        return X0 <= cx <= X1 and Y0 <= cy <= Y1
    except Exception: return False
for label, bic in (('Doors', BIC.OST_Doors), ('Windows', BIC.OST_Windows),
                   ('Plumbing Fixtures', BIC.OST_PlumbingFixtures),
                   ('Mechanical Equip', BIC.OST_MechanicalEquipment),
                   ('Lighting Fixtures', BIC.OST_LightingFixtures),
                   ('Electrical Fixtures', BIC.OST_ElectricalFixtures),
                   ('Structural Framing', BIC.OST_StructuralFraming),
                   ('Structural Foundations', BIC.OST_StructuralFoundation),
                   ('Rooms', BIC.OST_Rooms)):
    els = [e for e in FEC(doc).OfCategory(bic).WhereElementIsNotElementType() if inadu(e)]
    L.append('%-24s in ADU footprint: %d' % (label, len(els)))
L.append('--- Drawing List rows')
for s in FEC(doc).OfClass(ViewSchedule):
    if s.Name != 'Drawing List': continue
    try:
        td = s.GetTableData().GetSectionData(1)
        n = td.NumberOfRows
        L.append('Drawing List has %d body rows' % n)
        adu = 0
        for r in range(n):
            txt = ''
            for c in range(td.NumberOfColumns):
                txt += (s.GetCellText(1, r, c) or '') + ' '
            if 'ADU' in txt: adu += 1
        L.append('rows mentioning ADU: %d' % adu)
    except Exception as ex:
        L.append('Drawing List read ERR %s' % str(ex)[:60])
L.append('--- schedules that exist')
for s in sorted(FEC(doc).OfClass(ViewSchedule), key=lambda z: z.Name):
    if s.IsTemplate: continue
    L.append('   %s' % s.Name)
result = '\n'.join(L)
