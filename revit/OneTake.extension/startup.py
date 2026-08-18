# -*- coding: utf-8 -*-
"""OneTake routes API — typed verb layer for driving Revit from Claude.

IronPython 2.7 ONLY. No f-strings, print is a statement.
Registered at pyRevit startup; edit -> RELOAD pyRevit -> curl to test.

Smoke test:
    curl http://localhost:48884/onetake-v1/status
"""
from pyrevit import routes, HOST_APP
from pyrevit import versionmgr

from Autodesk.Revit.DB import (
    Transaction,
    Level,
    Wall,
    WallType,
    Line,
    XYZ,
    FilteredElementCollector,
    BuiltInParameter,
    ElementId,
    FamilySymbol,
    Options,
    Solid,
    PlanarFace,
    ReferenceArray,
    ViewPlan,
    UV,
    LinkElementId,
    SketchPlane,
    Plane,
    CurveArray,
    ElementTransformUtils,
    LocationCurve,
)
from Autodesk.Revit.DB.Structure import StructuralType
import math

api = routes.API('onetake-v1')

MM_TO_FT = 1.0 / 304.8


def _err(message, status=400):
    """JSON error the calling agent can actually read."""
    return routes.make_response(data={'ok': False, 'error': message}, status=status)


def _get_level(doc, name):
    for lvl in FilteredElementCollector(doc).OfClass(Level):
        if lvl.Name == name:
            return lvl
    return None


def _get_wall_type(doc, name):
    for wt in FilteredElementCollector(doc).OfClass(WallType):
        if wt.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString() == name:
            return wt
    return None




# ── Failure handling: never let a warning dialog block the API ──
from Autodesk.Revit.DB import (IFailuresPreprocessor, FailureProcessingResult,
                               FailureSeverity)


class _SwallowWarnings(IFailuresPreprocessor):
    """Delete warnings; auto-resolve errors that offer a resolution."""
    def PreprocessFailures(self, fa):
        resolved = False
        for f in fa.GetFailureMessages():
            sev = f.GetSeverity()
            if sev == FailureSeverity.Warning:
                fa.DeleteWarning(f)
            elif f.HasResolutions():
                fa.ResolveFailure(f)
                resolved = True
        if resolved:
            return FailureProcessingResult.ProceedWithCommit
        return FailureProcessingResult.Continue


def _prep(t):
    """Attach the warning-swallowing preprocessor to a Transaction."""
    try:
        opts = t.GetFailureHandlingOptions()
        opts.SetFailuresPreprocessor(_SwallowWarnings())
        opts.SetClearAfterRollback(True)
        t.SetFailureHandlingOptions(opts)
    except Exception:
        pass

# ── Read-only verbs ──────────────────────────────────────────────

@api.route('/status', methods=['GET'])
def status():
    """Is the server alive, what are we attached to."""
    return {
        'ok': True,
        'revit_version': HOST_APP.version,
        'revit_build': HOST_APP.build,
        'pyrevit_version': versionmgr.get_pyrevit_version().get_formatted(),
    }


@api.route('/doc', methods=['GET'])
def doc_info(doc):
    """Active document + the levels and wall types verbs can target."""
    if doc is None:
        return _err('No active document. Open a project in Revit first.', 409)
    levels = [{'name': l.Name, 'elevation_ft': l.Elevation}
              for l in FilteredElementCollector(doc).OfClass(Level)]
    wall_types = [wt.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
                  for wt in FilteredElementCollector(doc).OfClass(WallType)]
    return {
        'ok': True,
        'title': doc.Title,
        'levels': levels,
        'wall_types': wall_types,
    }


# ── Model-changing verbs ─────────────────────────────────────────

@api.route('/levels', methods=['POST'])
def create_level(doc, request):
    """Create a level.

    Body: {"name": "Level 3", "elevation_ft": 20.0}
    """
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    name = data.get('name')
    elevation = data.get('elevation_ft')
    if not name or elevation is None:
        return _err('Required: name (str), elevation_ft (number).')
    if _get_level(doc, name):
        return _err('Level "{}" already exists.'.format(name), 409)

    t = Transaction(doc, 'OneTake: create level {}'.format(name))
    _prep(t)
    t.Start()
    try:
        lvl = Level.Create(doc, float(elevation))
        lvl.Name = name
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error: {}'.format(ex), 500)
    return {'ok': True, 'id': lvl.Id.Value, 'name': name, 'elevation_ft': float(elevation)}


