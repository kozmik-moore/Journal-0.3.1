# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 21:04:38 2017

@author: Kozmik
"""

from tkinter import *
from tkinter.ttk import *
from JObject import *
from DateFilter import DateFilter
import DateTools

class DateFrame(Frame):
    def __init__(self, master, jentry, jobject, controller, **kw):
        self.master = master
        Frame.__init__(self, self.master, **kw)
        inner_frame = Frame(self)
        self.jobject = jobject
        self.jentry = jentry
        
        self.filter = DateFilter(self.jobject)
        
        self.user_date = ''
        self.program_date = None
        self.datebox_index={}
        self.updateDateboxIndex()
        
        self.datebox = Combobox(inner_frame, width=25, state='readonly', justify=CENTER, postcommand=self.updateDateboxList)
        self.FILTER = Button(inner_frame, text='Filter', command=self.filter.createFilterDialog)
#        self.datebox.state(statespec='readonly')
        
        self.style = Style()
        self.style.configure('NetInd.TLabel', foreground='gray')
        self.is_linked = StringVar(self, value='Not Linked')
        self.HASLINKS = Label(inner_frame, width=12, anchor=CENTER, textvariable=self.is_linked, style='NetInd.TLabel')
        
        self.HASLINKS.pack(side=LEFT)        
        self.datebox.pack(side=LEFT)
        self.FILTER.pack(side=LEFT)
        
        inner_frame.pack()
        
        if self.jentry.getDate():
            self.updateGUI(self.jentry)
        
    def setNetworkedIndicator(self):
        if self.jentry.getParent() or self.jentry.getChild():
            self.is_linked.set('Linked')
            self.style.configure('NetInd.TLabel', foreground='blue')
        else:
            self.is_linked.set('Not Linked')
            self.style.configure('NetInd.TLabel', foreground='gray')
            
    def updateDateboxList(self):
        combo_list = self.filter.getDatesList()
        for i in range(0, len(combo_list)):
            date = combo_list.pop(0)
            combo_list.append(DateTools.getDateGUIFormat(date))
        self.datebox['values'] = combo_list
        
    def updateDateboxIndex(self, date=None):
        if date:
            self.datebox_index[DateTools.getDateGUIFormat(date)] = date
        else:
            for date in self.jobject.getAllDates():
                self.datebox_index[DateTools.getDateGUIFormat(date)] = date

    def bindDatebox(self, function):
        self.datebox.bind("<<ComboboxSelected>>", function)
        
    def updateGUI(self, entry):
        self.jentry = entry
        if self.jentry.getDate():
            self.program_date = self.jentry.getDate()
            self.user_date = DateTools.getDateGUIFormat(self.program_date)
            self.datebox.set(self.user_date)
        else:
            self.datebox.set('')
            self.program_date = None
            self.user_date = ''
        self.setNetworkedIndicator()
        
    def clearGUI(self, entry):
        self.jentry = entry
        self.datebox.set('')
        self.program_date = 0
        self.user_date = ''
        self.setNetworkedIndicator()       
        
    def save(self):
        if not self.jentry.getDate():
            date = DateTools.getCurrentDate()
            self.updateDateboxIndex(date)
            self.jentry.setDate(date)
            self.updateDateboxIndex(date)
            self.updateGUI(self.jentry)
        
    def getDate(self):
        return self.datebox.get()
        
    def indexDate(self):
        if self.datebox.get():
            return self.datebox_index[self.datebox.get()]
            
    def getDateUserFormat(self):
        return self.user_date
        
    def getDateProgramFormat(self):
        return self.program_date