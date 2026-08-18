# -*- coding: utf-8 -*-
"""Scratch dev script. Run with:
   curl -X POST localhost:48884/onetake-v1/dev/run -H "Content-Type: application/json" -d "{\"file\":\"scratch.py\"}"
Globals available: doc, uidoc, uiapp, args (dict from the request), result (set it for the response),
plus Transaction, _prep, FilteredElementCollector, ElementId, XYZ, HOST_APP.
IronPython 2.7: print statement, no f-strings."""
result = {'hello': 'world', 'doc_title': doc.Title if doc else None}
