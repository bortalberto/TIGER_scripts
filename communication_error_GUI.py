from Tkinter import *
import numpy as np
from lib import GEM_COM_classes as COM_class
import binascii
from multiprocessing import Process,Pipe
import time
from lib import GEM_ANALYSIS_classes as AN_CLASS, GEM_CONF_classes as GEM_CONF
import sys
import array



OS = sys.platform
if OS == 'win32':
	sep = '\\'
elif OS == 'linux2':
	sep = '/'
else:
	print("ERROR: OS {} non compatible".format(OS))
	sys.exit()
class menu():
    def __init__(self,main_window,gemroc_handler):
        self.GEMROC_reading_dict=gemroc_handler
        self.error_window = Toplevel(main_window)
        Label(self.error_window,text='Communication Errors',font=("Courier", 25)).pack()
        self.grid_frame=Frame(self.error_window)
        self.grid_frame.pack()
        tot=len(self.GEMROC_reading_dict)
        self.TIGER_error_counters= {}
        self.GEMROC_error_counters={}
        self.TIGER_error_counters_display= {}
        self.GEMROC_error_counters_display={}
        self.GEMROC_OPENER=[]
        self.TD_scan_result={}
        number_list=[]
        i=0
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
            self.GEMROC_OPENER[i].grid(row=riga, column=colonna-1, sticky=NW,   pady=15)
            self.GEMROC_error_counters_display[number]=Label(self.grid_frame, text='----', padx=30)
            self.GEMROC_error_counters_display[number].grid(row=riga, column=colonna)
            i+=1
        self.second_row_frame=Frame(self.error_window)
        self.second_row_frame.pack()
        Button(self.second_row_frame, text ='Acquire errors on all GEMROCs', command=lambda: self.error_acquisition (0, 0, True, True)).pack(side=LEFT)
        Button(self.second_row_frame, text ='Launch TD scan on all GEMROCs', command=lambda: self.TD_scan (0, True)).pack(side=LEFT)
        Button(self.second_row_frame, text ='Load TD from TD delay file', command=lambda: self.load_TD_from_file()).pack(side=LEFT)
        self.third_row_frame=Frame(self.error_window)
        self.third_row_frame.pack()
        Button(self.third_row_frame, text ='Acquire errors since last reset', command=lambda: self.error_acquisition (0, 0, True, True,False)).pack(side=LEFT)


    def toggle(self, GEMROC_number):
        sync_winz=Toplevel(self.error_window)
        Label(sync_winz, text='GEMROC {} error counters'.format(GEMROC_number), font=("Courier", 18)).pack()
        frame_counters=Frame(sync_winz)
        frame_counters.pack()
        for T in range (0,8):
            if T<4:
                Label(frame_counters,text="TIGER {}".format(T)).grid(row=0,column=T*2,sticky=NW,pady=10)
                self.TIGER_error_counters_display["GEMROC {} TIGER {}".format(GEMROC_number, T)] = Label(frame_counters, text="-----".format(T), background='white')
                self.TIGER_error_counters_display["GEMROC {} TIGER {}".format(GEMROC_number, T)].grid(row=0, column=T * 2 + 1, sticky=NW, pady=10)
            else:
                Label(frame_counters,text="TIGER {}".format(T)).grid(row=1,column=(T-4)*2,sticky=NW,pady=10)
                self.TIGER_error_counters_display["GEMROC {} TIGER {}".format(GEMROC_number, T)] = Label(frame_counters, text="-----".format(T), background='white')
                self.TIGER_error_counters_display["GEMROC {} TIGER {}".format(GEMROC_number, T)].grid(row=1, column=(T - 4) * 2 + 1, sticky=NW, pady=10)
                #self.TIGER_error_counters_display["GEMROC {} TIGER {}".format(GEMROC_number, T)]['text']=self.TIGER_error_counters["GEMROC {} TIGER {}".format(GEMROC_number,T)]
        Button(sync_winz, text ='Launch TD scan on this GEMROC', command=lambda: self.TD_scan (GEMROC_number, False)).pack()
        Label(sync_winz,text='Manual TD setting').pack()
        manual_td=Frame(sync_winz)
        manual_td.pack()
        timing_array=[]

        for FEB in range(0,4):
            Label(manual_td,text="FEB {}".format(FEB)).pack(side=LEFT)
            timing_array.append(Entry(manual_td,width=3))
            timing_array[FEB].pack(side=LEFT)
        Button(manual_td,text="Set values",command=lambda : self.set_TD(GEMROC_number,timing_array)).pack()
    def set_TD(self,num,timing_array):
        GEMROC=self.GEMROC_reading_dict["GEMROC {}".format(num)]
        GEMROC.GEM_COM.set_FEB_timing_delays( int(timing_array[3].get()), int(timing_array[2].get()), int(timing_array[1].get()), int(timing_array[0].get()))
    def load_TD_from_file(self):
        for number, GEMROC in self.GEMROC_reading_dict.items():
            GEMROC.GEM_COM.reload_default_td()
    def TD_scan(self, GEMROC_num, to_all=False):
        if to_all:
            process_list = []
            pipe_list = []
            test_r_array=[]
            for number, GEMROC_num in self.GEMROC_reading_dict.items():

                    pipe_in,pipe_out=Pipe()
                    p=Process(target=self.TD_scan_process,args=(number,pipe_in))

                    process_list.append(p)
                    pipe_list.append(pipe_out)
                    p.start()

            for process,pipe_out in zip(process_list,pipe_list):
                process.join()
                value,key=pipe_out.recv()
                process.terminate()
                self.TD_scan_result["GEMROC {}".format(key)] = value
            GEMROC_num=-1

        else:
            GEMROC = self.GEMROC_reading_dict["GEMROC {}".format(GEMROC_num)]
            GEM_COM = GEMROC.GEM_COM
            c_inst = GEMROC.c_inst
            g_inst = GEMROC.g_inst
            test_r = (AN_CLASS.analisys_conf(GEM_COM, c_inst, g_inst))
            safe_delays = test_r.TIGER_delay_tuning()
            self.TD_scan_result["GEMROC {}".format(GEMROC_num)] = safe_delays
        self.save_values(GEMROC_num)
    def save_values(self,GEMROC_num):
        save_winz=Toplevel(self.error_window)
        ws = save_winz.winfo_screenwidth()
        hs = save_winz.winfo_screenheight()
        w,h=400,100
        # calculate position x, y
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        save_winz.geometry('%dx%d+%d+%d' % (w, h, x, y))

        Label(save_winz, text='Save the values?', font=("Courier", 18)).pack()
        cornice=Frame(save_winz)
        cornice.pack()
        Button(cornice, text ='Yes', command= lambda: self.save_TD(save_winz,GEMROC_num)).pack(side=LEFT)
        Button(cornice, text ='No', command= lambda: save_winz.destroy()).pack(side=LEFT)

    def save_TD(self,winz,GEMROC_num=-1):
        if GEMROC_num!=-1:
            safe_dealy = self.TD_scan_result["GEMROC {}".format(GEMROC_num)]
            GEMROC=self.GEMROC_reading_dict["GEMROC {}".format(GEMROC_num)]
            GEMROC.GEM_COM.save_TD_delay(safe_dealy)

        else:
            for number, GEMROC in self.GEMROC_reading_dict.items():
                safe_dealy=self.TD_scan_result[number]
                GEMROC.GEM_COM.save_TD_delay(safe_dealy)
                winz.destroy()

    def TD_scan_process(self,number,pipe_in):
        GEMROC=self.GEMROC_reading_dict[number]
        GEM_COM = GEMROC.GEM_COM
        c_inst = GEMROC.c_inst
        g_inst = GEMROC.g_inst
        test_r = (AN_CLASS.analisys_conf(GEM_COM, c_inst, g_inst))
        safe_delays = test_r.TIGER_delay_tuning()
        pipe_in.send((safe_delays,test_r.GEMROC_ID))
        pipe_in.close()
        test_r.__del__()



    def error_acquisition(self, GEMROC, TIGER, to_all_GEMROC, to_all_TIGERS,reset=True):
        process_list=[]
        pipe_list=[]
        if to_all_TIGERS:
            TIGER_LIST = [0, 1, 2, 3, 4, 5, 6, 7]
        else:
            TIGER_LIST = [TIGER]
        if to_all_GEMROC:
            for T in TIGER_LIST:
                for number, GEMROC in self.GEMROC_reading_dict.items():
                        GEMROC.GEM_COM.set_counter(int(T), 1, 0)
                        pipe_in,pipe_out=Pipe()
                        p=Process(target=self.acquire_errors,args=(number,T,pipe_in,reset))
                        process_list.append(p)
                        pipe_list.append(pipe_out)
                        p.start()
                for process,pipe_out in zip(process_list,pipe_list):
                    process.join()
                    key,value=pipe_out.recv()
                    process.terminate()
                    self.TIGER_error_counters[key] = value
                del process_list[:]
                del pipe_list[:]

        self.refresh_counters()

    def acquire_errors(self,GEMROC_num,TIGER,pipe_in,reset):
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
            self.GEMROC_error_counters[number]=0
        for key,value in self.TIGER_error_counters.items():
            number_int=int(key.split()[1])
            GEMROC="GEMROC "+str(number_int)
            self.GEMROC_error_counters[GEMROC]+=int(value)

        for key,label in self.GEMROC_error_counters_display.items():
            label['text']=self.GEMROC_error_counters[key]
        for key,label in self.TIGER_error_counters_display.items():
            #print self.TIGER_error_counters
            label['text']=int(self.TIGER_error_counters[key])
