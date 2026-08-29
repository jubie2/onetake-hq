# How do the OLD (working) Logan outlets differ from mine? Facing vs host-wall normal.
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId,
                               BuiltInCategory as BIC)
pdoc = None
for d in doc.Application.Documents:
    if not d.IsFamilyDocument and 'Electric Ave' in d.Title: pdoc = d; break
L = ['active doc: %s   (project ops run on: %s)' % (doc.Title, pdoc.Title)]
n = 0
flips = {True: 0, False: 0}
for e in FEC(pdoc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try: p = e.Location.Point
    except Exception: continue
    if p is None: continue
    if not (940 < p.X < 1030 and -160 < p.Y < -80): continue      # old Logan zone
    try:
        ff = e.FacingFlipped; cff = e.CanFlipFacing
    except Exception:
        ff = cff = '?'
    flips[ff] = flips.get(ff, 0) + 1
    if n < 12:
        try: hw = e.Host.Name[:20]
        except Exception: hw = '?'
        L.append('  %-9s (%.1f,%.1f) face(%.2f,%.2f) flipped=%-5s canflip=%-5s %-14s host %s' % (
            e.Id.Value, p.X, p.Y, e.FacingOrientation.X, e.FacingOrientation.Y,
            ff, cff, e.Symbol.Family.Name[:14], hw))
    n += 1
L.append('old outlets: %d   FacingFlipped counts: %s' % (n, flips))
result = '\n'.join(L)
