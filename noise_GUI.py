import os
import pickle
import sys
import time
import tkFileDialog
import ttk
from Tkinter import *
from multiprocessing import Process, Pipe
from ttk import Progressbar
import datetime
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from lib import GEM_ANALYSIS_classes as AN_CLASS, GEM_CONF_classes as GEM_CONF

OS = sys.platform
if OS == 'win32':
    sep = '\\'
elif OS == 'linux2':
    sep = '/'
else:
    print("ERROR: OS {} non compatible".format(OS))
    sys.exit()


class menu():
    def __init__(self, main_menu, gemroc_handler, main_menu_istance):
        self.error_window_main = Toplevel(main_menu)
        self.error_window_main.wm_title("Noise and thresholds")
        self.tabControl = ttk.Notebook(self.error_window_main)  # Create Tab Control

        noise_measure_ = noise_measure(self.error_window_main, gemroc_handler, self.tabControl, main_menu_istance)
        noise_measure_._insert("Noise measure")
        noise_measure_._init_windows()
        baseline_exit_ = baseline_exit(noise_measure, self.error_window_main, gemroc_handler, self.tabControl, main_menu_istance)
        baseline_exit_._insert("Baseline estimation")
        baseline_exit_._init_windows()
        self.tabControl.pack(expand=1, fill="both")  # Pack to make visible


