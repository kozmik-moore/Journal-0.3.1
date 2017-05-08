# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 10:02:45 2017

@author: Kozmik
"""

import tkinter as tk
import tkinter.ttk as ttk
from JObject import *
import DateTools

INF = -1
NIL = None
WIDTH = 300
HEIGHT = 200
BUTTON_LENGTH = 180
BUTTON_HEIGHT = 60
       
class JGraph(tk.Frame):
    def __init__(self, master, controller, journal, entry, **kw):
        self.master = master
        self.controller = controller
        self.journal=journal
        self.entry=entry
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
        
        self.style = ttk.Style()        
        self.style.configure('Current.TButton', width='', background='black', border=10)
        tk.Frame.__init__(self, self.master, **kw)
        self.NEWLINK = ttk.Button(master=self, style='UI.TButton', takefocus=0, text="Create Linked Entry", command=self.controller.newLink)
        self.DISPLAY = ttk.Button(master=self, style='UI.TButton', takefocus=0, text="Display Linked Entries", 
                              command=self.creatGraphDialog, state='disabled')
        self.NEWLINK.pack(fill='x')
        self.DISPLAY.pack(fill='x')
        
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
            x_value = -1*(len(piles[i])-1)/2
            for j in range(0, len(piles[i])):
                self.coordinates[piles[i][j]] = (x_value, self.height-i)
                x_value = x_value+1            
            
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
        
    def creatGraphDialog(self):
        date = self.entry.getDate()
        self.findTreeDims(self.getRoot(date))
        current = date
        
        self.graph_dialog = tk.Toplevel()
        self.graph_dialog.title('Graph')
        self.graph_dialog.grab_set()
        frame = tk.Frame(self.graph_dialog)
        xbar = ttk.Scrollbar(frame, orient='horizontal')
        ybar = ttk.Scrollbar(frame, orient='vertical')
        canvas = tk.Canvas(frame, yscrollcommand=ybar.set, xscrollcommand=xbar.set, 
                           bg='light slate gray')
        xbar.pack(side='bottom', fill='x')
        ybar.pack(side='right', fill='y')
        frame.pack(expand=True, fill='both')
        for date in sorted(self.coordinates):
            x=self.coordinates[date][0]*BUTTON_LENGTH
            y=self.coordinates[date][1]*BUTTON_HEIGHT
            if self.journal.getEntry(date).getChild():
                children = self.journal.getEntry(date).getChild()
                for child in children:
                    u = self.coordinates[child][0]*BUTTON_LENGTH
                    v = self.coordinates[child][1]*BUTTON_HEIGHT
                    canvas.create_line(x,y,u,v)
        for date in sorted(self.coordinates):
            x=self.coordinates[date][0]*BUTTON_LENGTH
            y=self.coordinates[date][1]*BUTTON_HEIGHT
            window = canvas.create_window(x,y)
            button=ttk.Button(canvas, takefocus=0, width=26, text=DateTools.getDateGUIFormat(date), 
                                  command=lambda date=date:self.previewEntry(date))
            if current == date:
                button.config(style='Current.UI.TButton')
            canvas.itemconfig(window, window=button)
        size = (canvas.bbox('all'))
        region = list(size)
        for i in range(len(region)):
            if i==3 or i==2:
                region[i] += 100
            else:
                region[i] -= 100
        region = tuple(region)
        canvas.config(scrollregion=region)
        width = region[2]-region[0]
        height = region[3]-region[1]
        screen_width = self.graph_dialog.winfo_screenwidth()
        screen_height = self.graph_dialog.winfo_screenheight()
        if width > screen_width:
            width = screen_width
        if height > screen_height:
            height = screen_height
        if width < WIDTH:
            width = WIDTH
        if height < HEIGHT:
            height = HEIGHT
        dims = str(width)+'x'+str(height)
        canvas.pack(fill='both', expand=True)
        self.graph_dialog.geometry(dims)
        self.graph_dialog.update_idletasks()
        xbar.config(command=canvas.xview)
        ybar.config(command=canvas.yview)
        canvas.xview_moveto(.15)
        self.graph_dialog.focus_force()
        self.graph_dialog.protocol("WM_DELETE_WINDOW", self.destroyGraphDialog)
        
    def destroyGraphDialog(self):
        try:
            self.graph_dialog.destroy()
        except AttributeError:
            pass
        self.graph_dialog = None
        self.coordinates = {}
        self.height = 0
        self.widest = 0
        
    def goToEntry(self, date):
        self.controller.updateGUI(entry=self.journal.getEntry(date))
        self.destroyPreviewDialog()
        self.destroyGraphDialog()
        
    def previewEntry(self, date):
        entry = self.journal.getEntry(date)
        
        self.preview_dialog = tk.Toplevel(bg='slate gray')
        self.preview_dialog.title('Preview')
        self.preview_dialog.grab_set()
        outer_frame = tk.Frame(self.preview_dialog, bg='slate gray')
        body_frame = tk.Frame(outer_frame, bg='slate gray')
        tags_frame = tk.Frame(outer_frame, height=1, bg='slate gray')
        
        date_label = ttk.Label(outer_frame, text=DateTools.getDateGUIFormat(date))
        
        scrollbar = ttk.Scrollbar(body_frame)
        body = tk.Text(body_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, bg='black', 
                       fg='lime green')
        scrollbar.config(command=body.yview)
        body.insert('insert', entry.getBody())
        body.config(state='disabled')
        
        tags_label = ttk.Label(tags_frame, text='Tags:')
        tags_list = ''
        tmp = entry.getTags()
        tags_list += tmp.pop(0)
        while len(tmp) != 0:
            tags_list += ', '
            tags_list += tmp.pop(0)
        tags_scrollbar = ttk.Scrollbar(tags_frame)
        tags = tk.Text(tags_frame, height=1, wrap='word', yscrollcommand=tags_scrollbar.set, 
                       bg='black', fg='lime green')
        tags_scrollbar.config(command=tags.yview)
        tags.insert('insert', tags_list)
        tags.config(state='disabled')
        
        button = ttk.Button(outer_frame, style='Bold.UI.TButton', text='Go To Entry',
                        command=lambda date=date: self.goToEntry(date))
        
        outer_frame.pack()
        date_label.pack()
        body_frame.pack()
        body.pack(side='left')
        scrollbar.pack(side='left', fill='y')
        tags_frame.pack()
        tags_label.pack(side='left')
        tags.pack(side='left')
        tags_scrollbar.pack(side='left')
        button.pack()
        self.preview_dialog.focus_force()
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
        
    def updateGUI(self, entry):
        self.entry = entry
        if (not self.entry.getChild() and not self.entry.getParent()) or not self.entry.getDate():
            self.DISPLAY.config(state='disabled')
        else:
            self.DISPLAY.config(state='normal')
            
    def clearGUI(self, entry):
        self.destroyGraphDialog()
        self.updateGUI(entry)