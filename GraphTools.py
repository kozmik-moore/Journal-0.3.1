# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 10:02:45 2017

@author: Kozmik
"""

from tkinter import *
from tkinter.ttk import *
from JObject import *
import DateTools

#class ButtonGraph:
#    def __init__(self):
#        None

INF = -1
NIL = None
       
class JGraph:
    def __init__(self, controller, journal):
        self.controller = controller
        self.journal=journal
        self.number_vertices = 0
        self.adjacency = {}
        self.parent = {}
        self.color = {}
        self.discovered = {}
        self.finished = {}
        self.time = 0
        for date in self.journal.getAllDates():
            self.adjacency[date] = []
            parent = self.journal.getEntry(date).getParent()
            if parent:
                self.adjacency[parent].append(date)
            self.number_vertices += 1
        self.tree_list = []
        self.widest = 0
        self.height = 0
        self.piles = []
        self.coordinates = {}
        
        self.graph_dialog = None
        self.preview_dialog = None
        
        self.style = Style()
        self.style.configure('Bold.TButton', font=('Sans', '8', 'bold'), background='black')
        
    def BFS(self, date):
        self.discovered = {}
        self.color = {}
        for vertex in self.journal.getAllDates():
            self.color[vertex] = 'white'
            self.discovered[vertex] = INF
            self.parent[vertex] = NIL
        self.color[date] = 'gray'
        self.discovered[date] = 0
        self.parent[date] = NIL
        queue = []
        queue.append(date)
        while queue:
            pointer = queue.pop(0)
            for vertex in self.adjacency[pointer]:
                if self.color[vertex] is 'white':
                    self.color[vertex] = 'gray'
                    self.discovered[vertex] = self.discovered[pointer] + 1
                    self.parent[vertex] = pointer
                    queue.append(vertex)
            self.color[pointer] = 'black'
            
    def findTreeDims(self, date):
        self.constructAdjacencies()         ##Inefficient: fix later with 'add' and 'delete'
        self.BFS(date)
        self.height = 0
#        self.coordinates = {}
        """Compute the height and size of the widest level of the tree"""
        discovered = list(sorted(self.discovered.values()))
        widths = {}
        for time in discovered:
            if time is not -1:
                if time not in widths:
                    widths[time] = 1
                else:
                    widths[time] += 1
            if self.height < time:
                self.height = time
        self.height += 1
        for number in widths:
            if widths[number] > self.widest:
                self.widest = widths[number]
        if self.widest == 0:
            self.widest = 1
        """Compute the size of each tree level"""
        piles = []
        for i in range(self.height):
            piles.append([])
        for date in sorted(self.discovered):
            if self.discovered[date] is not -1:
                piles[self.discovered[date]].append(date)
        """Compute coordinates of each node in the tree"""
        for i in range(0, len(piles)):
            for j in range(0, len(piles[i])):
                self.coordinates[piles[i][j]] = ((j+1)*(self.widest/(len(piles[i])+1)), self.height-i)
            
            
    def addEntry(self, date):
        self.adjacency[date] = []
        parent = self.journal.getEntry(date).getParent()
        if parent:
            self.adjacency[parent].append(date)
        self.number_vertices += 1
        
    def deleteEntry(self, date):
        parent = self.journal.getEntry(date).getParent()
        if parent:
            self.adjacency[parent].remove(date)
        del self.adjacency[date]
        self.number_vertices -= 1
        
    def constructAdjacencies(self):
        self.number_vertices = 0
        self.adjacency = {}
        for date in self.journal.getAllDates():
            self.adjacency[date] = []
            parent = self.journal.getEntry(date).getParent()
            if parent:
                self.adjacency[parent].append(date)
            self.number_vertices += 1
        
    def creatGraphDialog(self, date):
        
        self.findTreeDims(self.getRoot(date))
        
        self.graph_dialog = Toplevel()
        self.graph_dialog.title('Graph')
        self.graph_dialog.grab_set()
        xbar = Scrollbar(self.graph_dialog, orient=HORIZONTAL)
        ybar = Scrollbar(self.graph_dialog)
        canvas = Canvas(self.graph_dialog, yscrollcommand=ybar.set, xscrollcommand=xbar.set)
#        a=200
#        b=100
#        canvas.create_line(0,0,a,b)
        xbar.config(command=canvas.xview)
        ybar.config(command=canvas.yview)
        canvas.pack()
        xbar.pack(side=BOTTOM, fill=X)
        ybar.pack(side=RIGHT, fill=Y)
        for date in sorted(self.coordinates):
            x=self.coordinates[date][0]*250
            y=self.coordinates[date][1]*75
            if self.journal.getEntry(date).getChild():
                children = self.journal.getEntry(date).getChild()
                for child in children:
                    u = self.coordinates[child][0]*250
                    v = self.coordinates[child][1]*75
                    canvas.create_line(x,y,u,v)
        for date in sorted(self.coordinates):
            x=self.coordinates[date][0]*250
            y=self.coordinates[date][1]*75
            window = canvas.create_window(x,y,height=40, width=150)
            button=Button(canvas, text=DateTools.getDateGUIFormat(date), command=lambda date=date:self.previewEntry(date))
            canvas.itemconfig(window, window=button)
#        size = canvas.bbox('all')
#        width = size[2]-size[0]
#        height = size[3]-size[1]
#        canvas.config(width=width, height=height)
        self.graph_dialog.protocol("WM_DELETE_WINDOW", self.destroyGraphDialog)
        
    def destroyGraphDialog(self):
        try:
            self.graph_dialog.destroy()
        except AttributeError:
            pass
        self.graph_dialog = None
        self.coordinates = {}
        self.height=0
        self.widest
        
    def goToEntry(self, date):
        self.controller.updateGUI(entry=self.journal.getEntry(date))
        self.destroyPreviewDialog()
        self.destroyGraphDialog()
        
    def previewEntry(self, date):
        entry = self.journal.getEntry(date)
        
        self.preview_dialog = Toplevel()
        self.preview_dialog.title('Preview')
        self.preview_dialog.grab_set()
        outer_frame = Frame(self.preview_dialog)
        body_frame = Frame(outer_frame)
        tags_frame = Frame(outer_frame, height=1)
        date_label = Label(outer_frame, text=DateTools.getDateGUIFormat(date))
        scrollbar = Scrollbar(body_frame)
        body = Text(body_frame, wrap=WORD, yscrollcommand=scrollbar.set)
        scrollbar.config(command=body.yview)
        body.insert(INSERT, entry.getBody())
        body.config(state='disabled')
        tags_label = Label(tags_frame, text='Tags:')
        tags_list = ''
        tags_list += entry.getTags()[0]
        for i in range(1, len(entry.getTags())-1):
            tags_list += ', ' + entry.getTags()[i]
        tags = Text(tags_frame, height=1)
        tags.insert(INSERT, tags_list)
        tags.config(state='disabled')
        button = Button(outer_frame, style='Bold.TButton', text='Go To Entry', command=lambda date=date: self.goToEntry(date))
        outer_frame.pack()
        date_label.pack()
        body_frame.pack()
        body.pack(side=LEFT)
        scrollbar.pack(side=LEFT, fill=Y)
        tags_frame.pack()
        tags_label.pack(side=LEFT)
        tags.pack(side=LEFT)
        button.pack()
        
        self.preview_dialog.protocol('WM_DELETE_WINDOW', self.destroyPreviewDialog)
        
    def destroyPreviewDialog(self):
        self.preview_dialog.destroy()
        self.preview_dialog = None        
        
    def getRoot(self, date):
        root = self.journal.getEntry(date)
        parent = None
        if root.getParent():
            parent = self.journal.getEntry(root.getParent())
        while parent:
            root = parent
            if root.getParent():
                parent = self.journal.getEntry(root.getParent())
            else:
                parent = None
        return root.getDate()
        
    def updateGUI(self):
        None
        
            