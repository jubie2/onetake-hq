# Replace drawn keynote bubbles (leader line + 2 arcs + digit TextNote) with the
# office's TAG LABEL generic-annotation family (TEXT param = number), matching what
# Francis placed by hand on ADU - West Elevation. One family -> easy to relocate.
# args {"views":["ADU - North Elevation"],"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, TextNote,
                               CurveElement, Arc, Line, FamilySymbol, FamilyInstance,
                               BuiltInParameter as BIP, ElementId, XYZ as _XYZ,
                               BuiltInCategory as BIC)
from System.Collections.Generic import List
import re
dry = args.get('dry', True)
views = args.get('views', [])
R = 0.55
sym = None
for s in FEC(doc).OfClass(FamilySymbol).OfCategory(BIC.OST_GenericAnnotation):
    if s.Family.Name == 'TAG LABEL': sym = s; break
if sym is None:
    result = 'TAG LABEL family not found'
else:
    L = ['symbol id %s active %s' % (sym.Id.Value, sym.IsActive)]
    for nm in views:
        v = None
        for x in FEC(doc).OfClass(View):
            if not x.IsTemplate and x.Name == nm: v = x; break
        if v is None:
            L.append('%s NOT FOUND' % nm); continue
        arcs = []; lines = []; notes = []
        for e in FEC(doc, v.Id).WhereElementIsNotElementType():
            if isinstance(e, CurveElement):
                c = e.GeometryCurve
                if isinstance(c, Arc) and abs(c.Radius - R) < 0.05:
                    arcs.append((e.Id, c.Center))
                elif isinstance(c, Line):
                    lines.append((e.Id, c.GetEndPoint(0), c.GetEndPoint(1)))
            elif isinstance(e, TextNote):
                m = re.match(r'^\s*(\d)\s*$', (e.Text or '').replace('\r', ' ').replace('/', ' '))
                if m: notes.append((e.Id, m.group(1), e.Coord))
        # group arcs into bubbles by center
        centers = []
        for aid, c in arcs:
            hit = None
            for grp in centers:
                if grp['c'].DistanceTo(c) < 0.1: hit = grp; break
            if hit is None:
                centers.append({'c': c, 'ids': [aid]})
            else:
                hit['ids'].append(aid)
        jobs = []; kill = []
        for grp in centers:
            c = grp['c']; kill.extend(grp['ids'])
            best = None; bd = 1e9
            for nid, digit, p in notes:
                d = p.DistanceTo(c)
                if d < bd: bd = d; best = (nid, digit)
            if best is None or bd > 1.5:
                L.append('  bubble at (%.1f,%.1f,%.1f) - no digit note within 1.5' %
                         (c.X, c.Y, c.Z)); continue
            kill.append(best[0])
            jobs.append((best[1], c))
            for lid, p0, p1 in lines:      # leader touching the circle
                if min(p0.DistanceTo(c), p1.DistanceTo(c)) < R + 0.35:
                    if lid not in kill: kill.append(lid)
        L.append('%-26s %d bubbles -> tags %s, deleting %d elems' % (
            nm, len(jobs), ','.join(j[0] for j in jobs), len(kill)))
        if dry: continue
        t = Transaction(doc, 'OneTake: bubbles -> TAG LABEL'); _prep(t); t.Start()
        if not sym.IsActive:
            sym.Activate(); doc.Regenerate()
        n = 0
        for digit, c in jobs:
            try:
                fi = doc.Create.NewFamilyInstance(c, sym, v)
                p = fi.LookupParameter('TEXT')
                if p: p.Set(digit)
                n += 1
            except Exception as ex:
                L.append('  place %s FAIL %s' % (digit, str(ex)[:60]))
        if kill:
            doc.Delete(List[ElementId](kill))
        doc.Regenerate(); t.Commit()
        L.append('    placed %d tags, deleted %d' % (n, len(kill)))
    result = '\n'.join(L)
