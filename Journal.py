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
#        primary = style.getPrimary()
#        secondary = style.getSecondary()
#        text = style.getTextColor()
        self.custom_values = style.getCustomValues()
        
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (w*.95, h*.8))
        self.config(bg=self.custom_values['primarycolor'])
#        self.overrideredirect(1)
        self.title('kunnekted-jurnl')
        self.storage = Storage()
        self.custom_values['homepath'] = self.storage.getPath()
        iconpath = join(self.custom_values['homepath'], 'Resources\\web.ico')
        self.iconbitmap(iconpath)
        messagepath = (join(self.custom_values['homepath'], 'Resources\\Messages'))
        messagefile = open(messagepath)
        self.messages = messagefile.read()
        self.journal = self.storage.getJournal()
        self.entry = JEntry()
        
        self.backup_interval_var = self.storage.getBackupIntervalVar()
        self.journal_auto_save = self.storage.getAutosaveVar()
        self.last_backup_var = self.storage.getLastBackupVar()
        
        self.top_frame = ttk.Frame(self)
        self.date_frame = DateFrame(self.top_frame, self.entry, self.journal, 
                                    self, width=100, **self.custom_values)
        top_right_frame = ttk.Frame(self.top_frame)
        self.body_frame = BodyFrame(self, self.entry, **self.custom_values)
        self.tags_frame = TagsFrame(self, self.journal, self.entry, **self.custom_values)
        self.lower_frame = ttk.Frame(self)
        self.lower_left = ttk.Frame(self.lower_frame)
        self.options_frame = ttk.Frame(self.lower_frame, relief=self.custom_values['relief'], 
                                       border=self.custom_values['border'])
        self.lower_right = ttk.Frame(self.lower_frame)
        self.jgraph = JGraph(self.options_frame, self, self.journal, 
                             self.entry, **self.custom_values)
        self.attachmanager = AttachmentManager(self.options_frame, self, self.journal, 
                                               self.entry, **self.custom_values)

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
        
        menubar = tk.Menu(self, bg=self.custom_values['primarycolor'], 
                          fg=self.custom_values['textcolor1'])
        
        journal_menu = tk.Menu(menubar, bg=self.custom_values['primarycolor'], 
                               fg=self.custom_values['textcolor1'], tearoff=0)
        journal_menu.add_command(label='Save All Changes', 
                                 command=self.writeToDatabase)
        pref_menu = tk.Menu(journal_menu, bg=self.custom_values['primarycolor'], fg=self.custom_values['textcolor1'], 
                            tearoff=0)
        journal_menu.add_cascade(label='Database Preferences', menu=pref_menu)
        journal_menu.add_command(label='Quit', command=self.destroyApp)
        
        entry_menu = tk.Menu(menubar, bg=self.custom_values['primarycolor'], fg=self.custom_values['textcolor1'], 
                             tearoff=0)
        entry_menu.add_command(label='Save', command=self.save)
        entry_menu.add_command(label='Delete', command=self.delete)
#        pref_menu.add_command(label='Autosave changes on exit', command=self.changeAutoSavePref)
        pref_menu.add_command(label="Change Save Directory", 
                              command=self.storage.changeSaveDirectory)
        backup_menu = tk.Menu(pref_menu, bg=self.custom_values['primarycolor'], fg=self.custom_values['textcolor1'], 
                              tearoff=0)
        backup_menu.add_command(label='Change Backup Directory', 
                                command=self.storage.changeBackupDirectory)
        self.interval_menu = tk.Menu(backup_menu, bg=self.custom_values['primarycolor'], fg=self.custom_values['textcolor1'], 
                                     tearoff=0)
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
        

        help_menu = tk.Menu(menubar, bg=self.custom_values['primarycolor'], fg=self.custom_values['textcolor1'], 
                            tearoff=0)
        help_menu.add_command(label='Help', command=self.createHelpWindow)
        help_menu.add_command(label='Keyboard Shortcuts', 
                              command=self.createShortcutsWindow)
        help_menu.add_command(label="About", command=self.createAboutWindow)
        
        menubar.add_cascade(label='Journal', menu=journal_menu)
        menubar.add_cascade(label="Entry", menu=entry_menu)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)
        menubar.config(bg=self.custom_values['primarycolor'], fg=self.custom_values['textcolor1'])
        
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
        
    def createWindow(self, title, message, dims):
        main = tk.Toplevel(bg=self.custom_values['primarycolor'])
        main.title(title)
        main.iconbitmap(join(self.custom_values['homepath'], 'Resources\web.ico'))
