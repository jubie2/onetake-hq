# Why won't the outlets flip, and what will move them to the room side?
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, XYZ as _XYZ,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
from Autodesk.Revit.DB.Structure import StructuralType
pdoc = None
for d in doc.Application.Documents:
    if not d.IsFamilyDocument and 'Electric Ave' in d.Title: pdoc = d; break
e = pdoc.GetElement(ElementId(2244839))            # a kitchen GFI on the north wall
L = []
L.append('elem %s %s' % (e.Id.Value, e.Symbol.Family.Name))
for a in ('CanFlipFacing', 'CanFlipHand', 'FacingFlipped', 'HandFlipped',
          'CanRotate', 'Mirrored'):
    try: L.append('  %-14s = %s' % (a, getattr(e, a)))
    except Exception as ex: L.append('  %-14s ! %s' % (a, str(ex)[:40]))
try:
    h = e.Host
    L.append('  host %s %s  thickness %.3f' % (h.Id.Value, h.Name[:24], h.Width))
    c = h.Location.Curve
    a0 = c.GetEndPoint(0); b0 = c.GetEndPoint(1)
    L.append('  host curve (%.2f,%.2f)->(%.2f,%.2f)' % (a0.X, a0.Y, b0.X, b0.Y))
except Exception as ex:
    L.append('  host? %s' % str(ex)[:40])
p = e.Location.Point
L.append('  loc (%.3f,%.3f,%.3f)  facing (%.2f,%.2f)' % (
    p.X, p.Y, p.Z, e.FacingOrientation.X, e.FacingOrientation.Y))
# what parameters might control the side / offset?
for prm in e.Parameters:
    try:
        d2 = prm.Definition.Name
        if any(k in d2.lower() for k in ('offset', 'elev', 'host', 'side', 'flip')):
            L.append('  param %-28s = %s' % (d2, prm.AsValueString() or prm.AsString()))
    except Exception: pass
# try a test flip in a throwaway transaction
t = Transaction(pdoc, 'OneTake: flip test'); _prep(t); t.Start()
try:
    e.flipFacing()
    pdoc.Regenerate()
    L.append('  flipFacing() OK -> facing (%.2f,%.2f)' % (
        e.FacingOrientation.X, e.FacingOrientation.Y))
except Exception as ex:
    L.append('  flipFacing() FAILED: %s' % str(ex)[:70])
try:
    e.flipHand()
    pdoc.Regenerate()
    L.append('  flipHand() OK -> facing (%.2f,%.2f)' % (
        e.FacingOrientation.X, e.FacingOrientation.Y))
except Exception as ex:
    L.append('  flipHand() FAILED: %s' % str(ex)[:70])
t.RollBack()
result = '\n'.join(L)
