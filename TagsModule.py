# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 00:45:40 2017

@author: Kozmik
"""

from TagTools import TagSelectionManager
import tkinter as tk
import tkinter.ttk as ttk
from math import ceil
from math import sqrt
import tkinter.simpledialog as simpledialog
from os.path import join

class TagsManager(TagSelectionManager):
    def __init__(self, master, journal, entry):
        self.master = master
        self.entry = entry
        TagSelectionManager.__init__(self, journal, False, 'TM.')
        self.active_tags = []
        self.new_tags = {}
        
    def updateActiveTagsList(self, entry):
        """Clears the temporary tags lists, updates and gets the tags of the 
        JEntry object, and updates the list of active tags"""
        if entry:
            self.entry = entry
            self.active_tags = []
#            self.new_tags = {}
            for tag in self.entry.getTags():
                self.addTag(tag)
            self.compareActiveStringFirst()
        else:
            self.checkStates()
            
    def loadEntry(self, entry=None):
        """"""
        if entry:      
            self.entry = entry
            for tag in self.entry.getTags():  #Assumes that the JEntry is already saved
                self.activateTag(tag)
            
    def addTag(self, tag):
        """Receives a tag in string format and creates a StringVar to track it 
        as active"""
        if tag:
            if tag not in self.getActiveStrings():
                self.active_tags.append(tag)
            
    def removeTag(self, tag):
        """Receives a tag in string format and removes it from the list of 
        active tags, destroying its StringVar"""
        if tag in self.getActiveStrings():
            index = None
            for i in range(len(self.active_tags)):
                if self.active_tags[i] == tag:
                    index = i
            self.active_tags.pop(index)
            
    def activateTag(self, tag):
        """Receives a tag in string format and creates and sets the associated 
        BooleanVar"""
        if tag in self.vars:
            self.vars[tag][0].set(1)
        elif tag not in self.new_tags:
            self.new_tags[tag] = [tk.BooleanVar(master=None, value=True, name=self.id+tag), None]
        else:
            self.new_tags[tag][0].set(1)

    def deactivateTag(self, tag):
        """Receives a tag in string format and removes the tag from the list of 
        active tags and sets its associated BooleanVar to 0"""
        if tag in self.vars:
            self.vars[tag][0].set(0)
        elif tag in self.new_tags:
            self.new_tags[tag][0].set(0)
            
    def deactivateAllTags(self):
        for tag in self.active_tags:
            self.deactivateTag(tag)
        
    def activateAllTags(self):
        for tag in self.new_tags:
            self.activateTag(tag)
        for tag in self.vars:
            self.activateTag(tag)
            
    def saveTagsToEntry(self):
        """Writes the list of active tags to the JEntry"""
        if self.active_tags:
            for tag in self.active_tags:
                self.entry.addTag(tag)
            tags = self.entry.getTags()
            for tag in tags:
                if tag not in self.getActiveStrings():
                    self.entry.removeTag(tag)
            
    def getStatesStrings(self):
        """Returns the list of StringVars that tracks active tags"""
        return self.active_tags
    
    def getActiveStrings(self):
        """Returns a list of active tags, in string format"""
        return sorted(self.active_tags)
    
    def getActiveBoolVars(self):
        active = super().getActiveBoolVars()
        for tag in self.new_tags:
            if self.new_tags[tag][0].get():
                active.append(tag)
        return active
    
    def getAllTags(self):
        """Returns a dict of all tags, both temporary and permanent"""
        all_tags = {}
        for tag in self.vars:
            all_tags[tag] = self.vars[tag]
        for tag in self.new_tags:
            all_tags[tag] = self.new_tags[tag]
        return all_tags
        
    def compareActiveBoolFirst(self):
        active_bool = self.getActiveBoolVars()
        active_str = self.getActiveStrings()
        for item in active_bool:
            if item not in active_str:
                self.addTag(item)
        for item in active_str:
            if item not in active_bool:
                self.removeTag(item)

    def compareActiveStringFirst(self):
        active_str = self.getActiveStrings()
        active_bool = self.getActiveBoolVars()
        for item in active_str:
            if item not in active_bool:
                self.activateTag(item)
        for item in active_bool:
            if item not in active_str:
                self.deactivateTag(item)              
    
class TagButton(ttk.Button):
    def __init__(self, master, controller, tag, **kw):
        self.master = master
        self.controller = controller
        self.tag = tag                    #Expects a String
        self.args = kw
        self.dialog = None
        self.entry = None
        self.iconpath = join(self.args['homepath'], 'Resources\\web.ico')
        ttk.Button.__init__(self, master, text=self.tag, width='', 
                            style='Tags.Variable.UI.TButton', command=self.changeButton)
        
    def changeButton(self):
        """Creates a dialog window so that the user can change the Button's tag"""
