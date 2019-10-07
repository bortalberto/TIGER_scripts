from threading import Thread
from Tkinter import *
from lib import GEM_ACQ_classes as GEM_ACQ
import numpy as np
import ttk
import time
import Queue
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib
import matplotlib.pyplot as plt
import math
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
        rate_tab._insert("All system")
        rate_tab._init_windows()
        self.error_window_main.protocol("WM_DELETE_WINDOW", rate_tab.close_stopping)

        self.tabControl.pack(expand=1, fill="both")  # Pack to make visible

class noise_rate_measure ():
    def __init__(self,main_window,gemroc_handler,tab_control):
        self.title="Noise rate measure"
        self.tabControl=tab_control
        self.main_window=main_window
        self.sampling_scan=False
        self.GEMROC_reading_dict=gemroc_handler
        self.all_sys_window=Frame(self.main_window)

        self.start_frame=Frame(self.main_window)
        self.start_frame.pack()
        # self.queue = Queue.Queue()
        # self.getterino=Get_rate(self,self.queue)
        self.GMAX=int(max(int(key.split(" ")[1]) for key in self.GEMROC_reading_dict.keys()))
        self.count_matrix_channel = np.zeros((self.GMAX+1, 8, 64))
        self.count_matrix_TIGER = np.zeros((self.GMAX+1, 8))
        # self.rate_matrix_channel = np.zeros((GMAX+1, 8, 64))
        # self.rate_matrix_TIGER = np.zeros((GMAX+1, 8))
        self.GEMROC = StringVar(self.main_window)
        self.TIGER = StringVar(self.main_window)
        self.logscale = BooleanVar(self.main_window)
        # self.getterino.start()
    def _init_windows(self):
        Label(self.all_sys_window, text=self.title, font=("Courier", 25)).grid(row=0, column=2, sticky=S, pady=4, columnspan=10)
        self.first_lane_frame=Frame(self.start_frame)
        self.first_lane_frame.grid(row=1, column=2, sticky=S, pady=4,columnspan=10)
        self.start_button = Button(self.first_lane_frame, text="Acquire one cycle", command=self.start_acq)
        self.start_button.pack(side=LEFT)
        Button(self.first_lane_frame, text="Update plot", command=self.update_data ).pack(side=LEFT)
        Button(self.first_lane_frame, text="Clear", command=self.clear ).pack(side=LEFT)
        Label(self.first_lane_frame, text="Rate cap").pack(side=LEFT)
        self.cap=Entry(self.first_lane_frame, width=6)
        self.cap.pack(side=LEFT)
        self
        Button(self.first_lane_frame, text="Lower (T) ch above cap", command=lambda : self.thr_equalizing("a")).pack(side=LEFT)
        Button(self.first_lane_frame, text="Rise (T) ch below cap", command=lambda : self.thr_equalizing("b")).pack(side=LEFT)

        # Button(self.first_lane_frame, text="Stop rate acquisition", command=self.stop_acq ).pack(side=LEFT)
        fields_optionsG = self.GEMROC_reading_dict.keys()
        # fields_optionsG.append("All")
        OptionMenu(self.single_GEMROC, self.GEMROC, *fields_optionsG).grid(row=0, column=2, sticky=S, pady=4, columnspan=20)
        self.GEMROC.set(fields_optionsG[0])
        # fields_optionsT = range (0,8)
        # # fields_optionsT.append("All")
        # OptionMenu(self.single_TIGER, self.TIGER, *fields_optionsT).grid(row=0, column=0, sticky=S, pady=4, columnspan=20)
        # OptionMenu(self.single_TIGER, self.GEMROC, *fields_optionsG).grid(row=0, column=1, sticky=S, pady=4, columnspan=20)
        # # self.GEMROC.trace("w", lambda name, index, mode, sv=self.GEMROC: self.change_plot_G(sv))
        # self.TIGER.trace("w", lambda name, index, mode, sv=self.TIGER: self.change_plot_T(sv))
        """
        Create one plot for each tab mode
        """
        self.plot_frame_total= Frame(self.all_sys_window)
        self.plot_frame_total.grid(row=2, column=2, sticky=S, pady=4, columnspan=20)
        self.fig_total = Figure(figsize=(10, 8))
        self.axe_total = self.fig_total.add_subplot(111)
        self.heatmap_total, self.cbar_total = heatmap(self.count_matrix_TIGER, ["GEMROC {}".format(gem_num) for gem_num in range(0, 20)], ["TIGER {}".format(tig_num) for tig_num in range(0, 8)], ax=self.axe_total, cmap="winter", cbarlabel="Rate [hit/s]")
        self.canvas_total = FigureCanvasTkAgg(self.fig_total, master=self.plot_frame_total)
        self.canvas_total.get_tk_widget().pack(side=BOTTOM)
        self.canvas_total.draw()
        self.canvas_total.flush_events()
        self.toolbar_total = NavigationToolbar2Tk(self.canvas_total, self.plot_frame_total)
        self.toolbar_total.draw()




        self.plot_frame_GEMROC= Frame(self.single_GEMROC)
        Checkbutton(self.single_GEMROC, text="Log", variable=self.logscale).grid(row=0, column=1, sticky=NW, pady=4)
        self.plot_frame_GEMROC.grid(row=2, column=2, sticky=S, pady=4, columnspan=20)
        self.fig_GEMROC = Figure(figsize=(10, 8))
        self.axe_GEMROC_A = self.fig_GEMROC.add_subplot(121)
        self.heatmap_GEMROC_A,self.cbar_GEMRORA = heatmap(np.transpose(self.count_matrix_channel[0])[:32], ["Ch {}".format(tig_num) for tig_num in range(0, 32)], ["T {}".format(tig_num) for tig_num in range(0, 8)], ax=self.axe_GEMROC_A, cmap="winter", cbarlabel="Rate [hit/s]",spawn_cb=True)
        self.axe_GEMROC_B = self.fig_GEMROC.add_subplot(122)
        self.heatmap_GEMROC_B, self.cbar_GEMRORB = heatmap(np.transpose(self.count_matrix_channel[0])[32:], ["Ch {}".format(tig_num) for tig_num in range(32, 64)], ["T {}".format(tig_num) for tig_num in range(0, 8)], ax=self.axe_GEMROC_B, cmap="winter", cbarlabel="Rate [hit/s]")
        self.canvas_GEMROC = FigureCanvasTkAgg(self.fig_GEMROC, master=self.plot_frame_GEMROC)
        self.canvas_GEMROC.get_tk_widget().pack(side=BOTTOM)
        self.canvas_GEMROC.draw()
        self.canvas_GEMROC.flush_events()
        self.toolbar_GEMROC = NavigationToolbar2Tk(self.canvas_GEMROC, self.plot_frame_GEMROC)
        self.toolbar_GEMROC.draw()
        self.acquire_thread= Acquire_rate(self,self.GEMROC_reading_dict)

    def change_plot_G(self, sv):
        # print sv.get()
        # if sv.get()=="All":
        #     self.heatmap.remove()
        #     self.heatmap, = heatmap(self.count_matrix_TIGER, ["GEMROC {}".format(gem_num) for gem_num in range(0, 20)], ["TIGER {}".format(tig_num) for tig_num in range(0, 11)], ax=self.axe, cmap="YlGn", cbarlabel="Rate [hits/s]")
        # else:
        #     gem_num=int(sv.get().split(" ")[1])
        #     self.cbar.remov()
        #     self.heatmap,  = heatmap(self.count_matrix_channel[gem_num], ["TIGER {}".format(tig_num) for tig_num in range(0, 8)], ["Channel {}".format(ch_num) for ch_num in range(0, 64)], ax=self.axe, cmap="YlGn", cbarlabel="Rate [hits/s]")

        if sv.get()=="All":
        #     self.heatmap.remove()

            self.axe_total.set_xticks(np.arange(self.count_matrix_TIGER.shape[1]))
            self.axe_total.set_yticks(np.arange(self.count_matrix_TIGER.shape[0]))
            self.axe_total.set_xticklabels(["GEMROC {}".format(gem_num) for gem_num in range(0, 20)])
            self.axe_total.set_yticklabels(["TIGER {}".format(tig_num) for tig_num in range(0, 11)])

        else:
            gem_num=int(sv.get().split(" ")[1])
            print gem_num
            self.axe_total.set_xticks(np.arange(self.count_matrix_channel[gem_num].shape[0]))
            self.axe_total.set_yticks(np.arange(self.count_matrix_channel[gem_num].shape[1]))
            self.axe_total.set_xticklabels(["TIGER {}".format(tig_num) for tig_num in range(0, 11)])
            self.axe_total.set_yticklabels(["Ch {}".format(tig_num) for tig_num in range(0, 64)])


        self.canvas_total.draw()
        self.canvas_total.flush_events()

    def _insert(self,name):
        self.tabControl.add(self.all_sys_window, text=name)  # Add the tab
        self.single_GEMROC=Frame(self.main_window)
        self.single_TIGER=Frame(self.main_window)

        self.tabControl.add(self.single_GEMROC, text="Single GEMROC")  # Add the tab
        # self.tabControl.add(self.single_TIGER, text="Single TIGER")  # Add the tab

    def start_acq(self):
        """
        Start rate acquisition
        :return:
        """
        self.start_button["state"]="disabled"
        self.acquire_thread.acquire()
        self.start_button["state"]="normal"

    # def stop_acq(self):
    #     """
    #     Stop rate acquisition
    #     :return:
    #     """
    #     try:
    #         if self.acquire_thread.running== True:
    #             self.acquire_thread.running=False
    #             self.start_button["state"]="normal"
    #     except AttributeError:
    #         pass


    def clear(self):
        """
        clear the matrix
        :return:
        """
        self.count_matrix_channel = np.zeros((self.GMAX+1, 8, 64))
        self.acquire_thread.number_of_cycles = 0
    def thr_equalizing(self, mode):
        """
        Lower all the channel threhsolds with the rate above/below a certain level.
        :return:
        """
        if mode=="a":
            self.acquire_thread.lower_thr_above(self.cap.get(), "T")
        if mode=="b":
            self.acquire_thread.rise_thr_below(self.cap.get(), "T")

    def update_data(self):
        if self.tabControl.index("current") ==0:
            for key in self.GEMROC_reading_dict.keys():
                for T in range (0,8):
                    G = key.split(" ")[1]
                    self.count_matrix_TIGER[int(G)][T] = np.sum(self.count_matrix_channel[int(G)][T])
                    self.update_plot(self.count_matrix_TIGER/self.acquire_thread.number_of_cycles,"tot")
        if self.tabControl.index("current") ==1:
            self.update_plot(self.count_matrix_channel,"GEMROC")

    def update_plot(self,data,mode):
        if mode == "tot":
            # print "G0 : {}".format(data[0])
            # print "G1 : {}".format(data[1])
            self.heatmap_total.set_data(data)
            self.canvas_total.draw()
            self.canvas_total.flush_events()
            try:
                MIN_count=int(np.min(data))
                MAX_count=int(np.max(data))
            except ValueError:
                MIN_count=1
                MAX_count=1
            self.cbar_total.set_clim(vmin=MIN_count, vmax=MAX_count)
            cbar_ticks = np.linspace(MIN_count, MAX_count, num=11, endpoint=True)
            self.cbar_total.set_ticks(cbar_ticks)
            self.cbar_total.draw_all()


        if mode == "GEMROC":
            G = int(self.GEMROC.get().split(" ")[1])
            data = data / self.acquire_thread.number_of_cycles
            MIN_count = int(np.min(np.transpose(data[G])))
            MAX_count = int(np.max(np.transpose(data[G])))

            if self.logscale.get():
                data=np.ma.log10(data)
                data=data.filled(0)
                MIN_count = int(np.min(np.transpose(data[G])))
                MAX_count = int(np.max(np.transpose(data[G])))

            self.heatmap_GEMROC_A.set_data(np.transpose(data[G])[:32])
            self.heatmap_GEMROC_B.set_data(np.transpose(data[G])[32:])

            if self.logscale.get():
                # cbar_ticks = np. ma.log10(np.linspace(MIN_count, MAX_count, num=11, endpoint=True))
                # cbar_ticks = cbar_ticks.filled(0)
                cbar_ticks = np.linspace(MIN_count, MAX_count, num=11, endpoint=True)
                self.cbar_GEMRORB.ax.set_ylabel("Log(Rate [hit/s])", rotation=-90, va="bottom")
                self.cbar_GEMRORA.ax.set_ylabel("Log(Rate [hit/s])", rotation=-90, va="bottom")

            else:
                cbar_ticks = np.linspace(MIN_count, MAX_count, num=11, endpoint=True)

            self.cbar_GEMRORB.ax.set_ylabel("Rate [hit/s]", rotation=-90, va="bottom")
            self.cbar_GEMRORA.ax.set_ylabel("Rate [hit/s]", rotation=-90, va="bottom")
            self.cbar_GEMRORB.set_clim(vmin=MIN_count, vmax=MAX_count)
            self.cbar_GEMRORA.set_clim(vmin=MIN_count, vmax=MAX_count)

            self.cbar_GEMRORB.set_ticks(cbar_ticks)
            self.cbar_GEMRORB.draw_all()
            self.cbar_GEMRORA.set_ticks(cbar_ticks)
            self.cbar_GEMRORA.draw_all()
            self.canvas_GEMROC.draw()
            self.canvas_GEMROC.flush_events()

    def close_stopping(self):
        """
        Handle the closing protocol stopping the acquisition
        :return:
        """
        # self.stop_acq()
        self.main_window.destroy()


