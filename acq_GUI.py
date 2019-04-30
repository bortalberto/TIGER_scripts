from Tkinter import *
import numpy as np
from lib import GEM_ACQ_classes as GEM_ACQ
import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import communication_error_GUI as error_GUI
import time
from threading import Thread
from multiprocessing import Process, Pipe

import os

OS = sys.platform
if OS == 'win32':
    sep = '\\'
elif OS == 'linux2':
    sep = '/'
else:
    print("ERROR: OS {} non compatible".format(OS))
    sys.exit()


# TODO:
# Red dot if timedout (per acquizione e config)

class menu():
    def __init__(self, std_alone=True, main_winz=None, GEMROC_reading_dict=None,father=None):
        self.father=father
        self.restart=True
        self.PMT=False
        self.std_alone = std_alone
        self.GEM_to_read = np.zeros((20))
        self.GEM_to_read_last = np.zeros((20))
        self.errors_counters_810 = {}
        # for i in range (0,20):
        #     self.errors_counters_810[i]=i*20
        self.logfile = "." + sep + "log_folder" + sep + "ACQ_log_{}".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        self.mode = 'TL'
        self.LED = []
        self.FIELD_TIGER = []
        self.LED_UDP = []
        self.plotting_gemroc = 0
        self.plotting_TIGER = 0
        self.time = 2
        self.GEM = []

        if std_alone:
            self.master_window = Tk()
            self.master_window.title("GEMROC acquisition")
        else:
            self.master_window = Toplevel(main_winz)
            self.main_winz = main_winz
            self.GEMROC_reading_dict = GEMROC_reading_dict

        self.simple_analysis = IntVar(self.master_window)
        self.run_analysis = IntVar(self.master_window)


        Label(self.master_window, text='Acquisition setting', font=("Courier", 25)).pack()

        self.master = Frame(self.master_window)
        self.master.pack()
        self.icon_on = PhotoImage(file="." + sep + 'icons' + sep + 'on.gif')
        self.icon_off = PhotoImage(file="." + sep + 'icons' + sep + 'off.gif')
        self.icon_bad = PhotoImage(file="." + sep + 'icons' + sep + 'bad.gif')
        self.grid_frame = Frame(self.master_window)
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

        self.start_frame = Frame(self.master_window)
        self.start_frame.pack()
        Label(self.start_frame, text="Trigger less acq time (seconds)").grid(row=0, column=0, sticky=NW, pady=4)
        self.time_in = Entry(self.start_frame, width=3)
        self.time_in.insert(END, '1')
        self.time_in.grid(row=0, column=1, sticky=NW, pady=4)
        Checkbutton(self.start_frame, text="Fast analysis", variable=self.simple_analysis).grid(row=0, column=2, sticky=NW, pady=4)
        Checkbutton(self.start_frame, text="On run analysis", variable=self.run_analysis).grid(row=0, column=3, sticky=NW, pady=4)


        a_frame = Frame(self.master_window)
        a_frame.pack()
        self.but6 = Button(a_frame, text='Start acquisition', command=self.start_acq)
        self.but6.grid(row=1, column=2, sticky=NW, pady=4)
        self.but7 = Button(a_frame, text='Trigger less acquisition', command=self.switch_mode, background='#ccffff', activebackground='#ccffff', height=1, width=18)
        self.but7.grid(row=1, column=3, sticky=NW, pady=4)
        self.but8 = Button(a_frame, text='Stop acquisition', command=self.stop_acq, state='normal')
        b_frame = LabelFrame(a_frame)
        b_frame.grid(row=1, column=8, sticky=NW, pady=4,padx=40)
        if self.PMT:
            Button(b_frame, text='Turn ON PMTs', command=self.PMT_on,   width=10,activeforeground="green").pack(side=LEFT)
            Button(b_frame, text='Turn OFF PMTs', command=self.PMT_OFF,  width=10,activeforeground="red").pack(side=LEFT)

        # Label(b_frame,text='Message ').grid(row=0, column=1, sticky=NW, pady=4)
        # self.Launch_error_check=Label(b_frame, text='-', background='white')
        # self.Launch_error_check.grid(row=0, column=2, sticky=NW, pady=4)
        # Button(self.master,text='Exit', command='close').place(relx=0.9, rely=0.9, anchor=NW)
        # Button(a_frame, text='Communication errorinterfacee',command=error_GUI)

        self.but8.grid(row=1, column=4, sticky=NW, pady=4)
        for i in range(0, len(self.GEM_to_read)):
            if i < 10:
                riga = 0
            else:
                riga = 1

            colonna = ((i) % 10) * 2 + 1
            self.LED.append(Label(self.grid_frame, image=self.icon_off))
            self.LED[i].grid(row=riga, column=colonna)

        self.errors = Frame(self.master_window)
        self.errors.pack()
        self.LBerror = Label(self.errors, text='Acquisition errors check', font=("Courier", 25))
        self.LBerror.grid(row=0, column=0, columnspan=8, sticky=S, pady=5)
        self.butleftG_err = Button(self.errors, text='<', command=lambda: self.change_G_or_T(-1, "G")).grid(row=1, column=0, sticky=S, pady=4)
        self.LBGEM_err = Label(self.errors, text='GEMROC {}'.format(self.plotting_gemroc), font=("Courier", 14))
        self.LBGEM_err.grid(row=1, column=1, sticky=S, pady=4)
        self.butrightG_err = Button(self.errors, text='>', command=lambda: self.change_G_or_T(1, "G")).grid(row=1, column=2, sticky=S, pady=4)

        self.LBUDP0 = Label(self.errors, text='UDP packet error  ')
        self.LBUDP0.grid(row=2, column=1, sticky=S, pady=4)
        Label(self.errors, text='  TIGER missing').grid(row=2, column=2, sticky=S, pady=4)
        if not self.std_alone:
            self.open_adv_acq()

        self.LED_UDP = Label(self.errors, image=self.icon_off)
        self.LED_UDP.grid(row=4, column=1)
        self.FIELD_TIGER = Label(self.errors, text='-', background='white')
        self.FIELD_TIGER.grid(row=4, column=2)

        self.plot_window = Frame(self.master_window)
        self.plot_window.pack()
        # self.plot_window.geometry('900x800')
        self.corn0 = Frame(self.plot_window)
        self.corn0.pack()
        self.LBOCC = Label(self.corn0, text='Channel occupancy', font=("Times", 18))
        self.LBOCC.grid(row=0, column=1, sticky=S, pady=4)
        self.butleftG = Button(self.corn0, text='<', command=lambda: self.change_G_or_T(-1, "G")).grid(row=1, column=0, sticky=S, pady=4)
        self.LBGEM = Label(self.corn0, text='GEMROC {}'.format(self.plotting_gemroc), font=("Courier", 14))
        self.LBGEM.grid(row=1, column=1, sticky=S, pady=4)
        self.butrightG = Button(self.corn0, text='>', command=lambda: self.change_G_or_T(1, "G")).grid(row=1, column=2, sticky=S, pady=4)
        self.butleftT = Button(self.corn0, text='<', command=lambda: self.change_G_or_T(-1, "T")).grid(row=2, column=0, sticky=S, pady=4)
        self.LBTIG = Label(self.corn0, text='TIGER {}'.format(self.plotting_TIGER), font=("Courier", 14))
        self.LBTIG.grid(row=2, column=1, sticky=S, pady=4)
        self.butrightT = Button(self.corn0, text='>', command=lambda: self.change_G_or_T(1, "T")).grid(row=2, column=2, sticky=S, pady=4)
        self.corn1 = Frame(self.plot_window)
        self.corn1.pack()

        # Plot
        x = np.arange(0, 64)
        v = np.zeros((64))

        self.fig = Figure(figsize=(7, 7))
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
        for number, GEMROC in self.GEMROC_reading_dict.items():
            n=int(number.split()[1])
            self.toggle(n)
    def open_adv_acq(self):
        self.adv_wind = Toplevel(self.main_winz)
        self.error_dict810 = {}
        seconfF=Frame(self.adv_wind)
        seconfF.pack()
        firstF = Frame(self.adv_wind)
        firstF.pack()
        Label(firstF,text='Acquisiton set single TIGERs',font=("Courier", 16)).pack()
        self.button_dict={}
        for number, GEMROC in self.GEMROC_reading_dict.items():
            a = Frame(firstF)
            a.pack()
            Label(a, text='{} TIGERs:   '.format(number)).grid(row=0, column=0, sticky=NW, pady=4)
            for T in range(0, 8):
                self.button_dict["{} TIGER {}".format(number,T)]=Button(a, text='{}'.format(T),width=10,command=lambda (number,T)=(number,T): self.Change_Reading_Tigers((number,T)) )
                self.button_dict["{} TIGER {}".format(number, T)].grid(row=0, column=T+1, sticky=NW, pady=4)
            Label(a, text='{} Err(8/10):   '.format(number)).grid(row=1, column=0, sticky=NW, pady=4)
            for T in range(0, 8):
                    self.error_dict810["{} TIGER {}".format(number, T)]=Label(a,text="-------",width=11)
                    self.error_dict810["{} TIGER {}".format(number, T)].grid(row=1, column=T+1, sticky=NW, pady=4)


        self.refresh_but_TIGERs()

    def Change_Reading_Tigers(self,(number,T)):

        n=(self.GEMROC_reading_dict[number].GEM_COM.gemroc_DAQ_XX.EN_TM_TCAM_pattern >> T) & 0x1
        if n==1:
            self.GEMROC_reading_dict[number].GEM_COM.gemroc_DAQ_XX.EN_TM_TCAM_pattern -=2**T
        else:
            self.GEMROC_reading_dict[number].GEM_COM.gemroc_DAQ_XX.EN_TM_TCAM_pattern +=2**T
        self.GEMROC_reading_dict[number].GEM_COM.DAQ_set_register()
        self.refresh_but_TIGERs()

    def refresh_but_TIGERs(self):
        for number, GEMROC in self.GEMROC_reading_dict.items():
            for T in range (0,8):
                n=(self.GEMROC_reading_dict[number].GEM_COM.gemroc_DAQ_XX.EN_TM_TCAM_pattern >> T) & 0x1
                if n == 1:
                    self.button_dict["{} TIGER {}".format(number,T)]['background'] = '#0099ff'
                    self.button_dict["{} TIGER {}".format(number,T)]['activebackground'] = '#0099ff'
                else:
                    self.button_dict["{} TIGER {}".format(number, T)]['background'] = '#e6e6e6'
                    self.button_dict["{} TIGER {}".format(number, T)]['activebackground'] = '#e6e6e6'

    def refresh_8_10_counters_and_TimeOut(self):
        for key, label in self.error_dict810.items():
            try:
                label['text']=self.errors_counters_810[key]
            except:
                label['text'] ="-----"
        for i in self.GEM:
            if i.TIMED_out == True:
                self.LED[int(i.GEMROC_ID)]['image'] = self.icon_bad
                with open(self.logfile, 'a') as f:
                    f.write("{} -- GEMROC {} Timed_out\n".format(time.ctime(), i, self.mode))
            else:
                self.LED[int(i.GEMROC_ID)]['image'] = self.icon_on
        for i in self.GEM:
            if i.TIMED_out and self.restart:
                self.relaunch_acq()
                break
    def PMT_on(self):
        os.system("./HVWrappdemo ttyUSB0 VSet 2000")

    def PMT_OFF(self):
        os.system("./HVWrappdemo ttyUSB0 VSet 500")

    def relaunch_acq(self):
        self.stop_acq(True)
        if self.restart:

            if self.PMT:
                self.PMT_off()

            self.father.Synch_reset()
            self.father.power_off_FEBS()
            self.father.power_on_FEBS()
            self.father.Synch_reset()
            self.father.load_default_config()
            self.father.load_default_config()
            self.father.Synch_reset()
            time.sleep(0.2)
            self.father.set_pause_mode(to_all=True,value=1)
            self.father.Synch_reset()

            if self.PMT:
                self.PMT_on()

            self.start_acq()

    def ref_adv_acq(self):
        widget_list = all_children(self.adv_wind)
        for item in widget_list:
            item.pack_forget()
        self.refresh_but_TIGERs()


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

        self.refresh_plot()

    def refresh_plot(self):
        self.LBGEM['text'] = 'GEMROC {}'.format(self.plotting_gemroc)
        self.LBTIG['text'] = 'TIGER {}'.format(self.plotting_TIGER)
        self.plotta()
        self.refresh_error_status()

    def switch_mode(self):
        if self.mode == 'TL':
            self.mode = 'TM'
            self.but7['text'] = "Trigger match acquisition"
            self.but7['background'] = '#ccff99'
            self.but7['activebackground'] = '#ccff99'


        else:
            self.mode = 'TL'
            self.but7['text'] = "Trigger less acquisition"
            self.but7['background'] = '#ccffff'
            self.but7['activebackground'] = '#ccffff'

    def runna(self):
        mainloop()

    def start_acq(self):
        self.restart=True
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
        for i in range(0, len(self.GEM_to_read)):
            if self.GEM_to_read[i] == 1:
                lista.append(i)
                self.GEM.append(GEM_ACQ.reader(i, self.logfile))
                with open(self.logfile, 'a') as f:
                    f.write("{} -- Acquiring from GEMROC {} in {} mode\n".format(time.ctime(), i, self.mode))
                print ("Acquiring from GEMROC {} in {} mode".format(i, self.mode))
        # self.Launch_error_check['text']="Acquiring from GEMROCs: {} in {} mode\n".format(lista,self.mode)

        for i in range(0, len(self.GEM)):
            if self.mode == 'TL':
                self.thread.append(GEM_ACQ.Thread_handler("GEM ".format(i), float(self.time), self.GEM[i]))

            else:
                self.thread.append(GEM_ACQ.Thread_handler_TM("GEM ".format(i), self.GEM[i]))
        if not self.std_alone:
            self.error_thread = (Thread_handler_errors(self.GEMROC_reading_dict, self.GEM, self.errors_counters_810,self))
        self.GEM_to_read_last = self.GEM_to_read
        for i in range(0, len(self.GEM)):
            self.thread[i].start()
        if not self.std_alone:
            self.error_thread.start()

    def refresh_error_status(self):
        self.LBGEM_err['text'] = 'GEMROC {}'.format(self.plotting_gemroc)
        if self.simple_analysis.get() or self.run_analysis.get():
            if self.GEM_to_read_last[self.plotting_gemroc] == 1:

                for i in range(0, len(self.GEM)):
                    if int(self.GEM[i].GEMROC_ID) == self.plotting_gemroc:
                        if self.mode == 'TM':

                            if len(self.TM_errors[i][1]) > 0:
                                self.LED_UDP['image'] = self.icon_bad
                            else:
                                self.LED_UDP['image'] = self.icon_on
                            for i in range(0, len(self.GEM)):
                                for j in range(0, 8):
                                    self.FIELD_TIGER['text'] = '{}'.format(self.TM_errors[i][0])
                            self.LBUDP0['text'] = "UDP packet error  "

                            self.LBerror['text'] = "Acquisition errors check(TM) "

                        if self.mode == 'TL':

                            if len(self.TL_errors[i][1]) > 0:
                                self.LED_UDP['image'] = self.icon_bad
                            else:
                                self.LED_UDP['image'] = self.icon_on
                            for i in range(0, len(self.GEM)):
                                for j in range(0, 8):
                                    self.FIELD_TIGER['text'] = '{}'.format(self.TL_errors[i][0])
                            self.LBUDP0['text'] = "Frameword missing   "

                            self.LBerror['text'] = "Acquisition errors check(TL) "
            else:
                self.LBerror['text'] = "GEMROC not acquired "
                self.LED_UDP['image'] = self.icon_off
                self.FIELD_TIGER['text'] = '-'
        else:
            self.LBerror['text'] = "Data not analyzed "
            self.LED_UDP['image'] = self.icon_off
            self.FIELD_TIGER['text'] = '-'
        #self.FIELD_810['text'] = '{}'.format(int(self.errors_counters_810[self.plotting_gemroc])) TODO check later

    def stop_acq(self, auto=False):
        if not auto:
            self.restart=False
        if self.simple_analysis.get():
            print "Stopping analizing"
        else:
            print "Stopping"
        self.but6.config(state='normal')
        if not self.std_alone:
            self.error_thread.running = False
            #self.refresh_8_10_counters_and_TimeOut()
        for i in range(0, len(self.GEM)):
            self.thread[i].running = False

        for i in range(0, len(self.GEM)):
            if self.thread[i].isAlive():
                self.thread[i].join()
        for i in self.GEM:
            if i.TIMED_out == True:
                self.LED[int(i.GEMROC_ID)]['image'] = self.icon_bad
            else:
                self.LED[int(i.GEMROC_ID)]['image'] = self.icon_on
        if self.simple_analysis.get() or self.run_analysis.get():
            self.build_errors()
        self.refresh_error_status()
        self.refresh_plot()
        self.but7.config(state='normal')

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
        self.destroy()


