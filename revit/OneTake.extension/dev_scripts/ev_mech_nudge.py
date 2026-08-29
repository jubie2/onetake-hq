# Push the 12 / 13 (smoke & CO) keynote bubbles further out along their own leader
# so they stop sitting on the room-name tags.
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, XYZ as _XYZ,
                               BuiltInCategory as BIC)
L = []
t = Transaction(doc, 'OneTake: nudge SD/CO tags'); _prep(t); t.Start()
for vid in (2244930, 2244778):
    v = doc.GetElement(ElementId(vid))
    n = 0
    for e in FEC(doc, v.Id).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
        try:
            if e.Symbol.Family.Name != 'TAG LABEL': continue
            p = e.LookupParameter('TEXT')
            if not p or p.AsString() not in ('12', '13'): continue
        except Exception:
            continue
        try:
            lds = list(e.GetLeaders())
            if not lds: continue
            end = lds[0].End
            loc = e.Location.Point
            dx, dy = loc.X - end.X, loc.Y - end.Y
            m = math.hypot(dx, dy) or 1.0
            mx, my = dx / m * 2.0, dy / m * 2.0
            e.Location.Move(_XYZ(mx, my, 0))
            el = lds[0].Elbow
            lds[0].Elbow = _XYZ(el.X + mx * 0.5, el.Y + my * 0.5, 0)
            lds[0].End = end
            n += 1
        except Exception as ex:
            L.append('  %s' % str(ex)[:40])
    L.append('%s: %d bubbles nudged' % (v.Name, n))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