@api.route('/walls', methods=['POST'])
def create_walls(doc, request):
    """Create walls along a polyline. ALL UNITS DECIMAL FEET.

    Body: {
        "points": [[0,0], [30,0], [30,20], [0,20]],   # feet, in order
        "closed": true,                                # join last -> first
        "level": "Level 1",
        "height_ft": 10.0,
        "wall_type": null                              # optional; doc default if null
    }
    """
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    points = data.get('points')
    level_name = data.get('level')
    height = data.get('height_ft')
    if not points or len(points) < 2:
        return _err('Required: points, a list of at least 2 [x, y] pairs in FEET.')
    if not level_name or height is None:
        return _err('Required: level (str), height_ft (number).')

    level = _get_level(doc, level_name)
    if level is None:
        return _err('Level "{}" not found. GET /onetake-v1/doc lists levels.'.format(level_name), 404)

    wall_type_id = None
    type_name = data.get('wall_type')
    if type_name:
        wt = _get_wall_type(doc, type_name)
        if wt is None:
            return _err('WallType "{}" not found. GET /onetake-v1/doc lists types.'.format(type_name), 404)
        wall_type_id = wt.Id

    pts = [XYZ(float(p[0]), float(p[1]), 0.0) for p in points]
    pairs = zip(pts, pts[1:])
    if data.get('closed') and len(pts) > 2:
        pairs = pairs + [(pts[-1], pts[0])]

    created = []
    t = Transaction(doc, 'OneTake: create {} walls'.format(len(pairs)))
    _prep(t)
    t.Start()
    try:
        for start, end in pairs:
            if start.DistanceTo(end) < 0.01:  # degenerate segment, feet
                continue
            line = Line.CreateBound(start, end)
            if wall_type_id:
                # typed overload: works for Basic AND Curtain wall types
                wall = Wall.Create(doc, line, wall_type_id, level.Id,
                                   float(height), 0.0, False, False)
            else:
                wall = Wall.Create(doc, line, level.Id, False)
                hp = wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM)
                if hp:
                    hp.Set(float(height))
            created.append(wall.Id.Value)
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'wall_ids': created, 'count': len(created)}


@api.route('/delete', methods=['POST'])
def delete_elements(doc, request):
    """Delete elements by explicit ElementId list. One transaction; undoable.

    Body: {"ids": [4977585, 4977586]}
    Returns which ids were deleted (incl. dependents Revit removed) and
    which were not found. Refuses an empty list.
    """
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    ids = data.get('ids')
    if not ids or not isinstance(ids, list):
        return _err('Required: ids, a non-empty list of element ids.')

    found, missing = [], []
    for raw in ids:
        try:
            eid = ElementId(long(raw))
        except (ValueError, TypeError):
            return _err('Bad element id: {}'.format(raw))
        if doc.GetElement(eid) is None:
            missing.append(raw)
        else:
            found.append(eid)
    if not found:
        return _err('None of the ids exist in this document.', 404)

    deleted = []
    t = Transaction(doc, 'OneTake: delete {} elements'.format(len(found)))
    _prep(t)
    t.Start()
    try:
        for eid in found:
            for did in doc.Delete(eid):
                deleted.append(did.Value)
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'deleted_ids': deleted, 'count': len(deleted),
            'not_found': missing}


# ── Helpers for annotation / placement verbs ─────────────────────

def _plan_view(doc, level, view_name=None):
    """A non-template floor plan for `level` (active view preferred)."""
    if view_name:
        for v in FilteredElementCollector(doc).OfClass(ViewPlan):
            if not v.IsTemplate and v.Name == view_name:
                return v
        return None
    av = doc.ActiveView
    if isinstance(av, ViewPlan) and not av.IsTemplate and \
            av.GenLevel is not None and av.GenLevel.Id == level.Id:
        return av
    for v in FilteredElementCollector(doc).OfClass(ViewPlan):
        if v.IsTemplate or v.GenLevel is None:
            continue
        if v.GenLevel.Id == level.Id and str(v.ViewType) == 'FloorPlan':
            return v
    return None


def _wall_line(wall):
    loc = wall.Location
    if not isinstance(loc, LocationCurve):
        return None
    return loc.Curve