class noise_measure():
    def __init__(self, main_window, gemroc_handler, tab_control, main_menu_istance):
        self.title = "Noise_measure"
        self.tabControl = tab_control
        self.main_window = main_window
        self.main_menu_istance = main_menu_istance
        self.scan_matrixs = {}
        self.fits = {}
        self.TPfits = {}
        self.covs = {}
        self.TPcovs = {}
        self.baseline = {}
        self.baseline_pos = {}
        self.TPbaseline = {}
        self.gaussians = {}
        self.efine_average = {}
        self.efine_stdv = {}
        self.sampling_scan = False
        self.GEMROC_reading_dict = gemroc_handler
        self.error_window = Frame(self.main_window)

    def _init_windows(self):
        Label(self.error_window, text=self.title, font=("Courier", 25)).grid(row=0, column=2, sticky=S, pady=4, columnspan=10)
        tot = len(self.GEMROC_reading_dict)

        self.TD_scan_result = {}
        number_list = []
        i = 0

        self.plotting_gemroc = 0
        self.plotting_TIGER = 0
        self.plotting_Channel = 0

        self.second_row_frame = Frame(self.error_window)
        self.second_row_frame.grid(row=2, column=1, sticky=S, pady=4, columnspan=10)

        self.T_with_tp = BooleanVar(self.error_window)
        self.E_with_tp = BooleanVar(self.error_window)
        self.T_without_tp = BooleanVar(self.error_window)
        self.E_without_tp = BooleanVar(self.error_window)
        self.save_in_txt = BooleanVar(self.error_window)
        self.save_in_txt.set(False)

        self.T_with_tp.set(True)
        self.E_with_tp.set(True)
        self.T_without_tp.set(True)
        self.E_without_tp.set(True)

        self.GEMROC_num = StringVar(self.error_window)
        self.TIGER_num_first = IntVar(self.error_window)
        self.TIGER_num_last = IntVar(self.error_window)
        self.CHANNEL_num_first = IntVar(self.error_window)
        self.CHANNEL_num_last = IntVar(self.error_window)
        self.scan_period = DoubleVar(self.error_window)
        self.TP_rate = IntVar(self.error_window)
        self.TP_rate.set(49000)
        self.number_of_TP = IntVar(self.error_window)
        self.number_of_TP.set(2)
        fields_optionsG = self.GEMROC_reading_dict.keys()
        fields_optionsG.append("All")
        OptionMenu(self.second_row_frame, self.GEMROC_num, *fields_optionsG).pack(side=LEFT)

        self.icon_worry = PhotoImage(file="." + sep + 'icons' + sep + "gufi" + sep + 'worry.gif')
        self.icon_OK = PhotoImage(file="." + sep + 'icons' + sep + "gufi" + sep + 'OK.gif')
        self.icon_cry = PhotoImage(file="." + sep + 'icons' + sep + "gufi" + sep + 'cry.gif')
        self.icon_sleep = PhotoImage(file="." + sep + 'icons' + sep + "gufi" + sep + 'sleep.gif')
        self.icon_mappa = PhotoImage(file="." + sep + 'icons' + sep + 'mappa_mini.gif')

        Label(self.second_row_frame, text='First TIGER   ').pack(side=LEFT)
        Entry(self.second_row_frame, width=4, textvariable=self.TIGER_num_first).pack(side=LEFT)

        Label(self.second_row_frame, text='Last TIGER   ').pack(side=LEFT)
        Entry(self.second_row_frame, width=4, textvariable=self.TIGER_num_last).pack(side=LEFT)

        Label(self.second_row_frame, text='First Channel  ').pack(side=LEFT)
        Entry(self.second_row_frame, width=4, textvariable=self.CHANNEL_num_first).pack(side=LEFT)

        Label(self.second_row_frame, text='Last Channel   ').pack(side=LEFT)
        Entry(self.second_row_frame, width=4, textvariable=self.CHANNEL_num_last).pack(side=LEFT)

        Label(self.second_row_frame, text='TP rate (Hz)   ').pack(side=LEFT)
        Entry(self.second_row_frame, textvariable=self.TP_rate, width=8, ).pack(side=LEFT)
        Label(self.second_row_frame, text='TP per frameword').pack(side=LEFT)
        fields_optionsr = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
        OptionMenu(self.second_row_frame, self.number_of_TP, *fields_optionsr).pack(side=LEFT)

        self.third_row = Frame(self.error_window)
        self.third_row.grid(row=3, column=1, sticky=S, pady=4, columnspan=10)
        if self.title == "Noise_measure":
            Button(self.third_row, text='Start TP', command=self.start_TP).pack(side=LEFT, padx=2)

        self.strart_button = Button(self.third_row, text='Threshold scan', command=self.noise_scan)
        self.strart_button.pack(side=LEFT, padx=2)
        self.strart_button = Button(self.third_row, text='Threshold scan on VTH2', command=lambda: self.noise_scan(True))
        self.strart_button.pack(side=LEFT, padx=2)
        Button(self.third_row, text="Save", command=self.SAVE).pack(side=LEFT, padx=2)
        Button(self.third_row, text="Load", command=self.LOAD).pack(side=LEFT, padx=2)
        Button(self.third_row, text="Fit", command=self.fit).pack(side=LEFT, padx=2)
        self.E_branch = BooleanVar(self.main_window)
        Checkbutton(self.third_row, text="Save for E-branch", variable=self.E_branch).pack(side=LEFT, padx=2)
        if self.title == "Noise_measure":
            Button(self.third_row, text="Save noise levels", command=self.SAVE_noise).pack(side=LEFT, padx=2)
            self.load_TP_button = Button(self.third_row, text="Load TP settings", command=self.load_TP_settings)
            self.load_TP_button.pack(side=LEFT, padx=2)
            Button(self.third_row, text="Sampling time scan", command=self.sampling_time_scan).pack(side=LEFT, padx=25)
            # Button(self.third_row, text="Save noise levels for thr setting", command=self.SAVE_noise_for_thr_setting).pack(side=LEFT,padx=2)
            Button(self.third_row, text="Periodic scan ", command=self.periodic_scan_win).pack(side=LEFT, padx=2)

            Button(self.third_row, text="Fast noise scan", command=self.fast_noise_scan).pack(side=LEFT, padx=2)
            Button(self.third_row, text="2D scan", command=self.squared_noise_scan).pack(side=LEFT, padx=2)
        if self.title == "Baseline estimation":
            Button(self.third_row, text="Save baseline levels for thr setting", command=self.SAVE_baseline).pack(side=LEFT, padx=2)

        # Button(self.third_row, text="Switch to TP distribution measurment", command=self.switch_to_tp_distr).pack(side=LEFT, padx=25)
        with open("." + sep + "lib" + sep + "mapping.pickle", "rb") as filein:
            self.mapping_matrix = pickle.load(filein)
        self.master_frame = Frame(self.error_window)
        self.master_frame.grid(row=4, column=2, sticky=N, pady=4, columnspan=1, rowspan=2)

        self.corn0 = Frame(self.master_frame)
        self.corn0.grid(row=4, column=0, sticky=S, pady=10, columnspan=1)
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

        self.usefullframe = Frame(self.corn0)
        self.usefullframe.grid(row=3, column=1, sticky=S, pady=4)
        Button(self.usefullframe, text='<', command=lambda: self.change_G_or_T(-1, "C")).grid(row=0, column=0, sticky=S, pady=4)

        self.corn2 = Frame(self.master_frame)
        self.corn2.grid(row=4, column=1, sticky=N, pady=10, padx=50, columnspan=1)
        Label(self.corn2, text='Strip', font=("Times", 18)).pack()
        self.strip = Label(self.corn2, text="S-0", width=20)
        self.strip.pack()

        Label(self.corn2, text='FEB', font=("Times", 18)).pack()
        self.FEB_label = Label(self.corn2, text="0", width=20)
        self.FEB_label.pack()
        Label(self.corn2, image=self.icon_mappa).pack()

        self.LBCH = Label(self.usefullframe, text='CHANNEL ', font=("Courier", 12))
        self.LBCH.grid(row=0, column=1, sticky=S, pady=4)
        self.CHentry = Entry(self.usefullframe, textvariable=self.plotting_Channel, width=4)
        self.CHentry.grid(row=0, column=2, sticky=S, pady=4)
        Button(self.usefullframe, text='Go', command=lambda: self.change_G_or_T(1, "GO")).grid(row=0, column=3, sticky=S, pady=4)
        Button(self.usefullframe, text='>', command=lambda: self.change_G_or_T(1, "C")).grid(row=0, column=4, sticky=S, pady=4)
        if self.title == "Noise_measure":
            self.gufo = Label(self.corn0, image=self.icon_sleep)
            self.gufo.grid(row=4, column=1, sticky=S, pady=4)
        self.corn1 = Frame(self.error_window)
        self.corn1.grid(row=5, column=6, sticky=S, pady=4, columnspan=10)

        # Plot
        x = np.arange(0, 64)
        v = np.zeros((64))

        self.fig = Figure(figsize=(9, 7))
        self.plot_rate = self.fig.add_subplot(111)
        self.scatter, = self.plot_rate.plot(x, v, 'r+', label="data")

        self.plot_rate.set_title("TIGER {}, GEMROC {}".format(self.plotting_TIGER, self.plotting_gemroc))
        self.plot_rate.set_ylabel("Rate [Hz]", fontsize=14)
        self.plot_rate.set_xlabel("Threshold", fontsize=14)
        self.plot_rate.ticklabel_format(style='sci', scilimits=(-3, 4), axis='both')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.corn1)
        self.canvas.get_tk_widget().pack(side=BOTTOM)
        self.canvas.draw()
        self.canvas.flush_events()
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.corn1)
        self.toolbar.draw()
        self.line_list = []
        # for number, GEMROC_number in self.GEMROC_reading_dict.items():
        #     print number

        for key in self.GEMROC_reading_dict.keys():
            number = key
            self.scan_matrixs[number] = np.zeros((8, 64, 64))

            self.baseline[number] = {}
            self.TP_settings = {}
            self.baseline_pos[number] = {}
            self.efine_average[number] = {}
            self.efine_stdv[number] = {}
            for T in range(0, 8):

                self.baseline[number]["TIG{}".format(T)] = {}

                self.TP_settings["TIG{}".format(T)] = {}
                self.baseline_pos[number]["TIG{}".format(T)] = {}

                self.efine_average[number]["TIG{}".format(T)] = {}
                self.efine_stdv[number]["TIG{}".format(T)] = {}
                for ch in range(0, 64):
                    # self.gaussians[number]["TIG{}".format(T)]["CH{}".format(ch)]=(0,0,0,0)

                    self.baseline[number]["TIG{}".format(T)]["CH{}".format(ch)] = ["Fail", "Fail", "Fail"]
                    self.baseline_pos[number]["TIG{}".format(T)]["CH{}".format(ch)] = (0, 0, 0)
                    self.efine_average[number]["TIG{}".format(T)]["CH{}".format(ch)] = []
                    self.efine_stdv[number]["TIG{}".format(T)]["CH{}".format(ch)] = []
        for numb in range(0, 22):
            number = "GEMROC {}".format(numb)
            self.fits[number] = {}
            self.TPfits[number] = {}
            self.covs[number] = {}
            self.TPcovs[number] = {}
            for T in range(0, 8):
                self.fits[number]["TIG{}".format(T)] = {}
                self.covs[number]["TIG{}".format(T)] = {}
                self.TPcovs[number]["TIG{}".format(T)] = {}
                self.TPfits[number]["TIG{}".format(T)] = {}
                for ch in range(0, 64):
                    self.fits[number]["TIG{}".format(T)]["CH{}".format(ch)] = (0, 0, 1, 1, 0, 0)
                    self.covs[number]["TIG{}".format(T)]["CH{}".format(ch)] = np.zeros((6, 6))
                    self.TPcovs[number]["TIG{}".format(T)]["CH{}".format(ch)] = np.zeros((3, 3))
                    self.TPfits[number]["TIG{}".format(T)]["CH{}".format(ch)] = ["Fail", "Fail", "Fail"]

    def _insert(self, name):
        self.tabControl.add(self.error_window, text=name)  # Add the tab

    def fast_noise_scan(self, log=False):
        # Tbranch test pulses
        logfile = "periodic_noise_scan" + sep + "scan_log.txt"
        if log:
            with open(logfile, 'a+') as fi:
                fi.write("{} Starting scan cycle\n".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
        self.start_TP()

        if self.T_with_tp.get():

            self.log_T(init=True, inbranch="T")

            with open(logfile, 'a+') as fi:
                fi.write("{} Scanning branch T with TP\n".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
            self.load__fast_TP_settings()
            self.noise_scan()
            self.unload_TP_settings()
            File_name = "periodic_noise_scan" + sep + "T_branch_with_TP_{}".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))

            if not self.save_in_txt.get():
                with  open(File_name + ".ns", 'wb') as f:
                    pickle.dump(self.scan_matrixs, f)
            else:
                self.save_txt(File_name + ".txt")

            with open(logfile, 'a+') as fi:
                fi.write("{} Finished scan branch T with TP\n".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
            self.log_T(init=False, inbranch="T")

        if self.E_with_tp.get():
            self.log_T(init=True, inbranch="E")

            with open(logfile, 'a+') as fi:
                fi.write("{} Scanning branch E with TP\n".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
            self.load__fast_TP_settings(branch="E")
            self.noise_scan(True)
            self.unload_TP_settings()
            File_name = "periodic_noise_scan" + sep + "E_branch_with_TP_{}".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))

            if not self.save_in_txt.get():
                with  open(File_name + ".ns", 'wb') as f:
                    pickle.dump(self.scan_matrixs, f)
            else:
                self.save_txt(File_name + ".txt")

            with open(logfile, 'a+') as fi:
                fi.write("{} Finished scan E with TP\n".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
            self.log_T(init=False, inbranch="E")

        if self.T_without_tp.get():
            self.log_T(init=True, inbranch="T")

            with open(logfile, 'a+') as fi:
                fi.write("{} Scanning branch T without TP\n".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
            self.load__fast_TP_settings(branch="T", TP=False)
            self.noise_scan()
            self.unload_TP_settings()
            File_name = "periodic_noise_scan" + sep + "Baseline_T_{}".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))

            if not self.save_in_txt.get():
                with  open(File_name + ".ns", 'wb') as f:
                    pickle.dump(self.scan_matrixs, f)
            else:
                self.save_txt(File_name + ".txt")
            with open(logfile, 'a+') as fi:
                fi.write("{} Finished scan T without TP\n".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
            self.log_T(init=False, inbranch="T")

        if self.E_without_tp.get():
            self.log_T(init=True, inbranch="E")

            with open(logfile, 'a+') as fi:
                fi.write("{} Scanning branch E without TP\n".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
            self.load__fast_TP_settings(branch="E", TP=False)
            self.noise_scan(True)
            self.unload_TP_settings()
            File_name = "periodic_noise_scan" + sep + "Baseline_E_{}".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))

            if not self.save_in_txt.get():
                with  open(File_name + ".ns", 'wb') as f:
                    pickle.dump(self.scan_matrixs, f)
            else:
                self.save_txt(File_name + ".txt")
            with open(logfile, 'a+') as fi:
                fi.write("{} Finished scan E without TP\n".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
            self.log_T(init=False, inbranch="E")

    def periodic_scan_win(self):
        per_wind = Toplevel(self.error_window)
        per_wind.wm_title("Periodic scan")
        first_row = Frame(per_wind)
        first_row.grid(row=0, column=1, sticky=S, pady=4)
        second_row = Frame(per_wind)
        second_row.grid(row=2, column=1, sticky=S, pady=4)
        Label(first_row, text='Scan every [hours]:   ').pack(side=LEFT)
        Entry(first_row, width=4, textvariable=self.scan_period).pack(side=LEFT)
        Button(first_row, text="Launch periodic scan", command=self.periodic_scan_start).pack(side=LEFT)
        Button(first_row, text="Launch continous scan", command=lambda: self.periodic_scan_start(True)).pack(side=LEFT)

        Button(first_row, text="Stop scan", command=self.periodic_scan_stop).pack(side=LEFT)
        Checkbutton(second_row, text="Scan TP T", variable=self.T_with_tp).pack(side=LEFT, padx=2)
        Checkbutton(second_row, text="Scan no TP T", variable=self.T_without_tp).pack(side=LEFT, padx=2)
        Checkbutton(second_row, text="Scan TP E", variable=self.E_with_tp).pack(side=LEFT, padx=2)
        Checkbutton(second_row, text="Scan no TP E", variable=self.E_without_tp).pack(side=LEFT, padx=2)
        Checkbutton(second_row, text="Save_txt", variable=self.save_in_txt).pack(side=LEFT, padx=2)

    def save_txt(self, filename):
        """
        To save scans in TXT
        :param filename: 
        :return: 
        """
        with open(filename, 'w') as fi:

            GEMROC_n = self.GEMROC_num.get()
            dictio = {}
            if GEMROC_n == "All":
                dictio = self.scan_matrixs.copy()
            else:
                dictio["{}".format(GEMROC_n)] = self.scan_matrixs[GEMROC_n]

            for key in sorted(dictio.keys(), cmp=sort_by_number):
                for T in range(0, 8):
                    for ch in range(0, 64):
                        for vth in range(0, 64):
                            fi.write("{}\n".format(self.scan_matrixs[key][T][ch][vth]))

    def periodic_scan_start(self, cont=False):
        self.periodic_scan_process = Process(target=self.periodic_scan_processer(cont))
        self.periodic_scan_process.run()

    def periodic_scan_processer(self, cont=False):
        self.running = True
        while self.running:
            print ("Launching scan")
            self.fast_noise_scan(log=True)

            if self.running:
                if not cont:
                    print ("Scan finisched, waiting {} hours".format(self.scan_period.get()))
                if cont:
                    time.sleep(2)
                else:
                    time.sleep(int(self.scan_period.get()))

    def log_T(self, init, inbranch):
        """
         Save the temperature (avoiding the bug)
        :param init:
        :param branch:
        :return:
        """

        T_lof_filename = "periodic_noise_scan" + sep + "temp_log.txt"
        GEMROC_n = self.GEMROC_num.get()

        if GEMROC_n == "All":
            return
        GEMROC = self.GEMROC_reading_dict[GEMROC_n]
        IVT_dict = GEMROC.GEM_COM.save_IVT()
        date = datetime.datetime.now().strftime("%d/%m")
        hour = datetime.datetime.now().strftime("%H:%M")
        branch = inbranch
        itemp0 = IVT_dict['status']['FEB0']["TEMP[degC]"]
        itemp1 = IVT_dict['status']['FEB1']["TEMP[degC]"]
        itemp2 = IVT_dict['status']['FEB2']["TEMP[degC]"]
        itemp3 = IVT_dict['status']['FEB3']["TEMP[degC]"]
        if init:
            endl = "	"
        else:
            endl = "\n"

        with open(T_lof_filename, 'a') as T_log_file:
            T_log_file.write("{0}	{1}	{2}	{3:.1f}	{4:.1f}	{5:.1f}	{6:.1f}{7}".format(date, hour, branch, itemp0, itemp1, itemp2, itemp3, endl))

        self.main_menu_istance.power_off_FEBS()
        time.sleep(1)
        self.main_menu_istance.power_on_FEBS()
        self.main_menu_istance.load_default_config(set_check=False)

    def periodic_scan_stop(self):
        self.running = False
        print ("Scan stopped".format(self.scan_period.get()))

    def squared_noise_scan(self):
        """
        Scans both threshold at the same time (one channel)
        :return:
        """
        GEMROC_n = self.GEMROC_num.get()
        dictio = {}
        dictio["{}".format(GEMROC_n)] = self.GEMROC_reading_dict[GEMROC_n]
        for number, GEMROC_number in dictio.items():
            GEMROC = self.GEMROC_reading_dict[number]
            GEM_COM = GEMROC.GEM_COM
            c_inst = GEMROC.c_inst
            g_inst = GEMROC.g_inst
            test_c = AN_CLASS.analisys_conf(GEM_COM, c_inst, g_inst)
            first = self.TIGER_num_first.get()
            firstch = self.CHANNEL_num_first.get()
            test_c.both_vth_scan(first, firstch)

    def noise_scan(self, vth2=False):  # if GEMROC num=-1--> To all GEMROC, if TIGER_num=-1 --> To all TIGERs
        self.bar_win = Toplevel(self.error_window)
        # self.bar_win.focus_set()  # set focus on the ProgressWindow
        # self.bar_win.grab_set()
        progress_bars = []
        progress_list = []
        dictio = {}
        GEMROC_n = self.GEMROC_num.get()
        Label(self.bar_win, text="Threshold Scan completition").pack()

        if GEMROC_n == "All":
            dictio = self.GEMROC_reading_dict.copy()
        else:
            dictio["{}".format(GEMROC_n)] = self.GEMROC_reading_dict[GEMROC_n]
        i = 0
        for number, GEMROC_number in dictio.items():
            Label(self.bar_win, text='{}'.format(number)).pack()
            progress_list.append(IntVar())
            maxim = (((self.CHANNEL_num_last.get() - self.CHANNEL_num_first.get()) + 1) * (self.TIGER_num_last.get() - self.TIGER_num_first.get() + 1)) * 64
            progress_bars.append(Progressbar(self.bar_win, maximum=maxim, orient=HORIZONTAL, variable=progress_list[i], length=200, mode='determinate'))
            progress_bars[i].pack()

            i += 1
        process_list = []
        pipe_list = []
        i = 0
        for number, GEMROC_num in dictio.items():
            pipe_in, pipe_out = Pipe()
            p = Process(target=self.noise_scan_process, args=(number, pipe_out, vth2))
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

                    self.bar_win.update()
                    time.sleep(0.1)
                    # print progress.get()

        for process in process_list:
            if process.is_alive():
                process.join()

        for number, GEMROC_num in dictio.items():
            filename = GEMROC_num.GEM_COM.Noise_folder + sep + "GEMROC{}".format(GEMROC_num.GEM_COM.GEMROC_ID) + sep + "scan_matrix"
            with  open(filename, 'rb') as f:
                self.scan_matrixs[number] = pickle.load(f)
        self.plotta()
        self.bar_win.destroy()

        # else:
        #     GEMROC = self.GEMROC_reading_dict["GEMROC {}".format(GEMROC_num)]
        #     GEM_COM = GEMROC.GEM_COM
        #     c_inst = GEMROC.c_inst
        #     g_inst = GEMROC.g_inst
        #     test_r = (AN_CLASS.analisys_conf(GEM_COM, c_inst, g_inst))

    def sampling_time_scan(self):
        self.sampling_scan = True
        GEMROC = self.GEMROC_reading_dict["{}".format(self.GEMROC_num.get())]
        GEM_COM = GEMROC.GEM_COM
        c_inst = GEMROC.c_inst
        test_r = AN_CLASS.analisys_read(GEM_COM, c_inst)
        first = self.TIGER_num_first.get()
        last = self.TIGER_num_last.get() + 1
        firstch = self.CHANNEL_num_first.get()
        lastch = self.CHANNEL_num_last.get() + 1
        GEMROC_ID = GEM_COM.GEMROC_ID

        for T in range(first, last):  # TIGER
            for J in range(firstch, lastch):  # Channel
                GEM_COM.Set_param_dict_channel(c_inst, "TP_disable_FE", T, J, 0)

                self.efine_average["GEMROC {}".format(GEMROC_ID)]["TIG{}".format(T)]["CH{}".format(J)] = []
                self.efine_average["GEMROC {}".format(GEMROC_ID)]["TIG{}".format(T)]["CH{}".format(J)] = []
                print ("TIGER {},Ch: {}".format(T, J))
                for i in range(5, 6):
                    # print "Min Max integ time = {}".format(i)
                    GEM_COM.Set_param_dict_channel(c_inst, "MaxIntegTime", T, J, i)
                    GEM_COM.Set_param_dict_channel(c_inst, "MinIntegTime", T, J, i)
                    GEM_COM.SynchReset_to_TgtFEB()
                    average, stdv, total = test_r.acquire_Efine(J, T, 0.5)
                    self.efine_average["GEMROC {}".format(GEMROC_ID)]["TIG{}".format(T)]["CH{}".format(J)].append(average)
                    self.efine_stdv["GEMROC {}".format(GEMROC_ID)]["TIG{}".format(T)]["CH{}".format(J)].append(stdv)
                GEM_COM.Set_param_dict_channel(c_inst, "TP_disable_FE", T, J, 1)

    def noise_scan_process(self, number, pipe_out, vth2):
        self.sampling_scan = False
        scan_matrix = np.zeros((8, 64, 64))
        GEMROC = self.GEMROC_reading_dict[number]
        GEM_COM = GEMROC.GEM_COM
        c_inst = GEMROC.c_inst
        g_inst = GEMROC.g_inst
        test_c = AN_CLASS.analisys_conf(GEM_COM, c_inst, g_inst)
        test_r = AN_CLASS.analisys_read(GEM_COM, c_inst)
        first = self.TIGER_num_first.get()
        last = self.TIGER_num_last.get() + 1
        firstch = self.CHANNEL_num_first.get()
        lastch = self.CHANNEL_num_last.get() + 1
        GEMROC_ID = GEM_COM.GEMROC_ID

        for T in range(first, last):  # TIGER
            for J in range(firstch, lastch):  # Channel
                for i in range(0, 64):  # THR
                    scan_matrix[T, J, i] = test_c.noise_scan_using_GEMROC_COUNTERS_progress_bar(T, J, i, False, vth2)

                    position = ((T - first) * (lastch - firstch)) * 64 + (J) * 64 + i
                    pipe_out.send(position)

        test_r.thr_scan_matrix = scan_matrix
        test_r.thr_scan_rate = scan_matrix * 10
        test_r.colorPlot(GEM_COM.Noise_folder + sep + "GEMROC{}".format(GEMROC_ID) + sep + "GEMROC {}".format(GEMROC_ID) + "rate", first, last, True)
        test_r.colorPlot(GEM_COM.Noise_folder + sep + "GEMROC{}".format(GEMROC_ID) + sep + "GEMROC {}".format(GEMROC_ID) + "conteggi", first, last)

        filename = GEM_COM.Noise_folder + sep + "GEMROC{}".format(GEMROC_ID) + sep + "scan_matrix"
        with  open(filename, 'wb') as f:
            pickle.dump(test_r.thr_scan_rate, f)

        print "GEMROC {} done".format(GEMROC_ID)
        position = (last * (lastch - firstch) + 1) + (lastch)
        pipe_out.send(position)

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
            self.plotting_Channel = int(self.CHentry.get())
        self.strip["text"] = self.mapping_matrix[self.plotting_gemroc][self.plotting_TIGER][self.plotting_Channel]
        self.FEB_label["text"] = int(round((self.plotting_TIGER + self.plotting_gemroc * 8) / 2))
        self.refresh_plot()

    def refresh_plot(self):
        self.LBGEM['text'] = 'GEMROC {}'.format(self.plotting_gemroc)
        self.LBTIG['text'] = 'TIGER {}'.format(self.plotting_TIGER)
        # self.LBCH['text'] = 'CHANNEL {}'.format(self.plotting_Channel)
        self.CHentry.delete(0, END)
        self.CHentry.insert(END, self.plotting_Channel)
        self.plotta()

    def start_TP(self):
        for number, GEMROC_number in self.GEMROC_reading_dict.items():
            GEMROC_number.GEM_COM.Soft_TP_generate()
            GEMROC_number.GEM_COM.gemroc_DAQ_XX.DAQ_config_dict['TL_nTM_ACQ'] = 0
            GEMROC_number.GEM_COM.gemroc_DAQ_XX.DAQ_config_dict['Periodic_TP_EN_pattern'] = 15
            GEMROC_number.GEM_COM.gemroc_DAQ_XX.DAQ_config_dict['number_of_repetitions'] = 512 + self.number_of_TP.get()
            period = 8190 / self.number_of_TP.get()
            GEMROC_number.GEM_COM.gemroc_DAQ_XX.DAQ_config_dict['TP_period'] = period
            GEMROC_number.GEM_COM.gemroc_DAQ_XX.DAQ_config_dict['TP_width'] = 10
            GEMROC_number.GEM_COM.DAQ_set_with_dict()

    def plotta(self):
        if self.sampling_scan == True:
            for number, GEMROC_number in self.GEMROC_reading_dict.items():
                if int(number.split()[1]) == int(self.plotting_gemroc):
                    GEMROC_ID = self.plotting_gemroc
                    self.plot_rate.set_title("ROC {},TIG {}, CH {} ".format(self.plotting_gemroc, self.plotting_TIGER, self.plotting_Channel))
                    y = (self.efine_average["GEMROC {}".format(GEMROC_ID)]["TIG{}".format(self.plotting_TIGER)]["CH{}".format(self.plotting_Channel)])
                    yerr = self.efine_stdv["GEMROC {}".format(GEMROC_ID)]["TIG{}".format(self.plotting_TIGER)]["CH{}".format(self.plotting_Channel)]
                    x = (range(0, 11))
                    # print "First fit {}".<format(parameters[2])
                    # print "Second fit {}".format(TPparameters[1])
                    # self.sampling_plot_figure = Figure(figsize=(6, 6))
                    # self.samplit_plot = self.sampling_plot_figure.add_subplot(111)
                    # self.samplit_plot_error, = self.samplit_plot.errorbar(x, y, yerr, 'r+')
                    #
                    # self.samplit_plot_error.set_title("TIGER {}, GEMROC {}".format(self.plotting_TIGER, self.plotting_gemroc))
                    # self.samplit_plot_error.set_ylabel("Efine", fontsize=14)
                    #
                    # self.samplit_plot_error.set_xlabel("Sampling time", fontsize=14)
                    # self.samplit_plot_error.ticklabel_format(style='sci', scilimits=(-3, 4), axis='both')
                    # self.canvas = FigureCanvasTkAgg(self.sampling_plot_figure, master=self.corn1)
                    # self.canvas.get_tk_widget().pack(side=BOTTOM)
                    # self.canvas.draw()
                    # self.canvas.flush_events()
                    # self.toolbar = NavigationToolbar2Tk(self.canvas, self.corn1)
                    # self.toolbar.draw()
                    self.scatter.set_ydata(y)
                    # self.plot_rate.set_ylim(top=y[len(y)-1]+1)
                    self.scatter.set_xdata(x)
                    self.plot_rate.set_xlim(right=len(x) + 1)

                    # base_parameters=self.gaussians[number]["TIG{}".format(self.plotting_TIGER)]["CH{}".format(self.plotting_Channel)][0]
                    # print "Chi1 {}".format(self.chi[number]["TIG{}".format(self.plotting_TIGER)]["CH{}".format(self.plotting_Channel)])
                    # print "Chi2 {}".format(self.TPchi[number]["TIG{}".format(self.plotting_TIGER)]["CH{}".format(self.plotting_Channel)])
                    self.canvas.draw()
                    self.canvas.flush_events()
                    break

        else:
            for number, GEMROC_number in self.GEMROC_reading_dict.items():
                if int(number.split()[1]) == int(self.plotting_gemroc):
                    for line in self.line_list:
                        try:
                            line.pop(0).remove()
                        except Exception as E:
                            pass
                    data = self.scan_matrixs[number][self.plotting_TIGER, self.plotting_Channel]
                    self.plot_rate.set_title("ROC {},TIG {}, CH {} ".format(self.plotting_gemroc, self.plotting_TIGER, self.plotting_Channel))
                    self.scatter.set_ydata(self.scan_matrixs[number][self.plotting_TIGER, self.plotting_Channel])
                    self.plot_rate.set_ylim(top=np.max(self.scan_matrixs[number][self.plotting_TIGER, self.plotting_Channel]) + np.max(self.scan_matrixs[number][self.plotting_TIGER, self.plotting_Channel]) * 0.2)
                    self.plot_rate.set_xlim(right=65)
                    print self.fits.keys()
                    parameters = self.fits[number]["TIG{}".format(self.plotting_TIGER)]["CH{}".format(self.plotting_Channel)]
                    TPparameters = self.TPfits[number]["TIG{}".format(self.plotting_TIGER)]["CH{}".format(self.plotting_Channel)]
                    Bas_parameters_fit = self.baseline[number]["TIG{}".format(self.plotting_TIGER)]["CH{}".format(self.plotting_Channel)]
                    bas_parameters_not_fit = self.baseline_pos[number]["TIG{}".format(self.plotting_TIGER)]["CH{}".format(self.plotting_Channel)]
                    self.line_list.append(self.plot_rate.plot(bas_parameters_not_fit, (data.max(), data.max(), data.max()), 'o'))
                    if parameters[0] != "Fail":
                        self.line_list.append(self.plot_rate.plot(np.arange(0, 64), AN_CLASS.double_error_func(np.arange(0, 64), *parameters), '-.', label="Preliminary fit", linewidth=1))

                    if TPparameters[0] != "Fail":
                        noise = round(AN_CLASS.convert_to_fC(TPparameters[1], 55), 2)

                        self.line_list.append(self.plot_rate.plot(np.arange(0, 64, 1.0), AN_CLASS.errorfunc(np.arange(0, 64, 1.0), *TPparameters), '-', label="TP fit"))

                    else:
                        noise = "Canno't fit"

                    if Bas_parameters_fit[0] != "Fail" and TPparameters[0] != "Fail":
                        print Bas_parameters_fit
                        translated_gas = AN_CLASS.gaus(np.arange(TPparameters[0], 64, 1.0), *Bas_parameters_fit) + TPparameters[2]
                        self.line_list.append(self.plot_rate.plot(np.arange(TPparameters[0], 64, 1.0), translated_gas, '--', label="Gaussian baseline estimation"))
                    self.plot_rate.set_title("ROC {},TIG {}, CH {} , Sigma Noise={} fC".format(self.plotting_gemroc, self.plotting_TIGER, self.plotting_Channel, noise))
                    if self.title == "Noise_measure":
                        try:
                            if noise == "Canno't fit" or self.mapping_matrix[self.plotting_gemroc][self.plotting_TIGER][self.plotting_Channel] == "0":
                                self.gufo["image"] = self.icon_sleep
                            elif noise < 0.6 and self.mapping_matrix[self.plotting_gemroc][self.plotting_TIGER][self.plotting_Channel].split("-")[0] == "X":
                                self.gufo["image"] = self.icon_worry
                            elif noise < 0.25 and self.mapping_matrix[self.plotting_gemroc][self.plotting_TIGER][self.plotting_Channel].split("-")[0] == "V":
                                self.gufo["image"] = self.icon_worry
                            elif noise > 2:
                                self.gufo["image"] = self.icon_cry
                            else:
                                self.gufo["image"] = self.icon_OK
                        except:
                            pass
                    if self.title == "Baseline estimation":
                        if Bas_parameters_fit[0] != "Fail":
                            self.line_list.append(self.plot_rate.plot(np.arange(0, 64, 1.0), AN_CLASS.gaus(np.arange(0, 64, 1.0), *Bas_parameters_fit), '--', label="Gaussian baseline estimation"))
                            self.plot_rate.set_title("ROC {},TIG {}, CH {} , baseline: {}, {}(fit)".format(self.plotting_gemroc, self.plotting_TIGER, self.plotting_Channel, bas_parameters_not_fit[2], Bas_parameters_fit[1]))
                    self.plot_rate.legend()
                    break
                else:
                    self.plot_rate.set_title("GEMROC not active")
                    self.scatter.set_ydata(np.zeros((64)))

        self.canvas.draw()
        self.canvas.flush_events()

    def SAVE(self):
        File_name = tkFileDialog.asksaveasfilename(initialdir="." + sep + "noise_scan" + sep + "saves", title="Select file", filetypes=(("Noise scan files", "*.ns"), ("all files", "*.*")))
        with  open(File_name, 'wb') as f:
            pickle.dump(self.scan_matrixs, f)

    def LOAD(self):
        filename = tkFileDialog.askopenfilename(initialdir="." + sep + "noise_scan" + sep + "saves", title="Select file", filetypes=(("Noise scan files", "*.ns"), ("all files", "*.*")))
        with  open(filename, 'rb') as f:
            self.scan_matrixs = pickle.load(f)

    def load_TP_settings(self, branch="T", TP=True):
        filename = "." + sep + "conf" + sep + "TP_conf.pickle"
        with open(filename, 'rb') as f:
            TP_cof_dict = pickle.load(f)
        for number, GEMROC in self.GEMROC_reading_dict.items():
            try:
                GEMROC.g_inst.load_TP_cal(TP_cof_dict)
            except KeyError:
                pass
            if branch == "T":
                GEMROC.g_inst.load_specif_settings(GEMROC.GEM_COM.conf_folder + sep + "specific_conf_GLOBAL_for_TP")
            else:
                GEMROC.g_inst.load_specif_settings(GEMROC.GEM_COM.conf_folder + sep + "specific_conf_GLOBAL_for_TP_E_branch")
            for T in range(0, 8):
                if TP:
                    GEMROC.GEM_COM.Set_param_dict_global(GEMROC.g_inst, "FE_TPEnable", T, 1)
                else:
                    GEMROC.GEM_COM.Set_param_dict_global(GEMROC.g_inst, "FE_TPEnable", T, 0)
        self.load_TP_button.config(state='disabled')
        print("TP settings loaded")

    def load__fast_TP_settings(self, branch="T", TP=True):
        filename = "." + sep + "conf" + sep + "TP_conf.pickle"
        with open(filename, 'rb') as f:
            TP_cof_dict = pickle.load(f)
        for number, GEMROC in self.GEMROC_reading_dict.items():
            try:
                GEMROC.g_inst.load_TP_cal(TP_cof_dict)
            except KeyError:
                pass
            if branch == "T":
                if TP == True:
                    GEMROC.g_inst.load_specif_settings(GEMROC.GEM_COM.conf_folder + sep + "fast_TP_scan_settings_TP_T")
                else:
                    GEMROC.g_inst.load_specif_settings(GEMROC.GEM_COM.conf_folder + sep + "fast_TP_scan_settings_BS_T")
            else:
                if TP == True:
                    GEMROC.g_inst.load_specif_settings(GEMROC.GEM_COM.conf_folder + sep + "fast_TP_scan_settings_TP_E")
                else:
                    GEMROC.g_inst.load_specif_settings(GEMROC.GEM_COM.conf_folder + sep + "fast_TP_scan_settings_BS_E")

            for T in range(0, 8):
                if TP:
                    GEMROC.GEM_COM.Set_param_dict_global(GEMROC.g_inst, "FE_TPEnable", T, 1)
                else:
                    GEMROC.GEM_COM.Set_param_dict_global(GEMROC.g_inst, "FE_TPEnable", T, 0)
                for ch in range(0, 64):
                    if branch == "T":
                        GEMROC.GEM_COM.Set_param_dict_channel(GEMROC.c_inst, "TriggerMode2B", T, ch, 0)
                        GEMROC.GEM_COM.Set_param_dict_channel(GEMROC.c_inst, "TriggerMode2Q", T, ch, 0)
                        GEMROC.GEM_COM.Set_param_dict_channel(GEMROC.c_inst, "TriggerMode2E", T, ch, 0)
                        GEMROC.GEM_COM.Set_param_dict_channel(GEMROC.c_inst, "TriggerMode2T", T, ch, 0)
                    if branch == "E":
                        GEMROC.GEM_COM.Set_param_dict_channel(GEMROC.c_inst, "TriggerMode2B", T, ch, 1)
                        GEMROC.GEM_COM.Set_param_dict_channel(GEMROC.c_inst, "TriggerMode2Q", T, ch, 1)
                        GEMROC.GEM_COM.Set_param_dict_channel(GEMROC.c_inst, "TriggerMode2E", T, ch, 1)
                        GEMROC.GEM_COM.Set_param_dict_channel(GEMROC.c_inst, "TriggerMode2T", T, ch, 1)
                        GEMROC.GEM_COM.Set_param_dict_channel(GEMROC.c_inst, "Vth_T1", T, ch, 63)

        print("TP settings loaded")

    def unload_TP_settings(self):
        for number, GEMROC in self.GEMROC_reading_dict.items():
            default_g_inst_settigs_filename = GEMROC.GEM_COM.conf_folder + sep + "TIGER_def_g_cfg_2018.txt"
            GEMROC.g_inst = GEM_CONF.g_reg_settings(int(number.split(" ")[1]), default_g_inst_settigs_filename)
            for T in range(0, 8):
                write = GEMROC.GEM_COM.write_G_conf_on_TIGER(GEMROC.g_inst, T)
        print("TP settings unloaded")

    def fit(self):
        start = time.time()
        for GEMROC, matrix in self.scan_matrixs.items():
            for TIG in range(0, 8):
                for channel in range(0, 64):
                    if any(matrix[TIG][channel]) != 0:
                        print ("%s TIG%s CH%s" % (GEMROC, TIG, channel))
                        self.baseline_pos[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)] = AN_CLASS.find_baseline(matrix[TIG][channel])
                        values = AN_CLASS.error_fit(matrix[TIG][channel], int(self.TP_rate.get()), Ebranch=self.E_branch.get())
                        self.fits[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)] = values[0]
                        self.covs[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)] = values[1]
                        self.TPfits[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)] = values[2]
                        self.TPcovs[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)] = values[3]
                        self.baseline[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)] = values[4]
                        # self.chi[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)]=values[4]
                        # self.TPchi[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)]=values[5]
                        # if values[2][2]!="Fail":
                        # gauss_values=gauss_fit_baseline(matrix[TIG][channel],values[0][1],values[0][3],values[2][2])
                        # self.gaussians[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)]=gauss_values
        print ("time")
        print(time.time() - start)

    # def fit(self):
    #     start = time.time()
    #     for GEMROC,matrix in self.scan_matrixs.items():
    #         pool = Pool()
    #         # print type(pool.map(process_image, matrix))
    #         # print len(pool.map(process_image, matrix))
    #
    #         lista = pool.map(process_image, matrix)
    #
    #     print ("time")
    #     print(time.time()-start)

    def SAVE_noise(self):
        for GEMROC, dict0 in self.TPfits.items():
            filename = "noise_scan" + sep + "GEMROC{}".format(GEMROC.split()[1]) + sep + "noise.n"
            with open(filename, 'w') as f:
                for TIGER, dict1 in self.TPfits[GEMROC].items():
                    for CH, dictionary in self.TPfits[GEMROC][TIGER].items():
                        parameters = self.TPfits[GEMROC][TIGER][CH]
                        if parameters[0] != "Fail" and parameters[2] > int(self.TP_rate.get()) / 5 and parameters[2] < int(self.TP_rate.get()) * 5:
                            noise = AN_CLASS.convert_to_fC(parameters[1], 55)
                            cov = AN_CLASS.convert_to_fC(self.TPcovs[GEMROC][TIGER][CH][1][1], 55)
                        else:
                            noise = -1
                            cov = 9999
                        f.write("{} {} {} Noise: {} Variance: {}\n".format(GEMROC, TIGER, CH, noise, cov))

    def SAVE_noise_for_thr_setting(self):
        """
        Saves the values of the thrsholds for the advanced threshold placement
        :return:
        """
        if os.path.isfile("." + sep + "conf" + sep + "advanced_threshold_setting" + sep + "noise_fit.pickle"):
            os.rename("." + sep + "conf" + sep + "advanced_threshold_setting" + sep + "noise_fit.pickle", "." + sep + "conf" + sep + "advanced_threshold_setting" + sep + "last_noise_fit.pickle")

        with open("." + sep + "conf" + sep + "advanced_threshold_setting" + sep + "noise_fit.pickle", 'w') as f:
            pickle.dump(self.TPfits, f)

    def SAVE_baseline(self, NOT_FIT=True):
        """
        Saves the value of the baseline for advanced threshold placement
        """
        if self.E_branch.get():
            name = "Baseline_E"
        else:
            name = "Baseline_T"
        if os.path.isfile("." + sep + "conf" + sep + "advanced_threshold_setting" + sep + name + ".pickle"):
            os.rename("." + sep + "conf" + sep + "advanced_threshold_setting" + sep + name + ".pickle", "." + sep + "conf" + sep + "advanced_threshold_setting" + sep + "last" + name + ".pickle")

        with open("." + sep + "conf" + sep + "advanced_threshold_setting" + sep + name + ".pickle", 'w') as f:
            if NOT_FIT:
                pickle.dump(self.baseline_pos, f, protocol=2)
            else:
                pickle.dump(self.baseline, f, protocol=2)
        # print (self.E_branch.get())

    def switch_to_tp_distr(self):
        self.strart_button["text"] = "Acquire test pulses"


