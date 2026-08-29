# Report which sheets are currently open as tabs, and focus one. args {"focus":"A101"}
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet
open_sheets = []
for uv in uidoc.GetOpenUIViews():
    v = doc.GetElement(uv.ViewId)
    sn = getattr(v, 'SheetNumber', None)
    if sn: open_sheets.append('%s - %s' % (sn, v.Name))
    else: open_sheets.append('(view) %s' % v.Name)
foc = args.get('focus')
if foc:
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber == foc:
            uidoc.RequestViewChange(s)
result = '%d open:\n%s' % (len(open_sheets), '\n'.join(sorted(open_sheets)))