def _planar_faces(wall):
    """[(normal XYZ, origin XYZ, Reference)] for every planar face."""
    opt = Options()
    opt.ComputeReferences = True
    opt.IncludeNonVisibleObjects = False
    out = []
    geo = wall.get_Geometry(opt)
    if geo is None:
        return out
    for g in geo:
        if isinstance(g, Solid):
            for f in g.Faces:
                if isinstance(f, PlanarFace) and f.Reference is not None:
                    out.append((f.FaceNormal, f.Origin, f.Reference))
    return out


def _fmt_ft(v):
    ft = int(math.floor(v))
    inch = (v - ft) * 12.0
    return "{}'-{:.1f}in".format(ft, inch)


# ── Read-only: walls readback ────────────────────────────────────

@api.route('/walls', methods=['GET'])
def list_walls(doc):
    """Every wall: id, type, level, start/end (ft), length (ft + ft-in)."""
    if doc is None:
        return _err('No active document.', 409)
    out = []
    for w in FilteredElementCollector(doc).OfClass(Wall):
        c = _wall_line(w)
        if c is None:
            continue
        p0, p1 = c.GetEndPoint(0), c.GetEndPoint(1)
        lvl = doc.GetElement(w.LevelId)
        out.append({
            'id': w.Id.Value,
            'type': w.WallType.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString(),
            'level': lvl.Name if lvl else None,
            'start': [round(p0.X, 3), round(p0.Y, 3)],
            'end': [round(p1.X, 3), round(p1.Y, 3)],
            'length_ft': round(c.Length, 3),
            'length_ftin': _fmt_ft(c.Length),
        })
    return {'ok': True, 'count': len(out), 'walls': out}


# ── Read-only: loaded family types ───────────────────────────────

@api.route('/families', methods=['GET'])
def list_families(doc, request):
    """Loaded FamilySymbols. Optional ?category=Doors (substring, case-insens)."""
    if doc is None:
        return _err('No active document.', 409)
    want = None
    try:
        want = (request.params or {}).get('category')
    except Exception:
        want = None
    out = []
    for fs in FilteredElementCollector(doc).OfClass(FamilySymbol):
        cat = fs.Category.Name if fs.Category else ''
        if want and want.lower() not in cat.lower():
            continue
        out.append({'id': fs.Id.Value, 'category': cat,
                    'family': fs.FamilyName,
                    'type': fs.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()})
    out.sort(key=lambda d: (d['category'], d['family'], d['type']))
    return {'ok': True, 'count': len(out), 'symbols': out}


@api.route('/load-family', methods=['POST'])
def load_family(doc, request):
    """Body: {"path": "C:/families/Range.rfa"} -> loads .rfa into the doc."""
    if doc is None:
        return _err('No active document.', 409)
    path = (request.data or {}).get('path')
    if not path:
        return _err('Required: path to an .rfa file.')
    t = Transaction(doc, 'OneTake: load family')
    _prep(t)
    t.Start()
    try:
        ok = doc.LoadFamily(path)
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error: {}'.format(ex), 500)
    return {'ok': bool(ok), 'loaded': bool(ok), 'path': path}


# ── Place family instances (doors/windows hosted, or free-standing) ─

