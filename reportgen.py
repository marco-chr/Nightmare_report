# REPORT TEMPLATE NIGHTMARE REPORT

# IMPORT
from reportlab.lib.pagesizes import letter,A4
from reportlab.lib import utils
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm,mm
from reportlab.lib.enums import TA_LEFT,TA_CENTER,TA_JUSTIFY
from reportlab.lib.colors import grey,black,lightgrey,lightcyan
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
import urllib2
import sys
import psycopg2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pylab import rcParams
import read_settings
import datetime
import time
import uuid

pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))

def addFooter(canvas, doc):
    canvas.setFont('Arial',12)
    page_num = canvas.getPageNumber()
    text = "Page %s" % page_num
    canvas.drawRightString(200*mm, 10*mm, text)
    canvas.drawRightString(200*mm, 20*mm, "Signature_________________ Date:_______________")
    canvas.drawRightString(110*mm, 10*mm, "REPORT Model XXXX Generated on:" + datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    canvas.drawRightString(50*mm, 20*mm, "Proprietary Document")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._codes = []
    def showPage(self):
        self._codes.append({'code': self._code, 'stack': self._codeStack})
        self._startPage()
    def save(self):
        """add page info to each page (page x of y)"""
        # reset page counter
        self._pageNumber = 0
        for code in self._codes:
            # recall saved page
            self._code = code['code']
            self._codeStack = code['stack']
            self.setFont("Helvetica", 7)
            self.drawRightString(200*mm, 20*mm,
                "page %(this)i of %(total)i" % {
                   'this': self._pageNumber+1,
                   'total': len(self._codes),
                }
            )
            canvas.Canvas.showPage(self)

def get_image(path, width=1*cm):
    img = utils.ImageReader(path)
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    return Image(path, width=width, height=(width * aspect))

# Standalone execution
if __name__ == '__main__':
    read_settings.read_config()

# Batch argument
if len(sys.argv) > 1:
    batchid = sys.argv[1]
else:
    print >> sys.stderr, "Missing batch id argument - Cannot generate report"
    sys.exit(1)

# db connection
conn = psycopg2.connect(read_settings.Config_DbConnectionString[0])
cur = conn.cursor()

# getting batch info
query = 'SELECT * FROM public.batchdb WHERE batchdb."batchid"= (%s);'
data = (batchid,)

try:
    cur.execute(query,data)
except:
    print "I cannot find the specified batch ID"
    print "Report generation failed!"
    sys.exit(1)
rows=cur.fetchall()
data=[]

for row in rows:
    data.append(row)
StartTime = data[0][3]
EndTime = data[0][4]
Result = data[0][6]
print ("Batch start time " + StartTime.strftime('%Y-%m-%d %H:%M:%S'))
print ("Batch end time " + EndTime.strftime('%Y-%m-%d %H:%M:%S'))

# init template
styles = getSampleStyleSheet()
reportfname='.\\reports\\' + batchid + '_' + StartTime.strftime('%Y-%m-%d') + '.pdf'
doc = SimpleDocTemplate("report_temp.pdf", pagesize=A4, topMargin=120)
style = styles['Normal']
parts = []


# TABLE 2
data=   [['BATCH ID:', batchid],
        ['Started on:', StartTime],
        ['Ended on:', EndTime],
        ['Duration:', EndTime-StartTime],
        ['Result:', Result]]

ts2=[('GRID',(0,0),(1,4),0.5,grey)]
t2=Table(data,style=ts2,hAlign='LEFT')
parts.append(t2)

# SPACER
parts.append(Spacer(1,1*cm))

# ALARM TABLE
# Query DB
query = '''SELECT
  alarms."timestring",
  messagetext."MsgText",
  alarms."comment",
  alarms."value",
  alarms."state",
  alarms."operator"
FROM
  public.alarms,
  public.messagetext
WHERE
  alarms."msgnumber" = messagetext."MsgNumber"
AND
  alarms."timestring" >= (%s)
AND
  alarms."timestring" <= (%s);'''

try:
    cur.execute(query,(StartTime,EndTime))
except:
    print "I can't execute the ALARM query"

# Formatting Data for table in reportlab
data=[]
result=['Time','Text','Comment','Value','State','Operator']
data.append(result)

try:
    rows=cur.fetchall()
    for row in rows:
        result=[]
        result.append(row[0].strftime('%Y/%m/%d %H:%M:%S'))
        for i in range (1,5):
            result.append(row[i])
        data.append(result)
except:
    print "No alarms found in batch period"

parts.append(Paragraph('ALARMS',styles["Title"]))
t3=Table(data,repeatRows=1)
t3.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, black),('BOX', (0, 0), (-1, -1), 0.25, black),('LEFTPADDING', (0,0), (-1,-1), 3),('RIGHTPADDING', (0,0), (-1,-1), 3)]))
parts.append(t3)
# create a function with: query, first row, title, StartTime, EndTime, Style

