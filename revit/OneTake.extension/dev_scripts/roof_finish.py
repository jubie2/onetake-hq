# Clean the ADU roof plan and add the missing roof-plan information.
# args {"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, RoofBase, Options,
                               BuiltInCategory as BIC, BuiltInParameter as BIP, XYZ as _XYZ,
                               Line, TextNote, TextNoteOptions, TextNoteType,
                               HorizontalTextAlignment, ViewDetailLevel)
NM = 'ADU - Roof Plan'
dry = args.get('dry', True)
HIDE = ['Mechanical Equipment', 'Plumbing Fixtures', 'Casework', 'Specialty Equipment',
        'Furniture', 'Electrical Fixtures', 'Lighting Fixtures', 'Doors', 'Windows',
        'Stairs', 'Railings', 'Floors', 'Rooms', 'Ceilings']
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == NM: v = x; break
L = []
r = list(FEC(doc, v.Id).OfClass(RoofBase))
if r:
    b = r[0].get_BoundingBox(None)
    L.append('roof extent  X %.1f..%.1f  Y %.1f..%.1f  (%.1f x %.1f ft)' % (
        b.Min.X, b.Max.X, b.Min.Y, b.Max.Y, b.Max.X - b.Min.X, b.Max.Y - b.Min.Y))
    L.append('ADU walls    X 1157.9..1186.5  Y -150.3..-125.7  -> overhang %.2f ft' % (1157.9 - b.Min.X))
tt = None
for t2 in FEC(doc).OfClass(TextNoteType):
    if (t2.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == 'ARCH TEXT 12 1/8"':
        tt = t2; break
NOTES = ["CLASS 'A' ROOF SHINGLES OVER (1) LAYER 30# FELT",
         "OVER 1/2\" CDX PLYWOOD SHEATHING",
         "2x8 FASCIA W/ GUTTER - TYP. AT ALL EAVES",
         "1'-6\" ROOF OVERHANG - TYP. ALL SIDES",
         "PROVIDE ATTIC VENTILATION PER ROOF LEGEND"]
if not dry:
    t = Transaction(doc, 'OneTake: finish roof plan'); _prep(t); t.Start()
    cats = doc.Settings.Categories
    n = 0
    for cn in HIDE:
        try:
            c = cats.get_Item(cn)
            if c is not None and v.CanCategoryBeHidden(c.Id):
                v.SetCategoryHidden(c.Id, True); n += 1
        except Exception: pass
    doc.Regenerate()
    L.append('hid %d clutter categories' % n)
    bb = v.CropBox; tfm = bb.Transform; inv = tfm.Inverse
    # stack the notes clear of the roof: step X (vertical on this rotated plan)
    for i, txt in enumerate(reversed(NOTES)):
        q = inv.OfPoint(_XYZ(1156.0 - 1.4 - i * 1.4, -152.5, 0.0))
        p = tfm.OfPoint(_XYZ(q.X, q.Y, 0.0))
        o = TextNoteOptions(tt.Id)
        o.HorizontalAlignment = HorizontalTextAlignment.Left
        TextNote.Create(doc, v.Id, p, txt, o)
    doc.Regenerate(); t.Commit()
    L.append('wrote %d roof notes' % len(NOTES))
result = '\n'.join(L)
