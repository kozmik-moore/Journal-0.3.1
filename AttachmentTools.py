# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 13:22:32 2017

@author: Kozmik
"""

import DateTools as DT
from os.path import abspath
from os import mkdir
from os import remove
from inspect import getsourcefile
from shutil import copy
from subprocess import Popen
import PIL.Image as PI
from PIL import ImageTk
from tkinter import filedialog as filedialog
from tkinter import messagebox as messagebox
import tkinter as tk
import tkinter.ttk as ttk

class AttachmentManager(tk.Frame):
    def __init__(self, master, controller, jobject, jentry, **kw):
        self.master = master
        self.controller = controller
        self.journal = jobject
        self.entry = jentry
        self.old_attachments = [] #strings of filepaths
        self.new_attachments = [] #strings of filepaths
        self.all_attachments = None
        self.dialog = None
        self.frame = None
        self.DELETE = None
        self.buttonlist = None
        self.delete_icon = None
        
        self.path = abspath(getsourcefile(lambda:0).strip('AttachmentTools.py'))
        self.path += '\\Attachments\\'
        self.mainpath = self.path
        
        try:
            mkdir(self.path)
        except FileExistsError:
            pass
        
        tk.Frame.__init__(self, self.master, **kw)
        self.NEW = ttk.Button(self, takefocus=0, style='UI.TButton', text='Add Attachment', command=self.askForAttachment)
        self.DISPLAY = ttk.Button(self, takefocus=0, style='UI.TButton', text='Display Attachments', command=self.displayAttachments,
                              state=tk.DISABLED)
        self.NEW.pack(fill=tk.X)
        self.DISPLAY.pack(fill=tk.X)
        
    def updateGUI(self, jentry):
        self.DISPLAY.config(state=tk.DISABLED)
        self.old_attachments = []
        self.new_attachments = []
        self.entry = jentry
        date = self.entry.getDate()
        self.path = self.mainpath
        if date:
            self.path = self.mainpath + DT.getDateFileStorageFormat(date) + '\\'
        attachments = self.entry.getAttachments()
        if attachments:
            self.DISPLAY.config(state=tk.NORMAL)
            for filename in attachments:
                self.old_attachments.append(abspath(self.path + filename))
            
    def addAttachment(self, filepath):
        self.new_attachments.append(filepath)
        self.DISPLAY.config(state=tk.NORMAL)
        
    def askForAttachment(self):
        options = {}
        options['initialdir'] = self.path
        options['parent'] = self.controller
        options['title'] = 'Select a file to add'
        path = filedialog.askopenfilename(**options)
        if path:
            self.addAttachment(abspath(path))
            
    def displayAttachments(self):
        self.all_attachments = self.old_attachments + self.new_attachments
        self.buttonlist = []
        
        if self.all_attachments:
            self.dialog = tk.Toplevel()
            self.dialog.title('Attachments')
            self.dialog.maxsize(width=self.dialog.winfo_screenwidth(), height=self.dialog.winfo_screenheight())
            self.dialog.minsize(width=250, height=70)
            
            self.frame = tk.Frame(self.dialog)
            topframe = tk.Frame(self.frame)
            bottomframe = tk.Frame(self.dialog)
            
            for filepath in self.all_attachments:
                path = abspath(filepath)
                command = r'explorer /select, ' + '""' + path + '""'
                button = ttk.Button(self.frame, text=filepath.rsplit('\\', 1)[1], command=lambda c=command:
                    Popen(c))
                self.buttonlist.append([button, tk.BooleanVar(self.frame, False, button.cget('text')), path])
                button.pack(expand=1, fill=tk.X, pady=2)
            self.DELETE = ttk.Button(bottomframe, text='Delete Attachment', command=self.deleteAttachment)
            self.DELETE.pack(side=tk.RIGHT)
            self.frame.pack(side=tk.TOP)
            bottomframe.pack(side=tk.TOP, pady=4)
            self.dialog.grab_set()
            
            self.dialog.protocol('WM_DELETE_WINDOW', self.destroyDialog)
            
        else:
            message = "There are no attachments for this entry!"
            messagebox.showinfo(title='Attachments', message=message)
        
    def deleteAttachment(self):
        for item in self.frame.pack_slaves():
            item.pack_forget()
        self.dialog.title('Delete')
        
        for button in self.buttonlist:
            checkbutton = ttk.Checkbutton(self.frame, text=button[0].cget('text'), var=button[1])
            checkbutton.pack(side=tk.TOP, expand=True, fill=tk.X, pady=2)
            
        w = self.DELETE.winfo_width()
        h = self.DELETE.winfo_height()
        if not self.delete_icon:
            iconpath = self.mainpath.rsplit('\\Attachments',1)[0] + '\\Resources\\Trash_Can-512.png'
            self.delete_icon = PI.open(iconpath)
            self.delete_icon.thumbnail((h-2,h-2))
            self.delete_icon = ImageTk.PhotoImage(self.delete_icon)
        self.DELETE.config(command=self.refreshDialog, text='', image=self.delete_icon,
                           width=w)
        self.DELETE.pack()
#        self.frame.pack()
            
    def refreshDialog(self):
        deletelist = []
        saved_attachment = False
        for i in range(len(self.buttonlist)):
            button = self.buttonlist[i]
            if button[1].get():
                deletelist.append(i)
                if abspath(self.path+button[0].cget('text')) in self.old_attachments:
                    saved_attachment = True
        if deletelist:
            if len(deletelist) > 1 and saved_attachment:
                message = "This will delete previously saved attachments from your journal storage."\
                " If you want to keep any of the attachments, press \"Cancel\" and copy "\
                "them elsewhere. Then, return here to finish deleting.\n\n"\
                "Are you sure you want to delete them?"
            elif len(deletelist) > 1 and not saved_attachment:
                message = "Are you sure you want to remove these attachments?"
            elif saved_attachment:
                message = "This will delete the selected attachment from your "\
                "computer. If you want to keep the attachment, press \"Cancel\" "\
                "and copy the atttachment elsewhere. Then, return here to "\
                "delete it.\n\n Are you sure you want to delete it?"
            elif not saved_attachment:
                message = "Are you sure you want to remove the selected attachment?"
            choice = messagebox.askokcancel(title='Are You Sure?', message=message)
            if choice:
                for d in deletelist:
                    filename = self.buttonlist[d][0].cget('text')
                    filepath = abspath(self.path+filename)
                    if filepath == self.buttonlist[d][2]:
                        try:
                            remove(filepath)
                        except FileNotFoundError:
                            pass
                        if filepath in self.old_attachments:
                            self.old_attachments.remove(filepath)
                    else:
                        filepath = self.buttonlist[d][2]
                    if filepath in self.new_attachments:
                        self.new_attachments.remove(filepath)
                    self.entry.deleteAttachment(filename)
                for item in self.buttonlist:
                    item[0].destroy()
                self.buttonlist = None
                self.destroyDialog()
        
    def destroyDialog(self):
        self.dialog.destroy()
        self.dialog = None
        self.frame = None
        self.buttonlist = None
        if not self.old_attachments and not self.new_attachments:
            self.DISPLAY.config(state=tk.DISABLED)
        
    def clearGUI(self, jentry):
        self.entry = jentry
        self.old_attachments = []
        self.new_attachments = []
        
    def save(self):
        """Assumes that the JEntry object already has a date"""
        path = self.path
        if self.new_attachments:
            try:
                mkdir(path)
            except FileExistsError:
                pass
            for filepath in self.new_attachments:
                copy(filepath, path)
                f = filepath.rsplit('\\',1)[1]
                self.entry.addAttachment(f)
            tmp = self.entry.getAttachments()
            self.old_attachments = []
            for filename in tmp:
                self.old_attachments.append(self.path+filename)                
            self.new_attachments = []        