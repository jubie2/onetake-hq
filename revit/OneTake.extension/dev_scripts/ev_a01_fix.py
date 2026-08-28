# A01: rewrite header, scope, project data, building analysis, vicinity labels
# to the 6633 Electric Ave ADU facts.
from Autodesk.Revit.DB import ElementId
EDITS = {
 1132934: 'Steven Truong Residence- New ADU',
 1132935: '6633 Electric Ave\rLa Jolla, CA 92037',
 1132942: ('EXISTING 2-STORY SINGLE FAMILY RESIDENCE TO REMAIN.\r'
           'DEMOLISH EXISTING DETACHED GARAGE (~400 SF).\r'
           'PROPOSED NEW DETACHED TWO-STORY ADU BLDG\r'
           'W/ ATTACHED GARAGES AND ROOF DECK.'),
 1132943: ('BUILDING ANALYSIS:\r\r'
           'EXISTING RESIDENCE (2-STORY):\tTO REMAIN\r'
           'EXISTING DETACHED GARAGE:\t~400 SF (DEMOLISH)\r\r'
           'PROPOSED ADU BLDG:\r'
           '\t1ST FLOOR LIVING:\t900 SF\r'
           '\tGARAGE (2-CAR):\t228 SF\r'
           '\tGARAGE (1-CAR):\t222 SF\r'
           '\t2ND FLOOR LIVING:\t1,093 SF\r'
           '\t2ND FLOOR DECK:\t263 SF\r'
           '\tROOF DECK:\t\t1,148 SF\r\r'
           'TOTAL PROPOSED LIVING SF:\t1,993 SF'),
 1132948: ('PROJECT NAME:  STEVEN TRUONG RES - NEW ADU\r\r'
           'PROJECT ADDRESS:\t6633 Electric Ave.\r'
           '\t\tLa Jolla, CA 92037\r\r'
           'OWNER (Responsible for Water & Sewer Fees):\r'
           '\tSTEVEN TRUONG\r\r'
           'LEGAL DESCRIPTION: POR. LOT 10, HYMAN\'S ADDITION,\r'
           '\tMAP NO. 1808, DOC NO. 2019-0311700\r\r'
           'ZONE:\t\t-\r\r'
           'PARCEL NUMBER:\t351-493-10\r\r'
           'YEAR OF BUILT:\t-\r\r'
           'EXISTING BLDG FIRE SPRINKLER:\tNO\r\r'
           'COASTAL ZONE:\tYES'),
 1775447: 'ELECTRIC AVE.',
 1775398: 'LA JOLLA BLVD.',
 1599778: 'COLIMA ST.',
}
L = []
t = Transaction(doc, 'OneTake: A01 Electric Ave'); _prep(t); t.Start()
for eid, txt in EDITS.items():
    e = doc.GetElement(ElementId(eid))
    if e is None: L.append('%d MISSING' % eid); continue
    e.Text = txt
    L.append('%d ok' % eid)
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
