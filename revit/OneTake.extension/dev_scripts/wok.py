from Autodesk.Revit.DB import BuiltInParameter, Level, FamilySymbol
from Autodesk.Revit.DB.Structure import StructuralType
level = [l for l in FilteredElementCollector(doc).OfClass(Level) if l.Name == '1st Floor Level'][0]
base = doc.GetElement(ElementId(4305481))
name = 'PH-06 CHINESE WOK RANGE 9FT'
sym = None
for fs in FilteredElementCollector(doc).OfClass(FamilySymbol):
    if fs.FamilyName == base.FamilyName and fs.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString() == name:
        sym = fs
t = Transaction(doc, 'OneTake: wok range'); _prep(t); t.Start()
if sym is None:
    sym = doc.GetElement(base.Duplicate(name).Id)
    sym.LookupParameter('RANGE LENGTH').Set(9.0)
    sym.LookupParameter('RANGE WIDTH').Set(3.5)
    tm = sym.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_MARK)
    if tm: tm.Set('06')
if not sym.IsActive: sym.Activate()
inst = doc.Create.NewFamilyInstance(XYZ(float(args.get('x', 33.7)), float(args.get('y', 17.0)), level.Elevation), sym, level, StructuralType.NonStructural)
doc.Regenerate()
bb = inst.get_BoundingBox(None)
has_item = inst.LookupParameter('Item') is not None
t.Commit()
result = {'id': inst.Id.Value, 'bbox': [round(bb.Min.X,2), round(bb.Min.Y,2), round(bb.Max.X,2), round(bb.Max.Y,2)], 'has_Item_param': has_item,
          'category': inst.Category.Name}
