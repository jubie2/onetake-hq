# Place fixed windows (custom widths) + S-wall doors + air curtain 28 on the new solid walls.
from Autodesk.Revit.DB import FamilySymbol, BuiltInParameter, Level, Wall
from Autodesk.Revit.DB.Structure import StructuralType
import math
level = [l for l in FilteredElementCollector(doc).OfClass(Level) if l.Name == '1st Floor Level'][0]
base = doc.GetElement(ElementId(4429602))          # Fixed2 : 5'x8'
door_sym = doc.GetElement(ElementId(3484706))      # Single-Glass 36x80
ac_sym = doc.GetElement(ElementId(4979650))        # PH-28 air curtain
S = doc.GetElement(ElementId(4981922)); W1 = doc.GetElement(ElementId(4981923))
W2 = doc.GetElement(ElementId(4981924)); D = doc.GetElement(ElementId(4981925))
# name, width, host wall, center xy
d0 = (6.3, 49.25); ux, uy = 0.8905, 0.4550
wins = [
    ('PH-WIN S1 7-1', 7.1, S, (15.55, 0)), ('PH-WIN S2 10-8', 10.7, S, (27.25, 0)),
    ('PH-WIN S3 10-6', 10.5, S, (41.45, 0)), ('PH-WIN S4 10-0', 10.0, S, (57.5, 0)),
    ('PH-WIN W1 13-11', 13.9, W1, (6.3, 32.85)), ('PH-WIN W2 6-5', 6.45, W2, (6.3, 46.0)),
    ('PH-WIN D1 9-0', 9.0, D, (d0[0] + 5.9 * ux, d0[1] + 5.9 * uy)),
    ('PH-WIN D2 9-0', 9.0, D, (d0[0] + 15.6 * ux, d0[1] + 15.6 * uy)),
]
existing = {}
for fs in FilteredElementCollector(doc).OfClass(FamilySymbol):
    if fs.FamilyName == 'Fixed2':
        existing[fs.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()] = fs
placed = []
t = Transaction(doc, 'OneTake: windows + doors + air curtain')
_prep(t)
t.Start()
try:
    for name, w, host, c in wins:
        sym = existing.get(name)
        if sym is None:
            sym = doc.GetElement(base.Duplicate(name).Id)
            sym.LookupParameter('Width').Set(float(w))
            sym.LookupParameter('Height').Set(8.0)
            existing[name] = sym
        if not sym.IsActive:
            sym.Activate()
        pt = XYZ(c[0], c[1], level.Elevation + 0.5)
        inst = doc.Create.NewFamilyInstance(pt, sym, host, level, StructuralType.NonStructural)
        placed.append({'win': name, 'id': inst.Id.Value})
    if not door_sym.IsActive:
        door_sym.Activate()
    for x, lab in ((20.5, 'S single'), (47.55, 'S double L'), (51.65, 'S double R')):
        inst = doc.Create.NewFamilyInstance(XYZ(x, 0, level.Elevation), door_sym, S, level, StructuralType.NonStructural)
        placed.append({'door': lab, 'id': inst.Id.Value})
    if not ac_sym.IsActive:
        ac_sym.Activate()
    ac = doc.Create.NewFamilyInstance(XYZ(49.6, 0, level.Elevation), ac_sym, S, level, StructuralType.NonStructural)
    placed.append({'air_curtain_28': ac.Id.Value})
    doc.Regenerate()
    t.Commit()
except Exception:
    t.RollBack()
    raise
# read back bboxes
for p in placed:
    el = doc.GetElement(ElementId(long(p.values()[-1] if 'id' not in p else p['id'])))
    bb = el.get_BoundingBox(None)
    if bb:
        p['bbox'] = [round(bb.Min.X, 2), round(bb.Min.Y, 2), round(bb.Max.X, 2), round(bb.Max.Y, 2)]
result = placed
