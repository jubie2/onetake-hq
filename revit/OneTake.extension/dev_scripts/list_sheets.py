# All sheets in the doc: number | name.
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet
L = []
for s in FEC(doc).OfClass(ViewSheet):
    L.append('%-8s | %s' % (s.SheetNumber, s.Name))
L.sort()
result = '\n'.join(L)
