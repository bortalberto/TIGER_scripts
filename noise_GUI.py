from Tkinter import *
from ttk import Progressbar
import Tkinter, Tkconstants, tkFileDialog
from scipy.optimize import curve_fit
from scipy import special
import math
import numpy as np
from multiprocessing import Process,Pipe
import time
from lib import GEM_ANALYSIS_classes as AN_CLASS, GEM_CONF_classes as GEM_CONF
import sys
import array
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

TP_rate = 68000

#TODO check on TIGER number
def errorfunc(x, x0, sig, c):
    y = (special.erf((x - x0) / (1.4142 * sig))) * c / 2 + 0.5 * c
    return y
def double_error_func(x,x0,x1,sig0,sig1,c0,c1):
    y=errorfunc(x,x0,sig0,c0)+errorfunc(x,x1,sig1,c1)
    return y

def gaussian(x, mu, sig,c,norm ):
    if len(x)==1:
        y=norm/(sig*math.pi**(1/2))*math.exp((-(x - mu)**2) / (2 * sig**2))+c
    else:
        i=0
        y = np.zeros((len(x)))
        for xi in x:
            y[i]=norm/(sig*math.pi**(1/2))*math.exp((-(xi - mu)**2) / (2 * sig**2))+c
            i+=1
    return y

