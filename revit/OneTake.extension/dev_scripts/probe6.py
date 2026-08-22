from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewSheet, ViewSchedule,
                               BuiltInCategory as BIC, BuiltInParameter as BIP, XYZ as _XYZ,
                               SectionType)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
L = []
def cats_in(nm):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    if v is None: return None, {}
    c = {}
    for e in FEC(doc, v.Id):
        k = e.Category.Name if e.Category else '(none)'
        c[k] = c.get(k, 0) + 1
    return v, c
L.append('=== annotation content: main vs ADU floor plans')
for nm in ('1st Floor Plan', 'ADU - 1st Floor Plan'):
    v, c = cats_in(nm)
    keep = ['Keynote Tags', 'Dimensions', 'Text Notes', 'Room Tags', 'Rooms',
            'Door Tags', 'Window Tags', 'Generic Annotations', 'Detail Items']
    L.append('  %-22s %s' % (nm[:22], dict((k, c.get(k, 0)) for k in keep)))
L.append('=== does the Site plan cover the ADU?')
for nm in ('Site', 'BMP Site Plan', 'Landscaping Plan'):
    v, c = cats_in(nm)
    if v is None: continue
    bb = v.CropBox; tf = bb.Transform
    pts = []
    for x in (bb.Min.X, bb.Max.X):
        for y in (bb.Min.Y, bb.Max.Y):
            pts.append(tf.OfPoint(_XYZ(x, y, 0.0)))
    xs = [p.X for p in pts]; ys = [p.Y for p in pts]
    covers = min(xs) <= X0 and max(xs) >= X1 and min(ys) <= Y0 and max(ys) >= Y1
    L.append('  %-18s cropOn %-5s world X %.0f..%.0f Y %.0f..%.0f  covers ADU: %s' % (
        nm, v.CropBoxActive, min(xs), max(xs), min(ys), max(ys), covers))
L.append('=== schedules that could serve the ADU (rows + filters)')
for nm in ('HEATING FURNACE SCHEDULE', 'DRYER SCHEDULE', 'Exhaust Fan Schedule',
           'WATER HEATER SCHEDULE (HEATPUMP )', 'Electrical Notes', 'SHEAR WALL SCHEDULE',
           'TABLE 4.303.2', 'Plumbing Fixture Schedule'):
    for s in FEC(doc).OfClass(ViewSchedule):
        if s.Name != nm: continue
        d = s.Definition
        try:
            td = s.GetTableData().GetSectionData(SectionType.Body)
            rows = td.NumberOfRows
        except Exception: rows = '?'
        L.append('  %-34s rows %-4s fields %d filters %d  itemized=%s' % (
            nm[:34], rows, d.GetFieldCount(), d.GetFilterCount(), d.IsItemized))
L.append('=== drafting views not yet reused for the ADU')
for nm in ('KEY NOTES Floor Plan', 'GREEN CODE NOTES', 'ATTIC SECTION', 'DRAWING SYMBOLS',
           'ABBREVIATIONS'):
    hit = [x for x in FEC(doc).OfClass(View) if not x.IsTemplate and x.Name == nm]
    if not hit: L.append('  %-24s NOT FOUND' % nm); continue
    v = hit[0]
    on = 'unplaced'
    for s in FEC(doc).OfClass(ViewSheet):
        for vpid in s.GetAllViewports():
            if doc.GetElement(vpid).ViewId == v.Id: on = s.SheetNumber
    L.append('  %-24s type %-14s on sheet %s' % (nm, str(v.ViewType), on))
result = '\n'.join(L)
