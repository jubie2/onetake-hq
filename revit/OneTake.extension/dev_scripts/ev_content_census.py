# Count model elements by category inside the NEW building bbox vs OLD Logan bbox.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, FamilyInstance,
                               BuiltInCategory as BIC)
CATS = [('MechEquip', BIC.OST_MechanicalEquipment), ('AirTerminal', BIC.OST_DuctTerminal),
        ('ElecFixture', BIC.OST_ElectricalFixtures), ('LightFixture', BIC.OST_LightingFixtures),
        ('PlumbFixture', BIC.OST_PlumbingFixtures), ('StrFraming', BIC.OST_StructuralFraming),
        ('StrFoundation', BIC.OST_StructuralFoundation), ('GenericModel', BIC.OST_GenericModel),
        ('SpecEquip', BIC.OST_SpecialityEquipment), ('Casework', BIC.OST_Casework)]
def zone(p):
    if 1110 < p.X < 1210 and 55 < p.Y < 135: return 'NEW'
    if 940 < p.X < 1030 and -160 < p.Y < -80: return 'OLD'
    return None
L = []
for name, cat in CATS:
    n = {'NEW': 0, 'OLD': 0}
    for e in FEC(doc).OfCategory(cat).WhereElementIsNotElementType():
        try:
            bb = e.get_BoundingBox(None)
            if bb is None: continue
            from Autodesk.Revit.DB import XYZ as _XYZ
            c = _XYZ((bb.Min.X + bb.Max.X) / 2, (bb.Min.Y + bb.Max.Y) / 2, 0)
            z = zone(c)
            if z: n[z] += 1
        except Exception: pass
    L.append('%-14s NEW=%d OLD=%d' % (name, n['NEW'], n['OLD']))
result = '\n'.join(L)
