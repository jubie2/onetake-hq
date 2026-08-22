from Autodesk.Revit.DB import FilteredElementCollector as FEC, View, ViewPlan
L = []
for v in FEC(doc).OfClass(ViewPlan):
    if v.IsTemplate: continue
    if not (v.Name.startswith('ADU - ') or 'Electric' in v.Name or 'Mechanical' in v.Name): continue
    try: lv = v.GenLevel.Name if v.GenLevel else '?'
    except Exception: lv = '?'
    L.append('%-34s lvl %-18s scale %s cropOn %s' % (v.Name[:34], lv, v.Scale, v.CropBoxActive))
result = '\n'.join(sorted(L))