class menu():
    def __init__(self,main_window,gemroc_handler):
        self.scan_matrixs={}
        self.fits={}
        self.TPfits={}
        self.covs={}
        self.TPcovs={}
        self.chi = {}
        self.TPchi= {}
        self.gaussians={}

        self.GEMROC_reading_dict=gemroc_handler
        self.error_window_main = Toplevel(main_window)
        self.error_window=Frame(self.error_window_main)
        self.error_window.pack(side=LEFT,pady=10,padx=10)

        Label(self.error_window,text='Noise measure',font=("Courier", 25)).grid(row=0, column=2, sticky=S, pady=4,columnspan=10)
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
        self.TIGER_num_first = IntVar(self.error_window)
        self.TIGER_num_last = IntVar(self.error_window)
        self.CHANNEL_num_first = IntVar(self.error_window)
        self.CHANNEL_num_last = IntVar(self.error_window)



        Label(self.second_row_frame, text='First TIGER   ').pack(side=LEFT)
        Entry(self.second_row_frame, width=4, textvariable=self.TIGER_num_first).pack(side=LEFT)

        Label(self.second_row_frame, text='Last TIGER   ').pack(side=LEFT)
        Entry(self.second_row_frame, width=4, textvariable=self.TIGER_num_last).pack(side=LEFT)

        Label(self.second_row_frame, text='First Channel  ').pack(side=LEFT)
        Entry(self.second_row_frame, width=4, textvariable=self.CHANNEL_num_first).pack(side=LEFT)

        Label(self.second_row_frame, text='Last Channel   ').pack(side=LEFT)
        Entry(self.second_row_frame, width=4, textvariable=self.CHANNEL_num_last).pack(side=LEFT)


        fields_optionsG = self.GEMROC_reading_dict.keys()
        fields_optionsG.append("All")
        OptionMenu(self.first_row, self.GEMROC_num, *fields_optionsG).pack(side=LEFT)
        self.third_row=Frame(self.error_window)
        self.third_row.grid(row=3, column=1, sticky=S, pady=4,columnspan=10)
        Button(self.third_row, text ='Start TP',  command=self.start_TP).pack(side=LEFT,padx=2)

        self.strart_button=Button(self.third_row, text ='Threshold scan',  command=self.noise_scan)
        self.strart_button.pack(side=LEFT,padx=2)
        self.strart_button=Button(self.third_row, text ='Threshold scan on VTH2',  command= lambda: self.noise_scan(True))
        self.strart_button.pack(side=LEFT,padx=2)
        Button(self.third_row, text="Save", command=self.SAVE).pack(side=LEFT,padx=2)
        Button(self.third_row, text="Load", command=self.LOAD).pack(side=LEFT,padx=2)
        Button(self.third_row, text="Fit", command=self.fit).pack(side=LEFT,padx=2)
        Button(self.third_row, text="Save noise levels", command=self.SAVE_noise).pack(side=LEFT,padx=2)
        Button(self.third_row, text="Switch to TP distribution measurment", command=self.switch_to_tp_distr).pack(side=LEFT, padx=25)

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
        self.corn1.grid(row=12, column=1, sticky=S, pady=4,columnspan=100)

        # Plot
        x = np.arange(0, 64)
        v = np.zeros((64))

        self.fig = Figure(figsize=(6,6))
        self.plot_rate = self.fig.add_subplot(111)
        self.scatter, = self.plot_rate.plot(x, v, 'r+')
        self.line, = self.plot_rate.plot(x, v, '-')
        self.line2, = self.plot_rate.plot(x, v, 'r-')
        self.line3, = self.plot_rate.plot(x, v, 'g-')


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
        #
        # for number, GEMROC_number in self.GEMROC_reading_dict.items():
        #     print number
        for i in range (0,21):
            number="GEMROC {}".format(i)
            self.scan_matrixs[number]=np.zeros((8,64,64))
            self.fits[number]={}
            self.TPfits[number]={}

            self.covs[number]={}
            self.TPcovs[number]={}

            self.chi[number]={}
            self.TPchi[number]={}
            self.TP_settings={}
            # self.gaussians[number]={}

            for T in range (0,8):
                self.fits[number]["TIG{}".format(T)]={}
                self.covs[number]["TIG{}".format(T)]={}
                self.TPcovs[number]["TIG{}".format(T)]={}
                self.TPfits[number]["TIG{}".format(T)]={}

                self.chi[number]["TIG{}".format(T)]={}
                self.TPchi[number]["TIG{}".format(T)]={}

                self.TP_settings["TIG{}".format(T)]={}
                # self.gaussians[number]["TIG{}".format(T)] = {}

                for ch in range (0,64):
                    # self.gaussians[number]["TIG{}".format(T)]["CH{}".format(ch)]=(0,0,0,0)
                    self.fits[number]["TIG{}".format(T)]["CH{}".format(ch)] = (0,0,1,1,0,0)
                    self.covs[number]["TIG{}".format(T)]["CH{}".format(ch)] = np.zeros((6,6))
                    self.TPcovs[number]["TIG{}".format(T)]["CH{}".format(ch)] = np.zeros((3,3))
                    self.TPfits[number]["TIG{}".format(T)]["CH{}".format(ch)] = ("Fail","Fail","Fail")

                    self.chi[number]["TIG{}".format(T)]["CH{}".format(ch)] = np.zeros((6,6))
                    self.TPchi[number]["TIG{}".format(T)]["CH{}".format(ch)] = np.zeros((3,3))
                    #self.TP_settings[number]["TIG{}".format(T)]["CH{}".format(ch)] = (25    )

        # self.Conf_Frame=Frame(self.error_window_main)
        # self.Conf_Frame.pack(side=LEFT,pady=10,padx=20)
        # Global_frame=LabelFrame(self.Conf_Frame)
        # Global_frame.grid(row=0,column=0,sticky=N,pady=10,padx=10)
        # Label(Global_frame,text="Global configurations").pack()
        # fields_frame=Frame(Global_frame)
        # fields_frame.pack()
        # with open("lib" + sep + "keys" + sep + "global_conf_file_keys", 'r') as f:
        #     i = 0
        #     lenght = len(f.readlines())
        #     # print lenght
        #     f.seek(0)
        #     Label(fields_frame, text="Read").grid(row=1, column=1, sticky=W, pady=0)
        #     Label(fields_frame, text="To load").grid(row=1, column=2, sticky=W, pady=0)
        #     Label(fields_frame, text="Read").grid(row=1, column=4, sticky=W, pady=0)
        #     Label(fields_frame, text="To load").grid(row=1, column=5, sticky=W, pady=0)
        #
        #     for line in f.readlines():
        #         self.field_array.append(Label(fields_frame, text='-'))
        #         self.input_array.append(Entry(fields_frame, width=3))
        #         self.label_array.append(Label(fields_frame, text=line))
        #
        #         if i < lenght / 2:
        #             self.label_array[i].grid(row=i + 2, column=0, sticky=W, pady=0)
        #             self.input_array[i].grid(row=i + 2, column=2, sticky=W, pady=0)
        #             self.field_array[i].grid(row=i + 2, column=1, sticky=W, pady=0)
        #         else:
        #             self.label_array[i].grid(row=i + 2 - lenght / 2, column=3, sticky=W, pady=0)
        #             self.input_array[i].grid(row=i + 2 - lenght / 2, column=5, sticky=W, pady=0)
        #             self.field_array[i].grid(row=i + 2 - lenght / 2, column=4, sticky=W, pady=0)
        #
        #         i += 1
        #
        #
        #
        # ChannelFrame=LabelFrame(self.Conf_Frame)
        # ChannelFrame.grid(row=0,column=1,sticky=N,pady=10,padx=10)
        # Label(ChannelFrame,text="Channel configurations").pack()


    def noise_scan(self,vth2=False):  # if GEMROC num=-1--> To all GEMROC, if TIGER_num=-1 --> To all TIGERs
        self.bar_win = Toplevel(self.error_window)
        #self.bar_win.focus_set()  # set focus on the ProgressWindow
        #self.bar_win.grab_set()
        progress_bars = []
        progress_list = []
        dictio = {}
        GEMROC_n=self.GEMROC_num.get()
        Label(self.bar_win, text="Threshold Scan completition").pack()

        if GEMROC_n == "All":
            dictio = self.GEMROC_reading_dict.copy()
        else:
            dictio["{}".format(GEMROC_n)] = self.GEMROC_reading_dict[GEMROC_n]
        i = 0
        for number, GEMROC_number in dictio.items():
            Label(self.bar_win, text='{}'.format(number)).pack()
            progress_list.append(IntVar())
            maxim = ((self.CHANNEL_num_last.get()-self.CHANNEL_num_first.get()))*(self.TIGER_num_last.get()-self.TIGER_num_first.get())+1
            progress_bars.append(Progressbar(self.bar_win, maximum=maxim, orient=HORIZONTAL, variable=progress_list[i], length=200, mode='determinate'))
            progress_bars[i].pack()

            i += 1
        process_list = []
        pipe_list = []
        i = 0
        for number, GEMROC_num in dictio.items():
            pipe_in, pipe_out = Pipe()
            p = Process(target=self.noise_scan_process, args=(number,  pipe_out,vth2))
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
                        #print ("Can't acquire status")

                    self.bar_win.update()
                    time.sleep(0.1)
                    # print progress.get()

        for process in process_list:
            if process.is_alive():
                process.join()


        for number, GEMROC_num in dictio.items():
            filename=GEMROC_num.GEM_COM.Noise_folder + sep + "GEMROC{}".format(GEMROC_num.GEM_COM.GEMROC_ID) + sep +"scan_matrix"
            with  open(filename, 'rb') as f:
                self.scan_matrixs[number]=pickle.load(f)
        self.plotta()
        self.bar_win.destroy()

        # else:
        #     GEMROC = self.GEMROC_reading_dict["GEMROC {}".format(GEMROC_num)]
        #     GEM_COM = GEMROC.GEM_COM
        #     c_inst = GEMROC.c_inst
        #     g_inst = GEMROC.g_inst
        #     test_r = (AN_CLASS.analisys_conf(GEM_COM, c_inst, g_inst))

    def noise_scan_process(self, number,  pipe_out,vth2):
        scan_matrix=np.zeros((8,64,64))
        GEMROC = self.GEMROC_reading_dict[number]
        GEM_COM = GEMROC.GEM_COM
        c_inst = GEMROC.c_inst
        g_inst = GEMROC.g_inst
        test_c = AN_CLASS.analisys_conf(GEM_COM, c_inst, g_inst)
        test_r = AN_CLASS.analisys_read(GEM_COM, c_inst)
        first = self.TIGER_num_first.get()
        last = self.TIGER_num_last.get()+1
        firstch = self.CHANNEL_num_first.get()
        lastch = self.CHANNEL_num_last.get()+1
        GEMROC_ID = GEM_COM.GEMROC_ID



        for T in range(first,last):#TIGER
            for J in range (firstch,lastch):#Channel
                for i in range (0,64):#THR
                    scan_matrix[T,J,i]=test_c.noise_scan_using_GEMROC_COUNTERS_progress_bar(T,J, i,False,vth2)
                position = ((T-first) * (lastch-firstch)+1) + (J)
                pipe_out.send(position)


        test_r.thr_scan_matrix=scan_matrix
        test_r.thr_scan_rate=scan_matrix*10
        test_r.colorPlot(GEM_COM.Noise_folder + sep + "GEMROC{}".format(GEMROC_ID) + sep + "GEMROC {}".format(GEMROC_ID) + "rate", first, last, True)
        test_r.colorPlot(GEM_COM.Noise_folder + sep + "GEMROC{}".format(GEMROC_ID) + sep + "GEMROC {}".format(GEMROC_ID) + "conteggi", first, last)

        filename=GEM_COM.Noise_folder + sep + "GEMROC{}".format(GEMROC_ID) + sep +"scan_matrix"
        with  open(filename,'wb') as f:
            pickle.dump(test_r.thr_scan_rate,f)


        print "GEMROC {} done".format(GEMROC_ID)
        position = (last * (lastch-firstch) + 1) + (lastch)
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
    def plotta(self):
        for number, GEMROC_number in self.GEMROC_reading_dict.items():
            if int(number.split()[1]) == int(self.plotting_gemroc):

                self.plot_rate.set_title("ROC {},TIG {}, CH {} ".format(self.plotting_gemroc, self.plotting_TIGER,self.plotting_Channel))
                self.scatter.set_ydata(self.scan_matrixs[number][self.plotting_TIGER,self.plotting_Channel])
                self.plot_rate.set_ylim(top=np.max(self.scan_matrixs[number][self.plotting_TIGER,self.plotting_Channel])+ np.max(self.scan_matrixs[number][self.plotting_TIGER,self.plotting_Channel])*0.2)
                parameters=self.fits[number]["TIG{}".format(self.plotting_TIGER)]["CH{}".format(self.plotting_Channel)]
                TPparameters=self.TPfits[number]["TIG{}".format(self.plotting_TIGER)]["CH{}".format(self.plotting_Channel)]
                # base_parameters=self.gaussians[number]["TIG{}".format(self.plotting_TIGER)]["CH{}".format(self.plotting_Channel)][0]
                # print "Chi1 {}".format(self.chi[number]["TIG{}".format(self.plotting_TIGER)]["CH{}".format(self.plotting_Channel)])
                # print "Chi2 {}".format(self.TPchi[number]["TIG{}".format(self.plotting_TIGER)]["CH{}".format(self.plotting_Channel)])
                y=np.zeros((64))
                TPy=np.zeros((64))
                gauspnts=np.zeros((64))

                for x in range (0,64):
                    y[x]=double_error_func(x,*parameters)
                    if TPparameters[0]!="Fail":
                        noise = round(convert_to_fC(TPparameters[1], 55),2)
                    else:
                        noise= "Canno't fit"

                self.line.set_ydata(y)
                self.line2.set_ydata(TPy)
                self.line3.set_ydata(gauspnts)
                # print "First fit {}".format(parameters[2])
                # print "Second fit {}".format(TPparameters[1])
                self.plot_rate.set_title("ROC {},TIG {}, CH {} , Sigma Noise={} fC".format(self.plotting_gemroc, self.plotting_TIGER,self.plotting_Channel,noise))

                break
            else:
                self.plot_rate.set_title("GEMROC not active")
                self.scatter.set_ydata(np.zeros((64)))
        self.canvas.draw()
        self.canvas.flush_events()
    def SAVE(self):
        File_name = tkFileDialog.asksaveasfilename(initialdir="." + sep + "noise_scan" + sep + "saves", title="Select file", filetypes=(("Noise scan files", "*.ns"), ("all files", "*.*")))
        with  open(File_name, 'wb') as f:
            pickle.dump(self.scan_matrixs,f)


    def LOAD(self):
        filename = tkFileDialog.askopenfilename(initialdir="." + sep + "noise_scan" + sep + "saves", title="Select file", filetypes=(("Noise scan files", "*.ns"), ("all files", "*.*")))
        with  open(filename, 'rb') as f:
            self.scan_matrixs=pickle.load(f)

    def fit(self):
        for GEMROC,matrix in self.scan_matrixs.items():
            for TIG in range (0,8):
                for channel in range (0,64):
                    if any(matrix[TIG][channel]) != 0:
                        values=error_fit(matrix[TIG][channel])

                        self.fits[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)]=values[0]
                        self.covs[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)]=values[1]
                        self.TPfits[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)]=values[2]
                        self.TPcovs[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)]=values[3]
                        self.chi[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)]=values[4]
                        self.TPchi[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)]=values[5]
                        # if values[2][2]!="Fail":
                            # gauss_values=gauss_fit_baseline(matrix[TIG][channel],values[0][1],values[0][3],values[2][2])
                            # self.gaussians[GEMROC]["TIG{}".format(TIG)]["CH{}".format(channel)]=gauss_values


    def SAVE_noise(self):
        for GEMROC,dict0 in self.TPfits.items():
            filename = "noise_scan" + sep + "GEMROC{}".format(GEMROC.split()[1]) + sep + "noise.n"
            with open(filename, 'w') as f:
                for TIGER,dict1 in self.TPfits[GEMROC].items():
                    for CH,dictionary in self.TPfits[GEMROC][TIGER].items():
                        parameters=self.TPfits[GEMROC][TIGER][CH]
                        if parameters[0] != "Fail":
                            noise = convert_to_fC(parameters[1], 55)
                            cov = convert_to_fC(self.TPcovs[GEMROC][TIGER][CH][1][1], 55)

                        else:
                            noise=-1
                            cov=9999
                        f.write("{} {} {} Noise: {} Variance: {}\n".format(GEMROC,TIGER,CH,noise,cov))
    def switch_to_tp_distr(self):
        self.strart_button["text"]="Acquire test pulses"


