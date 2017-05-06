# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 17:05:45 2017

@author: Kozmik
"""

from TagsManager import TagsManager
import tkinter as tk
import tkinter.ttk as ttk
from math import ceil
import copy

class DateFilter(TagsManager):
    def __init__(self, jobject):
        TagsManager.__init__(self, jobject)
        self.dateslist = list(self.journal.getAllDates())
        self.dialog = None
        self.filter_type = tk.StringVar(name='SearchType', value='OR')
        self.islinked = tk.BooleanVar(name='IsLinkedFilter', value=False)
        self.num_entries = tk.IntVar(name='NumberOfEntries', value=len(self.dateslist))
        
    def createFilterDialog(self):
        self.dialog = tk.Toplevel(bg='slate gray')
        self.dialog.title("Filters")
        top = tk.Frame(self.dialog, bg='slate gray')
        middle = tk.Frame(self.dialog, bg='slate gray')
        bottom = tk.Frame(self.dialog, bg='slate gray')
        
        canvas = tk.Canvas(self.dialog, highlightthickness=0, bg='slate gray')
        tagslist = self.getVarsDict()
        if tagslist:
            for tag in tagslist:
                tagslist[tag][1] = tk.Checkbutton(master=canvas, text=tag, 
                        variable=tagslist[tag][0], bg='slate gray')
            tmp = sorted(tagslist.keys())
            row = 10
            col = ceil(len(tagslist) / row)
            grid = [(x, y) for x in range(0, col) for y in range(0, row) ]
            for i in range(0, len(tmp)):
                x, y = grid[i]
                tagslist[tmp[i]][1].grid(row=y, column=x, sticky=tk.W)
        else:
            message = tk.Message(canvas, text='There is nothing to display.')
            message.grid()
        
        ORPTYPE = tk.Radiobutton(middle, text="OR(P)", value="OR(P)", 
                                 variable=self.filter_type, bg='slate gray')
        ORPTYPE.grid(row=1, column=1)
        ORTYPE = tk.Radiobutton(middle, text="OR", value="OR", variable=self.filter_type, 
                                bg='slate gray')
        ORTYPE.grid(row=1, column=0)
        ANDTYPE = tk.Radiobutton(middle, text="AND", value="AND", variable=self.filter_type, 
                                 bg='slate gray')
        ANDTYPE.grid(row=1, column=2)
        
        canvas.pack()
        ALL = ttk.Button(bottom, text="All", command=self.selectAllBoxes)
        NONE = ttk.Button(bottom, text="None", command=self.deselectAllBoxes)
        INVERT = ttk.Button(bottom, text="Invert", command=self.invertAllBoxes)
        ISLINKED = tk.Checkbutton(middle, text='Is Linked', variable=self.islinked, 
                                  bg='slate gray')
        ALL.grid(row=1, column=0)
        NONE.grid(row=1, column=1)
        INVERT.grid(row=1, column=2)
        ISLINKED.grid(row=1, column=3)
        top.pack(side='top', expand=1, fill='x')
        middle.pack(side='top')
        bottom.pack(side='top')
        self.dialog.grab_set()
        self.dialog.protocol("WM_DELETE_WINDOW", self.destroyDialog)
        
    def destroyDialog(self):
        self.dialog.destroy()
        self.dialog = None
        self.filterDates()
        
    def sortLinked(self):
        self.dialog.destroy()
        self.dialog = None
        
    def filterDates(self):
        filtered_tags = []
        states_list = self.getStates()
        self.dateslist = list(self.journal.getAllDates())
        if self.filter_type.get() == 'OR(P)':
            for tag in states_list:
                if not states_list[tag]:
                    filtered_tags.append(tag)
            for date in sorted(self.dateslist):
                filter_flag = False
                tags = self.journal.getEntry(date).getTags()
                i = 0
                j = len(tags)
                tag = tags[i]
                while i < j and not filter_flag:
                    tag = tags[i]
                    if tag in filtered_tags:
                        filter_flag = True
                    i += 1
                if filter_flag:
                    self.dateslist.remove(date)
        elif self.filter_type.get() == 'OR':
            for tag in states_list:
                if states_list[tag]:
                    filtered_tags.append(tag)
            tmp_list = []
            for date in sorted(self.dateslist):
                for tag in self.journal.getEntry(date).getTags():
                    if tag in filtered_tags:
                        if date not in tmp_list:
                            tmp_list.append(date)
            self.dateslist = tmp_list
        elif self.filter_type.get() == 'AND':
            for tag in states_list:
                if states_list[tag]:
                    filtered_tags.append(tag)
            for date in sorted(self.dateslist):
                if len(self.journal.getEntry(date).getTags()) != len(filtered_tags):
                    self.dateslist.remove(date)
                else:
                    for tag in self.journal.getEntry(date).getTags():
                        if tag not in filtered_tags:
                            if date in self.dateslist:
                                self.dateslist.remove(date)
        if self.islinked.get():
            tmp = copy.copy(self.dateslist)
            for date in tmp:
                entry = self.journal.getEntry(date)
                if not entry.hasLinks():
                    self.dateslist.remove(date)
        self.num_entries.set(len(self.dateslist))
        
    def getDatesList(self):
        self.updateVarsDict()
        self.filterDates()
        return copy.copy(self.dateslist)
        
    def getTagsList(self):
        return self.tagslist
    
    def getNumEntryVar(self):
        return self.num_entries
        
    def selectAllBoxes(self):
        for tag in self.vars:
            self.vars[tag][0].set(True)
        
    def deselectAllBoxes(self):
        for tag in self.vars:
            self.vars[tag][0].set(False)
        
    def invertAllBoxes(self):
        for tag in self.vars:
            if self.vars[tag][0].get():
                self.vars[tag][0].set(False)
            else:
                self.vars[tag][0].set(True)