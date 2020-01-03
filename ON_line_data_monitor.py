from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog
from threading import Thread
import socket
import ttk
import numpy as np
from lib import GEM_ACQ_classes as GEM_ACQ
from collections import deque
import time
import binascii

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
        self.main_win = Tk()
        if OS == 'linux2':
            self.main_win.wm_iconbitmap('@' + "." + sep + 'icons' + sep + 'GUFO_ICON.xbm')
        self.main_win.wm_title("Online data monitoring")
        self.GEM_to_config = np.zeros((22))
        Title_frame = Frame(self.main_win)
        Title_frame.pack(side=TOP)

        Label(Title_frame, text="GUFI Online Monitor", font=("Times", 25)).pack(side=LEFT)

        self.tabControl = ttk.Notebook(self.main_win)  # Create Tab Control
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

        ##Control tab for buffer
        self.buffers_frame = Frame(self.main_win)
        self.tabControl.add(self.buffers_frame, text="Buffer control")
        self.buffer_label_list = []
        for i in range(0, len(self.GEM_to_config)):
            if i < 11:
                riga = 0
            else:
                riga = 1
            colonna = ((i) % 11) * 2 + 1
            self.buffer_label_list.append(Label(self.buffers_frame, text=" ---- ",width=6))
            self.buffer_label_list[i].grid(row=riga, column=colonna)
            Label(self.buffers_frame, text='ROC {}'.format(i),width=6,font=(12)).grid(row=riga, column=colonna - 1)

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

    def update_buffers(self, gemroc, lung):
        self.buffer_label_list[gemroc]["text"]=lung

class online_reader(GEM_ACQ.reader):
    def __init__(self, GEMROC_ID, logfile="ACQ_log"):
        GEM_ACQ.reader.__init__(self, GEMROC_ID)
        self.HOST_IP = "127.0.0.1"
        self.HOST_PORT = 58880 + self.GEMROC_ID  # 58880 + 1 # original +2
        self.TIMED_out = False
        self.timeout_for_sockets = 0

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
            print "--GEMROC {}-{}".format(self.GEMROC_ID, e)
            print "Can't bind the socket"

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
            self.data_buffer.append(self.reader.dataSock.recv(32000))
            self.caller2.blink(self.GEMROC_id)

            time.sleep(0.1)


