# -*- coding: utf-8 -*-
"""
Created on Sun Mar 26 18:18:35 2017

@author: Kozmik

This module manages the journal database and .ini file(s) and performs checks on
whether the Journal script is operating in a bundle (e.g. .exe) or freely in a 
Python environment.
"""

from os.path import exists
from os.path import abspath
from os.path import dirname
from os.path import join
from os import mkdir
from os import remove
from os import rmdir
from os import listdir
from os import makedirs
from shutil import move
from shutil import copy
from shutil import make_archive
import pickle
from tkinter import BooleanVar
from tkinter import IntVar
from tkinter import StringVar
import DateTools
from tkinter.filedialog import askdirectory
from tkinter.messagebox import askyesno
from tkinter.messagebox import askyesnocancel
import JObject
import sys

class Storage:
    def __init__(self, master=None):
        self.HOME = self.SAVE = self.BACKUP = self.IMPORTS = self.LAST_BACKUP = None
        self.BACKUP_INTERVAL = 168      #24, 72, 168, -1
        self.AUTOSAVE = False
        self.FIRST_TIME = True
        self.getWorkingDir()
        
        self.journal = None
        self.master = master
        self.auto_save = BooleanVar(master=self.master, name='Autosave', 
                                    value=self.AUTOSAVE)
        self.backup_interval = IntVar(master=self.master, 
                                      name='Backup Interval', 
                                      value=self.BACKUP_INTERVAL)
        self.last_backup = StringVar(master=self.master, name='Last Backup', 
                                     value=self.LAST_BACKUP)
        self.first_time = BooleanVar(self.master, name='First Time Use Flag', 
                                     value=self.FIRST_TIME)
        
