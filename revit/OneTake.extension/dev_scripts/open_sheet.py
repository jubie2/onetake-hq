# Make a sheet (or view) the active view in Revit. args {"sheet":"ADU-2"} or {"view":"..."}
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet, View
target = None
if args.get('sheet'):
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber == args['sheet']: target = s; break
elif args.get('view'):
    for v in FEC(doc).OfClass(View):
        if not v.IsTemplate and v.Name == args['view']: target = v; break
if target is None:
    result = 'not found'
else:
    uidoc.RequestViewChange(target)
    result = 'active view -> %s  %s' % (
        getattr(target, 'SheetNumber', ''), target.Name)
