import tkinter as tk
from tkinter import ttk

import time
import os
import numpy as np
import json

from Start_Page import *

red = '#ff6e6e'
yellow = "#feffa6"
green = "#b0ffa1"

class Table_Entry(tk.Frame):
    def __init__(self, container, app):
        tk.Frame.__init__(self, container)
        self.winfo_toplevel().title("Enter Parameters")

        self.app = app

        self.dropdown = None
        self.load = None
        self.delete = None

        self.v_entries = []
        self.t_entries = []
        self.c_labels = []
        self.s_labels = []
        self.r_entries = []

        # 20 steps max
        self.steps = 20
        
        self.make_tables()

        self.label = tk.Label(self, text="Enter parameters", 
                         bg = yellow, width = 20)
        self.label.grid(row=self.steps+1, column=0, columnspan = 2,
                        padx = 10, pady = 10)

        

        # printVoltages = ttk.Button(self, text = 'pv', command = 
        #                          self.print_voltages)
        # printVoltages.grid(row=23, column=0, padx = 10, pady = 10)


        # fileName = tk.Label(self, text="")
        # fileName.grid(row=23, column=1,)

        backToStart = ttk.Button(self, text = "Back", command = 
                                 app.show_start)
        backToStart.grid(row = 25, column = 0, padx = 10, pady = 10, 
                         sticky = 'w')

        confirm = ttk.Button(self, text = "Load Current Settings", command = 
                            lambda : self.set_params(
                            [self.v_entries[x].get() for x in range(20)], 
                            [self.t_entries[x].get() for x in range(20)],
                            [self.r_entries[x].get() for x in range(20)],
                            ))
        confirm.grid(row = self.steps+2, column = 0, columnspan = 2,
                     padx = 10, pady = 10)
  
        presetVar = tk.StringVar()
        presetVar.set('Preset Name...')
        presetName = tk.Entry(self, textvariable = presetVar)
        presetName.grid(row=self.steps+1, column=2, sticky = 's')
        name = tk.Label(self, text = 'Preset name')
        name.grid(row=self.steps+1, column=2, sticky = 'n')
        save = ttk.Button(self, text = "Save Current Settings", command = 
                            lambda : self.save_preset(presetVar.get(),
                            [self.v_entries[x].get() for x in range(20)], 
                            [self.t_entries[x].get() for x in range(20)],
                            [self.r_entries[x].get() for x in range(20)],
                            ))
        save.grid(row = self.steps+2, column = 2, padx = 10, pady = 10)

        self.preset = tk.StringVar()
        self.preset.set("Select preset...")
        self.preset_menu()
    
    def make_tables(self):
        # Entry table
        for row in range(self.steps+1):
            for col in range(6):
                # Step
                if(col == 0):
                    label = tk.Label(self, text=("Step" if row == 0 
                                                 else str(row)), width= 15,
                                                 height = 2 if row == 0 else 1)
                    if(row == 0):
                        label['fg'] = "#ffffff"
                        label['bg'] = "#31353b"
                    label.grid(row=row, column=col)
                # Voltage
                elif(col == 1):
                    if(row == 0):
                        label = tk.Label(self, text=("Voltage"), fg = "#ffffff", 
                                         width = 22, bg="#31353b", height = 2)
                        label.grid(row=row, column=col)
                    else:
                        entry = tk.Entry(self)
                        self.v_entries.append(entry)
                        entry.grid(row=row, column=col)
                # Time
                elif(col == 2):
                    if(row == 0):
                        label = tk.Label(self, text=("Time (sec)"), 
                                         fg = "#ffffff", 
                                         width = 25, height = 2, bg="#31353b")
                        label.grid(row=row, column=col)
                    else:
                        entry = tk.Entry(self)
                        self.t_entries.append(entry)
                        entry.grid(row=row, column=col)
                # Compressed Air Pressure
                elif(col == 3):
                    label = tk.Label(self, text="Compressed Air\nPressure (psi)" 
                                     if row == 0 else "--", width = 20)
                    if(row == 0):
                        label['fg'] = "#ffffff"
                        label['bg'] = "#31353b"
                    else:
                        self.c_labels.append(label)
                    label.grid(row=row, column=col)
                # Sample pressure
                elif(col == 4):
                    label = tk.Label(self, text="Sample Pressure\n(psi)" 
                                     if row == 0 else "--", width = 20)
                    if(row == 0):
                        label['fg'] = "#ffffff"
                        label['bg'] = "#31353b"
                    else:
                        self.s_labels.append(label)
                    label.grid(row=row, column=col)
                # TPR
                elif(col == 5):
                    if(row == 0):
                        label = tk.Label(self, text=("GDL Through\nPlate Resistance"), fg = "#ffffff", 
                                         width = 24, bg="#31353b")
                        label.grid(row=row, column=col)
                    else:
                        entry = tk.Entry(self)
                        self.r_entries.append(entry)
                        entry.grid(row=row, column=col)

    def get_presets(self):
        with open('presets.json', 'r+') as file:
            file_data = json.load(file)
            presets = [key for key in file_data]
            file.close()
        return presets

    def preset_menu(self):
        presets = self.get_presets()
        if(self.dropdown != None):
            self.dropdown.destroy()
            self.load.destroy()
            self.delete.destroy()
        try:
            self.dropdown = tk.OptionMenu(self, self.preset, *(presets))
            self.dropdown.grid(row = self.steps+1, column = 3, columnspan = 2)
            self.load = tk.Button(self, text = 'Load preset', command = 
                             lambda : self.load_preset(self.preset.get()))
            self.load.grid(row=self.steps+2, column=3, pady=10, columnspan = 2)
            self.delete = tk.Button(self, text = 'Delete preset', command = 
                             lambda : self.delete_preset(self.preset.get()))
            self.delete.grid(row=self.steps+3, column=3, pady=10, columnspan = 2)
        except TypeError:
            pass

    def load_preset(self, preset):
        with open('presets.json', 'r+') as file:
            file_data = json.load(file)
            if(preset not in file_data):
                self.label['text'] = 'Preset not found'
                self.label['bg'] = red
                return
            else:
                program = file_data[preset]
                self.label['text'] = 'Preset "' + preset + '" loaded'
                self.label['bg'] = green
        # print(program)
        self.set_params([x[0] for x in program], [x[1] for x in program],
                        [x[2] for x in program])
        self.label['text'] = 'Preset "' + preset + '" loaded'

    def delete_preset(self, preset):
        with open('presets.json', 'r+') as file:
            file_data = json.load(file)
            if(preset not in file_data):
                self.label['text'] = 'Preset not found'
                self.label['bg'] = red
            else:
                file_data.pop(preset)
        open('presets.json', 'w').close()
        with open('presets.json', 'r+') as file:
            file.seek(0)
            json.dump(file_data, file, indent = 4)
        self.label['text'] = 'Preset "' + preset + '" deleted'
        self.label['bg'] = yellow
        self.preset_menu()

    def print_voltages(self):
        print(self.app.voltages)
        print(self.app.times)
        print(type(self.v_entries[0]))

    def go_back(self, str_voltages, str_times, msg):
        for v in range(len(str_voltages)):
            if(str_voltages[v]) != self.app.voltages[v]:
                msg['text'] = "Unsaved changes"
                msg['bg'] = yellow
        for t in str_times:
            self.app.times = float(t)

    def check_params(self, str_voltages, str_times, str_tpr):
        counter = 0
        try:
            for (v,t,r) in zip(str_voltages, str_times, str_tpr):
                # print(v,t,r)
                float(v)
                float(t)
                float(r)
                if(float(v) == 0.0 and float(t) == 0.0 and float(r) == 0.0):
                    return counter
                counter += 1
            return counter
        except:
            return 0
    
    def set_params(self, str_voltages, str_times, str_tpr):
        # print(str_voltages, str_times)
        steps = self.check_params(str_voltages, str_times, str_tpr)
        if(steps == 0):
            self.label['text'] = 'Invalid value(s)'
            self.label['bg'] = red
            return
        
        self.app.voltages = []
        self.app.times = []
        self.app.samplePressure = []
        self.app.gdl_tpr = []

        for v in range(steps):
            self.app.frames[Start_Page].s_labels[v]['text'] = str(v+1)

            # Clearing the entry tables
            self.v_entries[v].delete(0,tk.END)
            self.t_entries[v].delete(0,tk.END)
            self.r_entries[v].delete(0,tk.END)

            # Adding parameters to list
            self.app.voltages.append(float(str_voltages[v]))
            self.app.times.append(float(str_times[v]))
            self.app.gdl_tpr.append(float(str_tpr[v]))
            self.app.samplePressure.append(float(str_voltages[v])/10.0*50.0 * 7.0)

            # Updating entry tables
            self.v_entries[v].insert(0,str_voltages[v])
            self.t_entries[v].insert(0,str_times[v])
            self.r_entries[v].insert(0,str_tpr[v])

            # Grid the buttons and start page labels
            self.app.frames[Start_Page].copy_buttons[v].grid()
            self.app.frames[Start_Page].s_labels[v].grid()
            self.c_labels[v]['text'] = (str(float(
                str_voltages[v])/10.0*50.0) if (v < len(
                str_voltages)) else "--")
            self.s_labels[v]['text'] = (str(float(
                str_voltages[v])/10.0*50.0 * 7.0) if (v < len(
                str_voltages)) else "--")
            self.app.frames[Start_Page].p_labels[v][1].set("--")
            self.app.frames[Start_Page].p_labels[v][0].grid()
            self.app.frames[Start_Page].r_labels[v][1].set("--")
            self.app.frames[Start_Page].r_labels[v][0].grid()
            self.app.frames[Start_Page].c_labels[v][1].set("--")
            self.app.frames[Start_Page].c_labels[v][0].grid()

        self.label['text'] = 'Parameters loaded'
        self.label['bg'] = green

        for v in range(steps, 20):
            self.app.frames[Start_Page].copy_buttons[v].grid_remove()
            self.app.frames[Start_Page].s_labels[v].grid_remove()
            self.app.frames[Start_Page].p_labels[v][0].grid_remove()
            self.app.frames[Start_Page].r_labels[v][0].grid_remove()
            self.app.frames[Start_Page].c_labels[v][0].grid_remove()
            self.v_entries[v].delete(0,tk.END)
            self.t_entries[v].delete(0,tk.END)
            self.r_entries[v].delete(0,tk.END)
            self.c_labels[v]['text'] = "--"
            self.s_labels[v]['text'] = "--"

        if(not self.app.ready):  self.app.ready = True
        self.app.frames[Start_Page].label['text'] = 'Ready'
        self.app.frames[Start_Page].label['bg'] = green
        
    def save_preset(self, preset_name, str_voltages, str_times, str_tpr):        
        steps = self.check_params(str_voltages, str_times, str_tpr)
        if(steps == 0):
            self.label['text'] = 'Invalid value(s)'
            self.label['bg'] = red
            return
        with open('presets.json', 'r+') as file:
            file_data = json.load(file)
            zipped = list(zip([float(x) for x in str_voltages[:steps]], 
                              [float(y) for y in str_times[:steps]], 
                              [float(y) for y in str_tpr[:steps]]))
            file_data[preset_name] = zipped
            file.seek(0)
            json.dump(file_data, file, indent = 4)
            file.close()
        self.label['text'] = 'Preset "' + preset_name + '" saved'
        self.label['bg'] = green
        self.preset_menu()