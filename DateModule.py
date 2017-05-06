# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 21:04:38 2017

@author: Kozmik
"""

import tkinter as tk
import tkinter.ttk as ttk
from DateFilter import DateFilter
import DateTools

class DateFrame(tk.Frame):
    def __init__(self, master, jentry, jobject, controller, **kw):
        self.master = master
        tk.Frame.__init__(self, self.master, **kw)
        inner_frame = tk.Frame(self, bg='slate gray')
        self.jobject = jobject
        self.jentry = jentry
        
        self.filter = DateFilter(self.jobject)
        
        self.user_date = ''
        self.program_date = None
        self.datebox_index={}
        self.updateDateboxIndex()
        
        self.datebox = ttk.Combobox(inner_frame, state='readonly', width=26, 
                                    justify='left', postcommand=self.updateDateboxList)
        self.FILTER = ttk.Button(inner_frame, takefocus=0, text='Filter', 
                                 command=self.filter.createFilterDialog)
#        self.datebox.state(statespec='readonly')
        
        self.style = ttk.Style()
        self.style.configure('NetInd.TLabel', foreground='dark slate gray')
        self.num_entries = self.filter.getNumEntryVar()
        self.NUMLINKS = ttk.Label(inner_frame, anchor='center', width=10, 
                                  textvariable=self.num_entries)
        
        self.NUMLINKS.pack(side=tk.LEFT, expand=True)        
        self.datebox.pack(side=tk.LEFT)
        self.FILTER.pack(side=tk.LEFT)
        
        inner_frame.pack()
        
        if self.jentry.getDate():
            self.updateGUI(self.jentry)
            
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
        
    def clearGUI(self, entry):
        self.jentry = entry
        self.datebox.set('')
        self.program_date = 0
        self.user_date = ''       
        
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