# Manually two-line the long legend items in MECHANICAL KEYNOTES.
from Autodesk.Revit.DB import FilteredElementCollector as FEC, View, TextNote
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == 'MECHANICAL KEYNOTES': v = x; break
FIX = {
 'CEILING EXHAUST FAN (MIN. OF 75CFM)':
   'CEILING EXHAUST FAN (MIN. OF 75CFM)\nMIN. OF 4" DIA. DUCTED TO OUTSIDE',
 '4" DIA. DRYER EXHAUST DUCT':
   '4" DIA. DRYER EXHAUST DUCT TO OUTSIDE -\nTWO 90 DEG. ELBOWS MAX., 14\' MAX. LENGTH',
 'KITCHEN HOOD EXHAUST FAN':
   'KITCHEN HOOD EXHAUST FAN (SEE SCHEDULE)\nMIN. OF 250CFM FOR INTERMITTENT',
 'ATTIC ACCESS LOCATION':
   'ATTIC ACCESS LOCATION MIN. OF 22"x30"\n(MIN. 30"x30" IF EQUIPMENT REQUIRES)',
 'KITCHEN EXHAUST DUCT TERMINATION':
   'KITCHEN EXHAUST DUCT TERMINATION\nLOCATION (PROVIDE W/ RAIN CAP)',
}
t = Transaction(doc, 'OneTake: legend wrap'); _prep(t); t.Start()
n = 0
for e in FEC(doc, v.Id).OfClass(TextNote):
    txt = (e.Text or '').strip()
    for k, rep in FIX.items():
        if txt.startswith(k):
            e.Text = rep; n += 1; break
doc.Regenerate(); t.Commit()
result = 'rewrapped %d items' % n