class baseline_exit(noise_measure):
    def __init__(self, noise_measure, main_window, gemroc_handler, tab_control, main_menu_istance):
        noise_measure.__init__(self, gemroc_handler=gemroc_handler, main_window=main_window, tab_control=tab_control, main_menu_istance=main_menu_istance)
        self.title = "Baseline estimation"

    def fit(self):
        for GEMROC, matrix in self.scan_matrixs.items():
            for TIG in range(0, 8):
                for channel in range(0, 64):
                    if any(matrix[TIG][channel]) != 0:
                        print ("TIG%s CH%s" % (TIG, channel))
                        self.baseline_pos[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)] = AN_CLASS.find_baseline(matrix[TIG][channel])
                        # self.baseline[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)] = AN_CLASS.gaus_fit_baseline(matrix[TIG][channel], 0, 0, 0)[0]
                        # self.chi[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)]=values[4]
                        # self.TPchi[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)]=values[5]
                        # if values[2][2]!="Fail":Save base
                        # gauss_values=gauss_fit_baseline(matrix[TIG][channel],values[0][1],values[0][3],values[2][2])
                        # self.gaussians[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)]=gauss_values


def squared_sum(A, B):
    # A= Aspettati
    if len(A) == len(B):
        C = np.zeros((len(A)))
        # for i in range (0,len(B)):
        # C[i]=((A[i]-B[i])**2)/(A[i]+0.001)
        C = ((A - B) ** 2) / (A + 0.001)
        return np.sum(C)
    else:
        raise Exception("A and B not same size")


def sort_by_number(stringa1, stringa2):
    number1 = find_number(stringa1)
    number2 = find_number(stringa2)
    return number1 - number2


def find_number(stringa):
    if type(stringa) != tuple:
        number = int(stringa.split(" ")[1])
    else:
        number = int(stringa[0].split(" ")[1])

    return number
# def process_image(data):
#     values =AN_CLASS.error_fit(data,self.TP_rate, Ebranch=True)
#     return values