@api.route('/place', methods=['POST'])
def place_instances(doc, request):
    """Body: {"level": "1st Floor Level", "items": [
         {"symbol_id": 123, "x": 10, "y": 5, "rotation_deg": 90,
          "host_wall_id": 4977589,   # doors/windows; auto-nearest if omitted
          "label": "cashier"}]}   ALL UNITS FEET.
    Hosted categories (Doors/Windows) are snapped onto the host wall line.
    """
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    items = data.get('items') or []
    level = _get_level(doc, data.get('level') or '')
    if level is None or not items:
        return _err('Required: level (existing name), items (non-empty list).')

    walls = [w for w in FilteredElementCollector(doc).OfClass(Wall)
             if _wall_line(w) is not None]

    def nearest_wall(pt):
        best, bd = None, 1e9
        for w in walls:
            d = _wall_line(w).Distance(pt)
            if d < bd:
                best, bd = w, d
        return best, bd

    placed, errors = [], []
    t = Transaction(doc, 'OneTake: place {} instances'.format(len(items)))
    _prep(t)
    t.Start()
    try:
        for i, it in enumerate(items):
            try:
                sym = doc.GetElement(ElementId(long(it['symbol_id'])))
                if not isinstance(sym, FamilySymbol):
                    errors.append({'i': i, 'error': 'symbol_id is not a FamilySymbol'})
                    continue
                if not sym.IsActive:
                    sym.Activate()
                    doc.Regenerate()
                pt = XYZ(float(it['x']), float(it['y']), level.Elevation)
                cat = sym.Category.Name if sym.Category else ''
                hosted = cat in ('Doors', 'Windows') or it.get('host_wall_id')
                if hosted:
                    if it.get('host_wall_id'):
                        host = doc.GetElement(ElementId(long(it['host_wall_id'])))
                    else:
                        host, dist = nearest_wall(pt)
                        if host is None or dist > 3.0:
                            errors.append({'i': i, 'error': 'no wall within 3 ft to host'})
                            continue
                    pt = _wall_line(host).Project(pt).XYZPoint
                    pt = XYZ(pt.X, pt.Y, level.Elevation)
                    inst = doc.Create.NewFamilyInstance(pt, sym, host, level,
                                                        StructuralType.NonStructural)
                else:
                    inst = doc.Create.NewFamilyInstance(pt, sym, level,
                                                        StructuralType.NonStructural)
                    rot = float(it.get('rotation_deg') or 0)
                    if abs(rot) > 1e-6:
                        axis = Line.CreateBound(pt, pt + XYZ.BasisZ)
                        ElementTransformUtils.RotateElement(doc, inst.Id, axis,
                                                            math.radians(rot))
                placed.append({'i': i, 'id': inst.Id.Value,
                               'label': it.get('label'), 'category': cat})
            except Exception as ex:
                errors.append({'i': i, 'label': it.get('label'), 'error': str(ex)})
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'placed': placed, 'errors': errors,
            'count': len(placed)}


# ── Rooms + tags ────────────────────────────────────────────────

@api.route('/room-lines', methods=['POST'])
def room_lines(doc, request):
    """Room separation lines. Body: {"level": "...", "lines": [[[x1,y1],[x2,y2]], ...]}"""
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    level = _get_level(doc, data.get('level') or '')
    lines = data.get('lines') or []
    if level is None or not lines:
        return _err('Required: level, lines (list of [[x1,y1],[x2,y2]]).')
    view = _plan_view(doc, level, data.get('view'))
    if view is None:
        return _err('No floor plan view found for level.', 404)
    t = Transaction(doc, 'OneTake: room separation lines')
    _prep(t)
    t.Start()
    try:
        z = level.Elevation
        sp = SketchPlane.Create(doc, Plane.CreateByNormalAndOrigin(XYZ.BasisZ, XYZ(0, 0, z)))
        ca = CurveArray()
        for a, b in lines:
            ca.Append(Line.CreateBound(XYZ(float(a[0]), float(a[1]), z),
                                       XYZ(float(b[0]), float(b[1]), z)))
        made = doc.Create.NewRoomBoundaryLines(sp, ca, view)
        ids = [e.Id.Value for e in made]
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'ids': ids, 'count': len(ids)}


@api.route('/rooms', methods=['POST'])
def create_rooms(doc, request):
    """Body: {"level": "...", "rooms": [{"name": "Kitchen", "x": 50, "y": 20}], "tag": true}"""
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    level = _get_level(doc, data.get('level') or '')
    rooms = data.get('rooms') or []
    if level is None or not rooms:
        return _err('Required: level, rooms (non-empty list of {name,x,y}).')
    view = _plan_view(doc, level, data.get('view'))
    want_tag = data.get('tag', True)
    if want_tag and view is None:
        return _err('No floor plan view found for level (needed for tags).', 404)
    made, errors = [], []
    t = Transaction(doc, 'OneTake: create {} rooms'.format(len(rooms)))
    _prep(t)
    t.Start()
    try:
        for i, r in enumerate(rooms):
            try:
                uv = UV(float(r['x']), float(r['y']))
                room = doc.Create.NewRoom(level, uv)
                room.get_Parameter(BuiltInParameter.ROOM_NAME).Set(
                    str(r.get('name') or 'Room'))
                if r.get('number'):
                    room.get_Parameter(BuiltInParameter.ROOM_NUMBER).Set(
                        str(r['number']))
                tag_id = None
                if want_tag:
                    tag = doc.Create.NewRoomTag(LinkElementId(room.Id), uv, view.Id)
                    tag_id = tag.Id.Value
                made.append({'i': i, 'room_id': room.Id.Value, 'tag_id': tag_id,
                             'name': room.Name,
                             'area_sf': round(room.Area, 1)})
            except Exception as ex:
                errors.append({'i': i, 'name': r.get('name'), 'error': str(ex)})
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'rooms': made, 'errors': errors, 'count': len(made)}


