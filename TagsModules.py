# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 09:50:53 2016

@author: Kozmik
"""
from tkinter import *
from tkinter.ttk import *
from JObject import *
from math import ceil
from math import sqrt
from tkinter import messagebox as messagebox
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
                self.vars[tag] = [BooleanVar(master=None, value=False, name='TF.'+tag), None]
            else: 
                self.vars[tag][0].set(False)
                self.vars[tag][1] = None
        for tag in self.entry.getTags():
            if tag in self.vars:
                self.vars[tag][0].set(True)
                self.vars[tag][1] = None
            else:
                self.vars[tag] = [BooleanVar(master=None, value=True, name='TF.'+tag), None]
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
        self.canvas = Canvas(master, height=1, width=0)
        self.tag = None
        self.dialog = None
        TagsCheckboxManager.__init__(self, master, journal)
        
    def updateGUI(self, entry=None):
        if entry:
            TagsCheckboxManager.updateManager(self, entry)
        self.updateVarsList()
        self.clearCanvas()
        self.displayed_tags = []
        for tag in self.entry.getTags():
            self.displayed_tags.append(Button(master=self.canvas, text=tag))
            self.displayed_tags[-1].config(command=lambda button=self.displayed_tags[-1]:self.updateButton(button))
        col = 10
        row = ceil(len(self.entry.getTags()) / col)
        grid = []
        grid = [(x,y) for y in range(0, row) for x in range(0, col)]
        for index in range(0, len(self.displayed_tags)):
            x, y = grid[index]
            self.displayed_tags[index].grid(column=x, row=y, sticky=EW)
        if len(self.displayed_tags) == 0:
            self.canvas.config(width=0)
            
    def clearGUI(self, entry):
        self.entry = entry
        self.clearCanvas()
        self.canvas.config(width=0)
                
    def updateFromStates(self, window=None):
        if type(window) is Toplevel:
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
        root = Toplevel()
        root.title('Tags')
        s=Style()
        print(s.theme_names())
        root.minsize(width=300, height=70)
        root.maxsize(width=root.winfo_screenwidth(), height=root.winfo_screenheight())
        canvas = Canvas(root, highlightthickness=0)
        tagslist = self.getVarsList()
        if tagslist:
            for tag in tagslist:
                tagslist[tag][1] = Checkbutton(master=canvas, text=tag, variable=tagslist[tag][0])
            tmp = sorted(tagslist.keys())
            row = ceil(sqrt(len(tmp)))
            col = ceil(len(tagslist) / row)
            grid = [(x, y) for x in range(0, col) for y in range(0, row) ]
            for i in range(0, len(tmp)):
                x, y = grid[i]
                tagslist[tmp[i]][1].grid(row=y, column=x, sticky=W)
        else:
            message = Message(canvas, text='There is nothing to display.')
            message.pack()
        canvas.pack(padx=10, pady=7, side=LEFT)
        root.grab_set()
        root.protocol("WM_DELETE_WINDOW", lambda window=root:self.updateFromStates(root))

    def updateButton(self, button):
        self.dialog = Toplevel()
        self.dialog.grab_set()
        self.dialog.title('Change Tag')
        message = Message(self.dialog, text='Enter a new tag here:', width=150)
        self.tag = Entry(self.dialog)
        self.tag.insert(0, button.cget('text'))
        button_box = Frame(self.dialog)
        OK = Button(button_box, text='OK', command=lambda button=button:self.updateButtonText(button))
        CANCEL = Button(button_box, text='Cancel', command=self.dialog.destroy)
        DELETE = Button(button_box, text='Delete', command=lambda button=button:self.delete(button))
        message.pack(side=TOP)
        self.tag.pack(side=TOP)
        OK.pack(side=LEFT)
        CANCEL.pack(side=LEFT)
        DELETE.pack(side=LEFT)
        button_box.pack(side=TOP)
        
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
   
            
class TagsFrame(Frame, TagsCanvas):
    def __init__(self, master, journal=None, entry=None):
        self.entry = entry
        Frame.__init__(self, master)
#        self.tags_frame = Frame(master)
        style =Style(self)
        style.configure('Tags.TButton', font=('Sans', '8', 'bold'), background='black')
        ADD = Button(self, text='Add', command=self.createAddDialog, style='Tags.TButton')
        TagsCanvas.__init__(self, self, journal)
        TAGS = Button(self, text='Tags:', command=self.createCheckboxDialog, style='Tags.TButton')
        TAGS.pack(side=LEFT)
        canvas = self.getCanvas()
        canvas.pack(side=LEFT)
        ADD.pack(side=LEFT)
        self.updateGUI(self.entry)
        
#    def clearGUI(self):
#        self.updateGUI(entry)
        
    def save(self):
        tags = self.entry.getTags()
        while not tags:
            self.createAddDialog()
            tags = self.entry.getTags()
        