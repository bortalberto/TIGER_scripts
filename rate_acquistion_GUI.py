from tkinter import *
from multiprocessing import Process,Pipe
import time
from lib import GEM_ANALYSIS_classes as AN_CLASS, GEM_CONF_classes as GEM_CONF
import sys



OS = sys.platform
if OS == 'win32':
	sep = '\\'
elif OS == 'linux2' or 'linux':
	sep = '/'
else:
	print("ERROR: OS {} non compatible".format(OS))
	sys.exit()

class menu():
    def __init__(self,main_window,gemroc_handler):
        self.GEMROC_reading_dict=gemroc_handler

        self.rate_window = Toplevel(main_window)
        Label(self.rate_window, text='Communication Errors', font=("Courier", 25)).pack()
        self.rate_window.wm_title('Communication Errors')
        self.grid_frame=Frame(self.rate_window)
        self.grid_frame.pack()
        tot=len(self.GEMROC_reading_dict)
        self.TIGER_rate_counters= {}
        self.GEMROC_rate_counters={}
        self.TIGER_rate_counters_display= {}
        self.GEMROC_rate_counters_display={}
        self.GEMROC_OPENER=[]
        self.TD_scan_result={}
        number_list=[]
        i=0
        if OS == 'linux':
            self.rate_window.wm_iconbitmap('@' + "." + sep + 'icons' + sep + '810_ICON.xbm')
        for number, GEMROC in self.GEMROC_reading_dict.items():
            number_int=int(number.split()[1])
            number_list.append(number_int)
            number_list.sort()
        for number, GEMROC in self.GEMROC_reading_dict.items():
            number_int=int(number.split()[1])
            position=number_list.index(number_int)
            if position<tot/2:
                riga=0
            else:
                riga=1
            if tot>1:
                colonna=((position)%(tot/2))*2+1
            else:
                colonna=1
            if tot%2!=0:
                if position==tot-1:
                    riga=3

            self.GEMROC_OPENER.append(Button(self.grid_frame, text=number, command=lambda number_int=number_int: self.toggle(number_int)))
            self.GEMROC_OPENER[i].grid(row=riga, column=int(colonna-1), sticky=NW,   pady=15)
            self.GEMROC_rate_counters_display[number]=Label(self.grid_frame, text='----', padx=30)
            self.GEMROC_rate_counters_display[number].grid(row=riga, column=int(colonna))
            i+=1
        self.second_row_frame=Frame(self.rate_window)
        self.second_row_frame.pack()

        Label(self.second_row_frame, text = 'Time for each acq  ').pack(side=LEFT)
        self.acq_time = Entry(self.second_row_frame, width = 4)
        self.acq_time.pack(side=LEFT)
        self.acq_time.insert(0,0.1 )
        self.third_row_frame=Frame(self.rate_window)
        self.third_row_frame.pack()
        Button(self.third_row_frame, text ='Start acq', command=self.rate_acqisition_start ).pack(side=LEFT)
        Button(self.third_row_frame, text ='Stop acq', command = self.rate_acqisition_stop).pack(side=LEFT)


    def toggle(self, GEMROC_number):
        sync_winz=Toplevel(self.rate_window)
        sync_winz.wm_title(GEMROC_number)
        Label(sync_winz, text='GEMROC {} rate counters'.format(GEMROC_number), font=("Courier", 18)).pack()
        frame_counters=Frame(sync_winz)
        frame_counters.pack()
        for T in range (0,8):
            if T<4:
                Label(frame_counters,text="TIGER {}".format(T)).grid(row=0,column=T*2,sticky=NW,pady=10)
                self.TIGER_rate_counters_display["GEMROC {} TIGER {}".format(GEMROC_number, T)] = Label(frame_counters, text="-----".format(T), background='white')
                self.TIGER_rate_counters_display["GEMROC {} TIGER {}".format(GEMROC_number, T)].grid(row=0, column=T * 2 + 1, sticky=NW, pady=10)
            else:
                Label(frame_counters,text="TIGER {}".format(T)).grid(row=1,column=(T-4)*2,sticky=NW,pady=10)
                self.TIGER_rate_counters_display["GEMROC {} TIGER {}".format(GEMROC_number, T)] = Label(frame_counters, text="-----".format(T), background='white')
                self.TIGER_rate_counters_display["GEMROC {} TIGER {}".format(GEMROC_number, T)].grid(row=1, column=(T - 4) * 2 + 1, sticky=NW, pady=10)
                #self.TIGER_error_counters_display["GEMROC {} TIGER {}".format(GEMROC_number, T)]['text']=self.TIGER_error_counters["GEMROC {} TIGER {}".format(GEMROC_number,T)]


    def rate_acqisition_start(self):
        self.running = True
        p=Process(target=self.rate_acquisition_process)
        p.start()

    def rate_acqisition_stop(self):
        self.running = False

    def rate_acquisition_process (self):
        print (self.running)
        while self.running:
            print ("Ciao")
            time.sleep(1)

    def rate_acquisition(self, reset=True):
        process_list=[]
        pipe_list=[]
        TIGER_LIST = [0, 1, 2, 3, 4, 5, 6, 7]
        for T in TIGER_LIST:
            for number, GEMROC in self.GEMROC_reading_dict.items():
                    GEMROC.GEM_COM.set_counter(int(T), 0, 0)
                    pipe_in,pipe_out=Pipe()
                    p = Process(target=self.acquire_errors,args=(number,T,pipe_in))
                    process_list.append(p)
                    pipe_list.append(pipe_out)
                    p.start()
            for process,pipe_out in zip(process_list,pipe_list):
                process.join()
                key,value=pipe_out.recv()
                process.terminate()
                self.TIGER_rate_counters[key] = value
            del process_list[:]
            del pipe_list[:]

        self.refresh_counters()

    def acquire_rate(self,GEMROC_num,TIGER,pipe_in,reset):
        GEMROC=self.GEMROC_reading_dict[GEMROC_num]
        if reset:
            GEMROC.GEM_COM.reset_counter()
            time.sleep(1)
        counter_value=GEMROC.GEM_COM.GEMROC_counter_get()
        tiger_string="{} TIGER {}".format(GEMROC_num,TIGER)
        pipe_in.send((tiger_string,counter_value))
        pipe_in.close()


    def refresh_counters(self):
        for number,GEMROC in self.GEMROC_reading_dict.items():
            self.GEMROC_rate_counters[number]=0

        for key,value in self.TIGER_rate_counters.items():
            number_int=int(key.split()[1])
            GEMROC="GEMROC "+str(number_int)
            self.GEMROC_rate_counters[GEMROC]+=int(value)
        for key,label in self.GEMROC_rate_counters_display.items():
            label['text']=self.GEMROC_rate_counters[key]
        for key,label in self.TIGER_rate_counters_display.items():
            #print self.TIGER_error_counters
            label['text']=int(self.TIGER_rate_counters[key])
