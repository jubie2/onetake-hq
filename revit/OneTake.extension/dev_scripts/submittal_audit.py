# Readiness audit: titleblock fields, project info, ADU areas, egress-relevant window sizes.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, FamilyInstance,
                               BuiltInCategory as BIC, BuiltInParameter as BIP, ViewSchedule)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
L = []
L.append('=== Project Information')
pi = doc.ProjectInformation
for bip, nm in ((BIP.PROJECT_NAME, 'Project Name'), (BIP.PROJECT_ADDRESS, 'Project Address'),
                (BIP.PROJECT_NUMBER, 'Project Number'), (BIP.CLIENT_NAME, 'Client Name'),
                (BIP.PROJECT_STATUS, 'Project Status'), (BIP.PROJECT_ISSUE_DATE, 'Issue Date'),
                (BIP.PROJECT_BUILDING_NAME, 'Building Name'), (BIP.PROJECT_AUTHOR, 'Author')):
    try:
        p = pi.get_Parameter(bip)
        L.append('  %-16s %r' % (nm, p.AsString() if p else None))
    except Exception: pass
L.append('=== titleblock fields on the ADU sheets')
for s in sorted(FEC(doc).OfClass(ViewSheet), key=lambda z: z.SheetNumber):
    if not s.SheetNumber.startswith('ADU'): continue
    tb = list(FEC(doc, s.Id).OfCategory(BIC.OST_TitleBlocks).WhereElementIsNotElementType())
    vals = {}
    for e in tb:
        for pn in ('Drawing Date', 'Check By', 'Drawn By', 'Job Number', 'Scale',
                   'Checked By', 'Sheet Number'):
            try:
                p = e.LookupParameter(pn)
                if p: vals[pn] = p.AsString() or (str(p.AsValueString()) if p.StorageType else '')
            except Exception: pass
    L.append('  %-7s %s' % (s.SheetNumber, vals))
L.append('=== ADU room areas (per floor)')
tot = {}
for r in FEC(doc).OfCategory(BIC.OST_Rooms).WhereElementIsNotElementType():
    try:
        if r.Area < 1: continue
        b = r.get_BoundingBox(None)
        cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
        if not (X0 <= cx <= X1 and Y0 <= cy <= Y1): continue
        k = r.Level.Name
        tot[k] = tot.get(k, 0.0) + r.Area
    except Exception: pass
for k in tot: L.append('  %-18s %.0f sf' % (k, tot[k]))
L.append('  TOTAL %.0f sf' % sum(tot.values()))
L.append('=== ADU bedroom egress windows (CRC R310: 5.7 sf min, 24" h, 20" w, sill <= 44")')
for e in FEC(doc).OfCategory(BIC.OST_Windows).WhereElementIsNotElementType():
    try:
        b = e.get_BoundingBox(None)
        cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
        if not (X0 <= cx <= X1 and Y0 <= cy <= Y1): continue
        w = e.Symbol.get_Parameter(BIP.WINDOW_WIDTH); h = e.Symbol.get_Parameter(BIP.WINDOW_HEIGHT)
        sill = e.get_Parameter(BIP.INSTANCE_SILL_HEIGHT_PARAM)
        mk = e.get_Parameter(BIP.ALL_MODEL_MARK)
        if w is None or h is None: continue
        ww = w.AsDouble(); hh = h.AsDouble()
        ok = (ww * hh >= 5.7 and hh >= 2.0 and ww >= 1.667)
        L.append('  mark %-4s %4.1f x %4.1f ft = %4.1f sf  sill %.2f  egress-size OK: %s' % (
            mk.AsString() if mk else '?', ww, hh, ww * hh,
            sill.AsDouble() if sill and sill.HasValue else -1, ok))
    except Exception: pass
result = '\n'.join(L)
