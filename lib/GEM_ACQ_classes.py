import binascii
import os
import socket
import sys
import time
from threading import Thread

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np

OS = sys.platform
if OS == 'win32':
    sep = '\\'
elif OS == 'linux2' or 'linux':
    sep = '/'
else:
    print("ERROR: OS {} non compatible".format(OS))
    sys.exit()
local_test = False


class Thread_handler(Thread):
    def __init__(self, name, acq_time, reader,sub_folder=".",sub_run_number=0):
        Thread.__init__(self)
        self.name = name
        self.acq_time = acq_time
        self.reader = reader
        self.running = True
        self.sub_folder=sub_folder
        self.isTM = False
        self.sub_run_number=sub_run_number
    def run(self):
        Total_data_MAX_size = 2 ** 11
        datapath = "." + sep + "data_folder" + sep+self.sub_folder+sep + "SubRUN_{}_GEMROC_{}_TL.dat".format(self.sub_run_number, self.reader.GEMROC_ID)
        # with open(self.reader.log_path, 'a') as log_file:
        #     log_file.write("{} --Launching acquisition on GEMROC {} for {} seconds\n".format(time.ctime(),self.reader.GEMROC_ID,self.acq_time))

        time0 = time.time()
        data_list = []
        self.TIMED_out = False
        with open(datapath, 'wb'):
            pass
        print ("Acquiring GEMROC {} for {} seconds".format(self.reader.GEMROC_ID, self.acq_time))
        self.reader.start_socket()
        while time.time() - time0 < self.acq_time and self.running:
            Total_Data = 0

            while (Total_Data < Total_data_MAX_size) and time.time() - time0 < self.acq_time and self.running:
                try:
                    x = self.reader.fast_acquisition(data_list)  # self.reader.fast_acquisition(data_list)
                    Total_Data += x
                except Exception as e:
                    print( e)
                    print ("\n---TIMED_OUT!!!...\n")
                    self.reader.dataSock.close()
                    self.running = False
                    self.reader.TIMED_out = True
                    Exception ("GEMROC {} TIMED_OUT".format(self.reader.GEMROC_ID))

                    return 0
            self.reader.data_list = list(data_list)
            with open(datapath, 'ab') as datafile:
                try:  # add a method to write the list on the file
                    self.reader.dump_list(datafile, data_list)
                    data_list = []
                except:
                    print ("\n----SOMETHING WRONG---FILE MISSING\n")
                    return 0

        self.reader.dataSock.close()
        self.reader.data_list = list(data_list)
        print (len(self.reader.data_list))

        # with open(self.reader.log_path, 'a') as log_file:
        #     log_file.write("{} -- Closing acquisition on GEMROC {}\n".format(time.ctime(),self.reader.GEMROC_ID))
        with open(datapath, 'ab') as datafile:
            try:  # add a method to write the list on the file
                self.reader.dump_list(datafile, data_list)
                data_list=[]

            except:
                print ("\n----SOMETHING WRONG---FILE MISSING\n")
                return 0
        self.reader.datapath = datapath
        print ("Done acquiring")


