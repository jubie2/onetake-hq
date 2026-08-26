# Rebuild TAG LABEL keynote tags in a view: wipe existing, place new ones with a
# bent leader arrow (like Francis's hand-placed West/South exemplars).
# args {"view":"ADU - North Elevation","wipe":true,
#       "tags":[{"n":"1","pt":[x,y,z],"elbow":[x,y,z],"end":[x,y,z]}]}
#   or {"view":"West Elev.","wipe":true,"copy_from":"ADU - West Elevation"}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, FamilySymbol,
                               BuiltInCategory as BIC, ElementId, XYZ as _XYZ)
from System.Collections.Generic import List
def getview(nm):
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: return x
    return None
def leaders_of(e):
    try: return list(e.GetLeaders())
    except Exception:
        out = []
        try:
            la = e.Leaders
            for i in range(la.Size): out.append(la.get_Item(i))
        except Exception: pass
        return out
v = getview(args['view'])
if v is None:
    result = 'view not found: %s' % args['view']
else:
    L = ['view %s' % args['view']]
    sym = None
    for s in FEC(doc).OfClass(FamilySymbol).OfCategory(BIC.OST_GenericAnnotation):
        if s.Family.Name == 'TAG LABEL': sym = s; break
    tags = args.get('tags', [])
    src = args.get('copy_from')
    if src:
        sv = getview(src)
        tags = []
        for e in FEC(doc, sv.Id).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
            if e.Symbol.Family.Name != 'TAG LABEL': continue
            pt = e.Location.Point
            p = e.LookupParameter('TEXT')
            spec = {'n': p.AsString() if p else '', 'pt': [pt.X, pt.Y, pt.Z]}
            lds = leaders_of(e)
            if lds:
                try:
                    en = lds[0].End; el = lds[0].Elbow
                    spec['end'] = [en.X, en.Y, en.Z]
                    spec['elbow'] = [el.X, el.Y, el.Z]
                except Exception: pass
            tags.append(spec)
        L.append('copied %d specs from %s' % (len(tags), src))
    placed = []
    t = Transaction(doc, 'OneTake: retag %s' % args['view']); _prep(t); t.Start()
    if args.get('wipe', True):
        kill = []
        for e in FEC(doc, v.Id).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
            if e.Symbol.Family.Name == 'TAG LABEL': kill.append(e.Id)
        if kill: doc.Delete(List[ElementId](kill))
        L.append('wiped %d old tags' % len(kill))
    if not sym.IsActive:
        sym.Activate(); doc.Regenerate()
    n = 0
    for spec in tags:
        try:
            pt = _XYZ(*[float(q) for q in spec['pt']])
            fi = doc.Create.NewFamilyInstance(pt, sym, v)
            p = fi.LookupParameter('TEXT')
            if p: p.Set(spec['n'])
            doc.Regenerate()
            e = doc.GetElement(fi.Id)
            if spec.get('end'):
                try:
                    e.addLeader()
                    doc.Regenerate()
                    lds = leaders_of(e)
                    if lds:
                        ld = lds[-1]
                        ld.End = _XYZ(*[float(q) for q in spec['end']])
                        if spec.get('elbow'):
                            ld.Elbow = _XYZ(*[float(q) for q in spec['elbow']])
                except Exception as ex:
                    L.append('  %s leader FAIL %s' % (spec['n'], str(ex)[:60]))
            placed.append((fi.Id, spec['n']))
            n += 1
        except Exception as ex:
            L.append('  %s place FAIL %s' % (spec['n'], str(ex)[:70]))
    doc.Regenerate()
    # setting TEXT right after NewFamilyInstance does not always stick -
    # re-set on the regenerated elements and verify
    for eid, num in placed:
        e2 = doc.GetElement(eid)
        p2 = e2.LookupParameter('TEXT')
        if p2 and p2.AsString() != num:
            ok = p2.Set(num)
            L.append('  re-set %s -> %s' % (num, ok))
    doc.Regenerate(); t.Commit()
    bad = []
    for eid, num in placed:
        p3 = doc.GetElement(eid).LookupParameter('TEXT')
        got = p3.AsString() if p3 else None
        if got != num: bad.append('%s got %s' % (num, got))
    L.append('placed %d tags%s' % (n, ('  BAD: ' + ', '.join(bad)) if bad else ', all TEXT verified'))
    result = '\n'.join(L)
