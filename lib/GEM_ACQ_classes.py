import time
from threading import Thread
import socket
import binascii
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import datetime
import matplotlib.gridspec as gridspec
import os
import pickle

OS = sys.platform
if OS == 'win32':
    sep = '\\'
elif OS == 'linux2':
    sep = '/'
else:
    print("ERROR: OS {} non compatible".format(OS))
    sys.exit()


class Thread_handler(Thread): #In order to scan during configuration is mandatory to use multithreading
    def __init__(self, name,acq_time,reader):
        Thread.__init__(self)
        self.name = name
        self.acq_time=acq_time
        self.reader=reader
    def run(self):
        datapath= "."+sep+"data_folder"+sep+"Spill_{}_GEMROC_{}.dat".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),self.reader.GEMROC_ID)
        # with open(self.reader.log_path, 'a') as log_file:
        #     log_file.write("{} --Launching acquisition on GEMROC {} for {} seconds\n".format(time.ctime(),self.reader.GEMROC_ID,self.acq_time))

        time0=time.time()
        data_list = []
        self.reader.start_socket()
        while time.time()-time0<self.acq_time:
            try:
               x=self.reader.fast_acquisition(data_list)# self.reader.fast_acquisition(data_list)
            except:
                print ("\n---TIMED_OUT!!!...\n")
                self.reader.dataSock.close()
                return 0
        self.reader.dataSock.close()
        self.reader.data_list=list(data_list)
        print len(self.reader.data_list)

        # with open(self.reader.log_path, 'a') as log_file:
        #     log_file.write("{} -- Closing acquisition on GEMROC {}\n".format(time.ctime(),self.reader.GEMROC_ID))
        with open(datapath, 'wb') as datafile:
            try: # add a method to write the list on the file
                self.reader.dump_list(datafile,data_list)
            except:
                print ("\n----SOMETHING WRONG---FILE MISSING\n")
                return 0
        self.reader.datapath=datapath

# class Thread_handler(Thread):  # In order to scan during configuration is mandatory to use multithreading
#     def __init__(self, name, acq_time, reader):
#         Thread.__init__(self)
#         self.name = name
#         self.acq_time = acq_time
#         self.reader = reader
#
#     def run(self):
#
#         datapath = "." + sep + "data_folder" + sep + "Spill_{}_GEMROC_{}.dat".format(
#             datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"), self.reader.GEMROC_ID)
#         self.first_framew=np.zeros(8)
#         self.last_framew = np.zeros(8)
#         with open(datapath, 'wb') as datafile:
#
#             # with open(self.reader.log_path, 'a') as log_file:
#             #     log_file.write("{} --Launching acquisition on GEMROC {} for {} seconds\n".format(time.ctime(),self.reader.GEMROC_ID,self.acq_time))
#
#             time0 = time.time()
#             data_list = []
#             self.reader.start_socket()
#             while time.time() - time0 < self.acq_time:
#                 self.reader.acquisition(datafile)  # self.reader.fast_acquisition(data_list)
#
#             self.reader.dataSock.close()


