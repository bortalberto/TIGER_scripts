#Author: Alberto Bortone
#Created 22/03/2018
import socket
import binascii
import numpy as np
import sys
import os
import matplotlib
matplotlib.use('pdf',warn=False, force=True)
import matplotlib.pyplot as plt
import pylab
from scipy.optimize import curve_fit
from scipy import special
from threading import Thread
import datetime
import multiprocessing
import time
OS = sys.platform
if OS == 'win32':
	sep = '\\'
elif OS == 'linux2':
	sep = '/'
else:
	print("ERROR: OS {} non compatible".format(OS))
	sys.exit()
BUFSIZE = 4096

int_time=0.2 #working at 0.5
#Building the data file, scanning through the THR values, for all the channels of both chips

def sigmoid(x, x0, k):  #Used for S-fit
    y =  1 / (1 + np.exp(-k * (x - x0)))
    return y

def errorfunc(x,x0,sig,c):
    y=(special.erf((x-x0)/(1.4142*sig)))*c/2+0.5*c
    return y

class analisys_conf: #Analysis class used for configurations10
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
             self.GEM_COM.SynchReset_to_TgtFEB(1, True)
             self.GEM_COM.SynchReset_to_TgtTCAM(0, 1)

             print ("_-_-_-_-_-Setting  channels for scan_-_-_-_-_-\n")



    def thr_conf(self, test_r, first_TIGER_to_SCAN, last_TIGER_to_SCAN): #Configuration on run for scan
        # self.GEM_COM.DAQ_set(self.GEM_COM.gemroc_DAQ_XX, self.GEMROC_ID, 0xff, 0x0, 0, 0, 1, 0)

        with open(self.log_path, 'a') as log_file:
            log_file.write("{} -- Starting thr scan\n".format(time.ctime()))
        for T in range(first_TIGER_to_SCAN, last_TIGER_to_SCAN):
            self.GEM_COM.Set_param_dict_global(self.g_inst, "CounterEnable",T,1)
            self.GEM_COM.Set_param_dict_global(self.g_inst, "CounterPeriod",T,3)

            #self.GEM_COM.ResetTgtGEMROC_ALL_TIGER_GCfgReg(self.GEMROC_ID, self.GEM_COM.gemroc_DAQ_XX)
            print("_-_-_-_-_-Configurating Tiger {}_-_-_-_-_-\n".format(T))
            default_filename = self.GEM_COM.conf_folder + sep + "TIGER_def_g_cfg_2018.txt"
            globalset = self.GEM_COM.WriteTgtGEMROC_TIGER_GCfgReg(self.g_inst, T)
            # default_filename = self.GEM_COM.conf_folder + sep + "TIGER_def_ch_cfg_2018.txt"
            # channelset = self.GEM_COM.WriteTgtGEMROC_TIGER_ChCfgReg_fromfile(self.c_inst, self.GEMROC_ID, T, 64,default_filename)

            self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, 64, 1, 3)

            self.GEM_COM.DAQ_set(2 ** T, 0, 0, 0, 1, 0)
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
                        self.GEM_COM.SynchReset_to_TgtFEB(0, 1)
                        self.GEM_COM.SynchReset_to_TgtTCAM(0, 1)
                        test_r.start_socket()
                        while word_count < 60:
                            #print word_count
                            try:
                                word_count = test_r.data_save_thr_scan(j, i, T, word_count, save_binout=False, save_txt=False)
                            #print "after word count {}".format(word_count)
                            except:
                                with open(self.log_path, 'a') as log_file:
                                    log_file.write("{} -- Timed out \n".format(time.ctime(), i, j))
                                    print ("\nTIMED OUT\n")
                                    time.sleep(0.1)
                                    break
                        test_r.dataSock.close()
                        # globalcheck= self.GEM_COM.ReadTgtGEMROC_TIGER_GCfgReg(self.g_inst, T)
                        # if (int(binascii.b2a_hex(globalset), 16)) != ((int(binascii.b2a_hex(globalcheck), 16)) - 2048):
                        #     with open(self.log_path, 'a') as log_file:
                        #         log_file.write("Global configuration error\n")
                        # globalcheck= self.GEM_COM.ReadTgtGEMROC_TIGER_GCfgReg(self.g_inst, T)
                        # if (int(binascii.b2a_hex(globalset), 16)) != ((int(binascii.b2a_hex(globalcheck), 16)) - 2048):
                        #     with open(self.log_path, 'a') as log_file:
                        #         log_file.write("Global configuration error\n")
                        # command_reply = self.GEM_COM.ReadTgtGEMROC_TIGER_ChCfgReg(self.c_inst, T, j, 0)
                        # L_array = array.array('I')  # L is an array of unsigned long
                        # L_array.fromstring(command_reply)
                        # L_array.byteswap()
                        # if ((L_array[8] >> 16) & 0x3) != 0:
                        #     self.GEM_COM.display_log_ChCfg_readback(command_reply,0)
                        #     print "TRIGGERMODE SBAGLIATA!!!\n"
                        #     time.sleep(10)

                        #print bin(int (binascii.b2a_hex(command_reply),16))
                        # self.GEM_COM.Channel_set_check(command_sent,command_reply,self.log_path)
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
    def thr_conf_using_GEMROC_COUNTERS(self,test_r, first_TIGER_to_SCAN, last_TIGER_to_SCAN,print_to_screen=True):
        with open(self.log_path, 'a') as log_file:
            log_file.write("{} -- Starting thr scan\n".format(time.ctime()))
        thr_scan_matrix=np.zeros((8,64,64))
        for T in range(first_TIGER_to_SCAN, last_TIGER_to_SCAN):
            self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, 64, 1, 3)
            self.GEM_COM.DAQ_set(0, 0, 0, 0, 1, 1)

            for j in range (0,64):  #Channel cycle
                self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, j, 0, 0)
                for i in range(0,64):#VTH Cycle, i)**
                        # with open(self.log_path, 'a') as log_file:
                        self.GEM_COM.Set_Vth_T1(self.c_inst, T, j, i)
                        # with open(self.log_path, 'a') as log_file:
                        #     log_file.write("@@@@@@   {} -- Set Vth={} on channel {} \n".format(time.ctime(),i,j))
                        self.GEM_COM.set_counter(T, 0, j)
                        self.GEM_COM.SynchReset_to_TgtFEB(0, 1)
                        #self.GEM_COM.SynchReset_to_TgtTCAM(0, 1)
                        self.GEM_COM.reset_counter()
                        time.sleep(0.03)
                        thr_scan_matrix[T, j, i] = self.GEM_COM.GEMROC_counter_get()
                        # print ("Events: {}".format(thr_scan_matrix[T, j, i]))
                        if print_to_screen:
                            #os.system('clear')
                            string="SCANNING [TIGER={}, VTh={}, CH={}]\n".format(T,i,j)
                            print(string)

                self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, j, 1, 3)

        return thr_scan_matrix
    def thr_autotune_wth_counter_progress(self, T, desired_rate, test_r, pipe_out,max_iter=16, tempo=0.2,print_to_screen=True):
        self.GEM_COM.SynchReset_to_TgtFEB(0, 1)
        doing_tuning_matrix = np.ones((64))

        for iter in range(0, max_iter):
            print("\nIteration {}".format(iter))
            autotune_scan_matrix = np.zeros((8, 64))
            # for T in range (first_TIGER_to_SCAN,last_TIGER_to_scan):
            # self.GEM_COM.DAQ_set(self.GEM_COM.gemroc_DAQ_XX, self.GEMROC_ID, 2 ** T, 0x0, 0, 0, 1, 0)
            self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, 64, 1, 0)
            self.GEM_COM.Load_VTH_fromMatrix(self.c_inst, T, self.vthr_matrix)
            self.GEM_COM.DAQ_set(2 ** T, 0x0, 0, 0, 1, 0)
            self.GEM_COM.SynchReset_to_TgtTCAM(0, 1)
            for j in range (0,64):
                self.GEM_COM.set_counter(T, 0, j)
                self.GEM_COM.SynchReset_to_TgtFEB(0, 1)
                self.GEM_COM.SynchReset_to_TgtTCAM(0, 1)
                self.GEM_COM.reset_counter()
                time.sleep(tempo)
                autotune_scan_matrix[T,j]=self.GEM_COM.GEMROC_counter_get()


            autotune_scan_matrix = autotune_scan_matrix*(1/tempo)

            for channel in range(0, 64):
                # if autotune_scan_matrix[T,channel]<(desired_rate-desired_rate/5) or autotune_scan_matrix[T,channel]>(desired_rate+desired_rate/5):
                #     if autotune_scan_matrix[T,channel]<(desired_rate/1000):
                #         self.vthr_matrix[T,channel]=self.vthr_matrix[T,channel]+2
                #     if autotune_scan_matrix[T,channel]>(desired_rate*1000):
                #         self.vthr_matrix[T,channel]=self.vthr_matrix[T,channel]-3
                if autotune_scan_matrix[T, channel] < desired_rate * (1.5) and autotune_scan_matrix[T, channel] > desired_rate * (0.5):
                    doing_tuning_matrix[channel] = 0

                if doing_tuning_matrix[channel] == 1:
                    if autotune_scan_matrix[T, channel] < desired_rate:
                        self.vthr_matrix[T, channel] = self.vthr_matrix[T, channel] + 1
                    if autotune_scan_matrix[T, channel] > desired_rate:
                        self.vthr_matrix[T, channel] = self.vthr_matrix[T, channel] - 1

                    if self.vthr_matrix[T, channel] <= 0:
                        self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, channel, 1, 3)
                        self.vthr_matrix[T, channel] = 0
                    if self.vthr_matrix[T, channel] > 63:
                        self.vthr_matrix[T, channel] = 63

                if doing_tuning_matrix[channel] == 0 and (autotune_scan_matrix[T, channel] > desired_rate * (15) or autotune_scan_matrix[T, channel] < desired_rate * (0.06)):
                    doing_tuning_matrix[channel] = 1

                self.GEM_COM.Load_VTH_fromMatrix(self.c_inst, T, self.vthr_matrix)
            pipe_out.send(T*iter+iter)
            if print_to_screen:
                print(" \n Scan matrix GEMROC {} TIGER {}".format(self.GEMROC_ID,T))
                print autotune_scan_matrix[T, :]
                print(" \n Threshold matrix GEMROC {} TIGER {}".format(self.GEMROC_ID,T))
                print(self.vthr_matrix[T, :])
                # self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, self.GEMROC_ID, T, 64, 1, 3)
        # for T in range (first_TIGER_to_SCAN,last_TIGER_to_scan):


        name = "." + sep + "log_folder" + sep + "THR_LOG{}_GEMROC{}_TIGER_{}_autotuned.txt".format(
            datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"), self.GEMROC_ID, T)
        np.savetxt(name, np.c_[self.vthr_matrix[T, :]])
        name = "." + sep + "conf" + sep +"thr" +sep+"GEMROC{}_TIGER_{}_autotuned.thr".format(self.GEMROC_ID, T)
        np.savetxt(name, np.c_[self.vthr_matrix[T, :]])

        X = "Autotune done"
    def thr_conf_using_GEMROC_COUNTERS_progress_bar(self, test_r, first_TIGER_to_SCAN, last_TIGER_to_SCAN, pipe_out, print_to_screen=True, branch=1):
        with open(self.log_path, 'a') as log_file:
            log_file.write("{} -- Starting thr scan\n".format(time.ctime()))
        thr_scan_matrix=np.zeros((8,64,64))
        # self.GEM_COM.sfo
        if branch == 1:
            self.GEM_COM.set_sampleandhold_mode(self.c_inst)
            self.GEM_COM.double_enable(0, self.c_inst)
        else:
            self.GEM_COM.set_sampleandhold_mode(self.c_inst)
            self.GEM_COM.only_E(self.c_inst)
            # print "E mode"
            # print self.c_inst.Channel_cfg_list

        for T in range(first_TIGER_to_SCAN, last_TIGER_to_SCAN):


            self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, 64, 1, 3)
            self.GEM_COM.DAQ_set(0, 0, 0, 0, 1, 1)

            for j in range (0,64):  #Channel cycle
                self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, j, 1, 0)
                for i in range(0,64):#VTH Cycle, i)
                        # with open(self.log_path, 'a') as log_file:
                        if branch==1:
                            self.GEM_COM.Set_Vth_T1(self.c_inst, T, j, i)
                        else:
                            self.GEM_COM.Set_param_dict_channel(self.c_inst, "Vth_T2", T, j, i)
                        # with open(self.log_path, 'a') as log_file:
                        #     log_file.write("@@@@@@   {} -- Set Vth={} on channel {} \n".format(time.ctime(),i,j))
                        self.GEM_COM.set_counter(T, 0, j)
                        self.GEM_COM.SynchReset_to_TgtFEB(0, 1)
                        #self.GEM_COM.SynchReset_to_TgtTCAM(0, 1)
                        self.GEM_COM.reset_counter()
                        time.sleep(0.03)
                        thr_scan_matrix[T, j, i] = self.GEM_COM.GEMROC_counter_get()
                        # print ("Events: {}".format(thr_scan_matrix[T, j, i]))
                        position=(T*64*64)+(j*64)+(i)
                        pipe_out.send(position)
                        if print_to_screen:
                            os.system('clear')
                            string="SCANNING [TIGER={}, VTh={}, CH={}]\n".format(T,i,j)
                            sys.stdout.write(string)

                self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, j, 1, 3)

        return thr_scan_matrix

    def noise_scan_using_GEMROC_COUNTERS_progress_bar(self, T,j,i, print_to_screen=True,vth2=False):

        self.GEM_COM.Set_param_dict_channel(self.c_inst,"TriggerMode", T, j, 0)
        self.GEM_COM.Set_param_dict_channel(self.c_inst,"TP_disable_FE", T, j, 0)
        if vth2==True:
            self.GEM_COM.Set_param_dict_channel(self.c_inst, "Vth_T2", T, j, i)
        else:
            self.GEM_COM.Set_param_dict_channel(self.c_inst, "Vth_T1", T, j, i)
        self.GEM_COM.set_counter(T, 0, j)
        self.GEM_COM.SynchReset_to_TgtFEB(0, 1)
        # self.GEM_COM.SynchReset_to_TgtTCAM(0, 1)
        # self.GEM_COM.Access_diagn_DPRAM_read_and_log(1,0)
        self.GEM_COM.reset_counter()
        time.sleep(0.1)
        value = self.GEM_COM.GEMROC_counter_get()
        print value
        if print_to_screen:
            os.system('clear')
            string = "SCANNING [TIGER={}, VTh={}, CH={}]\n".format(T, i, j)
            sys.stdout.write(string)

        self.GEM_COM.Set_param_dict_channel(self.c_inst, "TriggerMode", T, j, 3)
        self.GEM_COM.Set_param_dict_channel(self.c_inst,"TP_disable_FE", T, j, 1)

        return value

    def thr_conf_progress_bar(self,test_r, first_TIGER_to_SCAN, last_TIGER_to_SCAN,pipe_out,print_to_screen=True):
        # with open(self.log_path, 'a') as log_file:
        #     log_file.write("{} -- Starting thr scan\n".format(time.ctime()))
        thr_scan_matrix=np.zeros((8,64,64))
        for T in range(first_TIGER_to_SCAN, last_TIGER_to_SCAN):
            # self.GEM_COM.sfo
            self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, 64, 1, 3)
            self.GEM_COM.DAQ_set(2 ** T, 0, 0, 0, 1, 0)

            for j in range (0,64):  #Channel cycle
                self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, j, 1, 0)
                for i in range(0,64):#VTH Cycle, i)
                        # with open(self.log_path, 'a') as log_file:
                        command_sent = self.GEM_COM.Set_Vth_T1(self.c_inst, T, j, i)
                        word_count=0
                        self.GEM_COM.SynchReset_to_TgtFEB(0, 1)
                        self.GEM_COM.SynchReset_to_TgtTCAM(0, 1)
                        test_r.start_socket()
                        while word_count < 60:
                            # print word_count
                            try:
                                word_count = test_r.data_save_thr_scan(j, i, T, word_count, save_binout=False, save_txt=False)
                            # print "after word count {}".format(word_count)
                            except:
                                with open(self.log_path, 'a') as log_file:
                                    log_file.write("{} -- Timed out \n".format(time.ctime(), i, j))
                                    print ("\nTIMED OUT\n")
                                    time.sleep(0.1)
                                    break
                        test_r.dataSock.close()
                        position=(T*64*64)+(j*64)+(i)
                        pipe_out.send(position)
                        if print_to_screen:
                            os.system('clear')
                            string="SCANNING [TIGER={}, VTh={}, CH={}]\n".format(T,i,j)
                            sys.stdout.write(string)

                self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, j, 1, 3)
        thr_scan_matrix=test_r.thr_scan_matrix

        return thr_scan_matrix
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

        file_p = self.GEM_COM.conf_folder + sep +"thr"+sep+ "GEMROC{}_Chip{}.thr".format(self.GEMROC_ID,tiger_id)
        thr0 = np.loadtxt(file_p, )
        thr = np.rint(thr0[:, 0]) - np.rint(thr0[:, 1]) * number_sigma + offset
        for c in range(0, 64):
            if thr[c] < 0 or thr[c] == 0:
                thr[c] = 0
            if thr[c] > 63:
                thr[c] = 63
        self.vthr_matrix[tiger_id, :] = thr
        return 0

    # def thr_autotune(self, T, desired_rate, test_r, max_iter=20,final_lowering=True):
    #     frameMax = 50
    #     frame_count = 0
    #     self.GEM_COM.SynchReset_to_TgtFEB(self.GEM_COM.gemroc_DAQ_XX, 0, 1)
    #     self.GEM_COM.SynchReset_to_TgtTCAM(self.GEM_COM.gemroc_DAQ_XX, 0, 1)
    #
    #     self.GEM_COM.DAQ_set(self.GEM_COM.gemroc_DAQ_XX, 2 ** T, 0x0, 0, 0, 1, 0)
    #
    #     for iter in range(0, max_iter):
    #         print("\nIteration {}".format(iter))
    #         autotune_scan_matrix = np.zeros((8, 64))
    #         # for T in range (first_TIGER_to_SCAN,last_TIGER_to_scan):
    #         # self.GEM_COM.DAQ_set(self.GEM_COM.gemroc_DAQ_XX, self.GEMROC_ID, 2 ** T, 0x0, 0, 0, 1, 0)
    #         self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, 64, 1, 0)
    #         self.GEM_COM.Load_VTH_fromMatrix(self.c_inst, T, self.vthr_matrix)
    #         test_r.start_socket()
    #         while frame_count < frameMax and not self.timedOut:
    #             frame_count, autotune_scan_matrix = self.acquire_rate(frame_count, autotune_scan_matrix,test_r)
    #         test_r.dataSock.close()
    #         if not self.timedOut:
    #             autotune_scan_matrix = autotune_scan_matrix / frame_count * (1 / 0.0002048)
    #
    #             for channel in range(0, 64):
    #                 # if autotune_scan_matrix[T,channel]<(desired_rate-desired_rate/5) or autotune_scan_matrix[T,channel]>(desired_rate+desired_rate/5):
    #                 #     if autotune_scan_matrix[T,channel]<(desired_rate/1000):
    #                 #         self.vthr_matrix[T,channel]=self.vthr_matrix[T,channel]+2
    #                 #     if autotune_scan_matrix[T,channel]>(desired_rate*1000):
    #                 #         self.vthr_matrix[T,channel]=self.vthr_matrix[T,channel]-3
    #
    #                 if autotune_scan_matrix[T, channel] < desired_rate:
    #                     self.vthr_matrix[T, channel] = self.vthr_matrix[T, channel] + 1
    #                 if autotune_scan_matrix[T, channel] > desired_rate:
    #                     self.vthr_matrix[T, channel] = self.vthr_matrix[T, channel] - 1
    #
    #                 if self.vthr_matrix[T, channel] <= 0:
    #                     self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, channel, 1, 3)
    #                     self.vthr_matrix[T, channel] = 0
    #                 if self.vthr_matrix[T, channel] > 63:
    #                     self.vthr_matrix[T, channel] = 63
    #
    #                 self.GEM_COM.Load_VTH_fromMatrix(self.c_inst, T, self.vthr_matrix)
    #
    #             print(" \n Scan matrix TIGER {}".format(T))
    #             print autotune_scan_matrix[T, :]
    #             print(" \n Threshold matrix TIGER {}".format(T))
    #             print(self.vthr_matrix[T, :])
    #             self.timedOut = False
    #             frame_count = 0
    def thr_autotune(self, T, desired_rate, test_r, max_iter=16, final_lowering=True):
        frameMax = 104
        frame_count = 0
        self.GEM_COM.SynchReset_to_TgtFEB(0, 1)
        doing_tuning_matrix = np.ones((64))


        for iter in range(0, max_iter):
            print("\nIteration {}".format(iter))
            autotune_scan_matrix = np.zeros((8, 64))
            # for T in range (first_TIGER_to_SCAN,last_TIGER_to_scan):
            # self.GEM_COM.DAQ_set(self.GEM_COM.gemroc_DAQ_XX, self.GEMROC_ID, 2 ** T, 0x0, 0, 0, 1, 0)
            self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, 64, 1, 0)
            self.GEM_COM.Load_VTH_fromMatrix(self.c_inst, T, self.vthr_matrix)
            self.GEM_COM.DAQ_set(2 ** T, 0x0, 0, 0, 1, 0)
            self.GEM_COM.SynchReset_to_TgtTCAM(0, 1)
            test_r.start_socket()
            while frame_count < frameMax and not self.timedOut:
                frame_count, autotune_scan_matrix = self.acquire_rate(frame_count, autotune_scan_matrix, test_r)
            test_r.dataSock.close()
            if not self.timedOut:
                autotune_scan_matrix = autotune_scan_matrix / frame_count * (1 / 0.0002048)

                for channel in range(0, 64):
                    # if autotune_scan_matrix[T,channel]<(desired_rate-desired_rate/5) or autotune_scan_matrix[T,channel]>(desired_rate+desired_rate/5):
                    #     if autotune_scan_matrix[T,channel]<(desired_rate/1000):
                    #         self.vthr_matrix[T,channel]=self.vthr_matrix[T,channel]+2
                    #     if autotune_scan_matrix[T,channel]>(desired_rate*1000):
                    #         self.vthr_matrix[T,channel]=self.vthr_matrix[T,channel]-3
                    if autotune_scan_matrix[T, channel] < desired_rate*(1.5) and autotune_scan_matrix[T, channel] > desired_rate*(0.5):
                        doing_tuning_matrix[channel]=0

                    if doing_tuning_matrix[channel] ==1:
                        if autotune_scan_matrix[T, channel] < desired_rate:
                            self.vthr_matrix[T, channel] = self.vthr_matrix[T, channel] + 1
                        if autotune_scan_matrix[T, channel] > desired_rate:
                            self.vthr_matrix[T, channel] = self.vthr_matrix[T, channel] - 1

                        if self.vthr_matrix[T, channel] <= 0:
                            self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, channel, 1, 3)
                            self.vthr_matrix[T, channel] = 0
                        if self.vthr_matrix[T, channel] > 63:
                            self.vthr_matrix[T, channel] = 63


                    if doing_tuning_matrix[channel] ==0 and (autotune_scan_matrix[T, channel] > desired_rate*(15) or autotune_scan_matrix[T, channel] < desired_rate*(0.06)):
                        doing_tuning_matrix[channel] = 1

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
        name = "." + sep + "conf" + sep +"thr"+sep+ "GEMROC{}_TIGER_{}_autotuned.thr".format(self.GEMROC_ID, T)
        np.savetxt(name, np.c_[self.vthr_matrix[T, :]])

        X = "Autotune done"
        print (X)

    def thr_autotune_wth_counter(self, T, desired_rate, test_r, max_iter=16, tempo=0.2):
        self.GEM_COM.SynchReset_to_TgtFEB(0, 1)
        doing_tuning_matrix = np.ones((64))

        for iter in range(0, max_iter):
            print("\nIteration {}".format(iter))
            autotune_scan_matrix = np.zeros((8, 64))
            # for T in range (first_TIGER_to_SCAN,last_TIGER_to_scan):
            # self.GEM_COM.DAQ_set(self.GEM_COM.gemroc_DAQ_XX, self.GEMROC_ID, 2 ** T, 0x0, 0, 0, 1, 0)
            self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, 64, 1, 0)
            self.GEM_COM.Load_VTH_fromMatrix(self.c_inst, T, self.vthr_matrix)
            self.GEM_COM.DAQ_set(2 ** T, 0x0, 0, 0, 1, 0)
            self.GEM_COM.SynchReset_to_TgtTCAM(0, 1)
            for j in range (0,64):
                self.GEM_COM.set_counter(T, 0, j)
                self.GEM_COM.SynchReset_to_TgtFEB(0, 1)
                self.GEM_COM.SynchReset_to_TgtTCAM(0, 1)
                self.GEM_COM.reset_counter()
                time.sleep(tempo)
                autotune_scan_matrix[T,j]=self.GEM_COM.GEMROC_counter_get()


            autotune_scan_matrix = autotune_scan_matrix*(1/tempo)

            for channel in range(0, 64):
                # if autotune_scan_matrix[T,channel]<(desired_rate-desired_rate/5) or autotune_scan_matrix[T,channel]>(desired_rate+desired_rate/5):
                #     if autotune_scan_matrix[T,channel]<(desired_rate/1000):
                #         self.vthr_matrix[T,channel]=self.vthr_matrix[T,channel]+2
                #     if autotune_scan_matrix[T,channel]>(desired_rate*1000):
                #         self.vthr_matrix[T,channel]=self.vthr_matrix[T,channel]-3
                if autotune_scan_matrix[T, channel] < desired_rate * (1.5) and autotune_scan_matrix[T, channel] > desired_rate * (0.5):
                    doing_tuning_matrix[channel] = 0

                if doing_tuning_matrix[channel] == 1:
                    if autotune_scan_matrix[T, channel] < desired_rate:
                        self.vthr_matrix[T, channel] = self.vthr_matrix[T, channel] + 1
                    if autotune_scan_matrix[T, channel] > desired_rate:
                        self.vthr_matrix[T, channel] = self.vthr_matrix[T, channel] - 1

                    if self.vthr_matrix[T, channel] <= 0:
                        self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, T, channel, 1, 3)
                        self.vthr_matrix[T, channel] = 0
                    if self.vthr_matrix[T, channel] > 63:
                        self.vthr_matrix[T, channel] = 63

                if doing_tuning_matrix[channel] == 0 and (autotune_scan_matrix[T, channel] > desired_rate * (15) or autotune_scan_matrix[T, channel] < desired_rate * (0.06)):
                    doing_tuning_matrix[channel] = 1

                self.GEM_COM.Load_VTH_fromMatrix(self.c_inst, T, self.vthr_matrix)

            print(" \n Scan matrix TIGER {}".format(T))
            print autotune_scan_matrix[T, :]
            print(" \n Threshold matrix TIGER {}".format(T))
            print(self.vthr_matrix[T, :])
                # self.GEM_COM.Set_GEMROC_TIGER_ch_TPEn(self.c_inst, self.GEMROC_ID, T, 64, 1, 3)
        # for T in range (first_TIGER_to_SCAN,last_TIGER_to_scan):


        name = "." + sep + "log_folder" + sep + "THR_LOG{}_GEMROC{}_TIGER_{}_autotuned.txt".format(
            datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"), self.GEMROC_ID, T)
        np.savetxt(name, np.c_[self.vthr_matrix[T, :]])
        name = "." + sep + "conf" + sep +"thr" +sep+ "GEMROC{}_TIGER_{}_autotuned.thr".format(self.GEMROC_ID, T)
        np.savetxt(name, np.c_[self.vthr_matrix[T, :]])

        X = "Autotune done"
        print (X)
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

        self.GEM_COM.SynchReset_to_TgtFEB(0, 1)
        self.check_sync()
    def TIGER_delay_tuning(self):
        for T in range (0,8):
            self.GEM_COM.Set_param_dict_global(self.g_inst, "FE_TPEnable",T,0)
            for ch in range (0,64):
                self.GEM_COM.Set_param_dict_channel(self.c_inst, "TP_disable_FE", T, ch, 1)
                self.GEM_COM.Set_param_dict_channel(self.c_inst,"TriggerMode",T,ch,1)

        error_matrix = np.zeros((8,64))
        delay_vector = np.zeros((64))
        safe_delays =np.zeros((4)) #Best dealy for each FEB

        for TD in range (0,64):
            print ("Setting delay {}".format(TD))
            self.GEM_COM.set_FEB_timing_delays(TD, TD, TD, TD)
            self.GEM_COM.DAQ_set(0, 0xff, 1, 256, 1, 1, False)
            self.GEM_COM.SynchReset_to_TgtTCAM(0, 1)
            for Ts in range(0, 4):
                self.GEM_COM.SynchReset_to_TgtFEB(0, 1)
                self.GEM_COM.set_counter((Ts * 2), 1, 0)
                self.GEM_COM.reset_counter()
                time.sleep(0.2)
                counter1=self.GEM_COM.GEMROC_counter_get()
                self.GEM_COM.SynchReset_to_TgtFEB(0, 1)
                self.GEM_COM.set_counter((Ts * 2+1), 1, 0)
                self.GEM_COM.reset_counter()
                time.sleep(0.2)
                counter2=self.GEM_COM.GEMROC_counter_get()

                error_matrix[Ts * 2,TD]=counter1
                error_matrix[Ts*2 +1,TD]=counter2

        for i in range (0,64):
            delay_vector[i]=88*i

        for Ts in range(0, 4):
            first_zero=65
            second_zero=65
            Searching_first_zero=True
            Searching_second_zero=False

            for delay in range (0,64): #Searching for the zero error interval
                total_error=error_matrix[Ts * 2,delay]+error_matrix[Ts * 2+1,delay]
                if total_error== 0 and Searching_first_zero:
                    first_zero=delay
                    Searching_first_zero=False
                    Searching_second_zero=True
                if total_error != 0 and Searching_second_zero:
                    second_zero = delay-1
                    Searching_second_zero=False
                if total_error ==0 and not Searching_second_zero and not Searching_first_zero:
                    first_zero=delay

            print ("First zero {} second zero {}\n".format(first_zero,second_zero))
            if first_zero==second_zero: #Same zero, not stable (or not sero at all)
                print("\nWarning! Can't fine a stable communication delay for FEB {}!".format(Ts))
            if first_zero>second_zero:
                second_zero=second_zero+64

            safe_delays[Ts]=(second_zero+first_zero)/2
            if safe_delays[Ts]>63:
                safe_delays[Ts]=safe_delays[Ts]-64
        # if not direct_plot:
        for Ts in range (0,4):
            plt.plot(delay_vector[:],error_matrix[Ts*2,:], 'b-', label='TIGER {}'.format(Ts*2))
            plt.plot(delay_vector[:],error_matrix[Ts*2 + 1,:], 'g-',label='TIGER {}'.format(Ts*2+1))
            plt.axvline(x=safe_delays[Ts]*88,color='r',label="Time delay set at {}".format(safe_delays[Ts]))
            plt.legend(loc='best')
            plt.ylabel('Errors')
            plt.xlabel('Communication delay [ps] ')
            plt.title('Delay scan, GEMROC {} FEB {}'.format(self.GEM_COM.GEMROC_ID, Ts))
            plt.savefig(self.GEM_COM.conf_folder+sep+"TD_scan_results"+sep+"GEMROC_{}_TD_scan_FEB_{}.png".format(self.GEM_COM.GEMROC_ID,Ts))
            plt.clf()
        # else:
        #     return safe_delays
        #     self.plot_with_pooling(delay_vector,error_matrix,safe_delays)
        for i in range(0, 4):
            safe_delays[i]=int(safe_delays[i]//1)

        for T in range (0,8):
            self.GEM_COM.Set_param_dict_global(self.g_inst, "FE_TPEnable",T,0)
            for ch in range (0,64):
                self.GEM_COM.Set_param_dict_channel(self.c_inst, "TP_disable_FE", T, ch, 0)
                self.GEM_COM.Set_param_dict_channel(self.c_inst,"TriggerMode",T,ch,3)
        return safe_delays

    def plot_with_pooling(self,delay_vector,error_matrix,safe_delays):
        pool = multiprocessing.Pool()
        error_matrix_list=[]
        delay_vector_list=[]
        safe_delays_list=[]
        for i in range (0,4):
            error_matrix_list.append(error_matrix)
            delay_vector_list.append(delay_vector)
            safe_delays_list.append(safe_delays)
        input = zip( [0,1,2,3],error_matrix_list,delay_vector_list,safe_delays_list)
        pool.map(self.plot_for_multiproc, input)

    def plot_for_multiproc(self,args):
        Ts, delay_vector,error_matrix,safe_delays = args
        fig = plt.figure()
        plt.plot(delay_vector[:], error_matrix[Ts * 2, :], 'b-', label='TIGER {}'.format(Ts * 2))
        plt.plot(delay_vector[:], error_matrix[Ts * 2 + 1, :], 'g-', label='TIGER {}'.format(Ts * 2 + 1))
        plt.axvline(x=safe_delays[Ts] * 88, color='r', label="Time delay set at {}".format(safe_delays[Ts]))
        plt.legend(loc='best')
        plt.ylabel('Errors')
        plt.xlabel('Communication delay [ps] ')
        plt.title('Delay scan, GEMROC {} FEB {}'.format(self.GEM_COM.GEMROC_ID, Ts))
        plt.savefig(self.GEM_COM.conf_folder + sep + "TD_scan_results" + sep + "GEMROC_{}_TD_scan_FEB_{}.png".format(self.GEM_COM.GEMROC_ID, Ts))
        plt.clf()

    def __del__(self):
        return 0
class analisys_read:
    def __init__(self, com, c_inst,rate=0):
        self.TP_rate=rate
        self.c_inst=c_inst
        self.GEM_COM=com
        self.GEMROC_ID=self.GEM_COM.GEMROC_ID
        self.data_path = com.Tscan_folder+sep+'thr_scan_dump_data.txt'
        f=open(self.data_path,'w')
        f.close()
        self.bindata_path = com.Tscan_folder+sep+'thr_scan_dump_BIN.dat'
        f=open(self.bindata_path,'w')
        f.close()
        self.scan_path_T = com.Tscan_folder + sep + "Scan_{}.txt".format(self.GEMROC_ID)
        self.scan_path_E = com.Escan_folder+sep+"Scan_{}.txt".format(self.GEMROC_ID)

        self.HOST_IP = self.GEM_COM.HOST_IP
        self.HOST_PORT = 58880 + self.GEMROC_ID
        self.thr_scan_matrix=np.zeros((8,64,64))#Tiger,Channel,Threshold
        self.thr_scan_frames=np.ones((8,64,64))
        self.vthr_matrix=np.ones((8,64))
        self.thr_scan_rate = np.zeros((8, 64, 64))
        self.thr_scan_rate_norm = np.zeros((8, 64, 64))
        self.thresholds = np.zeros((8, 64, 2))

    def start_socket(self):
        self.dataSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dataSock.settimeout(0.1)
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

    def acquire_Efine (self, ch, TIG, run_time):
        self.start_socket()
        start_time=time.time()
        efine=[]
        while True:
            data, addr = self.dataSock.recvfrom(BUFSIZE)
            hexdata = binascii.hexlify(data)
            for x in range(0, len(hexdata) - 1, 16):
                int_x = 0
                for b in range(7, 0, -1):
                    hex_to_int = (int(hexdata[x + b * 2], 16)) * 16 + int(hexdata[x + b * 2 + 1], 16)
                    int_x = (int_x + hex_to_int) << 8
                hex_to_int = (int(hexdata[x], 16)) * 16 + int(hexdata[x + 1], 16)  # acr 2017-11-17 this should fix the problem
                int_x = (int_x + hex_to_int)

                if (((int_x & 0xFF00000000000000) >> 59) == 0x00):
                    s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'EW: ' + 'ChID: %02X ' % (
                            (int_x >> 48) & 0x3F) + 'tacID: %01X ' % ((int_x >> 46) & 0x3) + 'Tcoarse: %04X ' % (
                                (int_x >> 30) & 0xFFFF) + 'Ecoarse: %03X ' % (
                                (int_x >> 20) & 0x3FF) + 'Tfine: %03X ' % ((int_x >> 10) & 0x3FF) + 'Efine: %03X \n' % (
                                int_x & 0x3FF)
                    if ((ch & 0x3F)==(int(int_x >> 48) & 0x3F) and (TIG == (int_x >> 56) & 0x7)):
                        efine.append(int(int_x & 0x3FF))
                raw = "{}".format(bin((int_x & 0xFFFFFFFFFFFFFFFF)))

                if (((int_x & 0xFF00000000000000) >> 59) == 0x04):  # It's a frameword
                    s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'HB: ' + 'Framecount: %08X ' % (
                            (int_x >> 15) & 0xFFFF) + 'SEUcount: %08X\n' % (int_x & 0x7FFF)

                if (((int_x & 0xFF00000000000000) >> 59) == 0x08):
                    s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'CW: ' + 'ChID: %02X ' % (
                            (int_x >> 24) & 0x3F) + ' CounterWord: %016X\n' % (int_x & 0x00FFFFFF)
                if (((int_x & 0xFF00000000000000) >> 59) == 0x00):
                    s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'EW: ' + 'ChID: %02X ' % (
                            (int_x >> 48) & 0x3F) + 'tacID: %01X ' % ((int_x >> 46) & 0x3) + 'Tcoarse: %04X ' % (
                                (int_x >> 30) & 0xFFFF) + 'Ecoarse: %03X ' % (
                                (int_x >> 20) & 0x3FF) + 'Tfine: %03X ' % ((int_x >> 10) & 0x3FF) + 'Efine: %03X \n' % (
                                int_x & 0x3FF)
                # print "RAW: {}".format(raw)
                # print "Data: {}".format(s)

            if (time.time()-start_time) >run_time:
                break
        average=np.mean(efine)
        sigma=np.std(efine)
        total=len(efine)
        self.dataSock.close()
        print (average, sigma,total)
        return (average,sigma,total)

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

    def save_scan_on_file(self,branch=1):
        if branch==1:
            f = open(self.scan_path_T, 'w')
        else:
            f = open(self.scan_path_E, 'w')

        for T in range(0, 8):
            f.write("Tiger {}".format(T))
            f.write("Frames\n")
            for i in range(0, 64):
                f.write("\nChannel {}\n".format(i))

                for j in range (0,64):
                    if self.thr_scan_frames[T, i, j]:
                        f.write("{},".format(self.thr_scan_frames[T, i, j]))
                    else:
                        f.write("0,")

            f.write("\nEvents\n")
            for i in range(0, 64):
                f.write("\nChannel {}\n".format(i))

                for j in range (0,64):
                    if self.thr_scan_frames[T, i, j]:
                        f.write("{},".format(self.thr_scan_matrix[T, i, j]))
                    else:
                        f.write("0,")
            f.write("\n")

        f.close()

    def make_rate(self):
        self.thr_scan_rate = self.thr_scan_matrix / self.thr_scan_frames

    def colorPlot(self, file_name, first_TIGER_to_SCAN,last_TIGER_to_scan, rate=False):
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

    def normalize_rate(self,first_TIGER_to_SCAN,last_TIGER_to_scan):
        for T in range(first_TIGER_to_SCAN, last_TIGER_to_scan):
            for z in range(0, 64):
                max = np.max(self.thr_scan_rate[T, z, :])
                self.thr_scan_rate_norm[T, z, :] = self.thr_scan_rate[T, z, :] / max
                # for i in range (0,64):
                #     if self.thr_scan_rate[T,z,i]==1:
                #         for j in range (i,64):
                #             if self.thr_scan_rate[T, z, j] <0.9: #Force to 1 all the values after the max, necessary for convergence
                #                 self.thr_scan_rate[T, z, j]=1

    # def global_sfit_noise(self, scan_matrix):
    #     TP_rate=10000 #Set accordingly with the test pulse generator
    #
    #     self.close()

    def global_sfit(self,first_TIGER_to_SCAN, last_TIGER_to_scan, retry=False,branch=1):
        for T in range(first_TIGER_to_SCAN, last_TIGER_to_scan):
            if branch==1:
                thr_file_path = self.GEM_COM.conf_folder + sep +"thr"+sep+"GEMROC{}_Chip{}_T.thr".format(self.GEMROC_ID, T)
            else:
                thr_file_path = self.GEM_COM.conf_folder + sep +"thr"+sep+"GEMROC{}_Chip{}_E.thr".format(self.GEMROC_ID, T)

            f = open(thr_file_path, 'w')
            f.close()
            for ch in range(0, 64):
                try:
                    # (x,k)=self.sfit(self.thr_scan_rate[T,i,:])
                    (x, k, c) = self.errfit_thr(self.thr_scan_rate_norm[T, ch, :], T, ch,branch )
                except:
                    if retry:
                        pass
                        # print("Not converged, launching VTH scan on channel\n")
                        #
                        # try:
                        #     (x, k) = self.sfit(self.thr_scan_rate[T, ch, :])
                        #     # (x, k) = self.errfit(self.thr_scan_rate[T, i, :])
                        # except:
                        #     print ("Can't converge \n")
                        #     (x, k) = (0, 0)



                    else:

                        (x, k) = (np.argmax (self.thr_scan_rate[T, ch, :]>1000), 1)
                        print ("Can't fit ch {}, TIGER {}, set: mu  {} and sigma {}".format(ch, T,x,k))
                        # xdata = np.arange(0, 64)
                        # plt.plot(xdata, self.thr_scan_rate_norm[T, ch, :], 'o', label='Data')
                        # plt.ylim(0, 1.05)
                        # plt.legend(loc='best')
                        # plt.title("TIGER_{}_channel {}".format(T, ch))
                        # if branch == 1:
                        #     plt.savefig(self.GEM_COM.Tscan_folder + sep + "GEMROC{}".format(self.GEMROC_ID) + sep + "channel_fits" + sep + "TIGER_{}_channel {}.png".format(T, ch))
                        # else:
                        #     plt.savefig(self.GEM_COM.Escan_folder + sep + "GEMROC{}".format(self.GEMROC_ID) + sep + "channel_fits" + sep + "TIGER_{}_channel {}.png".format(T, ch))
                        # plt.clf()

            if x<0 or x>64:
                (x, k) = (np.argmax(self.thr_scan_rate[T, ch, :] > 1000), 1)
                print ("Invalid value on ch {}, TIGER {}, set: mu  {} and sigma {}".format(ch, T, x, k))
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

                #print("\n CHANNEL ={} x={} k={}".format(ch, x, k))

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
            plt.plot(xdata, ydata, 'o', label='data')
            plt.plot(x, y, label='fit')
            plt.ylim(0, 1.05)
            plt.legend(loc='best')
            plt.show()
        return popt

    def errfit_thr(self, ydata, Tiger, Channel, branch=1):
        showplot = True
        max_reach=0
        ydataorg=[]
        ydataorg[:]=ydata[:]
        # ydata = ydata
        for i, ytest in enumerate(ydata):
            if ytest ==1:
                max_reach=1
            if max_reach==1:
                ydata[i]=1

        xdata = np.arange(0, 64)
        try:
            popt, pcov = curve_fit(errorfunc, xdata, ydata, p0=(32,2,1),method='lm', maxfev=5000)
        except:
            if showplot:
                xdata = np.arange(0, 64)
                plt.plot(xdata, ydataorg, 'o', label='Original data', color='r')
                plt.plot(xdata, ydata, 'x', label='Data')
                plt.ylim(0, 1.05)
                plt.legend(loc='best')
                plt.title("TIGER_{}_channel {}".format(Tiger, Channel))
                if branch==1:
                    plt.savefig(self.GEM_COM.Tscan_folder + sep + "GEMROC{}".format(self.GEMROC_ID) + sep + "channel_fits" + sep + "TIGER_{}_channel {}.png".format(Tiger, Channel))
                else:
                    plt.savefig(self.GEM_COM.Escan_folder + sep + "GEMROC{}".format(self.GEMROC_ID) + sep + "channel_fits" + sep + "TIGER_{}_channel {}.png".format(Tiger, Channel))
                plt.clf()
            pass

        print "GEMROC {} TIGER {}, ch {}, fit: {}".format(self.GEMROC_ID,Tiger,Channel,popt)

        x = np.arange(0, 64)
        y = errorfunc(x, *popt)

        if showplot:
            xdata = np.arange(0, 64)
            plt.plot(xdata, ydataorg, 'o', label='original data',color='r')
            plt.plot(xdata, ydata, 'x', label='data')
            plt.plot(x, y, label='fit')
            plt.ylim(0, 1.05)
            plt.legend(loc='best')
            plt.title("TIGER_{}_channel {}".format(Tiger,Channel))
            if branch == 1:
                plt.savefig(self.GEM_COM.Tscan_folder + sep + "GEMROC{}".format(self.GEMROC_ID) + sep + "channel_fits" + sep + "TIGER_{}_channel {}.png".format(Tiger, Channel))
            else:
                plt.savefig(self.GEM_COM.Escan_folder + sep + "GEMROC{}".format(self.GEMROC_ID) + sep + "channel_fits" + sep + "TIGER_{}_channel {}.png".format(Tiger, Channel))
            plt.clf()
        return (popt)

    def errfit_noise(self, ydata, showplot=True):
        showplot = True
        # ydata = ydata
        for i, ytest in enumerate(ydata):
            if ytest> self.TP_rate*1.2:
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

            plt.plot(xdata, ydata, 'o', label='data')
            plt.plot(x, y, label='fit')
            plt.ylim(0, 1.05)
            plt.legend(loc='best')
            plt.show()
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
