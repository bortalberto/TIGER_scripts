#Author: Alberto Bortone
#Created 22/03/2018
import socket
import binascii
import numpy as np
import time
import sys
import os
import matplotlib.pyplot as plt
import pylab
from scipy.optimize import curve_fit
from scipy import special
from threading import Thread
import datetime
import random
import array

OS = sys.platform
if OS == 'win32':
	sep = '\\'
elif OS == 'linux2':
	sep = '/'
else:
	print("ERROR: OS {} non compatible".format(OS))
	sys.exit()
first_TIGER_to_SCAN=0
last_TIGER_to_scan=4
BUFSIZE = 4096

int_time=0.2 #working at 0.5
#Building the data file, scanning through the THR values, for all the channels of both chips

def sigmoid(x, x0, k):  #Used for S-fit
    y =  1 / (1 + np.exp(-k * (x - x0)))
    return y

def errorfunc(x,x0,sig,c):
    y=(special.erf((x-x0)/(1.4142*sig)))*c/2+0.5*c
    return y

class analisys_conf: #Analysis class used for configurations
    def __init__(self, com, c_inst, g_inst):
        self.GEM_COM=com
        self.GEMROC_ID=self.GEM_COM.GEMROC_ID
        self.c_inst=c_inst
        self.g_inst=g_inst
        self.log_path = "Analysis_log_GEMROC_{}.txt".format(self.GEMROC_ID)
        f=open(self.log_path,'w')
        f.close()

        self.currentCH=0
        self.currentVTH=0
        self.currentTIGER=0
        self.thr_scan_matrix=np.zeros((8,64,64))#Tiger,Channel,Threshold
        self.thr_scan_frames=np.ones((8,64,64))
        self.vthr_matrix=np.ones((8,64))
        self.timedOut=False


    def thr_preconf(self):  #Initial configuration for THR_SCAN
         #self.GEM_COM.ResetTgtGEMROC_ALL_TIGER_GCfgReg(self.GEMROC_ID,self.GEM_COM.gemroc_DAQ_XX)
         for T in range (0,8):
             print("_-_-_-_-_-Configurating Tiger {}_-_-_-_-_-\n".format(T))
             default_filename = self.GEM_COM.conf_folder+sep+"TIGER_def_g_cfg_2018.txt"
             command_reply = self.GEM_COM.WriteTgtGEMROC_TIGER_GCfgReg(self.g_inst, T)

             print("_-_-_-_-_-Configurating Channels_-_-_-_-_-\n")
             default_filename = self.GEM_COM.conf_folder+sep+"TIGER_def_ch_cfg_2018.txt"
             command_reply = self.GEM_COM.WriteTgtGEMROC_TIGER_ChCfgReg(self.c_inst, T, 64)
             print '\nCWdef command_reply: %s' % binascii.b2a_hex(command_reply)
             command_reply = self.GEM_COM.ReadTgtGEMROC_TIGER_ChCfgReg(self.c_inst, T, 64, 0)
             print '\nCRd   command_reply: %s' % binascii.b2a_hex(command_reply)

             print ("_-_-_-_-_-Send syncronous reset_-_-_-_-_-\n")
             self.GEM_COM.SynchReset_to_TgtFEB(self.GEM_COM.gemroc_DAQ_XX, 1, True)
             self.GEM_COM.SynchReset_to_TgtTCAM(self.GEM_COM.gemroc_DAQ_XX, 0, 1)

             print ("_-_-_-_-_-Setting  channels for scan_-_-_-_-_-\n")



    def thr_conf(self,test_r): #Configuration on run for scan
        # self.GEM_COM.DAQ_set(self.GEM_COM.gemroc_DAQ_XX, self.GEMROC_ID, 0xff, 0x0, 0, 0, 1, 0)

        with open(self.log_path, 'a') as log_file:
            log_file.write("{} -- Starting thr scan\n".format(time.ctime()))
        for T in range(first_TIGER_to_SCAN, last_TIGER_to_scan):
            self.GEM_COM.Set_param_dict_global(self.g_inst, "CounterEnable",T,1)
            self.GEM_COM.Set_param_dict_global(self.g_inst, "CounterPeriod",T,3)

            #self.GEM_COM.ResetTgtGEMROC_ALL_TIGER_GCfgReg(self.GEMROC_ID, self.GEM_COM.gemroc_DAQ_XX)
            print("_-_-_-_-_-Configurating Tiger {}_-_-_-_-_-\n".format(T))
            default_filename = self.GEM_COM.conf_folder + sep + "TIGER_def_g_cfg_2018.txt"
            globalset = self.GEM_COM.WriteTgtGEMROC_TIGER_GCfgReg(self.g_inst, T)
            # default_filename = self.GEM_COM.conf_folder + sep + "TIGER_def_ch_cfg_2018.txt"
            # channelset = self.GEM_COM.WriteTgtGEMROC_TIGER_ChCfgReg_fromfile(self.c_inst, self.GEMROC_ID, T, 64,default_filename)

            self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, 64, 1, 3)

            self.GEM_COM.DAQ_set(self.GEM_COM.gemroc_DAQ_XX, 2 ** T, 0, 0, 0, 1, 0)
            for j in range (0,64):  #Channel cycle
                self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, j, 1, 0)
                self.GEM_COM.Set_param_dict_channel(self.c_inst, "CounterMode", T, j, int(0x2))
                for i in range(0,64):#VTH Cycle

                        command_sent = self.GEM_COM.Set_Vth_T1(self.c_inst, T, j, i)
                        #self.GEM_COM.display_log_ChCfg_readback(command_sent,0)
                        #print bin(int (binascii.b2a_hex(command_sent),16))
                        #with open(self.log_path, 'a') as log_file:
                        #    log_file.write(binascii.b2a_hex(self.GEM_COM.Set_Vth_T1(self.c_inst, self.GEMROC_ID, T, j, i)))

                        self.currentTIGER=T
                        self.currentVTH = i
                        self.currentCH = j
                        with open(self.log_path, 'a') as log_file:
                            log_file.write("@@@@@@   {} -- Set Vth={} on channel {} \n".format(time.ctime(),i,j))

                        word_count = 0
                        self.GEM_COM.SynchReset_to_TgtFEB(self.GEM_COM.gemroc_DAQ_XX, 0, 1)
                        self.GEM_COM.SynchReset_to_TgtTCAM(self.GEM_COM.gemroc_DAQ_XX, 0, 1)
                        test_r.start_socket()
                        while word_count < 50:
                            #print word_count
                            try:
                                word_count = test_r.data_save_thr_scan(j, i, T, word_count, save_binout=False, save_txt=False)
                            #print "after word count {}".format(word_count)
                            except:
                                with open(self.log_path, 'a') as log_file:
                                    log_file.write("{} -- Timed out, sending synch reset \n".format(time.ctime(), i, j))
                                    print ("\nTIMED OUT\n")
                                    time.sleep(0.1)
                                    break
                        test_r.dataSock.close()
                        globalcheck= self.GEM_COM.ReadTgtGEMROC_TIGER_GCfgReg(self.g_inst, T)
                        if (int(binascii.b2a_hex(globalset), 16)) != ((int(binascii.b2a_hex(globalcheck), 16)) - 2048):
                            with open(self.log_path, 'a') as log_file:
                                log_file.write("Global configuration error\n")
                        globalcheck= self.GEM_COM.ReadTgtGEMROC_TIGER_GCfgReg(self.g_inst, T)
                        if (int(binascii.b2a_hex(globalset), 16)) != ((int(binascii.b2a_hex(globalcheck), 16)) - 2048):
                            with open(self.log_path, 'a') as log_file:
                                log_file.write("Global configuration error\n")
                        command_reply = self.GEM_COM.ReadTgtGEMROC_TIGER_ChCfgReg(self.c_inst, T, j, 0)
                        # L_array = array.array('I')  # L is an array of unsigned long
                        # L_array.fromstring(command_reply)
                        # L_array.byteswap()
                        # if ((L_array[8] >> 16) & 0x3) != 0:
                        #     self.GEM_COM.display_log_ChCfg_readback(command_reply,0)
                        #     print "TRIGGERMODE SBAGLIATA!!!\n"
                        #     time.sleep(10)

                        #print bin(int (binascii.b2a_hex(command_reply),16))
                        self.GEM_COM.Channel_set_check(command_sent,command_reply,self.log_path)
                        # if (int (binascii.b2a_hex(command_sent),16)) !=( (int (binascii.b2a_hex(command_reply),16)) -2048 ):
                        #     print "---____----____----____----____----"
                        #     print "!!! ERROR IN CONFIGURATION !!!"
                        #     print "---____----____----____----____----"
                        #     time.sleep(400)
                        os.system('clear')
                        string="SCANNING [TIGER={}, VTh={}, CH={}]\n".format(T,i,j)
                        sys.stdout.write(string)

                self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, j, 1, 3)
                self.GEM_COM.Set_param_dict_channel(self.c_inst, "CounterMode", T, j, 0)

            self.GEM_COM.Set_param_dict_global(self.g_inst, "CounterEnable", T, 0)

        return

    def acquire_rate(self, frame_count, rate_matrix,test_r):
        try:
            data, addr = test_r.dataSock.recvfrom(BUFSIZE)
        except:
            print "\nTimed out!"
            self.timedOut = True
            return frame_count, rate_matrix
        hexdata = binascii.hexlify(data)

        for x in range(0, len(hexdata) - 1, 16):
            int_x = 0
            for b in range(7, 0, -1):
                hex_to_int = (int(hexdata[x + b * 2], 16)) * 16 + int(hexdata[x + b * 2 + 1], 16)
                int_x = (int_x + hex_to_int) << 8
            hex_to_int = (int(hexdata[x], 16)) * 16 + int(hexdata[x + 1],
                                                          16)  # acr 2017-11-17 this should fix the problem
            int_x = (int_x + hex_to_int)
            raw = '%016X ' % int_x

            if (((int_x & 0xFF00000000000000) >> 59) == 0x04):
                frame_count = frame_count + 1
                # TIGER = (int_x >> 56) & 0x7
                # ch = (int_x >> 15) & 0xFFFF
                # s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'HB: ' + 'Framecount: %08X ' % (
                #         (int_x >> 15) & 0xFFFF) + 'SEUcount: %08X\n' % (int_x & 0x7FFF)

            if (((int_x & 0xFF00000000000000) >> 59) == 0x08):
                s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'CW: ' + 'ChID: %02X ' % (
                        (int_x >> 24) & 0x3F) + ' CounterWord: %016X\n' % (int_x & 0x00FFFFFF)

            if (((int_x & 0xFF00000000000000) >> 59) == 0x00):
                TIGER = (int_x >> 56) & 0x7
                ch = (int_x >> 48) & 0x3F
                # s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'EW: ' + 'ChID: %02X ' % (
                #         (int_x >> 48) & 0x3F) + 'tacID: %01X ' % ((int_x >> 46) & 0x3) + 'Tcoarse: %04X ' % (
                #             (int_x >> 30) & 0xFFFF) + 'Ecoarse: %03X ' % (
                #             (int_x >> 20) & 0x3FF) + 'Tfine: %03X ' % ((int_x >> 10) & 0x3FF) + 'Efine: %03X \n' % (
                #             int_x & 0x3FF)

                rate_matrix[TIGER, ch] = rate_matrix[TIGER, ch] + 1
            return frame_count, rate_matrix

    def acquire_frame(self, frame_count, frame_matrix, test_r):
        try:
            data, addr = test_r.dataSock.recvfrom(BUFSIZE)
        except:
            print "\nTimed out!"
            self.timedOut = True
            return frame_count, frame_matrix
        hexdata = binascii.hexlify(data)

        for x in range(0, len(hexdata) - 1, 16):
            int_x = 0
            for b in range(7, 0, -1):
                hex_to_int = (int(hexdata[x + b * 2], 16)) * 16 + int(hexdata[x + b * 2 + 1], 16)
                int_x = (int_x + hex_to_int) << 8
            hex_to_int = (int(hexdata[x], 16)) * 16 + int(hexdata[x + 1],
                                                          16)  # acr 2017-11-17 this should fix the problem
            int_x = (int_x + hex_to_int)
            raw = '%016X ' % int_x

            if (((int_x & 0xFF00000000000000) >> 59) == 0x04):
                frame_count = frame_count + 1
                TIGER = (int_x >> 56) & 0x7
                # ch = (int_x >> 15) & 0xFFFF
                # s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'HB: ' + 'Framecount: %08X ' % (
                #          (int_x >> 15) & 0xFFFF) + 'SEUcount: %08X\n' % (int_x & 0x7FFF)
                for i in range (0,len(frame_matrix[TIGER,:])):
                    if not frame_matrix[TIGER,i]:
                        frame_matrix[TIGER,i]=(int_x >> 15) & 0xFFFF
                        break

            # if (((int_x & 0xFF00000000000000) >> 59) == 0x08):
            #     s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'CW: ' + 'ChID: %02X ' % (
            #             (int_x >> 24) & 0x3F) + ' CounterWord: %016X\n' % (int_x & 0x00FFFFFF)
            #
            # if (((int_x & 0xFF00000000000000) >> 59) == 0x00):
            #     TIGER = (int_x >> 56) & 0x7
            #     ch = (int_x >> 48) & 0x3F
            #     s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'EW: ' + 'ChID: %02X ' % (
            #     #         (int_x >> 48) & 0x3F) + 'tacID: %01X ' % ((int_x >> 46) & 0x3) + 'Tcoarse: %04X ' % (
            #     #             (int_x >> 30) & 0xFFFF) + 'Ecoarse: %03X ' % (
            #     #             (int_x >> 20) & 0x3FF) + 'Tfine: %03X ' % ((int_x >> 10) & 0x3FF) + 'Efine: %03X \n' % (
            #     #             int_x & 0x3FF)
            #
            #     #rate_matrix[TIGER, ch] = rate_matrix[TIGER, ch] + 1
        return frame_count,frame_matrix

    def fill_VTHR_matrix(self, number_sigma, offset, tiger_id):

        file_p = self.GEM_COM.conf_folder + sep + "GEMROC{}_Chip{}.thr".format(self.GEMROC_ID,tiger_id)
        thr0 = np.loadtxt(file_p, )
        thr = np.rint(thr0[:, 0]) - np.rint(thr0[:, 1]) * number_sigma + offset
        for c in range(0, 64):
            if thr[c] < 0 or thr[c] == 0:
                thr[c] = 0
            if thr[c] > 63:
                thr[c] = 63
        self.vthr_matrix[tiger_id, :] = thr
        return 0

    def thr_autotune(self, T, desired_rate, test_r, max_iter=20,final_lowering=True):
        frameMax = 200
        frame_count = 0
        self.GEM_COM.SynchReset_to_TgtFEB(self.GEM_COM.gemroc_DAQ_XX, 0, 1)
        self.GEM_COM.SynchReset_to_TgtTCAM(self.GEM_COM.gemroc_DAQ_XX, 0, 1)

        self.GEM_COM.DAQ_set(self.GEM_COM.gemroc_DAQ_XX, 2 ** T, 0x0, 0, 0, 1, 0)

        for iter in range(0, max_iter):
            print("\nIteration {}".format(iter))
            autotune_scan_matrix = np.zeros((8, 64))
            # for T in range (first_TIGER_to_SCAN,last_TIGER_to_scan):
            # self.GEM_COM.DAQ_set(self.GEM_COM.gemroc_DAQ_XX, self.GEMROC_ID, 2 ** T, 0x0, 0, 0, 1, 0)
            self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, 64, 1, 0)
            self.GEM_COM.Load_VTH_fromMatrix(self.c_inst, T, self.vthr_matrix)
            test_r.start_socket()
            while frame_count < frameMax and not self.timedOut:
                frame_count, autotune_scan_matrix = self.acquire_rate(frame_count, autotune_scan_matrix,test_r)
            test_r.dataSock.close()
            if not self.timedOut:
                autotune_scan_matrix = autotune_scan_matrix / frame_count * (1 / 0.0002048)

                for channel in range(0, 64):
                    if autotune_scan_matrix[T,channel]<(desired_rate-desired_rate/5) or autotune_scan_matrix[T,channel]>(desired_rate+desired_rate/5):
                        if autotune_scan_matrix[T,channel]<(desired_rate/1000):
                            self.vthr_matrix[T,channel]=self.vthr_matrix[T,channel]+2
                        if autotune_scan_matrix[T,channel]>(desired_rate*1000):
                            self.vthr_matrix[T,channel]=self.vthr_matrix[T,channel]-3

                        if autotune_scan_matrix[T, channel] < desired_rate:
                            self.vthr_matrix[T, channel] = self.vthr_matrix[T, channel] + 1
                        if autotune_scan_matrix[T, channel] > desired_rate:
                            self.vthr_matrix[T, channel] = self.vthr_matrix[T, channel] - 1

                    if self.vthr_matrix[T, channel] <= 0:
                        self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, channel, 1, 3)
                        self.vthr_matrix[T, channel] = 0
                    if self.vthr_matrix[T, channel] > 63:
                        self.vthr_matrix[T, channel] = 63

                    self.GEM_COM.Load_VTH_fromMatrix(self.c_inst, T, self.vthr_matrix)

                print(" \n Scan matrix TIGER {}".format(T))
                print autotune_scan_matrix[T, :]
                print(" \n Threshold matrix TIGER {}".format(T))
                print(self.vthr_matrix[T, :])
                self.timedOut = False
                frame_count = 0

                #self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, self.GEMROC_ID, T, 64, 1, 3)
        # for T in range (first_TIGER_to_SCAN,last_TIGER_to_scan):

        if final_lowering:
            print ("____----Lowering all channels 5 times higher than the desired (can be disabled in code----____")
            test_r.start_socket()
            while frame_count < frameMax and not self.timedOut:
                frame_count, autotune_scan_matrix = self.acquire_rate(frame_count, autotune_scan_matrix, test_r)
            test_r.dataSock.close()
            if not self.timedOut:
                autotune_scan_matrix = autotune_scan_matrix / frame_count * (1 / 0.0002048)

                for channel in range(0, 64):
                    if autotune_scan_matrix[T, channel] > desired_rate*5:
                        self.vthr_matrix[T, channel] = self.vthr_matrix[T, channel] - 1

        name = "." + sep + "log_folder" + sep + "THR_LOG{}_GEMROC{}_TIGER_{}_autotuned.txt".format(
            datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"), self.GEMROC_ID, T)
        np.savetxt(name, np.c_[self.vthr_matrix[T, :]])
        name = "." + sep + "conf" + sep + "GEMROC{}_TIGER_{}_autotuned.thr".format(self.GEMROC_ID, T)
        np.savetxt(name, np.c_[self.vthr_matrix[T, :]])

        X = "Autotune done, press enter to exit"
        print (X)

        time.sleep(2)

    def check_rate(self, TIGER_ID, frameMax,test_r):
        scan_matrix = np.zeros((8, 64))
        frame_count = 0
        test_r.start_socket()
        while frame_count < frameMax and not self.timedOut:
            frame_count, scan_matrix = self.acquire_rate(frame_count, scan_matrix,test_r)
        test_r.dataSock.close()
        scan_matrix = scan_matrix / frameMax * (1 / 0.0002048)
        x = np.arange(0, 64)

        plt.plot()
        plt.ylabel('Rate')
        plt.xlabel('Channel')
        plt.bar(x, scan_matrix[TIGER_ID, :], width=1.0)
        plt.show()
        self.timedOut = False

        return 0

    def check_sync(self):
        test_r = analisys_read(self.GEM_COM, self.c_inst)
        frame_count = 0
        frameMax=48
        test_r.start_socket()
        frame_matrix=np.zeros((8,8))
        while frame_count < frameMax and not self.timedOut:
            frame_count, frame_matrix = self.acquire_frame(frame_count, frame_matrix,test_r)
        test_r.dataSock.close()
        print "Framewords collected:"
        print frame_matrix
        coincidence_matrix=np.zeros((8,8))
        for i in range (0,8):
            for j in range (i,8):
                coincidence_matrix[i,j]=np.any(np.in1d(frame_matrix[i,:], frame_matrix[j,:]))
                if not np.any(np.in1d(frame_matrix[i,:], frame_matrix[j,:])) and not np.all(frame_matrix[i,:]==np.zeros((1,len(frame_matrix)))) and not np.all(frame_matrix[j,:]==np.zeros((1,len(frame_matrix))).all()) :
                    print "TIGER {} not in sync with TIGER {}".format(i,j)
        #print coincidence_matrix
        self.timedOut=False

        return 0

    def TIGER_config_test(self):
        print "--------------------------"
        print "Configuration test, GEMROC {}".format(self.GEMROC_ID)
        print "--------------------------"

        default_g_inst_settings_filename = self.GEM_COM.conf_folder + sep + "TIGER_def_g_cfg_2018.txt"
        default_c_inst_settings_filename = self.GEM_COM.conf_folder + sep + "TIGER_def_ch_cfg_2018.txt"
        error_list=[]
        for T in range (0,8):
            print ("\nGemroc {}, TIGER {}".format(self.GEMROC_ID, T))
            command_sent = self.GEM_COM.WriteTgtGEMROC_TIGER_GCfgReg(self.g_inst, T, False)
            command_reply = self.GEM_COM.ReadTgtGEMROC_TIGER_GCfgReg(self.g_inst, T)
            if (int(binascii.b2a_hex(command_sent), 16)) != ((int(binascii.b2a_hex(command_reply), 16)) - 2048):
                print "   !!! Errors in global configuration !!!   "
                error_list.append(T)
            else:
                print "         Global Configuration OK         "
            ch_list = []

            for ch in range (0,64):
                command_sent = self.GEM_COM.WriteTgtGEMROC_TIGER_ChCfgReg(self.c_inst, T, ch)
                command_reply = self.GEM_COM.ReadTgtGEMROC_TIGER_ChCfgReg(self.c_inst, T,ch, 0)
                if (int(binascii.b2a_hex(command_sent), 16)) != ((int(binascii.b2a_hex(command_reply), 16)) - 2048):
                    if not T in error_list:
                        error_list.append(T)
                    ch_list.append(ch)
            if ch_list:
                #print "Errors configurating channels: {}".format(ch_list)
                print "   !!! Error(s) in channel(s) configuration !!!  "
            else:
                print "         Channel Configuration OK         "



        if error_list:
            print " \n--Gemroc {}: Errors configurating Tiger: {}".format(self.GEMROC_ID,error_list)
        else:
            print " \n--Gemroc {}: Configuration test passed".format(self.GEMROC_ID)


        return (error_list)

    def TIGER_TP_test(self):
        print "--------------------------"
        print "Test pulse reception, GEMROC {}". format(self.GEMROC_ID)
        print "--------------------------"
        for T in range (0,8):
            self.GEM_COM.set_FE_TPEnable(self.g_inst, T, 1)
            for ch in range (0,64):
                self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst,T,ch,0, 1)

            frameMax=10
            """ Acquiring rate """
            test_r=analisys_read(self.GEM_COM, self.c_inst)
            scan_matrix = np.zeros((8, 64))
            frame_count = 0
            test_r.start_socket()
            while frame_count < frameMax and not self.timedOut:
                frame_count, scan_matrix = self.acquire_rate(frame_count, scan_matrix, test_r)
            test_r.dataSock.close()
            scan_matrix = scan_matrix / frameMax * (1 / 0.0002048)
            for ch in range (0,64):
                self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst,T,ch,0, 3)
            self.GEM_COM.set_FE_TPEnable(self.g_inst, T, 0)
            if self.timedOut:
                print "\nTiger {} timed out".format(T)
                self.timedOut=0
        #TODO finish this function when we can check on real GEMROCS


    def TIGER_GEMROC_sync_test(self):
        print "--------------------------"
        print "Checking synchronization for GEMROC {}".format(self.GEMROC_ID)
        print "--------------------------"

        self.GEM_COM.SynchReset_to_TgtFEB(self.GEM_COM.gemroc_DAQ_XX, 0, 1)
        self.check_sync()
    def TIGER_delay_tuning(self):
        for T in range (0,8):
            self.GEM_COM.Set_param_dict_global(self.g_inst, "FE_TPEnable",T,1)
            for ch in range (0,63):
                self.GEM_COM.Set_param_dict_channel(self.c_inst, "TP_disable_FE", T, ch, 0)
                self.GEM_COM.Set_param_dict_channel(self.c_inst,"TriggerMode",T,ch,1)

        for Ts in range (0,4):
            self.GEM_COM.DAQ_set(self.GEM_COM.gemroc_DAQ_XX, 2 ** (Ts*2)+2**(Ts*2+1), 2 ** (Ts*2)+2**(Ts*2+1), 1, 1, 1, 1)
            average=[]
            for TD in range (0,64):
                self.GEM_COM.set_FEB_timing_delays(TD, TD, TD, TD)
                self.GEM_COM.set_counter((Ts * 2), 0, 0)
                self.GEM_COM.reset_counter()
                time.sleep(0.2)
                counter1=self.GEM_COM.GEMROC_counter_get()
                self.GEM_COM.set_counter((Ts * 2), 0, 0)
                self.GEM_COM.reset_counter(Ts*2+1)
                self.GEM_COM.reset_counter()
                time.sleep(0.2)
                counter2=self.GEM_COM.GEMROC_counter_get()
                average.append((counter1+counter2)/2)

        print average


    def __del__(self):
        return 0