#        kw = {'bg': 'slate gray'}
        self.dialog = tk.Toplevel(self.args['bgcolor1'])
        self.dialog.grab_set()
        self.dialog.title('Edit Tag')
        self.dialog.iconbitmap(self.iconpath)
        message = ttk.Label(self.dialog, text='Enter a new tag here: ')
        self.entry = ttk.Entry(self.dialog)
        self.entry.insert(0, self.tag)
        frame = ttk.Frame(self.dialog)
        OK = ttk.Button(frame, text='OK', command=self.updateTags)
        DELETE = ttk.Button(frame, text='Delete', 
                            command=self.destroyButton)
        message.pack(side='top')
        self.entry.pack(side='top')
        OK.pack(side='left')
        DELETE.pack(side='left')
        frame.pack(side='top')
        self.dialog.grab_set()
        self.entry.focus_force()
        
    def updateTags(self):
        old = self.tag
        self.tag = self.entry.get()
        self.config(text=self.tag)
        self.controller.updateTag(old, self.tag)
        self.dialog.destroy()
        self.dialog = None
        self.entry = None
        
    def destroyButton(self):
        self.controller.deleteTag(tag=self.tag)
        self.dialog.destroy()
        self.dialog = None
        self.destroy()
        
class TagsFrame(ttk.Frame, TagsManager):
    def __init__(self, master, journal, entry, **kw):
        self.journal = journal
        self.entry = entry
        self.args = kw
        self.iconpath = join(self.args['homepath'], 'Resources\\web.ico')
        
        self.tags_var = None
        TagsManager.__init__(self, self, journal, entry)
        
        ttk.Frame.__init__(self, master)
        self.config()
        self.ybar = ttk.Scrollbar(self)
        canvas_frame = ttk.Frame(self)
        self.canvas = tk.Canvas(canvas_frame, yscrollcommand=self.ybar.set, 
                                bg=self.args['bgcolor2'])
        self.ybar.config(command=self.canvas.yview)
        button_frame = ttk.Frame(self, relief=self.args['relief'], 
                                 border=self.args['border'])
        self.TAGS = ttk.Button(button_frame, takefocus=0, text='Tags', state='disabled', 
                               command=self.displayTagsDialog, style='Tags.Bold.UI.TButton')
        self.ADD = ttk.Button(button_frame, takefocus=0, text='Add', 
                              command=self.displayAddDialog, style='Tags.Bold.UI.TButton')
        self.TAGS.grid(row=0, column=0)
        self.ADD.grid(row=1, column=0)
        self.canvas.grid(row=0, column=1)
        button_frame.grid(row=0, column=0, sticky='nwes')
        canvas_frame.grid(row=0, column=1, sticky='nw', padx=4)
        self.update_idletasks()
        self.dialog = None
        
    def updateGUI(self, entry):
        self.entry = entry
        if self.getAllTags():
            self.TAGS.config(state='normal')
        self.updateActiveTagsList(entry)
        self.placeTags()          
        
    def clearGUI(self, entry):
        self.entry = entry
        self.updateActiveTagsList(entry)
        self.placeTags()
        
    def placeTags(self, event=None):
        self.ybar.grid_forget()
        for f in self.canvas.grid_slaves():
            f.destroy()
        frame = ttk.Frame(self.canvas)
        frame.grid(sticky='nw')
        height=1
        for var in sorted(self.getStatesStrings()):
            button = TagButton(frame, self, var, takefocus=0, **self.args)                
            button.pack(side='left')
            self.update_idletasks()
            if frame.winfo_width()+self.TAGS.winfo_width()>=self.winfo_width():
                frame = ttk.Frame(self.canvas)
                button.destroy()
                button = TagButton(frame, self, var, takefocus=0, style='Bold.UI.TButton', 
                                   **self.args)
                frame.grid(sticky='nw')
                height+=1
                button.pack(side='left')
                self.update_idletasks()
        if height>3:
            self.ybar.grid(column=2, row=0, sticky='nse')
                
    def displayTagsDialog(self):
        self.tags_var = self.getAllTags()
        
        self.dialog = tk.Toplevel(master=self, bg=self.args['bgcolor1'])