class GEMROC_decoder(Thread):
    def __init__(self, reader, data_buffer, caller2):
        self.GEMROC_id = reader.GEMROC_ID
        Thread.__init__(self)
        self.running = True
        self.reader = reader
        self.data_buffer = data_buffer
        self.caller2 = caller2
        self.last_UDP_number = 0
        self.skipped_UDP_number=[]
    def run(self):
        while self.running:
            if len(self.data_buffer) > 0:
                dato = self.data_buffer.popleft()
                if "Srt" in dato or "End" in dato:
                    print (dato)
                else:
                    self.decode(dato)
            self.caller2.update_buffers(self.GEMROC_id,len(self.data_buffer))
            time.sleep(0.05)
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
        for i in range(0, len(pacchetto) / 8):
            data = pacchetto[i * 8:i * 8 + 8]
            hexdata = binascii.hexlify(data)
            string = "{:064b}".format(int(hexdata, 16))
            inverted = []
            for i in range(8, 0, -1):
                inverted.append(string[(i - 1) * 8:i * 8])
            string_inv = "".join(inverted)
            int_x = int(string_inv, 2)
            raw = "{:064b}  ".format(int_x)

            s = '%016X \n' % int_x
            # acr 2018-06-25 out_file.write(s)
            LOCAL_L1_TIMESTAMP = 0
            ## comment this block to avoid parsing
            ##acr 2017-11-16        if (((int_x & 0xFF00000000000000)>>56) == 0x20):
            tipo = ""
            if (((int_x & 0xE000000000000000) >> 61) == 0x6):
                LOCAL_L1_COUNT_31_6 = int_x >> 32 & 0x3FFFFFF
                LOCAL_L1_COUNT_5_0 = int_x >> 24 & 0x3F
                LOCAL_L1_COUNT = (LOCAL_L1_COUNT_31_6 << 6) + LOCAL_L1_COUNT_5_0
                LOCAL_L1_TIMESTAMP = int_x & 0xFFFF
                HITCOUNT = (int_x >> 16) & 0xFF
                s = 'HEADER :  ' + 'STATUS BIT[2:0]: %01X: ' % ((int_x >> 58) & 0x7) + 'LOCAL L1 COUNT: %08X ' % (LOCAL_L1_COUNT) + 'HitCount: %02X ' % ((int_x >> 16) & 0xFF) + 'LOCAL L1 TIMESTAMP: %04X; ' % (int_x & 0xFFFF)
                # s = 'HEADER :  ' + 'STATUS BIT[2:0]: %01X: '%((int_x >> 58)& 0x7) + 'LOCAL L1 COUNT: %08X '%( LOCAL_L1_COUNT ) + 'HitCount: %02X '%((int_x >> 16) & 0xFF) + 'LOCAL L1 TIMESTAMP: %04X\n'%(int_x & 0xFFFF)
                tipo = "h"
            if (((int_x & 0xE000000000000000) >> 61) == 0x7):
                s = 'TRAILER: ' + 'LOCAL L1  FRAMENUM [23:0]: %06X: ' % ((int_x >> 37) & 0xFFFFFF) + 'GEMROC_ID: %02X ' % ((int_x >> 32) & 0x1F) + 'TIGER_ID: %01X ' % ((int_x >> 27) & 0x7) + 'LOCAL L1 COUNT[2:0]: %01X ' % (
                        (int_x >> 24) & 0x7) + 'LAST COUNT WORD FROM TIGER:CH_ID[5:0]: %02X ' % ((int_x >> 18) & 0x3F) + 'LAST COUNT WORD FROM TIGER: DATA[17:0]: %05X \n' % (int_x & 0x3FFFF)
                tipo = "t"
            if (((int_x & 0xC000000000000000) >> 62) == 0x0):
                LOCAL_L1_TS_minus_TIGER_COARSE_TS = LOCAL_L1_TIMESTAMP - ((int_x >> 32) & 0xFFFF)
                s = 'DATA   : TIGER: %01X ' % ((int_x >> 59) & 0x7) + 'L1_TS - TIGERCOARSE_TS: %d ' % (LOCAL_L1_TS_minus_TIGER_COARSE_TS) + 'LAST TIGER FRAME NUM[2:0]: %01X ' % ((int_x >> 56) & 0x7) + 'TIGER DATA: ChID [base10]: %d ' % ((int_x >> 50) & 0x3F) + 'tacID: %01X ' % (
                        (int_x >> 48) & 0x3) + 'Tcoarse: %04X ' % ((int_x >> 32) & 0xFFFF) + 'Ecoarse: %03X ' % ((int_x >> 20) & 0x3FF) + 'Tfine: %03X ' % ((int_x >> 10) & 0x3FF) + 'Efine: {} \n'.format(int_x & 0x3FF)
                tipo = "d"
            if (((int_x & 0xF000000000000000) >> 60) == 0x4):
                s = 'UDP_SEQNO: ' + 'GEMROC_ID: %02X ' % ((int_x >> 52) & 0x1F) + 'UDP_SEQNO_U48: %f' % (((int_x >> 32) & 0xFFFFF) + ((int_x >> 0) & 0xFFFFFFF)) + "  " \
                                                                                                                                                                      "STATUS BIT[5:3]:{}".format((int_x >> 57) & 0x7)
                if self.last_UDP_number!=(((int_x >> 32) & 0xFFFFF) + ((int_x >> 0) & 0xFFFFFFF))-1:
                    print "manca"
                self.last_UDP_number=(((int_x >> 32) & 0xFFFFF) + ((int_x >> 0) & 0xFFFFFFF))
                print s
                print self.last_UDP_number
                print "--"
                tipo = "u"


Main_menu = menu()
mainloop()
# 
# from collections import deque
# dq = deque(['b','c','d'])
# print dq
# # adding an element to the right of the queue
# dq.append('e')
# print dq
# # adding an element to the left of the queue
# dq.appendleft('a')
# print dq
# # iterate over deque's elements
# for elt in dq:
#     print(elt)
# # pop out an element at from the right of the queue
# dq.pop()
# print dq
# 
# dq.popleft()
