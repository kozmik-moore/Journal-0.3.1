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
from os import listdir
from shutil import move
import pickle
from tkinter import BooleanVar
from tkinter import IntVar
from tkinter import StringVar
import DateTools
from tkinter.filedialog import askdirectory
import JObject
import sys

class Storage:
    def __init__(self, master=None):
#        self.config_path = path.abspath(getsourcefile(lambda:0)).strip('Storage.py')
        self.config_path = ''
        self.getWorkingDir()
        self.ini = {'SAVE LOCATION': None, 'BACKUP LOCATION': None, 'LAST BACKUP': None, 'BACKUP INTERVAL': 168, 'AUTOSAVE': False}
        self.journal = None
        self.master = master
        self.auto_save = BooleanVar(master=self.master, name='Autosave', value=self.ini['AUTOSAVE'])
        self.backup_interval = IntVar(master=self.master, name='Backup Interval', value=self.ini['BACKUP INTERVAL'])
        self.last_backup = StringVar(master=self.master, name='Last Backup', value=self.ini['LAST BACKUP'])
        
        self.createResourceFolder()
        self.createImportsDir()
        self.LoadIniFile()
        self.openJournalFile()
#        self.checkImports()
        self.runBackup()
         
    def LoadIniFile(self):
        try:
            fin = open(self.config_path + "/Journal.ini", "rb")
            self.ini = pickle.load(fin)
        except FileNotFoundError:
            self.changeSaveDirectory()
            fin = open(self.config_path + "/Journal.ini", "wb")
            pickle.dump(self.ini, fin)
        fin.close()
        self.auto_save.set(self.ini['AUTOSAVE'])
        self.backup_interval.set(self.ini['BACKUP INTERVAL'])
        if not self.ini['LAST BACKUP']:
            self.last_backup.set('Never')
        else:
            self.last_backup.set(DateTools.getDateGUIFormat(self.ini['LAST BACKUP']))
        
    def openJournalFile(self):
        try:
            fin = open(self.ini['SAVE LOCATION'] + "/journal_db", "rb")
            self.journal = pickle.load(fin)
        except FileNotFoundError:
            fin = open(self.ini['SAVE LOCATION'] + "/journal_db", "wb")
            self.journal = JObject.JObject()
        fin.close()
        
    def changeSaveDirectory(self):
        self.dir_opt = options = {}
        if not self.ini['SAVE LOCATION']:
            options['initialdir'] = self.config_path
        else:
            options['initialdir'] = self.ini['SAVE LOCATION']
        options['mustexist'] = False
        options['parent'] = self.master
        options['title'] = 'Choose a Save Location'
        location = askdirectory(**self.dir_opt)
        if location != '':
            self.ini['SAVE LOCATION'] = location + "/"
        
    def changeBackupDirectory(self):
        self.backup_opt = options = {}
        if not self.ini['BACKUP LOCATION']:
            options['initialdir'] = self.config_path
        else:
            options['initialdir'] = self.ini['BACKUP LOCATION']
        options['mustexist'] = False
        options['parent'] = self.master
        options['title'] = 'Choose a Location for the Backup Folder'
        location = askdirectory(**self.backup_opt)
        if location != '':
            self.ini['BACKUP LOCATION'] = location + "/Backup/"
            if not exists(self.ini['BACKUP LOCATION']):
                mkdir(self.ini['BACKUP LOCATION'])
            
    def changeBackupSchedule(self):
        self.ini['BACKUP INTERVAL'] = self.backup_interval.get()            
        
    def toggleAutoSave(self):
        if self.auto_save.get() == True:
            self.auto_save.set(False)
        else:
            self.auto_save.set(True)
        self.ini['AUTOSAVE'] = self.auto_save.get()
        
