# crhPDF.py -- pdf document utilities (tier 2)
# Copyright (c) 2013-2015 CR Hailey
# v1.00 crh 30-may-13 -- initial release
# v1.13 crh 03-jul-13 -- revamp reportlab imports to get them working again
# provides wrapper functions, etc for reportlab packages
# note that reportlab native units are 1/72 inch (0.3528mm), aka 1 point

#!/usr/local/bin/python
#

from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, inch
from reportlab.lib.pagesizes import A4, A5, A6
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.platypus import BaseDocTemplate, PageTemplate, Flowable
from reportlab.platypus.frames import Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.fonts import tt2ps
from reportlab.rl_config import canvas_basefontname as _baseFontName

from crhGV import gv    # object holding global variables shared across modules & scripts 

## essential variables
_baseFontNameB = tt2ps(_baseFontName,1,0)
_baseFontNameI = tt2ps(_baseFontName,0,1)
_baseFontNameBI = tt2ps(_baseFontName,1,1)

pdfFrameLines = False

pdfPageSz = A5
pdfPageHt = pdfPageSz[1]
pdfPageWd = pdfPageSz[0]
pdfStyles = getSampleStyleSheet()
pdfMargin = 1*cm

pdfAuthorTxt = 'CR Hailey'
pdfTitleTxt = 'CRH_Title'
pdfSubtitleTxt = 'CRH_Subtitle'
pdfSubjectTxt = 'CRH_Subject'
pdfDescriptionTxt = ['CRH_Description_1', 'CRH_Description_2', 'CRH_Description_3']
pdfBottomLineTxt = 'CRH_Bottom_Line'
pdfHeaderTxt = 'CRH_Header'
pdfKeywordsTxt = 'crh python'
pdfCreatorTxt = 'crhPDF'

# classes

# bookmark flowable class
class Bookmark(Flowable):
    """ Utility class to display PDF bookmark. """

    def __init__(self, title, key):
        self.title = title
        self.key = key
        Flowable.__init__(self)

    def wrap(self, availWidth, availHeight):
        """ Doesn't take up any space. """
        return (0, 0)

    def draw(self):
#        self.canv.showOutline()
        self.canv.bookmarkPage(self.key)
        self.canv.addOutlineEntry(self.title, self.key, 0, 0)

# add custom styles
subtitle = ParagraphStyle(name = 'Subtitle', fontName = _baseFontNameB, fontSize = 14, 
    leading = 18, alignment = TA_CENTER, spaceAfter = 5)

normalA6 = ParagraphStyle(name = 'normalA6', fontName = _baseFontName, fontSize = 9, 
    leading = 11)

copyright = ParagraphStyle(name = 'copyright', fontName = _baseFontName, fontSize = 11, 
    leading = 16, alignment = TA_CENTER)

## define functions

def pdfSetDefPage(size = A5, margin = 1*cm):
    """set default page properties"""
    
    global pdfPageSz, pdfPageHt, pdfPageWd
    global pdfMargin, pdfTMargin, pdfBMargin, pdfLMargin, pdfRMargin
    pdfPageSz = size
    pdfPageHt = pdfPageSz[1]
    pdfPageWd = pdfPageSz[0]
    pdfMargin = margin
    pdfTMargin = pdfPageHt - pdfMargin
    pdfBMargin = pdfMargin
    pdfLMargin = pdfMargin
    pdfRMargin = pdfPageWd - pdfMargin

# getting pdgPageSz directly from a script doesn't seem to work
def pdfGetPageSize():
    """return the current page size"""
    
    return pdfPageSz
   
# pdfgen functions
def pdfCreateCanv(filename):
    """create basic canvas object"""
    
    canv = canvas.Canvas(filename, pagesize = pdfPageSz, invariant=1)
    canv.setPageCompression(1)
    return canv

def pdfSetMetadata(canv = None, mdAuthor = 'CR Hailey', mdSubject = None, 
        mdTitle = None, mdKeywords = None, mdCreator = None, mdHeader = None):
    """ set pdf document metadata"""
    
    global pdfAuthorTxt, pdfSubjectTxt, pdfTitleTxt
    global pdfKeywordsTxt, pdfCreatorTxt, pdfHeaderTxt
    if canv == None:    # set crhPDF defaults
        if mdAuthor:
            pdfAuthorTxt = mdAuthor
        if mdSubject:
            pdfSubjectTxt = mdSubject
        if mdTitle:
            pdfTitleTxt = mdTitle
        if mdKeywords:
            pdfKeywordsTxt = mdKeywords
        if mdCreator:
            pdfCreatorTxt = mdCreator
        if mdHeader:
            pdfHeaderTxt = mdHeader
    else:
#        canv.setDateFormatter(_dateFormat)
        canv.setAuthor(mdAuthor)
        if not mdCreator:
            canv.setCreator(gv.getVar('progName'))
        if mdTitle:
            canv.setTitle(mdTitle)
        if mdKeywords:
            canv.setKeywords(mdKeywords)
        if mdSubject:
            canv.setSubject(mdSubject)
        
def pdfTitlePage(canv, title  = 'CRH Title', subTitle = 'CRH Subtitle', 
        description = ['CRH Description 1', 'CRH Description 2', 'CRH Description 3'],
        bottomLine = 'CRH Bottom Line'):
    """create title page"""
    
    descrNr = len(description)
    canv.saveState()
    canv.setFont("Times-Bold", 24)
    canv.drawCentredString(0.5*pdfPageWd, 0.85*pdfPageHt, title)
    canv.setFont("Times-Bold", 18)
    canv.drawCentredString(0.5*pdfPageWd, 0.65*pdfPageHt, subTitle)
    canv.setFont("Times-Bold", 12)
    tx = canv.beginText(pdfLMargin, (descrNr + 1)*cm)
    for line in description:
        tx.textLine(line)
    tx.textLine('')
    tx.textLine(bottomLine)
    canv.drawText(tx)
    canv.restoreState()