# ── Dimensions ──────────────────────────────────────────────────

@api.route('/dimensions', methods=['POST'])
def create_dimensions(doc, request):
    """Linear dimensions in a plan view. ALL UNITS FEET.
    Body: {"level": "...", "view": null,
           "lengths":  [{"wall_id": 1, "offset_ft": 3.0}],          # wall end-to-end
           "between":  [{"wall_a": 1, "wall_b": 2, "axis": "x", "at": -4.0}]}
    offset_ft > 0 = left of the wall's draw direction.
    'between' measures the facing side-faces of two walls along axis x|y,
    with the dimension line at coordinate `at` on the other axis.
    """
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    level = _get_level(doc, data.get('level') or '')
    if level is None:
        return _err('Required: level (existing name).')
    view = _plan_view(doc, level, data.get('view'))
    if view is None:
        return _err('No floor plan view found for level.', 404)
    z = level.Elevation
    made, errors = [], []
    t = Transaction(doc, 'OneTake: dimensions')
    _prep(t)
    t.Start()
    try:
        for i, d in enumerate(data.get('lengths') or []):
            try:
                w = doc.GetElement(ElementId(long(d['wall_id'])))
                c = _wall_line(w)
                p0, p1 = c.GetEndPoint(0), c.GetEndPoint(1)
                dirv = (p1 - p0).Normalize()
                side = XYZ(-dirv.Y, dirv.X, 0)
                cands = []
                for n, o, ref in _planar_faces(w):
                    if abs(n.Z) > 0.5 or abs(n.DotProduct(side)) > 0.95:
                        continue  # top/bottom or side faces
                    cands.append(((o - p0).DotProduct(dirv), ref))
                if len(cands) < 2:
                    errors.append({'i': i, 'wall_id': d['wall_id'],
                                   'error': 'end faces not found'})
                    continue
                cands.sort(key=lambda x: x[0])
                ra = ReferenceArray()
                ra.Append(cands[0][1])
                ra.Append(cands[-1][1])
                off = float(d.get('offset_ft', 3.0))
                a = XYZ(p0.X, p0.Y, z) + side * off
                b = XYZ(p1.X, p1.Y, z) + side * off
                dim = doc.Create.NewDimension(view, Line.CreateBound(a, b), ra)
                made.append({'i': i, 'id': dim.Id.Value, 'wall_id': d['wall_id'],
                             'value_ft': round(dim.Value, 3) if dim.Value else None})
            except Exception as ex:
                errors.append({'i': i, 'wall_id': d.get('wall_id'), 'error': str(ex)})

        for i, d in enumerate(data.get('between') or []):
            try:
                axis = XYZ.BasisX if str(d.get('axis', 'x')).lower() == 'x' else XYZ.BasisY
                wa = doc.GetElement(ElementId(long(d['wall_a'])))
                wb = doc.GetElement(ElementId(long(d['wall_b'])))
                ca_, cb_ = _wall_line(wa), _wall_line(wb)
                pa = ca_.Evaluate(0.5, True).DotProduct(axis)
                pb = cb_.Evaluate(0.5, True).DotProduct(axis)

                far = bool(d.get('far', False))

                def pick(w, toward):
                    best, bd = None, (-1.0 if far else 1e9)
                    for n, o, ref in _planar_faces(w):
                        if abs(n.DotProduct(axis)) < 0.99:
                            continue
                        dist = abs(o.DotProduct(axis) - toward)
                        better = (dist > bd) if far else (dist < bd)
                        if better:
                            best, bd = (o.DotProduct(axis), ref), dist
                    return best
                fa = pick(wa, pb)
                fb = pick(wb, pa)
                if fa is None or fb is None:
                    errors.append({'i': i, 'error': 'faces along axis not found'})
                    continue
                at = float(d.get('at', 0.0))
                if axis.X == 1:
                    a, b = XYZ(fa[0], at, z), XYZ(fb[0], at, z)
                else:
                    a, b = XYZ(at, fa[0], z), XYZ(at, fb[0], z)
                ra = ReferenceArray()
                ra.Append(fa[1])
                ra.Append(fb[1])
                dim = doc.Create.NewDimension(view, Line.CreateBound(a, b), ra)
                made.append({'i': i, 'id': dim.Id.Value, 'between': [d['wall_a'], d['wall_b']],
                             'value_ft': round(dim.Value, 3) if dim.Value else None})
            except Exception as ex:
                errors.append({'i': i, 'error': str(ex)})
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'dimensions': made, 'errors': errors, 'count': len(made)}


