# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 17:00:24 2016

@author: Kozmik
"""
from JObject import JEntry
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font

class BodyFrame(tk.Frame):
    def __init__(self, master=None, entry=None, **kw):
        root = None
        self.master = master
        if not self.master:
            root = tk.Tk()
            tk.Frame.__init__(self, root, **kw)
        else:
            tk.Frame.__init__(self, self.master, **kw)
        body_font = font.Font(family='Georgia', size=11)
        self.entry = entry
        if not self.entry:
            self.entry = JEntry()
        
        self.scrollbar = ttk.Scrollbar(self)
        self.body_field = tk.Text(self, font=body_font, yscrollcommand=self.scrollbar.set,
                               wrap=tk.WORD, bg='black', fg='lime green', 
                               insertbackground='white', height=20)        
        self.scrollbar.config(command=self.body_field.yview)
        self.body_field.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        
        if self.entry.getBody():
            self.updateGUI(self.entry)
        
        if root:
            root.mainloop()
        
    def updateGUI(self, entry):
        self.entry = entry
        self.clearBody()
        if entry.getBody():
            self.body_field.insert(tk.CURRENT, entry.getBody())
            
    def clearGUI(self, entry):
        self.entry = entry
        self.clearBody()
            
    def clearBody(self):
        self.body_field.delete('1.0', tk.END)
        
    def save(self):
        string = self.body_field.get('1.0', tk.END)
        if string.strip():
            self.entry.setBody(string.rstrip())
            
    def getBody(self):
        return self.body_field.get('1.0', tk.END).rstrip()
            
    def bodyFieldIsEmpty(self):
        if self.body_field.get('1.0', tk.END).strip():
            return False
        else:
            return True
    
    def grabFocus(self):
        self.body_field.focus_force()