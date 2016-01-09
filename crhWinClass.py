# crhWinClass.py -- windows app class utilities (tier 2)
# Copyright (c) 2014-2015 CR Hailey
# v1.03 crh 03-jul-14 -- based on crhClass, which it supersedes

#!/usr/local/bin/python

import Tkinter as tk  # window widgets, etc
import ttk  # new implementation of window widgets, etc

from datetime import date
from crhString import *

## basic crh ttk frame

class crhFrm(object, ttk.Frame):
    '''base frame class'''

    def __init__(self, parent):
        '''the Frame'''

        ttk.Frame.__init__(self, parent, class_ = 'Frame')
        self.crhParent = parent
        self.padLbl = {}
        self.sepLbl = {}
        self.cbVar = {}
        self.cb = {}
        self.rbVar = {}
        self.rb = {}
#        self.setDate = tk.StringVar()
#        self.setDate1 = date.today()
        self.dateVar = {}
        self.dateSet = {}
        self.dateLbl = {}
        self.dateEntry = {}
        self.status  = "Unset status line text for crhFrm class"
        self.appLog = []
        self.grid()

    def _padRow(self, rowNr, colNr = 0, colSpan = 1):
        '''add padding row'''

        self.padLbl[rowNr] = ttk.Label(self, text = " ")  # add vertical padding
        self.padLbl[rowNr].grid(row = rowNr, column = colNr, columnspan = colSpan)

    def _sepRow(self, rowNr, colNr, colSpan, padY = 0, padX = 0):
        '''add horizontal line separator'''

        self.sepLbl[rowNr] = ttk.Separator(self, orient = tk.HORIZONTAL)
        self.sepLbl[rowNr].grid(row = rowNr, column = colNr, columnspan = colSpan, sticky = tk.EW, pady = padY, padx = padX)

    def _cbRow(self, cbRef, rowNr, colStart, padY, checkOn, *cbText):
        '''add row of check buttons'''

        self.cbVar[cbRef] = []
        self.cb[cbRef] = []

        for i in range(len(cbText)):
            self.cbVar[cbRef].append(tk.IntVar())
            self.cb[cbRef].append(ttk.Checkbutton(self, text = cbText[i], variable = self.cbVar[cbRef][i], 
                onvalue = 1, offvalue = 0))
            if checkOn:
                self.cbVar[cbRef][i].set(self.cb[cbRef][i]['onvalue'])
            else:
                self.cbVar[cbRef][i].set(self.cb[cbRef][i]['offvalue'])
            self.cb[cbRef][i].grid(row = rowNr, column = i + colStart, sticky = tk.W, pady = padY)

    def isSetCB(self, cbRef, idx = 0):
        '''return true if the checkbox is ticked (on)'''

        return self.cbVar[cbRef][idx].get() == self.cb[cbRef][idx]['onvalue']

    def _rbRow(self, rbRef, rowNr, colStart, padY, radioActive, *rbText):
        '''add row of radio buttons'''

        self.rbVar[rbRef] = tk.IntVar()
        self.rbVar[rbRef].set(radioActive)
        self.rb[rbRef] = []

        if (radioActive < 0) or (radioActive >= len(rbText)):
            self.rbVar[rbRef].set(0)
        for i in range(len(rbText)):
            self.rb[rbRef].append(ttk.Radiobutton(self, text = rbText[i], variable = self.rbVar[rbRef], 
                value = i))
            self.rb[rbRef][i].grid(row = rowNr, column = i + colStart, sticky = tk.W, pady = padY)

    def radioActive(self, rbRef):
        '''return the index value of the currently active radio button'''

        return self.rbVar[rbRef].get()

    def _dateEntry(self, dateRef, rowNr, colStart, dateText = 'Date: ', setDate = date.today(), padX = 0, padY = 0):
        '''simple date set/display using text entry widget'''

        self.dateVar[dateRef] = tk.StringVar()
        self.dateSet[dateRef] = setDate

        self.dateVar[dateRef].set(zeroPadNr(setDate.year, 4) + '-' + zeroPadNr(setDate.month, 2) + '-' + zeroPadNr(setDate.day, 2))
        self.dateLbl[dateRef] = ttk.Label(self, text = dateText)
        if colStart == 0:
            self.dateLbl[dateRef].grid(row = rowNr, column = 0, columnspan = 1, sticky = tk.W)
        else:
            self.dateLbl[dateRef].grid(row = rowNr, column = colStart, columnspan = 1, sticky = tk.E)
        self.dateEntry[dateRef] = ttk.Entry(self, width = 12, textvariable = self.dateVar[dateRef])
        self.dateEntry[dateRef].grid(row = rowNr, column = colStart + 1, columnspan = 1, sticky = tk.W, 
            padx = padX, pady = padY)

    def _checkDate(self, dateRef):
        '''check dateEntry[dateRef] value and update dateSet[dateRef] if valid
basic check, overrule in child class as required'''

        print(self.dateVar[dateRef].get().strip())
        dateStr = parseDate(self.dateVar[dateRef].get().strip())
        print(dateStr)
        if dateStr is None:
            self.dateVar[dateRef].set(zeroPadNr(self.dateSet[dateRef].year, 4) + '-' + zeroPadNr(self.dateSet[dateRef].month, 2) + '-' + zeroPadNr(self.dateSet[dateRef].day, 2))
            return None
        else:
            try:
                newDate = date(int(dateStr[:4]), int(dateStr[5:7]), int(dateStr[8:]))
                self.dateSet[dateRef] = newDate
                return newDate
            except:
                return None

    def _printStatus(self, text = ""):
        '''print status line, assumes statusLbl ttk.Label widget statusLbl defined in child class'''

        if text != "":
            self.status = text
        try:
            self.statusLbl["text"] = self.status
        except AttributeError:
            pass

    def _exit(self):
        '''destroy app'''

        self.crhParent.destroy()

    def clrLog(self):
        '''clear app log'''

        self.appLog = []

    def addLog(self, text):
        '''add line to app log'''

        self.appLog.append(text)

    def getLog(self):
        '''return app log as list of text lines'''

        return self.appLog
