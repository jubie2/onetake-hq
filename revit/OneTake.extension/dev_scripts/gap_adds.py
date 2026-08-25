# Step-4 gap additions from the approved set. args {"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewSheet, Viewport,
                               TextNote, TextNoteType, TextNoteOptions, HorizontalTextAlignment,
                               BuiltInParameter as BIP, XYZ as _XYZ)
dry = args.get('dry', True)
L = []
tt = None
for t2 in FEC(doc).OfClass(TextNoteType):
    if (t2.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == 'ARCH TEXT 12 1/8"':
        tt = t2; break
def note(v, x, y, txt, align):
    o = TextNoteOptions(tt.Id)
    o.HorizontalAlignment = align
    TextNote.Create(doc, v.Id, _XYZ(x, y, 0), txt, o)
# is there a MECH General Notes legend?
mech = None
for v in FEC(doc).OfClass(View):
    try:
        if v.IsTemplate: continue
        if 'MECH' in v.Name.upper() and 'GENERAL' in v.Name.upper(): mech = v
    except Exception: pass
L.append('MECH General Notes legend: %s' % (mech.Name if mech else 'NOT IN MODEL'))
if not dry:
    t = Transaction(doc, 'OneTake: approved-set gap adds'); _prep(t); t.Start()
    # 1. roof plan: FUTURE SOLAR PANELS + shingle spec (view coords are world here)
    rv = None
    for v in FEC(doc).OfClass(View):
        if not v.IsTemplate and v.Name == 'ADU - Roof Plan': rv = v; break
    tf = rv.CropBox.Transform; inv = tf.Inverse
    def rnote(wx, wy, txt, align=HorizontalTextAlignment.Left):
        q = inv.OfPoint(_XYZ(wx, wy, 0.0))
        note(rv, 0, 0, txt, align)   # placeholder replaced below
    # place directly with transformed points
    def rnote2(wx, wy, txt, align=HorizontalTextAlignment.Left):
        q = inv.OfPoint(_XYZ(wx, wy, 0.0))
        p = tf.OfPoint(_XYZ(q.X, q.Y, 0.0))
        o = TextNoteOptions(tt.Id)
        o.HorizontalAlignment = align
        o.Rotation = 1.5707963
        TextNote.Create(doc, rv.Id, p, txt, o)
    rnote2(1162.0, -131.5, 'FUTURE\nSOLAR PANELS', HorizontalTextAlignment.Center)
    rnote2(1153.0, -150.0,
           'ROOF SHINGLE: OWENS CORNING (OR EQ.), CLASS A,\n'
           'ICC-ESR LISTED / CRRC RATED, OVER (1) LAYER 30# FELT')
    L.append('roof plan: solar + shingle spec notes added')
    # 2. ADU-8: roof framing note block on the Roof Framing Plan view
    fv = None
    for v in FEC(doc).OfClass(View):
        if not v.IsTemplate and v.Name == 'ADU - Roof Framing Plan': fv = v; break
    tf2 = fv.CropBox.Transform; inv2 = tf2.Inverse
    lines = ['ROOF FRAMING NOTE:',
             'ROOF TRUSS MANUFACTURER: PER DEFERRED SUBMITTAL',
             'TRUSS SPACING: 24" O.C.',
             'HEEL HEIGHT: 3 15/16" U.N.O.',
             'TAIL LENGTH: 24" U.N.O. / TAIL SIZE: 2x4 U.N.O.']
    for i, s in enumerate(reversed(lines)):
        q = inv2.OfPoint(_XYZ(1157.9 - 8.6 - i * 1.4, -150.3 - 1.5, 0.0))
        p = tf2.OfPoint(_XYZ(q.X, q.Y, 0.0))
        o = TextNoteOptions(tt.Id)
        o.HorizontalAlignment = HorizontalTextAlignment.Left
        TextNote.Create(doc, fv.Id, p, s, o)
    L.append('ADU-8 framing plan: roof framing note block added')
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)