# SPACER
parts.append(Spacer(1,1*cm))

# ANALOG TABLE

querytrend = '''SELECT
  itemsvaluedb.numvalue,
  itemsdb."desc",
  itemsdb."tagname",
  itemsdb."Unit",
  itemsvaluedb.timeloc
FROM
  public.itemsvaluedb
INNER JOIN
  public.itemsdb
ON
  itemsvaluedb.itemid = itemsdb."Id"
WHERE
  itemsvaluedb."timeloc" > (%s) AND
  itemsvaluedb."timeloc" < (%s);'''

query = '''SELECT
  itemsdb."TagName",
  itemsdb."Desc",
  itemsdb."Unit",
  MIN(itemsvaluedb.numvalue),
  AVG(itemsvaluedb.numvalue),
  MAX(itemsvaluedb.numvalue)
FROM
  public.itemsvaluedb
INNER JOIN
  public.itemsdb
ON
  itemsvaluedb.itemid = itemsdb."Id"
WHERE
  itemsvaluedb."timeloc" > (%s) AND
  itemsvaluedb."timeloc" < (%s)
GROUP BY
  itemsdb."TagName",
  itemsdb."Desc",
  itemsdb."Unit"'''

try:
    cur.execute(query,(StartTime,EndTime))
except:
    print "I can't execute the ANALOG query"

rows=cur.fetchall()

# Formatting Data for table in reportlab
data=[]
result=['Tag','Description','Eng Unit','Min','Avg','Max']
data.append(result)
for row in rows:
    data.append(row)

parts.append(Paragraph('ANALOG MEASUREMENTS',styles["Title"]))
t3=Table(data,repeatRows=1)
t3.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, black),('BOX', (0, 0), (-1, -1), 0.25, black),('LEFTPADDING', (0,0), (-1,-1), 3),('RIGHTPADDING', (0,0), (-1,-1), 3)]))
parts.append(t3)

# Plots

query = '''SELECT
  itemsvaluedb.numvalue,
  itemsdb."Desc",
  itemsdb."TagName",
  itemsdb."Unit",
  itemsvaluedb.timeloc
FROM
  public.itemsvaluedb
INNER JOIN
  public.itemsdb
ON
  itemsvaluedb.itemid = itemsdb."Id"
WHERE
  itemsvaluedb."timeloc" > (%s) AND
  itemsvaluedb."timeloc" < (%s) AND
  itemsvaluedb.itemid = (%s);'''

def genfig(cursor,sqlquery,index,stime,etime):

    try:
        cursor.execute(sqlquery,(stime,etime,index))
    except:
        print "I can't execute the Trend query"
    rows=cursor.fetchall()
    y=[]
    x=[]
    for row in rows:
        y.append(row[0])
        x.append(row[4])
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.figure(figsize=(12,5))
    plt.plot(x,y,'-',linewidth=2)
    plt.gcf().autofmt_xdate()
    filename = str(uuid.uuid4()) + '.png'
    plt.savefig(filename)
    parts.append(get_image(filename, width=16*cm))

# SPACER
parts.append(Spacer(1,1*cm))
# IMAGE
parts.append(Paragraph('TRENDS',styles["Title"]))
parts.append(Paragraph('StartTime: '+StartTime.strftime('%Y/%m/%d'),styles["Normal"]))
parts.append(Paragraph('EndTime: '+EndTime.strftime('%Y/%m/%d'),styles["Normal"]))
genfig(cur,query,'2',StartTime,EndTime)
genfig(cur,query,'4',StartTime,EndTime)
genfig(cur,query,'5',StartTime,EndTime)
# BUILD DOCUMENT
doc.build(parts, onFirstPage=addFooter,onLaterPages=addFooter)

# ADD HEADER
os.system("python headergen.py " + reportfname)
os.system("del *.png")
