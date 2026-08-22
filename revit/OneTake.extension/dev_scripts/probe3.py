from Autodesk.Revit.DB import (FilteredElementCollector as FEC, BuiltInCategory as BIC,
                               BuiltInParameter as BIP, ViewSchedule, SectionType, View,
                               Group, GroupType, ElementType)
L = []
L.append('=== Drawing List rows (actual)')
for s in FEC(doc).OfClass(ViewSchedule):
    if s.Name != 'Drawing List': continue
    td = s.GetTableData().GetSectionData(SectionType.Body)
    for r in range(td.NumberOfRows):
        cells = [s.GetCellText(SectionType.Body, r, c) or '' for c in range(td.NumberOfColumns)]
        L.append('   %s' % ' | '.join(cells))
L.append('=== what is in "1st Floor Electrical Plan"')
for v in FEC(doc).OfClass(View):
    if v.IsTemplate or v.Name != '1st Floor Electrical Plan': continue
    cnt = {}
    for e in FEC(doc, v.Id):
        k = e.Category.Name if e.Category else '(none)'
        cnt[k] = cnt.get(k, 0) + 1
    for k in sorted(cnt, key=lambda z: -cnt[z]):
        L.append('   %-32s %d' % (k, cnt[k]))
L.append('=== detail group types available')
for g in FEC(doc).OfClass(GroupType):
    try:
        cat = g.Category.Name if g.Category else '?'
        L.append('   %-40s (%s)' % (g.Name, cat))
    except Exception: pass
L.append('=== structural elements model-wide')
for label, bic in (('Structural Framing', BIC.OST_StructuralFraming),
                   ('Structural Foundations', BIC.OST_StructuralFoundation),
                   ('Structural Columns', BIC.OST_StructuralColumns)):
    n = FEC(doc).OfCategory(bic).WhereElementIsNotElementType().GetElementCount()
    L.append('   %-24s %d' % (label, n))
L.append('=== what is in "1st  Floor Framing Plan"')
for v in FEC(doc).OfClass(View):
    if v.IsTemplate or v.Name != '1st  Floor Framing Plan': continue
    cnt = {}
    for e in FEC(doc, v.Id):
        k = e.Category.Name if e.Category else '(none)'
        cnt[k] = cnt.get(k, 0) + 1
    for k in sorted(cnt, key=lambda z: -cnt[z])[:14]:
        L.append('   %-32s %d' % (k, cnt[k]))
result = '\n'.join(L)
