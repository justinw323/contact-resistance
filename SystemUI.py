
from matplotlib.backends.backend_tkagg import FigureCanvas
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import tkinter as tk
from tkinter import ttk

import time
import csv
import os
import numpy as np

from controller import *
from Table_Entry import *
from Start_Page import *

pages = []
red = '#ff6e6e'
yellow = "#feffa6"
green = "#b0ffa1"

# Turn on relay only for measurement, then off

class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        self.controller, self.tdac = init_controller()
        clamp(self.tdac)
        self.running = False

        self.voltages = []
        self.times = []
        self.airpsi = []
        self.samplePressure = []
        self.gdl_tpr = []

        self.sp = []
        self.tpr = []
        self.cr = []

        self.ready = False
            
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)
            
        # creating a container
        container = tk.Frame(self) 
        container.pack(side = "top", fill = "both", expand = True)
    
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
    
        # initializing frames to an empty array
        self.frames = {}
        
        start_frame = Start_Page(container, self, self.ready)
        self.frames[Start_Page] = start_frame  
        start_frame.grid(row = 0, column = 0, sticky ="nsew")
        
        table_frame = Table_Entry(container, self)
        self.frames[Table_Entry] = table_frame  
        table_frame.grid(row = 0, column = 0, sticky ="nsew")

        self.update()
        
        self.show_frame(Start_Page)

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()
        self.update()
    
    def show_start(self):
        frame = self.frames[Start_Page]
        frame.tkraise()
        self.update()
    
    def show_table(self):
        frame = self.frames[Table_Entry]
        frame.tkraise()
        self.update()

    def relay(self, v):
        # Set to high to close, low to open
        self.controller.setDOState(2, state = v)

    def make_copier(self, row):
        return lambda: self.copy_row(row)

    def reg_read(self, rapid):
        if(self.running):
            print("running")
            return
        # Close the relay
        self.relay(1)
        self.running = True
        if(not self.ready):
            self.frames[Start_Page].label['text'] = 'No parameters set'
            self.frames[Start_Page].label['bg'] = red
            self.running = False
            return
        
        for i in range(20):
            if (self.frames[Start_Page].c_labels[i][1].get() != ''):
                self.frames[Start_Page].c_labels[i][1].set('--')
                self.frames[Start_Page].r_labels[i][1].set('--')
            else:
                break
            self.update()
                    
        times = [1.0 for x in range(len(self.voltages))] if rapid else self.times

        counter = 1
        self.samplePressure = []
        self.sp = []
        self.tpr = []
        self.cr = []
        graph_times = []
        graph_pressure = []
        graph_tpr = []
        graph_cr = []
        graph_gdltpr = []

        start_time = time.time()

        for i in range(len(self.voltages)):
            v = self.voltages[i]
            t = times[i]
            if(not self.running):
                return
            print(('Step %s' % counter))
            self.frames[Start_Page].label['text'] = 'Step %s' % counter
            self.frames[Start_Page].label['bg'] = yellow
            setVoltage(self.tdac, v)
            per_sec(self, self.controller, t, start_time, graph_times, 
                    graph_pressure,
                    self.gdl_tpr[i], graph_gdltpr, graph_tpr, graph_cr)

            reading = read(self.controller)
            v1 = reading[0]
            v2 = reading[1]
            v3 = reading[2]
            # Reading from AIN0, AIN1, AIN2
            # print(time.time())

            sp = v3
            tpr = v1-self.gdl_tpr[counter-1]
            cr = v2-(0.5*self.gdl_tpr[counter-1])
            self.sp.append(sp)
            self.tpr.append(tpr)
            self.cr.append(cr)
            self.frames[Start_Page].p_labels[counter-1][1].set(round(sp, 2))
            self.frames[Start_Page].r_labels[counter-1][1].set(round(tpr, 2))
            self.frames[Start_Page].c_labels[counter-1][1].set(round(cr, 2))
            self.update()
            counter += 1

        # elapsed = time.time() - start_time
        # intended = sum(times)
        # print(intended, elapsed)
        # print('off by ' + str((elapsed-intended)/intended))

        self.frames[Start_Page].graph(graph_times, 
                                      graph_pressure,
                                      graph_tpr, graph_cr)
        self.frames[Start_Page].label['text'] = 'Done'
        self.frames[Start_Page].label['bg'] = green
        self.running = False
        # Open the relay
        self.relay(0)
        clamp(self.tdac)
        # self.frames[Start_Page].save_to_file()
        self.update()

    def convert_readings(self, in1, in2, in3):
        # Three lists of readings in
        # Fill this out with whatever calculation for pressure
        return in1, in2, in3

    def stop_run(self):
        self.running = False
        self.frames[Start_Page].label['text'] = "Ready" 
        self.frames[Start_Page].label['bg'] = green
        clamp(self.tdac)
        self.update()

app = Application()

app.mainloop()




# Automatically savefile after run