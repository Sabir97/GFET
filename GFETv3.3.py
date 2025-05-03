# Author: Sabir Mohammedi Taieb

from fractions import Fraction
import sys
import customtkinter as tk
tk.set_appearance_mode("light")
# tk.set_default_color_theme("dark-blue")

from tkinter import filedialog # for browsing files

# from PIL import ImageTk, Image
# from tkinter import PhotoImage
# from tkinter import ttk

import numpy as np
# from tkinter import font as tkfont
from pyDecision.algorithm import ahp_method

from p_ii import promethee_ii # local file

from maut_v3 import maut_method # local file
# from pyDecision.algorithm import maut_method

from pyDecision.algorithm import saw_method
from pyDecision.algorithm import topsis_method
import matplotlib as plt
plt.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #, NavigationToolbar2Tk
from matplotlib.figure import Figure

import matplotlib.pyplot as pyplt
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D

import ctypes

import pandas as pd     # to import excel files

# To do: setup the input files


# Sharpness
ctypes.windll.shcore.SetProcessDpiAwareness(1)

np.set_printoptions(suppress=True)

weight_derivation = 'geometric'

election_criteria = ['Experience','Treated Breaks','Distance','Coordination','Response Time','Open Ports','Vulnerabilities','Severity Sum','Connection Type','Net Latency','Download','Upload']

# Dataset
dataset1 = np.array([
        [15,	21,	2500,	2,	15,	12,	13,	5.3,	0.6,	150,	20,	5],     #e1
        [13,	27,	750,	2,	5,	10,	11,	17.4,	1,	65,	1500,	750],   #e2
        [18,	32,	4000,	0,	10,	15,	18,	6.1,	0.3,	222,	50,	25],    #e3
        [10,	30,	1800,	1,	10,	9,	10,	12.9,	0.8,	95,	100,	50]     #e4
])

norm_dataset1=np.array([[0.83333333, 0.65625, 0.3,  1, 0.33333333, 0.75, 0.76923077, 1, 0.6, 0.43333333, 0.01333333, 0.00666667],
 [0.72222222, 0.84375,    1,         1,         1,         0.9, 0.90909091, 0.3045977,  1,         1,         1,         1],
 [1,         1,         0.1875,     0,         0.5,        0.6, 0.55555556, 0.86885246, 0.3,        0.29279279, 0.03333333, 0.03333333],
 [0.55555556, 0.9375,     0.41666667, 0.5,        0.5,        1, 1,         0.41085271, 0.8,        0.68421053, 0.06666667, 0.06666667]])

criterion_type = ['max', 'max', 'min', 'max', 'min', 'min', 'min', 'min', 'max', 'min', 'max','max']
weights_aip_wgmm=[0.073, 0.154,	0.086,	0.235,	0.068,	0.034,	0.055,	0.167,	0.022,	0.035,	0.024,	0.047]

default_weight_vectors = np.array([
    [0.075,	0.155,	0.086,	0.231,	0.067,	0.034,	0.054,	0.17,	0.022,	0.035,	0.023,	0.048],
    [0.076,	0.149,	0.086,	0.245,	0.067,	0.033,	0.054,	0.163,	0.022,	0.034,	0.023,	0.047],
    [0.074,	0.155,	0.085,	0.232,	0.067,	0.033,	0.055,	0.169,	0.022,	0.037,	0.023,	0.048],
    [0.069,	0.156,	0.086,	0.234,	0.07,	0.035,	0.056,	0.168,	0.022,	0.035,	0.026,	0.045]
])

weights = []
rc = 0

maut_f = [None] * 12
maut_param_list = [None] * 12

dms_number = 0
dms_number_entered = False
weights_fixed = False
input_ahp = np.zeros([12,12])
input_ahp_status = False
input_pm = np.zeros([dms_number,12])
input_pm_status = False

input_aip_wgmm_status = False
input_aip_wgmm_weights = []

# Input files status
ahp_file_input_status = False
pm_file_input_status = False

global chosen_method
chosen_method = ""




def aip_wgmm(weight_vectors):
    # wp = np.zeros(12)
    global_weights = np.zeros(12)
    weight_vectors = weight_vectors**0.25
    global_weights = np.product(weight_vectors, axis=0)
    return global_weights

# class CButton(tk.Button):
#     def __init__(self, master=None, **kwargs):
#         super().__init__(master, **kwargs)
#         self.config(
#             relief=tk.FLAT,  # Remove button relief
#             bd=0,  # Remove border
#             highlightthickness=0,  # Remove highlight
#             padx=10,  # Add horizontal padding
#             pady=5,  # Add vertical padding
#             font=("Arial", 12),  # Set font
#             foreground="white",  # Text color
#             background="grey",  # Background color
#         )
#         # Bind events
#         self.bind("<Enter>", self.on_hover)
#         self.bind("<Leave>", self.on_leave)

#     def on_hover(self, event):
#         if(self.configure(state="normal")=="normal"):
#             self.config(background="lightblue")  # Change color on hover

#     def on_leave(self, event):
#         if(self.configure(state="normal")=="normal"):
#             self.config(background="grey")  # Restore original color