#        main.geometry(str(dims[0])+'x'+str(dims[1]))
        outerframe = ttk.Frame(main)
        frame = ttk.Frame(outerframe)
        ybar = ttk.Scrollbar(frame)
        text=tk.Text(frame, yscrollcommand=ybar.set, 
                     wrap='word', font='TkMenuFont', bg=self.custom_values['primarycolor'], 
                     fg=self.custom_values['textcolor1'])
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
        self.tk_options = {}
        self.primary = None
        self.secondary = None
        self.text_color1 = None
        self.text_color2 = None
        self.text_color3 = None
        self.frame_borderwidth = 4
        self.frame_relief = 'groove'
        self.frame_background = None
        self.theme_create('shadow', parent='default')
        self.theme_settings('shadow', {
                'TButton': {
                        'configure': {'padding': 3, 'foreground': 'white', 'relief': 'raised',
                                      'font': 'TkDefaultFont', 'background': 'black', 
                                      'anchor': 'center', 'borderwidth': 4, 'width':18},
                        'layout': 
                            [('Button.border', {'sticky': 'nswe', 'children': 
                                [('Button.focus', {'sticky': 'nswe', 'children': 
                                    [('Button.padding', {'sticky': 'nswe', 'children': 
                                        [('Button.label', {'sticky': 'nswe', 'expand':1})]})]})]})],
                        'map': {'foreground': [('disabled', 'gray40'), ('pressed', 'white'), 
                                               ('active', 'white')],
                                'background': [('disabled', 'black'), ('pressed', 'gray20'), 
                                               ('active', 'gray10')],
                                'relief': [('pressed', 'flat'), ('!pressed', 'raised')]}},
                'TLabel': {
                        'configure': {'background': 'black', 'foreground': 'white'}},
                'TCombobox': {
                        'configure': {'fieldbackground': 'gray10', 'arrowcolor': 'gray50',
                                       'background': 'black'},
#                        'layout': 
#                            [('Combobox.border', {'sticky': 'nswe', 'children': 
#                                [('Combobox.rightdownarrow', {'side': 'right', 'sticky': 'news'}), 
#                                 ('Combobox.padding', {'expand': '1', 'sticky': 'nswe', 'children': 
#                                     [('Combobox.focus', {'expand': '1', 'sticky': 'nswe', 'children': 
#                                         [('Combobox.textarea', {'sticky': 'nswe'})]})]})]})],
                        'map': {'focusfill': [('readonly', 'focus', 'SystemHighlight')], 
                                'foreground': [('disabled', 'SystemGrayText'), 
                                               ('readonly', 'focus', 'black')], 
                                'selectforeground': [('readonly', 'white')], 
                                'selectbackground': [('readonly', 'gray10')]}},
                'TEntry': {
                        'configure': {'background': 'white'}},
                'TCheckbutton': {
                        'configure': {'foreground': 'white', 'background': 'black', 
                                      'font': ('TkDefaultFont','10'), 'indicatorcolor': 'black'},
                        'layout': [('Checkbutton.padding', {'sticky': 'nswe', 'children': 
                                    [('Checkbutton.indicator', {'side': 'left', 'sticky': ''}), ('Checkbutton.focus', {'side': 'left', 'sticky': 'w', 'children': 
                                        [('Checkbutton.label', {'sticky': 'nswe'})]})]})],
                        'map': {'indicatorcolor': [('pressed', 'white'), ('selected', 'blue')]}},
                'TRadiobutton': {
                        'configure': {'foreground': 'white', 'background': 'black', 
                                      'indicatorcolor': 'black', 'padding': 3},
                        'layout': [('Radiobutton.padding', {'sticky': 'nswe', 'children': 
                            [('Radiobutton.indicator', {'side': 'left', 'sticky': ''}), ('Radiobutton.focus', {'side': 'left', 'sticky': '', 'children': 
                                [('Radiobutton.label', {'sticky': 'nswe'})]})]})],
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
                'Tags.Variable.UI.TButton': {'width': ''},
                'Grooved.TFrame': {
                        'configure': {'borderwidth': 8, 'relief': 'groove'}},
                'TFrame': {
                        'configure': {'background': 'black'}}
                })

        
    def setDayStyle(self):
        self.theme_use('default')
        self.setBGColorsTK('gray', 'gray')
        
    def setNightStyle(self):
        self.theme_use('shadow')
        self.setBGColorsTK('black', 'gray8')
        self.setTextColorTK('white')
        self.setCustomFrameBG('black')
        textcolors = {'1': 'white', '2': 'lime green', '3': 'DeepSkyBlue2'}
        self.setTextColors(textcolors)
        
    def addFrame(self, frame):
        self.frame_list.append(frame)
        
    def setBGColorsTK(self, color1, color2):
        self.primary = color1
        self.secondary = color2
        
    def setTextColors(self, kw):
        self.text_color1 = kw['1']
        self.text_color2 = kw['2']
        self.text_color3 = kw['3']
        
    def setTextColorTK(self, color):
        self.text_color = color
        
    def setCustomFrameBG(self, color):
        self.frame_background = color
        
    def getBGColors(self):
        return self.primary, self.secondary
    
    def getPrimary(self):
        return self.primary
    
    def getSecondary(self):
        return self.secondary
    
    def getTextColor(self):
        return self.text_color
    
    def getButtonBorderWidth(self):
        return self.button_bwidth
    
    def getCustomValues(self):
        return {'relief': self.frame_relief, 'border': self.frame_borderwidth, 
                'primarycolor': self.primary, 'secondarycolor': self.secondary, 
                'textcolor1': self.text_color1, 'textcolor2': self.text_color2, 
                'textcolor3': self.text_color3}
            
        
app=Main()
app.mainloop()