class Acquire_rate():
    """
    Multhithread class to acquire rate while updating the plots
    """
    def __init__(self, caller, GEMROC_handler):
        self.caller=caller
        self.count_matrix = np.zeros((self.caller.GMAX+1, 8, 64))
        self.number_of_cycles = 0
        self.GEMROC_reading_dic = GEMROC_handler
        self.running = True
        for number, GEMROC in self.GEMROC_reading_dic.items():
            GEMROC.GEM_COM.gemroc_DAQ_XX.DAQ_config_dict["TL_nTM_ACQ"] = 0

    def acquire(self):
        # while self.running:
        self.number_of_cycles += 1
        for key,GEMROC in self.GEMROC_reading_dic.items():
            number = int(key.split(" ")[1])
            GEMROC.GEM_COM.gemroc_DAQ_XX.DAQ_config_dict["TL_nTM_ACQ"] = 1
            GEMROC.GEM_COM.DAQ_set_with_dict()
            acquirer = GEM_ACQ.reader(number)
            self.count_matrix[number] = acquirer.acquire_rate(1)
            # print "GEMROC {}: {}".format(number, self.count_matrix[number])
            # self.queue.put(self.count_matrix)
            print "Number of cycles{}".format(self.number_of_cycles)
            GEMROC.GEM_COM.gemroc_DAQ_XX.DAQ_config_dict["TL_nTM_ACQ"] = 0
            GEMROC.GEM_COM.DAQ_set_with_dict()

        self.caller.count_matrix_channel += self.count_matrix
        self.caller.update_data()

    def lower_thr_above(self, limit, branch):
        """
        Lower the thr above the given limit. No controll for -1 is given (su
        :param limit:
        :param branch:
        :return:
        """
        for key,GEMROC in self.GEMROC_reading_dic.items():
            number = int(key.split(" ")[1])
            for T in range (0,8):
                for ch in range(0,64):
                    if self.count_matrix[number][T][ch] > int(limit):
                        if branch == "T":
                            GEMROC.c_inst.Channel_cfg_list[T][ch]['Vth_T1'] = GEMROC.c_inst.Channel_cfg_list[T][ch]['Vth_T1'] - 1
                            print "G:{} T:{} Ch:{} Lowering T at {}".format(GEMROC.GEMROC_ID, T, ch, GEMROC.c_inst.Channel_cfg_list[T][ch]['Vth_T1'])
                        if branch == "E":
                            GEMROC.c_inst.Channel_cfg_list[T][ch]['Vth_T2'] = GEMROC.c_inst.Channel_cfg_list[T][ch]['Vth_T2'] - 1
                        if branch == "both":
                            GEMROC.c_inst.Channel_cfg_list[T][ch]['Vth_T1'] = GEMROC.c_inst.Channel_cfg_list[T][ch]['Vth_T1'] - 1
                            GEMROC.c_inst.Channel_cfg_list[T][ch]['Vth_T2'] = GEMROC.c_inst.Channel_cfg_list[T][ch]['Vth_T2'] - 1

    def rise_thr_below(self, limit, branch):
        """
        Rise the thr below the given limit
        :param limit:
        :param branch:
        :return:
        """
        #TODO aggiungere blocco per VTH=0
        for key,GEMROC in self.GEMROC_reading_dic.items():
            number = int(key.split(" ")[1])
            for T in range (0,8):
                for ch in range(0,64):
                    if self.count_matrix[number][T][ch] < int(limit):
                        if branch == "T":
                            GEMROC.c_inst.Channel_cfg_list[T][ch]['Vth_T1'] = GEMROC.c_inst.Channel_cfg_list[T][ch]['Vth_T1'] + 1
                            print "G:{} T:{} Ch:{} Rising T at {}".format(GEMROC.GEMROC_ID, T, ch, GEMROC.c_inst.Channel_cfg_list[T][ch]['Vth_T1'])
                        if branch == "E":
                            GEMROC.c_inst.Channel_cfg_list[T][ch]['Vth_T2'] = GEMROC.c_inst.Channel_cfg_list[T][ch]['Vth_T2'] + 1
                        if branch == "both":
                            GEMROC.c_inst.Channel_cfg_list[T][ch]['Vth_T1'] = GEMROC.c_inst.Channel_cfg_list[T][ch]['Vth_T1'] + 1
                            GEMROC.c_inst.Channel_cfg_list[T][ch]['Vth_T2'] = GEMROC.c_inst.Channel_cfg_list[T][ch]['Vth_T2'] + 1


