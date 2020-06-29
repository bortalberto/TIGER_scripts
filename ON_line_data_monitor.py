from tkinter import *
from tkinter.ttk import Notebook

from threading import Thread
import socket
import numpy as np
from lib import GEM_ACQ_classes as GEM_ACQ
from collections import deque
import time
import binascii, os
from influxdb import InfluxDBClient
import datetime
import subprocess
import pickle

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
TER = True
OS = sys.platform
if OS == 'win32':
    sep = '\\'
elif OS == 'linux2' or 'linux':
    sep = '/'
else:
    print("ERROR: OS {} non compatible".format(OS))
    sys.exit()


class menu():
    def __init__(self):
        self.main_win = Tk()
        # self.client = InfluxDBClient(host='localhost', port=8086)
        self.client = InfluxDBClient(host='192.168.38.191', port=8086)

        self.client.switch_database('GUFI_DB')
        if OS == 'linux2' or OS =='linux':
            self.main_win.wm_iconbitmap('@' + "." + sep + 'icons' + sep + 'GUFO_ICON.xbm')
        self.main_win.wm_title("Online data monitoring")
        self.GEM_to_config = np.zeros((22))
        Title_frame = Frame(self.main_win)
        Title_frame.pack(side=TOP)

        Label(Title_frame, text="GUFI Online Monitor", font=("Times", 25)).pack(side=LEFT)

        self.tabControl = Notebook(self.main_win)  # Create Tab Control
        self.tabControl.pack(side=TOP)
        self.select_frame = Frame(self.main_win)
        self.tabControl.add(self.select_frame, text="Selection")
        self.icon_on = PhotoImage(file="." + sep + 'icons' + sep + 'on.gif')
        self.icon_off = PhotoImage(file="." + sep + 'icons' + sep + 'off.gif')
        self.icon_bad = PhotoImage(file="." + sep + 'icons' + sep + 'bad.gif')
        self.icon_blink = PhotoImage(file="." + sep + 'icons' + sep + 'blinky.gif')
        self.icon_GUFI1 = PhotoImage(file="." + sep + 'icons' + sep + 'gufi3.gif')
        self.icon_GUFI2 = PhotoImage(file="." + sep + 'icons' + sep + 'gufi4.gif')

        self.handler_list = []
        self.GEMROC_acquiring_dict = {}

        self.grid_frame = Frame(self.select_frame)
        self.grid_frame.pack()
        self.LED = []
        self.button = []
        for i in range(0, len(self.GEM_to_config)):
            if i < 11:
                riga = 0
            else:
                riga = 1
            colonna = ((i) % 11) * 2 + 1
            self.LED.append(Label(self.grid_frame, image=self.icon_off))
            self.LED[i].grid(row=riga, column=colonna)
            self.button.append(Button(self.grid_frame, text='ROC {}'.format(i), command=lambda c=i: self.toggle(c)))
            self.button[i].grid(row=riga, column=colonna - 1)
        self.error_frame = Frame(self.main_win)
        self.error_frame.pack(side=TOP)
        self.Launch_error_check = Label(self.error_frame, text='-', background='white')
        self.Launch_error_check.grid(row=0, column=2, sticky=NW, pady=4)
        self.activate_frame = Frame(self.main_win)
        self.activate_frame.pack(side=TOP)
        self.conn_but = Button(self.activate_frame, text="Connect", command=self.connect_to_acquisition)
        self.conn_but.pack()
        self.start_but = Button(self.activate_frame, text="Start", command=self.start)
        self.start_but.pack()
        self.start_but.config(state='disabled')


        self.get_event_flag=False
        ##Control tab for buffer
        self.buffers_frame = Frame(self.main_win)
        self.tabControl.add(self.buffers_frame, text="Buffer control", )
        self.buffer_label_list = []
        for i in range(0, len(self.GEM_to_config)):
            if i < 11:
                riga = 0
            else:
                riga = 1
            colonna = ((i) % 11) * 2 + 1
            self.buffer_label_list.append(Label(self.buffers_frame, text=" ---- ", width=6))
            self.buffer_label_list[i].grid(row=riga, column=colonna)
            Label(self.buffers_frame, text='ROC {}'.format(i), width=6, font=(12)).grid(row=riga, column=colonna - 1)

        ## FIRST  status FRAME
        self.Status_frame = Frame(self.main_win)
        self.tabControl.add(self.Status_frame, text="Status 1")

        Label(self.Status_frame, text="Missing UDP packets in current subrun", font=("Courier", 25)).pack()
        self.UDP_frame = Frame(self.Status_frame)
        self.UDP_frame.pack()
        self.missing_UDP_label_list = []
        for i in range(0, len(self.GEM_to_config)):
            if i < 11:
                riga = 0
            else:
                riga = 1
            colonna = ((i) % 11) * 2 + 1
            self.missing_UDP_label_list.append(Label(self.UDP_frame, text=" ---- ", width=6))
            self.missing_UDP_label_list[i].grid(row=riga, column=colonna)
            Label(self.UDP_frame, text='ROC {}'.format(i), width=6, font=(12)).grid(row=riga, column=colonna - 1)

        Label(self.Status_frame, text="TP efficency", font=("Courier", 25)).pack()
        self.TP_frame = Frame(self.Status_frame)
        self.TP_frame.pack()

        self.TP_label_list = []
        self.TIG_list = []
        for i in range(0, len(self.GEM_to_config) - 1):
            if i < 7:
                riga = 0
            elif i < 14:
                riga = 1
            else:
                riga = 2
            colonna = ((i) % 7) * 2 + 1
            self.TP_label_list.append(Frame(self.TP_frame, width=6))
            self.TP_label_list[i].grid(row=riga, column=colonna)
            for TIG in range(0, 8):
                if TIG < 4:
                    colonna2 = 0
                else:
                    colonna2 = 1
                self.TIG_list.append(Label(self.TP_label_list[i], text=" -- ", width=3))
                self.TIG_list[TIG + i * 8].grid(row=TIG - colonna2 * 4, column=colonna2 * 2 + 1)
                Label(self.TP_label_list[i], text="{}".format(TIG),fg="red").grid(row=TIG - colonna2 * 4, column=colonna2 * 2)
            Label(self.TP_frame, text='ROC {}'.format(i), width=6, font=(12)).grid(row=riga, column=colonna - 1)

        Label(self.Status_frame, text="Status bits", font=("Courier", 25)).pack()
        self.StatusBit_frame = Frame(self.Status_frame)
        self.StatusBit_frame.pack()
        self.status_bit_list_frame = []
        self.single_status_bit = []
        # TODO to solve one day
        for i in range(0, len(self.GEM_to_config) - 1):
            if i < 7:
                riga = 0
            elif i < 14:
                riga = 1
            else:
                riga = 2
            colonna = ((i) % 7) * 2 + 1
            self.status_bit_list_frame.append(Frame(self.StatusBit_frame, width=3))
            self.status_bit_list_frame[i].grid(row=riga, column=colonna)
            for st_bit in range(0, 8):
                if st_bit < 4:
                    colonna2 = 0
                else:
                    colonna2 = 1
                self.single_status_bit.append(Label(self.status_bit_list_frame[i], text=" -- ", width=4))
                self.single_status_bit[st_bit + i * 8].grid(row=st_bit - colonna2 * 4, column=colonna2 * 2 + 1)
                Label(self.status_bit_list_frame[i], text="{}".format(st_bit),fg="red").grid(row=st_bit - colonna2 * 4, column=colonna2 * 2)
            Label(self.StatusBit_frame, text='ROC {}'.format(i), width=6, font=(12)).grid(row=riga, column=colonna - 1)
        Label(self.Status_frame, text="Bit 0:XCVR_rx_alignment_error, Bit 1 global_rx_error, Bit 2 top_daq_pll_unlocked_sticky_flag, Bit 3 enabled_FIFO_FULL_error, Bit 4 Header_Misalignment_across_FEBs_error, Bit 5 top_L1_chk_error", font=("Courier", 10)).pack()

        ## SECOND status frame
        self.Status_frame_2 = Frame(self.main_win)
        self.tabControl.add(self.Status_frame_2, text="Status 2")

        Label(self.Status_frame_2, text="Last UDP packet counter", font=("Courier", 25)).pack()
        self.UDP_frame_2 = Frame(self.Status_frame_2)
        self.UDP_frame_2.pack()
        self.last_UDP_list = []
        for i in range(0, len(self.GEM_to_config)):
            if i < 11:
                riga = 0
            else:
                riga = 1
            colonna = ((i) % 11) * 2 + 1
            self.last_UDP_list.append(Label(self.UDP_frame_2, text=" ---- ", width=6))
            self.last_UDP_list[i].grid(row=riga, column=colonna)
            Label(self.UDP_frame_2, text='ROC {}'.format(i), width=6, font=(12)).grid(row=riga, column=colonna - 1)

            # Label(self.Status_frame, text="TP efficency", font=("Courier", 25)).pack()
            # self.TP_frame = Frame(self.Status_frame)
            # self.TP_frame.pack()
            # self.TP_label_list = []
            # self.TIG_list = []
            # for i in range(0, len(self.GEM_to_config) - 1):
            #     if i < 7:
            #         riga = 0
            #     elif i < 14:
            #         riga = 1
            #     else:
            #         riga = 2
            #     colonna = ((i) % 7) * 2 + 1
            #     self.TP_label_list.append(Frame(self.TP_frame, width=6))
            #     self.TP_label_list[i].grid(row=riga, column=colonna)
            #     for TIG in range(0, 8):
            #         if TIG < 4:
            #             colonna2 = 0
            #         else:
            #             colonna2 = 1
            #         self.TIG_list.append(Label(self.TP_label_list[i], text=" -- ", width=3))
            #         self.TIG_list[TIG + i * 8].grid(row=TIG - colonna2 * 4, column=colonna2 * 2 + 1)
            #         Label(self.TP_label_list[i], text="{}".format(TIG)).grid(row=TIG - colonna2 * 4, column=colonna2 * 2)
            #     Label(self.TP_frame, text='ROC {}'.format(i), width=6, font=(12)).grid(row=riga, column=colonna - 1)


        Label(self.Status_frame_2, text="Noise rate", font=("Courier", 25)).pack()
        self.Noise_frame = Frame(self.Status_frame_2)
        self.Noise_frame.pack()

        self.Noise_frame_list = []
        self.noise_list = []
        for i in range(0, len(self.GEM_to_config) - 1):
            if i < 7:
                riga = 0
            elif i < 14:
                riga = 1
            else:
                riga = 2
            colonna = ((i) % 7) * 2 + 1
            self.Noise_frame_list.append(Frame(self.Noise_frame, width=6))
            self.Noise_frame_list[i].grid(row=riga, column=colonna)
            for TIG in range(0, 8):
                if TIG < 4:
                    colonna2 = 0
                else:
                    colonna2 = 1
                self.noise_list.append(Label(self.Noise_frame_list[i], text=" -- ", width=7))
                self.noise_list[TIG + i * 8].grid(row=TIG - colonna2 * 4, column=colonna2 * 2 + 1)
                Label(self.Noise_frame_list[i], text="{}".format(TIG),fg="red").grid(row=TIG - colonna2 * 4, column=colonna2 * 2)
            Label(self.Noise_frame, text='ROC {}'.format(i), width=6, font=(12)).grid(row=riga, column=colonna - 1)

        ## Alarms
        self.Allarm_tab = Frame(self.main_win)
        self.tabControl.add(self.Allarm_tab, text="Allarms ")

        r =[1,2]
        theta = [0,3.14]

        self.Events_Vi = Frame(self.main_win)
        self.tabControl.add(self.Events_Vi, text="Events visualizer ")
        first_war=Frame(self.Events_Vi)
        first_war.pack()
        Button(first_war,command=self.get_event,text="Get next event").pack()
        second_fr=Frame(self.Events_Vi)
        second_fr.pack()
        self.fig = Figure(figsize=(7, 7))
        self.plot_rate = self.fig.add_subplot(111, polar=True)
        self.plot_rate.set_rorigin(-1)
        self.scatter, = self.plot_rate.plot(theta, r,'r+',alpha=0.75)
        self.plot_rate.set_title("Event {}")
        self.canvas = FigureCanvasTkAgg(self.fig, master=second_fr)
        self.canvas.get_tk_widget().pack(side=BOTTOM)
        self.canvas.draw()
        self.canvas.flush_events()
        self.toolbar = NavigationToolbar2Tk(self.canvas, second_fr)
        self.toolbar.draw()


    def get_event(self):
        """
        Will get the next event for data visualizzation
        :return:
        """
        udp_list_int = []
        for elem in self.last_UDP_list[:]:
            try:
                udp_list_int.append(int(elem["text"]))
            except ValueError:
                pass
        self.UDP_trigger = np.max(udp_list_int)+4
        self.get_event_flag=True #This flag means that we will start to save the data from when the value in UDP
        hit_stack=[]
        running=True
        print (self.UDP_trigger)
        thread_for_plot=Plotter(self)
        thread_for_plot.start()
    def connect_to_acquisition(self):
        if np.count_nonzero(self.GEM_to_config) < 1:
            self.Launch_error_check['text'] = "Select at least one GEMROC"
        else:
            for button in self.button:
                button.config(state='disabled')
            self.Launch_error_check['text'] = "Connected"
        self.conn_but['text'] = "Disconnect"
        self.conn_but.config(command=self.disconnect)
        self.start_but.config(state='normal')

    def disconnect(self):
        for button in self.button:
            button.config(state='normal')
        self.Launch_error_check['text'] = "Disconnected"
        self.conn_but['text'] = "Connect"
        self.conn_but.config(command=self.connect_to_acquisition)
        self.start_but.config(state='disabled')

    def toggle(self, i):
        if self.GEM_to_config[i] == 0:
            self.GEM_to_config[i] = 1
        else:
            self.GEM_to_config[i] = 0
            del self.GEMROC_acquiring_dict["GEMROC {}".format(i)]
        self.convert0(i)

    def convert0(self, i):
        if self.GEM_to_config[i] == 1:
            try:
                self.handler_list.append(online_reader(i))
                self.LED[i]["image"] = self.icon_on
                self.Launch_error_check['text'] = "Listening for data from GEMROC {}".format(i)

            except  Exception as error:
                self.Launch_error_check['text'] = "GEMROC {}: {}".format(i, error)
                self.LED[i]["image"] = self.icon_bad


        else:
            self.LED[i]["image"] = self.icon_off
            for j in range(0, len(self.handler_list)):
                if self.handler_list[j].GEMROC_ID == i:
                    self.Launch_error_check['text'] = "Stopped listening for data from GEMROC {}".format(i)
                    break
        self.update_menu()

    def update_menu(self):
        for i in range(0, len(self.handler_list)):
            ID = self.handler_list[i].GEMROC_ID
            self.GEMROC_acquiring_dict["GEMROC {}".format(ID)] = self.handler_list[i]

    def start(self):
        for key in self.GEMROC_acquiring_dict:
            self.GEMROC_acquiring_dict[key].start_socket()
        self.runner = runner(self.GEMROC_acquiring_dict, self)
        self.runner.run()

        self.Launch_error_check['text'] = "Acquiring data"
        self.start_but['text'] = "Stop"
        self.start_but.config(command=self.stop)
        self.conn_but.config(state='disabled')

    def stop(self):
        self.runner.stop()
        self.Launch_error_check['text'] = "Stopping acquisition"
        self.start_but['text'] = "Start"
        self.start_but.config(command=self.start)
        for key in self.GEMROC_acquiring_dict:
            self.GEMROC_acquiring_dict[key].stop_socket()
        self.conn_but.config(state='normal')

    def blink(self, gemroc, update=1):
        self.LED[gemroc]["image"] = self.icon_blink
        if update == 1:
            self.main_win.after(100, lambda: self.blink(gemroc, 2))
        if update == 2:
            self.LED[gemroc]["image"] = self.icon_on

    def bad_blink(self, gemroc, update=1):
        self.LED[gemroc]["image"] = self.icon_bad
        if update == 1:
            self.main_win.after(200, lambda: self.blink(gemroc, 2))
        if update == 2:
            self.LED[gemroc]["image"] = self.icon_on

    def update_buffers(self, gemroc, lung):
        self.buffer_label_list[gemroc]["text"] = lung

    def send_to_db(self, json):
        try:
            self.client.write_points(json)
        except Exception as e:
            print("Unable to log in infludb: {}\n json: {}".format(e,json))


