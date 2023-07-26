import random
import os

from matplotlib.backends.backend_tkagg import FigureCanvas
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog

from Table_Entry import *
from controller import *

red = '#ff6e6e'
yellow = "#feffa6"
green = "#b0ffa1"

class Start_Page(tk.Frame):
    def __init__(self, container, app, ready):
        tk.Frame.__init__(self, container)
        self.winfo_toplevel().title("Contact Resistance")

        self.ready = ready
        self.app = app

        # v = Scrollbar(self, orient='vertical')    

        readV = ttk.Button(self, text = "Start", command = 
                           lambda: app.reg_read(False))
        readV.grid(row = 22, column = 2, padx = 10, pady = 10)

        rapid = ttk.Button(self, text = "Rapid", command = 
                           lambda: app.reg_read(True))
        # rapid.grid(row = 25, column = 2, padx = 10, pady = 10)

        enter_params = ttk.Button(self, text = "Parameters", command = 
                                app.show_table)
        enter_params.grid(row = 22, column = 4, padx = 10, pady = 10)

        stop = ttk.Button(self, text = "Stop", command = app.stop_run)
        stop.grid(row = 23, column = 2, padx = 10, pady = 10)

        notesHere = tk.Label(self, text='Notes for measurement:')
        notesHere.grid(row=23, column=1, sticky = 's')
        self.notes = ScrolledText(self, width = 40, height = 5)
        self.notes.grid(row=24, rowspan = 3, column=1, padx = 10, sticky = 'n')

        self.label = tk.Label(self, text="Waiting for parameters" if not self.ready
                               else "Ready", 
                         bg = yellow if not self.ready else green)
        self.label.grid(row=22, column=1, padx = 10)

        readVoltages = ttk.Button(self, text = 'read', command = 
                                 lambda : print_read(app.controller))
        readVoltages.grid(row=23, column=4, padx = 10, pady = 10)

        pv = ttk.Button(self, text = 'pv', command = self.print_voltages)
        pv.grid(row=23, column=3, padx = 10, pady = 10)

        self.cl = ttk.Button(self, text = 'Clamp', command = app.clamp_unclamp)
        self.cl.grid(row=22, column=3, padx = 10, pady = 10)

        fileField = tk.Label(self, text='File Name: (exclude ".csv")')
        fileField.grid(row=22, column=5, sticky = 'n')

        fileName = tk.StringVar()
        saveFile = tk.Entry(self, textvariable = fileName)
        saveFile.grid(row=22, column=5, sticky = 's')

        save = tk.Button(self, text = "Save to File", 
                          command = lambda: self.save_to_file(fileName.get()))
        save.grid(row=23, column=5, padx = 10, pady=10)

        saveFolder = tk.Button(self, text = "Save to Folder", 
                          command = lambda: self.save_to_folder(fileName.get()))
        saveFolder.grid(row=24, column=5, padx = 10, pady=10, sticky = 'n')

        self.fig = Figure(figsize=(5,5), dpi=100)
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.set_xlabel("Time (s)")
        self.ax1.set_ylabel("Resistance (ohm)")
        self.ax1.set(ylim=(0, 500))
        self.ax2 = self.ax1.twinx()
        self.ax2.set_ylabel('psi')
        randlist1 = [random.randint(0,10) for x in range(8)]
        randlist2 = [random.randint(0,10) for x in range(8)]
        self.ax1.plot([1,2,3,4,5,6,7,8],randlist1, color = 'tab:red')
        self.ax2.plot([1,2,3,4,5,6,7,8],randlist2, color = 'tab:blue')
        # self.fig.legend()
        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.graph_widget = self.canvas.get_tk_widget()
        self.graph_widget.grid(row = 1, column = 1, rowspan=21)

        toolbar = NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False)
        toolbar.update()
        self.canvas._tkcanvas.grid(row = 1, column = 1)
        toolbar.grid(row = 0, column = 1, padx = 10, pady = 10, sticky='s')

        self.s_labels = []
        self.p_labels = []
        self.r_labels = []
        self.c_labels = []
        self.copy_buttons = []

        saved_row = 1
        saved_col = 2

        # Saved params
        for row in range(21):
            for col in range(5):
                if(col == 0):
                    label = tk.Label(self, text=("Step" if row == 0 
                                                 else str(row)), width= 13, 
                                                 height = 2 if row == 0 else 1)
                    if(row == 0):
                        label['fg'] = "#ffffff"
                        label['bg'] = "#31353b"
                    else:
                        self.s_labels.append(label)
                    label.grid(row=row+saved_row, column=saved_col+col)
                elif(col == 1):
                    label = tk.Label(self, text="Sample Pressure\n(psi)" 
                                     if row == 0 else "--", width = 18)
                    if(row == 0):
                        label['fg'] = "#ffffff"
                        label['bg'] = "#31353b"
                    else:
                        textvar = tk.StringVar()
                        textvar.set('--')
                        label = tk.Entry(self, bd = 0, textvariable = textvar,
                                         state = 'readonly', justify = 'center',
                                         width = 10)
                        self.p_labels.append((label, textvar))
                    label.grid(row=row+saved_row, column=saved_col+col)
                # TPR
                elif(col == 2):
                    label = tk.Label(self, text="TPR" 
                                     if row == 0 else "--", width = 24, 
                                     height = 2)
                    if(row == 0):
                        label['fg'] = "#ffffff"
                        label['bg'] = "#31353b"
                    else:
                        textvar = tk.StringVar()
                        textvar.set('--')
                        label = tk.Entry(self, bd = 0, textvariable = textvar,
                                         state = 'readonly', justify = 'center',
                                         width = 10)
                        self.r_labels.append((label, textvar))
                    label.grid(row=row+saved_row, column=saved_col+col)
                # CR
                elif(col == 3):
                    label = tk.Label(self, text="CR" 
                                     if row == 0 else "--", width = 24, 
                                     height = 2)
                    if(row == 0):
                        label['fg'] = "#ffffff"
                        label['bg'] = "#31353b"
                    else:
                        textvar = tk.StringVar()
                        textvar.set('--')
                        label = tk.Entry(self, bd = 0, textvariable = textvar,
                                         state = 'readonly', justify = 'center',
                                         width = 10)
                        self.c_labels.append((label, textvar))
                    label.grid(row=row+saved_row, column=saved_col+col)
                elif(col == 4 and row != 0):
                    copybutton = tk.Button(self, text = 'Copy row', 
                                           command = self.make_copier(row))
                    self.copy_buttons.append(copybutton)
                    copybutton.grid(row=row+saved_row, column = saved_col+col)

    def make_copier(self, row):
        return lambda: self.copy_row(row)

    def copy_row(self, row):
        if(self.app.running):
            print('running')
            return
        if(row-1 > len(self.app.sp)):
            self.label['text'] = 'No data'
            self.label['bg'] = red
            return
        self.app.clipboard_clear()
        self.app.clipboard_append((str(self.app.sp[row-1]),
                                  str(self.app.tpr[row-1]),
                                  str(self.app.cr[row-1])))
        self.label['text'] = ('Copied row ' + str(row)) 
        self.label['bg'] = green
        
    def graph(self, graph_x, graph_y1, graph_y2, graph_y3):
        self.fig = Figure(figsize=(5,5), dpi=100)
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.set_xlabel("Time (s)")
        self.ax1.set_ylabel("Resistance (ohm)")
        self.ax2 = self.ax1.twinx()
        self.ax2.set_ylabel('psi')
        self.ax2.set(ylim=(0, max(500, max(graph_y1))))
        self.ax2.plot(graph_x,graph_y1, label = 'Sample Pressure', color = 'tab:green')
        self.ax1.plot(graph_x,graph_y2, label = 'TPR', color = 'tab:red')
        self.ax1.plot(graph_x,graph_y3, label = 'CR', color = 'tab:blue')
        self.fig.legend(fontsize = 'small')
        self.fig.tight_layout()

        self.graph_widget.grid_remove()

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.graph_widget = self.canvas.get_tk_widget()
        self.graph_widget.grid(row = 1, column = 1, rowspan=21)

    def save_to_file(self, fileName):
        numsteps = len(self.app.voltages)
        # if os.path.exists(fileName + '.csv'):        
        steps = ['#'] + [str(x+1) for x in range(numsteps)]
        compressed = ['Sample Pressure (psi)'] + [x[1].get() for x in self.p_labels[:numsteps]]
        tpr = ['TPR'] + [x[1].get() for x in self.r_labels[:numsteps]]
        cr = ['CR'] + [x[1].get() for x in self.c_labels[:numsteps]]
        gdltpr = ['GDL TPR'] + [str(x) for x in self.app.gdl_tpr]
        data = np.transpose(np.array([['Notes'] + steps, 
                                      [self.notes.get('1.0', 'end-1c')]
                                       + compressed, 
                                      [''] + tpr, [''] + cr,
                                      [''] + gdltpr]
                                      ))
        np.savetxt('runs/' + fileName + '.csv', data, fmt='%s', 
                                                delimiter = ',')
        self.label['text'] = 'Saved'
        self.label['bg'] = green

    def save_to_folder(self, fileName):
        if(fileName == ''):
            today = date.today()
            fileName = today.strftime("%Y")[2:] + today.strftime("%m") + \
                today.strftime("%d")
        steps = ['#'] + [str(x+1) for x in range(len(self.app.voltages))]
        compressed = ['Sample Pressure (psi)'] + [x[1].get() for x in self.p_labels[:len(self.app.voltages)]]
        tpr = ['TPR'] + [x[1].get() for x in self.r_labels[:len(self.app.voltages)]]
        cr = ['CR'] + [x[1].get() for x in self.c_labels[:len(self.app.voltages)]]
        gdltpr = ['GDL TPR'] + [str(x) for x in self.app.gdl_tpr]
        
        data = np.transpose(np.array([['Notes'] + steps, 
                                      [self.notes.get('1.0', 'end-1c')]
                                       + compressed, 
                                      [''] + tpr, [''] + cr,
                                      [''] + gdltpr]
                                      ))
        
        folder =  filedialog.askdirectory(initialdir = "/",title = 
                                          "Select folder")
        filepath = folder + '/' + fileName + '.csv'

        if os.path.isfile(filepath):
            filename, extension = os.path.splitext(filepath)
            counter = 1
            while os.path.isfile(filepath):
                filepath = filename + " (" + str(counter) + ")" + extension
                counter += 1
        
        np.savetxt(filepath, data, fmt='%s', delimiter = ',')
        self.label['text'] = ('Saved')
        self.label['bg'] = green

    def print_voltages(self):
        print(self.app.voltages)
        # print(self.app.times)
        # print(self.app.samplePressure)
        # print(self.app.gdl_tpr)