@api.route('/rooms', methods=['GET'])
def list_rooms(doc):
    """All rooms: id, name, number, level, area_sf."""
    if doc is None:
        return _err('No active document.', 409)
    from Autodesk.Revit.DB import BuiltInCategory
    out = []
    coll = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms)
    for r in coll:
        try:
            lvl = doc.GetElement(r.LevelId) if r.LevelId else None
            out.append({'id': r.Id.Value,
                        'name': r.get_Parameter(BuiltInParameter.ROOM_NAME).AsString(),
                        'number': r.get_Parameter(BuiltInParameter.ROOM_NUMBER).AsString(),
                        'level': lvl.Name if lvl else None,
                        'area_sf': round(r.Area, 1)})
        except Exception as ex:
            out.append({'id': r.Id.Value, 'error': str(ex)})
    return {'ok': True, 'count': len(out), 'rooms': out}


@api.route('/room-tags', methods=['POST'])
def tag_rooms(doc, request):
    """Tag rooms that have no tag in the plan view.
    Body: {"level": "...", "view": null, "room_ids": [..] (optional; default all on level)}"""
    if doc is None:
        return _err('No active document.', 409)
    from Autodesk.Revit.DB import BuiltInCategory
    from Autodesk.Revit.DB.Architecture import RoomTag
    data = request.data or {}
    level = _get_level(doc, data.get('level') or '')
    if level is None:
        return _err('Required: level.')
    view = _plan_view(doc, level, data.get('view'))
    if view is None:
        return _err('No floor plan view found for level.', 404)
    tagged_rooms = set()
    for tg in FilteredElementCollector(doc, view.Id).OfCategory(BuiltInCategory.OST_RoomTags):
        try:
            if tg.Room is not None:
                tagged_rooms.add(tg.Room.Id.Value)
        except Exception:
            pass
    want = data.get('room_ids')
    rooms = []
    for r in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms):
        if r.LevelId != level.Id or r.Area <= 0:
            continue
        if want and r.Id.Value not in [long(x) for x in want]:
            continue
        if r.Id.Value in tagged_rooms:
            continue
        rooms.append(r)
    made, errors = [], []
    t = Transaction(doc, 'OneTake: tag {} rooms'.format(len(rooms)))
    _prep(t)
    t.Start()
    try:
        for r in rooms:
            try:
                p = r.Location.Point
                uv = UV(p.X, p.Y)
                tag = doc.Create.NewRoomTag(LinkElementId(r.Id), uv, view.Id)
                made.append({'room_id': r.Id.Value, 'tag_id': tag.Id.Value,
                             'name': r.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()})
            except Exception as ex:
                errors.append({'room_id': r.Id.Value, 'error': repr(ex)})
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'tags': made, 'errors': errors, 'count': len(made),
            'view': view.Name, 'already_tagged': len(tagged_rooms)}


@api.route('/curtain-door', methods=['POST'])
def curtain_door(doc, request):
    """Swap the curtain panel nearest (x,y) on a curtain wall to a door/panel type.
    Body: {"wall_id": 123, "x": 50, "y": 0, "symbol_id": 4001162}  (feet)"""
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    try:
        wall = doc.GetElement(ElementId(long(data['wall_id'])))
        sym = doc.GetElement(ElementId(long(data['symbol_id'])))
        px, py = float(data['x']), float(data['y'])
    except Exception as ex:
        return _err('Required: wall_id, symbol_id, x, y. ({})'.format(ex))
    grid = getattr(wall, 'CurtainGrid', None)
    if grid is None:
        return _err('Wall {} is not a curtain wall.'.format(data['wall_id']))
    best, bd = None, 1e9
    for pid in grid.GetPanelIds():
        p = doc.GetElement(pid)
        bb = p.get_BoundingBox(None)
        if bb is None:
            continue
        c = (bb.Min + bb.Max) * 0.5
        dist = XYZ(c.X, c.Y, 0).DistanceTo(XYZ(px, py, 0))
        if dist < bd:
            best, bd = p, dist
    if best is None:
        return _err('No panels found on wall.', 404)
    t = Transaction(doc, 'OneTake: curtain door')
    _prep(t)
    t.Start()
    try:
        if not sym.IsActive:
            sym.Activate()
            doc.Regenerate()
        best.Pinned = False
        try:
            best.ChangeTypeId(sym.Id)
        except Exception:
            best.Symbol = sym
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'panel_id': best.Id.Value, 'distance_ft': round(bd, 2),
            'new_type': sym.FamilyName}