class online_reader(GEM_ACQ.reader):
    def __init__(self, GEMROC_ID, logfile="ACQ_log"):
        GEM_ACQ.reader.__init__(self, GEMROC_ID)
        self.HOST_IP = "127.0.0.1"
        self.HOST_PORT = 57880 + self.GEMROC_ID  # 57880 + 1 # original +2
        self.TIMED_out = False
        self.timeout_for_sockets = 180

    def stop_socket(self):
        self.dataSock.close()

    def start_socket(self):
        self.TIMED_out = False

        try:
            self.dataSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.dataSock.settimeout(self.timeout_for_sockets)
            self.dataSock.bind((self.HOST_IP, self.HOST_PORT))
            self.dataSock.setblocking(True)
        except Exception as e:
            print( "--GEMROC {}-{}".format(self.GEMROC_ID, e))
            print( "Can't bind the socket")

        # self.dataSock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8388608 )
        # print self.dataSock.getsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF)

    def __del__(self):
        self.cloning_sock.close()


class runner(Thread):

    def __init__(self, GEMROC_acquiring_dict, caller):
        Thread.__init__(self)
        self.running = True
        self.GEMROC_acquiring_dict = GEMROC_acquiring_dict
        self.data_buffer = {}
        for number, GEMROC in self.GEMROC_acquiring_dict.items():
            self.data_buffer[number] = deque()
        self.acquirer_list = []
        self.decoder_list = []
        self.caller = caller

    def run(self):
        for number, GEMROC in self.GEMROC_acquiring_dict.items():
            self.acquirer_list.append(GEMROC_runner(GEMROC, self.data_buffer[number], self.caller))
            self.decoder_list.append(GEMROC_decoder(GEMROC, self.data_buffer[number], self.caller))

        for thread in self.acquirer_list:
            thread.start()

        for thread in self.decoder_list:
            thread.start()

    def stop(self):
        for thread in self.acquirer_list:
            thread.running = False

        for thread in self.decoder_list:
            thread.running = False


