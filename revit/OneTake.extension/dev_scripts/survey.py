# Survey a doc for sheet-building: views, sheets, titleblocks, levels, crops, view templates.
from Autodesk.Revit.DB import (View, ViewSheet, ViewPlan, ViewSection, View3D, ViewDrafting,
                               FamilySymbol, BuiltInCategory, Level, ElementType, BuiltInParameter,
                               ViewFamilyType, ViewFamily)
import math
L = []
L.append('DOC: %s' % doc.Title)
L.append('PATH: %s' % doc.PathName)
lv = sorted(FilteredElementCollector(doc).OfClass(Level), key=lambda l: l.Elevation)
L.append('LEVELS (%d): %s' % (len(lv), ', '.join('%s@%.2f' % (l.Name, l.Elevation) for l in lv)))
sheets = list(FilteredElementCollector(doc).OfClass(ViewSheet))
L.append('SHEETS (%d):' % len(sheets))
for s in sorted(sheets, key=lambda s: s.SheetNumber)[:30]:
    try:
        n = len(list(s.GetAllPlacedViews()))
    except Exception:
        n = -1
    L.append('   %-10s %-42s  views=%d' % (s.SheetNumber, s.Name[:42], n))
tb = [t for t in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsElementType()]
L.append('TITLEBLOCK TYPES (%d):' % len(tb))
for t in tb[:12]:
    L.append('   %-9s %s : %s' % (t.Id.Value, t.FamilyName[:28],
             t.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()))
vfts = {}
for v in FilteredElementCollector(doc).OfClass(ViewFamilyType):
    vfts.setdefault(str(v.ViewFamily), []).append((v.Id.Value, v.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()))
L.append('VIEW FAMILY TYPES: %s' % ', '.join('%s=%d' % (k, len(v)) for k, v in sorted(vfts.items())))
byt = {}
for v in FilteredElementCollector(doc).OfClass(View):
    if v.IsTemplate: continue
    byt.setdefault(str(v.ViewType), []).append(v)
L.append('VIEWS BY TYPE: %s' % ', '.join('%s=%d' % (k, len(v)) for k, v in sorted(byt.items())))
for t in ('FloorPlan', 'CeilingPlan', 'Elevation', 'Section', 'ThreeD', 'DraftingView', 'Legend', 'AreaPlan'):
    for v in byt.get(t, [])[:14]:
        try:
            bb = v.CropBox; tf = bb.Transform
            p0 = tf.OfPoint(bb.Min); p1 = tf.OfPoint(bb.Max)
            ang = math.degrees(math.atan2(tf.BasisX.Y, tf.BasisX.X))
            geo = 'crop%s rot=%5.1f x %8.1f..%8.1f y %8.1f..%8.1f (%.0fx%.0f)' % (
                'ON ' if v.CropBoxActive else 'off', ang, min(p0.X,p1.X), max(p0.X,p1.X),
                min(p0.Y,p1.Y), max(p0.Y,p1.Y), abs(bb.Max.X-bb.Min.X), abs(bb.Max.Y-bb.Min.Y))
        except Exception:
            geo = ''
        try: sn = v.get_Parameter(BuiltInParameter.VIEWER_SHEET_NUMBER).AsString() or '-'
        except Exception: sn = '-'
        L.append('  %-13s %-9s %-34s sheet=%-7s %s' % (t, v.Id.Value, v.Name[:34], sn, geo))
result = '\n'.join(L)
