# A200 polish: re-anchor mech plan titles; make legend item 12 three lines.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               ElementId, XYZ as _XYZ)
L = []
t = Transaction(doc, 'OneTake: A200 polish'); _prep(t); t.Start()
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A200': sh = s
for vp in FEC(doc, sh.Id).OfClass(Viewport):
    v = doc.GetElement(vp.ViewId)
    if v.Name.startswith('ADU ') and 'Mech' in v.Name:
        try:
            vp.LabelOffset = _XYZ(0.06, -0.05, 0)
            L.append('%s label reset' % v.Name)
        except Exception as ex:
            L.append('label %s' % str(ex)[:40])
e2 = doc.GetElement(ElementId(1892507))
e2.Text = ('\r\rHEAT PUMP WATER HEATER PER SCHEDULE\r\r'
           'SMOKE DETECTOR, HARD-WIRED W/\r'
           'BATTERY BACK-UP, INTERCONNECTED\r'
           '[CRC R314]\r\r'
           'CARBON MONOXIDE ALARM [CRC R315]\r\r'
           'IAQ (WHOLE BLDG VENT) EXHAUST FAN\r'
           '64 CFM MIN. CONTINUOUS\r')
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
