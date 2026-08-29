# Inventory equipment already modelled in the new ADU (no Rooms collector).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, BuiltInCategory as BIC,
                               XYZ as _XYZ)
CATS = [('PLUMB', BIC.OST_PlumbingFixtures), ('SPEC', BIC.OST_SpecialityEquipment),
        ('MECH', BIC.OST_MechanicalEquipment), ('GENMOD', BIC.OST_GenericModel),
        ('CASEWORK', BIC.OST_Casework)]
L = []
for tag, cat in CATS:
    rows = []
    for e in FEC(doc).OfCategory(cat).WhereElementIsNotElementType():
        try: p = e.Location.Point
        except Exception: p = None
        if p is None:
            bb = e.get_BoundingBox(None)
            if bb is None: continue
            p = _XYZ((bb.Min.X + bb.Max.X) / 2, (bb.Min.Y + bb.Max.Y) / 2, bb.Min.Z)
        if not (1120 < p.X < 1200 and 78 < p.Y < 128): continue
        try: fam = e.Symbol.Family.Name
        except Exception: fam = '?'
        rows.append('  %-9s (%.1f,%.1f,%5.2f)  %s' % (e.Id.Value, p.X, p.Y, p.Z, fam[:34]))
    if rows:
        L.append('--- %s (%d) ---' % (tag, len(rows)))
        L += sorted(rows)
result = '\n'.join(L)