class GEMROC_runner(Thread):
    def __init__(self, reader, data_buffer, caller2):
        self.GEMROC_id = reader.GEMROC_ID
        Thread.__init__(self)
        self.running = True
        self.reader = reader
        self.data_buffer = data_buffer
        self.caller2 = caller2

    def run(self):
        while self.running:
            dato = self.reader.dataSock.recv(32000)
            self.log_pkt_DB(size=len(dato))
            self.data_buffer.append(dato)
            self.caller2.blink(self.GEMROC_id)


    def log_pkt_DB(self, size):
        """
        Logs the packet size in the db
        :param size:
        :return:
        """
        json_body = [{
            "measurement": "Online",
            "tags": {
                "type": "pkt_log",
                "gemroc": self.GEMROC_id
            },
            "time": str(datetime.datetime.utcnow()),
            "fields": {
                "size": size
            },
            "retention_policy":"online_data"
        }]
        self.caller2.send_to_db(json_body)


class GEMROC_decoder(Thread):
    def __init__(self, reader, data_buffer, caller2):
        self.GEMROC_id = reader.GEMROC_ID
        Thread.__init__(self)
        self.running = True
        self.reader = reader
        self.data_buffer = data_buffer
        self.caller2 = caller2
        self.last_UDP_number = 0
        self.skipped_UDP_number = []
        self.RUN = ""
        self.subRun = ""
        self.folder = ""
        self.logpath = ""
        self.first_packet = True
        self.missing_pkt_counter = 0
        self.number_TP = np.zeros((8))
        self.number_TP_rst = np.zeros((8))
        self.noise_rate = np.zeros((8))
        self.signal_rate = np.zeros((8))

        self.number_pkts_to_log = 20
        self.number_TP_rst = np.zeros((8))
        self.pkts_counter = 0
        self.pkts_counter_rst = 0
        self.noise_rate_rst = np.zeros((8))
        self.signal_rate_rst = np.zeros((8))

        self.save_this=False
        self.event_get_done=True
        self.event_to_display = []
    def run(self):

        while self.running:
            if len(self.data_buffer) > 0:
                dato_raw = self.data_buffer.popleft()
                try:
                    dato=dato_raw.decode()
                except:
                    self.decode(dato_raw)
                    dato="Dato"
                if "Srt" in dato or "End" in dato:
                    self.RUN = dato.split(" ")[3]
                    self.subRun = dato.split(" ")[5]
                    if "Srt" in dato:
                        self.reset_counter()
                        logpath_raw = dato.split(" ")[7].split("/")[:-1]
                        for piece in logpath_raw:
                            self.logpath = self.logpath + str(piece) + "/"
                        self.logpath = self.logpath + "Online_monitor_log_GEMROC_{}".format(self.GEMROC_id)
                        self.write_log("Logging started --> {}, Subrun {}".format(self.RUN, self.subRun))
                        self.send_run_start()
                    if "End" in dato:
                        self.write_log("Subrun end --> {}, Subrun {}".format(self.RUN, self.subRun))
                        self.send_run_end()
                        if TER:
                            if not os.path.isdir ("/home/cgemlab2/data/{}".format(self.RUN)):
                                os.mkdir ("/home/cgemlab2/data/{}".format(self.RUN))
                            if not os.path.isdir ("/home/cgemlab2/TIGER_Event_Reconstruction/TIGER_Event_Reconstruction/data/raw_root/{}".format(self.RUN.split("_")[1])):
                                os.mkdir ("/home/cgemlab2/TIGER_Event_Reconstruction/TIGER_Event_Reconstruction/data/raw_root/{}".format(self.RUN.split("_")[1]))
                            time.sleep(0.05)
                            os.system("cp ./data_folder/{}/SubRUN_{}_GEMROC_{}_TM.dat ~/data/{}/".format(self.RUN,self.subRun,self.GEMROC_id,self.RUN))
                            # print ("Copy return: {}".format(result))
                            subprocess.call(["/home/cgemlab2/TIGER_Event_Reconstruction/TIGER_Event_Reconstruction/TER.sh","-F",str(self.RUN.split("_")[1]), str(self.subRun), str(self.GEMROC_id)],timeout=120)
                            # print(proc.communicate())
                            key = list(self.caller2.GEMROC_acquiring_dict.keys())[0] #Only the first gemroc of the list will run the analysis
                            if self.GEMROC_id == int(key.split(" ")[1]):
                                time.sleep(30)
                                print ("GEMROC {} is running the data decode".format(self.GEMROC_id))
                                subprocess.call(["/home/cgemlab2/TIGER_Event_Reconstruction/TIGER_Event_Reconstruction/TER.sh", "-V", str(self.RUN.split("_")[1]), str(self.subRun)],timeout=120)
                                subprocess.call(["/home/cgemlab2/TIGER_Event_Reconstruction/TIGER_Event_Reconstruction/TER.sh", "-A", str(self.RUN.split("_")[1]), str(self.subRun)],timeout=120)
                                subprocess.call(["/home/cgemlab2/TIGER_Event_Reconstruction/TIGER_Event_Reconstruction/TER.sh", "-E", str(self.RUN.split("_")[1]), str(self.subRun)],timeout=120)
                                # subprocess.call(["/home/cgemlab2/TIGER_Event_Reconstruction/TIGER_Event_Reconstruction/TER.sh", "-C", str(self.RUN.split("_")[1]), str(self.subRun)])
                                # print(subprocess.call(["/home/cgemlab2/TIGER_Event_Reconstruction/TIGER_Event_Reconstruction/TER.sh", "-Q", str(self.RUN.split("_")[1]), str(self.subRun)]))
                                subprocess.call(["root", "-b", "-l", "-q","/home/cgemlab2/TIGER_Event_Reconstruction/TIGER_Event_Reconstruction/data/raw_root/data_status.cpp({})".format(int(self.RUN.split("_")[1]))],timeout=120)
                                subprocess.call(["root", "-b", "-l", "-q","/home/cgemlab2/TIGER_Event_Reconstruction/TIGER_Event_Reconstruction/data/raw_root/data_status_last_subs.cpp({}, {})".format(int(self.RUN.split("_")[1]), int (self.subRun))],timeout=120)

            self.caller2.update_buffers(self.GEMROC_id, len(self.data_buffer))
            time.sleep(0.01)
            # def run(self):
        # with open("./data_folder/prova.dat", "w+") as test_file:
        #     while self.running:
        #         if len(self.data_buffer)>0:
        #             dato= self.data_buffer.popleft()
        #             if "Srt" in dato or "End" in dato:
        #                 print dato
        #             else:
        #                 tipo=self.decode(dato)
        #                 test_file.write(dato)
        #                 if tipo=="u":
        #                     test_file.write("_spacer_")
        #         time.sleep(0.001)

    def decode(self, pacchetto):
        send_gem_error_updates = False
        LOCAL_L1_TIMESTAMP = 0

        for i in range(0, int(len(pacchetto) / 8)):
            data = pacchetto[i * 8:i * 8 + 8]
            hexdata = binascii.hexlify(data)
            string = "{:064b}".format(int(hexdata, 16))
            inverted = []
            for i in range(8, 0, -1):
                inverted.append(string[(i - 1) * 8:i * 8])
            string_inv = "".join(inverted)
            int_x = int(string_inv, 2)

            if (((int_x & 0xE000000000000000) >> 61) == 0x6):
                LOCAL_L1_COUNT_31_6 = int_x >> 32 & 0x3FFFFFF
                LOCAL_L1_COUNT_5_0 = int_x >> 24 & 0x3F
                LOCAL_L1_COUNT = (LOCAL_L1_COUNT_31_6 << 6) + LOCAL_L1_COUNT_5_0
                LOCAL_L1_TIMESTAMP = int_x & 0xFFFF
                HITCOUNT = (int_x >> 16) & 0xFF
                s = 'HEADER :  ' + 'STATUS BIT[2:0]: %01X: ' % ((int_x >> 58) & 0x7) + 'LOCAL L1 COUNT: %08X ' % (LOCAL_L1_COUNT) + 'HitCount: %02X ' % ((int_x >> 16) & 0xFF) + 'LOCAL L1 TIMESTAMP: %04X; ' % (int_x & 0xFFFF)
                # # s = 'HEADER :  ' + 'STATUS BIT[2:0]: %01X: '%((int_x >> 58)& 0x7) + 'LOCAL L1 COUNT: %08X '%( LOCAL_L1_COUNT ) + 'HitCount: %02X '%((int_x >> 16) & 0xFF) + 'LOCAL L1 TIMESTAMP: %04X\n'%(int_x & 0xFFFF)
                # tipo = "h"
                ##Prints status bits if changed:

                if ((int_x >> 58) & 0x1) != self.caller2.single_status_bit[self.GEMROC_id * 8 + 0]["text"]:
                    self.caller2.single_status_bit[self.GEMROC_id * 8 + 0]["text"] = ((int_x >> 58) & 0x1)
                    send_gem_error_updates = True
                if ((int_x >> 59) & 0x1) != self.caller2.single_status_bit[self.GEMROC_id * 8 + 1]["text"]:
                    self.caller2.single_status_bit[self.GEMROC_id * 8 + 1]["text"] = ((int_x >> 59) & 0x1)
                    send_gem_error_updates = True
                if ((int_x >> 60) & 0x1) != self.caller2.single_status_bit[self.GEMROC_id * 8 + 2]["text"]:
                    self.caller2.single_status_bit[self.GEMROC_id * 8 + 2]["text"] = ((int_x >> 60) & 0x1)
                    send_gem_error_updates = True


                ##Stuff for data display:
                if self.caller2.get_event_flag:
                    if LOCAL_L1_COUNT==self.caller2.UDP_trigger:
                        self.save_this=True
                        self.event_get_done=False
                        self.event_to_display=[]

            if (((int_x & 0xE000000000000000) >> 61) == 0x7):
                s = 'TRAILER: ' + 'LOCAL L1  FRAMENUM [23:0]: %06X: ' % ((int_x >> 37) & 0xFFFFFF) + 'GEMROC_ID: %02X ' % ((int_x >> 32) & 0x1F) + 'TIGER_ID: %01X ' % ((int_x >> 27) & 0x7) + 'LOCAL L1 COUNT[2:0]: %01X ' % (
                        (int_x >> 24) & 0x7) + 'LAST COUNT WORD FROM TIGER:CH_ID[5:0]: %02X ' % ((int_x >> 18) & 0x3F) + 'LAST COUNT WORD FROM TIGER: DATA[17:0]: %05X \n' % (int_x & 0x3FFFF)
                tipo = "t"

            if (((int_x & 0xC000000000000000) >> 62) == 0x0):
                # print LOCAL_L1_TIMESTAMP
                LOCAL_L1_TS_minus_TIGER_COARSE_TS = LOCAL_L1_TIMESTAMP - ((int_x >> 32) & 0xFFFF)
                channel = ((int_x >> 50) & 0x3F)
                tiger = (int_x >> 59) & 0x7
                s = 'DATA   : TIGER: %01X ' % ((int_x >> 59) & 0x7) + 'L1_TS - TIGERCOARSE_TS: %d ' % (LOCAL_L1_TS_minus_TIGER_COARSE_TS) + 'LAST TIGER FRAME NUM[2:0]: %01X ' % ((int_x >> 56) & 0x7) + 'TIGER DATA: ChID [base10]: %d ' % ((int_x >> 50) & 0x3F) + 'tacID: %01X ' % (
                         (int_x >> 48) & 0x3) + 'Tcoarse: %04X ' % ((int_x >> 32) & 0xFFFF) + 'Ecoarse: %03X ' % ((int_x >> 20) & 0x3FF) + 'Tfine: %03X ' % ((int_x >> 10) & 0x3FF) + 'Efine: {} \n'.format(int_x & 0x3FF)
                # tipo = "d"
                # print LOCAL_L1_TS_minus_TIGER_COARSE_TS
                if channel == 62:  ##Counts TP
                    self.number_TP[tiger] += 1
                    self.number_TP_rst[tiger] += 1  ##Counts eff every 50 pkts and store it



                elif 1380 < LOCAL_L1_TS_minus_TIGER_COARSE_TS < 1420:
                    self.signal_rate[tiger] += 1
                    self.signal_rate_rst[tiger] += 1
                    ##Stuff for event display:
                    if self.save_this:
                        self.event_to_display.append((self.GEMROC_id, ((int_x >> 59) & 0x7), ((int_x >> 50) & 0x3F)))

                elif LOCAL_L1_TS_minus_TIGER_COARSE_TS > 1420:
                    self.noise_rate[tiger] += 1
                    self.noise_rate_rst[tiger] += 1




            if (((int_x & 0xF000000000000000) >> 60) == 0x4):
                self.pkts_counter_rst += 1
                self.pkts_counter += 1
                s = 'UDP_SEQNO: ' + 'GEMROC_ID: %02X ' % ((int_x >> 52) & 0x1F) + 'UDP_SEQNO_U48: %f' % (((int_x >> 32) & 0xFFFFF) + ((int_x >> 0) & 0xFFFFFFF)) + "  " \
                    # Check UDP packets                                                                                                                                           "STATUS BIT[5:3]:{}".format((int_x >> 57) & 0x7)
                if self.caller2.single_status_bit[self.GEMROC_id * 8 + 3]["text"] != ((int_x >> 57) & 0x1):
                    send_gem_error_updates = True
                    self.caller2.single_status_bit[self.GEMROC_id * 8 + 3]["text"] = ((int_x >> 57) & 0x1)
                if self.caller2.single_status_bit[self.GEMROC_id * 8 + 4]["text"] != ((int_x >> 58) & 0x1):
                    send_gem_error_updates = True
                    self.caller2.single_status_bit[self.GEMROC_id * 8 + 4]["text"] = ((int_x >> 58) & 0x1)
                if self.caller2.single_status_bit[self.GEMROC_id * 8 + 5]["text"] != ((int_x >> 59) & 0x1):
                    send_gem_error_updates = True
                    self.caller2.single_status_bit[self.GEMROC_id * 8 + 5]["text"] = ((int_x >> 59) & 0x1)

                if not self.first_packet:
                    if self.last_UDP_number != (((int_x >> 32) & 0xFFFFF) + ((int_x >> 0) & 0xFFFFFFF)) - 1:
                        pacchetti_mancanti = (((int_x >> 32) & 0xFFFFF) + ((int_x >> 0) & 0xFFFFFFF)) - self.last_UDP_number - 1
                        print( "Missing {} UDP packets, up to {}".format(pacchetti_mancanti, self.last_UDP_number + 1))
                        self.write_log("Missing {} UDP packets, up to{}".format(pacchetti_mancanti, self.last_UDP_number + 1))
                        self.log_missing_UDP(self.last_UDP_number + 1, pacchetti_mancanti)
                        self.missing_pkt_counter += 1
                        self.caller2.bad_blink(self.GEMROC_id)
                    self.caller2.missing_UDP_label_list[self.GEMROC_id]["text"] = self.missing_pkt_counter

                    self.last_UDP_number = (((int_x >> 32) & 0xFFFFF) + ((int_x >> 0) & 0xFFFFFFF))
                    self.caller2.last_UDP_list[self.GEMROC_id]["text"] = self.last_UDP_number
                else:
                    self.first_packet = False
                    self.last_UDP_number = (((int_x >> 32) & 0xFFFFF) + ((int_x >> 0) & 0xFFFFFFF))

                    # Update rate list
                if self.last_UDP_number != 0:
                    for T in range(0, 8):
                        self.caller2.TIG_list[self.GEMROC_id * 8 + T]["text"] = "{:.2f}".format(self.number_TP[T] / self.last_UDP_number)
                    for T in range(0, 8):
                        self.caller2.noise_list[self.GEMROC_id * 8 + T]["text"] = "{:.2e}".format(self.number_TP[T] / (64*self.pkts_counter * 6.25e-9)) #Average over channels



                if self.caller2.get_event_flag:
                    if self.last_UDP_number==self.caller2.UDP_trigger:
                        self.save_this=False #Stop saving packets
                        self.event_get_done=True
                # print (s)
        if self.pkts_counter_rst > self.number_pkts_to_log:
            eff_list = [elem / (self.number_pkts_to_log+1) for elem in self.number_TP_rst]
            self.log_perf(eff_list)
            self.number_TP_rst = np.zeros((8))
            self.pkts_counter_rst = 0
            send_gem_error_updates = True
        if send_gem_error_updates:  ##If any status bit changed, update it on DB
            self.send_gemroc_error_status_to_DB()
    def write_log(self, text):
        with open(self.logpath, 'a+') as logfile:
            logfile.write("{}\n".format(text))

    def reset_counter(self):
        self.missing_pkt_counter = 0
        self.logpath = ""
        self.number_TP = np.zeros((8))
        self.noise_rate = np.zeros((8))
        self.signal_rate = np.zeros((8))
        self.noise_rate_rst = np.zeros((8))
        self.signal_rate_rst = np.zeros((8))
        self.pkts_counter_rst=0
        self.pkts_counter = 0
        self.first_packet=True
    def send_mail(self, error, subject="DAQ stop"):
        text = error
        os.system("python3 {}send_mail.py '{}' '{}' ".format("lib" + sep, subject, text))

    def log_missing_UDP(self, missing_pkt, number_pkt_missing):
        """
        Logs the packet size in the db
        :param size:
        :return:
        """
        json_body = [{
            "measurement": "Offline",
            "tags": {
                "type": "UDP_missing",
                "gemroc": self.GEMROC_id
            },
            "time": str(datetime.datetime.utcnow()),
            "fields": {
                "missing_pkt": missing_pkt,
                "number_of_pkt_missing": number_pkt_missing
            }
        }]
        self.caller2.send_to_db(json_body)

    def log_perf(self, eff_list):
        """
        LOG tp efficency and noise/sig rates
        :return:
        """
        json_body = [{
            "measurement": "Offline",
            "tags": {
                "type": "Performances_N_pkts",
                "gemroc": self.GEMROC_id,
                "tiger": -1

            },
            "time": str(datetime.datetime.utcnow()),
            "fields": {
                "pkts_counter": self.number_pkts_to_log,
            }
        }]
        for T in range(0, 8):
            json_body[0]["tags"]["tiger"] = T
            json_body[0]["fields"]["TP_eff"] = eff_list[T]
            json_body[0]["fields"]["Noise_rate"] = self.noise_rate_rst[T] / ((self.number_pkts_to_log+1) * 6.25e-9 * 39)
            json_body[0]["fields"]["Sig_rate"] = self.signal_rate_rst[T] / ((self.number_pkts_to_log+1) * 6.25e-9 * 149)
            self.caller2.send_to_db(json_body)

        self.noise_rate_rst=np.zeros((8))
        self.signal_rate_rst=np.zeros((8))

    def send_gemroc_error_status_to_DB(self):
        """
        Log the error GEMROC status in DB
        :return:
        """
        to_send=np.zeros((6))
        for field in range (0,6):
            if self.caller2.single_status_bit[self.GEMROC_id * 8 + field]["text"]=="--":
                to_send[field] = 0
            else:
                to_send[field] = int(self.caller2.single_status_bit[self.GEMROC_id * 8 + 0]["text"])
        json_body = [{
            "measurement": "Offline",
            "tags": {
                "type": "GEMROC_status_bits",
                "gemroc": self.GEMROC_id
            },
            "time": str(datetime.datetime.utcnow()),
            "fields": {
                "Bit 0:XCVR_rx_alignment_error": self.caller2.single_status_bit[self.GEMROC_id * 8 + 0]["text"],
                "Bit 1:global_rx_error": self.caller2.single_status_bit[self.GEMROC_id * 8 + 1]["text"],
                "Bit 2:top_daq_pll_unlocked_sticky_flag": self.caller2.single_status_bit[self.GEMROC_id * 8 + 2]["text"],
                "Bit 3:enabled_FIFO_FULL_error": self.caller2.single_status_bit[self.GEMROC_id * 8 + 3]["text"],
                "Bit 4:Header_Misalignment_across_FEBs_error": self.caller2.single_status_bit[self.GEMROC_id * 8 + 4]["text"],
                "Bit 5:top_L1_chk_error": self.caller2.single_status_bit[self.GEMROC_id * 8 + 5]["text"]
            }
        }]
        self.caller2.send_to_db(json_body)

    def send_run_start(self):
        """
        Log the error GEMROC status in DB
        :return:
        """
        json_body = [{
            "measurement": "Offline",
            "tags": {
                "type": "RUN_start",
                "gemroc": self.GEMROC_id
            },
            "time": str(datetime.datetime.utcnow()),
            "fields": {
                "run":self.RUN,
                "subrun": self.subRun
            }
        }]
        self.caller2.send_to_db(json_body)


    def send_run_end(self):
        """
        Log the error GEMROC status in DB
        :return:
        """
        json_body = [{
            "measurement": "Offline",
            "tags": {
                "type": "RUN_end",
                "gemroc": self.GEMROC_id
            },
            "time": str(datetime.datetime.utcnow()),
            "fields": {
                "run": self.RUN,
                "subrun": self.subRun
            }
        }]
        self.caller2.send_to_db(json_body)