class reader:
    def __init__(self, GEMROC_ID):
        self.GEMROC_ID = GEMROC_ID
        # self.log_path = "Acq_log_{}.txt".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        self.HOST_IP = "192.168.1.200"
        self.HOST_PORT = 58880+self.GEMROC_ID  # 58880 + 1 # original +2

        self.thr_scan_matrix = np.zeros((8, 64))  # Tiger,Channel
        self.thr_scan_frames = np.ones(8)
        self.thr_scan_rate = np.zeros((8, 64))
        self.BUFSIZE = 32000
        self.first_framew=np.zeros(8)
        self.last_framew=np.zeros(8)
        self.datapath = ""
        self.datalist = []
    def start_socket(self):
        self.dataSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dataSock.settimeout(0.1)
        self.dataSock.bind((self.HOST_IP, self.HOST_PORT))
        # self.dataSock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8388608 )
        # print self.dataSock.getsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF)

    def __del__(self):

        return 0
    def build_hist_and_miss(self,frameword_check=True):
        self.thr_scan_matrix = np.zeros((8, 64))  # Tiger,Channel
        self.thr_scan_frames = np.ones(8)
        self.thr_scan_rate = np.zeros((8, 64))
        for datastring in enumerate(self.data_list):
            data = datastring
            hexdata = binascii.hexlify(data[1])

            for x in range(0, len(hexdata) - 1, 16):
                int_x = 0
                for b in range(7, 0, -1):
                    hex_to_int = (int(hexdata[x + b * 2], 16)) * 16 + int(hexdata[x + b * 2 + 1], 16)
                    int_x = (int_x + hex_to_int) << 8

                hex_to_int = (int(hexdata[x], 16)) * 16 + int(hexdata[x + 1], 16)
                int_x = (int_x + hex_to_int)

                if (((int_x & 0xFF00000000000000) >> 59) == 0x04):  # It's a framword

                    self.thr_scan_frames[(int_x >> 56) & 0x7] = self.thr_scan_frames[(int_x >> 56) & 0x7] + 1

                    this_framecount = ((int_x >> 15) & 0xFFFF)
                    this_tiger = ((int_x >> 56) & 0x7)

                    if frameword_check:
                        if self.first_framew[this_tiger] == 0:
                            self.last_framew[this_tiger] = this_framecount
                            self.first_framew[this_tiger] = 1
                        else:
                            if this_framecount == 0xffff:
                                self.first_framew[this_tiger] = 0
                            else:
                                for F in range(int(self.last_framew[this_tiger]), int(this_framecount)):
                                    if self.last_framew[this_tiger] + 1 == this_framecount:
                                        self.last_framew[this_tiger] = this_framecount
                                        break
                                    else:
                                        print ("Frameword {} from Tiger {} missing".format(hex(F + 1), this_tiger))
                                        #fmiss.write("Frameword {} from Tiger {} missing\n".format(hex(F + 1), this_tiger))
                                        self.last_framew[this_tiger] = self.last_framew[this_tiger] + 1

                if (((int_x & 0xFF00000000000000) >> 59) == 0x00):
                    self.thr_scan_matrix[(int_x >> 56) & 0x7, int(int_x >> 48) & 0x3F] = self.thr_scan_matrix[
                                                                                             (int_x >> 56) & 0x7, int(
                                                                                                 int_x >> 48) & 0x3F] + 1
    def acquisition(self, savefile,frameword_check=True):
        data, addr = self.dataSock.recvfrom(self.BUFSIZE)
        savefile.write(data)  # Again, could be a similar problem? GM

        hexdata = binascii.hexlify(data)

        for x in range(0, len(hexdata) - 1, 16):
            int_x = 0
            for b in range(7, 0, -1):
                hex_to_int = (int(hexdata[x + b * 2], 16)) * 16 + int(hexdata[x + b * 2 + 1], 16)
                int_x = (int_x + hex_to_int) << 8
            hex_to_int = (int(hexdata[x], 16)) * 16 + int(hexdata[x + 1], 16)  # acr 2017-11-17 this should fix the problem
            int_x = (int_x + hex_to_int)
            # raw = '%016X ' % int_x

            if (((int_x & 0xFF00000000000000) >> 59) == 0x04):
                # s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'HB: ' + 'Framecount: %08X ' % (
                #         (int_x >> 15) & 0xFFFF) + 'SEUcount: %08X\n' % (int_x & 0x7FFF)
                self.thr_scan_frames[(int_x >> 56) & 0x7] = self.thr_scan_frames[(int_x >> 56) & 0x7] + 1

            # if (((int_x & 0xFF00000000000000) >> 59) == 0x08):
            # s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'CW: ' + 'ChID: %02X ' % (
            #         (int_x >> 24) & 0x3F) + ' CounterWord: %016X\n' % (int_x & 0x00FFFFFF)
            if (((int_x & 0xFF00000000000000) >> 59) == 0x00):
                # s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'EW: ' + 'ChID: %02X ' % (
                #         (int_x >> 48) & 0x3F) + 'tacID: %01X ' % ((int_x >> 46) & 0x3) + 'Tcoarse: %04X ' % (
                #             (int_x >> 30) & 0xFFFF) + 'Ecoarse: %03X ' % (
                #             (int_x >> 20) & 0x3FF) + 'Tfine: %03X ' % ((int_x >> 10) & 0x3FF) + 'Efine: %03X \n' % (
                #             int_x & 0x3FF)
                self.thr_scan_matrix[(int_x >> 56) & 0x7, int(int_x >> 48) & 0x3F] = self.thr_scan_matrix[
                                                                                         (int_x >> 56) & 0x7, int(
                                                                                             int_x >> 48) & 0x3F] + 1
    
            if (((int_x & 0xFF00000000000000) >> 59) == 0x04):  # Framewoird_integrity_check
    
                self.thr_scan_frames[(int_x >> 56) & 0x7] = self.thr_scan_frames[(int_x >> 56) & 0x7] + 1
    
                this_framecount = ((int_x >> 15) & 0xFFFF)
                this_tiger = ((int_x >> 56) & 0x7)
    
                if frameword_check:
                    if self.first_framew[this_tiger] == 0:
                        self.last_framew[this_tiger] = this_framecount
                        self.first_framew[this_tiger] = 1
                    else:
                        if this_framecount == 0xffff:
                            self.first_framew[this_tiger] = 0
                        else:
                            for F in range(int(self.last_framew[this_tiger]), int(this_framecount)):
                                if self.last_framew[this_tiger] + 1 == this_framecount:
                                    self.last_framew[this_tiger] = this_framecount
                                    break
                                else:
                                    print ("Frameword {} from Tiger {} missing".format(hex(F + 1), this_tiger))
                                    self.last_framew[this_tiger] = self.last_framew[this_tiger] + 1

        return 0

    def fast_acquisition(self, data_list_tmp):  # remove savefile to be added in a new class GM 11.06.18
        data, addr = self.dataSock.recvfrom(self.BUFSIZE)
        # savefile.write(data) # here the file is written - maybe to slow? APPEND? GM
        data_list_tmp.append(data)  # here append the data to the list, stored waiting to be dumped.
        return len(data)

    def dump_list(self, savefile, data_list_tmp):
        for item in data_list_tmp:
            savefile.write('%s' % item)

    def read_bin(self, path):
        self.thr_scan_matrix = np.zeros((8, 64))  # Tiger,Channel
        self.thr_scan_frames = np.ones(8)
        self.thr_scan_rate = np.zeros((8, 64))
        statinfo = os.stat(path)
        print statinfo.st_size
        with open(path, 'r') as f:
            for i in range(0, statinfo.st_size / 8):

                # while True:
                #     data=f.read(8)
                #     if not data or len(data)<8:
                #         # end of file
                #         print"End of file\n"
                #         break
                #     hexdata = binascii.hexlify(data)

                data = f.read(8)
                hexdata = binascii.hexlify(data)

                for x in range(0, len(hexdata) - 1, 16):
                    int_x = 0
                    for b in range(7, 0, -1):
                        hex_to_int = (int(hexdata[x + b * 2], 16)) * 16 + int(hexdata[x + b * 2 + 1], 16)
                        int_x = (int_x + hex_to_int) << 8

                    raw = '%016X ' % int_x

                    hex_to_int = (int(hexdata[x], 16)) * 16 + int(hexdata[x + 1],
                                                                  16)  # acr 2017-11-17 this should fix the problem
                    int_x = (int_x + hex_to_int)
                    if (((int_x & 0xFF00000000000000) >> 59) == 0x04):
                        # s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'HB: ' + 'Framecount: %08X ' % (
                        #         (int_x >> 15) & 0xFFFF) + 'SEUcount: %08X\n' % (int_x & 0x7FFF)
                        self.thr_scan_frames[(int_x >> 56) & 0x7] = self.thr_scan_frames[(int_x >> 56) & 0x7] + 1

                    # if (((int_x & 0xFF00000000000000) >> 59) == 0x08):
                    # s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'CW: ' + 'ChID: %02X ' % (
                    #         (int_x >> 24) & 0x3F) + ' CounterWord: %016X\n' % (int_x & 0x00FFFFFF)
                    if (((int_x & 0xFF00000000000000) >> 59) == 0x00):
                        # s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'EW: ' + 'ChID: %02X ' % (
                        #         (int_x >> 48) & 0x3F) + 'tacID: %01X ' % ((int_x >> 46) & 0x3) + 'Tcoarse: %04X ' % (
                        #             (int_x >> 30) & 0xFFFF) + 'Ecoarse: %03X ' % (
                        #             (int_x >> 20) & 0x3FF) + 'Tfine: %03X ' % ((int_x >> 10) & 0x3FF) + 'Efine: %03X \n' % (
                        #             int_x & 0x3FF)
                        self.thr_scan_matrix[(int_x >> 56) & 0x7, int(int_x >> 48) & 0x3F] = self.thr_scan_matrix[(
                                                                                                                              int_x >> 56) & 0x7, int(
                            int_x >> 48) & 0x3F] + 1

                    # with open ("out.txt", 'a') as ff:
                    # ff.write("{}\n".format(raw))

                hexdata = binascii.hexlify(data)
                for x in range(0, len(hexdata) - 1, 16):
                    int_x = 0
                    for b in range(7, 0, -1):
                        hex_to_int = (int(hexdata[x + b * 2], 16)) * 16 + int(hexdata[x + b * 2 + 1], 16)
                        int_x = (int_x + hex_to_int) << 8
                    hex_to_int = (int(hexdata[x], 16)) * 16 + int(hexdata[x + 1], 16)
                    int_x = (int_x + hex_to_int)
                    raw = '%016X ' % int_x

                    if (((int_x & 0xFF00000000000000) >> 59) == 0x04):
                        self.thr_scan_frames[(int_x >> 56) & 0x7] = self.thr_scan_frames[(int_x >> 56) & 0x7] + 1

                    if (((int_x & 0xFF00000000000000) >> 59) == 0x08):
                        a = 0

                    if (((int_x & 0xFF00000000000000) >> 59) == 0x00):
                        self.thr_scan_matrix[(int_x >> 56) & 0x7, int(int_x >> 48) & 0x3F] = self.thr_scan_matrix[(
                                                                                                                              int_x >> 56) & 0x7, int(
                            int_x >> 48) & 0x3F] + 1

                    with open("out.txt", 'a') as ff:
                        ff.write("{}\n".format(raw))

    def create_rate_plot(self):
        plt.ion()
        for i in range(0, 8):
            self.thr_scan_rate[i, :] = (self.thr_scan_matrix[i, :] / self.thr_scan_frames[i]) * (1 / 0.0002048)
        thr_scan_copy = self.thr_scan_rate
        fig = plt.figure(figsize=(8, 8))
        gs = gridspec.GridSpec(nrows=3, ncols=3)  # , height_ratios=[1, 1, 2])

        ax0 = fig.add_subplot(gs[0, 0])
        ax0.bar(np.arange(0, 64), thr_scan_copy[0, :])
        ax0.set_title('GEMROC {}, TIGER {}'.format(self.GEMROC_ID, 0))
        ax0.set_xlabel('Channel')
        ax0.set_ylabel('Rate [Hz]')

        ax1 = fig.add_subplot(gs[0, 1])
        ax1.bar(np.arange(0, 64), thr_scan_copy[1, :])
        ax1.set_title('GEMROC {}, TIGER {}'.format(self.GEMROC_ID, 1))
        ax1.set_xlabel('Channel')
        ax1.set_ylabel('Rate [Hz]')

        ax2 = fig.add_subplot(gs[1, 0])
        ax2.bar(np.arange(0, 64), thr_scan_copy[2, :])
        ax2.set_title('GEMROC {}, TIGER {}'.format(self.GEMROC_ID, 2))
        ax2.set_xlabel('Channel')
        ax2.set_ylabel('Rate [Hz]')

        ax3 = fig.add_subplot(gs[1, 1])
        ax3.bar(np.arange(0, 64), thr_scan_copy[3, :])
        ax3.set_title('GEMROC {}, TIGER {}'.format(self.GEMROC_ID, 3))
        ax3.set_xlabel('Channel')
        ax3.set_ylabel('Rate [Hz]')

        ax4 = fig.add_subplot(gs[2, 0])
        ax4.bar(np.arange(0, 64), thr_scan_copy[4, :])
        ax4.set_title('GEMROC {}, TIGER {}'.format(self.GEMROC_ID, 4))
        ax4.set_xlabel('Channel')
        ax4.set_ylabel('Rate [Hz]')

        ax5 = fig.add_subplot(gs[2, 1])
        ax5.bar(np.arange(0, 64), thr_scan_copy[5, :])
        ax5.set_title('GEMROC {}, TIGER {}'.format(self.GEMROC_ID, 5))
        ax5.set_xlabel('Channel')
        ax5.set_ylabel('Rate [Hz]')

        ax6 = fig.add_subplot(gs[0, 2])
        ax6.bar(np.arange(0, 64), thr_scan_copy[6, :])
        ax6.set_title('GEMROC {}, TIGER {}'.format(self.GEMROC_ID, 6))
        ax6.set_xlabel('Channel')
        ax6.set_ylabel('Rate [Hz]')

        ax7 = fig.add_subplot(gs[1, 2])
        ax7.bar(np.arange(0, 64), thr_scan_copy[7, :])
        ax7.set_title('GEMROC {}, TIGER {}'.format(self.GEMROC_ID, 7))
        ax7.set_xlabel('Channel')
        ax7.set_ylabel('Rate [Hz]')

        # plt.tight_layout()
        # fig.canvas.draw()

        axarray = [ax0, ax1, ax2, ax3, ax4, ax5,ax6,ax7]
        return fig, axarray

    def refresh_rate_plot(self, fig, axarray):
        for i in range(0, 8):
            self.thr_scan_rate[i, :] = (self.thr_scan_matrix[i, :] / self.thr_scan_frames[i]) * (1 / 0.0002048)
            thr_scan_copy = self.thr_scan_rate
        for i in range(0, 8):
            axarray[i].bar(np.arange(0, 64), thr_scan_copy[i, :])
