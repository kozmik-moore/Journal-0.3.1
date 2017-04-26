# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 15:00:50 2016

@author: Kozmik
"""
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from JObject import JEntry
from BodyModules import BodyFrame
from TagsModules import TagsFrame
from Storage import Storage
from DateModule import DateFrame
import DateTools
import textwrap
from GraphTools import JGraph
from AttachmentTools import AttachmentManager
                
class Main(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (w*.95, h*.8))
        self.config(background='slate gray')
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
            
        style = JournalStyle()
        style.setNightStyle()
        
        self.backup_interval_var = self.storage.getBackupIntervalVar()
        self.journal_auto_save = self.storage.getAutosaveVar()
        self.last_backup_var = self.storage.getLastBackupVar()
        
        self.top_frame = tk.Frame(self, bg='slate gray')
        top_left_frame = tk.Frame(self.top_frame, width=100)
        self.date_frame = DateFrame(self.top_frame, self.entry, self.journal, 
                                    self, width=100, bg='slate gray')
        top_right_frame = tk.Frame(self.top_frame, bg='slate gray')
        self.body_frame = BodyFrame(self, self.entry, bg='slate gray')
        self.body_frame.config(border=5, relief='ridge')
        self.tags_frame = TagsFrame(self, self.journal, self.entry, bg='slate gray',
                                    relief='ridge', border=5)
        self.lower_frame = tk.Frame(self, bg='slate gray')
        self.lower_left = tk.Frame(self.lower_frame, bg='slate gray')
        self.options_frame = tk.Frame(self.lower_frame, bg='slate gray', 
                                      relief='ridge', border=5)
        self.lower_right = tk.Frame(self.lower_frame, bg='slate gray')
        self.jgraph = JGraph(self.options_frame, self, self.journal, self.entry, 
                             bg='slate gray')
        self.attachmanager = AttachmentManager(self.options_frame, self, self.journal, 
                                               self.entry, bg='slate gray')

#        top_left_frame.grid(row=0, column=1)
        self.date_frame.grid(row=0, column=0, padx=5, sticky='w')
        top_right_frame.grid(row=0, column=2)
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=2)
        self.top_frame.grid_columnconfigure(2, weight=0)
        self.top_frame.pack(side='top', expand=True, fill='x', padx=5)
        self.body_frame.pack(side='top', expand=True, fill='both', padx=5)
        self.tags_frame.pack(side='top', expand=True, fill='x', padx=5)
        
        self.LAST_BACKUP_LABEL = ttk.Label(top_right_frame, text='Last Backup: ')
        self.LAST_BACKUP = ttk.Label(top_right_frame, textvariable=self.last_backup_var)
        self.LAST_BACKUP.pack(side='right', padx=3)
        self.LAST_BACKUP_LABEL.pack(side='right')
        
        self.lower_left.pack(side='left', expand=True, fill='x')
        self.options_frame.pack(side='left')
        self.lower_right.pack(side='left', expand=True, fill='x')
        self.lower_frame.pack(side='top', expand=True, fill='x', padx=5)
        
        self.SAVE = ttk.Button(self.options_frame, takefocus=0, text="Save", command=self.save)
        self.SAVE.grid(row=0, column=0)
        self.NEW = ttk.Button(self.options_frame, takefocus=0, text="New Entry", command=self.newEntry)
        self.NEW.grid(row=0, column=6)
        self.QUIT = ttk.Button(self.options_frame, takefocus=0, text="Quit", command=self.destroyApp)
        self.QUIT.grid(row=1, column=0)
        self.DELETE = ttk.Button(self.options_frame, takefocus=0, text="Delete", command=self.delete)
        self.DELETE.grid(row=1, column=6)
        self.jgraph.grid(row=0, column=2, rowspan=2)
        self.attachmanager.grid(row=0, column=4, rowspan=2)
        
        menubar = tk.Menu(self)
        
        journal_menu = tk.Menu(menubar, tearoff=0)
        journal_menu.add_command(label='Save All Changes', command=self.writeToDatabase)
        pref_menu = tk.Menu(journal_menu, tearoff=0)
        journal_menu.add_cascade(label='Database Preferences', menu=pref_menu)
        journal_menu.add_command(label='Quit', command=self.destroyApp)
        
        entry_menu = tk.Menu(menubar, tearoff=0)
        entry_menu.add_command(label='Save', command=self.save)
        entry_menu.add_command(label='Delete', command=self.delete)
#        pref_menu.add_command(label='Autosave changes on exit', command=self.changeAutoSavePref)
        pref_menu.add_command(label="Select Save Directory", command=self.storage.changeSaveDirectory)
        backup_menu = tk.Menu(pref_menu, tearoff=0)
        backup_menu.add_command(label='Select Backup Directory', command=self.storage.changeBackupDirectory)
        self.interval_menu = tk.Menu(backup_menu, tearoff=0)
        self.interval_menu.add_command(label='Immediately', command=self.storage.backupDatabase)
        self.interval_menu.add_radiobutton(label='Day', var=self.backup_interval_var, value=24, command=self.storage.changeBackupSchedule)
        self.interval_menu.add_radiobutton(label='3 Days', var=self.backup_interval_var, value=72, command=self.storage.changeBackupSchedule)
        self.interval_menu.add_radiobutton(label='Week', var=self.backup_interval_var, value=168, command=self.storage.changeBackupSchedule)
        self.interval_menu.add_radiobutton(label='Never', var=self.backup_interval_var, value=-1, command=self.storage.changeBackupSchedule)

        backup_menu.add_cascade(label='Backup Database Every...', menu=self.interval_menu)
        pref_menu.add_cascade(label='Backup Options', menu=backup_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.createAboutWindow)
        
        menubar.add_cascade(label='Journal', menu=journal_menu)
        menubar.add_cascade(label="Entry", menu=entry_menu)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)
        menubar.config(bg='slate gray')
        
        self.protocol("WM_DELETE_WINDOW", self.destroyApp)
        self.bindDateControl()
        self.storage.runBackup()
        self.updateGUI(entry=self.entry)
                
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
        if not self.body_frame.bodyFieldIsEmpty(): # and not self.date_frame.getDate():
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
        self.attachmanager.updateGUI(self.entry)
        self.jgraph.updateGUI(self.entry)
        self.body_frame.grabFocus()
        
    def clearGUI(self):
        self.entry = JEntry()
        self.date_frame.clearGUI(self.entry)
        self.body_frame.clearGUI(self.entry)
        self.tags_frame.clearGUI(self.entry)
        self.attachmanager.clearGUI(self.entry)
        self.jgraph.clearGUI(self.entry)
        self.body_frame.grabFocus()
        
    def bindDateControl(self):
        self.date_frame.bindDatebox(self.updateGUI)
            
    def save(self):
        self.date_frame.save()
        self.body_frame.save()
        self.tags_frame.save()
        self.attachmanager.save()
        if self.entry.getParent():
            date = self.entry.getParent()
            parent = self.journal.getEntry(date)
            parent.linkChild(self.entry.getDate())
        self.journal.add(self.entry)
        
    def writeToDatabase(self):
        self.save()
        self.storage.saveJournal()
        
    def delete(self):
        date = self.entry.getDate()
        if not date and not self.body_frame.bodyFieldIsEmpty():
            self.clearGUI()
        if date:
            selection = messagebox.askyesno("Delete Entry", "Delete this entry?")
            if selection:
                self.jgraph.deleteEntry(self.entry.getDate())
                self.journal.delete(self.entry)
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
                
class JournalStyle(ttk.Style):
    def __init__(self):
        ttk.Style.__init__(self)
        self.frame_list = []
        self.theme_create('shadow', parent='default')
        self.theme_settings('shadow', {
                'TButton': {
                        'configure': {'padding': 3, 'foreground': 'black', 'relief': 'raised',
                                      'font': 'TkDefaultFont', 'background': 'slate gray', 
                                      'anchor': 'center', 'borderwidth': 1, 'width':15},
                        'layout': 
                            [('Button.border', {'sticky': 'nswe', 'children': 
                                [('Button.focus', {'sticky': 'nswe', 'children': 
                                    [('Button.padding', {'sticky': 'nswe', 'children': 
                                        [('Button.label', {'sticky': 'nswe', 'expand':1})]})]})]})],
                        'map': {'foreground': [('disabled', 'dark slate gray'), ('pressed', 'black'), 
                                               ('active', 'black')],
                                'background': [('disabled', 'slate gray'), ('pressed', 'slate gray'), 
                                               ('active', 'light slate gray')],
                                'relief': [('pressed', 'flat'), ('!pressed', 'raised')]}},
                'TLabel': {
                        'configure': {'background': 'slate gray', 'foreground': 'black'}},
                'TCombobox': {
#                        'layout': 
#                            [('Combobox.border', {'sticky': 'nswe', 'children': 
#                                [('Combobox.rightdownarrow', {'side': 'right', 'sticky': 'news'}), 
#                                 ('Combobox.padding', {'expand': '1', 'sticky': 'nswe', 'children': 
#                                     [('Combobox.focus', {'expand': '1', 'sticky': 'nswe', 'children': 
#                                         [('Combobox.textarea', {'sticky': 'nswe'})]})]})]})],
                        'map': {'focusfill': [('readonly', 'focus', 'SystemHighlight')], 
                                'foreground': [('disabled', 'SystemGrayText'), 
                                               ('readonly', 'focus', 'black')], 
                                'selectforeground': [('!focus', 'black'), ('focus', 'black')], 
                                'selectbackground': [('!focus', 'white'), ('focus', 'gray70')]}},
                'TCheckbutton': {
                        'configure': {'indicatoron': 1}},
                'TScrollbar': {
                        'configure': {'background': 'slate gray', 'foreground': 'white'}},
                'UI.TButton': {
                        'configure': {'width': ''}},
                'Current.UI.TButton': {
                        'configure': {'background': 'black', 'foreground': 'white'},
                        'map': {'foreground': [('active', 'white'), ('pressed', 'white')],
                                               'background': [('active', 'gray10'), ('pressed', 'gray10')]}},
                'Bold.UI.TButton': {
                        'configure': {'font': ('TkDefault', '9', 'bold')}},
                'Tags.Bold.UI.TButton': {
                        'configure':{'foreground': 'black', 
                                     'font': ('TkDefault', '9', 'bold', 'underline')},
                        'map': {'foreground': [('disabled', 'dark slate gray'), ('pressed', 'black'), 
                                               ('active', 'black')]}}})

        
    def setDayStyle(self):
        self.theme_use('default')
        
    def setNightStyle(self):
        self.theme_use('shadow')
        
    def addFrame(self, frame):
        self.frame_list.append(frame)
            
        
app=Main()
app.mainloop()