class Thread_handler_TM(Thread):  # In order to scan during configuration is mandatory to use multithreading
    def __init__(self, name, reader,sub_folder=".",sub_run_number=0):
        Thread.__init__(self)
        self.name = name
        self.reader = reader
        self.running = True
        self.isTM = True
        self.sub_folder = sub_folder
        self.sub_run_number = sub_run_number


    def run(self):
        Totallissimi_packets=0
        Total_data_MAX_size = 2 ** 20
        Total_MAX_packets=20
        datapath = "." + sep + "data_folder" + sep+self.sub_folder+sep + "SubRUN_{}_GEMROC_{}_TM.dat".format(self.sub_run_number, self.reader.GEMROC_ID)
        with open(self.reader.log_path, 'a') as f:
            f.write("{} -- Saving data from  GEMROC {} in file {}\n".format(time.ctime(), self.reader.GEMROC_ID,datapath))
        # with open(self.reader.log_path, 'a') as log_file:
        #     log_file.write("{} --Launching acquisition on GEMROC {} for {} seconds\n".format(time.ctime(),self.reader.GEMROC_ID,self.acq_time))
        self.reader.datapath = datapath
        with open(datapath, 'wb'):
            pass
        data_list = []
        self.reader.start_socket()
        if self.reader.data_online_monitor:
            self.reader.send_start_packet(self.sub_folder, self.sub_run_number, datapath)
        while True:
            Total_Data = 0
            Total_packets =0
            while (Total_Data < Total_data_MAX_size) and (Total_packets<Total_MAX_packets) and self.running:
                try:
                    x = self.reader.fast_acquisition(data_list)  # self.reader.fast_acquisition(data_list)
                    Total_Data += x
                    Total_packets += 1
                    Totallissimi_packets += 1
                    #print ("Packet from GEMROC {}".format(self.reader.GEMROC_ID))
                except Exception as e:
                    print (e)
                    with open(self.reader.log_path, 'a') as f:
                        f.write("{} -- GEMROC {} TIMED_OUT\n".format(time.ctime(), self.reader.GEMROC_ID))

                    print ("\n---GEMROC {} - {}\n".format(self.reader.GEMROC_ID, e))
                    self.reader.TIMED_out = True
                    Exception("GEMROC {} TIMED_OUT".format(self.reader.GEMROC_ID))
                    with open(self.reader.log_path, 'a') as f:
                        f.write("{} -- Finished saving data from  GEMROC {} in file {}, total packets= {}\n".format(time.ctime(), self.reader.GEMROC_ID, self.reader.datapath, Totallissimi_packets))
                    print ("Finished saving data from  GEMROC {} in file {}, total packets= {}\n".format(self.reader.GEMROC_ID, self.reader.datapath, Totallissimi_packets))
                    self.reader.dataSock.close()

                    if self.reader.data_online_monitor:
                        self.reader.send_end_packet(self.sub_folder, self.sub_run_number, datapath)
                        self.reader.cloning_sock.close()

                    self.running=False
                    return 0
            self.reader.data_list = list(data_list)

            # with open(self.reader.log_path, 'a') as log_file:
            #     log_file.write("{} -- Closing acquisition on GEMROC {}\n".format(time.ctime(),self.reader.GEMROC_ID))
            with open(datapath, 'ab') as datafile:
                # print "Saving data on file"
                self.reader.dump_list(datafile, data_list)
                data_list=[]
            if self.running==False:
                break
        with open(datapath, 'ab') as datafile:
            # print "Saving data on file"
            try:  # add a method to write the list on the file
                self.reader.dump_list(datafile, data_list)
                data_list = []
            except:
                self.reader.datapath = datapath
                return 0
        self.reader.dataSock.close()
        self.reader.datapath = datapath
        with open(self.reader.log_path, 'a') as f:
            f.write("{} -- Finished saving data from  GEMROC {} in file {}, total packets= {}\n".format(time.ctime(), self.reader.GEMROC_ID, self.reader.datapath,Totallissimi_packets ))
        print ("Finished saving data from  GEMROC {} in file {}, total packets= {}\n".format( self.reader.GEMROC_ID, self.reader.datapath,Totallissimi_packets ))
        if self.reader.data_online_monitor:
            self.reader.send_end_packet(self.sub_folder, self.sub_run_number, datapath)
            self.reader.cloning_sock.close()



