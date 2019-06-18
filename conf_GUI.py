from Tkinter import *
from ttk import Progressbar
import Tkinter, Tkconstants, tkFileDialog
import numpy as np
from lib import GEM_COM_classes as COM_class
import communication_error_GUI as error_GUI
import noise_GUI as noise_GUI
from multiprocessing import Process, Pipe
import acq_GUI as acq_GUI
from lib import GEM_ANALYSIS_classes as AN_CLASS, GEM_CONF_classes as GEM_CONF
import sys
import array
import time
import ttk
import pickle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

OS = sys.platform
if OS == 'win32':
    sep = '\\'
elif OS == 'linux2':
    sep = '/'
else:
    print("ERROR: OS {} non compatible".format(OS))
    sys.exit()


# TODO: bugs:
# Add completition bars for TD scan
# TODO: LV settings
class menu():
    def __init__(self):
        self.GEM_to_config = np.zeros((20))
        self.configuring_gemroc = 0
        # main window
        self.main_window = Tk()

        self.icon_on = PhotoImage(file="." + sep + 'icons' + sep + 'on.gif')
        self.icon_off = PhotoImage(file="." + sep + 'icons' + sep + 'off.gif')
        self.icon_bad = PhotoImage(file="." + sep + 'icons' + sep + 'bad.gif')
        self.icon_GUFI1 = PhotoImage(file="." + sep + 'icons' + sep + 'gufi3.gif')
        self.icon_GUFI2 = PhotoImage(file="." + sep + 'icons' + sep + 'gufi4.gif')

        self.main_window.wm_title("Configuration")
        # self.main_window.tk.call('wm', 'iconphoto', self.main_window._w, self.icon_bad)
        #
        # self.main_window.title("GEMROC configurer")
        self.handler_list = []
        self.GEMROC_reading_dict = {}
        self.showing_GEMROC = StringVar(self.main_window)
        self.entry_text = StringVar(self.main_window)

        self.showing_TIGER = StringVar(self.main_window)
        self.showing_CHANNEL = StringVar(self.main_window)
        self.configure_MODE = StringVar(self.main_window)

        self.all_channels = StringVar(self.main_window)
        self.all_TIGERs = StringVar(self.main_window)
        self.all_GEMROCs = StringVar(self.main_window)
        self.rate = IntVar(self.main_window)
        # fields_options=["DAQ configuration", "LV configuration", "Global Tiger configuration", "Channel Tiger configuration"]
        fields_options = ["DAQ configuration", "Global Tiger configuration", "Channel Tiger configuration", "LV and diagnostic"]
        Label(self.main_window, text='Configuration', font=("Courier", 25)).pack()
        self.conf_frame = Frame(self.main_window)
        self.conf_frame.pack()
        self.first_row_frame = Frame(self.conf_frame)
        self.first_row_frame.grid(row=0, column=0, sticky=NW, pady=4)
        self.select_MODE = OptionMenu(self.first_row_frame, self.configure_MODE, *fields_options)
        self.select_MODE.grid(row=0, column=0, sticky=NW, pady=4)
        Label(self.first_row_frame, text="Errors").grid(row=0, column=1, sticky=W, padx=10)
        self.ERROR_LED = Label(self.first_row_frame, image=self.icon_off)
        self.ERROR_LED.grid(row=0, column=2, sticky=W, padx=1)
        self.second_row_frame = Frame(self.conf_frame)
        self.second_row_frame = Frame(self.conf_frame)
        self.second_row_frame.grid(row=1, column=0, sticky=NW, pady=4)
        self.label_array = []
        self.field_array = []
        self.input_array = []
        self.configure_MODE.trace('w', self.update_menu)
        self.dict_pram_list = []
        self.third_row_frame = Frame(self.conf_frame)
        self.TP_repeat = IntVar(self.main_window)
        self.TP_num = IntVar(self.main_window)
        ##Select window
        self.select_window = Toplevel(self.main_window, height=400, width = 900)
        Title_frame = Frame (self.select_window)
        Title_frame2 = Frame(self.select_window)
        Label(Title_frame2, text="         ",font=("Times", 10, "italic")).pack(side=LEFT)

        Label(Title_frame2, image=self.icon_GUFI1).pack(side=LEFT)
        Label(Title_frame2, text="GUFI software",font=("Times", 25)).pack(side=LEFT)
        Label(Title_frame2, image=self.icon_GUFI2).pack(side=LEFT)

        Label(Title_frame, text="             v.2.3 -- 2019 -- INFN-TO (abortone@to.infn.it)",font=("Times", 10, "italic")).pack(anchor=SE, side=RIGHT)
        Title_frame2.pack(anchor=S)
        Title_frame.pack(fill=BOTH)

        self.tabControl = ttk.Notebook(self.select_window)  # Create Tab Control
        self.select_frame = Frame(self.select_window)
        Tante_frame = Frame(self.select_window)

        self.tabControl.add(self.select_frame,text = "Selection")
        self.tabControl.add(Tante_frame,text = "Operations")

        self.select_window.wm_title("Selection window")
        self.tabControl.pack(expand=1, fill="both")  # Pack to make visible

        Label(self.select_frame, text='GEMROC selection', font=("Times", 25)).pack()
        self.grid_frame = Frame(self.select_frame)
        self.grid_frame.pack()
        Button(self.grid_frame, text='ROC 00', command=lambda: self.toggle(0)).grid(row=0, column=0, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 01', command=lambda: self.toggle(1)).grid(row=0, column=2, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 02', command=lambda: self.toggle(2)).grid(row=0, column=4, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 03', command=lambda: self.toggle(3)).grid(row=0, column=6, sticky=W, pady=15)
        Button(self.grid_frame, text='ROC 04', command=lambda: self.toggle(4)).grid(row=0, column=8, sticky=W, pady=15)
        Button(self.grid_frame, text='ROC 05', command=lambda: self.toggle(5)).grid(row=0, column=10, sticky=W, pady=15)
        Button(self.grid_frame, text='ROC 06', command=lambda: self.toggle(6)).grid(row=0, column=12, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 07', command=lambda: self.toggle(7)).grid(row=0, column=14, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 08', command=lambda: self.toggle(8)).grid(row=0, column=16, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 09', command=lambda: self.toggle(9)).grid(row=0, column=18, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 10', command=lambda: self.toggle(10)).grid(row=1, column=0, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 11', command=lambda: self.toggle(11)).grid(row=1, column=2, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 12', command=lambda: self.toggle(12)).grid(row=1, column=4, sticky=W, pady=15)
        Button(self.grid_frame, text='ROC 13', command=lambda: self.toggle(13)).grid(row=1, column=6, sticky=W, pady=15)
        Button(self.grid_frame, text='ROC 14', command=lambda: self.toggle(14)).grid(row=1, column=8, sticky=W, pady=15)
        Button(self.grid_frame, text='ROC 15', command=lambda: self.toggle(15)).grid(row=1, column=10, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 16', command=lambda: self.toggle(16)).grid(row=1, column=12, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 17', command=lambda: self.toggle(17)).grid(row=1, column=14, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 18', command=lambda: self.toggle(18)).grid(row=1, column=16, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 19', command=lambda: self.toggle(19)).grid(row=1, column=18, sticky=NW, pady=15)
        self.error_frame = Frame(self.select_frame)
        self.error_frame.pack()
        Label(self.error_frame, text='Message ').grid(row=0, column=1, sticky=NW, pady=4)
        self.Launch_error_check = Label(self.error_frame, text='-', background='white')
        self.Launch_error_check.grid(row=0, column=2, sticky=NW, pady=4)
        title_frame=Frame(Tante_frame)
        title_frame.grid(row=0, column=5, sticky=N, pady=4,columnspan=20)
        Label(title_frame, text='Functions', font=("Times", 25)).pack()

        first_row_coperations= Frame (Tante_frame)
        first_row_coperations.grid(row=2, column=5, sticky=N, pady=10,columnspan=20)
        Button(first_row_coperations, text="Sync Reset to all", command=self.Synch_reset, activeforeground="#f77f00").pack(side=LEFT)
        Button(first_row_coperations, text="Set ext clock to all", command=lambda: self.change_clock_mode(1, 1), activeforeground="#f77f00").pack(side=LEFT)
        Button(first_row_coperations, text="Set int clock to all", command=lambda: self.change_clock_mode(1, 0), activeforeground="#f77f00").pack(side=LEFT)
        Button(first_row_coperations, text="Set pause mode to all", command=lambda: self.set_pause_mode(True, 1), activeforeground="#f77f00").pack(side=LEFT)
        Button(first_row_coperations, text="Disable pause mode to all", command=lambda: self.set_pause_mode(True, 0), activeforeground="#f77f00").pack(side=LEFT)
        Button(first_row_coperations, text="Set trigger-less mode to all", command=lambda: self.change_acquisition_mode(True, 1), activeforeground="#f77f00").pack(side=LEFT)
        Button(first_row_coperations, text="Set trigger-matched to all", command=lambda: self.change_acquisition_mode(True, 0), activeforeground="#f77f00").pack(side=LEFT)
        Tantissime_frame = Frame(Tante_frame)
        Tantissime_frame.grid(row=3, column=5, sticky=N, pady=5,columnspan=20)
        Button(Tantissime_frame, text="Write configuration", command=self.load_default_config, activeforeground="#f77f00").pack(side=LEFT)
        Button(Tantissime_frame, text="Open communication error interface", command=self.open_communicaton_GUI, activeforeground="#f77f00").pack(side=LEFT)

        cornice = Frame(Tante_frame)
        cornice.grid(row=4, column=5, sticky=N, pady=5,columnspan=20)
        Button(cornice, text="THR scan (T-branch)", command=lambda: self.thr_Scan(-1, -1, 1), activeforeground="#f77f00").pack(side=LEFT)
        Button(cornice, text="THR scan (E-branch)", command=lambda: self.thr_Scan(-1, -1, 2), activeforeground="#f77f00").pack(side=LEFT)

        Button(cornice, text="Noise measure tool", command=self.launch_noise_window, activeforeground="#f77f00").pack(side=LEFT)

        Label(cornice, text="Rate").pack(side=LEFT)
        Entry(cornice, textvar=self.rate, width=5).pack(side=LEFT)
        Button(cornice, text="Set threshold aiming to a certain rate", command=lambda: self.auto_tune(-1, -1, 15), activeforeground="#f77f00").pack(side=LEFT)
        Button(cornice, text="Load thresholds to all", command=lambda: self.load_thr(True, source="scan"), activeforeground="#f77f00").pack(side=LEFT)

        Button(cornice, text="Load auto-thr to all", command=lambda: self.load_thr(True, source="auto"), activeforeground="#f77f00").pack(side=LEFT)

        self.error_frame2 = Frame(Tante_frame)
        self.error_frame2.grid(row=5, column=5, sticky=N, pady=10,columnspan=20)
        Label(self.error_frame2, text='Message ').grid(row=0, column=1, sticky=NW, pady=4)
        self.Launch_error_check_op = Label(self.error_frame2, text='-', background='white')
        self.Launch_error_check_op.grid(row=0, column=2, sticky=NW, pady=4)


        Frame(self.select_frame, height=20).pack()
        basic_operation_frame = Frame(self.select_frame)
        basic_operation_frame.pack()
        TROPPE_frame = LabelFrame(basic_operation_frame, padx=5, pady=5,background="#cce6ff")
        TROPPE_frame.pack(side=LEFT)
        Button(TROPPE_frame, text="FEB power ON", command=self.power_on_FEBS, activeforeground="green").pack(side=LEFT)
        Button(TROPPE_frame, text="FEB power OFF", command=self.power_off_FEBS, activeforeground="red").pack(side=LEFT)
        Frame(basic_operation_frame,width=160).pack(side=LEFT)  # Spacer
        TROPPii_frame = LabelFrame(basic_operation_frame, padx=5, pady=5,background="#cce6ff")
        TROPPii_frame.pack(side=LEFT)
        Button(TROPPii_frame, text="Sync Reset to all", command=self.Synch_reset, activeforeground="blue").pack(side=LEFT)
        Button(TROPPii_frame, text="Write configuration", command=self.load_default_config, activeforeground="blue").pack(side=LEFT)
        Frame(basic_operation_frame,width=90).pack(side=LEFT)  # Spacer
        TROPPi_frame = LabelFrame(basic_operation_frame, padx=5, pady=5,background="#cce6ff")
        TROPPi_frame.pack(side=LEFT)
        Button(TROPPi_frame, text="Run controller", command=self.launch_controller, activeforeground="blue").pack(side=RIGHT)
        Button(TROPPi_frame, text="Fast configuration", command=self.fast_configuration, activeforeground="blue").pack(side=RIGHT)
        Button(TROPPi_frame, text="Enable double thr", command=self.double_enable, activeforeground="blue").pack(side=RIGHT)

        self.LED = []
        for i in range(0, len(self.GEM_to_config)):
            if i < 10:
                riga = 0
            else:
                riga = 1

            colonna = ((i) % 10) * 2 + 1
            self.LED.append(Label(self.grid_frame, image=self.icon_off))
            self.LED[i].grid(row=riga, column=colonna)

        self.advanced_threshold_settings = Frame(self.select_window)
        self.tabControl.add(self.advanced_threshold_settings,text = "Advanced threshold options")
        Label(self.advanced_threshold_settings,text="---Threshold setting with scan on noise---").pack(anchor=N)
        scan_frame = Frame(self.advanced_threshold_settings)
        scan_frame.pack()
        Label(scan_frame,text="T sigmas").pack(side=LEFT)
        self.T_thr_sigma = Entry(scan_frame, width = 4)
        self.T_thr_sigma.pack(side=LEFT)
        Label(scan_frame,text="E sigmas").pack(side=LEFT)
        self.E_thr_sigma = Entry(scan_frame, width = 4)
        self.E_thr_sigma.pack(side=LEFT)
        Button(scan_frame, text="Load thr",command= lambda: self.load_thr(to_all = True, source = 'scan', sigma_T = int(self.T_thr_sigma.get()), sigma_E = int(self.E_thr_sigma.get()))).pack(side = LEFT)
        Label(self.advanced_threshold_settings,text="---Calculate thr fC from thr set---").pack(anchor=N)
        Button(self.advanced_threshold_settings, text="Calculate",command= self.calculate_FC_thr).pack(anchor=N)

        if COM_class.local_test == True:
            for G in range (0,11):
                self.toggle(G)

        self.status_tab = Frame (self.select_window)
        self.tabControl.add(self.status_tab, text = "Version & status")
        Button(self.status_tab, text="Acquire version and FEB IVT status", command = self.acquire_IVT_version).pack(anchor = NW)
        self.statu_tab_rows = Frame (self.status_tab)
        self.statu_tab_rows.pack(anchor = NW, fill =BOTH)
        self.version_dict = {}
        self.IVT_dict = {}



    def generate_rows(self):
        """
        Generate or regenerate the rows containing the GEMROCs
        :return:
        """
        self.statu_tab_rows.destroy()
        self.statu_tab_rows = Frame (self.status_tab)
        self.statu_tab_rows.pack(anchor = NW, fill =BOTH)
        scrollbar = Scrollbar(self.statu_tab_rows, orient=VERTICAL)

        self.canvas2 = Canvas(self.statu_tab_rows)
        frame = Frame(self.canvas2, bd=1)
        scrollbar.pack(side=RIGHT, fill=Y)
        scrollbar.config(command=self.canvas2.yview)
        self.canvas2.config(yscrollcommand=scrollbar.set)
        self.canvas2.create_window((0, 0), window=frame, anchor='nw')
        frame.bind("<Configure>", self.myfunction)
        self.canvas2.pack(side=LEFT, fill=BOTH)

        for number, GEMROC in sorted(self.GEMROC_reading_dict.items(),cmp = sort_by_number):
            this_ROC_IVT = self.IVT_dict[number]
            a = Frame(frame)
            a.pack(pady=5, fill=BOTH)
            Label(a, text='{} - Firmware version: {}'.format(number,self.version_dict[number]), font=("Times",14)).pack()
            Label(a, text='---Status---',font=("Times",12)).pack()
            for device in sorted(this_ROC_IVT['status'].keys()):
                if device[0] == "F":
                    string='FEB {}:    '.format(device[3])
                    for key,value in sorted(this_ROC_IVT['status'][device].items()):
                        string += ' {}: {} ---'.format(key,value)
                    Label(a, text=string,font=("Times",10)).pack()
                if device[0] == 'R':
                    Label(a, text="GEMROC TEMP [degC] = {}".format(this_ROC_IVT['status']["ROC"]["TEMP"]),font=("Times",10)).pack()

            Label(a, text='---Limit flags---', font=("Times", 12)).pack()
            for device in sorted(this_ROC_IVT['limits'].keys()):
                if device[0] == "F":
                    string='FEB {}:    '.format(device[3])
                    for key,value in sorted(this_ROC_IVT['limits'][device].items()):
                        string += ' {}: {} ---'.format(key,value)
                    Label(a, text=string,font=("Times",10)).pack()
                if device[0] == 'R':
                    Label(a, text="GEMROC OVT_FLAG = {}".format(this_ROC_IVT['limits']["ROC"]["OVT_FLAG"]),font=("Times",10)).pack()
            Label(a, text="___________________________________________________________________________________________________________________________").pack(side=BOTTOM)

    def acquire_IVT_version(self):
        """
        Acquire IVT and version from the GEMROC and store them in the dictionary created above
        :return:
        """
        for number, GEMROC in sorted(self.GEMROC_reading_dict.items()):
            self.version_dict[number] = GEMROC.GEM_COM.read_version(GEMROC.GEM_COM.Read_GEMROC_LV_CfgReg())
            self.IVT_dict[number] = GEMROC.GEM_COM.save_IVT()
        self.generate_rows()

    def myfunction(self, event):
        """
        Function used by the scrollbar
        :param event:
        :return:
        """
        self.canvas2.configure(scrollregion=self.canvas2.bbox("all"), width=1200, height=900)

    def calculate_FC_thr(self):
        file_T = ("." + sep + "conf" + sep + "advanced_threshold_setting" + sep + "Baseline_T" +".pickle")
        file_E = ("." + sep + "conf" + sep + "advanced_threshold_setting" + sep + "Baseline_E" +".pickle")
        list_t = []
        list_e = []
        with open (file_T, 'rb') as f:
            baseline_T = pickle.load(f)
        with open(file_E, 'rb') as f:
            baseline_E = pickle.load(f)
        for number, GEMROC in self.GEMROC_reading_dict.items():
            for T in range (0,8):
                for ch in range (0,64):
                    Vth_T1 = GEMROC.c_inst.Channel_cfg_list[T][ch]["Vth_T1"]
                    Vth_T2 = GEMROC.c_inst.Channel_cfg_list[T][ch]["Vth_T2"]
                    Baseline_T1 = baseline_T[number]["TIG{}".format(T)]["CH{}".format(ch)][1]
                    Baseline_T2 = baseline_E[number]["TIG{}".format(T)]["CH{}".format(ch)][1]
                    if Baseline_T1 != "Fail":
                        print (AN_CLASS.convert_to_fC(Baseline_T1-Vth_T1, 55))
                        list_t.append(AN_CLASS.convert_to_fC(Baseline_T1-Vth_T1, 55))
                    if Baseline_T2 != "Fail":
                        print (AN_CLASS.convert_to_fC(Baseline_T2-Vth_T2, 55))
                        list_e.append(AN_CLASS.convert_to_fC(Baseline_T2-Vth_T2, 55))
        self.plot_window = Toplevel(self.main_window)

        self.fig = Figure(figsize=(14, 8))
        self.thr_T = self.fig.add_subplot(121)
        self.thr_T.hist(list_t, bins=50)
        self.thr_T.set_title("Thresholds in FC, T branch")
        self.thr_T.set_xlabel("Threshold (fC)", fontsize=14)
        self.thr_E = self.fig.add_subplot(122)
        self.thr_E.hist(list_e, bins=50)
        self.thr_E.set_title("Thresholds in FC, E branch")
        self.thr_E.set_xlabel("Threshold (fC)", fontsize=14)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_window)
        self.canvas.get_tk_widget().pack(side=BOTTOM)
        self.canvas.draw()
        self.canvas.flush_events()
        self.toolbar = NavigationToolbar2Tk(self.canvas,self.plot_window)
        self.toolbar.draw()

    def launch_noise_window(self):
        self.noise_wind = noise_GUI.menu(self.main_window, self.GEMROC_reading_dict)

    def launch_controller(self):
        self.acq = acq_GUI.menu(False, self.main_window, self.GEMROC_reading_dict, self)

    def open_communicaton_GUI(self):
        # print self.GEMROC_reading_dict
        self.conf_wind = error_GUI.menu(self.main_window, self.GEMROC_reading_dict)

    def runna(self):
        mainloop()
        # while True:
        #     self.main_window.update_idletasks()
        #     self.main_window.update()

    def toggle(self, i):
        if self.GEM_to_config[i] == 0:
            self.GEM_to_config[i] = 1
        else:
            self.GEM_to_config[i] = 0
        self.convert0(i)

    def convert0(self, i):
        if self.GEM_to_config[i] == 1:
            try:
                self.handler_list.append(GEMROC_HANDLER(i))
                self.LED[i]["image"] = self.icon_on
            except  Exception as error:
                self.Launch_error_check['text'] = "GEMROC {}: {}".format(i, error)
                self.LED[i]["image"] = self.icon_bad
            else:
                Fake = " "
                if self.handler_list[-1].GEM_COM.local_test:
                    Fake = "Simulated "
                self.Launch_error_check['text'] = "{} Communication with GEMROC {} enstablished".format(Fake, i)


        else:
            self.LED[i]["image"] = self.icon_off
            for j in range(0, len(self.handler_list)):
                if self.handler_list[j].GEMROC_ID == i:
                    self.handler_list[j].__del__()
                    del self.handler_list[j]
                    self.Launch_error_check['text'] = "Communication with GEMROC {} closed".format(i)
                    break
        self.update_menu(1, 2, 3)

    def update_menu(self, a, b, c):
        self.second_row_frame.destroy()
        self.second_row_frame = Frame(self.conf_frame)
        self.second_row_frame.grid(row=1, column=0, sticky=NW, pady=4)
        self.GEMROC_reading_dict = {}
        for i in range(0, len(self.handler_list)):
            ID = self.handler_list[i].GEMROC_ID
            self.GEMROC_reading_dict["GEMROC {}".format(ID)] = self.handler_list[i]
        Label(self.second_row_frame, text='GEMROC   ').grid(row=0, column=0, sticky=NW, pady=4)
        # print self.GEMROC_reading_dict.keys()
        self.select_GEMROC = OptionMenu(self.second_row_frame, self.showing_GEMROC, *sorted(self.GEMROC_reading_dict.keys(),cmp = sort_by_number))
        self.select_GEMROC.grid(row=1, column=0, sticky=NW, pady=4)
        fields_options = ["DAQ configuration", "LV and diagnostic", "Global Tiger configuration", "Channel Tiger configuration"]

        if self.configure_MODE.get() == "DAQ configuration":
            self.Go = Button(self.second_row_frame, text='Go', command=self.DAQ_configurator)
            self.Go.grid(row=1, column=5, sticky=NW, pady=4)


        elif self.configure_MODE.get() == "Global Tiger configuration":
            Label(self.second_row_frame, text='TIGER   ').grid(row=0, column=1, sticky=NW, pady=4)
            self.select_TIGER = OptionMenu(self.second_row_frame, self.showing_TIGER, *range(8))
            self.select_TIGER.grid(row=1, column=1, sticky=NW, pady=4)
            self.Go = Button(self.second_row_frame, text='Go', command=self.TIGER_GLOBAL_configurator)
            self.Go.grid(row=1, column=5, sticky=NW, pady=4)


        elif self.configure_MODE.get() == "Channel Tiger configuration":
            Label(self.second_row_frame, text='TIGER   ').grid(row=0, column=1, sticky=W, pady=4)
            self.select_TIGER = OptionMenu(self.second_row_frame, self.showing_TIGER, *range(8))
            self.select_TIGER.grid(row=1, column=1, sticky=W, pady=4)
            Label(self.second_row_frame, text='Channel   ').grid(row=0, column=2, sticky=W, pady=4)
            self.Channel_IN = Entry(self.second_row_frame, width=4, textvariable=self.entry_text)
            self.entry_text.trace("w", lambda *args: character_limit(self.entry_text))
            self.Channel_IN.grid(row=1, column=2, sticky=W, pady=4)
            self.Go = Button(self.second_row_frame, text='Go', command=self.TIGER_CHANNEL_configurator)
            self.Go.grid(row=1, column=5, sticky=NW, pady=4)

        elif self.configure_MODE.get() == "LV and diagnostic":
            self.Go = Button(self.second_row_frame, text='Go', command=self.LV_diag)
            self.Go.grid(row=1, column=5, sticky=NW, pady=4)

    def power_on_FEBS(self):
        for number, GEMROC in self.GEMROC_reading_dict.items():
            GEMROC.GEM_COM.FEBPwrEnPattern_set(255)

    def power_off_FEBS(self):
        for number, GEMROC in self.GEMROC_reading_dict.items():
            GEMROC.GEM_COM.FEBPwrEnPattern_set(0)

    def double_enable(self):
        for number, GEMROC in self.GEMROC_reading_dict.items():
            GEMROC.GEM_COM.double_enable(1, GEMROC.c_inst)

    def thr_Scan(self, GEMROC_num, TIGER_num, branch=1):  # if GEMROC num=-1--> To all GEMROC, if TIGER_num=-1 --> To all TIGERs
        startT = time.time()
        self.bar_win = Toplevel(self.main_window)
        self.bar_win.focus_set()  # set focus on the ProgressWindow
        self.bar_win.grab_set()
        progress_bars = []
        progress_list = []
        dict = {}
        Label(self.bar_win, text="Threshold Scan completition").pack()
        if GEMROC_num == -1:
            dict = self.GEMROC_reading_dict.copy()
        else:
            dict["{}".format(GEMROC_num)] = self.GEMROC_reading_dict[GEMROC_num]
        i = 0
        for number, GEMROC_number in dict.items():
            Label(self.bar_win, text='{}'.format(number)).pack()
            progress_list.append(IntVar())
            if TIGER_num == -1:
                maxim = 32768
            else:
                maxim = 4096
            progress_bars.append(Progressbar(self.bar_win, maximum=maxim, orient=HORIZONTAL, variable=progress_list[i], length=200, mode='determinate'))
            progress_bars[i].pack()

            i += 1
        process_list = []
        pipe_list = []
        i = 0
        for number, GEMROC_num in dict.items():
            pipe_in, pipe_out = Pipe()
            if branch == 1:
                p = Process(target=self.THR_scan_process, args=(number, TIGER_num, pipe_out))
            else:
                p = Process(target=self.THR_scan_process, args=(number, TIGER_num, pipe_out, 2))
            # pipe_in.send(progress_bars[i])
            process_list.append(p)
            pipe_list.append(pipe_in)
            p.start()
            i += 1
        while True:

            for progress, pipe, process in zip(progress_list, pipe_list, process_list):
                if process.is_alive():
                    try:
                        if pipe.poll(0.05):
                            ric = pipe.recv()
                            progress.set(ric)
                            self.bar_win.update()
                    except  Exception as Err:
                        print ("Can't acquire status: {}".format(Err))
                        progress.set(maxim)
            if all(process.is_alive() is False for process in process_list):
                print ("All finished")
                break

        #
        # for process in process_list:
        #     if process.is_alive():
        #         process.terminate()

        stopT = time.time()
        print ("Execution time: {}".format(stopT - startT))
        self.bar_win.destroy()

        # else:
        #     GEMROC = self.GEMROC_reading_dict["GEMROC {}".format(GEMROC_num)]
        #     GEM_COM = GEMROC.GEM_COM
        #     c_inst = GEMROC.c_inst
        #     g_inst = GEMROC.g_inst
        #     test_r = (AN_CLASS.analisys_conf(GEM_COM, c_inst, g_inst))

    def THR_scan_process(self, number, TIGER, pipe_out, branch=1):
        GEMROC = self.GEMROC_reading_dict[number]
        GEM_COM = GEMROC.GEM_COM
        c_inst = GEMROC.c_inst
        g_inst = GEMROC.g_inst
        test_c = AN_CLASS.analisys_conf(GEM_COM, c_inst, g_inst)
        test_r = AN_CLASS.analisys_read(GEM_COM, c_inst)
        test_c.thr_preconf()
        if TIGER == -1:
            first = 0
            last = 8
        else:
            first = TIGER
            last = TIGER + 1
        GEMROC_ID = GEM_COM.GEMROC_ID
        if branch == 1:
            test_r.thr_scan_matrix = test_c.thr_conf_using_GEMROC_COUNTERS_progress_bar(test_r, first, last, pipe_out, print_to_screen=False)
        else:
            test_r.thr_scan_matrix = test_c.thr_conf_using_GEMROC_COUNTERS_progress_bar(test_r, first, last, pipe_out, print_to_screen=False, branch=2)

        test_r.make_rate()
        test_r.normalize_rate(first, last)

        if branch == 1:
            test_r.colorPlot(GEM_COM.Tscan_folder + sep + "GEMROC{}".format(GEMROC_ID) + sep + "GEMROC{}".format(GEMROC_ID) + "rate", first, last, True)
            test_r.colorPlot(GEM_COM.Tscan_folder + sep + "GEMROC{}".format(GEMROC_ID) + sep + "GEMROC{}".format(GEMROC_ID) + "conteggi", first, last)
            test_r.save_scan_on_file(branch=1)

        else:
            test_r.colorPlot(GEM_COM.Escan_folder + sep + "GEMROC{}".format(GEMROC_ID) + sep + "GEMROC{}".format(GEMROC_ID) + "rate", first, last, True)
            test_r.colorPlot(GEM_COM.Escan_folder + sep + "GEMROC{}".format(GEMROC_ID) + sep + "GEMROC{}".format(GEMROC_ID) + "conteggi", first, last)
            test_r.save_scan_on_file(branch=2)

        # test_r.normalize_rate( first,int(input_array[2]))
        if branch == 1:
            test_r.global_sfit(first, last, branch=1)
        else:
            test_r.global_sfit(first, last, branch=2)

        print ("GEMROC {} done".format(GEMROC_ID))
        pipe_out.send(0)

    def auto_tune(self, GEMROC_num, TIGER_num, iter):  # if GEMROC num=-1--> To all GEMROC, if TIGER_num=-1 --> To all TIGERs
        self.bar_win = Toplevel(self.main_window)
        self.bar_win.focus_set()  # set focus on the ProgressWindow
        self.bar_win.grab_set()
        progress_bars = []
        progress_list = []
        dict = {}

        Label(self.bar_win, text="Auto tune completition").pack()
        if GEMROC_num == -1:
            dict = self.GEMROC_reading_dict.copy()
        else:
            dict["{}".format(GEMROC_num)] = self.GEMROC_reading_dict[GEMROC_num]
        i = 0
        for number, GEMROC_number in dict.items():
            Label(self.bar_win, text='{}'.format(number)).pack()
            progress_list.append(IntVar())
            if TIGER_num == -1:
                maxim = 8 * iter
            else:
                maxim = iter
            progress_bars.append(Progressbar(self.bar_win, maximum=maxim, orient=HORIZONTAL, variable=progress_list[i], length=200, mode='determinate'))
            progress_bars[i].pack()

            i += 1
        process_list = []
        pipe_list = []
        i = 0
        for number, GEMROC_num in dict.items():
            pipe_in, pipe_out = Pipe()
            p = Process(target=self.auto_tune_process, args=(number, TIGER_num, pipe_out, iter))
            # pipe_in.send(progress_bars[i])
            process_list.append(p)
            pipe_list.append(pipe_in)
            p.start()
            i += 1
        while True:
            alive_list = []
            for process in process_list:
                alive_list.append(process.is_alive())
            if all(v == False for v in alive_list):
                break
            else:
                for progress, pipe in zip(progress_list, pipe_list):
                    try:
                        progress.set(pipe.recv())
                    except:
                        Exception("Can't acquire status")
                        # print ("Can't acquire status")
                    time.sleep(0.1)

                    self.bar_win.update()
                    # print progress.get()

        for process in process_list:
            if process.is_alive():
                process.join()
        self.bar_win.destroy()

        # else:
        #     GEMROC = self.GEMROC_reading_dict["GEMROC {}".format(GEMROC_num)]
        #     GEM_COM = GEMROC.GEM_COM
        #     c_inst = GEMROC.c_inst
        #     g_inst = GEMROC.g_inst
        #     test_r = (AN_CLASS.analisys_conf(GEM_COM, c_inst, g_inst))

    def auto_tune_process(self, number, TIGER, pipe_out, iter):
        GEMROC = self.GEMROC_reading_dict[number]
        GEM_COM = GEMROC.GEM_COM
        c_inst = GEMROC.c_inst
        g_inst = GEMROC.g_inst
        rate = int(self.rate.get())
        if TIGER != -1:
            test_r = AN_CLASS.analisys_read(GEM_COM, c_inst)

            auto_tune_C = AN_CLASS.analisys_conf(GEM_COM, c_inst, g_inst)
            GEM_COM.Load_VTH_fromfile(c_inst, TIGER, 2, 1, 0)
            print ("\nVth Loaded on TIGER {}".format(TIGER))
            auto_tune_C.fill_VTHR_matrix(3, 0, TIGER)

            auto_tune_C.thr_autotune_wth_counter_progress(TIGER, rate, test_r, pipe_out, iter, 0.03)
            # auto_tune_C.thr_autotune_wth_counter_progress(TIGER, rate, test_r,pipe_out, 2, 1)
            pipe_out.send(1)
            auto_tune_C.__del__()

            test_r.__del__()

        else:
            for T in range(0, 8):
                test_r = AN_CLASS.analisys_read(GEM_COM, c_inst)

                auto_tune_C = AN_CLASS.analisys_conf(GEM_COM, c_inst, g_inst)
                GEM_COM.Load_VTH_fromfile(c_inst, T, 2, 1, 0)
                print ("\nVth Loaded on TIGER {}".format(T))
                auto_tune_C.fill_VTHR_matrix(3, 0, T)

                auto_tune_C.thr_autotune_wth_counter_progress(T, rate, test_r, pipe_out, iter, 0.03)
                # auto_tune_C.thr_autotune_wth_counter_progress(T, rate, test_r, pipe_out,2, 1)

                auto_tune_C.__del__()

                test_r.__del__()

        GEMROC_ID = GEM_COM.GEMROC_ID
        # test_r.normalize_rate( first,int(input_array[2]))
        print("GEMROC {} done".format(GEMROC_ID))

    def TIGER_CHANNEL_configurator(self):
        self.dict_pram_list = self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].c_inst.Channel_cfg_list[int(self.showing_TIGER.get())][int(self.Channel_IN.get())].keys()
        self.third_row_frame.destroy()
        self.third_row_frame = Frame(self.conf_frame)
        self.third_row_frame.grid(row=2, column=0, sticky=NW, pady=4)
        single_use_frame = Frame(self.third_row_frame)
        single_use_frame.grid(row=1, column=0, sticky=W, pady=2)
        tasti = Frame(self.third_row_frame)
        tasti.grid(row=0, column=0, sticky=W, pady=2)
        Button(tasti, text='Read configuration', command=self.read_TIGER_channel).grid(row=0, column=1, sticky=W, pady=2)
        Button(tasti, text='Write configuration', command=self.write_CHANNEL_Handling).grid(row=0, column=2, sticky=W, pady=2)
        OptionMenu(tasti, self.all_channels, *["All Channels", "-"]).grid(row=0, column=3, sticky=W, pady=2)
        OptionMenu(tasti, self.all_TIGERs, *["All TIGERs", "-"]).grid(row=0, column=4, sticky=W, pady=2)
        OptionMenu(tasti, self.all_GEMROCs, *["All GEMROCs", "-"]).grid(row=0, column=5, sticky=W, pady=2)
        self.label_array = []
        self.field_array = []
        self.input_array = {}
        with open("lib" + sep + "keys" + sep + "channel_conf_file_keys", 'r') as f:
            i = 0
            j = 0
            lenght = len(f.readlines())
            # print lenght
            f.seek(0)
            Label(single_use_frame, text="Read").grid(row=1, column=1, sticky=W, pady=0, padx=2)
            Label(single_use_frame, text="To load").grid(row=1, column=2, sticky=W, pady=0, padx=2)
            Label(single_use_frame, text="Read").grid(row=1, column=4, sticky=W, pady=0, padx=2)
            Label(single_use_frame, text="To load").grid(row=1, column=5, sticky=W, pady=0, padx=2)

            for line in f.readlines():
                line = line.rstrip('\n')
                self.field_array.append(Label(single_use_frame, text='-'))
                if line in self.dict_pram_list:
                    # print (self.dict_pram_list)
                    self.input_array[line] = (Entry(single_use_frame, width=3))
                self.label_array.append(Label(single_use_frame, text=line))

                if i < lenght / 2:
                    self.label_array[i].grid(row=i + 2, column=0, sticky=W, pady=0)
                    # print line
                    # print dict_pram_list
                    if str(line) in self.dict_pram_list:
                        self.input_array[line].grid(row=i + 2, column=2, sticky=W, pady=0)
                        j += 1
                    self.field_array[i].grid(row=i + 2, column=1, sticky=W, pady=0)
                else:
                    self.label_array[i].grid(row=i + 2 - lenght / 2, column=3, sticky=W, pady=0)
                    if line in self.dict_pram_list:
                        self.input_array[line].grid(row=i + 2 - lenght / 2, column=5, sticky=W, pady=0)
                        j += 1
                    self.field_array[i].grid(row=i + 2 - lenght / 2, column=4, sticky=W, pady=0)

                i += 1
            thr_target = StringVar(self.third_row_frame)
            thr_target.set("This TIGER")
            saveframe = Frame(self.third_row_frame)
            saveframe.grid(row=4, column=0, sticky=W, pady=2)
            Button(saveframe, text="Save", command=self.SAVE).pack(side=LEFT)
            Button(saveframe, text="Load", command=self.LOAD).pack(side=LEFT)
            self.LOAD_ON = Button(saveframe, text="Load on TIGERs (loaded file)", command=self.LOAD_on_TIGER, state='disable')
            self.LOAD_ON.pack(side=LEFT)
            thr_frame = Frame(self.third_row_frame)
            thr_frame.grid(row=3, column=0, sticky=W, pady=2)
            Label(thr_frame, text="Sigma T").pack(side=LEFT)
            self.thr_sigma_T = Entry(thr_frame, width=2)
            self.thr_sigma_T.pack(side=LEFT)
            Label(thr_frame, text="Sigma E").pack(side=LEFT)
            self.thr_sigma_E = Entry(thr_frame, width=2)
            self.thr_sigma_E.pack(side=LEFT)
            OptionMenu(thr_frame, thr_target, *["This TIGER", "All TIGERs", "All TIGERs in all GEMROCs"]).pack(side=LEFT)
            Button(thr_frame, text="Load scan threshold", command=lambda: self.load_thr_Handling(thr_target, "scan")).pack(side=LEFT)
            Button(thr_frame, text="Load auto threshold", command=lambda: self.load_thr_Handling(thr_target, "auto")).pack(side=LEFT)
            Button(thr_frame, text="Launch THR scan on this TIGER", command=lambda: self.thr_Scan(self.showing_GEMROC.get(), int(self.showing_TIGER.get()))).pack(side=LEFT)

    def TIGER_GLOBAL_configurator(self):
        self.third_row_frame.destroy()
        self.third_row_frame = Frame(self.conf_frame)
        self.third_row_frame.grid(row=2, column=0, sticky=NW, pady=4)
        single_use_frame = Frame(self.third_row_frame)
        single_use_frame.grid(row=1, column=0, sticky=W, pady=2)
        tasti = Frame(self.third_row_frame)
        tasti.grid(row=0, column=0, sticky=W, pady=2)
        Button(tasti, text='Read configuration', command=self.read_TIGER_global).grid(row=0, column=1, sticky=W, pady=2)
        Button(tasti, text='Write configuration', command=self.write_TIGER_GLOBAL).grid(row=0, column=2, sticky=W, pady=2)
        Button(tasti, text='Write configuration to all TIGERs on this GEMROC', command=self.write_TIGER_GLOBAL_allGEM).grid(row=0, column=3, sticky=W, pady=2)
        Button(tasti, text='Write configuration to all TIGERs', command=self.write_TIGER_GLOBAL_allsystem).grid(row=0, column=4, sticky=W, pady=2)
        self.label_array = []
        self.field_array = []
        self.input_array = []
        with open("lib" + sep + "keys" + sep + "global_conf_file_keys", 'r') as f:
            i = 0
            lenght = len(f.readlines())
            # print lenght
            f.seek(0)
            Label(single_use_frame, text="Read").grid(row=1, column=1, sticky=W, pady=0)
            Label(single_use_frame, text="To load").grid(row=1, column=2, sticky=W, pady=0)
            Label(single_use_frame, text="Read").grid(row=1, column=4, sticky=W, pady=0)
            Label(single_use_frame, text="To load").grid(row=1, column=5, sticky=W, pady=0)

            for line in f.readlines():
                self.field_array.append(Label(single_use_frame, text='-'))
                self.input_array.append(Entry(single_use_frame, width=3))
                self.label_array.append(Label(single_use_frame, text=line))

                if i < lenght / 2:
                    self.label_array[i].grid(row=i + 2, column=0, sticky=W, pady=0)
                    self.input_array[i].grid(row=i + 2, column=2, sticky=W, pady=0)
                    self.field_array[i].grid(row=i + 2, column=1, sticky=W, pady=0)
                else:
                    self.label_array[i].grid(row=i + 2 - lenght / 2, column=3, sticky=W, pady=0)
                    self.input_array[i].grid(row=i + 2 - lenght / 2, column=5, sticky=W, pady=0)
                    self.field_array[i].grid(row=i + 2 - lenght / 2, column=4, sticky=W, pady=0)

                i += 1
        saveframe = Frame(self.third_row_frame)
        saveframe.grid(row=4, column=0, sticky=W, pady=2)
        Button(saveframe, text="Save", command=self.SAVE).pack(side=LEFT)
        Button(saveframe, text="Load", command=self.LOAD).pack(side=LEFT)

    def SAVE(self):
        if self.configure_MODE.get() == "Global Tiger configuration":
            File_name = tkFileDialog.asksaveasfilename(initialdir="." + sep + "conf" + sep + "saves", title="Select file name", filetypes=(("Global configuration saves", "*.gs"), ("all files", "*.*")))
            GEM_NAME = str(self.showing_GEMROC.get())
            self.GEMROC_reading_dict[GEM_NAME].g_inst.save_glob_conf(File_name)

        if self.configure_MODE.get() == "Channel Tiger configuration":
            File_name = tkFileDialog.asksaveasfilename(initialdir="." + sep + "conf" + sep + "saves", title="Select file name", filetypes=(("Channels configuration saves", "*.cs"), ("all files", "*.*")))
            GEM_NAME = str(self.showing_GEMROC.get())
            self.GEMROC_reading_dict[GEM_NAME].c_inst.save_ch_conf(File_name)

    def LOAD(self):
        if self.configure_MODE.get() == "Global Tiger configuration":
            GEM_NAME = str(self.showing_GEMROC.get())
            File_name = tkFileDialog.askopenfilename(initialdir="." + sep + "conf" + sep + "saves", title="Select file", filetypes=(("Global configuration saves", "*.gs"), ("all files", "*.*")))
            self.GEMROC_reading_dict[GEM_NAME].g_inst.load_glob_conf(File_name)

        if self.configure_MODE.get() == "Channel Tiger configuration":
            GEM_NAME = str(self.showing_GEMROC.get())
            File_name = tkFileDialog.askopenfilename(initialdir="." + sep + "conf" + sep + "saves", title="Select file", filetypes=(("Channels configuration saves", "*.cs"), ("all files", "*.*")))
            self.GEMROC_reading_dict[GEM_NAME].c_inst.load_ch_conf(File_name)
        self.LOAD_ON.config(state='normal')

    def LOAD_on_TIGER(self):
        GEMROC = self.showing_GEMROC.get()
        for T in range(0, 8):
            self.write_CHANNEL(self.GEMROC_reading_dict[GEMROC], T, 64, False)

    def LV_diag(self):
        self.third_row_frame.destroy()
        self.third_row_frame = Frame(self.conf_frame)
        self.third_row_frame.grid(row=2, column=0, sticky=NW, pady=4)
        single_use_frame = Frame(self.third_row_frame)
        single_use_frame.grid(row=0, column=0, sticky=W, pady=2)
        Button(single_use_frame, text='Read configuration', command=self.read_LV).grid(row=0, column=1, sticky=W, pady=2)
        Button(single_use_frame, text='Read diag status', command=self.read_diagn_dipram).grid(row=0, column=2, sticky=W, pady=2)
        Button(single_use_frame, text='Write default LV conf', command=self.write_default_LV_conf).grid(row=1, column=2, sticky=W, pady=2)

        self.field_array = []
        self.input_array = []
        self.label_array = []
        with open("lib" + sep + "keys" + sep + "LV_keys", 'r') as f:
            i = 0

            for line in f.readlines():
                self.label_array.append(Label(single_use_frame, text=line.rstrip('\n')))
                self.label_array[i].grid(row=i + 1, column=0, sticky=W, pady=1)
                self.field_array.append(Label(single_use_frame, text='-'))
                self.field_array[i].grid(row=i + 1, column=1, sticky=W, pady=1)
                i += 1

    def DAQ_configurator(self):
        self.third_row_frame.destroy()
        self.third_row_frame = Frame(self.conf_frame)
        self.third_row_frame.grid(row=2, column=0, sticky=NW, pady=4)
        single_use_frame = Frame(self.third_row_frame)
        single_use_frame.grid(row=0, column=0, sticky=W, pady=2)
        Button(single_use_frame, text='Read configuration', command=self.read_DAQ_CR).grid(row=0, column=1, sticky=W, pady=2)
        self.field_array = []
        self.input_array = []
        self.label_array = []
        with open("lib" + sep + "keys" + sep + "DAQ_cr_keys", 'r') as f:
            i = 0

            for line in f.readlines():
                self.label_array.append(Label(single_use_frame, text=line.rstrip('\n')))
                self.label_array[i].grid(row=i + 1, column=0, sticky=W, pady=1)
                self.field_array.append(Label(single_use_frame, text='-'))
                self.field_array[i].grid(row=i + 1, column=1, sticky=W, pady=1)
                self.input_array.append(Entry(single_use_frame, width="4"))
                self.input_array[i].grid(row=i + 1, column=2, sticky=W, pady=1)
                i += 1
        Label(single_use_frame, text="TP_repeat_burst_param").grid(row=i + 1, column=0, pady=1, sticky=W)
        Label(single_use_frame, text="---").grid(row=i + 1, column=1, pady=1, sticky=W)
        TP_repeat = Entry(single_use_frame, width="4", textvariable=self.TP_repeat)
        TP_repeat.grid(row=i + 1, column=2, pady=1, sticky=W)
        Label(single_use_frame, text="TP_Num_in_burst_param").grid(row=i + 2, column=0, pady=1, sticky=W)
        Label(single_use_frame, text="---").grid(row=i + 2, column=1, pady=1, sticky=W)
        TP_num = Entry(single_use_frame, width="4", textvariable=self.TP_num)
        TP_num.grid(row=i + 2, column=2, pady=1, sticky=W)
        # another_frame = Frame(self.third_row_frame)
        # another_frame.grid(row=0, column=1, sticky=W, pady=2)
        # Label(another_frame, text="Change configuration", font=("Courier", 20)).grid(row=0, column=0, columnspan=8, sticky=S, pady=5)
        # # modebut=Button(another_frame, text="Trigger matched",command= lambda : self.switch_mode(modebut))
        # # modebut.grid(row=1, column=1, sticky=W, pady=2)
        #
        # Label(another_frame, text="TCAM_Enable_pattern").grid(row=2, column=0, sticky=S, pady=0)
        # Label(another_frame, text="Periodic_FEB_TP_Enable_pattern").grid(row=3, column=0, sticky=S, pady=0)
        # Label(another_frame, text="TP_repeat_burst").grid(row=4, column=0, sticky=S, pady=0)
        # Label(another_frame, text="TP_Num_in_burst").grid(row=5, column=0, sticky=S, pady=0)
        # Label(another_frame, text="TL_nTM_ACQ_choice").grid(row=6, column=0, sticky=S, pady=0)
        # # Label(another_frame,text="Periodic_L1_Enable_BIT").grid(row=7, column=0,sticky=S, pady=0) #E' lo stesso di periodic FEB_TP_Enable pattern
        # Label(another_frame, text="Enab_Auto_L1_from_TP_bit_param").grid(row=8, column=0, sticky=S, pady=0)
        # Label(another_frame, text="Enable_DAQPause_Until_First_Trigger").grid(row=9, column=0, sticky=S, pady=0)
        # # Label(another_frame,text="DAQPause_Set").grid(row=10, column=0,sticky=S, pady=0)
        # # Label(another_frame,text="Tpulse_gen_w_ext_trigger_enable").grid(row=11, column=0,sticky=S, pady=0)
        # Label(another_frame, text="EXT_nINT_B3clk").grid(row=12, column=0, sticky=S, pady=0)
        #
        # self.IN1 = Entry(another_frame)
        # self.IN1.grid(row=2, column=1, sticky=S, pady=0)
        # self.IN2 = Entry(another_frame)
        # self.IN2.grid(row=3, column=1, sticky=S, pady=0)
        # self.IN3 = Entry(another_frame)
        # self.IN3.grid(row=4, column=1, sticky=S, pady=0)
        # self.IN4 = Entry(another_frame)
        # self.IN4.grid(row=5, column=1, sticky=S, pady=0)
        # self.IN5 = Entry(another_frame)
        # self.IN5.grid(row=6, column=1, sticky=S, pady=0)
        # # self.IN6=Entry(another_frame)
        # # self.IN6.grid(row=7, column=1,sticky=S, pady=0)
        # self.IN7 = Entry(another_frame)
        # self.IN7.grid(row=8, column=1, sticky=S, pady=0)
        # self.IN8 = Entry(another_frame)
        # self.IN8.grid(row=9, column=1, sticky=S, pady=0)
        # # self.IN9 = Entry(another_frame)
        # # self.IN9.grid(row=10, column=1, sticky=S, pady=0)
        # # self.IN10 = Entry(another_frame)
        # # self.IN10.grid(row=11, column=1, sticky=S, pady=0)
        # self.IN11 = Entry(another_frame)
        # self.IN11.grid(row=12, column=1, sticky=S, pady=0)

        Button(single_use_frame, text='Set', command=self.write_DAQ_CR).grid(row=0, column=2, sticky=W, pady=2)
        Button(single_use_frame, text='Set on all active GEMROCs', command=lambda: self.write_DAQ_CR(1)).grid(row=0, column=3, sticky=W, pady=2)
        I_love_frames = Frame(self.third_row_frame)
        I_love_frames.grid(row=2, column=1, sticky=W, pady=2)

        Button(I_love_frames, text="Sync Reset this GEMROC", command=lambda: self.Synch_reset(0)).pack(side=LEFT)
        self.Pause_state = Button(I_love_frames, text="GEMROC_paused", command=self.set_pause_mode)
        self.Clock_state = Button(I_love_frames, text="Internal clock", command=self.change_clock_mode)
        self.Acq_state = Button(I_love_frames, text="Trigger matched", command=self.change_acquisition_mode)
        self.check_clock_state()
        self.check_acq_state()
        self.check_pause_state()
        self.Clock_state.pack(side=LEFT)
        self.Pause_state.pack(side=LEFT)
        self.Acq_state.pack(side=LEFT)
        another0 = Frame(self.third_row_frame)
        another0.grid(row=0, column=1, sticky=W, pady=2)
        another1 = LabelFrame(another0)
        another1.grid(row=0, column=1, sticky=W, pady=2)
        Label(another1, text="Trigger window settings", font=("Courier", 20)).grid(row=0, column=0, columnspan=8, sticky=S, pady=5)

        Label(another1, text="L1_lat_B3clk_param").grid(row=1, column=2, sticky=S, pady=0)
        self.L1_field1 = Label(another1, text="---", width=4)
        self.L1_field1.grid(row=1, column=1, sticky=S, pady=0)
        self.L1_entry1 = Entry(another1, width=5)
        Label(another1, text="L1_win_upper_edge_offset_Tiger_clk").grid(row=1, column=0, sticky=S, pady=0)

        self.L1_entry1.grid(row=1, column=3, sticky=S, pady=0)

        Label(another1, text="TM_window_in_B3clk_param").grid(row=2, column=2, sticky=S, pady=0)
        self.L1_field2 = Label(another1, text="---", width=4)
        self.L1_field2.grid(row=2, column=1, sticky=S, pady=0)
        self.L1_entry2 = Entry(another1, width=5)
        Label(another1, text="L1_win_lower_edge_offset").grid(row=2, column=0, sticky=S, pady=0)

        self.L1_entry2.grid(row=2, column=3, sticky=S, pady=0)
        Button(another1, text='Set L1 windows (all GEMROCs)', command=self.set_L1_window).grid(row=3, column=2, pady=20, sticky=E, columnspan=8)

        another2 = Frame(another0)
        another2.grid(row=1, column=1, sticky=E, pady=2)

        Button(another2, text='Hard reset', width="10", command=lambda: self.hard_reset("False")).grid(row=3, column=2, pady=20, sticky=E, columnspan=8)

    def set_L1_window(self):
        for number, GEMROC in self.GEMROC_reading_dict.items():
            L1_lat_TIGER_clk_param = int(self.L1_entry1.get()) * 4  # default 358 <-> 8.6us
            TM_window_TIGER_clk_param = int(self.L1_entry2.get()) * 4  # default  66 <-> 1.6us
            L1_win_upper_edge_offset_Tiger_clk = int(L1_lat_TIGER_clk_param - (TM_window_TIGER_clk_param / 2))
            L1_win_lower_edge_offset_Tiger_clk = int(L1_lat_TIGER_clk_param + (TM_window_TIGER_clk_param / 2))
            GEMROC.GEM_COM.gemroc_DAQ_XX.DAQ_config_dict["L1_scan_window_UPPER_edge"] = L1_win_upper_edge_offset_Tiger_clk
            GEMROC.GEM_COM.gemroc_DAQ_XX.DAQ_config_dict["L1_scan_window_LOWER_edge"] = L1_win_lower_edge_offset_Tiger_clk
            GEMROC.GEM_COM.gemroc_DAQ_XX.DAQ_config_dict["L1_TM_extraction_latency"] = L1_lat_TIGER_clk_param
            GEMROC.GEM_COM.DAQ_set_with_dict()

    def hard_reset(self, to_all):
        if not to_all:
            GEMROC = self.GEMROC_reading_dict[self.showing_GEMROC.get()]
            GEMROC.GEM_COM.HARDReset_Send()
        else:
            for number, GEMROC in self.GEMROC_reading_dict.items():
                GEMROC.GEM_COM.HARDReset_Send()

    def check_clock_state(self):
        button = self.Clock_state
        for label, field in zip(self.label_array, self.field_array):
            if label.cget('text').split()[0] == "EXT_nINT_B3clk":
                if field.cget('text') == 1:
                    button['text'] = "External clock"
                    button['state'] = "normal"

                elif field.cget('text') == 0:
                    button['text'] = "Internal clock"
                    button['state'] = "normal"

                else:
                    button['text'] = "----------"
                    button['state'] = "disable"

                break

    def check_acq_state(self):
        button = self.Acq_state
        for label, field in zip(self.label_array, self.field_array):
            if label.cget('text').split()[0] == "TL_nTM_ACQ":
                if field.cget('text') == 1:
                    button['text'] = "Trigger-less"
                    button['state'] = "normal"

                elif field.cget('text') == 0:
                    button['text'] = "Trigger-Matched"
                    button['state'] = "normal"

                else:
                    button['text'] = "----------"
                    button['state'] = "disable"
                break

    def check_pause_state(self):
        button = self.Pause_state
        for label, field in zip(self.label_array, self.field_array):
            if label.cget('text').split()[0] == "Enable_DAQPause_Until_First_Trigger":
                if field.cget('text') == 1:
                    button['text'] = "Pause mode set, running"
                    button['state'] = "normal"

                    for label, field in zip(self.label_array, self.field_array):
                        if label.cget('text').split()[0] == "DAQPause_Flag":
                            if field.cget('text') == 1:
                                button['text'] = "Paused"
                                button['state'] = "normal"
                                break



                elif field.cget('text') == 0:
                    button['text'] = "Un-paused"
                    button['state'] = "normal"

                else:
                    button['text'] = "----------"
                    button['state'] = "disable"
                break

    def set_pause_mode(self, to_all=False, value=1):
        if to_all == False:
            GEMROC = self.GEMROC_reading_dict[self.showing_GEMROC.get()]
            DAQ_inst = GEMROC.GEM_COM.gemroc_DAQ_XX

            if self.Pause_state['text'] == "Paused":
                DAQ_inst.DAQ_config_dict["Enable_DAQPause_Until_First_Trigger"] = 0
                GEMROC.GEM_COM.DAQ_set_with_dict()

            else:
                DAQ_inst.DAQ_config_dict["Enable_DAQPause_Until_First_Trigger"] = 1
                DAQ_inst.DAQ_config_dict["DAQPause_Set"] = 0
                GEMROC.GEM_COM.DAQ_set_with_dict()
                self.Synch_reset()
                DAQ_inst.DAQ_config_dict["DAQPause_Set"] = 1
                GEMROC.GEM_COM.DAQ_set_with_dict()
                DAQ_inst.DAQ_config_dict["DAQPause_Set"] = 0
                GEMROC.GEM_COM.DAQ_set_with_dict()

            self.read_DAQ_CR()
            self.check_pause_state()
        if to_all == True:
            if value == 1:

                for number, GEMROC in self.GEMROC_reading_dict.items():
                    DAQ_inst = GEMROC.GEM_COM.gemroc_DAQ_XX
                    DAQ_inst.DAQ_config_dict["Enable_DAQPause_Until_First_Trigger"] = 1
                    DAQ_inst.DAQ_config_dict["DAQPause_Set"] = 0
                    GEMROC.GEM_COM.DAQ_set_with_dict()
                self.Synch_reset(1)
                for number, GEMROC in self.GEMROC_reading_dict.items():
                    DAQ_inst = GEMROC.GEM_COM.gemroc_DAQ_XX
                    DAQ_inst.DAQ_config_dict["DAQPause_Set"] = 1
                    GEMROC.GEM_COM.DAQ_set_with_dict()
                    DAQ_inst.DAQ_config_dict["DAQPause_Set"] = 0
                    GEMROC.GEM_COM.DAQ_set_with_dict()
            else:
                for number, GEMROC in self.GEMROC_reading_dict.items():
                    DAQ_inst = GEMROC.GEM_COM.gemroc_DAQ_XX
                    DAQ_inst.DAQ_config_dict["Enable_DAQPause_Until_First_Trigger"] = 0
                    DAQ_inst.DAQ_config_dict["DAQPause_Set"] = 0
                    GEMROC.GEM_COM.DAQ_set_with_dict()

    def change_clock_mode(self, to_all=0, value=0):
        if to_all == 0:
            GEMROC = self.GEMROC_reading_dict[self.showing_GEMROC.get()]
            DAQ_inst = GEMROC.GEM_COM.gemroc_DAQ_XX

            if self.Clock_state['text'] == "Internal clock":
                DAQ_inst.DAQ_config_dict["EXT_nINT_B3clk"] = 1

            else:
                DAQ_inst.DAQ_config_dict["EXT_nINT_B3clk"] = 0
            GEMROC.GEM_COM.DAQ_set_with_dict()

            self.read_DAQ_CR()
            self.check_clock_state()

        if to_all == 1:
            for number, GEMROC in self.GEMROC_reading_dict.items():
                DAQ_inst = GEMROC.GEM_COM.gemroc_DAQ_XX
                DAQ_inst.DAQ_config_dict["EXT_nINT_B3clk"] = value
                GEMROC.GEM_COM.DAQ_set_with_dict()

    def change_acquisition_mode(self, to_all=False, value=1):  # value=1, TL
        if to_all == 0:
            GEMROC = self.GEMROC_reading_dict[self.showing_GEMROC.get()]
            DAQ_inst = GEMROC.GEM_COM.gemroc_DAQ_XX

            if self.Acq_state['text'] == "Trigger-less":
                DAQ_inst.DAQ_config_dict["TL_nTM_ACQ"] = 0
            else:
                DAQ_inst.DAQ_config_dict["TL_nTM_ACQ"] = 1
            GEMROC.GEM_COM.DAQ_set_with_dict()

            self.read_DAQ_CR()
            self.check_acq_state()
        if to_all == 1:
            for number, GEMROC in self.GEMROC_reading_dict.items():
                DAQ_inst = GEMROC.GEM_COM.gemroc_DAQ_XX
                DAQ_inst.DAQ_config_dict["TL_nTM_ACQ"] = value
                GEMROC.GEM_COM.DAQ_set_with_dict()

    def switch_mode(self, modebut):
        if modebut['text'] == "Trigger matched":
            modebut['text'] = "Trigger less"
        elif modebut['text'] == "Trigger less":
            modebut['text'] = "Trigger matched"

    def write_DAQ_CR(self, to_all=0):

        if to_all == 1:

            for i, j in self.GEMROC_reading_dict.items():
                # print "ID:{} Istance {}".format(i,j)

                for G in range(0, len(self.label_array)):
                    label = self.label_array[G]
                    entry = self.input_array[G]
                    if label['text'] not in (("GEMROC", "UDP_DATA_DESTINATION_IPADDR", "UDP_DATA_DESTINATION_IPPORT", "B3Clk_sim_en")):
                        DAQ_inst = j.GEM_COM.gemroc_DAQ_XX
                        DAQ_inst.DAQ_config_dict[label['text']] = int(entry.get())
                        DAQ_inst.DAQ_config_dict['number_of_repetitions'] = ((int(self.TP_repeat.get()) & 0X1) << 9) + int(self.TP_num.get())

                        j.GEM_COM.DAQ_set_with_dict()


        else:
            for i in range(0, len(self.label_array)):
                label = self.label_array[i]
                entry = self.input_array[i]
                DAQ_inst = self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.gemroc_DAQ_XX
                DAQ_inst.DAQ_config_dict[label['text']] = int(entry.get())
                DAQ_inst.DAQ_config_dict['number_of_repetitions'] = ((int(self.TP_repeat.get()) & 0X1) << 9) + int(self.TP_num.get())

            self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.DAQ_set_with_dict()

    def read_LV(self):
        command_reply = self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.Read_GEMROC_LV_CfgReg()
        L_array = array.array('I')
        L_array.fromstring(command_reply)
        L_array.byteswap()
        read_dict = {
            "OVT_LIMIT_FEB3": ((L_array[1] >> 22) & 0xFF),
            "D_OVV_LIMIT_FEB3": ((L_array[1] >> 13) & 0x1FF),
            "D_OVC_LIMIT_FEB3": ((L_array[1] >> 4) & 0x1FF),
            "OVT_LIMIT_FEB2": ((L_array[2] >> 22) & 0xFF),
            "D_OVV_LIMIT_FEB2": ((L_array[2] >> 13) & 0x1FF),
            "D_OVC_LIMIT_FEB2": ((L_array[2] >> 4) & 0x1FF),
            "OVT_LIMIT_FEB1": ((L_array[3] >> 22) & 0xFF),
            "D_OVV_LIMIT_FEB1": ((L_array[3] >> 13) & 0x1FF),
            "D_OVC_LIMIT_FEB1": ((L_array[3] >> 4) & 0x1FF),
            "OVT_LIMIT_FEB0": ((L_array[4] >> 22) & 0xFF),
            "D_OVV_LIMIT_FEB0": ((L_array[4] >> 13) & 0x1FF),
            "D_OVC_LIMIT_FEB0": ((L_array[4] >> 4) & 0x1FF),
            "A_OVV_LIMIT_FEB3": ((L_array[5] >> 13) & 0x1FF),
            "A_OVC_LIMIT_FEB3": ((L_array[5] >> 4) & 0x1FF),
            "A_OVV_LIMIT_FEB2": ((L_array[6] >> 13) & 0x1FF),
            "A_OVC_LIMIT_FEB2": ((L_array[6] >> 4) & 0x1FF),
            "A_OVV_LIMIT_FEB1": ((L_array[7] >> 13) & 0x1FF),
            "A_OVC_LIMIT_FEB1": ((L_array[7] >> 4) & 0x1FF),
            "A_OVV_LIMIT_FEB0": ((L_array[8] >> 13) & 0x1FF),
            "A_OVC_LIMIT_FEB0": ((L_array[8] >> 4) & 0x1FF),
            "ROC_OVT_LIMIT": ((L_array[9] >> 24) & 0x3F),
            "XCVR_LPBCK_TST_EN": ((L_array[9] >> 18) & 0x1),
            "ROC_OVT_EN": ((L_array[9] >> 16) & 0x1),
            "FEB_OVT_EN_pattern": ((L_array[9] >> 12) & 0xF),
            "FEB_OVV_EN_pattern": ((L_array[9] >> 8) & 0xF),
            "FEB_OVC_EN_pattern": ((L_array[9] >> 4) & 0xF),
            "FEB_PWR_EN_pattern": ((L_array[9] >> 0) & 0xF),
            "TIMING_DLY_FEB3": ((L_array[10] >> 24) & 0x3F),
            "TIMING_DLY_FEB2": ((L_array[10] >> 16) & 0x3F),
            "TIMING_DLY_FEB1": ((L_array[10] >> 8) & 0x3F),
            "TIMING_DLY_FEB0": ((L_array[10] >> 0) & 0x3F)
        }
        for i in range(0, len(self.label_array)):
            label = self.label_array[i]
            field = self.field_array[i]
            field['text'] = read_dict[label['text']]

    def write_default_LV_conf(self):
        COMMAND_STRING = 'CMD_GEMROC_LV_CFG_WR'
        GEMROC = self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())]
        GEMROC.GEM_COM.gemroc_LV_XX.set_gemroc_cmd_code(COMMAND_STRING, 1)
        GEMROC.GEM_COM.gemroc_LV_XX.update_command_words()
        # keep gemroc_LV_XX.print_command_words()
        # keep gemroc_LV_XX.extract_parameters_from_UDP_packet()
        array_to_send = GEMROC.GEM_COM.gemroc_LV_XX.command_words

        command_echo = GEMROC.GEM_COM.send_GEMROC_CFG_CMD_PKT(COMMAND_STRING, array_to_send, GEMROC.GEM_COM.DEST_IP_ADDRESS,
                                                              GEMROC.GEM_COM.DEST_PORT_NO)

    def read_diagn_dipram(self, to_all=False):
        if to_all == False:
            self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.Access_diagn_DPRAM_read_and_log(1, 0)

    def read_DAQ_CR(self):
        command_reply = self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.Read_GEMROC_DAQ_CfgReg()
        # self.GEMROC_reading_dict[self.showing_GEMROC.get()].GEM_COM.display_log_GEMROC_DAQ_CfgReg_readback(command_reply, 1, 1)
        L_array = array.array('I')
        L_array.fromstring(command_reply)
        L_array.byteswap()
        # print(hex(L_array[0]))
        # print(hex(L_array[1]))
        # print(hex(L_array[2]))
        # print(hex(L_array[3]))
        # print(hex(L_array[4]))

        read_dict = {
            "GEMROC": ((L_array[0] >> 16) & 0X1f),
            "UDP_DATA_DESTINATION_IPADDR": ((L_array[0] >> 8) & 0xFF),
            "L1_TM_extraction_latency": ((L_array[1] >> 20) & 0x3FF),
            "TP_width": ((L_array[1] >> 16) & 0xF),
            "L1_scan_window_UPPER_edge": ((L_array[1] >> 0) & 0xFFFF),
            "L1_period_simulated": ((L_array[2] >> 20) & 0x3FF),
            "Tpulse_generation_w_L1Chk_enable": ((L_array[2] >> 17) & 0x1),
            "Periodic_L1En": ((L_array[2] >> 16) & 0x1),
            "L1_scan_window_LOWER_edge": ((L_array[2] >> 0) & 0xFFFF),
            "TP_period": ((L_array[3] >> 20) & 0x3FF),
            "Periodic_TP_EN_pattern": ((L_array[3] >> 16) & 0xF),
            "Enable_DAQPause_Until_First_Trigger": ((L_array[3] >> 15) & 0x1),
            "DAQPause_Set": ((L_array[3] >> 14) & 0x1),
            "Tpulse_generation_w_ext_trigger_enable": ((L_array[3] >> 13) & 0x1),
            "B3Clk_sim_en": ((L_array[2] >> 18) & 0x1),
            "EXT_nINT_B3clk": ((L_array[3] >> 12) & 0x1),
            "TL_nTM_ACQ": ((L_array[3] >> 11) & 0x1),
            "AUTO_L1_EN": ((L_array[3] >> 10) & 0x1),
            "AUTO_TP_EN": ((L_array[3] >> 9) & 0x1),
            "TP_Pos_nNeg": ((L_array[3] >> 8) & 0x1),
            "EN_TM_TCAM_pattern": ((L_array[3] >> 0) & 0xFF),
            "UDP_DATA_DESTINATION_IPPORT": ((L_array[4] >> 26) & 0xF),
            "number_of_repetitions": ((L_array[4] >> 16) & 0x3FF),
            "target_TCAM_ID": ((L_array[4] >> 8) & 0x3),
            "TO_ALL_TCAM_EN": ((L_array[4] >> 6) & 0x1),
            "DAQPause_Flag": ((L_array[4] >> 1) & 0x1),
            "top_daq_pll_unlocked_sticky_flag": ((L_array[4] >> 0) & 0x1)
        }
        for i in range(0, len(self.label_array)):
            label = self.label_array[i]
            field = self.field_array[i]
            entry = self.input_array[i]
            field['text'] = read_dict[label['text']]
            entry.delete(0, END)
            DAQ_inst = self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.gemroc_DAQ_XX
            entry.insert(END, DAQ_inst.DAQ_config_dict[label['text']])

        self.check_clock_state()
        self.check_pause_state()
        self.check_acq_state()

    def read_TIGER_global(self):
        TIGER_N = int(self.showing_TIGER.get())
        try:
            command_reply = self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.ReadTgtGEMROC_TIGER_GCfgReg(self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].g_inst, TIGER_N)
        except Exception as err:
            print ("Can't read configuration - ERROR: {}".format(err))
            self.error_led_update()
            return 0
        L_array = array.array('I')  # L is an array of unsigned long
        L_array.fromstring(command_reply)
        L_array.byteswap()
        for i in range(0, len(self.input_array)):
            self.input_array[i].delete(0, END)
            self.input_array[i].insert(END, self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].g_inst.Global_cfg_list[int(self.showing_TIGER.get())][self.label_array[i]['text'].rstrip('\n')])

        self.field_array[0]['text'] = ((L_array[1] >> 24) & 0x3)
        self.field_array[1]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[1] >> 16) & 0xF), 4))
        self.field_array[2]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[1] >> 8) & 0x1F), 5))
        self.field_array[3]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[1] >> 0) & 0x3F), 6))
        self.field_array[4]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[2] >> 24) & 0x3F), 6))
        self.field_array[5]['text'] = ((L_array[2] >> 16) & 0x3F)
        self.field_array[6]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[2] >> 8) & 0x1F), 5))
        self.field_array[7]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[2] >> 0) & 0xF), 4))
        self.field_array[8]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[3] >> 24) & 0x1F), 5))
        self.field_array[9]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[3] >> 16) & 0xF), 4))
        self.field_array[10]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[3] >> 8) & 0x3F), 6))
        self.field_array[11]['text'] = ((L_array[3] >> 0) & 0xF)
        self.field_array[12]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[4] >> 24) & 0x3F), 6))
        self.field_array[13]['text'] = ((L_array[4] >> 16) & 0x1F)
        self.field_array[14]['text'] = ((L_array[4] >> 8) & 0x1F)
        self.field_array[15]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[4] >> 0) & 0x3F), 6))
        self.field_array[16]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[5] >> 24) & 0x1F), 5))
        self.field_array[17]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[5] >> 16) & 0x1F), 5))
        self.field_array[18]['text'] = ((L_array[5] >> 8) & 0xF)
        self.field_array[19]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[5] >> 0) & 0x1F), 5))
        self.field_array[20]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[6] >> 24) & 0x1F), 5))
        self.field_array[21]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[6] >> 16) & 0x3F), 6))
        self.field_array[22]['text'] = ((L_array[6] >> 8) & 0x1)
        self.field_array[23]['text'] = ((L_array[6] >> 0) & 0x1)
        self.field_array[24]['text'] = ((L_array[7] >> 16) & 0x3)
        self.field_array[25]['text'] = ((L_array[7] >> 8) & 0xF)
        self.field_array[26]['text'] = ((L_array[7] >> 0) & 0x1)
        self.field_array[27]['text'] = ((L_array[8] >> 24) & 0x7)
        self.field_array[28]['text'] = ((L_array[8] >> 16) & 0x1)
        self.field_array[29]['text'] = ((L_array[8] >> 8) & 0x3)
        self.field_array[30]['text'] = ((L_array[8] >> 0) & 0x1F)
        self.field_array[31]['text'] = ((L_array[9] >> 24) & 0x1)
        self.field_array[32]['text'] = ((L_array[9] >> 16) & 0x3F)
        self.field_array[33]['text'] = ((L_array[9] >> 8) & 0x1)
        self.field_array[34]['text'] = ((L_array[9] >> 0) & 0x3)
        self.field_array[35]['text'] = ((L_array[10] >> 24) & 0x1)
        self.field_array[36]['text'] = ((L_array[10] >> 16) & 0x3)
        for input, field in zip(self.input_array, self.field_array):
            if int(input.get()) != int(field['text']):
                input.config({"background": "Red"})
            else:
                input.config({"background": "White"})

    def read_TIGER_channel(self):
        TIGER_N = int(self.showing_TIGER.get())
        command_reply = self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.ReadTgtGEMROC_TIGER_ChCfgReg(self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].c_inst, TIGER_N, int(self.Channel_IN.get()))

        L_array = array.array('I')  # L is an array of unsigned long
        L_array.fromstring(command_reply)
        L_array.byteswap()
        #
        for line in self.dict_pram_list:
            self.input_array[line].delete(0, END)
            self.input_array[line].insert(END, self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].c_inst.Channel_cfg_list[int(self.showing_TIGER.get())][int(self.Channel_IN.get())][line])

        self.field_array[0]['text'] = ((L_array[1] >> 24) & 0x1)
        self.field_array[1]['text'] = ((L_array[1] >> 16) & 0x7)
        self.field_array[2]['text'] = ((L_array[1] >> 8) & 0x7)
        self.field_array[3]['text'] = ((L_array[1] >> 0) & 0x1)
        self.field_array[4]['text'] = ((L_array[2] >> 24) & 0x1)
        self.field_array[5]['text'] = (L_array[2] >> 16) & 0xF
        self.field_array[6]['text'] = ((L_array[2] >> 8) & 0xF)
        self.field_array[7]['text'] = ((L_array[2] >> 0) & 0x1)
        self.field_array[8]['text'] = ((L_array[3] >> 24) & 0x3)
        self.field_array[9]['text'] = ((L_array[3] >> 16) & 0x1F)
        self.field_array[10]['text'] = ((L_array[3] >> 8) & 0x3F)
        self.field_array[11]['text'] = ((L_array[3] >> 0) & 0x3F)
        self.field_array[12]['text'] = ((L_array[4] >> 24) & 0x1)
        self.field_array[13]['text'] = ((L_array[4] >> 16) & 0x7F)
        self.field_array[14]['text'] = ((L_array[4] >> 8) & 0x7F)
        self.field_array[15]['text'] = ((L_array[4] >> 0) & 0x1)
        self.field_array[16]['text'] = ((L_array[5] >> 24) & 0x1)
        self.field_array[17]['text'] = ((L_array[5] >> 16) & 0x1)
        self.field_array[18]['text'] = ((L_array[5] >> 8) & 0x1)
        self.field_array[19]['text'] = ((L_array[5] >> 0) & 0x7)
        self.field_array[20]['text'] = ((L_array[6] >> 24) & 0x3)
        self.field_array[21]['text'] = ((L_array[6] >> 16) & 0x7)
        self.field_array[22]['text'] = ((L_array[6] >> 8) & 0x3)
        self.field_array[23]['text'] = ((L_array[6] >> 0) & 0x1F)
        self.field_array[24]['text'] = ((L_array[7] >> 24) & 0x1F)
        self.field_array[25]['text'] = ((L_array[7] >> 16) & 0xF)
        self.field_array[26]['text'] = ((L_array[7] >> 8) & 0x3F)
        self.field_array[27]['text'] = ((L_array[7] >> 0) & 0x3)
        self.field_array[28]['text'] = ((L_array[8] >> 24) & 0x3)
        self.field_array[29]['text'] = ((L_array[8] >> 16) & 0x3)

        i = 0
        # for key, input in self.input_array.iteritems():
        #     if int(input.get()) != int(self.field_array[i]['text']):
        #         input.config({"background": "Red"})
        #         i += 1
        #     else:
        #         input.config({"background": "White"})

    def write_TIGER_GLOBAL(self):
        GEMROC = self.showing_GEMROC.get()
        TIGER = int(self.showing_TIGER.get())
        i = 0
        for key in self.label_array:
            self.GEMROC_reading_dict['{}'.format(GEMROC)].g_inst.Global_cfg_list[TIGER][key['text'].rstrip('\n')] = int(self.input_array[i].get())
            i += 1
        write = self.GEMROC_reading_dict['{}'.format(GEMROC)].GEM_COM.Set_param_dict_global(self.GEMROC_reading_dict[GEMROC].g_inst, "TxDDR", TIGER, 0)
        read = self.GEMROC_reading_dict['{}'.format(GEMROC)].GEM_COM.ReadTgtGEMROC_TIGER_GCfgReg(self.GEMROC_reading_dict[GEMROC].g_inst, TIGER)
        try:
            self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.global_set_check(write, read)
        except:
            self.error_led_update()

    def write_TIGER_GLOBAL_allGEM(self):
        for TIGER in range(0, 8):
            i = 0
            for key in self.label_array:
                self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].g_inst.Global_cfg_list[int(TIGER)][key['text'].rstrip('\n')] = int(self.input_array[i].get())
                i += 1
            write = self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.Set_param_dict_global(self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].g_inst, "TxDDR", int(TIGER), 0)
            read = self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.ReadTgtGEMROC_TIGER_GCfgReg(self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].g_inst, int(TIGER))
            try:
                self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.global_set_check(write, read)
            except:
                self.error_led_update()

    def write_TIGER_GLOBAL_allsystem(self):
        for number, GEMROC in self.GEMROC_reading_dict.items():
            # print number
            for TIGER in range(0, 8):

                i = 0
                for key in self.label_array:
                    GEMROC.g_inst.Global_cfg_list[int(TIGER)][key['text'].rstrip('\n')] = int(self.input_array[i].get())
                    i += 1
                write = GEMROC.GEM_COM.Set_param_dict_global(GEMROC.g_inst, "TxDDR", int(TIGER), 0)
                read = GEMROC.GEM_COM.ReadTgtGEMROC_TIGER_GCfgReg(GEMROC.g_inst, int(TIGER))
                try:
                    GEMROC.GEM_COM.global_set_check(write, read)
                except:
                    self.error_led_update()

    def write_CHANNEL_Handling(self):
        if self.all_channels.get() == "All Channels":
            CHANNEL = 64
        else:
            CHANNEL = self.Channel_IN.get()
        if self.all_TIGERs.get() == "All TIGERs":
            TIGER_LIST = [0, 1, 2, 3, 4, 5, 6, 7]
        else:
            TIGER_LIST = [self.showing_TIGER.get()]
        for TIGER in TIGER_LIST:
            if self.all_GEMROCs.get() == "All GEMROCs":
                for number, GEMROC in self.GEMROC_reading_dict.items():
                    self.write_CHANNEL(GEMROC, TIGER, CHANNEL)
            else:
                print ("TIGER {}".format(TIGER))
                self.write_CHANNEL(self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())], TIGER, CHANNEL)

    def write_CHANNEL(self, GEMROC, TIGER, CHANNEL, update_fields=True):
        TIGER = int(TIGER)
        CHANNEL = int(CHANNEL)
        if update_fields == True:
            for key, elem in self.input_array.iteritems():
                if CHANNEL != 64:
                    GEMROC.c_inst.Channel_cfg_list[TIGER][CHANNEL][key] = int(elem.get())
                else:
                    for CH in range(0, 64):
                        GEMROC.c_inst.Channel_cfg_list[TIGER][CH][key] = int(elem.get())

        if CHANNEL != 64:

            write = GEMROC.GEM_COM.WriteTgtGEMROC_TIGER_ChCfgReg(GEMROC.c_inst, TIGER, CHANNEL)
            read = GEMROC.GEM_COM.ReadTgtGEMROC_TIGER_ChCfgReg(GEMROC.c_inst, TIGER, CHANNEL)
            try:
                GEMROC.GEM_COM.channel_set_check_GUI(write, read)
            except:
                self.error_led_update()
                print ("!!! ERROR IN CONFIGURATION  GEMROC {},TIGER {},CHANNEL {}!!!".format(GEMROC.GEM_COM.GEMROC_ID, TIGER, CHANNEL))
        else:
            failed = False

            for CH in range(0, 64):
                write = GEMROC.GEM_COM.WriteTgtGEMROC_TIGER_ChCfgReg(GEMROC.c_inst, TIGER, CH)
                read = GEMROC.GEM_COM.ReadTgtGEMROC_TIGER_ChCfgReg(GEMROC.c_inst, TIGER, CH)
                try:
                    GEMROC.GEM_COM.channel_set_check_GUI(write, read)
                except:
                    self.error_led_update()
                    failed = True
                    # print "!!! ERROR IN CONFIGURATION  GEMROC {},TIGER {},CHANNEL {}!!!".format(GEMROC.GEM_COM.GEMROC_ID, TIGER, CH)

            if failed:
                print ("!!! ERROR IN CHANNEL CONFIGURATION  GEMROC {},TIGER {}!!!".format(GEMROC.GEM_COM.GEMROC_ID, TIGER))

    def load_thr_Handling(self, thr_target_entry, mode):
        thr_target = thr_target_entry.get()
        if thr_target == "This TIGER":
            TIGER = int(self.showing_TIGER.get())
            self.load_thr(source=mode, sigma_T=int(self.thr_sigma_T.get()), sigma_E=int(self.thr_sigma_E.get()), first=TIGER, last=TIGER + 1)
            self.write_CHANNEL( self.GEMROC_reading_dict[self.showing_GEMROC.get()], TIGER, 64, False)
        if thr_target == "All TIGERs":
            self.load_thr(source=mode, sigma_T=int(self.thr_sigma_T.get()), sigma_E=int(self.thr_sigma_E.get()))
            for T in range(0,8):
                self.write_CHANNEL(self.GEMROC_reading_dict[self.showing_GEMROC.get()], T, 64, False)
        if thr_target == "All TIGERs in all GEMROCs":
            self.load_thr(source=mode, sigma_T=int(self.thr_sigma_T.get()), sigma_E=int(self.thr_sigma_E.get()), to_all=True)
            for number,gemroc in self.GEMROC_reading_dict.items():
                for T in range (0,8):
                    self.write_CHANNEL(gemroc, T,64)
    def load_thr(self, to_all=False, source="auto", sigma_T=3, sigma_E=2, offset=0, first=0, last=8):
        if not to_all:
            GEMROC = self.GEMROC_reading_dict[self.showing_GEMROC.get()]
            print (GEMROC)
            for T in range(first, last):
                if source == "auto":
                    GEMROC.GEM_COM.Load_VTH_fromfile_autotuned(GEMROC.c_inst, T)
                if source == "scan":
                    GEMROC.GEM_COM.Load_VTH_fromfile(GEMROC.c_inst, T, sigma_T, sigma_E, offset)
        else:
            for number, GEMROC in self.GEMROC_reading_dict.items():
                for T in range(first, last):
                    if source == "auto":
                        GEMROC.GEM_COM.Load_VTH_fromfile_autotuned(GEMROC.c_inst, T)
                    if source == "scan":
                        GEMROC.GEM_COM.Load_VTH_fromfile(GEMROC.c_inst, T, sigma_T, sigma_E, offset, send_command=False)

    def load_default_config(self):
        for number, GEMROC in self.GEMROC_reading_dict.items():
            for TIGER in range(0, 8):
                write = GEMROC.GEM_COM.Set_param_dict_global(GEMROC.g_inst, "TxDDR", int(TIGER), 0)
                read = GEMROC.GEM_COM.ReadTgtGEMROC_TIGER_GCfgReg(GEMROC.g_inst, int(TIGER))
                try:
                    GEMROC.GEM_COM.global_set_check(write, read)
                except:
                    self.error_led_update()
                self.write_CHANNEL(GEMROC, TIGER, 64, False)

    def Synch_reset(self, to_all=1):
        if to_all == 1:
            for number, GEMROC in self.GEMROC_reading_dict.items():
                GEMROC.GEM_COM.SynchReset_to_TgtFEB()
                GEMROC.GEM_COM.SynchReset_to_TgtTCAM()
                print ("{} reset".format(number))
        else:
            GEMROC = self.showing_GEMROC.get()
            self.GEMROC_reading_dict[GEMROC].GEM_COM.SynchReset_to_TgtFEB()
            self.GEMROC_reading_dict[GEMROC].GEM_COM.SynchReset_to_TgtTCAM()
            print ("{} reset".format(self.showing_GEMROC.get()))

    def error_led_update(self, update=1):
        self.ERROR_LED["image"] = self.icon_bad
        if update == 1:
            self.main_window.after(5000, lambda: self.error_led_update(2))
        if update == 2:
            self.ERROR_LED["image"] = self.icon_off

    def fast_configuration(self):
        self.power_on_FEBS()
        self.Synch_reset(1)
        self.change_acquisition_mode(True, 0)
        self.change_trigger_mode(value=0, to_all=True)
        self.load_thr(True, "scan", 3, 2, 0, 0, 8)
        self.specific_channel_fast_setting()
        self.load_default_config()
        self.Synch_reset(1)
        self.load_default_config()
        self.Synch_reset(1)
        self.Synch_reset(1)
        self.Synch_reset(1)
        self.set_pause_mode(True, 1)

    def change_trigger_mode(self, value, to_all=False):
        if to_all == True:
            for number, GEMROC in self.GEMROC_reading_dict.items():
                for T in range(0, 8):
                    for ch in range(0, 64):
                        GEMROC.c_inst.Channel_cfg_list[T][ch]["TriggerMode"] = value

    def specific_channel_fast_setting(self):
        for number, GEMROC in self.GEMROC_reading_dict.items():
            for T in range(0, 8):
                GEMROC.c_inst.Channel_cfg_list[T][62]["TriggerMode"] = 1

    def reactivate_TIGERS(self):
        for number, GEMROC in self.GEMROC_reading_dict.items():
            GEMROC.GEM_COM.gemroc_DAQ_XX.DAQ_config_dict["EN_TM_TCAM_pattern"] = 255
            GEMROC.GEM_COM.DAQ_set_register()