class Plotter(Thread):
    def __init__(self,caller):
        Thread.__init__(self)
        self.caller=caller

    def run(self):
        hit_stack=[]
        running=True
        for elem in self.caller.runner.decoder_list:
            elem.event_get_done = False
            elem.event_to_display = []
        while running:
            for elem in self.caller.runner.decoder_list:
                running = False
                time.sleep(0.05)
                if not elem.event_get_done:
                    running = True
                    break

        for elem in self.caller.runner.decoder_list:
            hit_stack.append(elem.event_to_display)

        with open("." + sep + "lib" + sep + "mapping.pickle", "rb") as filein:
            mapping_matrix = pickle.load(filein)
        L1_x=[]
        L2_x=[]
        for lista_GEMROC in hit_stack:
            for tupla in lista_GEMROC:
                if tupla[0]<4:
                    if mapping_matrix[tupla[0]][tupla[1]][tupla[2]].split("-")[0]=="X":
                        L1_x.append(float(mapping_matrix[tupla[0]][tupla[1]][tupla[2]].split("-")[1]))

                elif tupla[0]<11:
                    if mapping_matrix[tupla[0]][tupla[1]][tupla[2]].split("-")[0]=="X":
                        L2_x.append(float(mapping_matrix[tupla[0]][tupla[1]][tupla[2]].split("-")[1]))
        R=[]
        THETA=[]
        for elem in L1_x:
            R.append(1)
            THETA.append(elem/856*6.28)
        for elem in L2_x:
            R.append(2)
            THETA.append(elem/1260*6.28)
        print (THETA)
        self.caller.scatter.set_xdata(THETA)
        self.caller.scatter.set_ydata(R)

        self.caller.canvas.draw()
        self.caller.canvas.flush_events()

Main_menu = menu()
mainloop()
