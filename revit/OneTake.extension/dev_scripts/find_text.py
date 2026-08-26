# Find TextNotes containing a string, report owner view. args {"q":"CRRC"}
from Autodesk.Revit.DB import FilteredElementCollector as FEC, TextNote
q = args['q'].lower()
L = []
for e in FEC(doc).OfClass(TextNote):
    txt = (e.Text or '')
    if q in txt.lower():
        v = doc.GetElement(e.OwnerViewId)
        L.append('id %s view [%s]\n%s' % (e.Id.Value, v.Name if v else '?',
                                          txt.replace('\r', ' / ')[:220]))
result = '\n'.join(L) or 'not found'
