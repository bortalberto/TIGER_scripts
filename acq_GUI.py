from Tkinter import *
import numpy as np
from lib import GEM_ACQ_classes as GEM_ACQ
import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import time
import os

OS = sys.platform
if OS == 'win32':
	sep = '\\'
elif OS == 'linux2':
	sep = '/'
else:
	print("ERROR: OS {} non compatible".format(OS))
	sys.exit()


class menu():
    def __init__(self):
        self.GEM_to_read=np.zeros((20))
        self.GEM_to_read_last=np.zeros((20))
        self.errors_counters_810=np.zeros((20))
        # for i in range (0,20):
        #     self.errors_counters_810[i]=i*20
        self.logfile="."+sep+"log_folder"+sep+"ACQ_log_{}".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        self.mode='TL'
        self.LED=[]
        self.FIELD_TIGER=[]
        self.LED_UDP=[]
        self.plotting_gemroc=0
        self.plotting_TIGER=0

        self.time=2
        self.GEM=[]
        self.thread=[]
        self.master_window = Tk()
        self.master_window.title("GEMROC acquisition")

        Label(self.master_window,text='Acquisition setting',font=("Courier", 25)).pack()

        self.master = Frame(self.master_window)
        self.master.pack()
        self.icon_on = PhotoImage(file="."+sep+'icons'+sep+'on.gif')
        self.icon_off = PhotoImage(file="."+sep+'icons'+sep+'off.gif')
        self.icon_bad = PhotoImage(file="."+sep+'icons'+sep+'bad.gif')
        self.grid_frame=Frame(self.master_window)
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


        self.start_frame=Frame(self.master_window)
        self.start_frame.pack()
        Label(self.start_frame, text="Trigger less acq time (seconds)").grid(row=0, column=0, sticky=NW, pady=4)
        self.time_in = Entry(self.start_frame,width = 3)
        self.time_in.insert(END, '1')
        self.time_in.grid(row=0, column=1, sticky=NW, pady=4)
        self.but6 = Button(self.start_frame, text='Start acquisition', command=self.start_acq)
        self.but6.grid(row=1, column=2, sticky=NW, pady=4)
        self.but7 = Button(self.start_frame, text='Trigger less acquisition', command=self.switch_mode,background='#ccffff',activebackground='#ccffff',height = 1, width = 18)
        self.but7.grid(row=1, column=3, sticky=NW, pady=4)
        self.but8 = Button(self.start_frame, text='Stop acquisition', command=self.stop_acq,state='normal'   )
        #Button(self.master,text='Exit', command='close').place(relx=0.9, rely=0.9, anchor=NW)

        self.but8.grid(row=1, column=4, sticky=NW, pady=4)
        for i in range (0,len(self.GEM_to_read)):
            if i<10:
                riga=0
            else:
                riga=1

            colonna=((i)%10)*2+1
            self.LED.append( Label(self.grid_frame, image=self.icon_off))
            self.LED[i].grid(row=riga, column=colonna)

        self.errors = Frame(self.master_window)
        self.errors.pack()
        self.LBerror=Label(self.errors,text='Acquisition errors check',font=("Courier", 25))
        self.LBerror.grid(row=0, column=0,columnspan=8,sticky=S, pady=5)
        self.butleftG_err=Button(self.errors, text='<', command=lambda:self.change_G_or_T(-1,"G")).grid(row=1, column=0, sticky=S, pady=4)
        self.LBGEM_err=Label(self.errors,text='GEMROC {}'.format(self.plotting_gemroc),font=("Courier", 14 ))
        self.LBGEM_err.grid(row=1, column=1, sticky=S, pady=4)
        self.butrightG_err=Button(self.errors, text='>', command=lambda:self.change_G_or_T(1,"G")).grid(row=1, column=2, sticky=S, pady=4)

        self.LBUDP0=Label(self.errors,text='UDP packet error  ')
        self.LBUDP0.grid(row=2, column=1,sticky=S, pady=4)
        Label(self.errors,text='  TIGER missing').grid(row=2, column=2,sticky=S, pady=4)

        self.LB810=Label(self.errors,text='8/10 bit errors  ')
        self.LB810.grid(row=2, column=3,sticky=S, pady=4)
        self.FIELD_810=Label(self.errors, text='-',background='white')
        self.FIELD_810.grid(row=4, column=3)



        self.LED_UDP=Label(self.errors, image=self.icon_off)
        self.LED_UDP.grid(row=4, column=1)
        self.FIELD_TIGER=Label(self.errors, text='-',background='white')
        self.FIELD_TIGER.grid(row=4, column=2)


        self.plot_window = Frame(self.master_window)
        self.plot_window.pack()
        #self.plot_window.geometry('900x800')
        self.corn0=Frame(self.plot_window)
        self.corn0.pack()
        self.LBOCC=Label(self.corn0,text='Channel occupancy',font=("Times", 18 ))
        self.LBOCC.grid(row=0, column=1, sticky=S, pady=4)
        self.butleftG=Button(self.corn0, text='<', command=lambda:self.change_G_or_T(-1,"G")).grid(row=1, column=0, sticky=S, pady=4)
        self.LBGEM=Label(self.corn0,text='GEMROC {}'.format(self.plotting_gemroc),font=("Courier", 14 ))
        self.LBGEM.grid(row=1, column=1, sticky=S, pady=4)
        self.butrightG=Button(self.corn0, text='>', command=lambda:self.change_G_or_T(1,"G")).grid(row=1, column=2, sticky=S, pady=4)
        self.butleftT=Button(self.corn0, text='<', command=lambda:self.change_G_or_T(-1,"T")).grid(row=2, column=0, sticky=S, pady=4)
        self.LBTIG=Label(self.corn0,text='TIGER {}'.format(self.plotting_TIGER),font=("Courier", 14 ))
        self.LBTIG.grid(row=2, column=1, sticky=S, pady=4)
        self.butrightT=Button(self.corn0, text='>', command=lambda:self.change_G_or_T(1,"T")).grid(row=2, column=2, sticky=S, pady=4)
        self.corn1=Frame(self.plot_window)
        self.corn1.pack()

        #Plot
        x = np.arange(0,64)
        v = np.zeros((64))

        self.fig = Figure(figsize=(7, 7))
        self.plot_rate = self.fig.add_subplot(111)
        self.scatter,=self.plot_rate.plot(x, v, 'r+')
        self.plot_rate.set_title("TIGER {}, GEMROC {}".format(self.plotting_TIGER,self.plotting_gemroc))
        self.plot_rate.set_ylabel("HitRates", fontsize=14)
        self.plot_rate.set_xlabel("Channel", fontsize=14)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_window)
        self.canvas.get_tk_widget().pack(side=BOTTOM)
        self.canvas.draw()
        self.canvas.flush_events()
        self.toolbar = NavigationToolbar2Tk( self.canvas, self.corn1 )
        self.toolbar.draw()

    def plotta(self):
        if self.GEM_to_read_last[self.plotting_gemroc]==1:
            for i in range (0,len(self.GEM)):
                if int(self.GEM[i].GEMROC_ID)==self.plotting_gemroc:
                    self.plot_rate.set_title("TIGER {}, GEMROC {}".format(self.plotting_TIGER, self.plotting_gemroc))
                    self.scatter.set_ydata( self.GEM[i].thr_scan_rate[self.plotting_TIGER])
                    self.plot_rate.set_ylim(top=np.max(self.GEM[i].thr_scan_rate[self.plotting_TIGER])+np.max(self.GEM[i].thr_scan_rate[self.plotting_TIGER]/20))

        else:
            self.plot_rate.set_title("GEMROC not acquired".format(self.plotting_TIGER, self.plotting_gemroc))
            self.scatter.set_ydata(np.zeros((64)))
        self.canvas.draw()
        self.canvas.flush_events()

    def convert0(self):
        for i in range (0,len(self.GEM_to_read)):
            if self.GEM_to_read[i]==1:
                self.LED[i]["image"]=self.icon_on
            else:
                self.LED[i]["image"]=self.icon_off

    def toggle(self,i):
        if self.GEM_to_read[i]==0:
            self.GEM_to_read[i]=1
        else:
            self.GEM_to_read[i]=0
        print self.GEM_to_read
        self.convert0()

    def change_G_or_T(self,i,G_or_T):
        if G_or_T=="G":
            self.plotting_gemroc=self.plotting_gemroc+i
            if self.plotting_gemroc ==-1:
                self.plotting_gemroc =0
            if self.plotting_gemroc == 20:
                self.plotting_gemroc = 19

        if G_or_T=="T":
            self.plotting_TIGER=self.plotting_TIGER+i
            if self.plotting_TIGER ==-1:
                self.plotting_TIGER =0
            if self.plotting_TIGER == 8:
                self.plotting_TIGER = 7

        self.refresh_plot()
    def refresh_plot(self):
        self.LBGEM['text']='GEMROC {}'.format(self.plotting_gemroc)
        self.LBTIG['text']='TIGER {}'.format(self.plotting_TIGER)
        self.plotta()
        self.refresh_error_status()


    def switch_mode(self):
        if self.mode=='TL':
            self.mode='TM'
            self.but7['text']="Trigger match acquisition"
            self.but7['background']='#ccff99'
            self.but7['activebackground']='#ccff99'


        else:
            self.mode='TL'
            self.but7['text']="Trigger less acquisition"
            self.but7['background']='#ccffff'
            self.but7['activebackground']='#ccffff'


    def runna(self):
        mainloop()
    def start_acq(self):
        self.but7.config(state='disabled')
        self.but6.config(state='disabled')
        for i in range (0,len(self.GEM)):
            if self.thread[i].isAlive():
                self.thread[i].join()
                self.GEM[i].__del__()

        self.GEM=[]
        self.thread=[]
        self.TM_errors=[]
        self.TL_errors=[]
        self.errors_counters_810=np.zeros((20))
        self.time=self.time_in.get()

        for i in range (0,len(self.GEM_to_read)):
            if self.GEM_to_read[i]==1:
                self.GEM.append( GEM_ACQ.reader(i))
                with open(self.logfile, 'a') as f:
                    f.write("Acquiring from GEMROC {} in {} mode".format(i,self.mode))

        for i in range(0, len(self.GEM)):
            if self.mode=='TL':
                self.thread.append(GEM_ACQ.Thread_handler("GEM ".format(i),float(self.time) , self.GEM[i]))

            else:
                self.thread.append(GEM_ACQ.Thread_handler_TM("GEM ".format(i), self.GEM[i]))

        self.GEM_to_read_last=self.GEM_to_read
        for i in range(0, len(self.GEM)):
            self.thread[i].start()
            print

    def refresh_error_status(self):
        self.LBGEM_err['text']='GEMROC {}'.format(self.plotting_gemroc)
        if self.GEM_to_read_last[self.plotting_gemroc]==1:

            for i in range(0,len(self.GEM)):
                if int (self.GEM[i].GEMROC_ID)==self.plotting_gemroc:
                    if self.mode=='TM':

                        if len(self.TM_errors[i][1])>0:
                            self.LED_UDP['image']=self.icon_bad
                        else:
                            self.LED_UDP['image']=self.icon_on
                        for i in range (0,len(self.GEM)):
                            for j in range (0,8):
                                self.FIELD_TIGER['text']='{}'.format(self.TM_errors[i][0])
                        self.LBUDP0['text'] = "UDP packet error  "

                        self.LBerror['text'] = "Acquisition errors check(TM) "

                    if self.mode=='TL':

                        if len(self.TL_errors[i][1])>0:
                            self.LED_UDP['image']=self.icon_bad
                        else:
                            self.LED_UDP['image']=self.icon_on
                        for i in range (0,len(self.GEM)):
                            for j in range (0,8):
                                self.FIELD_TIGER['text']='{}'.format(self.TL_errors[i][0])
                        self.LBUDP0['text']="Frameword missing   "

                        self.LBerror['text'] = "Acquisition errors check(TL) "
        else:
            self.LBerror['text'] = "GEMROC not acquired "
            self.LED_UDP['image'] = self.icon_off
            self.FIELD_TIGER['text']= '-'
        self.FIELD_810['text']='{}'.format(int(self.errors_counters_810[self.plotting_gemroc]))
    def stop_acq(self):
        print "Stopping"
        self.but6.config(state='normal')

        for i in range (0,len(self.GEM)):
            self.thread[i].running=False

        for i in range (0,len(self.GEM)):
            if self.thread[i].isAlive():
                self.thread[i].join()

        for i in range(0, len(self.GEM)):
            if self.mode=='TL':
                self.TL_errors.append(self.GEM[i].check_TL_Frame_TIGERS("./data_folder/Spill_2018_12_11_11_02_03_GEMROC_3.dat"))
                # self.TL_errors.append(self.GEM[i].check_TL_Frame_TIGERS(self.GEM[i].datapath))
                print self.TL_errors
            else:
                self.TM_errors.append(self.GEM[i].check_TM_continuity("./data_folder/Spill_2018_12_12_17_39_51_GEMROC_0.dat"))
                #self.TM_errors.append(self.GEM[i].check_TM_continuity(self.GEM[i].datapath))

                print self.TM_errors
        self.refresh_error_status()
        self.refresh_plot()
        self.but7.config(state='normal')


    def close(self):
        self.master.destroy()
        self.errors.destroy()
        self.plot_window.destroy()
        self.destroy()

Main_menu=menu()
Main_menu.runna()


import pickle
