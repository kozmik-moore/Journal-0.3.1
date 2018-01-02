# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 13:22:32 2017

@author: Kozmik
"""

import DateTools as DT
from os.path import abspath
from os.path import exists
from os import listdir
from os import rename
from os import mkdir
from os import remove
from os import rmdir
from shutil import copy
from subprocess import Popen
import PIL.Image as PI
from PIL import ImageTk
from tkinter import filedialog as filedialog
from tkinter import messagebox as messagebox
import tkinter as tk
import tkinter.ttk as ttk

class AttachmentManager(tk.Frame):
    def __init__(self, master, controller, path, jobject, jentry, **kw):
        self.master = master
        self.controller = controller
        self.journal = jobject
        self.entry = jentry
        self.all_attachments = []
        self.dialog = None
        self.frame = None
        self.DELETE = None
        self.buttonlist = None
        self.delete_icon = None
        
        self.parentpath = path + '\\Attachments\\'        
        try:
            mkdir(self.parentpath)
        except FileExistsError:
            pass
        self.temppath = self.parentpath + 'temp\\'
        self.currentpath = self.temppath
#        try:
#            mkdir(self.currentpath)
#        except FileExistsError:
        if exists(abspath(self.currentpath)):
            self.delete()
        
        tk.Frame.__init__(self, self.master, **kw)
        self.NEW = ttk.Button(self, takefocus=0, style='UI.TButton', 
                              text='Add Attachment', 
                              command=self.askForAttachment)
        self.DISPLAY = ttk.Button(self, takefocus=0, style='UI.TButton', 
                                  text='Display Attachments', 
                                  command=self.displayAttachments, 
                                  state=tk.DISABLED)
        self.NEW.pack(fill=tk.X)
        self.DISPLAY.pack(fill=tk.X)
        
    def updateGUI(self, jentry):
        """Checks to see if the current JEntry has attachments and aligns variables, if so.
        Has exclusive control to generation of 'temp' folder."""
        self.all_attachments = []
        if exists(self.temppath):
            self.current = self.temppath
            self.delete()
        self.DISPLAY.config(state=tk.DISABLED)
        self.entry = jentry
        date = self.entry.getDate()
        if date:
            attachments = self.entry.getAttachments()
            path = self.parentpath + DT.getDateFileStorageFormat(date) + '\\'
            filepath = exists(path)
            if not attachments and not filepath:
                self.currentpath = self.temppath
                mkdir(self.currentpath)
            elif attachments and not filepath:
                message = ''
                if len(attachments) > 1:
                    message = 'The directory for this journal entry could ' +\
                    'not be located. The following attachments are missing: '
                    message += attachments[0] + '. Do you want to restore them?'
                    for item in range(1, len(attachments)):
                        message += ', ' + attachments[item]
                else:
                    message = 'The directory for this journal entry could ' +\
                    'not be located. The following attachment is missing: '
                    message += attachments[0] + '. Do you want to restore it?'
                choice = messagebox.askyesno(title='Missing Directory', 
                                             message=message)
                if choice:
                    self.currentpath = path
                    mkdir(self.currentpath)
                    self.askForAttachment()
                else:
                    for item in attachments:
                        self.entry.deleteAttachment(item)
                    self.currentpath = self.temppath
                    mkdir(self.currentpath)
                self.DISPLAY.config(state=tk.DISABLED)
            else:
                self.currentpath = path
                check = self.scanForAdditions()
                if check:
                    attachments = self.entry.getAttachments()
                self.DISPLAY.config(state=tk.NORMAL)
                for filename in attachments:
                    self.all_attachments.append(self.currentpath + 
                                                    filename)
        else:
            self.currentpath = self.temppath
            self.DISPLAY.config(state=tk.DISABLED)
            mkdir(self.currentpath)            
                    
    def addAttachment(self, pathtuple):
        for filepath in pathtuple:
            filepath = filepath.replace('/', '\\')
            if filepath not in self.all_attachments:
                self.all_attachments.append(filepath)
            copy(filepath, self.currentpath)
        self.DISPLAY.config(state=tk.NORMAL)
        
    def askForAttachment(self):
        options = {}
        options['initialdir'] = self.currentpath
        options['parent'] = self.controller
        options['title'] = 'Select a file to add'
        items = filedialog.askopenfilenames(**options)
        if items:
            self.addAttachment(items)
    
    def scanForAdditions(self):
        """[For later.] Allows manual addition of attachments that will be added 
        to associated folder upon opening the JEntry."""
        new = listdir(self.currentpath)
        old = self.entry.getAttachments()
        if old != new:
            for item in new:
                if item not in old:
                    self.entry.addAttachment(item)
            return True
        else:
            return False
#                self.updateGUI(self.entry)
            
    def displayAttachments(self):
        self.buttonlist = []
        
        if self.all_attachments:
            self.dialog = tk.Toplevel(bg='slate gray')
            self.dialog.title('Attachments')
            self.dialog.maxsize(width=self.dialog.winfo_screenwidth(), 
                                height=self.dialog.winfo_screenheight())
            self.dialog.minsize(width=250, height=70)
            
            self.frame = tk.Frame(self.dialog, bg='slate gray')
#            topframe = tk.Frame(self.frame, bg='slate gray')
            bottomframe = tk.Frame(self.dialog)
            
            for filepath in self.all_attachments:
                path = abspath(filepath)
                command = r'explorer /select, ' + '""' + path + '""'
                button = ttk.Button(self.frame, style='UI.TButton', 
                                    text=filepath.rsplit('\\', 1)[1], 
                                    command=lambda c=command: Popen(c))
                self.buttonlist.append([button, 
                                        tk.BooleanVar(self.frame, False, 
                                                      button.cget('text')), 
                                                      path])
                button.pack(expand=1, fill='x', pady=2)
            self.DELETE = ttk.Button(bottomframe, takefocus=0, 
                                     style='Bold.UI.TButton', 
                                     text='Delete', 
                                     command=self.deleteAttachment)
            self.DELETE.pack(side='right', expand=True, fill='x')
            self.frame.pack(side='top')
            bottomframe.pack(side='top', pady=4)
            self.dialog.grab_set()
            
            self.dialog.protocol('WM_DELETE_WINDOW', self.destroyDialog)
            
        else:
            message = "There are no attachments for this entry!"
            messagebox.showinfo(title='Attachments', message=message)
        
    def deleteAttachment(self):
        for item in self.frame.pack_slaves():
            item.pack_forget()
        self.dialog.title('Delete')
        
        for item in self.buttonlist:
            checkbutton = tk.Checkbutton(self.frame, 
                                         text=item[0].cget('text'), 
                                         var=item[1], bg='slate gray', 
                                         fg='black', 
                                         activebackground='light slate gray',
                                         activeforeground='black')
            checkbutton.pack(side=tk.TOP, expand=True, fill=tk.X, pady=2)
            
        w = self.DELETE.winfo_width()
        h = self.DELETE.winfo_height()
        if not self.delete_icon:
            iconpath = self.parentpath.rsplit('\\Attachments',1)[0] + \
            '\\Resources\\Trash_Can-512.png'
            self.delete_icon = PI.open(iconpath)
            self.delete_icon.thumbnail((h-2,h-2))
            self.delete_icon = ImageTk.PhotoImage(self.delete_icon)
        self.DELETE.config(command=self.refreshDialog, text='', 
                           image=self.delete_icon, width=w)
        self.DELETE.pack()

    def delete(self):
        """Deletes the folder associated with the entry."""
        try:
            items = listdir(self.currentpath)
            for item in items:
                remove(self.currentpath + item)
            rmdir(self.currentpath)
        except FileNotFoundError:
            pass
            
    def refreshDialog(self):
        deletelist = []
        for i in range(len(self.buttonlist)):
            button = self.buttonlist[i]
            if button[1].get():
                deletelist.append(i)
        if deletelist:
            if len(deletelist) > 1:
                message = "This will delete previously saved attachments from your journal storage."\
                " If you want to keep any of the attachments, press \"Cancel\" and copy "\
                "them elsewhere. Then, return here to finish deleting.\n\n"\
                "Are you sure you want to delete them?"
            else:
                message = "This will delete the selected attachment from your "\
                "computer. If you want to keep the attachment, press \"Cancel\" "\
                "and copy the attachment elsewhere. Then, return here to "\
                "delete it.\n\n Are you sure you want to delete it?"
            choice = messagebox.askokcancel(title='Are You Sure?', message=message)
            if choice:
                for d in deletelist:
                    path = self.buttonlist[d][2]
#                    filename = self.buttonlist[d][0].cget('text')
#                    filepath = abspath(self.currentpath+filename)
#                    if filepath == self.buttonlist[d][2]:
#                        try:
#                            remove(filepath)
#                        except FileNotFoundError:
#                            pass
#                        if filepath in self.old_attachments:
#                            self.old_attachments.remove(filepath)
#                    else:
#                        filepath = self.buttonlist[d][2]
#                    if filepath in self.new_attachments:
#                        self.new_attachments.remove(filepath)
                    try:
                        remove(path)
                    except FileNotFoundError:
                        pass
                    self.entry.deleteAttachment(filename = 
                                                self.buttonlist[d][0].cget('text'))
                    self.all_attachments.remove(path)
                self.destroyDialog()
        
    def destroyDialog(self):
        self.dialog.destroy()
        self.dialog = None
        self.frame = None
        for item in self.buttonlist:
            item[0].destroy()
        self.buttonlist = None
        if not self.all_attachments:
            self.delete()
            self.updateGUI(self.entry)
#            self.DISPLAY.config(state=tk.DISABLED)
#            rmdir(self.currentpath)
        
    def clearGUI(self, jentry):
        self.entry = jentry
        self.all_attachments = []
        self.currentpath = self.temppath
        self.delete()
#        mkdir(self.currentpath)
#        self.new_attachments = []
        
    def save(self):
        """Saves the attachments and renames the 'temp' folder to the date.
        Has exclusive control over generation of JEntry-associated folders.
        Assumes that the JEntry object already has a date"""
        src = self.temppath
        date = self.entry.getDate()
        dest = self.parentpath + DT.getDateFileStorageFormat(date)
#        tmp = False
        old = self.entry.getAttachments()
        new = listdir(src)
#        if not old:
        if exists(src) and new:
#            tmp = True
#            new = listdir(src)
            for item in new:
                if item not in old:
                    self.entry.addAttachment(item)
            rename(src, dest)
#        self.delete()
#        src = self.currentpath
#        if new and tmp:
            
#        if self.all_attachments:
#            try:
#                mkdir(path)
#            except FileExistsError:
#                pass
#            for filepath in self.new_attachments:
#                copy(filepath, path)
#                f = filepath.rsplit('\\',1)[1]
#                self.entry.addAttachment(f)
#            tmp = self.entry.getAttachments()
#            self.old_attachments = []
#            for filename in tmp:
#                self.old_attachments.append(self.currentpath+filename)                
#            self.new_attachments = []

    def clean(self):
        self.currentpath = self.temppath
        if exists(self.currentpath):
            check = listdir(self.currentpath)
            if check:
                message = 'There are files left in ' + self.currentpath + '. If you wish to '\
                'move them, do so before clicking \"OKAY\".'
                messagebox.showwarning(title='Unsaved files', message=message)
            self.delete()