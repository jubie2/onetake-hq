# Set door swing (facing) + hinge side (hand) and fixture facing.  args {"items":[{"id":..,"facing":[x,y],"hand":[x,y]}]}
# facing = direction the door swings toward / the fixture front; hand = direction from hinge to latch.
from Autodesk.Revit.DB import FamilyInstance, ElementTransformUtils, Line
import math
def v(a): return XYZ(float(a[0]), float(a[1]), 0)
def rep(el):
    return {'facing': [round(el.FacingOrientation.X, 2), round(el.FacingOrientation.Y, 2)],
            'hand': [round(el.HandOrientation.X, 2), round(el.HandOrientation.Y, 2)],
            'ff': el.FacingFlipped, 'hf': el.HandFlipped}
out = []
t = Transaction(doc, 'OneTake: door swings / fixture facing')
_prep(t)
t.Start()
try:
    for it in args.get('items', []):
        el = doc.GetElement(ElementId(long(it['id'])))
        r = {'id': it['id'], 'before': rep(el)}
        if it.get('facing'):
            want = v(it['facing'])
            if el.FacingOrientation.DotProduct(want) < 0.5:
                if el.CanFlipFacing:
                    el.flipFacing()
                    r['flipped_facing'] = True
                else:
                    # free-standing: rotate about its location point so facing matches
                    cur = el.FacingOrientation
                    ang = math.atan2(want.Y, want.X) - math.atan2(cur.Y, cur.X)
                    p = el.Location.Point
                    ElementTransformUtils.RotateElement(doc, el.Id, Line.CreateBound(p, p + XYZ.BasisZ), ang)
                    r['rotated_deg'] = round(math.degrees(ang), 1)
                doc.Regenerate()
        if it.get('hand'):
            want = v(it['hand'])
            if el.HandOrientation.DotProduct(want) < 0.5:
                if el.CanFlipHand:
                    el.flipHand()
                    r['flipped_hand'] = True
                else:
                    r['hand_error'] = 'cannot flip hand'
                doc.Regenerate()
        if it.get('to'):
            p = el.Location.Point
            ElementTransformUtils.MoveElement(doc, el.Id, XYZ(float(it['to'][0]) - p.X, float(it['to'][1]) - p.Y, 0))
            doc.Regenerate()
        r['after'] = rep(el)
        bb = el.get_BoundingBox(None)
        if bb:
            r['bbox'] = [round(bb.Min.X, 2), round(bb.Min.Y, 2), round(bb.Max.X, 2), round(bb.Max.Y, 2)]
        out.append(r)
    t.Commit()
except Exception:
    t.RollBack()
    raise
result = out
