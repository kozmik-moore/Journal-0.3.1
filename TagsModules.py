# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 09:50:53 2016

@author: Kozmik
"""
import tkinter as tk
import tkinter.ttk as ttk
from JObject import JObject
from math import ceil
from math import sqrt
from tkinter import simpledialog as simpledialog
        
        
class TagsCheckboxManager:
    def __init__(self, master, journal):
        self.master = master
        self.journal = JObject()
        self.vars = {}
        self.grid = None
        if journal:
            self.journal = journal
            self.updateVarsList()
        
    def updateManager(self, entry):
        self.entry = entry
        
    def updateVarsList(self):
#        self.vars = {}
        for tag in self.journal.getAllTags():
            if tag not in self.vars:
                self.vars[tag] = [tk.BooleanVar(master=None, value=False, name='TF.'+tag), None]
            else: 
                self.vars[tag][0].set(False)
                self.vars[tag][1] = None
        for tag in self.entry.getTags():
            if tag in self.vars:
                self.vars[tag][0].set(True)
                self.vars[tag][1] = None
            else:
                self.vars[tag] = [tk.BooleanVar(master=None, value=True, name='TF.'+tag), None]
        for tag in list(self.vars):
            if tag not in self.entry.getTags() and tag not in self.journal.getAllTags():
                del self.vars[tag]            
            
    def addTag(self, tag):
        self.entry.addTag(tag)
        self.updateVarsList()
            
    def removeTag(self, tag):
        self.entry.removeTag(tag)
        self.updateVarsList()
            
    def getStates(self):
        states = {}
        for tag in self.vars:
            states[tag] = self.vars[tag][0].get()
        return states
        
    def getJournalTags(self):
        return self.journal.getAllTags()
        
    def getEntryTags(self):
        return self.entry.getTags()
        
    def getVarsList(self):
        return self.vars
        
    def anyBoxesChecked(self):
        for tag in self.vars:
            if self.vars[tag][0].get():
                return True
        return False
        
    def boxChecked(self, tag):
        if self.tagslist[tag][0].get():
            return True
        else:
            return False
            
        
class TagsCanvas(TagsCheckboxManager):
    def __init__(self, master, journal):
        self.displayed_tags = []
        self.canvas = tk.Canvas(master, height=1, width=0, bg='slate gray')
        self.tag = None
        self.dialog = None
        style = ttk.Style()
#        style.configure('Tags.TButton', width='')
        TagsCheckboxManager.__init__(self, master, journal)
        
    def updateGUI(self, entry=None):
        if entry:
            TagsCheckboxManager.updateManager(self, entry)
        self.updateVarsList()
        self.clearCanvas()
        self.displayed_tags = []
        for tag in self.entry.getTags():
            self.displayed_tags.append(ttk.Button(master=self.canvas, takefocus=0, 
                                                  text=tag, style='Bold.UI.TButton'))
            self.displayed_tags[-1].config(command=lambda button=self.displayed_tags[-1]:self.updateButton(button))
        col = 10
        row = ceil(len(self.entry.getTags()) / col)
        grid = []
        grid = [(x,y) for y in range(0, row) for x in range(0, col)]
        for index in range(0, len(self.displayed_tags)):
            x, y = grid[index]
            self.displayed_tags[index].grid(column=x, row=y, sticky='ew')
        if len(self.displayed_tags) == 0:
            self.canvas.config(width=0)
            
    def clearGUI(self, entry):
        self.entry = entry
        self.clearCanvas()
        self.canvas.config(width=0)
                
    def updateFromStates(self, window=None):
        if type(window) is tk.Toplevel:
            window.destroy()
        states = self.getStates()
        for tag in states:
            if states[tag]:
                self.addTag(tag)
            else:
                self.removeTag(tag)
            
    def addTag(self, tag):
        TagsCheckboxManager.addTag(self, tag)
        self.updateGUI()
        
    def removeTag(self, tag):
        TagsCheckboxManager.removeTag(self, tag)
        self.updateGUI()
                    
    def createAddDialog(self):
        tags = simpledialog.askstring(title='Add Tags', prompt='Enter at least one tag, separating multiple tags with a comma:')
        if tags:
            tags = tags.split(',')
            for tag in tags:
                if tag.strip():
                    self.addTag(tag.strip())
        self.updateGUI()
        
    def createCheckboxDialog(self):
        root = tk.Toplevel(bg='slate gray')
        root.title('Tags')
        root.minsize(width=300, height=70)
        root.maxsize(width=root.winfo_screenwidth(), height=root.winfo_screenheight())
        canvas = tk.Canvas(root, highlightthickness=0, bg='slate gray')
        tagslist = self.getVarsList()
        if tagslist:
            for tag in tagslist:
                tagslist[tag][1] = tk.Checkbutton(master=canvas, text=tag, 
                        variable=tagslist[tag][0], bg='slate gray')
            tmp = sorted(tagslist.keys())
            row = ceil(sqrt(len(tmp)))
            col = ceil(len(tagslist) / row)
            grid = [(x, y) for x in range(0, col) for y in range(0, row) ]
            for i in range(0, len(tmp)):
                x, y = grid[i]
                tagslist[tmp[i]][1].grid(row=y, column=x, sticky='w')
        else:
            message = tk.Message(canvas, text='There is nothing to display.')
            message.pack()
        canvas.pack(padx=10, pady=7, side='left')
        root.grab_set()
        root.protocol("WM_DELETE_WINDOW", lambda window=root:self.updateFromStates(root))

    def updateButton(self, button):
        self.dialog = tk.Toplevel()
        self.dialog.grab_set()
        self.dialog.title('Change Tag')
        message = tk.Message(self.dialog, text='Enter a new tag here:', width=150)
        self.tag = ttk.Entry(self.dialog)
        self.tag.insert(0, button.cget('text'))
        button_box = tk.Frame(self.dialog, bg='slate gray')
        OK = ttk.Button(button_box, text='OK', 
                        command=lambda button=button:self.updateButtonText(button))
        CANCEL = ttk.Button(button_box, text='Cancel', command=self.dialog.destroy)
        DELETE = ttk.Button(button_box, text='Delete', 
                            command=lambda button=button:self.delete(button))
        message.pack(side='top')
        self.tag.pack(side='top')
        OK.pack(side='left')
        CANCEL.pack(side='left')
        DELETE.pack(side='left')
        button_box.pack(side='top')
        
    def updateButtonText(self, button):
        old = button.cget('text')
        new = self.tag.get()
        new = new.strip()
        button.config(text=new)
        self.dialog.destroy()
        self.removeTag(old)
        self.addTag(new)
        self.updateGUI()
        
    def delete(self, button):
        self.dialog.destroy()
#        delete = messagebox.askyesno(title='Delete?', message='Are you sure you want to delete this tag?')
        delete = True
        if delete:
            self.removeTag(button.cget('text'))
            self.updateGUI()
            
    def clearCanvas(self):
        for button in self.displayed_tags:
            button.destroy()
            
    def getCanvas(self):
        return self.canvas
   
            
class TagsFrame(tk.Frame, TagsCanvas):
    def __init__(self, master, journal=None, entry=None, **kw):
        self.entry = entry
        tk.Frame.__init__(self, master, **kw)
        ADD = ttk.Button(self, takefocus=0, width=15, text='Add', command=self.createAddDialog, 
                         style='Tags.Bold.UI.TButton')
        TagsCanvas.__init__(self, self, journal)
        TAGS = ttk.Button(self, takefocus=0, width=15, text='Tags:', command=self.createCheckboxDialog, 
                      style='Tags.Bold.UI.TButton')
        TAGS.pack(side='left')
        canvas = self.getCanvas()
        canvas.pack(side='left')
        ADD.pack(side='left')
        self.updateGUI(self.entry)
        
#    def clearGUI(self):
#        self.updateGUI(entry)
        
    def save(self):
        tags = self.entry.getTags()
        while not tags:
            self.createAddDialog()
            tags = self.entry.getTags()
        