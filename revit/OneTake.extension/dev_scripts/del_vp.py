# Delete a viewport by the view's element id. args {"sheet":"ADU-6","view_ids":[1019342]}
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet, Viewport, ElementId
from System.Collections.Generic import List
L = []
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == args['sheet']: sh = s; break
kill = []
for vp in FEC(doc, sh.Id).OfClass(Viewport):
    if vp.ViewId.IntegerValue in args['view_ids']:
        kill.append(vp.Id)
        L.append('removing viewport of view %s' % vp.ViewId)
if kill:
    t = Transaction(doc, 'OneTake: remove viewport'); _prep(t); t.Start()
    doc.Delete(List[ElementId](kill)); doc.Regenerate(); t.Commit()
    L.append('deleted %d' % len(kill))
result = '\n'.join(L) or 'nothing matched'
