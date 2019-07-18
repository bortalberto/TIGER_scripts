from threading import Thread
from Tkinter import *
from lib import GEM_ACQ_classes as GEM_ACQ
import numpy as np
import ttk
import time
import Queue
OS = sys.platform
if OS == 'win32':
    sep = '\\'
elif OS == 'linux2':
    sep = '/'
else:
    print("ERROR: OS {} non compatible".format(OS))
    sys.exit()


class menu():
    def __init__(self,main_menu,gemroc_handler):
        self.error_window_main = Toplevel(main_menu)
        self.error_window_main.wm_title("Noise and thresholds")
        self.tabControl = ttk.Notebook(self.error_window_main)  # Create Tab Control

        rate_tab=noise_rate_measure(self.error_window_main ,gemroc_handler,self.tabControl)
        rate_tab._insert("Noise rate measure")
        rate_tab._init_windows()
        self.tabControl.pack(expand=1, fill="both")  # Pack to make visible

class noise_rate_measure ():
    def __init__(self,main_window,gemroc_handler,tab_control):
        self.title="Noise rate measure"
        self.tabControl=tab_control
        self.main_window=main_window
        self.sampling_scan=False
        self.GEMROC_reading_dict=gemroc_handler
        self.error_window=Frame(self.main_window)
        self.queue = Queue.Queue()
        self.acquire_thread=Acquire_rate(gemroc_handler,self,self.queue)

    def _init_windows(self):
        Label(self.error_window,text=self.title,font=("Courier", 25)).grid(row=0, column=2, sticky=S, pady=4,columnspan=10)
        self.first_lane_frame=Frame(self.error_window)
        self.first_lane_frame.grid(row=1, column=2, sticky=S, pady=4,columnspan=10)
        Button(self.first_lane_frame, text="Start rate acquisition", command=self.start_acq).pack(side=LEFT)
        Button(self.first_lane_frame, text="Stop rate acquisition", command=self.stop_acq ).pack(side=LEFT)

    def _insert(self,name):
        self.tabControl.add(self.error_window, text=name)  # Add the tab
    def start_acq(self):
        """
        Start rate acquisition
        :return:
        """
        self.count_matrix = np.zeros((20,8,64))
        self.acquire_thread.number_of_cycles = 0
        self.acquire_thread.running=True
        self.acquire_thread.start()

    def stop_acq(self):
        """
        Stop rate acquisition
        :return:
        """
        self.acquire_thread.running=False
        self.acquire_thread.join()


class Acquire_rate(Thread):
    """
    Multhithread class to acquire rate while updating the plots
    """
    def __init__(self, GEMROC_handler,caller, queue):
        self.queue = queue
        self.count_matrix = np.zeros((20,8,64))
        self.number_of_cycles = 0
        self.GEMROC_reading_dic = GEMROC_handler
        self.running = True
        self.caller=caller
        for number, GEMROC in self.GEMROC_reading_dic.items():
            GEMROC.GEM_COM.gemroc_DAQ_XX.DAQ_config_dict["TL_nTM_ACQ"] = 0
        Thread.__init__(self)
    def run(self):
        while self.running:
            self.number_of_cycles += 1
            for key,GEMROC in self.GEMROC_reading_dic.items():
                number = int(key.split(" ")[1])
                print number
                GEMROC.GEM_COM.gemroc_DAQ_XX.DAQ_config_dict["TL_nTM_ACQ"] = 1
                GEMROC.GEM_COM.DAQ_set_with_dict()
                acquirer = GEM_ACQ.reader(number)
                self.count_matrix[number] = acquirer.acquire_rate(0.5)
                self.queue.put(self.count_matrix)
