# Renumber ADU sheets to the approved convention; park old colliding sheets as X-*.
# args {"dry":true}
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet
dry = args.get('dry', True)
PARK = ['A101', 'A102', 'A103', 'A104', 'A105', 'A200', 'A201', 'S101']
NEW = [
 ('ADU-1', 'A101', 'Floor Plan'),
 ('ADU-3', 'A102', 'Sections'),
 ('ADU-4', 'A103', 'Roof Plan'),
 ('ADU-2', 'A104', 'Elevations'),
 ('ADU-7', 'A105', 'Door-Windows Schedule & Notes'),
 ('ADU-5', 'A200', 'Mechanical Plan'),
 ('ADU-6', 'A201', 'Electrical Plan'),
 ('ADU-8', 'S101', 'Foundation / Framing Plan'),
]
by = {}
for s in FEC(doc).OfClass(ViewSheet):
    by[s.SheetNumber] = s
L = []
for n in PARK:
    L.append('park %-6s -> X-%-6s (%s)' % (n, n, by[n].Name if n in by else 'MISSING'))
for o, n, nm in NEW:
    L.append('adu  %-6s -> %-6s "%s"' % (o, n, nm))
if not dry:
    t = Transaction(doc, 'OneTake: renumber sheets'); _prep(t); t.Start()
    for n in PARK:
        if n in by: by[n].SheetNumber = 'X-' + n
    doc.Regenerate()
    for o, n, nm in NEW:
        s = by.get(o)
        if s is None: L.append('%s MISSING' % o); continue
        s.SheetNumber = n
        s.Name = nm
    doc.Regenerate(); t.Commit()
    L.append('done')
result = '\n'.join(L)