def character_limit(entry_text):
    try:
        if int(entry_text.get()) < 0:
            entry_text.set(0)
        if int(entry_text.get()) > 63:
            entry_text.set(63)
    except:
        entry_text.set("")
        "Not valid input in channel field"


class GEMROC_HANDLER:
    def __init__(self, GEMROC_ID):
        self.GEMROC_ID = GEMROC_ID
        self.GEM_COM = COM_class.communication(GEMROC_ID, 0)  # Create communication class
        default_g_inst_settigs_filename = self.GEM_COM.conf_folder + sep + "TIGER_def_g_cfg_2018.txt"
        self.g_inst = GEM_CONF.g_reg_settings(GEMROC_ID, default_g_inst_settigs_filename)
        default_ch_inst_settigs_filename = self.GEM_COM.conf_folder + sep + "TIGER_def_ch_cfg_2018.txt"
        self.c_inst = GEM_CONF.ch_reg_settings(GEMROC_ID, default_ch_inst_settigs_filename)

    def __del__(self):
        self.GEM_COM.__del__()

def sort_by_number(stringa1,stringa2):
    number1=find_number(stringa1)
    number2=find_number(stringa2)
    return number1-number2

def find_number(stringa):
    if type(stringa) != tuple:
        number = int(stringa.split(" ")[1])
    else:
        number = int(stringa[0].split(" ")[1])

    return number

Main_menu = menu()
Main_menu.runna()