#        self.createImportsDirectory()
        self.LoadIniFile()
        self.createResourceFolder()
        self.openJournalFile()
        self.checkImports()
        self.runBackup()
         
    def LoadIniFile(self):
        try:
            fin = open(join(self.HOME, "Journal.ini"), "rb")
            ini_file = pickle.load(fin)
            self.SAVE = ini_file['SAVE LOCATION']
            self.BACKUP = ini_file['BACKUP LOCATION']
            self.IMPORTS = ini_file['IMPORTS LOCATION']
            self.BACKUP_INTERVAL = ini_file['BACKUP INTERVAL']
            self.auto_save.set(ini_file['AUTOSAVE'])
            self.backup_interval.set(ini_file['BACKUP INTERVAL'])
            if not ini_file['LAST BACKUP']:
                self.last_backup.set('Never')
            else:
                self.LAST_BACKUP = ini_file['LAST BACKUP']
                self.last_backup.set(DateTools.getDateGUIFormat(self.LAST_BACKUP))
            try:
                self.first_time.set(ini_file['FIRST TIME'])
                self.FIRST_TIME = ini_file['FIRST TIME']
            except KeyError:
                self.FIRST_TIME = True
                self.first_time.set(True)
        except FileNotFoundError:
            self.changeSaveDirectory()
            fin = open(join(self.HOME, "Journal.ini"), "wb")
        fin.close()
            
    def saveIniFile(self):
        ini_file = {'SAVE LOCATION': self.SAVE, 'BACKUP LOCATION': self.BACKUP, 
                    'IMPORTS LOCATION': self.IMPORTS, 
                    'LAST BACKUP': self.LAST_BACKUP, 
                    'BACKUP INTERVAL': self.BACKUP_INTERVAL, 
                    'AUTOSAVE': self.AUTOSAVE, 
                    'FIRST TIME': self.FIRST_TIME}
        fout = open(join(self.HOME, 'Journal.ini'), 'wb')
        pickle.dump(ini_file, fout)
        fout.close()
        
    def openJournalFile(self):
        try:
            fin = open(join(self.SAVE, "journal_db"), "rb")
            self.journal = pickle.load(fin)
        except FileNotFoundError:
            fin = open(join(self.SAVE, "journal_db"), "wb")
            self.journal = JObject.JObject()
        fin.close()
        
    def changeSaveDirectory(self):
        self.dir_opt = options = {}
        old = None
        if not self.SAVE:
            options['initialdir'] = self.HOME
        else:
            old = options['initialdir'] = self.SAVE
        options['mustexist'] = False
        options['parent'] = self.master
        options['title'] = 'Choose a Save Location'
        location = askdirectory(**self.dir_opt)
        if location != '':
            self.SAVE = location
            new = join(self.SAVE, 'journal_db')
            if not exists(new):
                if old:
                    move_db = askyesno('Move?', 'Do you want to move the old ' +\
                                      'database to the new location?')
                    if move_db:
                        move(join(old, 'journal_db'), self.SAVE)
                    else:
                        self.saveJournal(self.journal)
            self.saveIniFile()
        
    def changeBackupDirectory(self):
        self.backup_opt = options = {}
        old = None
        if not self.BACKUP:
            options['initialdir'] = self.HOME
        else:
            old = options['initialdir'] = self.BACKUP
        options['mustexist'] = False
        options['parent'] = self.master
        options['title'] = 'Choose a Location for the Backup Folder'
        location = askdirectory(**self.backup_opt)
        if location != '':
            self.BACKUP = join(location , "Backup")
            if not exists(self.BACKUP):
                if old:
                    move(old, self.BACKUP)
                else:
                    mkdir(self.BACKUP)
            self.saveIniFile()
                                
    def changeImportsDirectory(self):
        self.backup_opt = options = {}
        location = self.IMPORTS
        old = None
        if not location:
            options['initialdir'] = self.HOME
        else:
            old = options['initialdir'] = location
        options['mustexist'] = False
        options['parent'] = self.master
        options['title'] = 'Choose a Location for the Imports Folder'
        location = askdirectory(**self.backup_opt)
        if location != '':
            self.IMPORTS = join(location, 'Journal Imports')
            if not exists(self.IMPORTS):
                if old:
                    move(old, self.IMPORTS)
                else:
                    mkdir(self.IMPORTS)
            self.saveIniFile()
            
    def changeBackupSchedule(self):
        self.BACKUP_INTERVAL = self.backup_interval.get()            
        
    def toggleAutoSave(self):
        if self.auto_save.get() == True:
            self.auto_save.set(False)
        else:
            self.auto_save.set(True)
        self.AUTOSAVE = self.auto_save.get()
        
    def changeFirstTimeFlag(self):
        self.first_time.set(False)
        self.FIRST_TIME = False
            
    def backupDatabase(self):
        """Backs up the database held by the storage object(not the one
        passed to the journal object) and updates associated variables"""
        
        backup_loc = self.BACKUP
        test = exists(backup_loc)
        backup_db = None
        fout = None
        check = None
        if test:
            backup_db = join(backup_loc, 'journal_db')
            fout = open(backup_db, "wb")
        else:
            message = 'The backup folder could not be located at ' + backup_loc +\
            '.\n\n Would you like to reassign the directory?' +\
            '\n\n (If you choose not to reassign, you can do so later via the menu.)'
            new = askyesno('Directory Not Found!', message)
            self.BACKUP = None
            if new:
                self.changeBackupDirectory()
                fout = open(join(self.BACKUP, 'journal_db'), "wb")
            else:
                self.LAST_BACKUP = None
#                self.BACKUP_INTERVAL = -1
        if fout:
            pickle.dump(self.journal, fout)
            fout.close()
            att_loc = join(self.HOME, 'Attachments')
            try:
                check = listdir(att_loc)
            except FileNotFoundError:
                None
            if check:
                try:
                    remove(join(backup_loc, 'Attachments.zip'))
                except FileNotFoundError:
                    None
                make_archive('Attachments', 'zip', backup_loc, att_loc)
                move('Attachments.zip', backup_loc)
            date = DateTools.getCurrentDate()
            self.LAST_BACKUP = date
            self.last_backup.set(DateTools.getDateGUIFormat(date))
            
    def getSaveDirectory(self):
        return self.SAVE
        
    def getBackupDirectory(self):
        return self.BACKUP
        
    def getAutosaveVar(self):
        return self.auto_save
        
    def getBackupIntervalVar(self):
        return self.backup_interval
        
    def getLastBackupVar(self):
        return self.last_backup
    
    def getFirstTimeVar(self):
        return self.first_time
        
    def getJournal(self):
        return self.journal.__deepcopy__()
        
    def journalIsSaved(self, journal):
        if self.journal.equals(journal):
            return True
        else:
            return False
        
    def runBackup(self):
        if self.BACKUP_INTERVAL != -1:
            if self.FIRST_TIME:
                self.backupDatabase()
            today = DateTools.getCurrentDate()
            if self.LAST_BACKUP:
                if (today-self.LAST_BACKUP).total_seconds() > self.BACKUP_INTERVAL*3600:
                    self.backupDatabase()
