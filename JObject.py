# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 16:45:07 2016

@author: Kozmik
"""

class JEntry:
    def __init__(self, date=None, body=None, tags=None, parent=None):
        self.date = date      #datetime object
        self.body = body
        self.tags = tags
        if not tags:
            self.tags = []
        self.parent = parent  #datetime object
        self.child = []
        
    def getDate(self):
        return self.date
        
    def getBody(self):
        return self.body
        
    def getTags(self):
        return sorted(self.tags)
        
    def getParent(self):
        return self.parent
        
    def getChild(self):         #change to 'children'
        return self.child
        
    def setDate(self, date):
        self.date = date
        
    def setBody(self, body):
        self.body = body.rstrip()
        
    def setTags(self, tags):
        self.tags = tags
        
    def setParent(self, parent):
        self.parent = parent
        
    def setChild(self, child):
        self.child.append(child)
        
    def addTag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)
        
    def removeTag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)
            
    def linkParent(self, date):
        self.parent = date
        
    def unlinkParent(self):
        self.parent = None
        
    def linkChild(self, date):
        if date not in self.child:
            self.child.append(date)
        
    def unlinkChild(self, date):
        self.child.remove(date)
        
#    def deleteChildren(self):
#        self.child = []
#        
#    def importChildren(self, children):
#        self.child = children
        
    def __deepcopy__(self):
        new = JEntry(self.date, self.body, self.tags, self.parent)
        if self.child:
            for date in self.child:
                new.linkChild(date)
        return new
        
    def equals(self, entry):
        if len(self.getTags()) != len(entry.getTags()):
            return False
        if self.date != entry.getDate():
            return False
        if self.body != entry.getBody():
            return False
        if self.parent != entry.getParent():
            return False
        if self.child != entry.getChild():
            return False
        for tag in self.tags:
            if tag not in entry.getTags():
                return False
        return True


class JObject:
    def __init__(self):
        self.storage = dict()
        self.population = 0
        self.tagslist = []
        
    def getAllDates(self):
        return sorted(self.storage.keys())
        
    def getAllTags(self):
        self.sortTags()
        return sorted(self.tagslist)
        
    def sortTags(self):
        for date in self.storage:
            for tag in self.storage[date].getTags():
                if tag not in self.tagslist:
                    self.tagslist.append(tag)
        self.tagslist = sorted(self.tagslist)
                    
    def add(self, entry):
        self.storage[entry.getDate()] = entry
        if entry not in self.storage:
            self.population += 1
        
    def delete(self, entry):
#        if entry in self.storage:
        parent = entry.getParent()
        if parent:
            self.getEntry(parent).unlinkChild(entry.getDate())
        children = entry.getChild()
        if children:
            for child in children:
                self.getEntry(child).unlinkParent()
        del self.storage[entry.getDate()]
        self.population -= 1
        
    def getEntry(self, date):
        return self.storage[date]
        
    def getNumberOfEntries(self):
        return self.population
        
    def __deepcopy__(self):
        new = JObject()
        for date in self.getAllDates():
            new.add(self.getEntry(date).__deepcopy__())
        return new   
        
    def isEmpty(self):
        if self.storage:
            return False
        else:
            return True
            
    def equals(self, journal):
        if self.population != journal.getNumberOfEntries():
            return False
        for date in self.getAllDates():
            if date not in journal.getAllDates():
                return False
            else:
                if not self.getEntry(date).equals(journal.getEntry(date)):
                    return False
        return True
