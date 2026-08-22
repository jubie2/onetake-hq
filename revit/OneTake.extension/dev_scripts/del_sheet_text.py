# Delete text notes on sheets matching a substring. args {"sheets":["ADU-2"],"contains":"ADU - ","dry":true}
from Autodesk.Revit.DB import ViewSheet, TextNote, FilteredElementCollector as FEC
L = []
t = None
if not args.get('dry', True):
    t = Transaction(doc, 'OneTake: delete sheet text'); _prep(t); t.Start()
for sh in FEC(doc).OfClass(ViewSheet):
    if args.get('sheets') and sh.SheetNumber not in args['sheets']: continue
    for tn in list(FEC(doc, sh.Id).OfClass(TextNote)):
        try:
            txt = tn.Text or ''
            if args.get('contains', '') in txt:
                L.append('%s: "%s"' % (sh.SheetNumber, txt.strip()[:40]))
                if not args.get('dry', True): doc.Delete(tn.Id)
        except Exception: pass
if t is not None:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L) or 'none'