#            else:
#                self.backupDatabase()
        
    def saveJournal(self, journal):
        """Saves the journal of the storage object (not the journal of the 
        journal object) [Is this the same journal?]"""
        
        fout = open(join(self.SAVE, "journal_db"), "wb")
        pickle.dump(journal, fout)
        fout.close()
        
    def closeStreams(self):
        None
        
    def createResourceFolder(self):
        tmp = join(self.HOME, 'Resources')
        if not exists(abspath(tmp)):
            mkdir(tmp)
            
#    def createImportsDirectory(self):
##        tmp = join(self.HOME, 'Imports')
##        if not exists(abspath(tmp)):
##            mkdir(tmp)
#        None
            
    def getWorkingDir(self):
        frozen = False
        if getattr(sys, 'frozen', False):
            frozen = True
            self.HOME = sys._MEIPASS
        else:
            self.HOME = dirname(abspath('Storage.py'))
            
    def getPath(self):
        return self.HOME
    
    def importEntry(self, jeif_path):
        if exists(jeif_path):    
            path = self.IMPORTS
            att_path = None
            fin = open(jeif_path)
            contents = fin.read()
            fin.close()
            date = contents.split('<Datetime>')[1]
            date = DateTools.createDatetimeObject(date.strip())
            body = contents.split('<Body>')[1].strip()
            if not body:
                body = '--Body section of import file was empty--'
            if not date:
                date = DateTools.getCurrentDate()
                body = '--This entry was created by an import file with ' +\
                             'no associated date. The import file can be ' +\
                             'viewed in the attachments folder associated ' +\
                             'with this entry--\n\n' + body
            tags = contents.split('<Tags>')[1].strip()
            if not tags:
                tags = ['Untagged']
                body += '--This entry was created without tags--'
            else:
                tags = tags.strip(',')
                tags = tags.split(',')
                tmp = tags.copy()
                for i in range(0, len(tmp)):
                    if tmp[i]:
                        tags.append(tmp[i].strip())
                    tags.pop(0)
            attachments = contents.split('<Attachment>')[1].strip()
            if attachments:
                attachments = attachments.strip(',')
                attachments = attachments.split(',')
                tmp = attachments.copy()
                for i in range(0, len(tmp)):
                    if tmp[i]:
                        attachments.append(tmp[i].strip())
                    attachments.pop(0)
            att_path = join(join(self.HOME, 'Attachments'), 
                            DateTools.getDateFileStorageFormat(date))
            if not exists(att_path):
                mkdir(att_path)
                move(jeif_path, att_path)
            else:
                remove(jeif_path)
            entry = JObject.JEntry(date=date, body=body, tags=tags, 
                                   attachments=attachments)
            self.journal.add(entry)
            for item in attachments:
                try:
                    item_path = abspath(join(path, item))
                    copy(item_path, att_path)
                    remove(item_path)
                except FileNotFoundError:
                    None
            
    def checkImports(self):
        path = self.IMPORTS
        if not path:
            self.changeImportsDirectory()
        check = None
        try:
            check = listdir(path)
        except FileNotFoundError:
            message = 'The imports folder could not be located at ' + path +\
            '.\n\n Would you like to reassign the directory?'
            new = askyesno('Directory Not Found!', message)
            if new:
                self.changeImportsDirectory()
                path = self.IMPORTS
                check = listdir(path)
        if check:
            for file in check:
                if file.endswith('.jeif'):
                    self.importEntry(abspath(join(path,file)))