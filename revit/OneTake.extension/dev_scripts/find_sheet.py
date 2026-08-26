# args {"num":"A105"} -> sheet name for a sheet number
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet
L = []
for s in FEC(doc).OfClass(ViewSheet):
    if args.get('num') in (s.SheetNumber,):
        L.append('%s | %s' % (s.SheetNumber, s.Name))
result = '\n'.join(L) or 'not found'
