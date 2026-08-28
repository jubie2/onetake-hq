# Rewrite mechanical keynote legend for mini-split flat-roof design;
# drop the stale furnace schedule from A200.
from Autodesk.Revit.DB import ElementId
t = Transaction(doc, 'OneTake: mech legend'); _prep(t); t.Start()
e = doc.GetElement(ElementId(1183395))
e.Text = ('THERMOSTAT / CONTROLLER MOUNTED AT 5\'-0"\r\r'
          'DUCTLESS MINI-SPLIT INDOOR UNIT (WALL MTD)\r\r'
          'MINI-SPLIT CONDENSING UNIT ON CONC. PAD\r\r'
          'CEILING EXHAUST FAN (MIN. OF 75CFM) MIN. OF 4" DIA. DUCTED TO\rOUTSIDE\r\r'
          '4" DIA. DRYER EXHAUST DUCT TO OUTSIDE TOTAL OF TWO 90 DEGREE\rELBOWS MAXIMUM 14\' OF LENGTH\r\r'
          'DRYER EXHAUST DUCT TERMINATION LOCATION\r\r'
          'KITCHEN HOOD EXHAUST FAN (SEE SCHEDULE) WHICH  MIN. OF 250CFM\rFOR INTERMITTENT\r\r'
          '6" DIA. KITCHEN EXHAUST DUCT TO OUTSIDE BLDG\r\r'
          'KITCHEN EXHAUST DUCT TERMINATION LOCATION (PROVIDE W/ RAIN CAP)\r\r'
          'WATER HEATER P&T LINE TO OUTSIDE BLDG')
e2 = doc.GetElement(ElementId(1892507))
e2.Text = ('\r\rHEAT PUMP WATER HEATER PER SCHEDULE\r\r'
           'SMOKE DETECTOR, HARD-WIRED W/ BATTERY\r'
           'BACK-UP, INTERCONNECTED [CRC R314]\r\r'
           'CARBON MONOXIDE ALARM [CRC R315]\r\r'
           'IAQ (WHOLE BLDG VENT) EXHAUST FAN\r'
           '64 CFM MIN. CONTINUOUS\r')
try:
    doc.Delete(ElementId(1019353))
    ok = 'furnace schedule removed'
except Exception as ex:
    ok = 'furnace sched fail %s' % str(ex)[:40]
doc.Regenerate(); t.Commit()
result = 'legend rewritten; ' + ok
