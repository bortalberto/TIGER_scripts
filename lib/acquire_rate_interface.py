from threading import Thread

from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Progressbar
from tkinter.ttk import Notebook
from lib import GEM_ACQ_classes as GEM_ACQ
import numpy as np
from multiprocessing import Process, Pipe
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib
import matplotlib.pyplot as plt
from lib import GEM_ANALYSIS_classes as AN_CLASS, GEM_CONF_classes as GEM_CONF
import time
OS = sys.platform
if OS == 'win32':
    sep = '\\'
elif OS == 'linux2' or 'linux':
    sep = '/'
else:
    print("ERROR: OS {} non compatible".format(OS))
    sys.exit()
debug=True

class menu():
    def __init__(self,main_menu,gemroc_handler,main_menu_istance):

        self.error_window_main = Toplevel(main_menu)
        self.error_window_main.wm_title("ACQ_rate")
        self.rate_tab=noise_rate_measure(self.error_window_main ,gemroc_handler,main_menu_istance)
        self.rate_tab._init_windows()

class noise_rate_measure ():
    def __init__(self,main_window,gemroc_handler,main_menu_istance):
        self.main_menu = main_menu_istance
        self.title="Noise rate measure"
        self.main_window=main_window
        self.GEMROC_reading_dict=gemroc_handler
        self.showing_GEMROC = StringVar(self.main_window)
        self.showing_TIGER = StringVar(self.main_window)
        self.start_frame=Frame(self.main_window)
        self.start_frame.pack()
        self.entry_text = StringVar(self.main_window)

        # self.queue = Queue.Queue()
        # self.getterino=Get_rate(self,self.queue)


    def _init_windows(self):
        Label(self.start_frame, text=self.title, font=("Courier", 25)).pack()
        first_lane_frame=Frame(self.start_frame)
        first_lane_frame.pack()
        OptionMenu(first_lane_frame, self.showing_GEMROC, *sorted(self.GEMROC_reading_dict.keys(),key = find_number)).grid(row=0, column=2, sticky=W, pady=2)
        Label(first_lane_frame, text='     TIGER').grid(row=0, column=3, sticky=W, pady=4)

        OptionMenu(first_lane_frame, self.showing_TIGER,*range(8) ).grid(row=0, column=4, sticky=W, pady=2)
        Label(first_lane_frame, text='     Channel').grid(row=0, column=5, sticky=W, pady=4)
        self.Channel_IN = Entry(first_lane_frame, width=4, textvariable=self.entry_text)
        self.entry_text.trace("w", lambda *args: character_limit(self.entry_text))
        self.Channel_IN.grid(row=0, column=6, sticky=W, pady=4)
        self.Channel_IN.get()
        Label(first_lane_frame, text='Time(s)').grid(row=1, column=1, sticky=W, pady=4)
        self.time = Entry(first_lane_frame, width=4)
        self.time.grid(row=1, column=2, sticky=W, pady=4)
        self.acq_button=Button(first_lane_frame,text="Start",command=self.start_acq)
        self.acq_button.grid(row=1, column=3, sticky=W, pady=4)
        Label(first_lane_frame,text="   Rate").grid(row=2, column=2, sticky=W, pady=4)
        self.entry_lbl=Label(first_lane_frame,text="-",width=10)
        self.entry_lbl.grid(row=2, column=3, sticky=W, pady=4)

    def start_acq(self):
        self.acq_button.config(state='disabled')
        GEMROC = self.GEMROC_reading_dict[self.showing_GEMROC.get()]
        TIGER = self.showing_TIGER.get()
        Channel = self.Channel_IN.get()
        GEMROC.GEM_COM.set_counter(int(TIGER), 0, int(Channel))
        GEMROC.GEM_COM.SynchReset_to_TgtFEB(0, 1)
        GEMROC.GEM_COM.reset_counter()
        time.sleep(float(self.time.get()))
        self.rate = GEMROC.GEM_COM.GEMROC_counter_get()/float(self.time.get())
        self.entry_lbl["text"] = "{:.2f}".format(self.rate)
        self.acq_button.config(state='normal')
        print (self.rate)

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


def character_limit(entry_text):
    try:
        if int(entry_text.get()) < 0:
            entry_text.set(0)
        if int(entry_text.get()) > 63:
            entry_text.set(63)
    except:
        entry_text.set("")
        "Not valid input in channel field"

