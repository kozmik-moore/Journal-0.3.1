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
        style = JournalStyle()
        style.setNightStyle()
        self.args = style.getCustomValues()
        
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (w*0.995, h*.87))
        self.config(bg=self.args['bgcolor1'])
#        self.overrideredirect(1)
        self.title('kunnekted-jurnl')
        self.storage = Storage()
        self.args['homepath'] = self.storage.getPath()
        iconpath = join(self.args['homepath'], 'Resources\\web.ico')
        self.iconbitmap(iconpath)
        messagepath = (join(self.args['homepath'], 'Resources\\Messages'))
        messagefile = open(messagepath)
        self.messages = messagefile.read()
        self.journal = self.storage.getJournal()
        self.entry = JEntry()
        
        self.backup_interval_var = self.storage.getBackupIntervalVar()
        self.journal_auto_save = self.storage.getAutosaveVar()
        self.last_backup_var = self.storage.getLastBackupVar()
        
        """Frame 1"""
        frame1 = ttk.Frame(self)
        frame1_1 = ttk.Frame(frame1)
        self.date_frame = DateFrame(frame1_1, self.entry, self.journal, 
                                    self, width=100, **self.args)
        frame1_3 = ttk.Frame(frame1)
        self.LAST_BACKUP_LABEL = ttk.Label(frame1_3, text='Last Backup: ')
        self.LAST_BACKUP = ttk.Label(frame1_3, 
                                     textvariable=self.last_backup_var)
        self.LAST_BACKUP.pack(side='right', padx=3)
        self.LAST_BACKUP_LABEL.pack(side='right')
        frame1_1.grid(row=0, column=0, sticky='w')
        self.date_frame.grid(row=1, column=0, padx=self.args['padx'], sticky='w')
        frame1_3.grid(row=0, column=2)
        frame1.grid_columnconfigure(0, weight=1)
        frame1.grid_columnconfigure(1, weight=2)
        frame1.grid_columnconfigure(2, weight=0)
        frame1.pack(side='top', expand=True, fill='x', padx=self.args['padx'])
        
        """Frame 2"""
        frame2 = ttk.Frame(self)
        self.body_frame = BodyFrame(frame2, self.entry, **self.args)
        self.tags_frame = TagsFrame(frame2, self.journal, self.entry, **self.args)
        self.body_frame.pack(side='top', expand=True, fill='both', 
                             padx=self.args['padx'], pady=self.args['pady'])
        self.tags_frame.pack(side='top', expand=True, fill='x', 
                             padx=self.args['padx'], pady=self.args['pady'])
        frame2.pack(side='top', expand=True, fill='x', padx=self.args['padx'], 
                    pady=self.args['pady'])
        
        """Frame 3"""
        frame3 = ttk.Frame(self)
        frame3_1 = ttk.Frame(frame3)
        self.options_frame = ttk.Frame(frame3, relief=self.args['relief'], 
                                       border=self.args['border'])
        frame3_3 = ttk.Frame(frame3)
        self.jgraph = JGraph(self.options_frame, self, self.journal, 
                             self.entry, **self.args)
        self.attachmanager = AttachmentManager(self.options_frame, self, self.journal, 
                                               self.entry, **self.args)    
        frame3_1.pack(side='left', expand=True, fill='x')
        self.options_frame.pack(side='left', pady=self.args['pady'])
        frame3_3.pack(side='left', expand=True, fill='x')
        frame3.pack(side='top', expand=True, fill='x', padx=self.args['padx'])
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
        
        """Menu"""
        menubutton = ttk.Menubutton(frame1_1, text='Options')
        menubar = tk.Menu(menubutton, bg=self.args['bgcolor1'], 
                               fg=self.args['textcolor1'], tearoff=0, 
                               selectcolor=self.args['arrow'])
        menubutton.config(menu=menubar)
        
        journal_menu = tk.Menu(menubar, bg=self.args['bgcolor1'], 
                               fg=self.args['textcolor1'], tearoff=0)
        journal_menu.add_command(label='Save All Changes', 
                                 command=self.writeToDatabase)
        pref_menu = tk.Menu(journal_menu, bg=self.args['bgcolor1'], 
                            fg=self.args['textcolor1'], tearoff=0, 
                            selectcolor=self.args['arrow'])
        journal_menu.add_cascade(label='Database Preferences', menu=pref_menu)
        
        entry_menu = tk.Menu(menubar, bg=self.args['bgcolor1'], 
                             fg=self.args['textcolor1'], tearoff=0, 
                             selectcolor=self.args['arrow'])
        entry_menu.add_command(label='Save', command=self.save)
        entry_menu.add_command(label='Delete', command=self.delete)
        pref_menu.add_command(label="Change Save Directory", 
                              command=self.storage.changeSaveDirectory)
        backup_menu = tk.Menu(pref_menu, bg=self.args['bgcolor1'], 
                              fg=self.args['textcolor1'], tearoff=0, 
                              selectcolor=self.args['arrow'])
        backup_menu.add_command(label='Change Backup Directory', 
                                command=self.storage.changeBackupDirectory)
        self.interval_menu = tk.Menu(backup_menu, bg=self.args['bgcolor1'], 
                                     fg=self.args['textcolor1'], tearoff=0, 
                                     selectcolor=self.args['arrow'])
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
        

        help_menu = tk.Menu(menubar, bg=self.args['bgcolor1'], fg=self.args['textcolor1'], 
                            tearoff=0, selectcolor=self.args['arrow'])
        help_menu.add_command(label='Help', command=self.createHelpWindow)
        help_menu.add_command(label='Keyboard Shortcuts', 
                              command=self.createShortcutsWindow)
        help_menu.add_command(label="About", command=self.createAboutWindow)
        
        menubar.add_cascade(label='Journal', menu=journal_menu)
        menubar.add_cascade(label="Entry", menu=entry_menu)
        menubar.add_cascade(label="Help", menu=help_menu)
        menubar.add_command(label='Quit', command=self.destroyApp)
        self.config(menu=menubutton)
        menubar.config(bg=self.args['bgcolor1'], fg=self.args['textcolor1'])
        menubutton.grid(row=0, column=0, sticky='w', pady=self.args['pady'])
        
        self.protocol("WM_DELETE_WINDOW", self.destroyApp)
        self.bindDateControl()
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
        
    def createWindow(self, title, message, dims):
        main = tk.Toplevel(bg=self.args['bgcolor1'])
        main.title(title)
        main.iconbitmap(join(self.args['homepath'], 'Resources\web.ico'))
        outerframe = ttk.Frame(main)
        frame = ttk.Frame(outerframe)
        ybar = ttk.Scrollbar(frame)
        text=tk.Text(frame, yscrollcommand=ybar.set, 
                     wrap='word', font='TkMenuFont', bg=self.args['bgcolor1'], 
                     fg=self.args['textcolor1'])
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
        self.storage.saveJournal(self.journal)
        
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
        self.tk_options = {}
        self.bgcolor1 = None
        self.bgcolor2 = None
        self.text_color1 = None
        self.text_color2 = None
        self.text_color3 = None
        self.frame_borderwidth = 4
        self.padx = 5
        self.pady = 3
        self.frame_relief = 'groove'

        
    def setDayStyle(self):
        self.theme_use('default')
        textcolors = {'1': 'black', '2': 'black', '3': 'blue'}
        bgcolors = {'1': 'gray', '2': 'gray'}
        self.setTkBGColors(bgcolors)
        self.setTkTextColors(textcolors)
        
    def setNightStyle(self):
        self.theme_create('shadow', parent='default')
        self.theme_settings('shadow', {
                'TButton': {
                        'configure': {'padding': 3, 'foreground': 'white', 'relief': 'raised',
                                      'font': 'TkDefaultFont', 'background': 'black', 
                                      'anchor': 'center', 'borderwidth': 4, 'width': 18},
                        'map': {'foreground': [('disabled', 'gray40'), ('pressed', 'white'), 
                                               ('active', 'white')],
                                'background': [('disabled', 'black'), ('pressed', 'gray20'), 
                                               ('active', 'gray10')],
                                'relief': [('pressed', 'groove'), ('!pressed', 'raised')]}},
                'TLabel': {
                        'configure': {'background': 'black', 'foreground': 'white'}},
                'TCombobox': {
                        'configure': {'fieldbackground': 'gray10', 'arrowcolor': 'gray50',
                                       'background': 'black'},
                        'map': {'focusfill': [('readonly', 'focus', 'SystemHighlight')], 
                                'foreground': [('disabled', 'SystemGrayText'), 
                                               ('readonly', 'focus', 'black')], 
                                'selectforeground': [('readonly', 'white')], 
                                'selectbackground': [('readonly', 'gray10')]}},
                'TCheckbutton': {
                        'configure': {'foreground': 'white', 'background': 'black', 
                                      'font': ('TkDefaultFont','10'), 'indicatorcolor': 'black'},
                        'map': {'indicatorcolor': [('pressed', 'white'), ('selected', 'blue')]}},
                'TRadiobutton': {
                        'configure': {'foreground': 'white', 'background': 'black', 
                                      'indicatorcolor': 'black', 'padding': 3},
                        'map': {'indicatorcolor': [('pressed', 'white'), ('selected', 'blue')]}},
                'Vertical.TScrollbar': {
                        'configure': {'background': 'black', 'troughcolor': 'gray30', 'arrowcolor': 'white'}},
                'Horizontal.TScrollbar': {
                        'configure': {'background': 'black', 'troughcolor': 'gray30', 'arrowcolor': 'white'}},
                'UI.TButton': {
                        'configure': {}},
                'Current.UI.TButton': {
                        'configure': {'background': 'black', 'foreground': 'DeepSkyBlue2'},
                        'map': {'foreground': [('active', 'DeepSkyBlue2')]}},
                'Bold.UI.TButton': {
                        'configure': {'font': ('TkDefault', '9', 'bold')}},
                'Tags.Bold.UI.TButton': {
                        'configure':{'font': ('TkDefault', '9', 'bold', 'underline')}},
                'Tags.Variable.UI.TButton': {
                        'configure': {'width': ''}},
                'TFrame': {
                        'configure': {'background': 'black'}},
                'TMenubutton': {
                        'configure': {'background': 'black', 'foreground': 'white',
                                      'indicator': 'red'}}
                })
        self.theme_use('shadow')
        textcolors = {'1': 'white', '2': 'lime green', '3': 'DeepSkyBlue2'}
        bgcolors = {'1': 'black', '2': 'gray8'}
        self.setTkBGColors(bgcolors)
        self.setTkTextColors(textcolors)
        
    def setTkBGColors(self, kw):
        self.bgcolor1 = kw['1']
        self.bgcolor2 = kw['2']
        
    def setTkTextColors(self, kw):
        self.text_color1 = kw['1']
        self.text_color2 = kw['2']
        self.text_color3 = kw['3']
    
    def getCustomValues(self):
        return {'relief': self.frame_relief, 'border': self.frame_borderwidth, 
                'bgcolor1': self.bgcolor1, 'bgcolor2': self.bgcolor2, 
                'textcolor1': self.text_color1, 'textcolor2': self.text_color2, 
                'textcolor3': self.text_color3, 'padx': self.padx, 
                'pady': self.pady, 'arrow': self.text_color1}
            
        
app=Main()
app.mainloop()