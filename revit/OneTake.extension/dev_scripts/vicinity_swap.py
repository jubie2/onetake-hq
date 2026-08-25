# Replace the Logan-Ave vicinity drawing with the Keeler OSM map image.
# args {"dry":true,"paper_w":0.42}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, TextNote, CurveElement,
                               ElementId, ImageTypeOptions, ImageType, ImageInstance,
                               ImagePlacementOptions, XYZ as _XYZ, BoxPlacement,
                               ImageTypeSource, FilledRegion)
from System.Collections.Generic import List
dry = args.get('dry', True)
PW = float(args.get('paper_w', 0.42))
IMG = r'C:\dev\onetake-hq\revit\reference\keeler-vicinity.png'
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == 'VINCINITY': v = x; break
L = ['view %s scale %s' % (v.Id, v.Scale)]
kill = []
keep_notes = []
for e in FEC(doc, v.Id).WhereElementIsNotElementType():
    if isinstance(e, (TextNote, CurveElement, FilledRegion)):
        txt = (e.Text or '').strip() if isinstance(e, TextNote) else ''
        kill.append(e.Id)
        L.append('  del %-12s %r' % (e.Category.Name if e.Category else '?', txt[:24]))
    elif isinstance(e, ImageInstance):
        kill.append(e.Id); L.append('  del old image %s' % e.Id)
L.append('%d elements to remove' % len(kill))
if not dry:
    t = Transaction(doc, 'OneTake: Keeler vicinity map'); _prep(t); t.Start()
    if kill: doc.Delete(List[ElementId](kill))
    doc.Regenerate()
    opts = ImageTypeOptions(IMG, False, ImageTypeSource.Import)
    it = ImageType.Create(doc, opts)
    po = ImagePlacementOptions(_XYZ(0, 0, 0), BoxPlacement.Center)
    inst = ImageInstance.Create(doc, v, it.Id, po)
    doc.Regenerate()
    # size it: Width is in model feet; paper size = width / view scale
    try:
        inst.Width = PW * v.Scale
        doc.Regenerate()
    except Exception as ex:
        L.append('  width set fail %s' % str(ex)[:50])
    # NO SCALE note under the map
    from Autodesk.Revit.DB import TextNoteType, TextNoteOptions, HorizontalTextAlignment, BuiltInParameter as BIP
    tt = None
    for t2 in FEC(doc).OfClass(TextNoteType):
        if (t2.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == 'ARCH TEXT 12 1/8"':
            tt = t2; break
    if tt:
        o = TextNoteOptions(tt.Id)
        o.HorizontalAlignment = HorizontalTextAlignment.Center
        h = PW * v.Scale
        TextNote.Create(doc, v.Id, _XYZ(0, -h / 2.0 - 0.06 * v.Scale, 0), 'NO SCALE', o)
    doc.Regenerate(); t.Commit()
    L.append('placed image %s at %.2f ft paper width' % (inst.Id, PW))
result = '\n'.join(L)
