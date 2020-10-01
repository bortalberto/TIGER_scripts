import datetime
import glob
import json
import os
import pickle
import time
from tkinter import *
from tkinter.ttk import Notebook
from multiprocessing import Process, Pipe
import subprocess
from threading import Thread
import array
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import ctypes
import psutil
TER = True


from lib import GEM_ACQ_classes as GEM_ACQ

OS = sys.platform
if OS == 'win32':
    sep = '\\'
elif OS == 'linux2' or 'linux':
    sep = '/'
else:
    print("ERROR: OS {} non compatible".format(OS))
    sys.exit()

debug = False
#db_address = '127.0.0.1'
db_address = '192.168.38.191'
db_port = 8086



class menu():
    def __init__(self, std_alone=True, main_winz=None, GEMROC_reading_dict=None, father=None):
        try:
            from influxdb import InfluxDBClient
            from lib import DB_classes
            self.DB = True
        except:
            print("Can't find DB library")
            self.DB = False

        self.father = father
        self.PMT = True
        self.std_alone = std_alone
        self.GEM_to_read = np.zeros((22))
        self.GEM_to_read_last = np.zeros((22))
        self.errors_counters_810 = {}
        self.logfile = "." + sep + "log_folder" + sep + "ACQ_log_{}".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        self.conffile = "." + sep + "log_folder" + sep + "CONF_log_{}".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        if self.DB:
            try:
                self.db_sender = DB_classes.Database_Manager()
            except:
                print("Can't connect to BD")
                self.DB = False

        self.sub_run_number = 0
        self.mode = 'TL'
        self.LED = []
        self.FIELD_TIGER = []
        self.LED_UDP = []
        self.plotting_gemroc = 0
        self.plotting_TIGER = 0
        self.time = 2
        self.GEM = []
        self.run_folder = "."
        self.reset_810 = 0
        self.reset_timedout = 0
        self.reading_TIGERs_matrix = np.zeros((22, 8))
        self.last_810_log = 0
        self.build_DCT_matrix()
        if std_alone:
            self.master_window = Tk()
        else:
            self.master_window = Toplevel(main_winz)
            self.main_winz = main_winz
            self.GEMROC_reading_dict = GEMROC_reading_dict
            self.tabControl = Notebook(self.master_window)  # Create Tab Control

        self.master_window.wm_title("GEMROC acquisition")
        self.restart = BooleanVar(self.master_window)
        self.configure_every_restart = BooleanVar(self.master_window)
        self.restart.set(True)
        self.configure_every_restart.set(True)

        self.error_GEMROC = BooleanVar(self.master_window)
        self.error_GEMROC.set(False)
        self.online_monitor = BooleanVar(self.master_window)
        self.online_monitor.set(False)
        self.online_monitor_data = BooleanVar(self.master_window)
        self.online_monitor_data.set(False)

        self.save_conf_every_run = BooleanVar(self.master_window)
        self.simple_analysis = IntVar(self.master_window)
        self.run_analysis = IntVar(self.master_window)
        if OS == 'linux':
            self.master_window.wm_iconbitmap('@' + "." + sep + 'icons' + sep + 'ACQ_ICON.xbm')
        Label(self.master_window, text='Acquisition setting', font=("Courier", 25)).pack()
        if not std_alone:
            self.master = Frame(self.tabControl)
            self.tabControl.add(self.master, text='Acquisition')  # Add the tab
            self.tabControl.pack(expand=1, fill="both")  # Pack to make visible
        else:
            self.master = Frame(self.master_window)
            self.master.pack()

        self.icon_on = PhotoImage(file="." + sep + 'icons' + sep + 'on.gif')
        self.icon_off = PhotoImage(file="." + sep + 'icons' + sep + 'off.gif')
        self.icon_bad = PhotoImage(file="." + sep + 'icons' + sep + 'bad.gif')
        self.mappa = PhotoImage(file="." + sep + 'icons' + sep + 'mappa_updated_normal.gif')
        self.grid_frame = Frame(self.master)
        self.grid_frame.pack()
        Button(self.grid_frame, text='ROC 00', command=lambda: self.toggle(0)).grid(row=0, column=0, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 01', command=lambda: self.toggle(1)).grid(row=0, column=2, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 02', command=lambda: self.toggle(2)).grid(row=0, column=4, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 03', command=lambda: self.toggle(3)).grid(row=0, column=6, sticky=W, pady=4)
        Button(self.grid_frame, text='ROC 04', command=lambda: self.toggle(4)).grid(row=0, column=8, sticky=W, pady=4)
        Button(self.grid_frame, text='ROC 05', command=lambda: self.toggle(5)).grid(row=0, column=10, sticky=W, pady=4)
        Button(self.grid_frame, text='ROC 06', command=lambda: self.toggle(6)).grid(row=0, column=12, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 07', command=lambda: self.toggle(7)).grid(row=0, column=14, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 08', command=lambda: self.toggle(8)).grid(row=0, column=16, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 09', command=lambda: self.toggle(9)).grid(row=0, column=18, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 10', command=lambda: self.toggle(10)).grid(row=1, column=0, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 11', command=lambda: self.toggle(11)).grid(row=1, column=2, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 12', command=lambda: self.toggle(12)).grid(row=1, column=4, sticky=W, pady=4)
        Button(self.grid_frame, text='ROC 13', command=lambda: self.toggle(13)).grid(row=1, column=6, sticky=W, pady=4)
        Button(self.grid_frame, text='ROC 14', command=lambda: self.toggle(14)).grid(row=1, column=8, sticky=W, pady=4)
        Button(self.grid_frame, text='ROC 15', command=lambda: self.toggle(15)).grid(row=1, column=10, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 16', command=lambda: self.toggle(16)).grid(row=1, column=12, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 17', command=lambda: self.toggle(17)).grid(row=1, column=14, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 18', command=lambda: self.toggle(18)).grid(row=1, column=16, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 19', command=lambda: self.toggle(19)).grid(row=1, column=18, sticky=NW, pady=4)

        self.start_frame = Frame(self.master)
        self.start_frame.pack()
        Label(self.start_frame, text="Acq time (seconds for TL, minutes for TM)").grid(row=0, column=0, sticky=NW, pady=4)
        self.time_in = Entry(self.start_frame, width=3)
        self.time_in.insert(END, '10')
        self.time_in.grid(row=0, column=1, sticky=NW, pady=4)
        Checkbutton(self.start_frame, text="Fast analysis", variable=self.simple_analysis).grid(row=0, column=2, sticky=NW, pady=4)
        Checkbutton(self.start_frame, text="On run analysis", variable=self.run_analysis).grid(row=0, column=3, sticky=NW, pady=4)
        Checkbutton(self.start_frame, text="Restart", variable=self.restart).grid(row=0, column=4, sticky=NW, pady=4)
        Checkbutton(self.start_frame, text="Save conf. at every subrun", variable=self.save_conf_every_run).grid(row=0, column=5, sticky=NW, pady=4)
        Checkbutton(self.start_frame, text="Save GEMROC global errors at the end", variable=self.error_GEMROC).grid(row=0, column=5, sticky=NW, pady=4)

        a_frame = Frame(self.master)
        a_frame.pack()
        zero_frame = LabelFrame(a_frame)
        zero_frame.grid(row=1, column=1, sticky=NW, padx=70)

        self.but6 = Button(zero_frame, text='New run folder', command=self.new_run_folder)
        self.but6.grid(row=1, column=2, sticky=NW)
        self.but7 = Button(zero_frame, text='Test folder', command=self.set_test_folder)
        self.but7.grid(row=1, column=3, sticky=NW)
        self.folder_label = Label(zero_frame, text="-", width=20)
        self.folder_label.grid(row=1, column=4, sticky=W)

        self.but6 = Button(a_frame, text='Start acquisition', command=self.start_acq)
        self.but6.grid(row=1, column=2, sticky=NW, pady=4)
        self.but7 = Button(a_frame, text='Trigger less file name', command=self.switch_mode, background='#ccffff', activebackground='#ccffff', height=1, width=18)
        self.but7.grid(row=1, column=3, sticky=NW, pady=4)
        self.but8 = Button(a_frame, text='Stop acquisition', command=self.stop_acq, state='normal')
        b_frame = LabelFrame(a_frame)
        b_frame.grid(row=1, column=8, sticky=NW, pady=4, padx=40)
        if self.PMT:
            Button(b_frame, text='Turn ON PMTs', command=self.PMT_on, width=10, activeforeground="green").pack(side=LEFT)
            Button(b_frame, text='Turn OFF PMTs', command=self.PMT_OFF, width=10, activeforeground="red").pack(side=LEFT)

        # Label(b_frame,text='Message ').grid(row=0, column=1, sticky=NW, pady=4)
        # self.Launch_error_check=Label(b_frame, text='-', background='white')
        # self.Launch_error_check.grid(row=0, column=2, sticky=NW, pady=4)
        # Button(self.master,text='Exit', command='close').place(relx=0.9, rely=0.9, anchor=NW)
        # Button(a_frame, text='Communication errorinterfacee',command=error_GUI)

        self.but8.grid(row=1, column=4, sticky=NW, pady=4)
        for i in range(0, len(self.GEM_to_read)):
            if i < 10:
                riga = 0
            elif i < 20:
                riga = 1
            else:
                riga = 2

            colonna = ((i) % 10) * 2 + 1
            self.LED.append(Label(self.grid_frame, image=self.icon_off))

            self.LED[i].grid(row=riga, column=colonna)
        middle_frame = Frame(self.master)
        middle_frame.pack()
        frame_mails = Frame(middle_frame)
        frame_mails.pack(side=LEFT, padx=20)
        Button(frame_mails, text="Get number of triggers", command=self.get_total_trig).pack(side=LEFT, padx=5)
        self.mail_start_but = Button(frame_mails, text="Send acq start mail", command=self.send_acq_start)
        self.mail_start_but.pack(side=LEFT)

        self.mail_stop_but = Button(frame_mails, text="Send acq stop mail", command=self.send_acq_stop)
        self.mail_stop_but.pack(side=LEFT)

        self.launch_GRAAL_bt = Button(frame_mails, text="Launch GRAAL analysis", command=self.run_GRAAL)
        self.launch_GRAAL_bt.pack(side=LEFT)

        spacer = Frame(frame_mails)
        spacer.pack(side=LEFT, padx=50)

        self.errors = Frame(middle_frame)
        self.errors.pack(side=LEFT)
        self.LBerror = Label(self.errors, text='Warnings', font=("Courier", 25))
        self.LBerror.grid(row=0, column=1, columnspan=8, sticky=S, pady=5)
        # self.butleftG_err = Button(self.errors, text='<', command=lambda: self.change_G_or_T(-1, "G")).grid(row=1, column=0, sticky=S, pady=4)
        # self.LBGEM_err = Label(self.errors, text='GEMROC {}'.format(self.plotting_gemroc), font=("Courier", 14))
        # self.LBGEM_err.grid(row=1, column=1, sticky=S, pady=4)
        # self.butrightG_err = Button(self.errors, text='>', command=lambda: self.change_G_or_T(1, "G")).grid(row=1, column=2, sticky=S, pady=4)

        # self.LBUDP0 = Label(self.errors, text='UDP packet error  ')
        # self.LBUDP0.grid(row=2, column=1, sticky=S, pady=4)
        # Label(self.errors, text='  TIGER missing').grid(row=2, column=2, sticky=S, pady=4) #Tolto TIGER missing perche' inutile
        if not self.std_alone:
            self.open_adv_acq()
            self.open_on_run_tab()
            self.online_monitor.set(True)
            self.online_monitor_data.set(True)
            Checkbutton(self.start_frame, text="Online monitor", variable=self.online_monitor).grid(row=0, column=6, sticky=NW, pady=4)
            Checkbutton(self.start_frame, text="Online data monitor", variable=self.online_monitor_data).grid(row=0, column=7, sticky=NW, pady=4)

        # TO be restored
        # Checkbutton(self.start_frame, text="Data online monitor", variable=self.online_monitor_data).grid(row=0, column=3, sticky=NW, pady=4)

        self.LED_UDP = Label(self.errors, image=self.icon_off)
        self.LED_UDP.grid(row=4, column=1)
        self.messagge_field = Label(self.errors, text="--", background='white', width=40, height=3, wraplength=350, justify="center")
        self.messagge_field.grid(row=4, column=2)
        # self.FIELD_TIGER = Label(self.errors, text='-', background='white')
        # self.FIELD_TIGER.grid(row=4, column=2)

        self.plot_window = Frame(self.master)
        self.plot_window.pack(side=LEFT)
        # self.plot_window.geometry('900x800')
        self.corn0 = Frame(self.plot_window)
        self.corn0.pack()
        self.LBOCC = Label(self.corn0, text='Channel counts', font=("Times", 18))
        self.LBOCC.grid(row=0, column=1, sticky=S, pady=4)
        self.butleftG = Button(self.corn0, text='<', command=lambda: self.change_G_or_T(-1, "G")).grid(row=1, column=0, sticky=S, pady=4)
        self.LBGEM = Label(self.corn0, text='GEMROC {}'.format(self.plotting_gemroc), font=("Courier", 14))
        self.LBGEM.grid(row=1, column=1, sticky=S, pady=4)
        self.butrightG = Button(self.corn0, text='>', command=lambda: self.change_G_or_T(1, "G")).grid(row=1, column=2, sticky=S, pady=4)
        self.butleftT = Button(self.corn0, text='<', command=lambda: self.change_G_or_T(-1, "T")).grid(row=2, column=0, sticky=S, pady=4)
        self.LBTIG = Label(self.corn0, text='TIGER {}'.format(self.plotting_TIGER), font=("Courier", 14))
        self.LBTIG.grid(row=2, column=1, sticky=S, pady=4)
        self.butrightT = Button(self.corn0, text='>', command=lambda: self.change_G_or_T(1, "T")).grid(row=2, column=2, sticky=S, pady=4)
        self.FEB_label = Label(self.corn0, text='FEB {}'.format(int(round((self.plotting_TIGER + self.plotting_gemroc * 8) / 2))), font=("Courier", 14))
        self.FEB_label.grid(row=3, column=1, sticky=S, pady=4)
        self.corn1 = Frame(self.plot_window)
        self.corn1.pack()

        # Plot
        x = np.arange(0, 64)
        v = np.zeros((64))

        self.fig = Figure(figsize=(6, 4))
        self.plot_rate = self.fig.add_subplot(111)
        self.scatter, = self.plot_rate.plot(x, v, 'r+')
        self.plot_rate.set_title("TIGER {}, GEMROC {}".format(self.plotting_TIGER, self.plotting_gemroc))
        self.plot_rate.set_ylabel("HitRates", fontsize=14)
        self.plot_rate.set_xlabel("Channel", fontsize=14)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_window)
        self.canvas.get_tk_widget().pack(side=BOTTOM)
        self.canvas.draw()
        self.canvas.flush_events()
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.corn1)
        self.toolbar.draw()
        self.switch_mode()

        if not std_alone:
            for number, GEMROC in self.GEMROC_reading_dict.items():
                n = int(number.split()[1])
                self.toggle(n)
        self.set_last_folder()

        self.map_frame = Frame(self.master)
        self.map_frame.pack(side=RIGHT)
        Label(self.map_frame, image=self.mappa).pack()
        ##Variables for network stats logging
        self.master_window.protocol("WM_DELETE_WINDOW", self._delete_window)
        # self.master_window.bind("<Destroy>", self._destroy)
        #
        # button = Button(self.master_window, text="Destroy", command=self.master_window.destroy)
        # button.pack()

    def build_DCT_matrix(self):
        """
        Don't care matrix, TIGER that will not stop the acquisition if they do too many errors
        :return:
        """
        self.DCT_matrix = np.zeros((22, 8))
        with open("conf" + sep + "DCT", 'r') as f:
            for line in f.readlines():
                if line[0] != "#":
                    try:
                        gemroc, tiger = line.split(" ")
                        gemroc = int(gemroc)
                        if tiger != "ALL":
                            tiger = int(tiger)
                    except Exception as E:
                        print("Parsing Error: {}".format(E))
                        return

                    if tiger != "ALL":
                        self.DCT_matrix[gemroc][tiger] = 1
                    else:
                        for T in range(0, 8):
                            self.DCT_matrix[gemroc][T] = 1

    def send_acq_start(self):
        self.send_mail(error="Run start {}".format(self.run_folder), subject="Run start {}".format(self.run_folder))
        self.mail_start_but.config(state='disabled')
        self.master_window.after(5000, lambda: self.reset_mail_but())

    def send_acq_stop(self):
        self.send_mail(error="Run stop {}. ~ {} triggers in this run".format(self.run_folder, self.get_total_trig()), subject="Run stop {}".format(self.run_folder))
        self.mail_stop_but.config(state='disabled')
        self.master_window.after(5000, lambda: self.reset_mail_but())
        if TER:
            subprocess.call(['/bin/bash', "copy_data {}".format(self.run_folder.split("_")[1])])
            subprocess.call(['/bin/bash', "sync_data"])
    def run_GRAAL(self):
        self.launch_GRAAL_bt.config(state='disabled')
        subprocess.call(["/home/cgemlab2/GRAAL/GRAAL.sh", "-a", str(self.run_folder.split("_")[1])])

        self.master_window.after(5000, lambda: self.reset_mail_but())

    def reset_mail_but(self):
        self.mail_start_but.config(state='normal')
        self.mail_stop_but.config(state='normal')
        self.launch_GRAAL_bt.config(state='normal')
    def set_last_folder(self):
        """
        Funzione per andare all'ultima cartella
        """
        list_folder = [name for name in os.listdir("." + sep + "data_folder") if os.path.isdir("." + sep + "data_folder" + sep + name)]
        list_number = [int(folder[4:]) for folder in list_folder if folder[0:3] == "RUN"]
        if len(list_number) != 0:
            list_number.sort()
            self.run_folder = "RUN_{}".format(list_number[-1])
        else:
            os.mkdir("." + sep + "data_folder" + sep + "RUN_0")

            self.run_folder = "RUN_0"

        print("Data folder set: {}".format(self.run_folder))
        self.folder_label['text'] = "Folder : {}".format(self.run_folder)

    def new_run_folder(self):
        list_folder = [name for name in os.listdir("." + sep + "data_folder") if os.path.isdir("." + sep + "data_folder" + sep + name)]
        list_number = [int(folder[4:]) for folder in list_folder if folder[0:3] == "RUN"]
        list_number.sort()
        last_run_number = list_number[-1]
        os.mkdir("." + sep + "data_folder" + sep + "RUN_{}".format(last_run_number + 1))
        self.set_last_folder()

    def set_test_folder(self):
        self.run_folder = "test_folder"
        print("Test folder set: {}".format(self.run_folder))
        self.folder_label['text'] = "Folder : {}".format(self.run_folder)

    def open_adv_acq(self):
        self.adv_frame = Frame(self.tabControl)
        # self.adv_self.canvas = Canvas(self.adv_frame,scrollregion=(0,0,500,500))
        self.tabControl.add(self.adv_frame, text='TIGERs errors and selection')
        self.error_dict810 = {}
        scrollbar = Scrollbar(self.adv_frame, orient=VERTICAL)

        self.canvas2 = Canvas(self.adv_frame)
        frame = Frame(self.canvas2, bd=1)
        scrollbar.pack(side=RIGHT, fill=Y)
        scrollbar.config(command=self.canvas2.yview)
        self.canvas2.config(yscrollcommand=scrollbar.set)
        self.canvas2.create_window((0, 0), window=frame, anchor='nw')
        frame.bind("<Configure>", self.myfunction)
        self.canvas2.pack(side=LEFT, fill=BOTH)
        Label(frame, text='Acquisition set single TIGERs', font=("Courier", 16)).pack()
        self.button_dict = {}
        for number, GEMROC in sorted(self.GEMROC_reading_dict.items(), key=find_number):
            a = Frame(frame)
            a.pack(pady=5, fill=BOTH)
            Label(a, text='{} Err(8/10):   '.format(number), font=("Courier", 10)).grid(row=1, column=0, sticky=NW, pady=4)
            for T in range(0, 8):
                self.error_dict810["{} TIGER {}".format(number, T)] = Label(a, text="-----", width=8, font=("Courier", 10))
                self.error_dict810["{} TIGER {}".format(number, T)].grid(row=1, column=T + 1, sticky=NW, pady=4)
            Label(a, text='{} TIGERs:   '.format(number), font=("Courier", 10)).grid(row=0, column=0, sticky=NW, pady=4)
            for T in range(0, 8):
                self.button_dict["{} TIGER {}".format(number, T)] = Button(a, text='{}'.format(T), width=4, height=1, font=("Courier", 10), command=lambda T=T, number=number: self.Change_Reading_Tigers(number, T))
                self.button_dict["{} TIGER {}".format(number, T)].grid(row=0, column=T + 1, sticky=NW, pady=4)

            Label(a, text="___________________________________________________________________________________________________________________________").grid(row=2, column=0, sticky=NW, columnspan=12)

        self.refresh_buttons_TIGERs()

    def open_on_run_tab(self):
        self.on_run_frame = Frame(self.tabControl)
        # self.adv_self.canvas = Canvas(self.adv_frame,scrollregion=(0,0,500,500))
        self.tabControl.add(self.on_run_frame, text='On run check settings')
        Label(self.on_run_frame, text='On run check settings', font=("Courier", 16)).pack()

        first_row = Frame(self.on_run_frame)
        first_row.pack()
        self.check_810 = BooleanVar(self.master_window)
        self.check_810.set(True)

        self.stop_timeout = BooleanVar(self.master_window)
        self.stop_timeout.set(True)

        self.numb_of_810_reset = IntVar(self.master_window)
        self.numb_of_timeout_reset = IntVar(self.master_window)
        self.numb_of_810_reset.set(4)
        self.numb_of_timeout_reset.set(4)

        fram810 = LabelFrame(first_row)
        fram810.pack(side=LEFT)

        framtimed = LabelFrame(first_row)
        framtimed.pack(side=LEFT)
        Checkbutton(fram810, var=self.check_810, text="Check on 8/10 bit errors").pack(side=LEFT, padx=3)
        Label(fram810, text="     Maximum number of reset in a row").pack(side=LEFT)
        Entry(fram810, width=3, textvariable=self.numb_of_810_reset).pack(side=LEFT)
        Checkbutton(framtimed, var=self.stop_timeout, text="Stop for timeout").pack(side=LEFT)
        Label(framtimed, text="     Maximum number of timeout in a row").pack(side=LEFT, padx=3)
        Entry(framtimed, width=3, textvariable=self.numb_of_timeout_reset).pack(side=LEFT)

        second_row = LabelFrame(self.on_run_frame)
        second_row.pack()
        self.check_thr = BooleanVar(self.master_window)
        self.check_thr.set(True)
        self.vth_t_toll = IntVar(self.master_window)
        self.vth_t_toll.set(7)
        self.vth_e_toll = IntVar(self.master_window)
        self.vth_e_toll.set(7)
        self.numb_of_viol = IntVar(self.master_window)
        self.numb_of_viol.set(40)
        Checkbutton(second_row, var=self.check_thr, text="Check on thr before start").pack(side=LEFT)
        Label(second_row, text="     Tollerance on the T thr").pack(side=LEFT)
        Entry(second_row, width=3, textvariable=self.vth_t_toll).pack(side=LEFT)

        Label(second_row, text="     Tollerance on the E thr").pack(side=LEFT)
        Entry(second_row, width=3, textvariable=self.vth_e_toll).pack(side=LEFT)

        Label(second_row, text="     Number of concess violation").pack(side=LEFT)
        Entry(second_row, width=3, textvariable=self.numb_of_viol).pack(side=LEFT)

        third_row = LabelFrame(self.on_run_frame)
        third_row.pack()

        self.check_pause = BooleanVar(self.master_window)
        self.check_pause.set(True)
        self.check_TM = BooleanVar(self.master_window)
        self.check_TM.set(True)
        Checkbutton(third_row, var=self.check_pause, text="Check pause").pack(side=LEFT)
        Checkbutton(third_row, var=self.check_TM, text="Check TM").pack(side=LEFT)

    def myfunction(self, event):
        self.canvas2.configure(scrollregion=self.canvas2.bbox("all"), width=1200, height=700)

    def Change_Reading_Tigers(self, number, T, ForceOff=False):
        n = (self.GEMROC_reading_dict[number].GEM_COM.gemroc_DAQ_XX.DAQ_config_dict["EN_TM_TCAM_pattern"] >> T) & 0x1
        if n == 1:
            print (T)
            print (n)
            print (self.GEMROC_reading_dict[number].GEM_COM.gemroc_DAQ_XX.DAQ_config_dict["EN_TM_TCAM_pattern"])
            self.GEMROC_reading_dict[number].GEM_COM.gemroc_DAQ_XX.DAQ_config_dict["EN_TM_TCAM_pattern"] -= 2 ** T

            print (self.GEMROC_reading_dict[number].GEM_COM.gemroc_DAQ_XX.DAQ_config_dict["EN_TM_TCAM_pattern"])
            with open(self.logfile, 'a') as f:
                f.write("{} -- {} TIGER {} disabled\n".format(time.ctime(), number, T))

        elif ForceOff == False:
            self.GEMROC_reading_dict[number].GEM_COM.gemroc_DAQ_XX.DAQ_config_dict["EN_TM_TCAM_pattern"] += 2 ** T
        # print self.GEMROC_reading_dict[number].GEM_COM.gemroc_DAQ_XX.DAQ_config_dict["EN_TM_TCAM_pattern"]
        # self.GEMROC_reading_dict[number].GEM_COM.DAQ_set_register()
        self.refresh_buttons_TIGERs()

    def refresh_buttons_TIGERs(self):
        for number, GEMROC in self.GEMROC_reading_dict.items():
            for T in range(0, 8):
                n = (self.GEMROC_reading_dict[number].GEM_COM.gemroc_DAQ_XX.DAQ_config_dict["EN_TM_TCAM_pattern"] >> T) & 0x1
                self.reading_TIGERs_matrix[int(number.split()[1])][T] = n
                if n == 1:
                    self.button_dict["{} TIGER {}".format(number, T)]['background'] = '#0099ff'
                    self.button_dict["{} TIGER {}".format(number, T)]['activebackground'] = '#0099ff'
                else:
                    self.button_dict["{} TIGER {}".format(number, T)]['background'] = '#e6e6e6'
                    self.button_dict["{} TIGER {}".format(number, T)]['activebackground'] = '#e6e6e6'

    def refresh_8_10_counters_and_TimeOut(self):

        if self.DB and self.online_monitor_data.get() and time.time() - self.last_810_log > 10:
            self.db_sender.send_810b_error_to_DB(self.GEMROC_reading_dict, self.error_dict810)
            self.db_sender.log_PC_stats()
            self.last_810_log = time.time()

        for key, label in self.error_dict810.items():
            try:
                label['text'] = self.errors_counters_810[key]
            except:
                label['text'] = "-----"
        for i in self.GEM:
            if i.TIMED_out == True:
                self.LED[int(i.GEMROC_ID)]['image'] = self.icon_bad
                with open(self.logfile, 'a') as f:
                    f.write("{} -- GEMROC {} Timed_out\n".format(time.ctime(), i.GEMROC_ID, self.mode))
            else:
                self.LED[int(i.GEMROC_ID)]['image'] = self.icon_on
        if self.online_monitor.get():
            for key, label in self.error_dict810.items():
                if label['text'] == 16777215:
                    GEMROC = int(key.split()[1])
                    TIGER = int(key.split()[3])
                    if self.reading_TIGERs_matrix[GEMROC][TIGER] == 1 and self.DCT_matrix[GEMROC][TIGER] != 1:
                        self.reset_810 += 1
                        if self.reset_810 < int(self.numb_of_810_reset.get()):
                            print("Restarting acquisition due to 8bit/10bit errors \n")
                            self.LED_UDP['image'] = self.icon_bad

                            self.messagge_field['text'] = "Restarting acquisition due to 8bit/10bit errors"
                            print("Number of reset for 8bit/10bit errors in a row: {}".format(self.reset_810))
                            with open(self.logfile, 'a') as f:
                                f.write("{} -- Restarting acquisition due to 8bit/10bit errors \n".format(time.ctime()))
                                if self.restart.get():
                                    self.relaunch_acq()
                                else:
                                    self.stop_acq(True)
                            break
                        else:
                            print("Stopping acquisition due to 8/10bit errors {} times in a row\n".format(self.reset_810))
                            self.messagge_field['text'] = "Stopping acquisition due to 8bit/10bit errors {} times in a row".format(self.reset_810)
                            self.LED_UDP['image'] = self.icon_bad

                            with open(self.logfile, 'a') as f:
                                f.write("{} -- Stopping acquisition due to 8/10bit errors {} times in a row \n".format(time.ctime(), self.reset_810))
                            self.send_mail("{} --8/10 bit errors counter saturated {} times in a row: GEMROC {} TIGER {}\n (Note: there could be more errors).".format(time.ctime(), self.reset_810, GEMROC, TIGER))
                            # self.send_telegram("{} --8/10 bit errors counter saturated {} times in a row: GEMROC {} TIGER {}\n (Note: there could be more errors).".format(time.ctime(), self.reset_810, GEMROC, TIGER))
                            # self.restart.set(False)
                            # self.stop_acq(True)
                            break

            for i in self.GEM:
                # print ("{} timeout:{}".format(i.GEMROC_ID,i.TIMED_out))
                if i.TIMED_out and self.reset_timedout < int(self.numb_of_timeout_reset.get()):
                    self.reset_timedout += 1
                    self.LED_UDP['image'] = self.icon_bad

                    self.messagge_field['text'] = "Restarting acquisition for timeout"

                    print("Number of reset for time out errors in a row: {}".format(self.reset_timedout))
                    if self.restart.get():
                        self.relaunch_acq()

                    else:
                        self.restart.set(False)
                        self.stop_acq(True)
                    break
                if i.TIMED_out and self.reset_timedout >= int(self.numb_of_timeout_reset.get()) and self.stop_timeout.get():
                    self.messagge_field['text'] = "Stopping acquisition for {} timeouts in a row".format(self.reset_timedout)
                    self.LED_UDP['image'] = self.icon_bad

                    with open(self.logfile, 'a') as f:
                        f.write("{} -- Stopping acquisition due to time out errors {} times in a row \n".format(time.ctime(), self.reset_timedout))
                    self.send_mail("{} -- Stopping acquisition due to time out errors {} times in a row (GEMROC {})\n (Note: there could be more errors).".format(time.ctime(), self.reset_timedout, i.GEMROC_ID))
                    self.send_telegram("{} -- Stopping acquisition due to time out errors {} times in a row (GEMROC {})\n (Note: there could be more errors).".format(time.ctime(), self.reset_timedout, i.GEMROC_ID))
                    self.restart.set(False)
                    self.stop_acq(True, stop_log=False)
                    break





    def PMT_on(self):
        os.system("./HVWrappdemo_0 ttyUSB0 VSet 2000")
        os.system("./HVWrappdemo_2 ttyUSB0 VSet 2100")

    def PMT_OFF(self):
        os.system("./HVWrappdemo_0 ttyUSB0 VSet 1300")
        os.system("./HVWrappdemo_2 ttyUSB0 VSet 800")

    def relaunch_acq(self):
        self.stop_acq(True)
        try:
            if self.restart.get():
                self.messagge_field['text'] = "Restart process ongoing, please wait"
                time.sleep(8)
                # print ("Sending hard reset")
                # self.father.hard_reset(1)
                if debug:
                    print("Restarting")
                if self.PMT:
                    if debug:
                        print("PMT down")
                    self.PMT_OFF()
                # time.sleep(17)
                # print ("Writing GEMROC configuration")
                # for number, GEMROC in self.GEMROC_reading_dict.items():
                #     GEMROC.GEM_COM.DAQ_set_with_dict()
                #     self.father.write_default_LV_conf(GEMROC)
                #     GEMROC.GEM_COM.reload_default_td()
                #
                time.sleep(10)

                # self.father.reactivate_TIGERS()
                # self.refresh_buttons_TIGERs()
                self.father.Synch_reset()

                # self.father.Synch_reset()
                # print ("Writing TIGER configuration")
                # # self.father.Synch_reset()
                # self.father.load_default_config_parallel(set_check=False)
                # self.father.Synch_reset()
                self.father.load_default_config_parallel(set_check=False)
                self.father.doing_something=False
                print("Configuration wrote")
                time.sleep(2)

                self.father.Synch_reset()
                self.father.TCAM_reset()
                if debug:
                    print("Setting pause")
                self.father.set_pause_mode(to_all=True, value=1)

                if self.PMT:
                    if debug:
                        print("PMT ON")
                    self.PMT_on()
                time.sleep(15)
                self.start_acq(First_launch=False)
        except:
            if not self.std_alone:
                self.error_thread = (Thread_handler_errors(self.GEMROC_reading_dict, self.GEM, self.errors_counters_810, self))

            if not self.std_alone:
                self.error_thread.start()

    def ref_adv_acq(self):
        widget_list = all_children(self.adv_self.canvas)
        for item in widget_list:
            item.pack_forget()
        self.refresh_buttons_TIGERs()

    def save_conf_registers(self, save_txt=False, save_pickle=True):
        """
        Save configuration registers during acquisition start
        """
        conf_dict_total = {}
        for number, GEMROC in self.GEMROC_reading_dict.items():
            conf_dict_total[number] = {}
            conf_dict_total[number]["DAQ"] = GEMROC.GEM_COM.gemroc_DAQ_XX.DAQ_config_dict
            for T in range(0, 8):
                conf_dict_total[number]["TIGER {}".format(T)] = {}
                conf_dict_total[number]["TIGER {}".format(T)]["Global"] = GEMROC.g_inst.Global_cfg_list[T]
                for ch in range(0, 64):
                    conf_dict_total[number]["TIGER {}".format(T)]["Ch {}".format(ch)] = {}
                    conf_dict_total[number]["TIGER {}".format(T)]["Ch {}".format(ch)] = GEMROC.c_inst.Channel_cfg_list[T][ch]
        if save_txt:
            with open(self.conffile, 'a+') as f:
                f.write(json.dumps(conf_dict_total))
        if save_pickle:
            with open(self.conffile + ".pkl", 'wb+') as f:
                pickle.dump(conf_dict_total, f)

                # print self.GEMROC_reading_dict.items()
            # for number, GEMROC in self.GEMROC_reading_dict.items():
            #     f.write ("\n\n ---  {} configurations   ---\n\n".format(number))
            #     f.write ("\n\n ---  DAQ configurations  ---\n\n".format(number))
            #     f.write(json.dumps(GEMROC.GEM_COM.gemroc_DAQ_XX.DAQ_config_dict))
            #     for T in range (0,8):
            #         f.write("\n\n ---  GEMROC {} TIGER {} global configurations  ---\n\n".format(number,T))
            #         f.write(json.dumps(GEMROC.g_inst.Global_cfg_list[T]))
            #         f.write("\n\n ---  GEMROC {} TIGER {} Channel configurations  ---\n\n".format(number,T))
            #         for ch in range(0, 64):
            #             f.write("\n\n GEMROC {} TIGER {} Channel {} ---\n\n".format(number,T,ch))
            #
            #             f.write(json.dumps(GEMROC.c_inst.Channel_cfg_list[T][ch]))

    def plotta(self):
        if self.simple_analysis.get() or self.run_analysis.get():
            if self.GEM_to_read_last[self.plotting_gemroc] == 1:
                for i in range(0, len(self.GEM)):
                    if int(self.GEM[i].GEMROC_ID) == self.plotting_gemroc:
                        self.plot_rate.set_title("TIGER {}, GEMROC {}".format(self.plotting_TIGER, self.plotting_gemroc))
                        self.scatter.set_ydata(self.GEM[i].thr_scan_rate[self.plotting_TIGER])
                        self.plot_rate.set_ylim(top=np.max(self.GEM[i].thr_scan_rate[self.plotting_TIGER]) + np.max(self.GEM[i].thr_scan_rate[self.plotting_TIGER] / 20))

            else:
                self.plot_rate.set_title("GEMROC not acquired".format(self.plotting_TIGER, self.plotting_gemroc))
                self.scatter.set_ydata(np.zeros((64)))
        self.canvas.draw()
        self.canvas.flush_events()

    def convert0(self):
        for i in range(0, len(self.GEM_to_read)):
            if self.GEM_to_read[i] == 1:
                self.LED[i]["image"] = self.icon_on
            else:
                self.LED[i]["image"] = self.icon_off

    def toggle(self, i):
        if self.GEM_to_read[i] == 0:
            self.GEM_to_read[i] = 1
        else:
            self.GEM_to_read[i] = 0
        self.convert0()

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
        self.FEB_label['text'] = "FEB {}".format(int(round((self.plotting_TIGER + self.plotting_gemroc * 8) / 2)))
        self.refresh_plot()

    def refresh_plot(self):
        self.LBGEM['text'] = 'GEMROC {}'.format(self.plotting_gemroc)
        self.LBTIG['text'] = 'TIGER {}'.format(self.plotting_TIGER)
        self.plotta()

    def switch_mode(self):
        if self.mode == 'TL':
            self.mode = 'TM'
            self.but7['text'] = "Trigger match file name"
            self.but7['background'] = '#ccff99'
            self.but7['activebackground'] = '#ccff99'


        else:
            self.mode = 'TL'
            self.but7['text'] = "Trigger less file name"
            self.but7['background'] = '#ccffff'
            self.but7['activebackground'] = '#ccffff'

    def runna(self):
        mainloop()

    def check_sub_run(self):
        if glob.glob("." + sep + "data_folder" + sep + self.run_folder + sep + "ACQ_log*"):
            numbers = [int(name.split("ACQ_log")[1].split("_")[1]) for name in glob.glob("." + sep + "data_folder" + sep + self.run_folder + sep + "ACQ_log*")]
            max = np.max(numbers)
            self.sub_run_number = max + 1
        else:
            self.sub_run_number = 0

        print("Sub_run={}".format(self.sub_run_number))

    def start_acq(self, First_launch=True):
        self.check_sub_run()
        self.logfile = "." + sep + "data_folder" + sep + self.run_folder + sep + "ACQ_log_{}".format(self.sub_run_number)

        self.LED_UDP['image'] = self.icon_on
        Ok = True
        if First_launch:
            self.reset_810 = 0
            self.reset_timedout = 0
            if self.online_monitor.get():
                Ok = self.preliminary_checks()

        if not Ok:
            return 0
        if self.save_conf_every_run.get():
            self.conffile = "." + sep + "data_folder" + sep + self.run_folder + sep + "CONF_log_{}".format(self.sub_run_number)
        else:
            self.conffile = "." + sep + "data_folder" + sep + self.run_folder + sep + "CONF_run_{}".format(self.run_folder.split("_")[1])
        if not self.std_alone:
            self.save_conf_registers()
            self.log_disabled_channels()
        self.but7.config(state='disabled')
        self.but6.config(state='disabled')
        for i in range(0, len(self.GEM)):
            if self.thread[i].isAlive():
                self.thread[i].join()
                self.GEM[i].__del__()

        self.GEM = []
        self.thread = []

        self.time = self.time_in.get()
        lista = []
        if not self.std_alone:
            for number, GEMROC in self.GEMROC_reading_dict.items():
                with open(self.logfile, 'a+') as f:
                    f.write("{} -- {} Thr set : {} \n".format(time.ctime(), number, GEMROC.thr))

        for i in range(0, len(self.GEM_to_read)):
            if self.GEM_to_read[i] == 1:
                lista.append(i)
                self.GEM.append(GEM_ACQ.reader(i, self.logfile, self.online_monitor_data.get()))
                with open(self.logfile, 'a+') as f:
                    f.write("{} -- Acquiring from GEMROC {} in {} mode\n".format(time.ctime(), i, self.mode))
                print("Acquiring from GEMROC {} in {} mode".format(i, self.mode))

        # self.Launch_error_check['text']="Acquiring from GEMROCs: {} in {} mode\n".format(lista,self.mode)

        for i in range(0, len(self.GEM)):
            if self.mode == 'TL':
                self.thread.append(GEM_ACQ.Thread_handler("GEM ".format(i), float(self.time), self.GEM[i], sub_folder=self.run_folder, sub_run_number=self.sub_run_number))

            else:
                self.thread.append(GEM_ACQ.Thread_handler_TM("GEM ".format(i), self.GEM[i], sub_folder=self.run_folder, sub_run_number=self.sub_run_number))
        if not self.std_alone:
            self.error_thread = (Thread_handler_errors(self.GEMROC_reading_dict, self.GEM, self.errors_counters_810, self))
        self.GEM_to_read_last = self.GEM_to_read
        for i in range(0, len(self.GEM)):
            self.thread[i].start()
        if not self.std_alone:
            self.error_thread.start()
        time.sleep(0.5)
        self.messagge_field['text'] = "Acquiring"

    def log_disabled_channels(self):
        with open("." + sep + "data_folder" + sep + self.run_folder + sep + "disabled_channels", 'w+') as f:
            print("#G   T   ch")
            for number, GEMROC in self.GEMROC_reading_dict.items():
                    for T in range(0,8):
                        for ch in range(0,64):
                            if GEMROC.c_inst.Channel_cfg_list[T][ch]["TriggerMode"]==3:
                                f.write("{}  {}  {}\n".format(GEMROC.GEMROC_ID, T, ch))


    def preliminary_checks(self):

        """
        Checks if the thresholds are not too far from the refenrece values

        :return:
        """
        th_tollerance = (int(self.vth_t_toll.get()), int(self.vth_e_toll.get()))
        numb_of_toll_channels = int(self.numb_of_viol.get())
        if self.check_thr.get():
            thr_out_of_position = 0
            buff = ""
            for numb, value in enumerate(self.GEM_to_read):
                if value == 1:
                    number = "GEMROC {}".format(numb)
                    GEMROC = self.GEMROC_reading_dict[number]
                    filename = GEMROC.GEM_COM.conf_folder + sep + "thr" + sep + "GEMROC{}_reference_vth".format(GEMROC.GEM_COM.GEMROC_ID)
                    if os.path.exists(filename):
                        with open(filename, 'r') as f:
                            for line in f.readlines():
                                splitted = line.replace(" ", ":").split(":")
                                if self.DCT_matrix[GEMROC.GEMROC_ID][int(splitted[1])]!=1:
                                    diff_T = int(splitted[5]) - GEMROC.c_inst.Channel_cfg_list[int(splitted[1])][int(splitted[3])]['Vth_T1']
                                    diff_E = int(splitted[7]) - GEMROC.c_inst.Channel_cfg_list[int(splitted[1])][int(splitted[3])]['Vth_T2']
                                    if diff_T > th_tollerance[0]:
                                        buff = buff + "{} TIGER {}, CHANNEL {}, thr T at {} from reference\n".format(number, int(splitted[1]), int(splitted[3]), diff_T)
                                        print("{} TIGER {}, CHANNEL {}, thr T at {} from reference\n".format(number, int(splitted[1]), int(splitted[3]), diff_T))
                                        #GEMROC.c_inst.Channel_cfg_list[int(splitted[1])][int(splitted[3])]['Vth_T1'] = int(splitted[5])
                                        thr_out_of_position += 1
                                    if diff_E > th_tollerance[1]:
                                        buff = buff + "{} TIGER {}, CHANNEL {}, thr E at {} from reference\n".format(number, int(splitted[1]), int(splitted[3]), diff_E)
                                        print("{} TIGER {}, CHANNEL {}, thr E at {} from reference".format(number, int(splitted[1]), int(splitted[3]), diff_E))
                                        #GEMROC.c_inst.Channel_cfg_list[int(splitted[1])][int(splitted[3])]['Vth_T2'] = int(splitted[7])
                                        thr_out_of_position += 1
                    else:
                        print("Warning: no reference thr found for {}".format(number))
                        self.messagge_field['text'] = "No reference thr found for {}!!".format(number)
                        self.LED_UDP['image'] = self.icon_bad
                        self.write_in_log("Warning: no reference thr found for {}".format(number))
                        self.master_window.update()
                        time.sleep(0.5)
            if thr_out_of_position > numb_of_toll_channels:
                self.messagge_field['text'] = "{} thr out of reference position by at least {}, stopping acquisition".format(thr_out_of_position, th_tollerance)
                self.LED_UDP['image'] = self.icon_bad
                self.master_window.update()
                self.write_in_log("{} thr out of reference position by at least {}, stopping acq".format(thr_out_of_position, th_tollerance))
                self.write_in_log(buff)
                return False

            elif thr_out_of_position != 0:
                self.messagge_field['text'] = "{} thr out of reference position by at least {}, less than {}, keeps stating acq".format(thr_out_of_position, th_tollerance, numb_of_toll_channels)
                self.master_window.update()
                self.write_in_log("{} thr out of reference position by at least {}:".format(thr_out_of_position, th_tollerance))
                self.write_in_log(buff)
        if self.check_pause.get() or self.check_TM.get():
            for number, GEMROC in self.GEMROC_reading_dict.items():
                TL, pause = self.read_pause_and_TM(GEMROC)
                if TL and self.check_TM.get():
                    self.messagge_field['text'] = "GEMROC in TL mode"
                    self.LED_UDP['image'] = self.icon_bad
                    return False
                if not pause and self.check_pause.get():
                    self.messagge_field['text'] = "GEMROC not paused"
                    self.LED_UDP['image'] = self.icon_bad
                    return False

        self.messagge_field['text'] = "Preliminary checks ok"
        self.LED_UDP['image'] = self.icon_on
        return True

    def read_pause_and_TM(self, GEMROC):
        """
        Function for preliminay checks
        :param GEMROC:
        :return:
        """
        command_reply = GEMROC.GEM_COM.Read_GEMROC_DAQ_CfgReg()
        L_array = array.array('I')
        L_array.fromstring(command_reply)
        L_array.byteswap()

        read_dict = {
            "TL_nTM_ACQ": ((L_array[3] >> 11) & 0x1),
            "DAQPause_Flag": ((L_array[4] >> 1) & 0x1),
        }
        return (read_dict['TL_nTM_ACQ'], read_dict['DAQPause_Flag'])

    def refresh_error_status(self):
        """
        :return:
        """

    def stop_acq(self, auto=False, stop_log=True):
        if not auto:
            self.restart.set(False)
        self.run_analysis.set(False)

        if self.simple_analysis.get():
            print("Stopping and analyzing")
        else:
            print("Stopping")

        self.but6.config(state='normal')

        if not self.std_alone and stop_log:
            self.error_thread.running = False
            self.error_thread.stopper_thr.running = False
            # self.error_thread.raise_exception()
            # self.refresh_8_10_counters_and_TimeOut()
        for thr in self.thread:
            thr.running = False
        print([thr.isAlive() for thr in self.thread])

        while True in [thr.isAlive() for thr in self.thread]:
            print([thr.isAlive() for thr in self.thread])
            print ("At least one alive thread")
            for thr in self.thread:
                if thr.isAlive():
                    print ("Thread {} is alive, joining".format(thr.reader.GEMROC_ID))
                    thr.join(timeout=15)
                if thr.isAlive():
                    print ("Can't join one of the threads (this time)")
                time.sleep (0.1)
            print([thr.isAlive() for thr in self.thread])

        for i in self.GEM:
            if i.TIMED_out == True:
                self.LED[int(i.GEMROC_ID)]['image'] = self.icon_bad
            else:
                self.LED[int(i.GEMROC_ID)]['image'] = self.icon_on
        if not self.std_alone:
            for number, GEMROC in self.GEMROC_reading_dict.items():
                GEMROC.GEM_COM.flush_rcv_socket()
        if self.simple_analysis.get() or self.run_analysis.get():
            # self.build_errors()
            pass
        if self.error_GEMROC.get():
            self.save_GEMROC_errors()
        self.but7.config(state='normal')
        if not auto:
            self.messagge_field['text'] = "Acquisition stopped"
            self.LED_UDP['image'] = self.icon_off
        time.sleep(2)

    def save_GEMROC_errors(self):
        for number, GEMROC in self.GEMROC_reading_dict.items():
            GEMROC.GEM_COM.Access_diagn_DPRAM_read_and_log(0, 1, logtype="not_auto", logpth=self.logfile)

    def build_errors(self):
        self.TM_errors = []
        self.TL_errors = []
        for i in range(0, len(self.GEM)):
            if self.mode == 'TL':
                # self.TL_errors.append(self.GEM[i].check_TL_Frame_TIGERS("./data_folder/Spill_2018_12_11_11_02_03_GEMROC_3.dat"))
                self.TL_errors.append(self.GEM[i].check_TL_Frame_TIGERS(self.GEM[i].datapath))
                # print self.TL_errors
            else:
                # self.TM_errors.append(self.GEM[i].check_TM_continuity("./data_folder/Spill_2019_02_09_07_22_18_GEMROC_10_TM.dat"))
                self.TM_errors.append(self.GEM[i].check_TM_continuity(self.GEM[i].datapath))

                # print self.TM_errors

    def close(self):
        self.master.destroy()
        self.errors.destroy()
        self.plot_window.destroy()

    def send_mail(self, error, subject="DAQ stop"):
        text = error
        os.system("python3 {}send_mail.py '{}' '{}' ".format("lib" + sep, subject, text))

    def send_telegram(self, error):
        pass

    def write_in_log(self, text):
        """
        Just to write on log
        :param text:
        :return:
        """
        with open(self.logfile, 'a') as f:
            f.write(time.ctime() + " -- " + text + "\n")

    def get_total_trig(self):
        trig_tot = np.zeros((22))
        for filename in os.listdir("." + sep + "data_folder" + sep + self.run_folder):
            if "ACQ_log" in filename:
                with open("." + sep + "data_folder" + sep + self.run_folder + sep + filename, 'r') as logf:
                    lines = logf.readlines()
                    for lin in lines:
                        if "Finished saving data" in lin:
                            ROC_N = int(lin.split("GEMROC")[1].split(" ")[1])
                            trig = int(lin.split("=")[1])
                            trig_tot[ROC_N] = trig_tot[ROC_N] + trig
        total = 0
        avg = 0
        for i in range(0, 22):
            if trig_tot[i] != 0:
                print("GEMROC {}, triggers: {}".format(i, trig_tot[i]))
            if self.GEM_to_read[i]:
                # total += trig_tot[i]
                avg = np.min(trig_tot[np.where(trig_tot>0)])
        self.messagge_field['text'] = "Avg number of triggers in this run: {}".format(avg)
        return avg

    def _delete_window(self):
        if not self.std_alone:
            self.father.run_control_Button.config(state='normal')
            self.father.doing_something=False
        self.master_window.destroy()
   #
    # def _destroy(self, event):
    #     print( "destroy")





