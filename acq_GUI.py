
from Tkinter import *
import numpy as np
from lib import GEM_ACQ_classes as GEM_ACQ
import datetime
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


class menu(Frame):
    def __init__(self):
        Frame.__init__(self)
        self.GEM_to_read=np.zeros((9))
        self.logfile="."+sep+"log_folder"+sep+"ACQ_log_{}".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        self.mode='TL'
        self.LED=[]
        self.FIELD_TIGER=[]
        self.LED_UDP=[]


        self.time=2
        self.GEM=[]
        self.thread=[]

        self.master = Toplevel()
        self.master.geometry('600x400')
        self.icon_on = PhotoImage(file="."+sep+'icons'+sep+'on.gif')
        self.icon_off = PhotoImage(file="."+sep+'icons'+sep+'off.gif')
        self.icon_bad = PhotoImage(file="."+sep+'icons'+sep+'bad.gif')

        self.but0 = Button(self.master, text='GEMROC0', command=lambda:self.toggle(0)).grid(row=3, column=0, sticky=NW, pady=4)
        self.but1 = Button(self.master, text='GEMROC1', command=lambda:self.toggle(1)).grid(row=3, column=2, sticky=NW, pady=4)
        self.but2 = Button(self.master, text='GEMROC2', command=lambda:self.toggle(2)).grid(row=3, column=4, sticky=NW, pady=4)
        self.but3 = Button(self.master, text='GEMROC3', command=lambda:self.toggle(3)).grid(row=4, column=0, sticky=W, pady=4)
        self.but4 = Button(self.master, text='GEMROC4', command=lambda:self.toggle(4)).grid(row=4, column=2, sticky=W, pady=4)
        self.but5 = Button(self.master, text='GEMROC5', command=lambda:self.toggle(5)).grid(row=4, column=4, sticky=W, pady=4)
        self.but9 = Button(self.master, text='GEMROC6', command=lambda:self.toggle(6)).grid(row=5, column=0, sticky=NW, pady=4)
        self.but10 = Button(self.master, text='GEMROC7', command=lambda:self.toggle(7)).grid(row=5, column=2, sticky=NW, pady=4)
        self.but11 = Button(self.master, text='GEMROC8', command=lambda:self.toggle(8)).grid(row=5, column=4, sticky=NW, pady=4)

        Label(self.master, text="Trigger less acq time (seconds)").place(relx=0.1, rely=0.6, anchor=NW)
        self.time_in = Entry(self.master,width = 3)
        self.time_in.insert(END, '1')
        self.time_in.place(relx=0.5, rely=0.6, anchor=NW)
        self.but6 = Button(self.master, text='Start acquisition', command=self.start_acq)
        self.but6.place(relx=0.5, rely=0.4, anchor=NW)
        self.but7 = Button(self.master, text='Trigger less acquisition', command=self.switch_mode,background='#ccffff',activebackground='#ccffff',height = 1, width = 18)
        self.but7.place(relx=0.05, rely=0.4, anchor=NW)
        self.but8 = Button(self.master, text='Stop acquisition', command=self.stop_acq,state='normal')
        #Button(self.master,text='Exit', command='close').place(relx=0.9, rely=0.9, anchor=NW)

        self.but8.place(relx=0.75, rely=0.4, anchor=NW)
        for i in range (0,len(self.GEM_to_read)):
            if i<3:
                riga=3
            elif i<6:
                riga=4
            else:
                riga=5

            colonna=((i)%3)*2+1
            self.LED.append( Label(self.master, image=self.icon_off))
            self.LED[i].grid(row=riga, column=colonna)

        self.errors = Toplevel()
        self.errors.geometry('900x600')

        Label(self.errors,text='Acquisition errors check',font=("Courier", 25)).grid(row=0, column=0,columnspan=8,sticky=S, pady=5)

        Label(self.errors,text='UDP packet error  ').grid(row=1, column=1,sticky=S, pady=4)
        Label(self.errors,text='  TIGER missing').grid(row=1, column=2,sticky=S, pady=4)

        Label(self.errors,text='UDP packet error ').grid(row=1, column=4,sticky=S, pady=4)
        Label(self.errors,text='  TIGER missing').grid(row=1, column=5,sticky=S, pady=4)


        Label(self.errors,text='UDP packet error  ').grid(row=1, column=7,sticky=S, pady=4)
        Label(self.errors,text='  TIGER missing').grid(row=1, column=8,sticky=S, pady=4)


        Label(self.errors, text='GEMROC0').grid(row=3, column=0, sticky=S, pady=4)
        Label(self.errors, text='GEMROC1').grid(row=3, column=3, sticky=S, pady=4)
        Label(self.errors, text='GEMROC2').grid(row=3, column=6, sticky=S, pady=4)
        Label(self.errors, text='GEMROC3').grid(row=4, column=0, sticky=S, pady=4)
        Label(self.errors, text='GEMROC4').grid(row=4, column=3, sticky=S, pady=4)
        Label(self.errors, text='GEMROC5').grid(row=4, column=6, sticky=S, pady=4)
        Label(self.errors, text='GEMROC6').grid(row=5, column=0, sticky=S, pady=4)
        Label(self.errors, text='GEMROC7').grid(row=5, column=3, sticky=S, pady=4)
        Label(self.errors, text='GEMROC8').grid(row=5, column=6, sticky=S, pady=4)

        for i in range (0,len(self.GEM_to_read)):
            if i<3:
                riga=3
            elif i<6:
                riga=4
            else:
                riga=5
            colonna = ((i) % 3) * 3 + 1

            self.LED_UDP.append(Label(self.errors, image=self.icon_off))
            self.LED_UDP[i].grid(row=riga, column=colonna)

        for i in range (0,len(self.GEM_to_read)):
            if i<3:
                riga=3
            elif i<6:
                riga=4
            else:
                riga=5
            colonna = ((i) % 3) * 3 + 2

            self.FIELD_TIGER.append(Label(self.errors, text='-',background='white'))
            self.FIELD_TIGER[i].grid(row=riga, column=colonna)


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



        for i in range(0, len(self.GEM)):
            self.thread[i].start()
            print

    def refresh_error_status(self):
        for i in range (0,len(self.GEM)):
            if self.mode=='TM':

                if len(self.TM_errors[i][1])>0:
                    self.LED_UDP[int(self.GEM[i].GEMROC_ID)]['image']=self.icon_bad
                else:
                    self.LED_UDP[int(self.GEM[i].GEMROC_ID)]['image']=self.icon_on
                for i in range (0,len(self.GEM)):
                    for j in range (0,8):
                        self.FIELD_TIGER[i]['text']='{}'.format(self.TM_errors[i][0])



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
                a=1
            else:
                time.sleep(1)
                self.TM_errors.append(self.GEM[i].check_TM_continuity(self.GEM[i].datapath))
                print self.TM_errors
        self.refresh_error_status()
        self.but7.config(state='normal')


    def close(self):
        self.master.destroy()
        self.errors.destroy()
        self.destroy()

Main_menu=menu()
Main_menu.runna()


import pickle
