# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 02:27:54 2017

@author: Kozmik
"""

from JObject import JObject
from tkinter import BooleanVar

class TagSelectionManager:
    def __init__(self, journal, boolean, ident):
        """Creates a dictionary of lists that each contains a BooleanVar corresponding
        to a specific tag"""
        self.journal = JObject()
        self.vars = {}
        self.id = ident
        self.default_bool = boolean
        if journal:
            self.journal = journal
            self.updateVarsDict()
        
    def updateVarsDict(self):
        "Manages the BooleanVars in the dict"
        for tag in self.journal.getAllTags():
            if tag not in self.vars:
                self.vars[tag] = [BooleanVar(master=None, value=self.default_bool, name=self.id+tag), None]
        for tag in list(self.vars):
            if tag not in self.journal.getAllTags():
                del self.vars[tag]
                
    def activateTag(self, tag):
        if tag not in self.vars:
            self.vars[tag] = [BooleanVar(master=None, value=True, name=self.id+tag), None]
        else:
            self.vars[tag][0].set(1)
            
    def deactivateTag(self, tag):
        if tag in self.vars:
            self.vars[tag][0].set(0)
                
    def getState(self, tag):
        return self.vars[tag][0].get()
            
    def getStates(self):
        "Returns a dictionary of boolean objects representing selected tags"
        states = {}
        for tag in self.vars:
            states[tag] = self.vars[tag][0].get()
        return states
    
    def getActiveBoolVars(self):
        """Returns a list of the active BooleanVars, in string format"""
        active = []
        states = self.getStates()
        for tag in states:
            if states[tag]:
                active.append(tag)
        return active
        
    def getVarsDict(self):
        "Updates and returns the dictionary of BooleanVars"
        self.updateVarsDict()
        return self.vars
        
    def anyBoxesChecked(self):
        "Checks to see if any of the BooleanVars are set to true (i.e. any tag is selected)"
        for tag in self.vars:
            if self.vars[tag][0].get():
                return True
        return False
        
    def boxChecked(self, tag):
        "Checks to see if a specific BooleanVar is set to true (i.e. a tag is selected)"
        if self.tagslist[tag][0].get():
            return True
        else:
            return False