#        self.dialog.config(relief='flat')
        self.dialog.title('Tags')
        self.dialog.iconbitmap(self.iconpath)
        canvas = tk.Canvas(self.dialog, highlightthickness=0, bg=self.args['bgcolor1'])
        canvas.config(relief='flat')
        for tag in self.tags_var:
            self.tags_var[tag][1] = ttk.Checkbutton(master=canvas, text=tag, 
                        variable=self.tags_var[tag][0])
            tmp = sorted(self.tags_var.keys())
            row = ceil(sqrt(len(tmp)))
            col = ceil(len(self.tags_var) / row)
            grid = [(x, y) for x in range(0, col) for y in range(0, row) ]
        for i in range(0, len(tmp)):
            x, y = grid[i]
            self.tags_var[tmp[i]][1].grid(row=y, column=x, sticky='w')
        self.dialog.update_idletasks()
        canvas.pack(padx=10, pady=7, side='left')
        self.dialog.grab_set()
        self.dialog.focus_force()
        self.dialog.protocol("WM_DELETE_WINDOW", self.destroySelectionDialog)
        
    def destroySelectionDialog(self):
        self.compareActiveBoolFirst()
        self.dialog.destroy()
        self.placeTags()
        self.dialog = None
        self.tags_var = None

    def displayAddDialog(self):
        self.tags_var = tk.StringVar()
        
        self.dialog = tk.Toplevel(bg=self.args['bgcolor1'])
        self.dialog.title('Add')
        self.dialog.iconbitmap(self.iconpath)
        text = 'Enter at least one tag, separating multiple tags with a comma: '
        message = ttk.Label(self.dialog, text=text)
#        message.config(relief='flat')
        entry = tk.Entry(self.dialog, textvariable=self.tags_var)
        message.pack()
        entry.pack(expand=True, fill='x')
        entry.focus_force()
        self.dialog.grab_set()
        self.dialog.protocol("WM_DELETE_WINDOW", self.destroyAddDialog)

    def destroyAddDialog(self):
        tags = self.tags_var.get()
        tags = tags.split(',')
        for tag in tags:
            self.addTag(tag.strip())
        self.compareActiveStringFirst()
        self.placeTags()
        self.dialog.destroy()
        self.dialog = None
        self.tags_var = None

    def createAddDialog(self):
        tags = simpledialog.askstring(title='Add Tags', 
                                      prompt='Enter at least one tag, ' +\
                                      'separating multiple tags with a comma:')
        if tags:
            tags = tags.split(',')
            for tag in tags:
                if tag.strip():
                    self.addTag(tag.strip())
            self.compareActiveStringFirst()
        
    def save(self):
        """This is annoying behavior and needs fixing"""
        while not self.getActiveStrings():
            self.createAddDialog()
        self.saveTagsToEntry()
        self.updateGUI(self.entry)
        
    def deleteTag(self, tag):
        self.deactivateTag(tag)
        self.removeTag(tag)
        
    def updateTag(self, oldtag, newtag):
        self.addTag(newtag.strip())
        self.removeTag(oldtag)
        self.compareActiveStringFirst()