# ── Parameters + schedules ───────────────────────────────────────

def _set_param(el, name, value):
    p = el.LookupParameter(name)
    if p is None:
        return 'no param "{}"'.format(name)
    if p.IsReadOnly:
        return 'param "{}" read-only'.format(name)
    try:
        st = str(p.StorageType)
        if st == 'String':
            p.Set(str(value))
        elif st == 'Double':
            p.Set(float(value))
        elif st == 'Integer':
            p.Set(int(value))
        elif st == 'ElementId':
            p.Set(ElementId(long(value)))
        else:
            return 'unsupported storage {}'.format(st)
    except Exception as ex:
        return 'set "{}" failed: {}'.format(name, ex)
    return None


@api.route('/set-params', methods=['POST'])
def set_params(doc, request):
    """Body: {"items": [{"id": 123,
                         "instance": {"Mark": "01", "Comments": "EXISTING"},
                         "type": {"Description": "...", "Manufacturer": "...", "Model": "..."},
                         "dup_type_name": "HS-1615W"   # optional: duplicate the symbol first
                       }]}"""
    if doc is None:
        return _err('No active document.', 409)
    items = (request.data or {}).get('items') or []
    if not items:
        return _err('Required: items (non-empty list).')
    results = []
    t = Transaction(doc, 'OneTake: set params on {} elements'.format(len(items)))
    _prep(t)
    t.Start()
    try:
        for it in items:
            res = {'id': it.get('id'), 'warnings': []}
            try:
                el = doc.GetElement(ElementId(long(it['id'])))
                if el is None:
                    res['warnings'].append('element not found')
                    results.append(res)
                    continue
                dup = it.get('dup_type_name')
                if dup and hasattr(el, 'Symbol'):
                    newsym = None
                    for fs in FilteredElementCollector(doc).OfClass(FamilySymbol):
                        if fs.FamilyName == el.Symbol.FamilyName and \
                                fs.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString() == dup:
                            newsym = fs
                            break
                    if newsym is None:
                        newsym = el.Symbol.Duplicate(dup)
                    if not newsym.IsActive:
                        newsym.Activate()
                    el.Symbol = newsym
                    res['type_id'] = newsym.Id.Value
                for k, v in (it.get('instance') or {}).items():
                    w = _set_param(el, k, v)
                    if w:
                        res['warnings'].append(w)
                tp = it.get('type') or {}
                if tp:
                    sym = getattr(el, 'Symbol', None) or doc.GetElement(el.GetTypeId())
                    for k, v in tp.items():
                        w = _set_param(sym, k, v)
                        if w:
                            res['warnings'].append('type: ' + w)
            except Exception as ex:
                res['warnings'].append(str(ex))
            results.append(res)
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'results': results, 'count': len(results)}


def _schedule_rows(sched, max_rows=400):
    from Autodesk.Revit.DB import SectionType
    td = sched.GetTableData()
    rows = []
    for sec in (SectionType.Header, SectionType.Body):
        sd = td.GetSectionData(sec)
        if sd is None:
            continue
        for r in range(sd.NumberOfRows):
            row = []
            for c in range(sd.NumberOfColumns):
                try:
                    row.append(sched.GetCellText(sec, r, c))
                except Exception:
                    row.append('')
            rows.append(row)
            if len(rows) >= max_rows:
                return rows
    return rows


