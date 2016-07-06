from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileWriter, PdfFileReader
import os
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

# Standalone execution
if __name__ == '__main__':

    if len(sys.argv) > 1:
        reportfname = sys.argv[1]
    else:
        print >> sys.stderr, "Missing file argument - Cannot generate header"
        sys.exit(1)


logopath = './template/logo.png'

def get_python_image():
    """ Get a python logo image for this example """
    if not os.path.exists(logopath):
        response = urllib2.urlopen(
            'http://www.python.org/community/logos/python-logo.png')
        f = open(logopath, 'w')
        f.write(response.read())
        f.close()

def get_image(path, width=1*cm):
    img = utils.ImageReader(path)
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    return Image(path, width=width, height=(width * aspect))

styles = getSampleStyleSheet()
get_python_image()

doc = SimpleDocTemplate('header.pdf', pagesize=A4, topMargin=20)
style = styles['Normal']
parts = []

I = get_image(logopath, width=1.5*cm)

data=   [[I,'Line XXXX Machine XXXX' ],
         ['REPORT Report Test01', 'XXXX Plant, XXXX']]
t1=Table(data,hAlign='CENTER',rowHeights=(1.5*cm),repeatRows=1)
t1.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,grey),
                        ('BACKGROUND',(0,0),(-1,-1),lightcyan),
                        ('SIZE',(0,0),(-1,-1),16),
                        ('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
parts.append(t1)
t1._argW[0]=9*cm
t1._argW[1]=9*cm
doc.build(parts)

# Get the watermark file you just created
watermark = PdfFileReader(open("header.pdf", "rb"))

# Get our files ready
output_file = PdfFileWriter()
input_file = PdfFileReader(open("report_temp.pdf", "rb"))

# Number of pages in input document
page_count = input_file.getNumPages()

# Go through all the input file pages to add a watermark to them
for page_number in range(page_count):
    print "Adding header to page {} of {}".format(page_number, page_count)
    # merge the watermark with the page
    input_page = input_file.getPage(page_number)
    input_page.mergePage(watermark.getPage(0))
    # add page from input file to output document
    output_file.addPage(input_page)

# write output
with open(reportfname, "wb") as outputStream:
    output_file.write(outputStream)

outputStream.close()