class analisys_read:
    def __init__(self, com, c_inst):
        self.c_inst=c_inst
        self.GEM_COM=com
        self.GEMROC_ID=self.GEM_COM.GEMROC_ID
        self.data_path = com.Tscan_folder+sep+'thr_scan_dump_data.txt'
        f=open(self.data_path,'w')
        f.close()
        self.bindata_path = com.Tscan_folder+sep+'thr_scan_dump_BIN.dat'
        f=open(self.bindata_path,'w')
        f.close()
        self.scan_path = com.Tscan_folder+sep+"Scan_{}.txt".format(self.GEMROC_ID)
        self.HOST_IP = self.GEM_COM.HOST_IP
        self.HOST_PORT = 58880 + self.GEMROC_ID
        self.thr_scan_matrix=np.zeros((8,64,64))#Tiger,Channel,Threshold
        self.thr_scan_frames=np.ones((8,64,64))
        self.vthr_matrix=np.ones((8,64))

        self.thr_scan_rate = np.zeros((8, 64, 64))
        self.thresholds = np.zeros((8, 64, 2))

    def start_socket(self):
        self.dataSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dataSock.settimeout(0.02)
        self.dataSock.bind((self.HOST_IP, self.HOST_PORT))
        #self.dataSock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8388608 )
        #self.dataSock.getsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF)

    def __del__(self):
        return 0

    def data_save_thr_scan(self, ch, vth, TIG, frame_count, save_binout=False, save_txt=False):
        #print 'count_frame {}'.format(frame_count)
        is_framecount = False
        event_counter = 0
        return_string = ""
        data, addr = self.dataSock.recvfrom(BUFSIZE)
        if save_binout:
            with open(self.bindata_path, 'a') as binout_file:
                binout_file.write(data)

        hexdata = binascii.hexlify(data)

        for x in range(0, len(hexdata) - 1, 16):
            int_x = 0
            for b in range(7, 0, -1):
                hex_to_int = (int(hexdata[x + b * 2], 16)) * 16 + int(hexdata[x + b * 2 + 1], 16)
                int_x = (int_x + hex_to_int) << 8
            hex_to_int = (int(hexdata[x], 16)) * 16 + int(hexdata[x + 1],
                                                          16)  # acr 2017-11-17 this should fix the problem
            int_x = (int_x + hex_to_int)
            raw = '%016X ' % int_x

            if (((int_x & 0xFF00000000000000) >> 59) == 0x04):
                is_framecount = True
                frame_count = frame_count +1
                s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'HB: ' + 'Framecount: %08X ' % (
                        (int_x >> 15) & 0xFFFF) + 'SEUcount: %08X\n' % (int_x & 0x7FFF)
                if TIG == (int_x >> 56) & 0x7:
                    self.thr_scan_frames[(int_x >> 56) & 0x7, ch, vth] = self.thr_scan_frames[(int_x >> 56) & 0x7, ch, vth] + 1

            elif (((int_x & 0xFF00000000000000) >> 59) == 0x08):
                s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'CW: ' + 'ChID: %02X ' % (
                        (int_x >> 24) & 0x3F) + ' CounterWord: %016X\n' % (int_x & 0x00FFFFFF)
            elif (((int_x & 0xFF00000000000000) >> 59) == 0x00):
                s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'EW: ' + 'ChID: %02X ' % (
                        (int_x >> 48) & 0x3F) + 'tacID: %01X ' % ((int_x >> 46) & 0x3) + 'Tcoarse: %04X ' % (
                            (int_x >> 30) & 0xFFFF) + 'Ecoarse: %03X ' % (
                            (int_x >> 20) & 0x3FF) + 'Tfine: %03X ' % ((int_x >> 10) & 0x3FF) + 'Efine: %03X \n' % (
                            int_x & 0x3FF)
                #if (int_x & 0x3FF) not in [1008,768,15]:
                if ((ch & 0x3F)==(int(int_x >> 48) & 0x3F) and (TIG == (int_x >> 56) & 0x7)):
                    self.thr_scan_matrix[(int_x >> 56) & 0x7, int(int_x >> 48) & 0x3F, vth] = self.thr_scan_matrix[(int_x >> 56) & 0x7, int(int_x >> 48) & 0x3F, vth] + 1
                    event_counter = event_counter + 1
                    is_framecount = False
            else:
                with open(self.data_path, 'a') as out_file:
                    out_file.write("ENCODING ERROR\n")
            if save_txt:
                return_string = return_string + ("\n" + raw + " " + s)

        with open(self.data_path, 'a') as out_file:
            out_file.write(return_string)
        return frame_count


    def data_save_thr_scan_with_counter(self, ch, vth, TIG, frame_count, save_binout=False, save_txt=False):
        #print 'count_frame {}'.format(frame_count)
        is_framecount = False
        event_counter = 0
        return_string = ""
        data, addr = self.dataSock.recvfrom(BUFSIZE)
        if save_binout:
            with open(self.bindata_path, 'a') as binout_file:
                binout_file.write(data)

        hexdata = binascii.hexlify(data)

        for x in range(0, len(hexdata) - 1, 16):
            int_x = 0
            for b in range(7, 0, -1):
                hex_to_int = (int(hexdata[x + b * 2], 16)) * 16 + int(hexdata[x + b * 2 + 1], 16)
                int_x = (int_x + hex_to_int) << 8
            hex_to_int = (int(hexdata[x], 16)) * 16 + int(hexdata[x + 1],
                                                          16)  # acr 2017-11-17 this should fix the problem
            int_x = (int_x + hex_to_int)
            raw = bin(int_x)

            if (((int_x & 0xFF00000000000000) >> 59) == 0x04):
                frame_count = frame_count +1
                s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'HB: ' + 'Framecount: %08X ' % (
                        (int_x >> 15) & 0xFFFF) + 'SEUcount: %08X\n' % (int_x & 0x7FFF)
                if TIG == (int_x >> 56) & 0x7:
                    self.thr_scan_frames[(int_x >> 56) & 0x7, ch, vth] = self.thr_scan_frames[(int_x >> 56) & 0x7, ch, vth] + 1

            elif (((int_x & 0xFF00000000000000) >> 59) == 0x08):
                s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'CW: ' + 'ChID: %02X ' % (
                        (int_x >> 24) & 0x3F) + ' CounterWord: %016X\n' % (int_x & 0x00FFFFFF)
                if (ch ==(int(int_x >> 24) & 0x3F) and (TIG == (int_x >> 56) & 0x7)):
                    self.thr_scan_matrix[(int_x >> 56) & 0x7, int(int_x >> 24) & 0x3F, vth] = int_x & 0x00FFFFFF
                    frame_count=20000000



            elif (((int_x & 0xFF00000000000000) >> 59) == 0x00):
                s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'EW: ' + 'ChID: %02X ' % (
                        (int_x >> 48) & 0x3F) + 'tacID: %01X ' % ((int_x >> 46) & 0x3) + 'Tcoarse: %04X ' % (
                            (int_x >> 30) & 0xFFFF) + 'Ecoarse: %03X ' % (
                            (int_x >> 20) & 0x3FF) + 'Tfine: %03X ' % ((int_x >> 10) & 0x3FF) + 'Efine: %03X \n' % (
                            int_x & 0x3FF)

            else:
                with open(self.data_path, 'a') as out_file:
                    out_file.write("ENCODING ERROR\n")
            if save_txt:
                return_string = return_string + ("\n" + raw + " " + s)

        with open(self.data_path, 'a') as out_file:
            out_file.write(return_string)
        return frame_count

    def channel_plot(self, Chip, Channel):
        plt.plot(self.thr_scan_matrix[Chip, Channel, :], 'bo')
        plt.ylabel('Counts')
        plt.xlabel('V Threshold [Digits]')
        plt.title('Threshold Scan Tiger {}, channel {}'.format(Chip, Channel))
        plt.show()
        return 0

    def save_scan_on_file(self):
        f = open(self.scan_path, 'w')
        for T in range(0, 8):
            f.write("Tiger {}".format(T))
            f.write("Frames\n")
            for i in range(0, 64):
                f.write("Channel {}\n".format(i))

                for j in range (0,64):
                    if self.thr_scan_frames[T, i, j]:
                        f.write("{}    ".format(self.thr_scan_frames[T, i, j]))
                    else:
                        f.write("0    ")

            f.write("\nEvents\n")
            for i in range(0, 64):
                f.write("Channel {}\n".format(i))

                for j in range (0,64):
                    if self.thr_scan_frames[T, i, j]:
                        f.write("{}    ".format(self.thr_scan_matrix[T, i, j]))
                    else:
                        f.write("0    ")
            f.write("\n")

        f.close()

    def make_rate(self):
        self.thr_scan_rate = self.thr_scan_matrix / self.thr_scan_frames

    def colorPlot(self, file_name, rate=False):
        for T in range(first_TIGER_to_SCAN, last_TIGER_to_scan):
            plt.plot()
            x = np.arange(0, 64)
            y = np.arange(0, 64)
            if rate == True:
                string = "rate"
                z = self.thr_scan_rate[T, :, :]
            else:
                string = "counts"
                z = self.thr_scan_matrix[T, :, :]
            plt.ylabel('Channels')
            plt.xlabel('V Threshold [Digits]')
            plt.pcolor(x, y, z, cmap="plasma", )
            plt.colorbar()

            plt.title('Threshold Scan Tiger {}, {}'.format(T, string))
            plt.savefig('{}CHIP{}.png'.format(file_name, T))
            plt.clf()

        return 0

    def normalize_rate(self):
        for T in range(first_TIGER_to_SCAN, last_TIGER_to_scan):

            for z in range(0, 64):
                max = np.max(self.thr_scan_rate[T, z, :])
                self.thr_scan_rate[T, z, :] = self.thr_scan_rate[T, z, :] / max
                # for i in range (0,64):
                #     if self.thr_scan_rate[T,z,i]==1:
                #         for j in range (i,64):
                #             if self.thr_scan_rate[T, z, j] <0.9: #Force to 1 all the values after the max, necessary for convergence
                #                 self.thr_scan_rate[T, z, j]=1

    def global_sfit(self, retry=False):
        for T in range(first_TIGER_to_SCAN, last_TIGER_to_scan):
            thr_file_path = self.GEM_COM.conf_folder + sep + "GEMROC{}_Chip{}.thr".format(self.GEMROC_ID, T)
            f = open(thr_file_path, 'w')
            f.close()
            for ch in range(0, 64):
                try:
                    # (x,k)=self.sfit(self.thr_scan_rate[T,i,:])
                    print ("Showing fit channel {}".format(ch))
                    (x, k, c) = self.errfit(self.thr_scan_rate[T, ch, :])
                except:
                    if retry:
                        print("Not converged, launching VTH scan on channel\n")

                        try:
                            (x, k) = self.sfit(self.thr_scan_rate[T, ch, :])
                            # (x, k) = self.errfit(self.thr_scan_rate[T, i, :])
                        except:
                            print ("Can't converge \n")
                            (x, k) = (0, 0)



                    else:
                        (x, k) = (0, 0)

                # if x>63:
                #     if retry:
                #         print("Not converged, launching VTH scan on channel\n")
                #
                #         # self.scan_configurer.currentVTH=i
                #         # self.scan_configurer.currentTIGER=T
                #         # single_scan=self.scan_threader.Thread_handler("scanner",test_c,test_r)
                #         # single_scan.start()
                #         # self.scan_configurer.single_thr(T,i)
                #         # single_scan.join()
                #
                #         try:
                #             (x, k) = self.sfit(self.thr_scan_rate[T, ch, :])
                #             # (x, k) = self.errfit(self.thr_scan_rate[T, i, :])
                #         except:
                #             print ("Can't converge \n")
                #             (x,k)=(0,0)
                #         if x > 63:
                #             (x,k)=(0,0)
                #
                #     else:
                #         (x, k) = (0, 0)

                self.thresholds[T, ch, 0] = x
                self.thresholds[T, ch, 1] = k

                print("\n CHANNEL ={} x={} k={}".format(ch, x, k))

                with open(thr_file_path, 'a') as f:
                    f.write("{}     {}\n".format(self.thresholds[T, ch, 0], self.thresholds[T, ch, 1]))

    def sfit(self, ydata, showplot=True):
        guess = np.array([35, 1, 0.35])
        xdata = np.arange(0, 64)
        ydata = ydata
        popt, pcov = curve_fit(sigmoid, xdata, ydata, guess, method='lm', maxfev=50000)

        x = np.arange(0, 64)
        y = sigmoid(x, *popt)
        if showplot:
            pylab.plot(xdata, ydata, 'o', label='data')
            pylab.plot(x, y, label='fit')
            pylab.ylim(0, 1.05)
            pylab.legend(loc='best')
            pylab.show()
        return popt

    def errfit(self, ydata, showplot=True):
        showplot = False
        # ydata = ydata
        for i, ytest in enumerate(ydata):
            if ytest > 0.9:
                m = i
                break
        xdata = np.arange(0, int(m) )

        popt, pcov = curve_fit(errorfunc, xdata, ydata[:m ], method='lm', maxfev=5000)

        print ("\n")
        print popt

        x = np.arange(0, 64)
        y = errorfunc(x, *popt)

        if showplot:
            xdata = np.arange(0, 64)

            pylab.plot(xdata, ydata, 'o', label='data')
            pylab.plot(x, y, label='fit')
            pylab.ylim(0, 1.05)
            pylab.legend(loc='best')
            pylab.show()
        return (popt)

    def splot(self, TIGER=0, CHANNEL=2):
        plt.plot(self.thr_scan_rate[TIGER, CHANNEL, :], 'bo')

        plt.ylabel('Channels')
        plt.xlabel('V Threshold [Digits]')
        # ax.set_zlabel('Counts')
        plt.title('Threshold Scan Tiger {}, ch {}'.format(TIGER, CHANNEL))
        plt.show()



class Thread_handler(Thread): #In order to scan during configuration is mandatory to use multithreading
    def __init__(self, name,analisys_conf,analysys_reader):
        Thread.__init__(self)
        self.name = name
        self.configurer=analisys_conf
        self.reader=analysys_reader
        self.scanning=True

    def run(self):
        # if option=="multi":
        while self.scanning:
            # print ("TIGER={}".format(self.configurer.currentTIGER))
            # print ("Channel={}".format(self.configurer.currentCH))
            # print ("VTH={}".format(self.configurer.currentVTH))
            self.reader.data_save_thr_scan(self.configurer.currentCH, self.configurer.currentVTH, self.configurer.currentTIGER, False, True)
        with open(self.configurer.log_path, 'a') as log_file:
            log_file.write("{} --Timed out, closing acquisition\n".format(time.ctime()))