@api.route('/schedule', methods=['POST'])
def create_schedule(doc, request):
    """Create (or replace) a multi-category schedule.
    Body: {"name": "EQUIPMENT SCHEDULE",
           "fields": [{"param": "Mark", "heading": "ITEM"}, {"param": "Description"},
                      {"count": true, "heading": "QTY"}, {"param": "Manufacturer"},
                      {"param": "Model"}, {"param": "Comments", "heading": "STATUS"}],
           "filter": {"param": "Comments", "equals": "EXISTING"},
           "sort_by": "Mark", "itemize": false, "replace": true}
    param names: Mark, Description, Manufacturer, Model, Comments, Type Comments, Level, Family and Type..."""
    from Autodesk.Revit.DB import (ViewSchedule, BuiltInCategory, ScheduleFieldType,
                                   ScheduleFilter, ScheduleFilterType, ScheduleSortGroupField)
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    name = data.get('name') or 'OneTake Schedule'
    fields = data.get('fields') or []
    if not fields:
        return _err('Required: fields.')
    t = Transaction(doc, 'OneTake: schedule {}'.format(name))
    _prep(t)
    t.Start()
    try:
        if data.get('replace', False):
            # collect first: deleting while iterating invalidates the collector
            dup_ids = [v.Id for v in FilteredElementCollector(doc).OfClass(ViewSchedule)
                       if v.Name == name and not v.IsTemplate]
            for did in dup_ids:
                doc.Delete(did)
        cat = data.get('category')
        cat_id = ElementId(BuiltInCategory.INVALID)
        if cat:
            cat_id = ElementId(getattr(BuiltInCategory, cat))
        sched = ViewSchedule.CreateSchedule(doc, cat_id)
        sched.Name = name
        sdef = sched.Definition
        schedulable = list(sdef.GetSchedulableFields())
        by_name = {}
        count_sf = None
        for sf in schedulable:
            try:
                nm = sf.GetName(doc)
            except Exception:
                nm = None
            if sf.FieldType == ScheduleFieldType.Count:
                count_sf = sf
            if nm and nm not in by_name:
                by_name[nm] = sf
        added = {}
        missing = []
        for f in fields:
            if f.get('count'):
                sf = count_sf
            else:
                sf = by_name.get(f.get('param'))
            if sf is None:
                missing.append(f.get('param') or 'count')
                continue
            fld = sdef.AddField(sf)
            if f.get('heading'):
                fld.ColumnHeading = f['heading']
            if f.get('width_ft'):
                fld.GridColumnWidth = float(f['width_ft'])
            added[f.get('param') or 'count'] = fld
        flt = data.get('filter')
        if flt and flt.get('param') in added:
            sdef.AddFilter(ScheduleFilter(added[flt['param']].FieldId,
                                          ScheduleFilterType.Equal, str(flt['equals'])))
        sb = data.get('sort_by')
        if sb and sb in added:
            sdef.AddSortGroupField(ScheduleSortGroupField(added[sb].FieldId))
        sdef.IsItemized = bool(data.get('itemize', False))
        doc.Regenerate()
        rows = _schedule_rows(sched)
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'schedule_id': sched.Id.Value, 'name': name,
            'missing_fields': missing, 'available_fields': sorted(by_name.keys())[:80],
            'rows': rows}


@api.route('/schedule-read', methods=['POST'])
def read_schedule(doc, request):
    """Body: {"name": "EQUIPMENT SCHEDULE"} -> header + body rows as text."""
    from Autodesk.Revit.DB import ViewSchedule
    if doc is None:
        return _err('No active document.', 409)
    name = (request.data or {}).get('name')
    for v in FilteredElementCollector(doc).OfClass(ViewSchedule):
        if v.Name == name and not v.IsTemplate:
            return {'ok': True, 'schedule_id': v.Id.Value, 'rows': _schedule_rows(v)}
    return _err('Schedule "{}" not found.'.format(name), 404)


@api.route('/warnings', methods=['GET'])
def list_warnings(doc):
    """Model warnings (Manage > Warnings): description + failing element ids."""
    if doc is None:
        return _err('No active document.', 409)
    out = []
    for fm in doc.GetWarnings():
        try:
            out.append({'description': fm.GetDescriptionText(),
                        'severity': str(fm.GetSeverity()),
                        'element_ids': [e.Value for e in fm.GetFailingElements()],
                        'additional_ids': [e.Value for e in fm.GetAdditionalElements()]})
        except Exception as ex:
            out.append({'error': str(ex)})
    return {'ok': True, 'count': len(out), 'warnings': out}