def pdfPageFrame(canv, header = 'CRH Header', pageNr = False):
    """draw page frame"""

    canv.saveState()
    if pdfFrameLines:
        canv.line(pdfLMargin, pdfTMargin, pdfRMargin, pdfTMargin)
        canv.line(pdfLMargin, pdfBMargin, pdfRMargin, pdfBMargin)
    if pdfPageSz == A6:
       canv.setFont('Times-Italic', 8)
       # do not include page footer for A6 PDFs
    else:
        canv.setFont('Times-Italic', 12)
        canv.drawString(pdfMargin, (pdfMargin - 0.4*cm),
                pdfAuthorTxt)
    canv.drawString(pdfLMargin, pdfTMargin + 0.2*pdfMargin, header)

    if pageNr:
        canv.drawCentredString(0.5*pdfPageWd, (pdfMargin - 0.4*cm),
                'Page %d' % canv.getPageNumber())
    canv.restoreState()

# platypus functions
def pdfRewriter(text):
    """replace dodgy chars for platypus"""

    # replace EOL escape seq and &, etc
    text = text.replace('&', '&amp;')
    text = text.replace(r'\r\n', '<br/>')
    # some nasty workarounds!
    text = text.replace(':nbsp:', '&nbsp;')
    text = text.replace(':pound:', '&pound;')
    text = text.replace(':reg:', '&reg;')
    text = text.replace(':bullet:', '&#149;')
    return text

def pdfDocTemplate(filename):
    """create document template sized as required"""

    doc = BaseDocTemplate(filename, pagesize = pdfPageSz, 
        leftMargin = pdfMargin, rightMargin = pdfMargin, topMargin = pdfMargin, 
        bottomMargin = pdfMargin, creator = gv.getVar('progName'),
        author = pdfAuthorTxt, subject = pdfSubjectTxt, title = pdfTitleTxt, 
        keywords = pdfKeywordsTxt, pageCompression = 1)
    # normal frame as for SimpleFlowDocument
    frameN = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    doc.addPageTemplates([PageTemplate(id = 'all',frames = frameN, onPage = allPages)])
    return doc

def allPages(canv, doc):
    pdfPageFrame(canv, pdfHeaderTxt)

## define helper functions

def _dateFormat(yr, mon, dy, hr, min, sec):

    return str(hr) + ':' + str(min) + ' ' + str(dy) + '-' + str(mon) + '-' +str(yr)

## initialise

pdfSetDefPage(A5)

## testing code

if __name__ == '__main__':
    # add test stuff here
    testCanv = pdfCreateCanv('testA5.pdf')
    pdfSetMetadata(testCanv, 'Chris Hailey', 'CRH Subject', 'CRH Title', 
        'test crhPDF', 'crhPDF')
    pdfPageFrame(testCanv)
    pdfTitlePage(testCanv)
    testCanv.showPage()
    testCanv.save()
    pdfSetDefPage(A6)
    print 'A6: ', pdfPageSz
    testCanv = pdfCreateCanv('testA6.pdf')
    pdfSetMetadata(testCanv, 'Chris Hailey', 'CRH Subject', 'CRH Title', 
        'test crhPDF', 'crhPDF')
    pdfPageFrame(testCanv)
    pdfTitlePage(testCanv)
    testCanv.showPage()
    testCanv.save()
    pdfSetDefPage(A4)
    testCanv = pdfCreateCanv('testA4.pdf')
    pdfSetMetadata(testCanv, 'Chris Hailey', 'CRH Subject', 'CRH Title', 
        'test crhPDF', 'crhPDF')
    pdfPageFrame(testCanv)
    pdfTitlePage(testCanv)
    testCanv.showPage()
    testCanv.save()
    print 'A4: ', A4
    print 'pdfMargin: ', pdfMargin
    print 'pdfTMargin: ', pdfTMargin
    print 'pdfBMargin: ', pdfBMargin
    print 'pdfLMargin: ', pdfLMargin
    print 'pdfRMargin: ', pdfRMargin
    print 'A5: ', A5
    print 'A6: ', A6
    pdfSetDefPage(A5)
    testDoc = pdfDocTemplate('testA6a.pdf')
    Story = [Spacer(1, 0.25*cm)]
    if pdfPageSz == A6:
        styleN = normalA6    # slightly smaller font
        print 'styleN = normalA6'
    else:
        styleN = pdfStyles["Normal"]
        print 'styleN = normal'
    styleT = pdfStyles["Title"]
    styleST = subtitle
    titleTxt1 = 'CRH_Title'
    titleTxt2 = 'CRH_Subtitle'
    p = Paragraph(titleTxt1, styleT)
    Story.append(p)
    Story.append(Spacer(1, 2.0*cm))
    p = Paragraph(titleTxt2, styleST)
    Story.append(p)
    Story.append(PageBreak())
    for i in range(20):
        bodyText = ("This is Paragraph number %s. " % i) *10
        p = Paragraph(bodyText, styleN)
        Story.append(p)
        Story.append(Spacer(1, 0.25*cm))
    testDoc.build(Story)