class reader:
    def __init__(self, GEMROC_ID,logfile="ACQ_log",online_monitor=False):
        local_reader= True
        self.local_test=local_test

        self.GEMROC_ID = GEMROC_ID
        # self.log_path = "Acq_log_{}.txt".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        self.HOST_IP = "192.168.1.200"
        self.HOST_PORT = 58880 + self.GEMROC_ID  # 58880 + 1 # original +2
        if self.local_test:
            self.HOST_IP = "127.0.0.1"
            self.HOST_PORT = 20000 + self.GEMROC_ID# 58880 + 1 # original +2
        self.TIMED_out=False

        self.thr_scan_matrix = np.zeros((8, 64))  # Tiger,Channel
        self.thr_scan_frames = np.ones(8)
        self.thr_scan_rate = np.zeros((8, 64))
        self.BUFSIZE = 32000
        self.first_framew = np.zeros(8)
        self.last_framew = np.zeros(8)
        self.datalist = []
        self.log_path=logfile
        self.data_online_monitor = online_monitor
        self.timeout_for_sockets = 25
        if self.data_online_monitor:
            if local_reader:
                self.port_for_cloning = 58880 + self.GEMROC_ID
                # self.port_for_cloning =58912 + 1 + self.GEMROC_ID
                self.cloning_sending_port=51000 + self.GEMROC_ID
                self.address_for_cloning_sender="127.0.0.1"
                self.address_for_cloning_rcv="127.0.0.1"
            else:
                self.port_for_cloning = 58880 + self.GEMROC_ID
                self.cloning_sending_port=51000+ self.GEMROC_ID
                self.address_for_cloning_sender="192.168.1.200"
                self.address_for_cloning_rcv="192.168.1.150" #just an example, change it accordingly
            self.create_cloning_socket()

    def create_cloning_socket(self):
        self.cloning_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.cloning_sock.bind((self.address_for_cloning_sender, self.cloning_sending_port))

    def start_socket(self):
        self.TIMED_out=False

        try:
            self.dataSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.dataSock.settimeout(self.timeout_for_sockets)
            self.dataSock.bind((self.HOST_IP, self.HOST_PORT))
            # self.dataSock.setblocking(False)
        except Exception as e:

            print ("--GEMROC {}-{}".format(self.GEMROC_ID,e))
            Exception("TIMED_OUT")
            with open(self.log_path, 'a') as f:
                f.write("{} -- GEMROC {} TIMED_OUT\n".format(time.ctime(), self.GEMROC_ID))
            self.TIMED_out=True
            print ("Can't bind the socket")

        # self.dataSock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8388608 )
        # print self.dataSock.getsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF)

    def __del__(self):
        return 0

    def acquire_rate(self, max_time):
        acq_matrix = np.zeros((8,64))
        self.beginning_time = time.time()
        self.start_socket()
        while time.time()-self.beginning_time<max_time:
            data_pack, addr = self.dataSock.recvfrom(self.BUFSIZE)
            data_pack = bytearray(data_pack)
            for slices in range(0,len(data_pack)/8):
                data=data_pack[slices*8:slices*8+8]
                # print "LEN {}".format(len(data))
                reversed_data = (list(reversed(data)))  # Swaps the byte order
                this_word={}


                if (reversed_data[0] >> 5) == 0:  # It's a hit
                    this_word = {
                        "word_type": "hit",
                        "TIGER": (reversed_data[0]) & 0x7,
                        "Channel": (reversed_data[1]) & 0x3F,

                        # "TAC": (reversed_data[1]) & 0x3,
                        # "T_coarse": (reversed_data[2] << 8 | reversed_data[3] | reversed_data[4] >> 8) & 0xFFFF,
                        # "E_coarse": (reversed_data[4] << 4 | reversed_data[5] >> 4) & 0x3FF,
                        # "T_fine": (reversed_data[5] << 6 | reversed_data[   6] >> 2) & 0x3FF,
                        # "E_fine": (reversed_data[6] << 8 | reversed_data[7]) & 0x3FF

                    }
                # hexdata = binascii.hexlify(data)
                # string= "{:064b}".format(int(hexdata,16))
                # inverted=[]
                # for i in range (8,0,-1):
                #     inverted.append(string[(i-1)*8:i*8])
                # string_inv="".join(inverted)
                # int_x = int(string_inv,2)
                # raw = "{:064b}  ".format(int_x)
                # print raw
                #
                # if (((int_x & 0xFF00000000000000) >> 59) == 0x00):  # It's a hit
                #     this_word = {
                #         "word_type": "hit",
                #         "TIGER": ((int_x >> 56) & 0x7),
                #         "Channel": ((int_x >> 48) & 0x3F)
                #         # "TAC": (reversed_data[1]) & 0x3,
                #         # "T_coarse": (reversed_data[2] << 8 | reversed_data[3] | reversed_data[4] >> 8) & 0xFFFF,
                #         # "E_coarse": (reversed_data[4] << 4 | reversed_data[5] >> 4) & 0x3FF,
                #         # "T_fine": (reversed_data[5] << 6 | reversed_data[   6] >> 2) & 0x3FF,
                #         # "E_fine": (reversed_data[6] << 8 | reversed_data[7]) & 0x3FF
                #
                #     }
                    acq_matrix[this_word["TIGER"]][this_word["Channel"]]+=1
        self.dataSock.close()
        return acq_matrix

    def build_hist_and_miss(self, frameword_check=True):
        self.thr_scan_matrix = np.zeros((8, 64))  # Tiger,Channel
        self.thr_scan_frames = np.ones(8)
        self.thr_scan_rate = np.zeros((8, 64))
        if len(self.datalist) != 0:
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
                                            # fmiss.write("Frameword {} from Tiger {} missing\n".format(hex(F + 1), this_tiger))
                                            self.last_framew[this_tiger] = self.last_framew[this_tiger] + 1

                    if (((int_x & 0xFF00000000000000) >> 59) == 0x00):
                        self.thr_scan_matrix[(int_x >> 56) & 0x7, int(int_x >> 48) & 0x3F] = self.thr_scan_matrix[
                                                                                                 (int_x >> 56) & 0x7, int(
                                                                                                     int_x >> 48) & 0x3F] + 1

    # def acquisition(self, savefile, frameword_check=True):
    #     data, addr = self.dataSock.recvfrom(self.BUFSIZE)
    #     savefile.write(data)  # Again, could be a similar problem? GM
    #
    #     hexdata = binascii.hexlify(data)
    #
    #     for x in range(0, len(hexdata) - 1, 16):
    #         int_x = 0
    #         for b in range(7, 0, -1):
    #             hex_to_int = (int(hexdata[x + b * 2], 16)) * 16 + int(hexdata[x + b * 2 + 1], 16)
    #             int_x = (int_x + hex_to_int) << 8
    #         hex_to_int = (int(hexdata[x], 16)) * 16 + int(hexdata[x + 1], 16)  # acr 2017-11-17 this should fix the problem
    #         int_x = (int_x + hex_to_int)
    #         # raw = '%016X ' % int_x
    #
    #         if (((int_x & 0xFF00000000000000) >> 59) == 0x04):
    #             # s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'HB: ' + 'Framecount: %08X ' % (
    #             #         (int_x >> 15) & 0xFFFF) + 'SEUcount: %08X\n' % (int_x & 0x7FFF)
    #             self.thr_scan_frames[(int_x >> 56) & 0x7] = self.thr_scan_frames[(int_x >> 56) & 0x7] + 1
    #
    #         # if (((int_x & 0xFF00000000000000) >> 59) == 0x08):
    #         # s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'CW: ' + 'ChID: %02X ' % (
    #         #         (int_x >> 24) & 0x3F) + ' CounterWord: %016X\n' % (int_x & 0x00FFFFFF)
    #         if (((int_x & 0xFF00000000000000) >> 59) == 0x00):
    #             # s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'EW: ' + 'ChID: %02X ' % (
    #             #         (int_x >> 48) & 0x3F) + 'tacID: %01X ' % ((int_x >> 46) & 0x3) + 'Tcoarse: %04X ' % (
    #             #             (int_x >> 30) & 0xFFFF) + 'Ecoarse: %03X ' % (
    #             #             (int_x >> 20) & 0x3FF) + 'Tfine: %03X ' % ((int_x >> 10) & 0x3FF) + 'Efine: %03X \n' % (
    #             #             int_x & 0x3FF)
    #             self.thr_scan_matrix[(int_x >> 56) & 0x7, int(int_x >> 48) & 0x3F] = self.thr_scan_matrix[
    #                                                                                      (int_x >> 56) & 0x7, int(
    #                                                                                          int_x >> 48) & 0x3F] + 1
    #
    #         if (((int_x & 0xFF00000000000000) >> 59) == 0x04):  # Framewoird_integrity_check
    #
    #             self.thr_scan_frames[(int_x >> 56) & 0x7] = self.thr_scan_frames[(int_x >> 56) & 0x7] + 1
    #
    #             this_framecount = ((int_x >> 15) & 0xFFFF)
    #             this_tiger = ((int_x >> 56) & 0x7)
    #
    #             if frameword_check:
    #                 if self.first_framew[this_tiger] == 0:
    #                     self.last_framew[this_tiger] = this_framecount
    #                     self.first_framew[this_tiger] = 1
    #                 else:
    #                     if this_framecount == 0xffff:
    #                         self.first_framew[this_tiger] = 0
    #                     else:
    #                         for F in range(int(self.last_framew[this_tiger]), int(this_framecount)):
    #                             if self.last_framew[this_tiger] + 1 == this_framecount:
    #                                 self.last_framew[this_tiger] = this_framecount
    #                                 break
    #                             else:
    #                                 print ("Frameword {} from Tiger {} missing".format(hex(F + 1), this_tiger))
    #                                 self.last_framew[this_tiger] = self.last_framew[this_tiger] + 1
    #
    #     return 0

    def fast_acquisition(self, data_list_tmp):  # remove savefile to be added in a new class GM 11.06.18
        if self.local_test:
            with open("./data_folder/SubRUN_5_GEMROC_0_TM.dat", 'rb') as fi:
                data = fi.read()

            for i in range (0,len(data)//8):
                self.cloning_sock.sendto(data[i*8:i*8+8], (self.address_for_cloning_rcv, self.port_for_cloning))
                time.sleep(0.05)
        else:
            data = self.dataSock.recv(self.BUFSIZE)
            if self.data_online_monitor:
                self.cloning_sock.sendto(data,(self.address_for_cloning_rcv, self.port_for_cloning))
            # savefile.write(data) # here the file is written - maybe to slow? APPEND? GM
            data_list_tmp.append(data)  # here append the data to the list, stored waiting to be dumped.
        return len(data)

    def dump_list(self, savefile, data_list_tmp):
        for item in data_list_tmp:
            savefile.write(item)
        # with open(self.log_path, 'ab') as f:
        #     f.write("{} -- Dumping Data for GEMROC {} in file {}\n".format(time.ctime(), self.GEMROC_ID,savefile))

    def read_bin(self, path):
        self.thr_scan_matrix = np.zeros((8, 64))  # Tiger,Channel
        self.thr_scan_frames = np.ones(8)
        self.thr_scan_rate = np.zeros((8, 64))
        statinfo = os.stat(path)
        print (statinfo.st_size)
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

        axarray = [ax0, ax1, ax2, ax3, ax4, ax5, ax6, ax7]
        return fig, axarray

    def refresh_rate_plot(self, fig, axarray):
        for i in range(0, 8):
            self.thr_scan_rate[i, :] = (self.thr_scan_matrix[i, :] / self.thr_scan_frames[i]) * (1 / 0.0002048)
            thr_scan_copy = self.thr_scan_rate
        for i in range(0, 8):
            axarray[i].bar(np.arange(0, 64), thr_scan_copy[i, :])

    def check_TM_continuity(self, path):
        print ("OPEN {}".format(path))
        LOCAL_L1_COUNT_31_6 = 0
        LOCAL_L1_COUNT_5_0 = 0
        LOCAL_L1_COUNT = 0
        LOCAL_L1_TIMESTAMP = 0
        previous_L1_TS = 0
        L1_TS_abs_diff = 0
        self.thr_scan_matrix = np.zeros((8, 64))  # Tiger,Channel
        self.thr_scan_frames = np.ones(8)
        self.thr_scan_rate = np.zeros((8, 64))
        statinfo = os.stat(path)
        last_counter = 0
        first_counter = 0
        TIGER_not_missing = np.zeros((8))
        packet_missing = []
        print ("size={}\n".format(statinfo.st_size))
        with open(path, 'rb') as f:
            for i in range(0, int(statinfo.st_size / 8)):
                data = f.read(8)
                hexdata = binascii.hexlify(data)
                string = "{:064b}".format(int(hexdata, 16))
                inverted = []
                for i in range(8, 0, -1):
                    inverted.append(string[(i - 1) * 8:i * 8])
                string_inv = "".join(inverted)
                int_x = int(string_inv, 2)
                s = '%016X \n' % int_x
                # acr 2018-06-25 out_file.write(s)

                ## comment this block to avoid parsing
                ##acr 2017-11-16        if (((int_x & 0xFF00000000000000)>>56) == 0x20):
                if (((int_x & 0xE000000000000000) >> 61) == 0x6):
                    LOCAL_L1_COUNT_31_6 = int_x >> 32 & 0x3FFFFFF
                    LOCAL_L1_COUNT_5_0 = int_x >> 24 & 0x3F
                    LOCAL_L1_COUNT = (LOCAL_L1_COUNT_31_6 << 6) + LOCAL_L1_COUNT_5_0
                    if first_counter == 0:
                        last_counter = LOCAL_L1_COUNT
                        first_counter = 1
                    else:
                        if LOCAL_L1_COUNT == 0xffff:
                            first_counter = 0
                        else:
                            for F in range(int(last_counter), int(LOCAL_L1_COUNT)):
                                if last_counter + 1 == LOCAL_L1_COUNT:
                                    last_counter = LOCAL_L1_COUNT
                                    break
                                else:
                                    packet_missing.append(hex(F + 1))
                                    print ("Missing packet number {}, GEMROC {}".format(hex(F + 1),self.GEMROC_ID))
                                    last_counter = last_counter + 1

                    LOCAL_L1_TIMESTAMP = int_x & 0xFFFF
                    HITCOUNT = (int_x >> 16) & 0xFF
                    if (((int_x & 0xFFFF) - previous_L1_TS) > 0):
                        L1_TS_abs_diff = ((int_x & 0xFFFF) - previous_L1_TS)
                    else:
                        # THIS PRODUCES WRONG RESULTS (INCONSISTENT PERIOD) FOR PERIODS L1_TS_abs_diff = 65536 +((int_x & 0xFFFF) - previous_L1_TS)
                        # THIS ALSO PRODUCES WRONG RESULTS (INCONSISTENT PERIOD) FOR PERIODS L1_TS_abs_diff = 32768 - ((int_x & 0xFFFF) - previous_L1_TS)
                        L1_TS_abs_diff = 65536 + ((int_x & 0xFFFF) - previous_L1_TS)
                    s = 'HEADER :  ' + 'STATUS BIT[2:0]: %01X: ' % ((int_x >> 58) & 0x7) + 'LOCAL L1 COUNT: %08X ' % (LOCAL_L1_COUNT) + 'HitCount: %02X ' % ((int_x >> 16) & 0xFF) + 'LOCAL L1 TIMESTAMP: %04X; ' % (int_x & 0xFFFF) + 'Diff w.r.t. previous L1_TS: %04f us\n' % (
                                L1_TS_abs_diff * 6 / 1000)
                    previous_L1_TS = (int_x & 0xFFFF)
                    # s = 'HEADER :  ' + 'STATUS BIT[2:0]: %01X: '%((int_x >> 58)& 0x7) + 'LOCAL L1 COUNT: %08X '%( LOCAL_L1_COUNT ) + 'HitCount: %02X '%((int_x >> 16) & 0xFF) + 'LOCAL L1 TIMESTAMP: %04X\n'%(int_x & 0xFFFF)
                if (((int_x & 0xE000000000000000) >> 61) == 0x7):
                    s = 'TRAILER: ' + 'LOCAL L1  FRAMENUM [23:0]: %06X: ' % ((int_x >> 37) & 0xFFFFFF) + 'GEMROC_ID: %02X ' % ((int_x >> 32) & 0x1F) + 'TIGER_ID: %01X ' % ((int_x >> 27) & 0x7) + 'LOCAL L1 COUNT[2:0]: %01X ' % (
                                (int_x >> 24) & 0x7) + 'LAST COUNT WORD FROM TIGER:CH_ID[5:0]: %02X ' % ((int_x >> 18) & 0x3F) + 'LAST COUNT WORD FROM TIGER: DATA[17:0]: %05X \n' % (int_x & 0x3FFFF)
                if (((int_x & 0xC000000000000000) >> 62) == 0x0):

                    LOCAL_L1_TS_minus_TIGER_COARSE_TS = LOCAL_L1_TIMESTAMP - ((int_x >> 32) & 0xFFFF)
                    s = 'DATA   : TIGER: %01X ' % ((int_x >> 59) & 0x7) + 'L1_TS - TIGERCOARSE_TS: %d ' % (LOCAL_L1_TS_minus_TIGER_COARSE_TS) + 'LAST TIGER FRAME NUM[2:0]: %01X ' % ((int_x >> 56) & 0x7) + 'TIGER DATA: ChID: %02X ' % ((int_x >> 50) & 0x3F) + 'tacID: %01X ' % (
                                (int_x >> 48) & 0x3) + 'Tcoarse: %04X ' % ((int_x >> 32) & 0xFFFF) + 'Ecoarse: %03X ' % ((int_x >> 20) & 0x3FF) + 'Tfine: %03X ' % ((int_x >> 10) & 0x3FF) + 'Efine: %03X \n' % (int_x & 0x3FF)
                    TIGER_not_missing[int((int_x >> 59) & 0x7)] = 1
                    self.thr_scan_rate[((int_x >> 59) & 0x7)][(int_x >> 50) & 0x3F]+=1
                    #print "C'e il TIGER!"
                #print s

        ##-- field size in bits (56 total):   2      6        2       16         10       10     10
        ##-- received_tdata                 "10" & ch_ID & tac_ID & tcoarse & ecoarse & tfine & efine
        # ff.write("{}\n".format(raw))
        TIGER_out=[]
        for i in range (0,8):
            if TIGER_not_missing[i]==0:
                TIGER_out.append(i)
        return TIGER_out, packet_missing

    def check_TL_Frame_TIGERS(self, path):
        self.thr_scan_matrix = np.zeros((8, 64))  # Tiger,Channel
        self.thr_scan_frames = np.ones(8)
        self.thr_scan_rate = np.zeros((8, 64))
        statinfo = os.stat(path)
        last_framecount = np.zeros(8)
        first_frameword = np.zeros(8)
        TIGER_not_missing = np.zeros((8))
        frame_missing =np.zeros((8))
        print ("size={}\n".format(statinfo.st_size))
        with open(path, 'r') as f:
            for i in range(0, statinfo.st_size / 8):
                data = f.read(8)
                hexdata = binascii.hexlify(data)

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

                        if first_frameword[this_tiger] == 0:
                            last_framecount[this_tiger] = this_framecount
                            first_frameword[this_tiger] = 1
                        else:
                            if this_framecount == 0xffff:
                                first_frameword[this_tiger] = 0
                            else:
                                for F in range(int(last_framecount[this_tiger]), int(this_framecount)):
                                    if last_framecount[this_tiger] + 1 == this_framecount:
                                        last_framecount[this_tiger] = this_framecount
                                        break
                                    else:
                                        print ("Frameword {} from Tiger {} missing".format(hex(F + 1), this_tiger))
                                        last_framecount[this_tiger] = last_framecount[this_tiger] + 1
                                        frame_missing[this_tiger]=1

                    if (((int_x & 0xFF00000000000000) >> 59) == 0x00):
                        self.thr_scan_matrix[(int_x >> 56) & 0x7, int(int_x >> 48) & 0x3F] = self.thr_scan_matrix[(int_x >> 56) & 0x7, int(int_x >> 48) & 0x3F] + 1
                        TIGER_not_missing[((int_x >> 56) & 0x7)]=1
        for i in range(0, 8):
            # self.thr_scan_rate[i, :] = (self.thr_scan_matrix[i, :] / self.thr_scan_frames[i]) * (1 / 0.0002048)
            self.thr_scan_rate = self.thr_scan_matrix

        TIGER_out=[]
        for i in range (0,8):
            if TIGER_not_missing[i]==0:
                TIGER_out.append(i)
        return TIGER_out, frame_missing

    def send_start_packet(self, run, subrun,datapath):

        self.cloning_sock.sendto("Srt - RUN {} SUBRUN {} FOLDER {} GEMROC{}".format(run, subrun, datapath, self.GEMROC_ID).encode(), (self.address_for_cloning_rcv, self.port_for_cloning))

    def send_end_packet(self, run, subrun, datapath):
        self.cloning_sock.sendto("End - RUN {} SUBRUN {} FOLDER {} GEMROC{}".format(run, subrun, datapath, self.GEMROC_ID).encode(), (self.address_for_cloning_rcv, self.port_for_cloning))