if __name__ == '__main__':
    Main_menu = menu()
    Main_menu.runna()


class Thread_handler_errors(Thread):  # In order to scan during configuration is mandatory to use multithreading
    def __init__(self, GEM_ROC_reading_dict, GEM, errors_counters_810, caller):
        self.GEMROC_reading_dict = GEM_ROC_reading_dict
        self.number_list = []
        self.running = True
        self.TIGER_error_counters = errors_counters_810
        for istance in GEM:
            self.number_list.append(int(istance.GEMROC_ID))
        self.GEM = GEM
        Thread.__init__(self)
        self.caller = caller
        for key in self.TIGER_error_counters.keys():
            self.TIGER_error_counters[key] = 0

    def run(self):
        if self.caller.mode == 'TM':
            print("Acquiring for {:.2f} seconds".format(float(self.caller.time) * 60))
        self.start_time = time.time()
        check_time = 7
        check_counter = 0
        self.stopper_thr = stopper(self.caller, self.start_time, )
        self.stopper_thr.daemon = True
        self.stopper_thr.start()

        while self.running:
            # if (time.time()-self.start_time)>float(self.caller.time)*60:
            #     self.caller.relaunch_acq()
            time.sleep(0.2)

            if (time.time() - self.start_time) > check_counter * check_time:
                if debug:
                    print ("DEBUG: reading counters @{}".format(time.time()))
                if self.caller.run_analysis.get():
                    self.update_err_and_plot_onrun()
                    time.sleep(1)

                TIGER_LIST = [0, 1, 2, 3, 4, 5, 6, 7]
                for T in TIGER_LIST:
                    process_list = []
                    pipe_list = []
                    for number, GEMROC in self.GEMROC_reading_dict.items():
                        if int(number.split()[1]) in self.number_list:
                            GEMROC.GEM_COM.set_counter(int(T), 1, 0)
                            pipe_in, pipe_out = Pipe()
                            p = Process(target=self.acquire_errors, args=(number, T, pipe_in, False))
                            process_list.append(p)
                            pipe_list.append(pipe_out)
                            p.start()
                            time.sleep(0.01)

                    for process, pipe_out in zip(process_list, pipe_list):

                        # if process.is_alive():
                        if self.running:
                            try:
                                process.join(timeout=2)
                                key, value = pipe_out.recv()

                                if key not in self.TIGER_error_counters.keys():
                                    self.TIGER_error_counters[key] = 0
                                if value != 0 and int(self.TIGER_error_counters[key]) != 16777215:
                                    with open(self.caller.logfile, 'a') as f:
                                        f.write("{} -- {} : {} 8/10 bit errors since last reset\n".format(time.ctime(), key, value))
                                        print("{} -- {} : {} 8/10 bit errors since last reset\n".format(time.ctime(), key, value))
                                self.TIGER_error_counters[key] = value
                            except Exception as e:
                                print("Error controller timeout: {}".format(e))
                        process.terminate()

                process_list_2 = []
                pipe_list_2 = []

                if check_counter % 2 == 0 and self.caller.online_monitor.get():
                    self.check_buffer()
                    for number, GEMROC in self.GEMROC_reading_dict.items():
                        pipe_in, pipe_out = Pipe()
                        p = Process(target=self.caller.db_sender.log_IVT_in_DB, args=(number,self.GEMROC_reading_dict, pipe_in))
                        pipe_list_2.append(pipe_out)
                        process_list_2.append(p)
                        p.start()
                        time.sleep(0.05)

                    for process, pipe_out in zip(process_list_2, pipe_list_2):
                        if self.running:
                            try:
                                process.join(timeout=2)
                                gem_number, FEBs_to_off = pipe_out.recv()
                                if len(FEBs_to_off)>0:
                                    for FEB in FEBs_to_off:
                                        self.shut_down_FEB(self.GEMROC_reading_dict[gem_number].GEM_COM, FEB)
                            except Exception as e:
                                print("IVT logger controller timeout: {}".format(e))

                del process_list_2[:]

                if self.running:
                    self.check_buffer()
                    self.caller.refresh_8_10_counters_and_TimeOut()
                check_counter += 1
        self.stopper_thr.running = False
        if debug:
            print("Error thread stopped")

    def check_buffer(self):
        """
        Check the buffer of the rcv socket, if there is stuff in it, try to empty it
        :return:
        """
        if sys.platform == "linux2":
            # comm=["ss","-a","-u","|","grep","{}:{}".format(GEMROC.GEM_COM.HOST_IP, GEMROC.GEM_COM.HOST_PORT_RECEIVE)]
            comm = ["ss", "-a", "-u", ""]
            buffer_status = subprocess.check_output(comm)
            for line in buffer_status.splitlines():
                if "State" not in line and ("192.168.1.200" in line or "127.0.0.1" in line) and int(line.split()[1]) != 0:
                    print(line)
                    GEMROC_key = "GEMROC {}".format(int(line.split()[3].split(":")[1]) - 58912 - 1)
                    if GEMROC_key in self.GEMROC_reading_dict:
                        self.GEMROC_reading_dict[GEMROC_key].GEM_COM.hard_flush_rcv_socket()

    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        # for id, thread in threading._active.items():
        #     if thread is self:
        #         return id

    def raise_exception(self):
        """
        Raise exception to stop the error thread asyncronuosly
        :return:
        """
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')
        print("Exception raised")

    def update_err_and_plot_onrun(self):
        # self.caller.build_errors()
        # self.caller.refresh_error_status()
        self.caller.refresh_plot()

        # print self.TM_errors

    def acquire_errors(self, GEMROC_num, TIGER, pipe_in, reset, read_IVT=TRUE):
        GEMROC = self.GEMROC_reading_dict[GEMROC_num]
        GEMROC.GEM_COM.set_counter(int(TIGER), 1, 0)
        if reset:
            GEMROC.GEM_COM.reset_counter()
            time.sleep(1)
        counter_value = GEMROC.GEM_COM.GEMROC_counter_get()
        tiger_string = "{} TIGER {}".format(GEMROC_num, TIGER)
        # GEMROC.GEM_COM.flush_rcv_socket()
        pipe_in.send((tiger_string, counter_value))
        pipe_in.close()

    def shut_down_FEB(self, gemcom, num):
        pwr_pattern=gemcom.gemroc_LV_XX.FEB_PWR_EN_pattern
        pwr_pattern = pwr_pattern & ~(1 << num)
        print (pwr_pattern)
        print("SHUT DOWN FEB {}, GEMROC{}".format(num,gemcom.GEMROC_ID))
        self.caller.write_in_log("SHUT DOWN FEB {}, GEMROC{}".format(num,gemcom.GEMROC_ID))
        gemcom.FEBPwrEnPattern_set(pwr_pattern)




class stopper(Thread):  #
    def __init__(self, caller, start_time):
        self.running = True
        Thread.__init__(self)
        self.caller = caller
        self.start_time = start_time
        self.running = True

    def run(self):
        while self.running:
            if self.caller.mode == "TM":
                time_max = float(self.caller.time) * 60
            else:
                time_max = float(self.caller.time)
            if debug:
                print("Elapsed time {}".format(time.time() - self.start_time))
            # print (time_max)
            if (time.time() - self.start_time) > (time_max):
                self.caller.reset_810 = 0  # The stopper resets the reset counter if the subrun finished well
                self.caller.reset_timedout = 0
                if debug:
                    print("Out of time")
                try:
                    if debug:
                        print("Stopping and relaunching")
                    self.caller.relaunch_acq()
                except Exception as e:
                    if debug:
                        print("Something wrong: ").format(e)
                    time.sleep(10)
                    self.caller.relaunch_acq()
                    return 0
                return 0
            time.sleep(0.5)


def all_children(window):
    _list = window.winfo_children()

    for item in _list:
        if item.winfo_children():
            _list.extend(item.winfo_children())

    return _list


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