class SampleApp(tk.CTk):

    def __init__(self, *args, **kwargs):
        tk.CTk.__init__(self, *args, **kwargs)

        self.title_font = tk.CTkFont(family='Arial', size=18, weight="bold")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.CTkFrame(self)

        # Scaling of the window
        container.tk.call('tk','scaling', 1.5)

        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (ModePage, StartPage, PM, AHP, SelectMCDA, Results, AHP_AIP_WGMM_Weights, MAUT_Parameters, Pii_Functions):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("ModePage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

class SimpleTableInput(tk.CTkFrame):
    def __init__(self, parent, rows, columns):
        tk.CTkFrame.__init__(self, parent)

        self._entry = {}
        self.rows = rows
        self.columns = columns

        # register a command to use for validation
        vcmd = (self.register(self._validate), "%P")
        
        i = 1
        j = 0

        for c in range(self.columns):
            cr = tk.CTkLabel(self, text=election_criteria[j])
            cr.grid(row=0,column=c+1)
            j += 1

        # cr = tk.Label(self, text=election_criteria[self.columns])
        # cr.grid

        # create the table of widgets
        for row in range(self.rows):
            expLbl = "DM " + str(i)
            i += 1
            dm_lbl = tk.CTkLabel(self, text=expLbl, width=4)
            dm_lbl.grid(row=i-1,column=0, padx=(5,0))

            for column in range(self.columns-1):
                index = (row, column)
                e = tk.CTkEntry(self, validate="key", validatecommand=vcmd, width=5)
                e.grid(row=row+1, column=column+1, stick="nsew")
                self._entry[index] = e

            fi = (row, self.columns-1)
            ef = tk.CTkEntry(self, validate="key", validatecommand=vcmd, width=5)
            ef.grid(row=row+1, column=self.columns, stick="nsew", padx=(0,10))
            self._entry[fi] = ef


        # adjust column weights so they all expand equally
        for column in range(self.columns+1):
            self.grid_columnconfigure(column, weight=1)
        # designate a final, empty row to fill up any extra space
        # self.grid_rowconfigure(rows, weight=1)

    def get(self):
        '''Return a list of lists, containing the data in the table'''
        matrix = np.zeros(shape=(self.rows,self.columns)) 
        # matrix = []
        for row in range(self.rows):
            current_row = []
            for column in range(self.columns):
                index = (row, column)
                if(self._entry[index].get()==''):
                    current_row = np.append(current_row, 0)
                else:
                    current_row = np.append(current_row, self._entry[index].get())
            matrix[row] = current_row
        return matrix
    
    def _validate(self, P):
        '''Perform input validation. 

        Allow only an empty value, or a value that can be converted to a float
        '''
        if P.strip() == "":
            return True

        try:
            f = float(P)
        except ValueError:
            self.bell()
            return False
        return True
    
class WeightVectorsTable(tk.CTkFrame):
    def __init__(self, parent, rows, columns):
        tk.CTkFrame.__init__(self, parent)

        self._entry = {}
        self._labels = {}
        self.rows = rows
        self.columns = columns
        
        i = 1
        j = 0

        for c in range(self.columns):
            cr = tk.CTkLabel(self, text=election_criteria[j])
            cr.grid(row=0,column=c+1, padx=5)
            j += 1
        
        icr_lbl = tk.CTkLabel(self, text="Consistency Ratio")
        icr_lbl.grid(row=0, column=self.columns+1, padx=5)

        # create the table of widgets
        for row in range(self.rows):
            expLbl = "Exp " + str(i)
            i += 1
            dm = tk.CTkLabel(self, text=expLbl)
            dm.grid(row=i-1,column=0, pady=2)                

            for column in range(self.columns+1):
                index = (row, column)
                e = tk.CTkLabel(self, text="") #, bg="white")
                e.grid(row=row+1, column=column+1, stick="nsew", padx=5, pady=2)
                self._entry[index] = e

        gw_lbl = tk.CTkLabel(self, text="Global Weights")
        gw_lbl.grid(row=self.rows+1, column=0)

        #Global Weight Labels
        for c in range(self.columns):
            wl_index = (self.rows+1, c)
            wl = tk.CTkLabel(self, text="") #,bg="white")
            wl.grid(row=self.rows+1, column=c+1, padx=5,pady=2, stick="nsew")
            self._labels[wl_index] = wl

        # adjust column weights so they all expand equally
        for column in range(self.columns+1):
            self.grid_columnconfigure(column, weight=1)
        # designate a final, empty row to fill up any extra space
        self.grid_rowconfigure(rows, weight=1)

    def get(self):
        '''Return a list of lists, containing the data in the table'''
        matrix = np.zeros(shape=(self.rows,self.columns)) 
        # matrix = []
        for row in range(self.rows):
            current_row = []
            for column in range(self.columns):
                index = (row, column)
                if(self._entry[index].get()==''):
                    current_row = np.append(current_row, 0)
                else:
                    current_row = np.append(current_row, self._entry[index].get())
            matrix[row] = current_row
        return matrix

class AHP_table(tk.CTkFrame):
    def __init__(self, parent, rows, columns):
        tk.CTkFrame.__init__(self, parent)

        self._entry = {}
        self._cr_rows = {}
        self._cr_columns = {}
        self.w_labels = {}
        self.rows = rows
        self.columns = columns
        global weights_aip_wgmm

        # register a command to use for validation
        vcmd = (self.register(self._validate), "%P")
        
        j = 0

        for c in range(self.columns):
            cr = tk.CTkEntry(self)
            cr.insert(0, election_criteria[j])
            cr.grid(row=0,column=c+1)
            cr.configure(state="disabled")
            self._cr_columns[c] = cr
            j += 1

        # create the table of widgets
        j = 0
        for row in range(self.rows):
            cr_row = tk.CTkEntry(self)
            cr_row.insert(0, election_criteria[j])
            cr_row.grid(row=j+1,column=0, padx=5)
            cr_row.configure(state="disabled")
            self._cr_rows[row] = cr_row
            j += 1
            for column in range(self.columns):
                index = (row, column)
                e = tk.CTkEntry(self, validate="key", validatecommand=vcmd)
                e.grid(row=row+1, column=column+1, stick="nsew")
                self._entry[index] = e
                
        l_weights = tk.CTkLabel(self, text="Weights")
        l_weights.grid(row=13,column=0)

        # default weights
        for column in range(self.columns):
            l = tk.CTkLabel(self, text="")
            l.grid(row=13, column=column+1, stick="nsew")
            self.w_labels[column] = l

        # adjust column weights so they all expand equally
        for column in range(self.columns+1):
            self.grid_columnconfigure(column, weight=1)
        # designate a final, empty row to fill up any extra space
        self.grid_rowconfigure(rows, weight=1)

    def calc_weights(self, weights):
        for column in range(self.columns):
            t = self.w_labels[column]
            t.configure(text= round(weights[column],3))
            self.w_labels[column] = t


    def get(self):
        '''Return a list of lists, containing the data in the table'''
        matrix = np.zeros(shape=(self.rows,self.columns)) 
        # matrix = []
        for row in range(self.rows):
            current_row = []
            for column in range(self.columns):
                index = (row, column)
                if(self._entry[index].get()==''):
                    current_row = np.append(current_row, 0)
                else:
                    current_row = np.append(current_row, eval(self._entry[index].get()))
            matrix[row] = current_row
        return matrix

    def _validate(self, P):
        '''Perform input validation. 

        Allow only an empty value, or a value that can be converted to a float
        '''
        if P.strip() == "":
            return True

        try:
            if '/' in str(P):
                return True
            
            if (isinstance(eval(P), (int, float))):
                return True

        except: 
            self.bell()
            return False
        # try:
        #     f = str(P)
        # except ValueError:
            # 
        #     return False
        return
    
class ModePage(tk.CTkFrame):

    def __init__(self, parent, controller):
        tk.CTkFrame.__init__(self, parent)
        self.controller = controller
        self.parent = parent

        mode_lbl = tk.CTkLabel(self, text="Choose a mode: ", font=self.controller.title_font)
        mode_lbl.pack(pady= 5, padx=5)

        simplified_mode_explanation = tk.CTkLabel(self, text="\"Simplified Mode\": You have to enter the performance matrix and the individual pair-wise comparison matrices of the election criteria to fix their weights.", justify="center", wraplength=327)
        simplified_mode_explanation.pack(pady=5, padx=5)

        advanced_mode_explanation = tk.CTkLabel(self, text=" \"Advanced mode\": In addition to what Simplified Mode offers, Advanced Mode allows you to choose the multi-criteria method to use and gives you the option to change the preference functions and their parameters.", justify="center", wraplength=327)
        advanced_mode_explanation.pack(pady=5, padx=5)

        advanced_btn = tk.CTkButton(self, text="Advanced Mode", command= self.advanced_mode)
        advanced_btn.pack(side="bottom", pady= 5, padx=5)

        simplified_btn = tk.CTkButton(self, text="Simplified Mode", command=self.simplified_mode)
        simplified_btn.pack(side="bottom", pady=5, padx=5)

    def simplified_mode(self):
        global mode
        mode = "simplified"

        self.controller.show_frame("StartPage")

    def advanced_mode(self):
        global mode
        mode= "advanced"

        self.controller.show_frame("StartPage")


class StartPage(tk.CTkFrame):

    def __init__(self, parent, controller):
        tk.CTkFrame.__init__(self, parent)
        self.controller = controller
        self.parent = parent

        # app.geometry("1041x379")

        label = tk.CTkLabel(self, text="GDSS Facilitator Election Tool", font=controller.title_font) #font=controller.title_font
        label.pack(side="top", fill="x", pady=10)

        case_study_lbl = tk.CTkLabel(self, text="Collaborative E-maintenance Case Study", font=('Arial',12))
        case_study_lbl.pack(side="top", pady=10)

        self.pm_btn = tk.CTkButton(self, text="Go to PM",
                            command=self.goto_pm) #, bd=0 ,relief="flat", foreground="white", background="grey",font=("Arial", 12))
        
        # self.ahp_btn = tk.CTkButton(self, text="Go to AHP",
                            # command=lambda: controller.show_frame("AHP"))#, bd=0 ,relief="flat", foreground="white", background="grey",font=("Arial", 12))
        
        # register a command to use for validation
        vcmd = (self.register(self._validate), "%P")

        # Number of DMs 
        nbr_dms_lbl = tk.CTkLabel(self, text="Enter the number of DMs : ")
        self.nbr_dms_entry = tk.CTkEntry(self, validate="key", validatecommand=vcmd)

        nbr_dms_lbl.pack()
        self.nbr_dms_entry.pack()
        
        self.select_mcda_btn = tk.CTkButton(self, text="Apply an MCDA Method", command=self.goto_MCDA) #, bd=0 ,relief="flat", foreground="white", background="grey",font=("Arial", 12))
        nbr_dms_btn = tk.CTkButton(self, text="Enter", command=self.enableBtn) #=0 ,relief="flat", foreground="white", background="grey",font=("Arial", 12))
        nbr_dms_btn.pack(pady=5)

        self.aip_wgmm_btn = tk.CTkButton(self, text="AHP AIP WGMM", command= self.goto_ahp_aip) #=0 ,relief="flat", foreground="white", background="grey", pady=5,font=("Arial", 12))

        self.test_lbl = tk.CTkLabel(self, text="No DMs")
        self.test_lbl.pack()

        # author_lbl = tk.Label(self, text="Author: Sabir Mohammedi Taieb")
        # author_lbl.pack(side="bottom", pady=5, padx=5)

        self.pm_btn.pack(side="bottom", pady=5)

        # self.ahp_btn.pack(side="bottom", pady=5)
        
        self.aip_wgmm_btn.pack(side="bottom", pady=5)

        self.select_mcda_btn.pack(side="bottom", pady=5)
        self.select_mcda_btn.configure(state="disabled")

        self.pm_btn.configure(state='disabled')

        # self.ahp_btn.configure(state="disabled") 
        
        # self.aip_wgmm_btn.configure(state="disabled")="disabled"

        self.aip_wgmm_btn.configure(state="disabled")

    #     global enter_dms_bind
    #     enter_dms_bind = self.controller.bind('<Return>', self.dms_nbr_key_press)

    #     # if(dms_number_entered == True):
    #     #     controller.unbind('<Return>',enter_dms_bind)

    # def dms_nbr_key_press(self, event):
    #     self.enableBtn()

    def goto_ahp_aip(self):
        # app.geometry("1182x476")
        app.geometry("1280x500")
        self.controller.show_frame("AHP_AIP_WGMM_Weights")

    def goto_pm(self):
        app.geometry("1280x500")
        self.controller.show_frame("PM")

    def goto_MCDA(self):
        app.geometry("300x340")
        global mode
        if(mode == "simplified"):
            self.controller.frames["Pii_Functions"].simplified_results()
        elif(mode=="advanced"):
            self.controller.show_frame("SelectMCDA")

    def enableBtn(self):
        if(self.nbr_dms_entry.get()!="" and int(self.nbr_dms_entry.get())>1):
            self.pm_btn.configure(state='normal')
            # self.ahp_btn.configure(state="normal") 
            self.aip_wgmm_btn.configure(state="normal") 
            self.select_mcda_btn.configure(state="disabled") 
            global dms_number
            global dms_number_entered
            dms_number = int(self.nbr_dms_entry.get())
            dms_number_entered = True
            self.test_lbl.configure(text= str(dms_number) + " Decision makers")
            self.controller.frames['PM'].rebuild()
            self.controller.frames['AHP_AIP_WGMM_Weights'].rebuild()
            # self.controller.unbind('<Return>',self.enter_dms_bind)
        else:
            self.pm_btn.configure(state="disabled")
            self.aip_wgmm_btn.configure(state="disabled")
            self.test_lbl.configure(text="No DMs")
            # self.ahp_btn.configure(state="disabled") 

    def _validate(self, P):
        '''Perform input validation. 

        Allow only an empty value, or a value that can be converted to a float
        '''
        if P.strip() == "":
            return True

        try:
            f = int(P)
        except ValueError:
            self.bell()
            return False
        return True

class PM(tk.CTkFrame):
    def __init__(self, parent, controller):
        tk.CTkFrame.__init__(self, parent)
        self.controller = controller

    def on_submit(self):
        print("\n")
        print(self.table.get())
        global input_pm
        global input_pm_status
        global input_aip_wgmm_status
        input_pm = self.table.get()
        input_pm_status = True

        self.status_lbl.configure(text= "Performance matrix entered !")

        if(input_pm_status == True and input_aip_wgmm_status == True):
            self.controller.frames['StartPage'].select_mcda_btn.configure(state="normal") 
            self.goto_mcda_btn.configure(state="normal") 
            self.controller.frames['AHP_AIP_WGMM_Weights'].goto_mcda.configure(state="normal")
            
            # self.controller.unbind('<Return>',enter_dms_bind)

    def rebuild(self):
        for widget in self.winfo_children():
            widget.destroy()

        global dms_number
        global input_pm
        input_pm = np.zeros(shape=(dms_number, 12))
        self.table = SimpleTableInput(self, dms_number, 12)
        
        self.reset_btn = tk.CTkButton(self, text="Reset", command=self.rebuild)
        self.reset_btn.pack(side="bottom")

        self.submit = tk.CTkButton(self, text="Submit", command=self.on_submit)

        self.pm = tk.CTkLabel(self, text="Performance Matrix", font=self.controller.title_font)
        self.pm.pack(side="top", pady=5)
        self.table.pack(side="top", fill="both", expand=True, pady=10)
        
        self.submit.pack(side="bottom")
        
        goto_ahp_btn = tk.CTkButton(self, text="Go to AHP AIP WGMM",
                            command=lambda: self.controller.show_frame("AHP_AIP_WGMM_Weights"))
        goto_ahp_btn.pack(side="bottom")

        startpage_btn = tk.CTkButton(self, text="Go to Start Frame", command=lambda: self.controller.show_frame("StartPage"))
        startpage_btn.pack(side="bottom")

        self.goto_mcda_btn = tk.CTkButton(self, text="Apply an MCDA Method", command=self.simplified_results)
        self.goto_mcda_btn.pack(side="bottom")

        self.status_lbl = tk.CTkLabel(self, text="Enter the evaluation of each DM based on the election criteria")
        self.status_lbl.pack(side="bottom", pady=5)

        if(input_ahp_status == False or input_pm_status == False):
            self.goto_mcda_btn.configure(state="disabled") 

        browse_btn = tk.CTkButton(self, text="Import PM File", command= self.get_file)
        browse_btn.pack(side="bottom")

    #     global enter_dms_bind
    #     enter_dms_bind = self.controller.bind('<Return>', self.submit_key_press)

    # def submit_key_press(self, event):
    #     self.on_submit()

    def simplified_results(self):
        global mode
        app.geometry("300x340")
        if(mode == "simplified"):
            self.controller.frames["MAUT_Parameters"].simplified_results()
        elif(mode =="advanced"):
            self.controller.show_frame("SelectMCDA")

    def get_file(self):
        file = filedialog.askopenfile(parent=self, mode='rb',title='Choose the Excel file containing the performance matrix', filetypes=[("Excel files", ".xlsx .xls")])

        global pm_file_input_status
        # global input_pm_status

        pm_ifile = pd.read_excel(file, sheet_name='Sheet1', header=None)
        pm_ifile_matrix = pm_ifile.to_numpy()      # Convert pandas df to numpy array

        if file:
            print(pm_ifile_matrix)
            for i in range(input_pm.shape[0]):
                for j in range(input_pm.shape[1]):
                    index = (i,j)
                    self.table._entry[index].delete(0, tk.END)
                    self.table._entry[index].insert(0, pm_ifile_matrix[i][j])
                    
            pm_file_input_status = True
            # input_pm_status = True

            # data = file.read()
            # file.close()
            # print("I got %d bytes from this file." % len(data))

        # Grey the submit button until all inputs are filled
        # for i in range(self.table.rows):
        #     for j in range(self.table.columns):
        #         index = (i,j)
        #         if(self.table._entry[index].get()==""):
        #             self.submit.configure(state="disabled")="disabled"
        #             break
        #         else:
        #             self.submit.configure(state="normal")="normal"


class AHP_AIP_WGMM_Weights(tk.CTkFrame):
    def __init__(self,parent, controller):
        tk.CTkFrame.__init__(self,parent)
        self.controller = controller

    def rebuild(self):
        for w in self.winfo_children():
            w.destroy()

        self.columns = 12
        global dms_number

        global input_aip_wgmm_status
        input_aip_wgmm_status = False

        global input_aip_wgmm_weights
        input_aip_wgmm_weights = []

        ahp_label = tk.CTkLabel(self, text="AHP AIP WGMM for Fixing Election Criteria Weights", font=self.controller.title_font)
        ahp_label.pack(side="top", pady=10)

        self.global_table = WeightVectorsTable(self, dms_number, self.columns)
        self.global_table.pack()
        
        # scale_frame = tk.CTkFrame(self)
        # scale_frame.pack(side="right",padx=5)

        # self.scale_title = tk.Label(scale_frame, text="Saaty's Scale of Relative Importance:", font=('Arial',10))
        # self.scale_title.grid(row=0, columnspan=2)

        # self.scale_intensity = tk.Label(scale_frame, text="Intensity\n 1\n 3\n 5\n 7\n 9\n 2, 4, 6, 8")
        # self.scale_def = tk.Label(scale_frame, text="Definition\n Equal Importance\n Moderate Importance\n Strong Importance \n Very Strong Importance \n Extreme Importance\n Intermidiate Values")
        # self.scale_intensity.grid(row=1, column=0)
        # self.scale_def.grid(row=1, column=1)

        self.d = 1
        self.next_btn = tk.CTkButton(self, text="Enter Pair-wise Comparison Matrix of DM "+str(self.d), command= self.next_frame)
        self.next_btn.pack(side="bottom")
        back_btn = tk.CTkButton(self, text="Go Back", command=lambda: self.controller.show_frame("StartPage"))
        back_btn.pack(side="bottom")
        
        self.compute_btn = tk.CTkButton(self, text="Compute Global Weights", command=lambda: self.compute_aip_wgmm(self.vectors)) #default_weight_vectors

        self.compute_btn.pack(side="bottom")
        self.compute_btn.configure(state="disabled") 

        self.reset_btn = tk.CTkButton(self, text="Reset", command=self.rebuild)
        self.reset_btn.pack(side="bottom")
        self.reset_btn.configure(state="disabled") 

        self.goto_mcda = tk.CTkButton(self, text="Apply an MCDA Method", command=self.simplified_results)
        self.goto_mcda.pack(side="bottom")
        self.goto_mcda.configure(state="disabled")

        self.goto_pm = tk.CTkButton(self, text="Performance Matrix", command=lambda: self.controller.show_frame("PM"))
        self.goto_pm.pack(side="bottom")
        
        self.vectors = np.zeros(shape=(dms_number, 12))

        self.browse_btn = tk.CTkButton(self, text="Import pair-wise comparison matrices file", command=lambda: self.get_file("all"))
        self.browse_btn.pack(side="bottom")

        self.input_lbl = tk.CTkLabel(self, text="")
        self.input_lbl.pack(side="bottom")
        
    # def bind_btn(self):
    #     global enter_dms_bind
    #     enter_dms_bind = self.controller.bind('<Return>', self.submit_comp_matrix)

    # def submit_comp_matrix(self, event):
    #     self.add_vector()

    def simplified_results(self):
        global mode
        app.geometry("300x340")
        if(mode == "simplified"):
            self.controller.frames["Pii_Functions"].simplified_results()
        elif(mode == "advanced"):
            self.controller.show_frame("SelectMCDA")

    def get_file(self, type):
        global ahp_file_input_status
        global dms_number
        global weight_derivation

        if(type=="all"):
            file = filedialog.askopenfile(parent=self, mode='rb',title='Choose the Excel file containing the criteria pair-wise comparison matrices', filetypes=[("Excel files", ".xlsx .xls")])

            if file:
                for i in range(dms_number):
                    ahp_vector_ifile = pd.read_excel(file, sheet_name='Sheet'+str(i+1),header=None)
                    ahp_vector_ifile_matrix = ahp_vector_ifile.to_numpy()      # Convert pandas df to numpy array
                    # print(ahp_vector_ifile_matrix)
                    iwv, icr = ahp_method(ahp_vector_ifile_matrix, wd=weight_derivation)
                    self.vectors[i] = iwv
                    print(icr)
                    if(icr<0.1):
                        self.global_table._entry[(i,12)].configure(text= str(round(icr,3)) + " Consistent")
                    elif(icr>=0.1):
                        self.global_table._entry[(i,12)].configure(text= str(round(icr,3)) + " Inconsistent")
                    else:
                        self.global_table._entry[(i,12)].configure(text= "Invalid")

                    for j in range(12):
                        index = (i,j)
                        self.global_table._entry[index].configure(text= str(round(self.vectors[i][j],3)))
                
                print(self.vectors)
                self.input_lbl["text"]="Individual weight vectors imported"
                ahp_file_input_status = True
                self.compute_btn.configure(state="normal")
                self.browse_btn.configure(state="disabled") 
                self.next_btn.configure(state="disabled") 
                self.reset_btn.configure(state="normal")

        elif(type=="individual"):
            file = filedialog.askopenfile(parent=self, mode='rb',title='Excel file containing the criteria pair-wise comparison matrix', filetypes=[("Excel files", ".xlsx .xls")])

            if file:
                ahp_vector_ifile = pd.read_excel(file, sheet_name='Sheet1', header=None)
                ahp_vector_ifile_matrix = ahp_vector_ifile.to_numpy()      # Convert pandas df to numpy array

                for i in range(ahp_vector_ifile_matrix.shape[0]):
                    for j in range(ahp_vector_ifile_matrix.shape[1]):
                        self.i_comp_table._entry[(i,j)].delete(0, tk.END)
                        if(ahp_vector_ifile_matrix[i][j]>1):
                            self.i_comp_table._entry[(i,j)].insert(0, int(ahp_vector_ifile_matrix[i][j]))
                        else:
                            self.i_comp_table._entry[(i,j)].insert(0, str(Fraction(ahp_vector_ifile_matrix[i][j]).limit_denominator()))
            

        return
        
    def rebuild_dm_win(self):
        for i in range(len(election_criteria)):
            self.i_comp_table.w_labels[i].configure(text="")
            for j in range(len(election_criteria)):
                self.i_comp_table._entry[(i,j)].delete(0, tk.END)

        return

    def next_frame(self):
        global weight_derivation
        if(self.d<=dms_number):
            self.dm_ahp_win = tk.CTkToplevel(app)
            self.dm_ahp_win.title("Individual Pair-wise Comparison for DM "+ str(self.d))
            self.dm_ahp_win.geometry("1481x574")
            
            self.i_comp_table = AHP_table(self.dm_ahp_win,self.columns,self.columns)
            self.i_comp_table.pack(padx=5)

            scale_frame = tk.CTkFrame(self.dm_ahp_win)
            scale_frame.pack(side="right",padx=5)

            self.scale_title = tk.CTkLabel(scale_frame, text="Saaty's Scale of Relative Importance:", font=('Arial',10))
            self.scale_title.grid(row=0, columnspan=2)

            self.scale_intensity = tk.CTkLabel(scale_frame, text="Intensity\n 1\n 3\n 5\n 7\n 9\n 2, 4, 6, 8")
            self.scale_def = tk.CTkLabel(scale_frame, text="Definition\n Equal Importance\n Moderate Importance\n Strong Importance \n Very Strong Importance \n Extreme Importance\n Intermidiate Values")
            self.scale_intensity.grid(row=1, column=0)
            self.scale_def.grid(row=1, column=1)

            self.cr = tk.CTkLabel(self.dm_ahp_win, text="Fill the Pair-wise Comparison Matrix")
            self.cr.pack(pady=5)

            self.i_import_btn = tk.CTkButton(self.dm_ahp_win, text="Import DM " + str(self.d)+ " comparison matrix", command=lambda: self.get_file("individual"))
            self.i_import_btn.pack(pady=5)

            self.i_submit = tk.CTkButton(self.dm_ahp_win,text="Submit Matrix",command=self.add_vector)
            self.i_submit.pack()
            self.i_submit.configure(state="normal")

            self.i_reset_btn = tk.CTkButton(self.dm_ahp_win, text="Reset", command=self.rebuild_dm_win)
            self.i_reset_btn.pack(pady=5)

        return

    def add_vector(self):
        # iw, icr =ahp_method(self.i_comp_table.get(), wd=weight_derivation)
        # global input_aip_wgmm_status
        # for j in range(self.columns):
        #     self.i_comp_table.w_labels[j].configure(text=str(round(iw[j],3)))

        # if(icr>0.1):
        #     icr_txt = "Consistency Ratio is : " + str(round(rc,2)) + "The values entered are not consistent ! Change the values in the pairwise comparison matrix."

        # elif(self.d <= dms_number and icr<0.1):
        #     for j in range(self.columns):
        #         self.global_table._entry[(self.d-1,j)].configure(text= str(round(iw[j],3)))
            
        #     icr_txt = "Consistency Ratio is : " + str(round(rc,2)) + " The matrix is consistant."
        #     self.reset_btn.configure(state="normal")

        #     # self.vectors.append(iw)
        #     self.vectors[self.d-1] = iw

        #     if(self.d != dms_number):
        #         self.d = self.d + 1
        #         self.next_btn.configure(text="Enter Pair-wise Comparison Matrix of "+ str(self.d))
        #         self.i_submit.configure(state="disabled")
        #         self.i_submit["background"] = "grey"

        #     # elif(self.d == dms_number):
        #     #     self.d = self.d + 1
            
        # elif(self.d >= dms_number):
        #     self.next_btn.configure(state="disabled")
        #     self.next_btn.configure(text= "Pair-wise Comparison Matrices Filled")
        #     self.next_btn["background"]= "grey"
        #     # global default_weight_vectors
        #     self.compute_btn.configure(state="normal")
           
        # else:
        #     icr_txt = "Complete the missing values"

        # self.cr.configure(text= icr_txt)

        # print(icr)

        # return
        iw, icr =ahp_method(self.i_comp_table.get(), wd=weight_derivation)
        global input_aip_wgmm_status
        
        if(icr<0.1):
            for j in range(self.columns):
                self.global_table._entry[(self.d-1,j)].configure(text= str(round(iw[j],3))) #.delete(0, tk.END)

            self.global_table._entry[(self.d-1, self.columns)].configure(text= str(round(icr, 3)) + " Consistent")
        
        if(icr>0.1):
            icr_txt = "Consistency Ratio is: " + str(round(icr, 2)) + "The values entered are not consistent ! Change the values in the pairwise comparison matrix."
        elif(icr<0.1):
            # self.vectors.append(iw)
            self.vectors[self.d-1] = iw

            icr_txt = "Consistency Ratio is: " + str(round(icr, 3)) + " The matrix is consistant."
            self.reset_btn.configure(state="normal") 
        else:
            icr_txt = "Complete the missing values"

        self.cr.configure(text= icr_txt)

        print(icr)
        if(self.d <= dms_number and icr<0.1):
            self.d += 1
            self.next_btn.configure(text="Enter Pair-wise Comparison Matrix of "+str(self.d))
            self.i_submit.configure(state="disabled")
            self.i_submit["background"] = "grey"
            
            
        if(self.d > dms_number):
            self.next_btn.configure(state="disabled")
            self.next_btn.configure(text= "Pair-wise Comparison Matrices Filled")
            self.next_btn["background"]= "grey"
            # global default_weight_vectors
            self.compute_btn.configure(state="normal")
            self.i_submit.configure(state="disabled")

        return

    def compute_aip_wgmm(self, vectors):
        global input_aip_wgmm_status
        print("Individual Weight Vectors: ")
        print(str(self.vectors) + "\n")
        input_aip_wgmm_weights = aip_wgmm(vectors)
        input_aip_wgmm_status = True
       
        print("Global Weights: ")
        print(str(input_aip_wgmm_weights) + "\n")
        j=0
        for w in input_aip_wgmm_weights:
            self.global_table._labels[(dms_number+1,j)].configure(text=str(round(w,3)))
            j += 1

        self.compute_btn.configure(state="disabled") 
        self.compute_btn["background"] = "grey"
        self.next_btn.configure(state="disabled") 
        self.reset_btn.configure(state="normal") 
        self.browse_btn.configure(state="disabled") 
        self.input_lbl.configure(text="Global weights calculated")

        # self.controller.unbind('<Return>',enter_dms_bind)

        if(input_aip_wgmm_status == True and input_pm_status== True):
            self.goto_mcda.configure(state="normal") 
            self.controller.frames["PM"].goto_mcda_btn.configure(state="normal") 
            self.controller.frames["StartPage"].select_mcda_btn.configure(state="normal")

        return


class AHP(tk.CTkFrame):

    def __init__(self, parent, controller):
        tk.CTkFrame.__init__(self, parent)
        self.controller = controller
        label = tk.CTkLabel(self, text="AHP for Fixing Weights", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        self.table = AHP_table(self, 12, 12)
        self.table.pack(side="top", fill="both", expand=True)

        scale_frame = tk.CTkFrame(self)
        scale_frame.pack(side="right",padx=5)

        self.scale_title = tk.CTkLabel(scale_frame, text="Saaty's Scale of Relative Importance:", font=('Arial',10))
        self.scale_title.grid(row=0, columnspan=2)

        self.scale_intensity = tk.CTkLabel(scale_frame, text="Intensity\n 1\n 3\n 5\n 7\n 9\n 2, 4, 6, 8")
        self.scale_def = tk.CTkLabel(scale_frame, text="Definition\n Equal Importance\n Moderate Importance\n Strong Importance \n Very Strong Importance \n Extreme Importance\n Intermidiate Values")
        self.scale_intensity.grid(row=1, column=0)
        self.scale_def.grid(row=1, column=1)

        self.cr = tk.CTkLabel(self, text="Consistency Ratio is : ")
        # self.weights = AHP_AIP_WGMM_Weights(self)
        # self.weights.pack(side="top", fill="both",expand=True)
        button = tk.CTkButton(self, text="Go to the start frame",
                           command=lambda: controller.show_frame("StartPage"))
        calc_weights = tk.CTkButton(self, text="Calculate Weights", command=self.on_submit)
        button.pack(pady=5)
        calc_weights.pack(pady=5)
        self.cr = tk.CTkLabel(self, text="")
        self.cr.pack(side="left")

    def on_submit(self):
        print(self.table.get())
        global input_ahp
        global input_ahp_status
        input_ahp = self.table.get()
        global weights
        global rc
        global weight_derivation
        weights, rc = ahp_method(input_ahp, wd=weight_derivation)
        print("weight derivation : " + weight_derivation)
        print(weights)
        print(rc)
        self.table.calc_weights(weights)
        if(rc>0.1):
            cr_txt = "Consistency Ratio is : " + str(round(rc,2)) + "The values entered are not consistent ! Change the values in the pairwise comparison matrix."
        elif(rc<0.1):
            input_ahp_status = True
            cr_txt = "Consistency Ratio is : " + str(round(rc,2)) + " The matrix is consistant."
        else:
            cr_txt = "Complete the missing values"

        self.cr.configure(text= cr_txt)
        

class SelectMCDA(tk.CTkFrame):

    def __init__(self, parent, controller):
        tk.CTkFrame.__init__(self, parent)
        self.controller = controller
        global input_pm
        global weights_aip_wgmm
        global criterion_type
        label = tk.CTkLabel(self, text="Select an MCDA method: ", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.CTkButton(self, text="Go to the start page", command=lambda: controller.show_frame("StartPage"))
        button.pack(side="bottom",pady=5)
        maut_btn = tk.CTkButton(self, text="MAUT", command=self.maut)
        maut_btn.pack(pady=5)
        saw_btn = tk.CTkButton(self, text="SAW", command=self.saw)
        saw_btn.pack(pady=5)
        pii_btn = tk.CTkButton(self, text="PROMETHEE II", command= self.pii)
        pii_btn.pack(pady=5)
        topsis_btn = tk.CTkButton(self, text="TOPSIS", command=self.topsis)
        topsis_btn.pack(pady=5)

    def maut(self):
        app.geometry("710x572")
        self.controller.show_frame("MAUT_Parameters")
        # self.controller.frames["MCDA_Parameters"].maut_functions()
        # self.controller.frames["Results"].ranking(flow)
        return
    
    def saw(self):
        global chosen_method
        chosen_method = "SAW"
        self.controller.show_frame("Results")
        flow = saw_method(input_pm, criterion_type, weights_aip_wgmm, graph = False)
        # flow = flow[np.argsort(flow[:, 1])]
        # flow = flow[::-1]
        
        self.controller.frames["Results"].ranking(flow)
        return
    
    def pii(self):
        # global chosen_method
        # chosen_method = "PROMETHEE II"
        # self.controller.show_frame("Results")

        # self.controller.frames["Results"].ranking(flow)

        self.controller.show_frame("Pii_Functions")
        app.geometry("1076x562")

        return
    
    def topsis(self):
        global chosen_method
        chosen_method = "TOPSIS"
        self.controller.show_frame("Results")
        c_i = topsis_method(input_pm, weights_aip_wgmm, criterion_type, graph = False)
        flow = np.copy(c_i)
        flow = np.reshape(flow, (c_i.shape[0], 1))
        flow = np.insert(flow, 0, list(range(1, c_i.shape[0]+1)), axis = 1)
        # flow = flow[np.argsort(flow[:, 1])]
        # flow = flow[::-1]

        self.controller.frames["Results"].ranking(flow)
        return
    
class MAUT_Parameters(tk.CTkFrame):

    def __init__(self, parent, controller):
        tk.CTkFrame.__init__(self, parent)
        self.controller = controller
        
        # self.controller.geometry("710x572")

        # for w in self.winfo_children():
        #     w.destroy()

        global input_pm
        global weights_aip_wgmm
        global criterion_type
        global election_criteria
        

        label = tk.CTkLabel(self, text="Choose a utility function for each criterion", font=self.controller.title_font)
        label.grid(row=0, column=0, padx=5, pady=10)

        go_back_btn = tk.CTkButton(self, text="Go Back", command=lambda: self.controller.show_frame("SelectMCDA"))
        go_back_btn.grid(row=13,column=0, pady=5, padx= 5)
        
        global maut_f # list of chosen MAUT utility functions
        # global maut_param_list

        global default_maut_functions
        default_maut_functions = ["Logarithmic","Logarithmic","Exponential","Logarithmic","Exponential","Exponential","Logarithmic","Logarithmic","Step","Linear","Logarithmic","Exponential"]

        global default_maut_step
        default_maut_step = [None, None, None, None, None, None, None, None, 4, None, None, None]

        # maut_f = [None] * 12

        self.mf_list = []  # list of the Option Menus corresponding to the utility functions
        self.op_entries = [None] * 12  # list of entries for the number of options for the step function

        self.op_nbr = [None] * 12 # list of the number of options for the step function
        self.op_flag = [None] * 12 # flag to check if the entry of the number of options exist already or not

        global op_entry
        op_entry = tk.CTkEntry(self)
        op_entry.grid(row=9, column=2)
        op_entry.insert(0,"4")
        self.op_entries[8] = op_entry
        self.op_flag[8] = True
        self.op_entries[8] = op_entry


        # def function_change(event):
        #     for i in range(12):
        #         if(options_list[i].get()=="Step" and self.op_flag==False):
        #             global op_entry
        #             op_entry = tk.CTkEntry(self)
        #             op_entry.grid(row=i+1,column=2)
        #             self.op_flag = True

        #         elif(options_list[i].get()!="Step" and self.op_flag==True):
        #             op_entry.destroy()
        #             self.op_flag = False

        self.step_lbl = tk.CTkLabel(self, text="Number of Options")
        self.step_lbl.grid(row=0, column=2, padx=5, pady=5)

        def function_change(event, obj):
            # w = event.widget.master.get()
            w = obj.get()
            r = obj.grid_info()["row"]
            if(w=="Step"):
                global op_entry
                op_entry = tk.CTkEntry(self)
                op_entry.grid(row=r, column=2)
                self.op_entries[r-1] = op_entry
                self.op_flag[r-1] = True

            elif(w != "Step" and self.op_flag[r-1]==True):
                self.op_entries[r-1].destroy()
                self.op_flag[r-1] = False

        ji = 1
        for j in election_criteria:
            c_lbl = tk.CTkLabel(self, text=j)
            c_lbl.grid(row=ji, column=0, pady=5, padx=5)

            mf = tk.CTkOptionMenu(self, values=['Linear', 'Logarithmic', 'Quadratic', 'Exponential', 'Step'])
            mf.configure(command=lambda event, obj=mf : function_change(event, obj))
            mf.grid(row=ji, column=1)
            mf.set(default_maut_functions[ji-1])
            self.mf_list.append(mf)

            ji += 1

        utility_function_lbl = tk.CTkLabel(self, text="Utility Function")
        utility_function_lbl.grid(row=0, column=1, padx=5, pady=5)

        self.submit_btn = tk.CTkButton(self, text="Submit Parameters", command=self.submit_maut)
        self.submit_btn.grid(row=13, column=1, pady=5, padx= 5)


        self.view_results_btn = tk.CTkButton(self, text="View Results", command=self.show_results)
        self.view_results_btn.grid(row=13, column=2, padx=5, pady=5)
        
        self.view_results_btn.configure(state='disabled')

        self.submit_lbl = tk.CTkLabel(self, text="")
        self.submit_lbl.grid(row=14, column=1, pady= 5, padx=5)

        
        # self.controller.show_frame("Results")
        # utility_functions= ['log','log','exp','log','exp','exp','log','log','step','lin','log','exp']
        # flow = maut_method(dataset1, weights_aip_wgmm, criterion_type, utility_functions, graph=False)
        

    def submit_maut(self):
        
        for j in range(12):
            if(self.mf_list[j].get()=="Step"):
                maut_f[j] = "step"
                self.op_nbr[j] = int(self.op_entries[j].get())
            elif(self.mf_list[j].get()=="Quadratic"):
                maut_f[j] = "quad"
            else:
                maut_f[j] = self.mf_list[j].get().lower()[0:3]

            print(maut_f[j])

        print(self.op_nbr)
        self.submit_lbl.configure(text="Utility functions submitted.")

        self.view_results_btn.configure(state='normal')

        return
    
    def show_results(self):
        flow = maut_method(input_pm, weights_aip_wgmm, criterion_type, maut_f, self.op_nbr, graph=False)

        global chosen_method
        chosen_method = "MAUT"
        
        self.controller.frames["Results"].ranking(flow)
        self.controller.show_frame('Results')
        
        return
    
    def simplified_results(self):
        # global default_maut_functions, default_maut_step
        d_simple_maut_functions = [""]*12
        for j in range(12):
            if(default_maut_functions[j]=="Step"):
                d_simple_maut_functions[j] = "step"
                # self.op_nbr[j] = int(self.op_entries[j].get())
            elif(default_maut_functions[j]=="Quadratic"):
                d_simple_maut_functions[j] = "quad"
            else:
                d_simple_maut_functions[j] = default_maut_functions[j].lower()[0:3]

        flow = maut_method(input_pm, weights_aip_wgmm, criterion_type, d_simple_maut_functions, default_maut_step, graph=False)

        global chosen_method
        chosen_method = "MAUT"
        
        self.controller.frames["Results"].ranking(flow)
        self.controller.show_frame('Results')
    
    
class Pii_Functions(tk.CTkFrame):
    def __init__(self, parent, controller):
        tk.CTkFrame.__init__(self, parent)
        self.controller = controller

        global pii_f
        pii_f = [None] * 12 # list of Pii preference functions

        # list of parameters entered by the user
        global q,p,s, pf_dict

        q = [0] * 12
        p = [0] * 12
        s = [0] * 12

        pf_dict = {"Usual":"t1", "U-Shape":"t2", "V-Shape":"t3", "Level":"t4", "V-Shape with Indifference":"t5","Gaussian":"t6", "C-Form":"t7"}

        self.pfm_list = [] # list of Pii Option Menus widgets

        # Default Parameters 
        global default_Q, default_S, default_P
        default_Q = [ 0,  1,   15,  0,  2,  0,   0,  0, 0.1,  0,  0,  0] #Indifference
        default_S = [ 0,  0,    0,  0,  0,  5,   0,  9,   0,  0,  2,  1] # Gaussian t6 and t7
        default_P = [ 2,  5,  100,  1, 20,  0,  10,  0,   0,  0,  0,  0] # Preference

        default_W = [0.081, 0.153, 0.1,	0.215, 0.068, 0.036, 0.054, 0.168, 0.023, 0.034, 0.022, 0.045] # Weights

        global default_pii_functions 
        default_pii_functions= ['V-Shape', 'Level', 'V-Shape with Indifference', 'V-Shape','V-Shape with Indifference', 'Gaussian', 'V-Shape', 'Gaussian','U-Shape', 'Usual', 'Gaussian', 'Gaussian'] # 't1' = Usual; 't2' = U-Shape; 't3' = V-Shape; 't4' = Level; 't5' = V-Shape with Indifference; 't6' = Gaussian; 't7' = C-Form

        global qe_list, pe_list, se_list
        qe_list = [None] * 12
        pe_list = [None] * 12
        se_list = [None] * 12

        title_lbl = tk.CTkLabel(self, text="Choose a preference function for each criterion:", font=self.controller.title_font)
        title_lbl.grid(row=0, column=0, padx=5, pady=5)

        parameters_lbl= tk.CTkLabel(self, text="Preference Functions")
        parameters_lbl.grid(row=0, column=1, padx=5, pady=5)

        q_param_lbl = tk.CTkLabel(self, text="Indifference (Q)")
        q_param_lbl.grid(row=0, column=2)
        p_param_lbl = tk.CTkLabel(self, text="Preference (P)")
        p_param_lbl.grid(row=0, column=3)
        s_param_lbl = tk.CTkLabel(self, text="Gaussian (S)")
        s_param_lbl.grid(row=0, column=4)


        # pfm = tk.CTkOptionMenu(self, values=['Type 1', 'Type 2'])
        # pfm.grid(row=1, column=1, padx=5, pady=5)

        def function_change(event, obj):
            # w = event.widget.master.get()
            w = obj.get()
            r = obj.grid_info()["row"]
            if(w=="Usual"):
                qe_list[r-1].delete(0,tk.END)
                pe_list[r-1].delete(0,tk.END)
                se_list[r-1].delete(0,tk.END)

                qe_list[r-1].configure(state="disabled")
                pe_list[r-1].configure(state="disabled")
                se_list[r-1].configure(state="disabled")
                # self.qe[r-1].configure(state="normal")
                # self.op_flag[r-1] = True

            elif(w=="U-Shape"):
                qe_list[r-1].configure(state="normal")

                pe_list[r-1].delete(0,tk.END)
                se_list[r-1].delete(0,tk.END)

                pe_list[r-1].configure(state="disabled")
                se_list[r-1].configure(state="disabled")
                # self.op_flag[r-1] = True

            elif(w=="V-Shape"):
                qe_list[r-1].delete(0,tk.END)
                se_list[r-1].delete(0,tk.END)

                qe_list[r-1].configure(state="disabled")
                pe_list[r-1].configure(state="normal")
                se_list[r-1].configure(state="disabled")


            elif(w=="Level"):
                qe_list[r-1].configure(state="normal")
                pe_list[r-1].configure(state="normal")
                se_list[r-1].delete(0,tk.END)
                se_list[r-1].configure(state="disabled")
                # op_entry = tk.CTkEntry(self)
                # op_entry.grid(row=r, column=2)
                # self.op_entries[r-1] = op_entry
                # self.op_flag[r-1] = True

            elif(w=="V-Shape with Indifference"):
                qe_list[r-1].configure(state="normal")
                pe_list[r-1].configure(state="normal")
                se_list[r-1].delete(0,tk.END)
                se_list[r-1].configure(state="disabled")

            elif(w=="Gaussian"):
                qe_list[r-1].delete(0,tk.END)
                pe_list[r-1].delete(0,tk.END)
                qe_list[r-1].configure(state="disabled")
                pe_list[r-1].configure(state="disabled")

                se_list[r-1].configure(state="normal")

            elif(w=="C-Form"):
                qe_list[r-1].delete(0,tk.END)
                pe_list[r-1].delete(0,tk.END)
                qe_list[r-1].configure(state="disabled")
                pe_list[r-1].configure(state="disabled")

                se_list[r-1].configure(state="normal")

            # elif(w != "Usual" and self.op_flag[r-1]==True):
            #     self.op_entries[r-1].destroy()
            #     self.op_flag[r-1] = False


        ji = 1
        for j in election_criteria:
            c_lbl = tk.CTkLabel(self, text=j)
            c_lbl.grid(row=ji, column=0, pady=5, padx=5)

            pfm = tk.CTkOptionMenu(self, values=['Usual', 'U-Shape', 'V-Shape', 'Level', 'V-Shape with Indifference', 'Gaussian', 'C-Form'])
            pfm.configure(command=lambda event, obj=pfm : function_change(event, obj))
            pfm.grid(row=ji, column=1)
            pfm.set(default_pii_functions[ji-1])

            self.pfm_list.append(pfm)

            qe = tk.CTkEntry(self)
            pe = tk.CTkEntry(self)
            se = tk.CTkEntry(self)

            qe.grid(row=ji, column=2)
            pe.grid(row=ji, column=3)
            se.grid(row=ji, column=4)

            qe_list[ji-1] = qe
            pe_list[ji-1] = pe
            se_list[ji-1] = se

            if(pfm.get()=="Usual"):
                qe_list[ji-1].configure(state="disabled")
                pe_list[ji-1].configure(state="disabled")
                se_list[ji-1].configure(state="disabled")
                # self.qe[r-1].configure(state="normal")
                # self.op_flag[r-1] = True

            elif(pfm.get()=="U-Shape"):
                qe_list[ji-1].configure(state="normal")
                pe_list[ji-1].configure(state="disabled")
                se_list[ji-1].configure(state="disabled")

                qe_list[ji-1].insert(0, default_Q[ji-1])
                # self.op_flag[r-1] = True

            elif(pfm.get()=="V-Shape"):
                qe_list[ji-1].configure(state="disabled")
                pe_list[ji-1].configure(state="normal")
                se_list[ji-1].configure(state="disabled")

                pe_list[ji-1].insert(0, default_P[ji-1])

            elif(pfm.get()=="Level"):
                qe_list[ji-1].configure(state="normal")
                pe_list[ji-1].configure(state="normal")
                se_list[ji-1].configure(state="disabled")

                qe_list[ji-1].insert(0, default_Q[ji-1])
                pe_list[ji-1].insert(0, default_P[ji-1])

            elif(pfm.get()=="V-Shape with Indifference"):
                qe_list[ji-1].configure(state="normal")
                pe_list[ji-1].configure(state="normal")
                se_list[ji-1].configure(state="disabled")

                qe_list[ji-1].insert(0, default_Q[ji-1])
                pe_list[ji-1].insert(0, default_P[ji-1])

            elif(pfm.get()=="Gaussian"):
                qe_list[ji-1].configure(state="disabled")
                pe_list[ji-1].configure(state="disabled")
                se_list[ji-1].configure(state="normal")

                se_list[ji-1].insert(0, default_S[ji-1])

            elif(pfm.get()=="C-Form"):
                qe_list[ji-1].configure(state="disabled")
                pe_list[ji-1].configure(state="disabled")
                se_list[ji-1].configure(state="normal")

                se_list[ji-1].insert(0, default_S[ji-1])

            # qe.configure(state="disabled")
            # pe.configure(state="disabled")
            # se.configure(state="disabled")
            
            ji += 1


        go_back_btn = tk.CTkButton(self, text="Go Back", command=lambda: controller.show_frame("SelectMCDA"))
        go_back_btn.grid(row=13, column= 0, padx=5, pady=5)

        self.submit_btn = tk.CTkButton(self, text="Submit Parameters", command=self.submit_pii)
        self.submit_btn.grid(row=13, column=1, pady=5, padx= 5)


        self.view_results_btn = tk.CTkButton(self, text="View Results", command=self.show_results)
        self.view_results_btn.grid(row=13, column=2, padx=5, pady=5)

        self.view_results_btn.configure(state='disabled')

        self.submit_lbl = tk.CTkLabel(self, text="")
        self.submit_lbl.grid(row=14, column=1, pady= 5, padx=5)

    
    def submit_pii(self):
        for j in range(12):
            if(self.pfm_list[j].get() == "U-Shape"):
                q[j] = float(qe_list[j].get())

            elif(self.pfm_list[j].get()=="V-Shape"):
                p[j] = float(pe_list[j].get())
            
            elif(self.pfm_list[j].get() =="Level"):
                q[j] = float(qe_list[j].get())
                p[j] = float(pe_list[j].get())

            elif(self.pfm_list[j].get() == "V-Shape with Indifference"):
                q[j] = float(qe_list[j].get())
                p[j] = float(pe_list[j].get())

            elif(self.pfm_list[j].get() =="Gaussian"):
                s[j] = float(se_list[j].get())

            elif(self.pfm_list[j].get() =="C-Form"):
                s[j] = float(se_list[j].get())
                    
            print(self.pfm_list[j].get())
            pii_f[j] = pf_dict[self.pfm_list[j].get()]

        print(q)
        print(p)
        print(s)

        self.submit_lbl.configure(text="PROMETHEE II Parameters Submitted")
        self.view_results_btn.configure(state='normal')
    
    def show_results(self):
        flow = promethee_ii(input_pm, criterion_type, W = weights_aip_wgmm, Q = q, S = s, P = p, F = pii_f, sort = False, topn = 10, graph = False)
        # flow = flow[np.argsort(flow[:, 1])]
        # flow = flow[::-1]

        global chosen_method
        chosen_method = "PROMETHEE II"

        self.controller.frames["Results"].ranking(flow)

        self.controller.show_frame("Results")

        return
    
    # For simplified mode
    def simplified_results(self):
        # global default_maut_functions, default_maut_step
        # default_pii_functions = [""]*12
        # for j in range(12):
        #     if(default_pii_functions[j]=="Step"):
        #         d_simple_maut_functions[j] = "step"
        #         # self.op_nbr[j] = int(self.op_entries[j].get())
        #     elif(default_pii_functions[j]=="Quadratic"):
        #         d_simple_maut_functions[j] = "quad"
        #     else:
        #         d_simple_maut_functions[j] = default_maut_functions[j].lower()[0:3]

        # flow = maut_method(input_pm, weights_aip_wgmm, criterion_type, default_pii_functions, default_maut_step, graph=False)
        global default_pii_functions
        for i in range(len(default_pii_functions)):
            default_pii_functions[i] = pf_dict[default_pii_functions[i]]

        flow = promethee_ii(input_pm, criterion_type, weights_aip_wgmm, default_Q, default_S, default_P, default_pii_functions, sort=False, topn = 10, graph = False)

        global chosen_method
        chosen_method = "PROMETHEE II"
        
        self.controller.frames["Results"].ranking(flow)
        self.controller.show_frame('Results')

class Results(tk.CTkFrame):

    def __init__(self, parent, controller):
        tk.CTkFrame.__init__(self, parent)
        self.controller = controller
        

    def ranking(self, flow):
        for widget in self.winfo_children():
            widget.destroy()

        app.geometry("1271x562")

        global chosen_method

        global scores_txt
        scores_txt= "DM "

        for i in range(dms_number):
            if(i==dms_number-1):
                scores_txt += str(i+1) + ": " + str(round(flow[i,1], 3)) + "."

            else:
                scores_txt += str(i+1) + ": " + str(round(flow[i,1], 3)) + ", DM "

        print(flow)

        flow = flow[np.argsort(flow[:, 1])]
        flow = flow[::-1]
        print(flow[0,0])

        title = tk.CTkLabel(self, text=chosen_method + " Election Results", font=self.controller.title_font)
        title.pack(side="top", fill="x", pady=10)

        self.winner_lbl = tk.CTkLabel(self, text="", font=('Arial', 12))
        self.winner_lbl.pack(side='top')

        labels_frame = tk.CTkFrame(self.controller.frames["Results"], height=100)
        labels_frame.pack(side="top")#, expand=True, fill='x')

        ranking_graph_lbl = tk.CTkLabel(labels_frame, text="Outranking Graph")
        # ranking_graph_lbl.grid(row=0,column=2, sticky='E')
        ranking_graph_lbl.pack(side="right", padx=259.5)

        radar_chart_lbl = tk.CTkLabel(labels_frame, text="Radar Chart")
        # radar_chart_lbl.grid(row=0,column=0, sticky='W')
        radar_chart_lbl.pack(side="left", padx=259.5)

        # graphs_frame = tk.CTkFrame(self)
        # graphs_frame.pack(fill="both", expand=True)

        button = tk.CTkButton(self, text="Go to the start frame",
                           command=lambda: self.controller.show_frame("StartPage"))
        button.pack(side="bottom")

        global mode
        
        if(mode !="simplified"):
            go_back_btn = tk.CTkButton(self, text="Go Back", command=lambda: self.controller.show_frame(prev_frame))
            go_back_btn.pack(side="bottom")
        
        self.scores_lbl = tk.CTkLabel(self, text=chosen_method + " Scores: "+ scores_txt)
        self.scores_lbl.pack(side='bottom')
        
        
        f = Figure(figsize=(1,2), dpi=100)
        a = f.add_subplot(111)
        # a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])

        rank_xy = np.zeros((flow.shape[0], 2))

        # Vertical Graph
        # for i in range(0, rank_xy.shape[0]):
        #     rank_xy[i, 0] = 0
        #     rank_xy[i, 1] = flow.shape[0]-i

        # a.text(rank_xy[0, 0],  rank_xy[0, 1], 'DM ' + str(int(flow[0,0])), size = 20, ha = 'center', va = 'center', bbox= dict(boxstyle = 'round', ec = (0.0, 0.0, 0.0), fc = 'y'))           
        # for i in range(1, rank_xy.shape[0]):
        #     a.text(rank_xy[i, 0],  rank_xy[i, 1], 'DM ' + str(int(flow[i,0])), size = 20, ha = 'center', va = 'center', bbox= dict(boxstyle = 'round', ec = (0.0, 0.0, 0.0), fc = 'c'))
        # for i in range(0, rank_xy.shape[0]-1):
        #     a.arrow(rank_xy[i, 0], rank_xy[i, 1], rank_xy[i+1, 0] - rank_xy[i, 0], rank_xy[i+1, 1] - rank_xy[i, 1]+0.1, head_width = 0.05, head_length = 0.2, overhang = 0.0, color = 'black', linewidth = 0.9, length_includes_head = True)

        # a.set_xlim([-1, +1])
        # ymin = np.amin(rank_xy[:,1])
        # ymax = np.amax(rank_xy[:,1])
        # if (ymin < ymax):
        #     a.set_ylim([ymin, ymax])
        # else:
        #     a.set_ylim([ymin-1, ymax+1])
        # a.axis('off')
        
        #Horizontal Graph:
        for i in range(0, rank_xy.shape[0]):
            rank_xy[i, 0] = 0
            rank_xy[i, 1] = i #flow.shape[0]-i           
        for i in range(0, rank_xy.shape[0]):
            a.text(rank_xy[i, 1],  rank_xy[i, 0], 'DM ' + str(int(flow[i,0])), size = 18, ha = 'center', va = 'center', bbox= dict(boxstyle = 'round', ec = (0.0, 0.0, 0.0), fc = 'c'))
        for i in range(0, rank_xy.shape[0]-1):
            a.arrow(rank_xy[i, 1], rank_xy[i, 0], rank_xy[i+1, 1] - rank_xy[i, 1]-0.1, rank_xy[i+1, 0] - rank_xy[i, 0], head_width = 0.05, head_length = 0.2, overhang = 0.0, color = 'black', linewidth = 0.9, length_includes_head = True)

        a.set_ylim([-1, +1])
        xmin = np.amin(rank_xy[:,1])
        xmax = np.amax(rank_xy[:,1])
        if (xmin < xmax):
            a.set_xlim([xmin, xmax])
        else:
            a.set_xlim([xmin-1, xmax+1])
        a.axis('off')


        # axes = a.gca()
        # plt.show()

        canvas = FigureCanvasTkAgg(f, self)
        # canvas.show()
        canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()

        canvas._tkcanvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        
        # graph_coord_x = canvas.get_tk_widget().winfo_rootx()

        #Radar Chart
        # global norm_dataset1
        global input_pm
        global election_criteria

        #Normalize the input PM
        norm_input_pm = np.zeros([input_pm.shape[0],input_pm.shape[1]])

        for i in range(input_pm.shape[0]):
            norm_row = []
            for j in range(input_pm.shape[1]):
                norm_row.append(input_pm[i,j]/ np.max(input_pm[:,j]))

            norm_input_pm[i] = norm_row

        print(norm_input_pm)
        # print(norm_dataset1)

        # data = [['Experience as DM', 'Treated Breakdowns', 'Distance', 'Coordination Experience', 'Response Time', 'Open Ports', 'Vulnerabilities', 'Severity Sum','Connection Type','Network Latency','Download Speed', 'Upload Speed'],
        # ('Basecase', [
        #     [0.88, 0.01, 0.03, 0.03, 0.00, 0.06, 0.01, 0.00, 0.00],
        #     [0.07, 0.95, 0.04, 0.05, 0.00, 0.02, 0.01, 0.00, 0.00],
        #     [0.01, 0.02, 0.85, 0.19, 0.05, 0.10, 0.00, 0.00, 0.00],
        #     [0.02, 0.01, 0.07, 0.01, 0.21, 0.12, 0.98, 0.00, 0.00],
        #     [0.01, 0.01, 0.02, 0.71, 0.74, 0.70, 0.00, 0.00, 0.00]])]
        
        N = 12
        theta = radar_factory(N, frame='polygon')

        spoke_labels = election_criteria
        title = 'Objective Attainment Percentages for DM ' + str(int(flow[0,0]))
        # case_data = [norm_input_pm[int(flow[0,0])-1]]
        case_data = [norm_dataset1[int(flow[0,0])-1]]
        # print(case_data.shape)

        fig, ax = pyplt.subplots(figsize=(1, 1), subplot_kw=dict(projection='radar'))
        fig.subplots_adjust(top=0.85, bottom=0.1)
        # fig.set_size_inches(7,6)

        ax.set_rgrids([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_title(title,  position=(0.5, 1.1), ha='center')

        for d in case_data:
            line = ax.plot(theta, d)
            ax.fill(theta, d,  alpha=0.25)
        ax.set_varlabels(spoke_labels)
        
        canvas2 = FigureCanvasTkAgg(fig, self)
        canvas2.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # toolbar = NavigationToolbar2Tk(canvas2, self)
        # toolbar.update()
        # canvas2.show()
        canvas2._tkcanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # app doesn't stop in the terminal after closing the window !

        prev_frame = ""

        if(chosen_method=="MAUT"):
            prev_frame = "MAUT_Parameters"
        elif(chosen_method == "PROMETHEE II" and mode=="simplified"):
            prev_frame = "StartPage"
        elif(chosen_method =="PROMETHEE II" and mode=="advanced"):
            prev_frame = "Pii_Functions"
        elif(chosen_method == "SAW"):
            prev_frame = "SelectMCDA"
        elif(chosen_method == "TOPSIS"):
            prev_frame = "SelectMCDA"
        

        self.winner_lbl.configure(text= "The elected facilitator is DM "+ str(int(flow[0,0])))


        



def radar_factory(num_vars, frame='circle'):
    """Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle' | 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)

    class RadarAxes(PolarAxes):

        name = 'radar'

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # rotate plot such that the first axis is at the top
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            # The Axes patch must be centered at (0.5, 0.5) and of radius 0.5
            # in axes coordinates.
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars,
                                      radius=.5, edgecolor="k")
            else:
                raise ValueError("unknown value for 'frame': %s" % frame)

        def draw(self, renderer):
            """ Draw. If frame is polygon, make gridlines polygon-shaped """
            if frame == 'polygon':
                gridlines = self.yaxis.get_gridlines()
                for gl in gridlines:
                    gl.get_path()._interpolation_steps = num_vars
            super().draw(renderer)


        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                spine = Spine(axes=self,
                              spine_type='circle',
                              path=Path.unit_regular_polygon(num_vars))
                # unit_regular_polygon gives a polygon of radius 1 centered at
                # (0, 0) but we want a polygon of radius 0.5 centered at (0.5,
                # 0.5) in axes coordinates.
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5)
                                    + self.transAxes)


                return {'polar': spine}
            else:
                raise ValueError("unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)
    return theta

# root = tk.CTk()
# PM(root).pack(side="top", fill="both", expand=True)
# root.mainloop()

if __name__ == "__main__":
    app = SampleApp()
    app.title("Coordinator Election")
    # app.iconbitmap("win_icon.ico")
    app.after(201, lambda: app.iconbitmap("win_icon.ico"))
    
    app.protocol("WM_DELETE_WINDOW", lambda:on_closing_window())

    def on_closing_window():
        # app.destroy()
        # quit()
        sys.exit()

    # app.geometry("332x417")
    # app.geometry("1271x562")
    app.geometry("1280x500")

    app.resizable(width=False, height=False)
    # app.tk.call('tk','scaling', 2)
    
    # app.tk.call("source", "azure.tcl")
    # app.tk.call("set_theme", "light")
    
    app.mainloop()
