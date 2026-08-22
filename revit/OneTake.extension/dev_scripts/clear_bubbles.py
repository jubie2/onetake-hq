# Remove the drawn keynote bubbles (detail curves + single-number texts) from the ADU sections.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, CurveElement, TextNote,
                               ElementId)
from System.Collections.Generic import List
L = []
for nm in ('ADU - Section 1', 'ADU - Section 2', 'ADU - Section 3', 'ADU - Section 4'):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    if v is None: continue
    kill = [e.Id for e in FEC(doc, v.Id).OfClass(CurveElement)]
    for t2 in FEC(doc, v.Id).OfClass(TextNote):
        txt = (t2.Text or '').strip()
        if txt.isdigit() and len(txt) <= 2: kill.append(t2.Id)
    if kill:
        t = Transaction(doc, 'OneTake: clear bubbles'); _prep(t); t.Start()
        doc.Delete(List[ElementId](kill)); doc.Regenerate(); t.Commit()
    L.append('%-18s removed %d' % (nm, len(kill)))
result = '\n'.join(L)
