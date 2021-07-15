import os
import pickle
import sys
import time

from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Progressbar
from tkinter.ttk import Notebook
from tkinter.ttk import Combobox

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from lib import GEM_ANALYSIS_classes as AN_CLASS

OS = sys.platform
if OS == 'win32':
	sep = '\\'
elif OS == 'linux2' or 'linux':
	sep = '/'
else:
	print("ERROR: OS {} non compatible".format(OS))
	sys.exit()

TP_rate = 49000



class menu():
    def __init__(self,main_menu,gemroc_handler):
        self.error_window_main = Toplevel(main_menu)
        self.error_window_main.wm_title("Generic scan interface")
        self.tabControl = Notebook(self.error_window_main)  # Create Tab Control

        noise_measure_=generic_scan(self.error_window_main ,gemroc_handler,self.tabControl)
        noise_measure_._insert("Generic scan")
        noise_measure_._init_windows()
        self.tabControl.pack(expand=1, fill="both")  # Pack to make visible

class generic_scan ():
    def __init__(self,main_window,gemroc_handler,tab_control):
        self.title="Generic scan"
        self.tabControl=tab_control
        self.main_window=main_window
        self.scan_matrixs={}
        self.efine_average={}
        self.efine_stdv={}
        self.total_events = {}
        self.GEMROC_reading_dict=gemroc_handler
        self.error_window=Frame(self.main_window)

    def _init_windows(self):
        Label(self.error_window,text=self.title,font=("Courier", 25)).grid(row=0, column=2, sticky=S, pady=4,columnspan=10)
        tot=len(self.GEMROC_reading_dict)

        self.TD_scan_result={}
        number_list=[]
        i=0
        self.first_row=Frame(self.error_window)
        self.first_row.grid(row=1, column=1, sticky=S, pady=4,columnspan=10)

        self.plotting_gemroc = 0
        self.plotting_TIGER = 0
        self.plotting_Channel = 0

        self.second_row_frame=Frame(self.error_window)
        self.second_row_frame.grid(row=2, column=1, sticky=S, pady=4,columnspan=10)


        self.GEMROC_num = StringVar(self.error_window)
        self.scan_key = StringVar(self.error_window)

        self.TIGER_num_first = IntVar(self.error_window)
        self.TIGER_num_last = IntVar(self.error_window)
        self.CHANNEL_num_first = IntVar(self.error_window)
        self.CHANNEL_num_last = IntVar(self.error_window)
        self.param_first = IntVar(self.error_window)
        self.param_last = IntVar(self.error_window)


        Label(self.second_row_frame, text='First TIGER   ').pack(side=LEFT)
        Entry(self.second_row_frame, width=4, textvariable=self.TIGER_num_first).pack(side=LEFT)

        Label(self.second_row_frame, text='Last TIGER   ').pack(side=LEFT)
        Entry(self.second_row_frame, width=4, textvariable=self.TIGER_num_last).pack(side=LEFT)

        Label(self.second_row_frame, text='First Channel  ').pack(side=LEFT)
        Entry(self.second_row_frame, width=4, textvariable=self.CHANNEL_num_first).pack(side=LEFT)

        Label(self.second_row_frame, text='Last Channel   ').pack(side=LEFT)
        Entry(self.second_row_frame, width=4, textvariable=self.CHANNEL_num_last).pack(side=LEFT)

        Label(self.second_row_frame, text='Start ').pack(side=LEFT)
        Entry(self.second_row_frame, width=4, textvariable=self.param_first).pack(side=LEFT)

        Label(self.second_row_frame, text='End   ').pack(side=LEFT)
        Entry(self.second_row_frame, width=4, textvariable=self.param_last).pack(side=LEFT)

        fields_optionsG = self.GEMROC_reading_dict.keys()
        # fields_optionsG.append("All") Add again all lter
        OptionMenu(self.first_row, self.GEMROC_num, *fields_optionsG,).pack(side=LEFT)
        self.third_row=Frame(self.error_window)
        self.third_row.grid(row=3, column=1, sticky=S, pady=4,columnspan=10)
        self.fields_optionspar_c,  self.fields_optionspar_g= self.acquire_keys()
        fields_optionspar = self.fields_optionspar_c + self.fields_optionspar_g
        self.scan_key.set("TP_Vcal_ref")
        Combobox(self.third_row, textvariable=self.scan_key, values=fields_optionspar).pack(side=LEFT)
        self.strart_button=Button(self.third_row, text ='Launch scan',  command=self.launch_scan)
        self.strart_button.pack(side=LEFT,padx=2)
        Button(self.third_row, text="Save", command=self.SAVE).pack(side=LEFT,padx=2)
        Button(self.third_row, text="Load", command=self.LOAD).pack(side=LEFT,padx=2)
        self.Activate_TP = BooleanVar (self.main_window)
        Checkbutton(self.third_row, text="Activate TP on channels (one by one)", variable=self.Activate_TP).pack(side=LEFT, padx=2)
        Button(self.third_row, text="Dump on txt", command=self.DUMP).pack(side=LEFT,padx=2)

        self.corn0 = Frame(self.error_window)
        self.corn0.grid(row=4, column=0, sticky=S, pady=4,columnspan=10)
        self.LBOCC = Label(self.corn0, text='Threshold scan', font=("Times", 18))
        self.LBOCC.grid(row=0, column=1, sticky=S, pady=4)
        self.butleftG = Button(self.corn0, text='<', command=lambda: self.change_G_or_T(-1, "G")).grid(row=1, column=0, sticky=S, pady=4)
        self.LBGEM = Label(self.corn0, text='GEMROC {}'.format(self.plotting_gemroc), font=("Courier", 12))
        self.LBGEM.grid(row=1, column=1, sticky=S, pady=4)
        self.butrightG = Button(self.corn0, text='>', command=lambda: self.change_G_or_T(1, "G")).grid(row=1, column=2, sticky=S, pady=4)
        self.butleftT = Button(self.corn0, text='<', command=lambda: self.change_G_or_T(-1, "T")).grid(row=2, column=0, sticky=S, pady=4)
        self.LBTIG = Label(self.corn0, text='TIGER {}'.format(self.plotting_TIGER), font=("Courier", 12))
        self.LBTIG.grid(row=2, column=1, sticky=S, pady=4)
        self.butrightT = Button(self.corn0, text='>', command=lambda: self.change_G_or_T(1, "T")).grid(row=2, column=2, sticky=S, pady=4)

        self.usefullframe=Frame(self.corn0)
        self.usefullframe.grid(row=3, column=1, sticky=S, pady=4)
        Button(self.usefullframe, text='<', command=lambda: self.change_G_or_T(-1, "C")).grid(row=0, column=0, sticky=S, pady=4)

        self.LBCH = Label(self.usefullframe, text='CHANNEL ', font=("Courier", 12))
        self.LBCH.grid(row=0, column=1, sticky=S, pady=4)
        self.CHentry=Entry(self.usefullframe,textvariable=self.plotting_Channel,width=4)
        self.CHentry.grid(row=0, column=2, sticky=S, pady=4)
        Button(self.usefullframe, text='Go', command=lambda: self.change_G_or_T(1, "GO")).grid(row=0, column=3, sticky=S, pady=4)
        Button(self.usefullframe, text='>', command=lambda: self.change_G_or_T(1, "C")).grid(row=0, column=4, sticky=S, pady=4)

        self.corn1 = Frame(self.error_window)
        self.corn1.grid(row=12, column=1, sticky=S, pady=8,padx=8,columnspan=100)

        # Plot
        x = np.arange(0, 1)
        v = np.zeros((1))

        self.fig = Figure(figsize=(5,5))
        self.plot_rate = self.fig.add_subplot()
        self.scatter, = self.plot_rate.plot(x, v, 'r+',label = "data")



        self.plot_rate.set_title("TIGER {}, GEMROC {}".format(self.plotting_TIGER, self.plotting_gemroc))
        self.plot_rate.set_ylabel("Efine")

        self.plot_rate.set_xlabel("Step")
        self.plot_rate.ticklabel_format(style='sci', scilimits=(-3, 4), axis='both')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.corn1)
        self.canvas.get_tk_widget().pack(side=BOTTOM)
        self.canvas.draw()
        self.canvas.flush_events()
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.corn1)
        self.toolbar.canvas.draw_idle()
        self.line_list=[]
        # for number, GEMROC_number in self.GEMROC_reading_dict.items():
        #     print number
        for i in range (0,21):
            number="GEMROC {}".format(i)
            self.scan_matrixs[number]=np.zeros((8,64,64))

            self.TP_settings={}
            self.total_events[number] = {}
            self.efine_average[number] = {}
            self.efine_stdv[number] = {}
            for T in range (0,8):

                self.TP_settings["TIG{}".format(T)]={}
                self.total_events[number]["TIG{}".format(T)] = {}
                self.efine_average[number]["TIG{}".format(T)] = {}
                self.efine_stdv[number]["TIG{}".format(T)] = {}
                for ch in range (0,64):
                    # self.gaussians[number]["TIG{}".format(T)]["CH{}".format(ch)]=(0,0,0,0)
                    self.efine_average[number]["TIG{}".format(T)]["CH{}".format(ch)] = []
                    self.efine_stdv[number]["TIG{}".format(T)]["CH{}".format(ch)] = []
                    self.total_events[number]["TIG{}".format(T)]["CH{}".format(ch)] = []


    def _insert(self,name):
        self.tabControl.add(self.error_window, text=name)  # Add the tab


    def launch_scan(self):
        """
        Launch the scna procedure
        :return:
        """
        self.sampling_scan=True
        if self.Activate_TP.get():
            self.start_TP()
        GEMROC=self.GEMROC_reading_dict["{}".format(self.GEMROC_num.get())]
        GEM_COM = GEMROC.GEM_COM
        c_inst = GEMROC.c_inst
        g_inst = GEMROC.g_inst
        test_r = AN_CLASS.analisys_read(GEM_COM, c_inst)
        first = self.TIGER_num_first.get()
        last = self.TIGER_num_last.get()+1
        firstch = self.CHANNEL_num_first.get()
        lastch = self.CHANNEL_num_last.get()+1
        GEMROC_ID = GEM_COM.GEMROC_ID

        for T in range(first, last):  # TIGER
            for J in range(firstch, lastch):  # Channel
                self.efine_average["GEMROC {}".format(GEMROC_ID)]["TIG{}".format(T)]["CH{}".format(J)]=[]
                self.efine_average["GEMROC {}".format(GEMROC_ID)]["TIG{}".format(T)]["CH{}".format(J)]=[]
                self.total_events["GEMROC {}".format(GEMROC_ID)]["TIG{}".format(T)]["CH{}".format(J)]=[]

                for i in range(int(self.param_first.get()), int(self.param_last.get())):
                    print ("{} set {}".format(self.scan_key.get(),i))
                    if self.Activate_TP.get():
                        GEM_COM.Set_param_dict_channel(c_inst,"TP_disable_FE", T, J, 0)
                        GEM_COM.Set_param_dict_global(g_inst,"FE_TPEnable", T, 1)

                    GEM_COM.Set_param_dict_channel(c_inst, "TriggerMode", T, J, 0)
                    if self.scan_key.get() in self.fields_optionspar_c:
                        GEM_COM.Set_param_dict_channel(c_inst, self.scan_key.get(), T,J, i)
                    if self.scan_key.get() in self.fields_optionspar_g:
                        GEM_COM.Set_param_dict_global(g_inst, self.scan_key.get(), T, i)
                    GEM_COM.SynchReset_to_TgtFEB()
                    average,stdv,total=test_r.acquire_Efine(J,T,0.5)
                    self.efine_average["GEMROC {}".format(GEMROC_ID)]["TIG{}".format(T)]["CH{}".format(J)].append(average)
                    self.efine_stdv["GEMROC {}".format(GEMROC_ID)]["TIG{}".format(T)]["CH{}".format(J)].append(stdv)
                    self.total_events["GEMROC {}".format(GEMROC_ID)]["TIG{}".format(T)]["CH{}".format(J)].append(total)
                    GEM_COM.Set_param_dict_channel(c_inst, "TriggerMode", T, J, 3)
                    if self.Activate_TP.get():
                        GEM_COM.Set_param_dict_channel(c_inst,"TP_disable_FE", T, J, 1)
                        GEM_COM.Set_param_dict_global(g_inst,"FE_TPEnable", T, 0)


    def change_G_or_T(self, i, G_or_T):
        if G_or_T == "G":
            self.plotting_gemroc = self.plotting_gemroc + i
            if self.plotting_gemroc == -1:
                self.plotting_gemroc = 0
            if self.plotting_gemroc == 20:
                self.plotting_gemroc = 19

        if G_or_T == "T":
            self.plotting_TIGER = self.plotting_TIGER + i
            if self.plotting_TIGER == -1:
                self.plotting_TIGER = 0
            if self.plotting_TIGER == 8:
                self.plotting_TIGER = 7

        if G_or_T == "C":
            self.plotting_Channel = self.plotting_Channel + i
            if self.plotting_Channel < 0:
                self.plotting_Channel = 0
            if self.plotting_Channel > 63:
                self.plotting_Channel = 63
        if G_or_T == "GO":
            self.plotting_Channel=int(self.CHentry.get())

        self.refresh_plot()


    def refresh_plot(self):
        self.LBGEM['text'] = 'GEMROC {}'.format(self.plotting_gemroc)
        self.LBTIG['text'] = 'TIGER {}'.format(self.plotting_TIGER)
        # self.LBCH['text'] = 'CHANNEL {}'.format(self.plotting_Channel)
        self.CHentry.delete(0,END)
        self.CHentry.insert(END,self.plotting_Channel)
        self.plotta()

    def start_TP(self):
        for number, GEMROC_number in self.GEMROC_reading_dict.items():
            GEMROC_number.GEM_COM.Soft_TP_generate()
            GEMROC_number.GEM_COM.gemroc_DAQ_XX.DAQ_config_dict['TL_nTM_ACQ'] = 1
            GEMROC_number.GEM_COM.gemroc_DAQ_XX.DAQ_config_dict['Periodic_TP_EN_pattern'] = 15
            GEMROC_number.GEM_COM.gemroc_DAQ_XX.DAQ_config_dict['number_of_repetitions'] = 512 + 1
            GEMROC_number.GEM_COM.gemroc_DAQ_XX.DAQ_config_dict['TP_width'] = 14
            GEMROC_number.GEM_COM.DAQ_set_with_dict()
    def plotta(self):
        for number, GEMROC_number in self.GEMROC_reading_dict.items():
            if int(number.split()[1]) == int(self.plotting_gemroc):
                GEMROC_ID=self.plotting_gemroc
                self.plot_rate.set_title("ROC {},TIG {}, CH {} ".format(self.plotting_gemroc, self.plotting_TIGER, self.plotting_Channel))
                y=(self.efine_average["GEMROC {}".format(GEMROC_ID)]["TIG{}".format(self.plotting_TIGER)]["CH{}".format(self.plotting_Channel)])
                x=(range(self.param_first.get(),self.param_last.get()))
                y=np.nan_to_num(y)
                if len (y)>0:
                    self.scatter.set_ydata(y)
                    self.scatter.set_xdata(x)
                    self.plot_rate.set_xlim([x[0]-1,x[-1]+1])
                    self.plot_rate.set_ylim([np.min(y)-0.1*np.max(y), np.max(y)+0.1*np.max(y)])
                    self.plot_rate.set_xlabel(f"{self.scan_key.get()}", fontsize=14)

                    self.canvas.draw()
                    self.canvas.flush_events()
                break

        self.canvas.draw()
        self.canvas.flush_events()
    def SAVE(self):
        File_name = filedialog.asksaveasfilename(initialdir="." + sep + "noise_scan" + sep + "saves", title="Select file", filetypes=(("Noise scan files", "*.ns"), ("all files", "*.*")))
        with  open(File_name, 'wb') as f:
            pickle.dump(self.scan_matrixs,f)


    def LOAD(self):
        filename = filedialog.askopenfilename(initialdir="." + sep + "noise_scan" + sep + "saves", title="Select file", filetypes=(("Noise scan files", "*.ns"), ("all files", "*.*")))
        with  open(filename, 'rb') as f:
            self.scan_matrixs=pickle.load(f)

    def DUMP(self):
        """
        Dump the matrix in a txt file
        :return:
        """
        File_name = filedialog.asksaveasfilename(initialdir=".", title="Select file for dump", filetypes=(("txt", "*.txt"), ("all files", "*.*")))
        with open (File_name,'w+') as dumpfile:
            GEMROC_key=self.GEMROC_num.get()
            dumpfile.write(f"Scan of {self.scan_key.get()} from {self.param_first.get()} to {self.param_last.get()-1}\n")
            for TIGER_key in range(self.TIGER_num_first.get(), self.TIGER_num_last.get()+1):
                for chkey in range(self.CHANNEL_num_first.get(), self.CHANNEL_num_last.get()+1):
                        dumpfile.write(f"{GEMROC_key}   Tiger {TIGER_key}   Channel {chkey}\n")
                        dumpfile.write("Total event\t Efine\tSigma\n")
                        for Efine,sigma,tota in zip(self.efine_average[GEMROC_key][f"TIG{TIGER_key}"][f"CH{chkey}"], self.efine_stdv[GEMROC_key][f"TIG{TIGER_key}"][f"CH{chkey}"], self.total_events[GEMROC_key][f"TIG{TIGER_key}"][f"CH{chkey}"]):
                            dumpfile.write(f"{tota}\t{Efine}\t{sigma}\n")

    def acquire_keys(self):
        """
        Function to acquire all the keys for global and channel configuration
        :return:
        """
        key_list_channel = []
        with open ("lib"+sep+"keys"+sep+"channel_conf_file_keys", 'r') as G:
            for line in G.readlines():
                key_list_channel.append(line.strip())

        key_list_global = []
        with open("lib" + sep + "keys" + sep + "global_conf_file_keys", 'r') as C:
            for line in C.readlines():
                key_list_global.append(line.strip())
        return key_list_channel,key_list_global

def squared_sum(A,B):
    #A= Aspettati
    if len(A)== len(B):
        C=np.zeros((len(A)))
        #for i in range (0,len(B)):
            # C[i]=((A[i]-B[i])**2)/(A[i]+0.001)
        C=((A-B)**2)/(A+0.001)
        return np.sum(C)
    else:
        raise Exception("A and B not same size")

def process_image(data):
    values =AN_CLASS.error_fit(data,TP_rate, Ebranch=True)
    return values