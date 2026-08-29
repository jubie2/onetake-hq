# Flip the 5 north-run kitchen GFIs and report FacingFlipped before/after.
from Autodesk.Revit.DB import ElementId
pdoc = None
for d in doc.Application.Documents:
    if not d.IsFamilyDocument and 'Electric Ave' in d.Title: pdoc = d; break
IDS = [2244839, 2244840, 2244841, 2244842, 2244843]
L = []
t = Transaction(pdoc, 'OneTake: flip kitchen GFIs'); _prep(t); t.Start()
for i in IDS:
    e = pdoc.GetElement(ElementId(i))
    if e is None: L.append('%s missing' % i); continue
    before = e.FacingFlipped
    try:
        e.flipFacing()
        pdoc.Regenerate()
        L.append('%s flipped %s -> %s' % (i, before, e.FacingFlipped))
    except Exception as ex:
        L.append('%s FAIL %s' % (i, str(ex)[:60]))
pdoc.Regenerate(); t.Commit()
result = '\n'.join(L)