if __name__ == '__main__':
    Main_menu = menu()
    Main_menu.runna()


class Thread_handler_errors(Thread):  # In order to scan during configuration is mandatory to use multithreading
    def __init__(self, GEM_ROC_reading_dict, GEM, errors_counters_810,caller):
        self.GEMROC_reading_dict = GEM_ROC_reading_dict
        self.number_list = []
        self.running = True
        self.TIGER_error_counters = errors_counters_810
        for istance in GEM:
            self.number_list.append(int(istance.GEMROC_ID))
        self.GEM=GEM
        Thread.__init__(self)
        self.caller=caller
    def run(self):
        while self.running:
            time.sleep(30)
            if self.caller.run_analysis.get():
                self.update_err_and_plot_onrun()
            process_list = []
            pipe_list = []
            TIGER_LIST = [0, 1, 2, 3, 4, 5, 6, 7]
            for T in TIGER_LIST:
                for number, GEMROC in self.GEMROC_reading_dict.items():
                    if int(number.split()[1]) in self.number_list:
                        GEMROC.GEM_COM.set_counter(int(T), 1, 0)
                        pipe_in, pipe_out = Pipe()
                        p = Process(target=self.acquire_errors, args=(number, T, pipe_in, False))
                        process_list.append(p)
                        pipe_list.append(pipe_out)
                        p.start()
                        time.sleep(0.001)
            for process, pipe_out in zip(process_list, pipe_list):
                #if process.is_alive():
                    process.join()
                    try:
                        key, value = pipe_out.recv()
                        if value!=0 :
                        # if value!=0 and (self.caller.GEMROC_reading_dict[key]):
                            with open(self.caller.logfile, 'a') as f:
                                f.write("{} -- {} : {} 8/10 bit errors in the last 20 seconds\n".format(time.ctime(), key,value ))
                            number=key.split()[0]+" "+key.split()[1]
                            #self.caller.relaunch_acq()

                            # GEMROC=self.GEMROC_reading_dict[number]
                            # GEMROC.GEM_COM.SynchReset_to_TgtFEB()
                            # GEMROC.GEM_COM.SynchReset_to_TgtTCAM()
                        self.TIGER_error_counters[key] = value

                    except Exception as e:
                        print e
                    process.terminate()
            self.caller.refresh_8_10_counters_and_TimeOut()
            del process_list[:]
            del pipe_list[:]
    def update_err_and_plot_onrun(self):
        self.caller.build_errors()
        self.caller.refresh_error_status()
        self.caller.refresh_plot()

                    #print self.TM_errors
    def acquire_errors(self, GEMROC_num, TIGER, pipe_in, reset):
        GEMROC = self.GEMROC_reading_dict[GEMROC_num]
        if reset:
            GEMROC.GEM_COM.reset_counter()
            time.sleep(1)
        counter_value = GEMROC.GEM_COM.GEMROC_counter_get()
        tiger_string = "{} TIGER {}".format(GEMROC_num, TIGER)
        pipe_in.send((tiger_string, counter_value))
        pipe_in.close()



def all_children(window):
    _list = window.winfo_children()

    for item in _list:
        if item.winfo_children():
            _list.extend(item.winfo_children())

    return _list
