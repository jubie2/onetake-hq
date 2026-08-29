# Bring the project document to the front (RequestViewChange on a UIDocument built
# from the project) so document-context operations like flipFacing work again.
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet
from Autodesk.Revit.UI import UIDocument
pdoc = None
for d in doc.Application.Documents:
    if not d.IsFamilyDocument and 'Electric Ave' in d.Title: pdoc = d; break
L = ['active before: %s' % doc.Title]
target = None
for s in FEC(pdoc).OfClass(ViewSheet):
    if s.SheetNumber == 'A201': target = s; break
try:
    ud = UIDocument(pdoc)
    ud.RequestViewChange(target)
    L.append('requested view change to %s - %s' % (target.SheetNumber, target.Name))
except Exception as ex:
    L.append('activate FAILED: %s' % str(ex)[:80])
result = '\n'.join(L)
