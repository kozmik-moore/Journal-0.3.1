# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 15:00:50 2016

@author: Kozmik
"""
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from JObject import JEntry
from BodyModule import BodyFrame
from TagsModule import TagsFrame
from Storage import Storage
from DateModule import DateFrame
from os.path import join
#import DateTools
#import textwrap
from GraphTools import JGraph
from AttachmentTools import AttachmentManager
                
class Main(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (w*.95, h*.8))
        self.config(background='slate gray')
#        self.overrideredirect(1)
        self.title('kunnekted-jurnl')
        self.storage = Storage()
        self.app_loc = self.storage.getPath()
        iconpath = join(self.app_loc, 'Resources\\web.ico')
        self.iconbitmap(iconpath)
        messagepath = (join(self.app_loc, 'Resources\\Messages'))
        messagefile = open(messagepath)
        self.messages = messagefile.read()
#        self.storage.LoadIniFile()
#        self.storage.openJournalFile()
        self.journal = self.storage.getJournal()
#        self.storage.runBackup()
        self.entry = JEntry()
        kw = {'journal':self.journal, 'jentry': self.entry, 
                    'icon': iconpath, 'messages': self.messages,
                    'app': self.app_loc, 'controller': self, 
                    'bg': 'slate gray'}
   
        style = JournalStyle()
        style.setNightStyle()
        
        self.backup_interval_var = self.storage.getBackupIntervalVar()
        self.journal_auto_save = self.storage.getAutosaveVar()
        self.last_backup_var = self.storage.getLastBackupVar()
        
        self.top_frame = tk.Frame(self, bg='slate gray')
#        top_left_frame = tk.Frame(self.top_frame, width=100)
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
        self.jgraph = JGraph(self.options_frame, self, self.journal, 
                             self.entry, self.app_loc, bg='slate gray')
        self.attachmanager = AttachmentManager(self.options_frame, self, 
                                               self.app_loc, self.journal, 
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
        self.LAST_BACKUP = ttk.Label(top_right_frame, 
                                     textvariable=self.last_backup_var)
        self.LAST_BACKUP.pack(side='right', padx=3)
        self.LAST_BACKUP_LABEL.pack(side='right')
        
        self.lower_left.pack(side='left', expand=True, fill='x')
        self.options_frame.pack(side='left')
        self.lower_right.pack(side='left', expand=True, fill='x')
        self.lower_frame.pack(side='top', expand=True, fill='x', padx=5)
        
        self.SAVE = ttk.Button(self.options_frame, takefocus=0, text="Save", 
                               command=self.save)
        self.SAVE.grid(row=0, column=0)
        self.NEW = ttk.Button(self.options_frame, takefocus=0, text="New Entry", 
                              command=self.newEntry)
        self.NEW.grid(row=0, column=6)
        self.QUIT = ttk.Button(self.options_frame, takefocus=0, text="Quit", 
                               command=self.destroyApp)
        self.QUIT.grid(row=1, column=0)
        self.DELETE = ttk.Button(self.options_frame, takefocus=0, text="Delete", 
                                 command=self.delete)
        self.DELETE.grid(row=1, column=6)
        self.jgraph.grid(row=0, column=2, rowspan=2)
        self.attachmanager.grid(row=0, column=4, rowspan=2)
        
        menubar = tk.Menu(self, bg='slate gray')
        
        journal_menu = tk.Menu(menubar, bg='slate gray', tearoff=0)
        journal_menu.add_command(label='Save All Changes', 
                                 command=self.writeToDatabase)
        pref_menu = tk.Menu(journal_menu, bg='slate gray', tearoff=0)
        journal_menu.add_cascade(label='Database Preferences', menu=pref_menu)
        journal_menu.add_command(label='Quit', command=self.destroyApp)
        
        entry_menu = tk.Menu(menubar, bg='slate gray', tearoff=0)
        entry_menu.add_command(label='Save', command=self.save)
        entry_menu.add_command(label='Delete', command=self.delete)
#        pref_menu.add_command(label='Autosave changes on exit', command=self.changeAutoSavePref)
        pref_menu.add_command(label="Change Save Directory", 
                              command=self.storage.changeSaveDirectory)
        backup_menu = tk.Menu(pref_menu, bg='slate gray', tearoff=0)
        backup_menu.add_command(label='Change Backup Directory', 
                                command=self.storage.changeBackupDirectory)
        self.interval_menu = tk.Menu(backup_menu, bg='slate gray', tearoff=0)
        self.interval_menu.add_command(label='Immediately', 
                                       command=self.storage.backupDatabase)
        self.interval_menu.add_radiobutton(label='Day', 
                                           var=self.backup_interval_var, 
                                           value=24, 
                                           command=self.storage.changeBackupSchedule)
        self.interval_menu.add_radiobutton(label='3 Days', 
                                           var=self.backup_interval_var, 
                                           value=72, 
                                           command=self.storage.changeBackupSchedule)
        self.interval_menu.add_radiobutton(label='Week', 
                                           var=self.backup_interval_var, 
                                           value=168, 
                                           command=self.storage.changeBackupSchedule)
        self.interval_menu.add_radiobutton(label='Never', 
                                           var=self.backup_interval_var, 
                                           value=-1, 
                                           command=self.storage.changeBackupSchedule)

        backup_menu.add_cascade(label='Backup Database Every...', 
                                menu=self.interval_menu)
        pref_menu.add_cascade(label='Backup Options', menu=backup_menu)
        pref_menu.add_command(label="Change Imports Directory", 
                              command=self.storage.changeImportsDirectory)
        

        help_menu = tk.Menu(menubar, bg='slate gray', tearoff=0)
        help_menu.add_command(label='Help', command=self.createHelpWindow)
        help_menu.add_command(label='Keyboard Shortcuts', 
                              command=self.createShortcutsWindow)
        help_menu.add_command(label="About", command=self.createAboutWindow)
        
        menubar.add_cascade(label='Journal', menu=journal_menu)
        menubar.add_cascade(label="Entry", menu=entry_menu)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)
        menubar.config(bg='slate gray')
        
        self.protocol("WM_DELETE_WINDOW", self.destroyApp)
        self.bindDateControl()
#        self.storage.runBackup()
        self.updateGUI(entry=self.entry)
        if self.storage.getFirstTimeVar().get():
            self.createWelcomeWindow()
            self.storage.changeFirstTimeFlag()
            
    def createWelcomeWindow(self):
        self.createWindow('Welcome!', self.messages.split('<Welcome>')[1], 
                          (500, 500))
        
    def createShortcutsWindow(self):
        self.createWindow('Shortcuts', self.messages.split('<Shortcuts>')[1], 
                          (500, 500))
        
    def createHelpWindow(self):
        self.createWindow('Help', self.messages.split('<Help>')[1], (300, 500))
                
    def createAboutWindow(self):
        self.createWindow('About', self.messages.split('<About>')[1], 
                          (200, 300))
        
##        message = "Journal 0.3.1\nAuthor: kozmik-moore @ GitHub\nDeveloped using the Anaconda Suite (Python 3.6)"
##        main = messagebox.Message(title="About", message=text)
#        main = tk.Toplevel(master=self)
#        main.title('About')
#        main.iconbitmap(join(self.app_loc, 'Resources\web.ico'))
#        message = tk.Message(main, text=text, bg='slate gray')
#        message.pack()
##        main.show()
#        main.grab_set()
        
    def createWindow(self, title, message, dims):
##        text = message
##        message = "Journal 0.3.1\nAuthor: kozmik-moore @ GitHub\nDeveloped using the Anaconda Suite (Python 3.6)"
##        main = messagebox.Message(title="About", message=text)
#        main = tk.Toplevel(master=self)
#        main.title(title)
#        main.iconbitmap(join(self.app_loc, 'Resources\web.ico'))
#        main.geometry(str(dims[0])+'x'+str(dims[1]))
#        ybar = ttk.Scrollbar(main)
#        canvas = tk.Canvas(main, yscrollcommand = ybar.set, 
#                           width=dims[1],height=dims[0])
#        frame = tk.Frame(canvas, bg='slate gray')
#        ybar.config(command=canvas.yview)
#        ybar.pack(side='right', fill='y')
#        message = tk.Message(frame, text=message, bg='slate gray')
#        canvas.pack(side='left', fill='both', expand=True)
#        canvas.create_window(0,0,window=frame, anchor='nw')
#        message.pack()
##        frame.pack(fill='both', expand=True)
#        main.update()
#        canvas.config(scrollregion=canvas.bbox('all'))
##        main.show()
#        main.focus_force()
#        main.grab_set()
        main = tk.Toplevel()
        main.title(title)
        main.iconbitmap(join(self.app_loc, 'Resources\web.ico'))
#        main.geometry(str(dims[0])+'x'+str(dims[1]))
        outerframe = tk.Frame(main, bg='slate gray')
        frame = tk.Frame(outerframe, bg='slate gray')
        ybar = ttk.Scrollbar(frame)
        text=tk.Text(frame, bg='slate gray', yscrollcommand=ybar.set, 
                     wrap='word', font='TkMenuFont')
        ybar.config(command=text.yview)
        text.insert('insert', message)
        text.config(state='disabled')
        text.pack(side='left', fill='both', expand=True)
        ybar.pack(side='left', fill='y', expand=False, anchor='w')
        frame.pack(side='left', fill='both', expand=True, anchor='e', padx=3)
        outerframe.pack(expand=True, fill='both')
        main.focus_force()
        main.grab_set()
        
    def destroyApp(self):
        if self.entry.getDate() or not self.body_frame.bodyFieldIsEmpty():
            self.save()
        self.attachmanager.clean()
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
            self.jgraph.updateGUI(self.entry)
        self.journal.add(self.entry)
        
    def writeToDatabase(self):
        self.save()
        self.storage.saveJournal()
        
    def delete(self):
        date = self.entry.getDate()
        if not date:
            self.clearGUI()
        else:
            selection = messagebox.askyesno("Delete Entry", "Delete this entry?")
            if selection:
                self.jgraph.deleteEntry(self.entry.getDate())
                self.journal.delete(self.entry)
                self.attachmanager.delete()
                self.clearGUI()
#            else:
#                self.clearGUI()
            
    def newEntry(self):
        if self.entry.getDate() or not self.body_frame.bodyFieldIsEmpty():
            self.save()
        self.updateGUI(entry=JEntry())
        
    def newLink(self):
        if self.entry.getDate() or not self.body_frame.bodyFieldIsEmpty():
            self.save()
            self.updateGUI(entry=JEntry(parent=self.entry.getDate(), 
                                        tags=self.entry.getTags()))
                
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