def error_fit(data):
    # for i, ytest in enumerate(ydata):
    #     if ytest == np.max(ydata):
    #         m = i
    #         break
    M=int(np.argmax(data))
    ydata=np.copy(data)
    for i in range (M,64):
        ydata[i]=np.max(data)

    xdata = np.arange(0, 64)
    #  popt, pcov = curve_fit(errorfunc, xdata, ydata[:m], method='lm', maxfev=5000)
    #  double_error_func(x, x0, x1, sig0, sig1, c0, c1)115fvb





    #  fit with double error function summed
    # guess=np.array([2,50,5,5,TP_rate,300000])
    # boundsd = ((0,0,0,0,TP_rate*0.7,200000),(64,64,20,20,TP_rate*1.3,500000))
    # popt1, pcov1 = curve_fit(double_error_func, xdata, ydata, method='trf', maxfev=20000,p0=guess,bounds=boundsd)



    #fit with double error function + single fit on TP

    guess=np.array([2,50,5,5,TP_rate,300000])
    boundsd = ((0,0,0,0,TP_rate*0.6,200000),(64,64,20,20,TP_rate*1.5,500000))
    try:
        popt1, pcov1 = curve_fit(double_error_func, xdata, ydata, method='trf', maxfev=20000,p0=guess,bounds=boundsd)

        y=np.zeros(64)
        for i in range (0,len(ydata)):
            y[i]=double_error_func(i,*popt1)

        chi1=squared_sum(ydata,y)/64
        end=int(round(popt1[1]-5*popt1[3]))
        if end>5:
            xdata=xdata[:end]
            ydata=ydata[:end]
            guess=np.array([popt1[0],popt1[2],popt1[4]])
            boundsd=((0,0,TP_rate*0.2),(64,20,TP_rate*2))
            try:
                popt2, pcov2 = curve_fit(errorfunc, xdata, ydata, method='trf', maxfev=20000,p0=guess,bounds=boundsd)
                for i in range(0, len(ydata)):
                    y[i] = errorfunc(i, *popt2)
                chi2 = squared_sum(ydata, y[:end]) / end
            except:
                popt2 = ("Fail", "Fail", "Fail")
                pcov2 = np.zeros((3, 3))
                chi2 = 0



        else:
            popt2=("Fail","Fail","Fail")
            pcov2=np.zeros((3,3))
            chi2=0
    except:
        popt1 = (2, 50, 600)
        pcov1 = np.zeros((6, 6))
        popt2 = ("Fail", "Fail", "Fail")
        pcov2 = np.zeros((3, 3))
        chi1 = 0
        chi2 = 0
    return (popt1,pcov1,popt2,pcov2,chi1,chi2)
def gauss_fit_baseline(data,mu_s1, sigma_s1,norm_tp):
    print mu_s1, sigma_s1,norm_tp
    M=int(np.argmax(data))
    first=int(round(mu_s1-3*sigma_s1))
    second=int(round(M+4*sigma_s1))
    if first>=0 and second <64:
        print first
        print second
        ydata = np.copy(data)[first:second]
        xdata = np.arange(first, second)

        result=curve_fit(gaussian,xdata,ydata,method='trf', maxfev=20000)
        return result
def convert_to_fC(sigma,VcaspVth):
    guadagno=12.25
    fC=(VcaspVth*-0.621+39.224)/guadagno*sigma
    return fC
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