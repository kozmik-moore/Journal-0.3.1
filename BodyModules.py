# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 17:00:24 2016

@author: Kozmik
"""
from JObject import *
from tkinter import *
from tkinter.ttk import *
from tkinter import font

class BodyFrame(Frame):
    def __init__(self, master=None, entry=None):
        root = None
        self.master = master
        if not self.master:
            root = Tk()
            Frame.__init__(self, root)
        else:
            Frame.__init__(self, self.master)
        body_font = font.Font(family='Microsoft Sans Serif', size=10)
        self.entry = entry
        if not self.entry:
            self.entry = JEntry()
        
        self.scrollbar = Scrollbar(self)
        self.body_field = Text(self, font=body_font, yscrollcommand=self.scrollbar.set, wrap=WORD)        
        self.scrollbar.config(command=self.body_field.yview)
        self.body_field.pack(side=LEFT, expand=True, fill=BOTH)
        self.scrollbar.pack(side=LEFT, fill=Y)
        
        if self.entry.getBody():
            self.updateGUI(self.entry)
        
        if root:
            root.mainloop()
        
    def updateGUI(self, entry):
        self.entry = entry
        self.clearBody()
        if entry.getBody():
            self.body_field.insert(CURRENT, entry.getBody())
            
    def clearGUI(self, entry):
        self.entry = entry
        self.clearBody()
            
    def clearBody(self):
        self.body_field.delete('1.0', END)
        
    def save(self):
        string = self.body_field.get('1.0', END)
        if string.strip():
            self.entry.setBody(string.rstrip())
            
    def getBody(self):
        return self.body_field.get('1.0', END).rstrip()
            
    def bodyFieldIsEmpty(self):
        if self.body_field.get('1.0', END).strip():
            return False
        else:
            return True