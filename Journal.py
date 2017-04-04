# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 15:00:50 2016

@author: Kozmik
"""
from tkinter import *
from tkinter.ttk import *
import pickle
import tkinter.messagebox as messagebox
from inspect import getsourcefile
from os.path import abspath
from tkinter import filedialog as filedialog
import os
import pdb
from JObject import *
from BodyModules import *
#from DateFrame import *
from TagsModules import *
from Storage import *
from DateModule import *
import DateTools
import textwrap
from GraphTools import *
import pdb
                
class Main(Tk):
    def __init__(self):
        Tk.__init__(self)
        
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (w*.9, h*.8))
        self.title('Journal')
        self.storage = Storage()
        self.storage.LoadIniFile()
        self.storage.openJournalFile()
        self.journal = self.storage.getJournal()
        self.entry = None
        if self.journal.isEmpty():
            date = DateTools.getCurrentDate()
            body = textwrap.dedent("Welcome!\n\nThis entry is to provide a little guidance if you happen "
            "to have any questions. Keep in mind that this is a work in progress, so...bugs ahead! "
            "That being said, onto the tutorial."
            "\n\nThis panel you are reading from is where you write entries. If you want to make a new entry, "
            "click the button marked \"New Entry\"."
            "\n\nClicking the button marked \"Linked Entry\" from an entry that is already saved "
            "will make a new entry that is \"connected\" to the previous one. The \"Tags\" button "
            "allows you to select and deselect tags to add to your entry and the \"Filter\" button "
            "lets you filter dates from the datebar by their associated tags."
            "\n\nWhen you open the Filter dialog, there will be three radiobutton marked \"OR\", "
            "\"AND\", and \"OR(P)\". Selecting tags while the \"OR\" button is selected "
            "narrows dates to any containing at least those tags. \"AND\" returns dates that "
            "have those tags and only those tags. \"OR(P)\" gives those dates that have at "
            "least one of those tags and not any dates that have tags which are not selected. "
            "(For those of you who know, think \"power sets\".)"
            "\n\n\"Save\" saves your entries and \"Delete\" deletes them from the database. "
            "\"Quit\" exits the application, saving all changes on the way out. Closing the "
            "window with the \"X\" in the corner will accomplish the same thing."
            "\nThe \"Display Linked Entries\" button is for a future implementation where you "
            "will have a visual representation of your interconnected thoughts. This is the "
            "primary reason I developed this, so that you could see how your thoughts are "
            "networked together as they develop over time."
            "\n\nThe \"Preferences\" menu allows you to change your database location, "
            "backup location, how often the app will backup the database, and contains an "
            "option to backup immediately."
            "\n\nThe \"Help\" menu has details of where I can be contacted, if further "
            "questions arise or you want to look at the code."
            "\n\nGood writing!")
            tags = ['Welcome']
            self.entry = JEntry(date, body, tags)
            self.journal.add(self.entry)
        else:
            self.entry = JEntry()
#        self.buffer_entry = None
        self.backup_interval_var = self.storage.getBackupIntervalVar()
        self.journal_auto_save = self.storage.getAutosaveVar()
        self.last_backup_var = self.storage.getLastBackupVar()
        
        self.top_frame = Frame(self)
        self.date_frame = DateFrame(self.top_frame, self.entry, self.journal, self)
        self.body_frame = BodyFrame(self, self.entry)
        self.tags_frame = TagsFrame(self, self.journal, self.entry)
        self.options_frame = Frame(self)
        
        self.jgraph = JGraph(self, self.journal)
        
        self.date_frame.pack(side=TOP, expand=True, fill=X)
        self.top_frame.pack(side=TOP, expand=True, fill=X)
        self.body_frame.pack(side=TOP, expand=True, fill=BOTH)
        self.tags_frame.pack(side=TOP, expand=True, fill=X)
        
        self.LAST_BACKUP_LABEL = Label(self.top_frame, text='Last Backup: ')
        self.LAST_BACKUP = Label(self.top_frame, textvariable=self.last_backup_var)
        self.LAST_BACKUP.pack(side=RIGHT)
        self.LAST_BACKUP_LABEL.pack(side=RIGHT)
        
        self.SAVE = Button(self.options_frame, text="Save", command=self.save).grid(row=0, column=0, columnspan=2)
        self.LINK = Button(self.options_frame, text="Create Linked Entry", command=self.newLink).grid(row=0, column=2, columnspan=2, sticky=EW)
        self.NEW = Button(self.options_frame, text="New Entry", command=self.newEntry).grid(row=0, column=4, columnspan=2)
        self.QUIT = Button(self.options_frame, text="Quit", command=self.destroyApp).grid(row=1, column=0, columnspan=2)
        self.LINKS = Button(self.options_frame, text="Display Linked Entries", command=self.displayLinks).grid(row=1, column=2, columnspan=2)
        self.DELETE = Button(self.options_frame, text="Delete", command=self.delete).grid(row=1, column=4)
#        self.FIX = Button(self.options_frame, text='FIX!', command=self.fixParent).grid(row=1, column=5)
        self.options_frame.pack(side=TOP)
        
        menubar = Menu(self)
        pref_menu = Menu(menubar, tearoff=0)
        pref_menu.add_command(label='Autosave changes on exit', command=self.changeAutoSavePref)
        pref_menu.add_command(label="Select Save Directory", command=self.storage.changeSaveDirectory)
        backup_menu = Menu(pref_menu, tearoff=0)
        backup_menu.add_command(label='Select Backup Directory', command=self.storage.changeBackupDirectory)
        self.interval_menu = Menu(backup_menu, tearoff=0)
        self.interval_menu.add_command(label='Immediately', command=self.storage.backupDatabase)
        self.interval_menu.add_radiobutton(label='Day', var=self.backup_interval_var, value=24, command=self.storage.changeBackupSchedule)
        self.interval_menu.add_radiobutton(label='3 Days', var=self.backup_interval_var, value=72, command=self.storage.changeBackupSchedule)
        self.interval_menu.add_radiobutton(label='Week', var=self.backup_interval_var, value=168, command=self.storage.changeBackupSchedule)
        self.interval_menu.add_radiobutton(label='Never', var=self.backup_interval_var, value=-1, command=self.storage.changeBackupSchedule)

        backup_menu.add_cascade(label='Backup Database Every: ', menu=self.interval_menu)
        pref_menu.add_cascade(label='Backup Options', menu=backup_menu)
        
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.createAboutWindow)
        
        menubar.add_cascade(label="Preferences", menu=pref_menu)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)
        
        self.protocol("WM_DELETE_WINDOW", self.destroyApp)
        self.bindDateControl()
        self.storage.runBackup()
        self.updateGUI(self.entry)
                
    def createAboutWindow(self):
        message = "Journal 0.3.1\nAuthor: kozmik-moore @ GitHub\nDeveloped using the Anaconda 4.3.1 Suite (Python 3.6)"
        main = messagebox.Message(title="About", message=message)
        main.show()
        
    def destroyApp(self):
        if self.entry.getDate() or not self.body_frame.bodyFieldIsEmpty():
            self.save()
        self.storage.saveJournal(self.journal)
        self.storage.saveIniFile()
        self.destroy()

    def changeAutoSavePref(self):
        self.storage.toggleAutoSave()
        if self.journal_auto_save.get():
            message = 'Journal autosave is ON.'
        else:
            message = 'Journal autosave is OFF'
        messagebox.showinfo(title='Autosave', message=message)
        
    def updateGUI(self, event=None, entry=None):
        if not self.body_frame.bodyFieldIsEmpty() and not self.date_frame.getDate():
            self.save()
        date = self.date_frame.indexDate()
        if entry:
            self.entry = entry
        elif date:
            self.entry = self.journal.getEntry(date)
        else:
            self.entry = JEntry()
        self.date_frame.updateGUI(self.entry)
        self.body_frame.updateGUI(self.entry)
        self.tags_frame.updateGUI(self.entry)
        
    def clearGUI(self):
        self.entry = JEntry()
        self.date_frame.clearGUI(self.entry)
        self.body_frame.clearGUI(self.entry)
        self.tags_frame.clearGUI(self.entry)       
        
    def bindDateControl(self):
        self.date_frame.bindDatebox(self.updateGUI)
        
    def journalIsChanged(self):
        if self.storage.journalIsSaved(self.journal):
            return False
        else:
            return True
            
    def entryIsChanged(self):
        date = self.entry.getDate()
        storage = self.storage.getJournal()
        if not date:
            return True
        if date in storage.getAllDates():
            if not storage.getEntry(date).equals(self.entry):
                return True
            if self.entry.getBody() != self.body_frame.getBody():
                return True
            if self.entry.getTags() != storage.getEntry(date).getTags():
                return True
        elif date in self.journal.getAllDates():
            if self.entry.getBody() != self.body_frame.getBody():
#            if self.journal.getEntry(date).equals(self.entry):
                return True
        return False
                
    def throwSaveWarning(self):
#        selection = messagebox.askyesno('Save Entry', 'Save before continuing?')
#        if selection:
        self.save()
            
    def throwFinalSaveWarning(self):
        """Needs more thought before fully implementing:
        leaves filestreams open when 'no' is selected"""
#        selection = messagebox.askyesno("Save All Changes", "Save all changes before exiting?")
#        if selection:
        self.storage.saveJournal(self.journal)
#        else:
#            self.storage.closeStreams()
            
    def save(self):
        self.date_frame.save()
        self.body_frame.save()
        self.tags_frame.save()
        if self.entry.getParent():
            date = self.entry.getParent()
            parent = self.journal.getEntry(date)
            parent.linkChild(self.entry.getDate())
        self.journal.add(self.entry)
        
    def delete(self):
        if self.entry.getDate():
            selection = messagebox.askyesno("Delete Entry", "Delete this entry?")
            if selection:
                self.jgraph.deleteEntry(self.entry.getDate())
                self.journal.delete(self.entry)
                entry = JEntry()
                self.clearGUI()
            else:
                self.clearGUI()
            
    def newEntry(self):
        if self.entry.getDate() or not self.body_frame.bodyFieldIsEmpty():
            self.save()
        self.updateGUI(entry=JEntry())
        
    def newLink(self):
        if self.entry.getDate() or not self.body_frame.bodyFieldIsEmpty():
            self.save()
            self.updateGUI(entry=JEntry(parent=self.entry.getDate(), tags=self.entry.getTags()))
        
    def displayLinks(self):
        if self.entry.getDate():
            if not self.entry.getChild() and not self.entry.getParent():
                message = "No linked entries to display!"
                main = messagebox.Message(title='Linked Entries', message=message)
                main.show()
            else:
                self.jgraph.creatGraphDialog(self.entry.getDate())
            
        
app=Main()
app.mainloop()