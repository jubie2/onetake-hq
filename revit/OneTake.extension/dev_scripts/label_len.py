# Set viewport title-line length to the drawing width. args {"prefix":"ADU - ","dry":true}
from Autodesk.Revit.DB import Viewport, ViewSheet
L = []
t = None
if not args.get('dry', True):
    t = Transaction(doc, 'OneTake: label line length'); _prep(t); t.Start()
for vp in FilteredElementCollector(doc).OfClass(Viewport):
    try:
        v = doc.GetElement(vp.ViewId)
        if not v.Name.startswith(args.get('prefix', 'ADU - ')): continue
        bb = v.CropBox
        w = (bb.Max.X - bb.Min.X) / float(v.Scale)
        before = vp.LabelLineLength
        if not args.get('dry', True):
            vp.LabelLineLength = max(0.25, w)
        o = vp.GetBoxOutline()
        L.append('%-30s line %.2f -> %.2f   box now %.2f x %.2f' %
                 (v.Name[:30], before, w, o.MaximumPoint.X-o.MinimumPoint.X,
                  o.MaximumPoint.Y-o.MinimumPoint.Y))
    except Exception as ex:
        L.append('err %s' % ex)
if t is not None:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)