#    def checkBackup(self):
#        today = DateTools.getCurrentDate()
#        if self.ini['LAST BACKUP']:
#            if (today-self.ini['LAST BACKUP']).total_seconds() > self.ini['BACKUP INTERVAL']*3600:
#                self.backupDatabase()
#        else:
#            self.backupDatabase()
            
    def backupDatabase(self):
        """Backs up the database held by the storage object(not the one
        passed to the journal object) and updates associated variables"""
        
        if self.ini['BACKUP LOCATION']:
            fout = open(self.ini['BACKUP LOCATION'] + "/journal_db", "wb")
        else:
            self.changeBackupDirectory()
            fout = open(self.ini['BACKUP LOCATION'] + "/journal_db", "wb")
        pickle.dump(self.journal, fout)
        fout.close()
        date = DateTools.getCurrentDate()
        self.ini['LAST BACKUP'] = date
        self.last_backup.set(DateTools.getDateGUIFormat(date))
            
    def getSaveDirectory(self):
        return self.ini['SAVE LOCATION']
        
    def getBackupDirectory(self):
        return self.ini['BACKUP LOCATION']
        
    def getAutosaveVar(self):
        return self.auto_save
        
    def getBackupIntervalVar(self):
        return self.backup_interval
        
    def getLastBackupVar(self):
        return self.last_backup
        
    def getJournal(self):
        return self.journal.__deepcopy__()
        
    def journalIsSaved(self, journal):
        if self.journal.equals(journal):
            return True
        else:
            return False
        
    def runBackup(self):
        if self.ini['BACKUP INTERVAL'] != -1:
            if not self.ini['BACKUP LOCATION']:
                self.changeBackupDirectory()
            today = DateTools.getCurrentDate()
            if self.ini['LAST BACKUP']:
                if (today-self.ini['LAST BACKUP']).total_seconds() > self.ini['BACKUP INTERVAL']*3600:
                    self.backupDatabase()
            else:
                self.backupDatabase()
    
    def saveIniFile(self):
        fout = open(self.config_path + '/Journal.ini', 'wb')
        pickle.dump(self.ini, fout)
        fout.close()
        
    def saveJournal(self, journal):
        """Saves the journal of the storage object (not the journal of the 
        journal object) [Is this the same journal?]"""
        
        fout = open(self.ini['SAVE LOCATION'] + "/journal_db", "wb")
        pickle.dump(journal, fout)
        fout.close()
        
    def closeStreams(self):
        None
        
    def createResourceFolder(self):
        tmp = self.config_path+'/Resources'
        if not exists(abspath(tmp)):
            mkdir(tmp)
            
    def createImportsDir(self):
        tmp = join(self.config_path, 'Imports\\')
        if not exists(abspath(tmp)):
            mkdir(tmp)
            
    def getWorkingDir(self):
        frozen = False
        if getattr(sys, 'frozen', False):
            frozen = True
            self.config_path = sys._MEIPASS
        else:
            self.config_path = dirname(abspath('Storage.py'))
            
    def getPath(self):
        return self.config_path
    
    def importEntry(self, jeif_path):
        if exists(jeif_path):
            att_path = None
            fin = open(jeif_path)
            contents = fin.read()
            fin.close()
            date = contents.split('<Datetime>')[1]
            date = DateTools.createDatetimeObject(date.strip())
            body = contents.split('<Body>')[1]
            if not body:
                body = '(Body section of import file was empty.)'
            if not date:
                date = DateTools.getCurrentDate()
                body = 'This entry was created by an import file with ' +\
                             'no associated date. The import file can be ' +\
                             'viewed in the attachments folder associated ' +\
                             'with this entry.\n\n' + body
            att_path = join(self.config_path, 'Attachments\\' + 
                            DateTools.getDateFileStorageFormat(date))
            mkdir(att_path)
            move(jeif_path, att_path)
            tags = contents.split('<Tags>')[1]
            tags = tags.strip()
            tags = tags.strip(',')
            tags = tags.split(',')
            for i in range(0, len(tags)):
                tags[i] = tags[i].strip()
            if not tags:
                tags = ['Untagged']
            entry = JObject.JEntry(date, body, tags)
            self.journal.add(entry)
            
    def checkImports(self):
        path = join(self.config_path, 'Imports\\')
        check = listdir(path)
        if check:
            for file in check:
                if file.endswith('.jeif'):
                    self.importEntry(abspath(join(path,file)))