#
# class Get_rate(Thread):
#     """
#     Thread to get the numbers and update plots
#     """
#     def __init__(self,caller, queue):
#         self.queue = queue
#         self.caller=caller
#         Thread.__init__(self)
#
#     def run(self):
#         while True:
#             if not self.queue.empty():
#                 print "Dimensione coda: {}".format(self.queue.qsize())
#                 self.caller.count_matrix_channel += self.queue.get()
#                 print "GEMROC {}: {}".format(0, self.caller.count_matrix_channel[0][0])
#
#                 self.caller.update_data()
#             else:
#                 time.sleep(0.2)

def heatmap(data, row_labels, col_labels, ax=None,
            cbar_kw={}, cbarlabel="",spawn_cb=True, **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (N, M).
    row_labels
        A list or array of length N with the labels for the rows.
    col_labels
        A list or array of length M with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    if spawn_cb:
        cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
        cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                   labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-45, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=1)
    ax.tick_params(which="minor", bottom=False, left=False)
    if spawn_cb:
        return im, cbar
    else:
        return im


def annotate_heatmap(im, data=None, valfmt="{x:.2f}",
                     textcolors=["black", "white"],
                     threshold=None, **textkw):
    """
    A function to annotate a heatmap.

    Parameters
    ----------
    im
        The AxesImage to be labeled.
    data
        Data used to annotate.  If None, the image's data is used.  Optional.
    valfmt
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}", or be a
        `matplotlib.ticker.Formatter`.  Optional.
    textcolors
        A list or array of two color specifications.  The first is used for
        values below a threshold, the second for those above.  Optional.
    threshold
        Value in data units according to which the colors from textcolors are
        applied.  If None (the default) uses the middle of the colormap as
        separation.  Optional.
    **kwargs
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    """

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            texts.append(text)

    return texts

