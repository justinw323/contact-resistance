
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
from LabJackPython import *

pages = []
red = '#ff6e6e'
yellow = "#feffa6"
green = "#b0ffa1"

# Turn on relay only for measurement, then off

class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        self.running = False
        self.clamping = False
        
        # self.controller, self.tdac = init_controller()

        self.voltages = []
        self.times = []
        self.airpsi = []
        self.samplePressure = []
        self.gdl_tpr = []
        self.area = 0.0

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

    def clamp_unclamp(self):
        if self.clamping:
            self.frames[Start_Page].cl['text'] = 'Clamp'
            unclamp(self.tdac)
            self.close_controller()
        else:
            self.frames[Start_Page].cl['text'] = 'Unclamp'
            self.controller, self.tdac = init_controller()
            clamp(self.tdac)
        self.clamping = not self.clamping

    def reg_read(self, rapid):
        if(self.running):
            return
        # Close the relay
        if(not self.ready):
            self.frames[Start_Page].label['text'] = 'No parameters set'
            self.frames[Start_Page].label['bg'] = red
            self.running = False
            return
        self.running = True
        self.controller, self.tdac = init_controller()
        clamp(self.tdac)
        self.relay(1)
        
        for i in range(20):
            if (self.frames[Start_Page].c_labels[i][1].get() != ''):
                self.frames[Start_Page].p_labels[i][1].set('--')
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
            # print(('Step %s' % counter))
            self.frames[Start_Page].label['text'] = 'Step %s' % counter
            self.frames[Start_Page].label['bg'] = yellow
            setVoltage(self.tdac, v)
            tpr_stream, cr_stream, sp_stream = per_sec(self, self.controller, t, 
                                            start_time, graph_times, 
                                            graph_pressure, self.gdl_tpr[i], 
                                            graph_gdltpr, graph_tpr, graph_cr,
                                            self.area)
            # Final third of measurement
            tpr_stream = tpr_stream[int(2*len(tpr_stream)/3):]
            cr_stream = cr_stream[int(2*len(cr_stream)/3):]
            sp_stream = sp_stream[int(2*len(sp_stream)/3):]
            try:
                tpr = sum(tpr_stream)/len(tpr_stream)        # Through-plate voltage
                cr = sum(cr_stream)/len(cr_stream)          # Contact voltage
                sp = sum(sp_stream)/len(sp_stream)          # Pressure
            except ZeroDivisionError:
                continue
            # print('Readings: ', read(self.controller)[0] - 0.4)
            # print('TPR: ', tpr)
            # Reading from AIN0, AIN1, AIN2
            # print(time.time())

            self.sp.append(sp)
            self.tpr.append(tpr)
            self.cr.append(cr)
            self.frames[Start_Page].p_labels[counter-1][1].set(round(sp, 2))
            self.frames[Start_Page].r_labels[counter-1][1].set(round(tpr, 2))
            self.frames[Start_Page].c_labels[counter-1][1].set(round(cr, 2))
            self.frames[Start_Page].graph(graph_times, 
                                        graph_pressure,
                                        graph_tpr, graph_cr)
            self.update()
            counter += 1


        self.frames[Start_Page].label['text'] = 'Done'
        self.frames[Start_Page].label['bg'] = green
        self.running = False
        # Open the relay
        self.relay(0)
        unclamp(self.tdac)
        self.update()
        # self.close_controller()

    def close_controller(self):
        if(self.controller == None):
            return
        unclamp(self.tdac)
        self.controller.close()
        Close()
        self.controller = None
        self.tdac = None

    def stop_run(self):
        self.running = False
        self.frames[Start_Page].label['text'] = "Ready" 
        self.frames[Start_Page].label['bg'] = green
        self.relay(0)
        unclamp(self.tdac)
        self.update()
        self.close_controller()

if __name__ == "__main__":
    app = Application()
    try:
        app.mainloop()
    finally:
        app.close_controller()