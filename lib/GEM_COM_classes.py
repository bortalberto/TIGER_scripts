# file: Cfg_GEMROC_TIGER.py
# author: Angelo Cotta Ramusino INFN Ferrara
# date: 15 Jan 2018
# last mod: 03 Mar 2018
# purpose: to debug TIGER configuration and data acquisition through the GEMROC prototype
# last modifications / additions
# acr 2018-01-15 modified "GEMconf_classes" to split LV parameter control from DAQ parameter control
# acr 2017-07-11 modified "GEMconf_classes" to read single TIGER global / channel configuration from files
import socket
import time
import GEM_CONF_classes as GEM_CONF_classes  # acr 2018-02-19 import GEMconf_classes_2018
import struct
import binascii
import array
import classes_test_functions
import numpy as np
import datetime
import sys


OS = sys.platform
if OS == 'win32':
	sep = '\\'
elif OS == 'linux2':
	sep = '/'
else:
	print("ERROR: OS {} non compatible".format(OS))
	sys.exit()


class communication: ##The directory are declared here to avoid multiple declaration

    def __init__(self,gemroc_ID,feb_pwr_pattern):
        self.conf_folder = "conf"
        self.Tscan_folder="thr_scan"
        self.GEMROC_ID=gemroc_ID
        self.FEB_PWR_EN_pattern=feb_pwr_pattern
        log_fname = "."+sep+"log_folder"+sep+"GEMROC{}_interactive_cfg_log_{}.txt".format(self.GEMROC_ID,datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        self.log_file = open(log_fname, 'w')
        IVT_log_fname = "."+sep+"log_folder"+sep+"GEMROC{}_IVT_log_{}.txt".format(self.GEMROC_ID,datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        self.IVT_log_file = open(IVT_log_fname, 'w')

        local_test=True

        if local_test==True:
            # HOST_DYNAMIC_IP_ADDRESS = "192.168.1.%d" %(GEMROC_ID)
            self.HOST_IP = "127.0.0.1"  # uncomment for test only

            self.HOST_PORT = 54816 + 1 + self.GEMROC_ID
            self.HOST_PORT_RECEIVE = 52816 + 1 + self.GEMROC_ID

            # DEST_IP_ADDRESS = "192.168.1.%d" %(GEMROC_ID+16) # offset 16 is determined by Stefano's MAC
            # DEST_PORT_NO = 58912+1 # STEFANO CHIOZZI - 2018-03-08 offset 0 is reserved by the MAC for a custom protocol; offset 3 is also a special debug port
            self.DEST_IP_ADDRESS = "127.0.0.1"
            self.DEST_PORT_NO = 52816 + 1 + self.GEMROC_ID
        else:
            self.HOST_IP = "192.168.1.200"
            self.HOST_PORT = 54816 + 1 + self.GEMROC_ID #Port from where send to the gemroc
            self.HOST_PORT_RECEIVE = 58912 + 1 + self.GEMROC_ID #Port where listen to configuration answer

            # DEST_IP_ADDRESS = "192.168.1.%d" %(GEMROC_ID+16) # offset 16 is determined by Stefano's MAC
            # DEST_PORT_NO = 58912+1 # STEFANO CHIOZZI - 2018-03-08 offset 0 is reserved by the MAC for a custom protocol; offset 3 is also a special debug port
            self.DEST_IP_ADDRESS = "192.168.1.%d" %(self.GEMROC_ID+16)
            self.DEST_PORT_NO = 58912+1 #Port where send the configuration

        self.tiger_index = 0
        self.BUFSIZE = 4096

        self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clientSock.bind((self.HOST_IP, self.HOST_PORT))


        self.receiveSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiveSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.receiveSock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 106496 )
        self.receiveSock.settimeout(4)

        self.receiveSock.bind((self.HOST_IP, self.HOST_PORT_RECEIVE))
        self.remote_IP_Address = '192.168.1.%d' % (self.GEMROC_ID + 16)
        ##receiveSock.connect( (remote_IP_Address, 54817,) )
        ##print '\nnew socket handling'

        ## creating an instance of the GEMROC LV configuration settings object
        ## parameter list:
        ##  TARGET_GEMROC_ID_param = 0, # acr 2017-09-22
        ##  command_string_param = 'NONE',
        ##  number_of_repetitions_param = 1,
        cfg_filename =self.conf_folder+sep+ 'GEMROC_%d_def_cfg_LV_2018.txt' % self.GEMROC_ID
        self.gemroc_LV_XX = GEM_CONF_classes.gemroc_cmd_LV_settings(self.GEMROC_ID, 'NONE', 1, cfg_filename)
        self.gemroc_LV_XX.set_FEB_PWR_EN_pattern(self.FEB_PWR_EN_pattern)
        COMMAND_STRING = 'CMD_GEMROC_LV_CFG_WR'
        self.gemroc_LV_XX.set_gemroc_cmd_code(COMMAND_STRING, 1)
        self.gemroc_LV_XX.update_command_words()
        # keep gemroc_LV_XX.print_command_words()
        # keep gemroc_LV_XX.extract_parameters_from_UDP_packet()
        array_to_send = self.gemroc_LV_XX.command_words


        command_echo = self.send_GEMROC_CFG_CMD_PKT(self.GEMROC_ID, COMMAND_STRING, array_to_send, self.DEST_IP_ADDRESS, self.DEST_PORT_NO)
        ##print 'CMD_GEMROC_LV_CFG_WR'

        ## creating an instance of the GEMROC DAQ configuration settings object
        ## parameter list:
        ##  TARGET_GEMROC_ID_param = 0, # acr 2017-09-22
        ##  command_string_param = 'NONE',
        ##  TCAM_ID_param = 1,
        ##  number_of_repetitions_param = 1,
        ##  to_ALL_TCAM_enable_param = 0,

        cfg_filename =self.conf_folder+sep+ 'GEMROC_%d_def_cfg_DAQ_2018v5.txt' % self.GEMROC_ID
        self.gemroc_DAQ_XX = GEM_CONF_classes.gemroc_cmd_DAQ_settings(self.GEMROC_ID, 'NONE', 0, 1, 0, cfg_filename)



        ##acr 2018-03-16 added yesterday while debugging DAQ_CFG readback, removed today: gemroc_DAQ_XX.extract_parameters_from_UDP_packet()
        COMMAND_STRING = 'CMD_GEMROC_DAQ_CFG_WR'
        command_echo = self.send_GEMROC_DAQ_CMD(self.GEMROC_ID, self.gemroc_DAQ_XX, COMMAND_STRING)
        self.enable_pattern_array = array.array('I', [0x0, 0x1, 0x3, 0x7, 0xf, 0x1f, 0x3f, 0x7f, 0xff])  # acr 2018-08-08
        # self.enable_pattern_array_test = array.array('I',[0x0, 0x3, 0x9, 0xA, 0x41, 0x42, 0x81, 0x82,  0xC0]) #Test 2 Tigers
        self.enable_pattern_array_test = array.array('I', [0x0, 0xc8, 0x4a, 0x0b,  0xca, 0xc3, 0x4b, 0xcb])  # Test 3,4,5 Tigers

    def __del__(self):
        self.log_file.close()
        self.IVT_log_file.close()
    def flush_socket(self):
        self.receiveSock.close()
        self.receiveSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiveSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.receiveSock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 106496 )
        self.receiveSock.settimeout(4)

        self.receiveSock.bind((self.HOST_IP, self.HOST_PORT_RECEIVE))

    def send_GEMROC_CFG_CMD_PKT(self,TARGET_GEMROC_ID_param, COMMAND_STRING_PARAM, array_to_send_param, DEST_IP_ADDRESS_PARAM,
                                DEST_PORT_NO_PARAM):

        buffer_to_send = struct.pack('>' + str(len(array_to_send_param)) + 'L', *array_to_send_param)
        self.flush_socket()
        self.clientSock.sendto(buffer_to_send, (DEST_IP_ADDRESS_PARAM, DEST_PORT_NO_PARAM))
        cmd_message = "\nTarget GEMROC: %d; CMD sent (%s): \n" % (TARGET_GEMROC_ID_param, COMMAND_STRING_PARAM)
        self.log_file.write(cmd_message)
        self.log_file.write(binascii.b2a_hex(buffer_to_send))
        command_echo_f = self.receiveSock.recv(self.BUFSIZE)
        ##    (command_echo_f, source_IPADDR) = receiveSock.recvfrom(BUFSIZE) #S.C. 2018-03-08
        ##    cmd_message = "\nTarget GEMROC: %d; Target GEMROC IP_ADDR_LOWER_BYTE: %s; \nCMD echo (%s): \n" %(TARGET_GEMROC_ID_param, source_IPADDR, COMMAND_STRING_PARAM)
        ##    print (cmd_message)
        ##    time.sleep(5)
        self.log_file.write(cmd_message)
        self.log_file.write(binascii.b2a_hex(command_echo_f))
        return command_echo_f


    ## acr 2018-02-19 BEGIN definining a function to call within the display loop
    def display_and_log_IVT(self,command_echo_param, display_enable_param, log_enable_param,
                            log_filename_param):  ## acr 2018-02-23
        L_array = array.array('I')  # L is an array of unsigned long, I for some systems, L for others
        L_array.fromstring(command_echo_param)
        L_array.byteswap()

        FEB3_T_U = (L_array[1] >> 22) & 0Xff
        FEB2_T_U = (L_array[2] >> 22) & 0Xff
        FEB1_T_U = (L_array[3] >> 22) & 0Xff
        FEB0_T_U = (L_array[4] >> 22) & 0Xff
        FEB3_VD_U = (L_array[1] >> 13) & 0X1ff
        FEB2_VD_U = (L_array[2] >> 13) & 0X1ff
        FEB1_VD_U = (L_array[3] >> 13) & 0X1ff
        FEB0_VD_U = (L_array[4] >> 13) & 0X1ff
        FEB3_ID_U = (L_array[1] >> 4) & 0X1ff
        FEB2_ID_U = (L_array[2] >> 4) & 0X1ff
        FEB1_ID_U = (L_array[3] >> 4) & 0X1ff
        FEB0_ID_U = (L_array[4] >> 4) & 0X1ff
        FEB3_VA_U = (L_array[5] >> 13) & 0X1ff
        FEB2_VA_U = (L_array[6] >> 13) & 0X1ff
        FEB1_VA_U = (L_array[7] >> 13) & 0X1ff
        FEB0_VA_U = (L_array[8] >> 13) & 0X1ff
        FEB3_IA_U = (L_array[5] >> 4) & 0X1ff
        FEB2_IA_U = (L_array[6] >> 4) & 0X1ff
        FEB1_IA_U = (L_array[7] >> 4) & 0X1ff
        FEB0_IA_U = (L_array[8] >> 4) & 0X1ff
        ROC_T_U = (L_array[9] >> 24) & 0X3f
        FEB3_OVT_FLAG = (L_array[1] >> 3) & 0X1
        FEB3_DOVV_FLAG = (L_array[1] >> 2) & 0X1
        FEB3_DOVC_FLAG = (L_array[1] >> 1) & 0X1
        FEB3_AOVV_FLAG = (L_array[5] >> 2) & 0X1
        FEB3_AOVC_FLAG = (L_array[5] >> 1) & 0X1
        FEB2_OVT_FLAG = (L_array[2] >> 3) & 0X1
        FEB2_DOVV_FLAG = (L_array[2] >> 2) & 0X1
        FEB2_DOVC_FLAG = (L_array[2] >> 1) & 0X1
        FEB2_AOVV_FLAG = (L_array[6] >> 2) & 0X1
        FEB2_AOVC_FLAG = (L_array[6] >> 1) & 0X1
        FEB1_OVT_FLAG = (L_array[3] >> 3) & 0X1
        FEB1_DOVV_FLAG = (L_array[3] >> 2) & 0X1
        FEB1_DOVC_FLAG = (L_array[3] >> 1) & 0X1
        FEB1_AOVV_FLAG = (L_array[7] >> 2) & 0X1
        FEB1_AOVC_FLAG = (L_array[7] >> 1) & 0X1
        FEB0_OVT_FLAG = (L_array[4] >> 3) & 0X1
        FEB0_DOVV_FLAG = (L_array[4] >> 2) & 0X1
        FEB0_DOVC_FLAG = (L_array[4] >> 1) & 0X1
        FEB0_AOVV_FLAG = (L_array[8] >> 2) & 0X1
        FEB0_AOVC_FLAG = (L_array[8] >> 1) & 0X1
        ROC_OVT_FLAG = (L_array[9] >> 17) & 0X1  # ACR 2018-03-15
        del L_array
        T_ref_PT1000 = 25.0
        V_ADC_at_25C = 247.2
        ADC_res_mV_1LSB = 0.305
        # acr 2018-03-15 BEGIN increased the sensitivity of temperature measurement and adjusted some parameters
        # T_ADC_data_shift = 3
        T_ADC_data_shift = 2  # acr 2018-03-15 increased the sensitivity
        # acr 2018-03-15 BEGIN increased the sensitivity T_ADC_data_shift = 3
        ##calibration_offset_mV_FEB3 = 4.0
        ##calibration_offset_mV_FEB2 = 4.0
        ##calibration_offset_mV_FEB1 = 4.0
        ##calibration_offset_mV_FEB0 = 4.0
        calibration_offset_mV_FEB3 = 1.0
        calibration_offset_mV_FEB2 = 1.0
        calibration_offset_mV_FEB1 = 1.0
        calibration_offset_mV_FEB0 = 1.0
        # acr 2018-03-15 END increased the sensitivity of temperature measurement and adjusted some parameters
        shifted_T_ADC_res_mV_1LSB = 0.305 * (2 ** T_ADC_data_shift)
        V_ADC_data_shift = 4
        shifted_V_ADC_res_mV_1LSB = 0.305 * (2 ** V_ADC_data_shift)
        deltaT_over_deltaV_ratio = 1.283
        FEB3_T = T_ref_PT1000 + (((
                                              FEB3_T_U * shifted_T_ADC_res_mV_1LSB) + calibration_offset_mV_FEB3 - V_ADC_at_25C) * deltaT_over_deltaV_ratio)
        FEB2_T = T_ref_PT1000 + (((
                                              FEB2_T_U * shifted_T_ADC_res_mV_1LSB) + calibration_offset_mV_FEB2 - V_ADC_at_25C) * deltaT_over_deltaV_ratio)
        FEB1_T = T_ref_PT1000 + (((
                                              FEB1_T_U * shifted_T_ADC_res_mV_1LSB) + calibration_offset_mV_FEB1 - V_ADC_at_25C) * deltaT_over_deltaV_ratio)
        FEB0_T = T_ref_PT1000 + (((
                                              FEB0_T_U * shifted_T_ADC_res_mV_1LSB) + calibration_offset_mV_FEB0 - V_ADC_at_25C) * deltaT_over_deltaV_ratio)
        Vout_atten_factor = 0.5
        FEB3_VD = (FEB3_VD_U * shifted_V_ADC_res_mV_1LSB) / Vout_atten_factor
        FEB2_VD = (FEB2_VD_U * shifted_V_ADC_res_mV_1LSB) / Vout_atten_factor
        FEB1_VD = (FEB1_VD_U * shifted_V_ADC_res_mV_1LSB) / Vout_atten_factor
        FEB0_VD = (FEB0_VD_U * shifted_V_ADC_res_mV_1LSB) / Vout_atten_factor
        FEB3_VA = (FEB3_VA_U * shifted_V_ADC_res_mV_1LSB) / Vout_atten_factor
        FEB2_VA = (FEB2_VA_U * shifted_V_ADC_res_mV_1LSB) / Vout_atten_factor
        FEB1_VA = (FEB1_VA_U * shifted_V_ADC_res_mV_1LSB) / Vout_atten_factor
        FEB0_VA = (FEB0_VA_U * shifted_V_ADC_res_mV_1LSB) / Vout_atten_factor
        ## acr 2018-02-28 BEGIN prototype V2 of GEMROC_IFC_CARD have INA GAIN set at 200 instead of 50!!!###
        IADC_conv_fact_INA_GAIN_50 = 8.13
        IADC_conv_fact_INA_GAIN_200 = 8.13 / 4  ## mA per LSB
    #    if self.GEMROC_ID < 3:
    #        IADC_conv_fact_INA_GAIN = IADC_conv_fact_INA_GAIN_50
    #   else:
        IADC_conv_fact_INA_GAIN = IADC_conv_fact_INA_GAIN_200
        FEB3_IA = (FEB3_IA_U * IADC_conv_fact_INA_GAIN)
        FEB2_IA = (FEB2_IA_U * IADC_conv_fact_INA_GAIN)
        FEB1_IA = (FEB1_IA_U * IADC_conv_fact_INA_GAIN)
        FEB0_IA = (FEB0_IA_U * IADC_conv_fact_INA_GAIN)
        FEB3_ID = (FEB3_ID_U * IADC_conv_fact_INA_GAIN)
        FEB2_ID = (FEB2_ID_U * IADC_conv_fact_INA_GAIN)
        FEB1_ID = (FEB1_ID_U * IADC_conv_fact_INA_GAIN)
        FEB0_ID = (FEB0_ID_U * IADC_conv_fact_INA_GAIN)
        ## acr 2018-02-28 END  prototype V2 have INA GAIN set at 200 instead of 50!!!###
        ROC_T_conv_fact_C_per_LSB = 1.0
        ROC_T = ROC_T_U * ROC_T_conv_fact_C_per_LSB
        if display_enable_param == 1:
            print'\n' + 'FEB3_T[degC]: ' + '%d; ' % FEB3_T + 'FEB3_VD[mV]: ' + '%d; ' % FEB3_VD + 'FEB3_ID[mA]: ' + '%d; ' % FEB3_ID + 'FEB3_VA[mV]: ' + '%d; ' % FEB3_VA + 'FEB3_IA[mA]: ' + '%d; ' % FEB3_IA
            print'\n' + 'FEB2_T[degC]: ' + '%d; ' % FEB2_T + 'FEB2_VD[mV]: ' + '%d; ' % FEB2_VD + 'FEB2_ID[mA]: ' + '%d; ' % FEB2_ID + 'FEB2_VA[mV]: ' + '%d; ' % FEB2_VA + 'FEB2_IA[mA]: ' + '%d; ' % FEB2_IA
            print'\n' + 'FEB1_T[degC]: ' + '%d; ' % FEB1_T + 'FEB1_VD[mV]: ' + '%d; ' % FEB1_VD + 'FEB1_ID[mA]: ' + '%d; ' % FEB1_ID + 'FEB1_VA[mV]: ' + '%d; ' % FEB1_VA + 'FEB1_IA[mA]: ' + '%d; ' % FEB1_IA
            print'\n' + 'FEB0_T[degC]: ' + '%d; ' % FEB0_T + 'FEB0_VD[mV]: ' + '%d; ' % FEB0_VD + 'FEB0_ID[mA]: ' + '%d; ' % FEB0_ID + 'FEB0_VA[mV]: ' + '%d; ' % FEB0_VA + 'FEB0_IA[mA]: ' + '%d; ' % FEB0_IA
            print'\n' + 'ROC_T: ' + '%d; ' % ROC_T
            print'\n' + 'FEB3_OVT: ' + '%d; ' % FEB3_OVT_FLAG + 'FEB3_DOVV: ' + '%d; ' % FEB3_DOVV_FLAG + 'FEB3_DOVC: ' + '%d; ' % FEB3_DOVC_FLAG + 'FEB3_AOVV: ' + '%d; ' % FEB3_AOVV_FLAG + 'FEB3_AOVC: ' + '%d; ' % FEB3_AOVC_FLAG
            print'\n' + 'FEB2_OVT: ' + '%d; ' % FEB2_OVT_FLAG + 'FEB2_DOVV: ' + '%d; ' % FEB2_DOVV_FLAG + 'FEB2_DOVC: ' + '%d; ' % FEB2_DOVC_FLAG + 'FEB2_AOVV: ' + '%d; ' % FEB2_AOVV_FLAG + 'FEB2_AOVC: ' + '%d; ' % FEB2_AOVC_FLAG  # acr 2018-10-19 END   test the functionality of the ADC read
            print'\n' + 'FEB1_OVT: ' + '%d; ' % FEB1_OVT_FLAG + 'FEB1_DOVV: ' + '%d; ' % FEB1_DOVV_FLAG + 'FEB1_DOVC: ' + '%d; ' % FEB1_DOVC_FLAG + 'FEB1_AOVV: ' + '%d; ' % FEB1_AOVV_FLAG + 'FEB1_AOVC: ' + '%d; ' % FEB1_AOVC_FLAG
            print'\n' + 'FEB0_OVT: ' + '%d; ' % FEB0_OVT_FLAG + 'FEB0_DOVV: ' + '%d; ' % FEB0_DOVV_FLAG + 'FEB0_DOVC: ' + '%d; ' % FEB0_DOVC_FLAG + 'FEB0_AOVV: ' + '%d; ' % FEB0_AOVV_FLAG + 'FEB0_AOVC: ' + '%d; ' % FEB0_AOVC_FLAG
            print'\n' + 'ROC_OVT: ' + '%d; ' % ROC_OVT_FLAG
        if log_enable_param == 1:
            self.IVT_log_file.write(
                '\n' + 'FEB3_T[degC]: ' + '%d; ' % FEB3_T + 'FEB3_VD[mV]: ' + '%d; ' % FEB3_VD + 'FEB3_ID[mA]: ' + '%d; ' % FEB3_ID + 'FEB3_VA[mV]: ' + '%d; ' % FEB3_VA + 'FEB3_IA[mA]: ' + '%d; ' % FEB3_IA)
            self.IVT_log_file.write(
                '\n' + 'FEB2_T[degC]: ' + '%d; ' % FEB2_T + 'FEB2_VD[mV]: ' + '%d; ' % FEB2_VD + 'FEB2_ID[mA]: ' + '%d; ' % FEB2_ID + 'FEB2_VA[mV]: ' + '%d; ' % FEB2_VA + 'FEB2_IA[mA]: ' + '%d; ' % FEB2_IA)
            self.IVT_log_file.write(
                '\n' + 'FEB1_T[degC]: ' + '%d; ' % FEB1_T + 'FEB1_VD[mV]: ' + '%d; ' % FEB1_VD + 'FEB1_ID[mA]: ' + '%d; ' % FEB1_ID + 'FEB1_VA[mV]: ' + '%d; ' % FEB1_VA + 'FEB1_IA[mA]: ' + '%d; ' % FEB1_IA)
            self.IVT_log_file.write(
                '\n' + 'FEB0_T[degC]: ' + '%d; ' % FEB0_T + 'FEB0_VD[mV]: ' + '%d; ' % FEB0_VD + 'FEB0_ID[mA]: ' + '%d; ' % FEB0_ID + 'FEB0_VA[mV]: ' + '%d; ' % FEB0_VA + 'FEB0_IA[mA]: ' + '%d; ' % FEB0_IA)
            self.IVT_log_file.write('\n' + 'ROC_T: ' + '%d; ' % ROC_T)
            self.IVT_log_file.write(
                '\n' + 'FEB3_OVT: ' + '%d; ' % FEB3_OVT_FLAG + 'FEB3_DOVV: ' + '%d; ' % FEB3_DOVV_FLAG + 'FEB3_DOVC: ' + '%d; ' % FEB3_DOVC_FLAG + 'FEB3_AOVV: ' + '%d; ' % FEB3_AOVV_FLAG + 'FEB3_AOVC: ' + '%d; ' % FEB3_AOVC_FLAG)
            self.IVT_log_file.write(
                '\n' + 'FEB2_OVT: ' + '%d; ' % FEB2_OVT_FLAG + 'FEB2_DOVV: ' + '%d; ' % FEB2_DOVV_FLAG + 'FEB2_DOVC: ' + '%d; ' % FEB2_DOVC_FLAG + 'FEB2_AOVV: ' + '%d; ' % FEB2_AOVV_FLAG + 'FEB2_AOVC: ' + '%d; ' % FEB2_AOVC_FLAG)  # acr 2018-10-19 END   test the functionality of the ADC read
            self.IVT_log_file.write(
                '\n' + 'FEB1_OVT: ' + '%d; ' % FEB1_OVT_FLAG + 'FEB1_DOVV: ' + '%d; ' % FEB1_DOVV_FLAG + 'FEB1_DOVC: ' + '%d; ' % FEB1_DOVC_FLAG + 'FEB1_AOVV: ' + '%d; ' % FEB1_AOVV_FLAG + 'FEB1_AOVC: ' + '%d; ' % FEB1_AOVC_FLAG)
            self.IVT_log_file.write(
                '\n' + 'FEB0_OVT: ' + '%d; ' % FEB0_OVT_FLAG + 'FEB0_DOVV: ' + '%d; ' % FEB0_DOVV_FLAG + 'FEB0_DOVC: ' + '%d; ' % FEB0_DOVC_FLAG + 'FEB0_AOVV: ' + '%d; ' % FEB0_AOVV_FLAG + 'FEB0_AOVC: ' + '%d; ' % FEB0_AOVC_FLAG)
            self.IVT_log_file.write('\n' + 'ROC_OVT : ' + '%d; ' % ROC_OVT_FLAG)
        return


    ## acr 2018-02-19 END definining a function to call within the display loop

    def display_log_GCfg_readback(self, command_echo_param, log_enable):  # acr 2018-03-02
        L_array = array.array('I')  # L is an array of unsigned long
        L_array.fromstring(command_echo_param)
        L_array.byteswap()
        print('\nList of Global Config Register parameters read back from TIGER%d on RESPONDING GEMROC%d:' % (
        ((L_array[11] >> 8) & 0X7), ((L_array[0] >> 16) & 0X1f)))  # acr 2018-01-23
        print('\nTIGER REPLY BYTE (LOW LEVEL SERIAL PROTOCOL ERROR FLAG):%02X;' % ((L_array[11] >> 16) & 0xFF))
        print('\nBufferBias: %d' % ((L_array[1] >> 24) & 0x3))
        print('\nTDCVcasN: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[1] >> 16) & 0xF), 4)))
        print('\nTDCVcasP: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[1] >> 8) & 0x1F), 5)))
        print('\nTDCVcasPHyst: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[1] >> 0) & 0x3F), 6)))
        print('\nDiscFE_Ibias: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[2] >> 24) & 0x3F), 6)))
        print('\nBiasFE_PpreN: %d' % ((L_array[2] >> 16) & 0x3F))
        print('\nAVcasp_global: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[2] >> 8) & 0x1F), 5)))
        print('\nTDCcompVcas: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[2] >> 0) & 0xF), 4)))
        print('\nTDCIref_cs: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[3] >> 24) & 0x1F), 5)))
        print('\nDiscVcasN: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[3] >> 16) & 0xF), 4)))
        print('\nIntegVb1: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[3] >> 8) & 0x3F), 6)))
        print('\nBiasFE_A1: %d' % ((L_array[3] >> 0) & 0xF))
        print('\nVcasp_Vth: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[4] >> 24) & 0x3F), 6)))
        print('\nTAC_I_LSB: %d' % ((L_array[4] >> 16) & 0x1F))
        print('\nTDCcompVbias: %d' % ((L_array[4] >> 8) & 0x1F))
        print('\nVref_Integ: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[4] >> 0) & 0x3F), 6)))
        print('\nIBiasTPcal: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[5] >> 24) & 0x1F), 5)))
        print('\nTP_Vcal: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[5] >> 16) & 0x1F), 5)))
        print('\nShaperIbias: %d' % ((L_array[5] >> 8) & 0xF))
        print('\nIPostamp: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[5] >> 0) & 0x1F), 5)))
        print('\nTP_Vcal_ref: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[6] >> 24) & 0x1F), 5)))
        print('\nVref_integ_diff: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[6] >> 16) & 0x3F), 6)))
        print('\nSig_pol: %d' % ((L_array[6] >> 8) & 0x1))
        print('\nFE_TPEnable: %d' % ((L_array[6] >> 0) & 0x1))
        print('\nDataClkDiv: %d' % ((L_array[7] >> 16) & 0x3))
        print('\nTACrefreshPeriod: %d' % ((L_array[7] >> 8) & 0xF))
        print('\nTACrefreshEnable: %d' % ((L_array[7] >> 0) & 0x1))
        print('\nCounterPeriod: %d' % ((L_array[8] >> 24) & 0x7))
        print('\nCounterEnable: %d' % ((L_array[8] >> 16) & 0x1))
        print('\nStopRampEnable: %d' % ((L_array[8] >> 8) & 0x3))
        print('\nRClkEnable: %d' % ((L_array[8] >> 0) & 0x1F))
        print('\nTDCClkdiv: %d' % ((L_array[9] >> 24) & 0x1))
        print('\nVetoMode: %d' % ((L_array[9] >> 16) & 0x3F))
        print('\nCh_DebugMode: %d' % ((L_array[9] >> 8) & 0x1))
        print('\nTxMode: %d' % ((L_array[9] >> 0) & 0x3))
        print('\nTxDDR: %d' % ((L_array[10] >> 24) & 0x1))
        print('\nTxLinks: %d' % ((L_array[10] >> 16) & 0x3))
        if log_enable == 1:
            self.log_file.write(
                '\nList of Global Config Register parameters read back from TIGER%d on RESPONDING GEMROC%d:' % (
                ((L_array[11] >> 8) & 0X7), ((L_array[0] >> 16) & 0X1f)))  # acr 2018-01-23
            self.log_file.write(
                "\nTIGER REPLY BYTE (LOW LEVEL SERIAL PROTOCOL ERROR FLAG):%02X;" % ((L_array[11] >> 16) & 0XFF))
            self.log_file.write('\nBufferBias: %d' % ((L_array[1] >> 24) & 0x3))
            self.log_file.write(
                '\nTDCVcasN: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[1] >> 16) & 0xF), 4)))
            self.log_file.write(
                '\nTDCVcasP: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[1] >> 8) & 0x1F), 5)))
            self.log_file.write(
                '\nTDCVcasPHyst: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[1] >> 0) & 0x3F), 6)))
            self.log_file.write(
                '\nDiscFE_Ibias: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[2] >> 24) & 0x3F), 6)))
            self.log_file.write('\nBiasFE_PpreN: %d' % ((L_array[2] >> 16) & 0x3F))
            self.log_file.write(
                '\nAVcasp_global: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[2] >> 8) & 0x1F), 5)))
            self.log_file.write(
                '\nTDCcompVcas: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[2] >> 0) & 0xF), 4)))
            self.log_file.write(
                '\nTDCIref_cs: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[3] >> 24) & 0x1F), 5)))
            self.log_file.write(
                '\nDiscVcasN: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[3] >> 16) & 0xF), 4)))
            self.log_file.write(
                '\nIntegVb1: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[3] >> 8) & 0x3F), 6)))
            self.log_file.write('\nBiasFE_A1: %d' % ((L_array[3] >> 0) & 0xF))
            self.log_file.write(
                '\nVcasp_Vth: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[4] >> 24) & 0x3F), 6)))
            self.log_file.write('\nTAC_I_LSB: %d' % ((L_array[4] >> 16) & 0x1F))
            self.log_file.write('\nTDCcompVbias: %d' % ((L_array[4] >> 8) & 0x1F))
            self.log_file.write(
                '\nVref_Integ: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[4] >> 0) & 0x3F), 6)))
            self.log_file.write(
                '\nIBiasTPcal: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[5] >> 24) & 0x1F), 5)))
            self.log_file.write(
                '\nTP_Vcal: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[5] >> 16) & 0x1F), 5)))
            self.log_file.write('\nShaperIbias: %d' % ((L_array[5] >> 8) & 0xF))
            self.log_file.write(
                '\nIPostamp: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[5] >> 0) & 0x1F), 5)))
            self.log_file.write(
                '\nTP_Vcal_ref: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[6] >> 24) & 0x1F), 5)))
            self.log_file.write(
                '\nVref_integ_diff: %d' % (GEM_CONF_classes.swap_order_N_bits(((L_array[6] >> 16) & 0x3F), 6)))
            self.log_file.write('\nSig_pol: %d' % ((L_array[6] >> 8) & 0x1))
            self.log_file.write('\nFE_TPEnable: %d' % ((L_array[6] >> 0) & 0x1))
            self.log_file.write('\nDataClkDiv: %d' % ((L_array[7] >> 16) & 0x3))
            self.log_file.write('\nTACrefreshPeriod: %d' % ((L_array[7] >> 8) & 0xF))
            self.log_file.write('\nTACrefreshEnable: %d' % ((L_array[7] >> 0) & 0x1))
            self.log_file.write('\nCounterPeriod: %d' % ((L_array[8] >> 24) & 0x7))
            self.log_file.write('\nCounterEnable: %d' % ((L_array[8] >> 16) & 0x1))
            self.log_file.write('\nStopRampEnable: %d' % ((L_array[8] >> 8) & 0x3))
            self.log_file.write('\nRClkEnable: %d' % ((L_array[8] >> 0) & 0x1F))
            self.log_file.write('\nTDCClkdiv: %d' % ((L_array[9] >> 24) & 0x1))
            self.log_file.write('\nVetoMode: %d' % ((L_array[9] >> 16) & 0x3F))
            self.log_file.write('\nCh_DebugMode: %d' % ((L_array[9] >> 8) & 0x1))
            self.log_file.write('\nTxMode: %d' % ((L_array[9] >> 0) & 0x3))
            self.log_file.write('\nTxDDR: %d' % ((L_array[10] >> 24) & 0x1))
            self.log_file.write('\nTxLinks: %d' % ((L_array[10] >> 16) & 0x3))

    def display_log_ChCfg_readback(self, command_echo_param, log_enable):  # acr 2018-03-02
        L_array = array.array('I')  # L is an array of unsigned long
        L_array.fromstring(command_echo_param)
        L_array.byteswap()
        print('\nList of Channel %d Config Register parameters read back from TIGER%d on RESPONDING GEMROC%d:' % (
            ((L_array[9] >> 0) & 0X3F), ((L_array[9] >> 8) & 0X7), ((L_array[0] >> 16) & 0X1f)))  # acr 2018-01-23
        print("\nTIGER REPLY BYTE (LOW LEVEL SERIAL PROTOCOL ERROR FLAG):%02X;" % (((L_array[9] >> 16) & 0Xff)))
        print('\n DisableHyst: %d' % ((L_array[1] >> 24) & 0x1))
        print('\n T2Hyst: %d' % ((L_array[1] >> 16) & 0x7))
        print('\n T1Hyst: %d' % ((L_array[1] >> 8) & 0x7))
        print('\n Ch63ObufMSB: %d' % ((L_array[1] >> 0) & 0x1))
        print('\n TP_disable_FE: %d' % ((L_array[2] >> 24) & 0x1))
        print('\n TDC_IB_E: %d' % ((L_array[2] >> 16) & 0xF))
        print('\n TDC_IB_T: %d' % ((L_array[2] >> 8) & 0xF))
        print('\n Integ: %d' % ((L_array[2] >> 0) & 0x1))
        print('\n PostAmpGain: %d' % ((L_array[3] >> 24) & 0x3))
        print('\n FE_delay: %d' % ((L_array[3] >> 16) & 0x1F))
        print('\n Vth_T2: %d' % ((L_array[3] >> 8) & 0x3F))
        print('\n Vth_T1: %d' % ((L_array[3] >> 0) & 0x3F))
        print('\n QTx2Enable: %d' % ((L_array[4] >> 24) & 0x1))
        print('\n MaxIntegTime: %d' % ((L_array[4] >> 16) & 0x7F))
        print('\n MinIntegTime: %d' % ((L_array[4] >> 8) & 0x7F))
        print('\n TriggerBLatched: %d' % ((L_array[4] >> 0) & 0x1))
        print('\n QdcMode: %d' % ((L_array[5] >> 24) & 0x1))
        print('\n BranchEnableT: %d' % ((L_array[5] >> 16) & 0x1))
        print('\n BranchEnableEQ: %d' % ((L_array[5] >> 8) & 0x1))
        print('\n TriggerMode2B: %d' % ((L_array[5] >> 0) & 0x7))
        print('\n TriggerMode2Q: %d' % ((L_array[6] >> 24) & 0x3))
        print('\n TriggerMode2E: %d' % ((L_array[6] >> 16) & 0x7))
        print('\n TriggerMode2T: %d' % ((L_array[6] >> 8) & 0x3))
        print('\n TACMinAge: %d' % ((L_array[6] >> 0) & 0x1F))
        print('\n TACMaxAge: %d' % ((L_array[7] >> 24) & 0x1F))
        print('\n CounterMode: %d' % ((L_array[7] >> 16) & 0xF))
        print('\n DeadTime: %d' % ((L_array[7] >> 8) & 0x3F))
        print('\n SyncChainLen: %d' % ((L_array[7] >> 0) & 0x3))
        print('\n Ch_DebugMode: %d' % ((L_array[8] >> 24) & 0x3))
        print('\n TriggerMode: %d' % ((L_array[8] >> 16) & 0x3))
        if log_enable == 1:
            self.log_file.write(
                '\nList of Channel %d Config Register parameters read back from TIGER%d on RESPONDING GEMROC%d:' % (
                    ((L_array[9] >> 0) & 0X3F), ((L_array[9] >> 8) & 0X7),
                    ((L_array[0] >> 16) & 0X1f)))  # acr 2018-01-23
            self.log_file.write(
                "\nTIGER REPLY BYTE (LOW LEVEL SERIAL PROTOCOL ERROR FLAG):%02X;" % (((L_array[9] >> 16) & 0Xff)))
            self.log_file.write('\n DisableHyst: %d' % ((L_array[1] >> 24) & 0x1))
            self.log_file.write('\n T2Hyst: %d' % ((L_array[1] >> 16) & 0x7))
            self.log_file.write('\n T1Hyst: %d' % ((L_array[1] >> 8) & 0x7))
            self.log_file.write('\n Ch63ObufMSB: %d' % ((L_array[1] >> 0) & 0x1))
            self.log_file.write('\n TP_disable_FE: %d' % ((L_array[2] >> 24) & 0x1))
            self.log_file.write('\n TDC_IB_E: %d' % ((L_array[2] >> 16) & 0xF))
            self.log_file.write('\n TDC_IB_T: %d' % ((L_array[2] >> 8) & 0xF))
            self.log_file.write('\n Integ: %d' % ((L_array[2] >> 0) & 0x1))
            self.log_file.write('\n PostAmpGain: %d' % ((L_array[3] >> 24) & 0x3))
            self.log_file.write('\n FE_delay: %d' % ((L_array[3] >> 16) & 0x1F))
            self.log_file.write('\n Vth_T2: %d' % ((L_array[3] >> 8) & 0x3F))
            self.log_file.write('\n Vth_T1: %d' % ((L_array[3] >> 0) & 0x3F))
            self.log_file.write('\n QTx2Enable: %d' % ((L_array[4] >> 24) & 0x1))
            self.log_file.write('\n MaxIntegTime: %d' % ((L_array[4] >> 16) & 0x7F))
            self.log_file.write('\n MinIntegTime: %d' % ((L_array[4] >> 8) & 0x7F))
            self.log_file.write('\n TriggerBLatched: %d' % ((L_array[4] >> 0) & 0x1))
            self.log_file.write('\n QdcMode: %d' % ((L_array[5] >> 24) & 0x1))
            self.log_file.write('\n BranchEnableT: %d' % ((L_array[5] >> 16) & 0x1))
            self.log_file.write('\n BranchEnableEQ: %d' % ((L_array[5] >> 8) & 0x1))
            self.log_file.write('\n TriggerMode2B: %d' % ((L_array[5] >> 0) & 0x7))
            self.log_file.write('\n TriggerMode2Q: %d' % ((L_array[6] >> 24) & 0x3))
            self.log_file.write('\n TriggerMode2E: %d' % ((L_array[6] >> 16) & 0x7))
            self.log_file.write('\n TriggerMode2T: %d' % ((L_array[6] >> 8) & 0x3))
            self.log_file.write('\n TACMinAge: %d' % ((L_array[6] >> 0) & 0x1F))
            self.log_file.write('\n TACMaxAge: %d' % ((L_array[7] >> 24) & 0x1F))
            self.log_file.write('\n CounterMode: %d' % ((L_array[7] >> 16) & 0xF))
            self.log_file.write('\n DeadTime: %d' % ((L_array[7] >> 8) & 0x3F))
            self.log_file.write('\n SyncChainLen: %d' % ((L_array[7] >> 0) & 0x3))
            self.log_file.write('\n Ch_DebugMode: %d' % ((L_array[8] >> 24) & 0x3))
            self.log_file.write('\n TriggerMode: %d' % ((L_array[8] >> 16) & 0x3))

    # def display_log_ChCfg_readback(self, command_echo_param, log_enable):  # acr 2018-03-02
    #     L_array = array.array('I')  # L is an array of unsigned long
    #     L_array.fromstring(command_echo_param)
    #     L_array.byteswap()
    #     print('\nList of Channel %d Config Register parameters read back from TIGER%d on RESPONDING GEMROC%d:' % (
    #     ((L_array[9] >> 0) & 0X3F), ((L_array[9] >> 8) & 0X7), ((L_array[0] >> 16) & 0X1f)))  # acr 2018-01-23
    #     print("\nTIGER REPLY BYTE (LOW LEVEL SERIAL PROTOCOL ERROR FLAG):%02X;" % ((L_array[9] >> 16) & 0Xff))
    #     print('\n DisableHyst: %d' % ((L_array[1] >> 24) & 0x1))
    #     print('\n T2Hyst: %d' % ((L_array[1] >> 16) & 0x7))
    #     print('\n T1Hyst: %d' % ((L_array[1] >> 8) & 0x7))
    #     print('\n Ch63ObufMSB: %d' % ((L_array[1] >> 0) & 0x1))
    #     print('\n TP_disable_FE: %d' % ((L_array[2] >> 24) & 0x1))
    #     print('\n TDC_IB_E: %d' % ((L_array[2] >> 16) & 0xF))
    #     print('\n TDC_IB_T: %d' % ((L_array[2] >> 8) & 0xF))
    #     print('\n Integ: %d' % ((L_array[2] >> 0) & 0x1))
    #     print('\n PostAmpGain: %d' % ((L_array[3] >> 24) & 0x3))
    #     print('\n FE_delay: %d' % ((L_array[3] >> 16) & 0x1F))
    #     print('\n Vth_T2: %d' % ((L_array[3] >> 8) & 0x3F))
    #     print('\n Vth_T1: %d' % ((L_array[3] >> 0) & 0x3F))
    #     print('\n QTx2Enable: %d' % ((L_array[4] >> 24) & 0x1))
    #     print('\n MaxIntegTime: %d' % ((L_array[4] >> 16) & 0x7F))
    #     print('\n MinIntegTime: %d' % ((L_array[4] >> 8) & 0x7F))
    #     print('\n TriggerBLatched: %d' % ((L_array[4] >> 0) & 0x1))
    #     print('\n QdcMode: %d' % ((L_array[5] >> 24) & 0x1))
    #     print('\n BranchEnableT: %d' % ((L_array[5] >> 16) & 0x1))
    #     print('\n BranchEnableEQ: %d' % ((L_array[5] >> 8) & 0x1))
    #     print('\n TriggerMode2B: %d' % ((L_array[5] >> 0) & 0x7))
    #     print('\n TriggerMode2Q: %d' % ((L_array[6] >> 24) & 0x3))
    #     print('\n TriggerMode2E: %d' % ((L_array[6] >> 16) & 0x7))
    #     print('\n TriggerMode2T: %d' % ((L_array[6] >> 8) & 0x3))
    #     print('\n TACMinAge: %d' % ((L_array[6] >> 0) & 0x1F))
    #     print('\n TACMaxAge: %d' % ((L_array[7] >> 24) & 0x1F))
    #     print('\n CounterMode: %d' % ((L_array[7] >> 16) & 0xF))
    #     print('\n DeadTime: %d' % ((L_array[7] >> 8) & 0x3F))
    #     print('\n SyncChainLen: %d' % ((L_array[7] >> 0) & 0x3))
    #     print('\n Ch_DebugMode: %d' % ((L_array[8] >> 24) & 0x3))
    #     print('\n TriggerMode: %d' % ((L_array[8] >> 16) & 0x3))
    #     if log_enable == 1:
    #         self.log_file.write(
    #             '\nList of Channel %d Config Register parameters read back from TIGER%d on RESPONDING GEMROC%d:' % (
    #             ((L_array[9] >> 0) & 0X3F), ((L_array[9] >> 8) & 0X7), ((L_array[0] >> 16) & 0X1f)))  # acr 2018-01-23
    #         self.log_file.write(
    #             "\nTIGER REPLY BYTE (LOW LEVEL SERIAL PROTOCOL ERROR FLAG):%02X;" % ((L_array[9] >> 16) & 0Xff))
    #         self.log_file.write('\n DisableHyst: %d' % ((L_array[1] >> 24) & 0x1))
    #         self.log_file.write('\n T2Hyst: %d' % ((L_array[1] >> 16) & 0x7))
    #         self.log_file.write('\n T1Hyst: %d' % ((L_array[1] >> 8) & 0x7))
    #         self.log_file.write('\n Ch63ObufMSB: %d' % ((L_array[1] >> 0) & 0x1))
    #         self.log_file.write('\n TP_disable_FE: %d' % ((L_array[2] >> 24) & 0x1))
    #         self.log_file.write('\n TDC_IB_E: %d' % ((L_array[2] >> 16) & 0xF))
    #         self.log_file.write('\n TDC_IB_T: %d' % ((L_array[2] >> 8) & 0xF))
    #         self.log_file.write('\n Integ: %d' % ((L_array[2] >> 0) & 0x1))
    #         self.log_file.write('\n PostAmpGain: %d' % ((L_array[3] >> 24) & 0x3))
    #         self.log_file.write('\n FE_delay: %d' % ((L_array[3] >> 16) & 0x1F))
    #         self.log_file.write('\n Vth_T2: %d' % ((L_array[3] >> 8) & 0x3F))
    #         self.log_file.write('\n Vth_T1: %d' % ((L_array[3] >> 0) & 0x3F))
    #         self.log_file.write('\n QTx2Enable: %d' % ((L_array[4] >> 24) & 0x1))
    #         self.log_file.write('\n MaxIntegTime: %d' % ((L_array[4] >> 16) & 0x7F))
    #         self.log_file.write('\n MinIntegTime: %d' % ((L_array[4] >> 8) & 0x7F))
    #         self.log_file.write('\n TriggerBLatched: %d' % ((L_array[4] >> 0) & 0x1))
    #         self.log_file.write('\n QdcMode: %d' % ((L_array[5] >> 24) & 0x1))
    #         self.log_file.write('\n BranchEnableT: %d' % ((L_array[5] >> 16) & 0x1))
    #         self.log_file.write('\n BranchEnableEQ: %d' % ((L_array[5] >> 8) & 0x1))
    #         self.log_file.write('\n TriggerMode2B: %d' % ((L_array[5] >> 0) & 0x7))
    #         self.log_file.write('\n TriggerMode2Q: %d' % ((L_array[6] >> 24) & 0x3))
    #         self.log_file.write('\n TriggerMode2E: %d' % ((L_array[6] >> 16) & 0x7))
    #         self.log_file.write('\n TriggerMode2T: %d' % ((L_array[6] >> 8) & 0x3))
    #         self.log_file.write('\n TACMinAge: %d' % ((L_array[6] >> 0) & 0x1F))
    #         self.log_file.write('\n TACMaxAge: %d' % ((L_array[7] >> 24) & 0x1F))
    #         self.log_file.write('\n CounterMode: %d' % ((L_array[7] >> 16) & 0xF))
    #         self.log_file.write('\n DeadTime: %d' % ((L_array[7] >> 8) & 0x3F))
    #         self.log_file.write('\n SyncChainLen: %d' % ((L_array[7] >> 0) & 0x3))
    #         self.log_file.write('\n Ch_DebugMode: %d' % ((L_array[8] >> 24) & 0x3))
    #         self.log_file.write('\n TriggerMode: %d' % ((L_array[8] >> 16) & 0x3))


    def send_TIGER_GCFG_Reg_CMD_PKT(self, TIGER_ID_param, COMMAND_STRING_PARAM, array_to_send_param, DEST_IP_ADDRESS_PARAM,
                                    DEST_PORT_NO_PARAM):  # acr 2018-03-05
        buffer_to_send = struct.pack('>' + str(len(array_to_send_param)) + 'L', *array_to_send_param)
        self.flush_socket()

        self.clientSock.sendto(buffer_to_send, (DEST_IP_ADDRESS_PARAM, DEST_PORT_NO_PARAM))
        cmd_message = '\nTIGER%d Global Cfg Reg CMD %s sent:\n' % (TIGER_ID_param, COMMAND_STRING_PARAM)
        self.log_file.write(cmd_message)
        self.log_file.write(binascii.b2a_hex(buffer_to_send))
        cmd_message = '\nTIGER%d Global Cfg Reg CMD %s command echo:\n' % (TIGER_ID_param, COMMAND_STRING_PARAM)
        self.log_file.write(cmd_message)
        command_echo_f = self.receiveSock.recv(self.BUFSIZE)
        self.log_file.write(binascii.b2a_hex(command_echo_f))
        # print "\nMandato : {}".format(binascii.b2a_hex(buffer_to_send))
        # print "\nRicevuto : {}".format(binascii.b2a_hex(command_echo_f))
        # time.sleep(2)
        return command_echo_f


    def send_TIGER_Ch_CFG_Reg_CMD_PKT(self, TIGER_ID_param, COMMAND_STRING_PARAM, array_to_send_param, DEST_IP_ADDRESS_PARAM,
                                      DEST_PORT_NO_PARAM):  # acr 2018-03-04
        buffer_to_send = struct.pack('>' + str(len(array_to_send_param)) + 'L', *array_to_send_param)
        self.flush_socket()

        self.clientSock.sendto(buffer_to_send, (DEST_IP_ADDRESS_PARAM, DEST_PORT_NO_PARAM))
        Target_Ch_ToALL_f = (array_to_send_param[(len(array_to_send_param) - 1)] >> 6) & 0x1
        Target_Ch_ID_f = (array_to_send_param[(len(array_to_send_param) - 1)] >> 0) & 0x3F
        cmd_message = '\nTIGER% d; TOALL = % d; Channel% s Cfg Reg CMD %s sent\n' % (
        TIGER_ID_param, Target_Ch_ToALL_f, Target_Ch_ID_f, COMMAND_STRING_PARAM)
        self.log_file.write(cmd_message)
        self.log_file.write(binascii.b2a_hex(buffer_to_send))
        cmd_message = '\nTIGER% d; TOALL = % d; Channel% s Cfg Reg CMD %s echo\n' % (
        TIGER_ID_param, Target_Ch_ToALL_f, Target_Ch_ID_f, COMMAND_STRING_PARAM)
        self.log_file.write(cmd_message)
        command_echo_f = self.receiveSock.recv(self.BUFSIZE)
        self.log_file.write(binascii.b2a_hex(command_echo_f))
        return command_echo_f


    # def GEMROC_IVT_read_and_log(self, GEMROC_ID_param, display_enable_param, log_enable_param, log_filename_param):
    #     self.gemroc_LV_XX.set_target_GEMROC(GEMROC_ID_param)
    #     COMMAND_STRING = 'CMD_GEMROC_LV_IVT_READ'
    #     self.gemroc_LV_XX.set_gemroc_cmd_code(COMMAND_STRING, 1)
    #     self.gemroc_LV_XX.update_command_words()
    #     array_to_send = self.gemroc_LV_XX.command_words
    #     command_echo_ivt = self.send_GEMROC_CFG_CMD_PKT(GEMROC_ID_param, COMMAND_STRING, array_to_send, self.DEST_IP_ADDRESS,
    #                                                self.DEST_PORT_NO)
    #     # print '\nGEMROC_ID: %d: CMD_GEMROC_LV_IVT_READ' %GEMROC_ID_param
    #     self.display_and_log_IVT(command_echo_ivt, display_enable_param, log_enable_param, log_filename_param)
    #     return

    def GEMROC_IVT_read_and_log(self, GEMROC_ID_param, display_enable_param, log_enable_param,
                                log_filename_param):
        self.gemroc_LV_XX.set_target_GEMROC(GEMROC_ID_param)
        COMMAND_STRING = 'CMD_GEMROC_LV_IVT_READ'
        self.gemroc_LV_XX.set_gemroc_cmd_code(COMMAND_STRING, 1)
        self.gemroc_LV_XX.update_command_words()
        array_to_send = self.gemroc_LV_XX.command_words
        DEST_IP_ADDRESS = self.DEST_IP_ADDRESS
        DEST_PORT_NO = self.DEST_PORT_NO
        command_echo_ivt = self.send_GEMROC_CFG_CMD_PKT(GEMROC_ID_param, COMMAND_STRING, array_to_send,
                                                   self.DEST_IP_ADDRESS, self.DEST_PORT_NO)
        # print '\nGEMROC_ID: %d: CMD_GEMROC_LV_IVT_READ' %GEMROC_ID_param
        self.display_and_log_IVT(command_echo_ivt, display_enable_param, log_enable_param, log_filename_param)
        return


    def send_GEMROC_LV_CMD(self, GEMROC_ID_param, COMMAND_STRING_PARAM):
        self.gemroc_LV_XX.set_target_GEMROC(GEMROC_ID_param)
        self.gemroc_LV_XX.set_gemroc_cmd_code(COMMAND_STRING_PARAM, 1)
        self.gemroc_LV_XX.update_command_words()
        array_to_send = self.gemroc_LV_XX.command_words
        command_echo = self.send_GEMROC_CFG_CMD_PKT(GEMROC_ID_param, COMMAND_STRING_PARAM, array_to_send, self.DEST_IP_ADDRESS,
                                               self.DEST_PORT_NO)
        return command_echo


    def FEBPwrEnPattern_set(self, GEMROC_ID_param, FEB_PWREN_pattern_param):
        self.gemroc_LV_XX.set_target_GEMROC(GEMROC_ID_param)
        self.gemroc_LV_XX.set_FEB_PWR_EN_pattern(FEB_PWREN_pattern_param)
        COMMAND_STRING = 'CMD_GEMROC_LV_CFG_WR'
        command_echo = self.send_GEMROC_LV_CMD(GEMROC_ID_param, COMMAND_STRING)
        return command_echo


    def set_FEB_timing_delays(self, GEMROC_ID_param, FEB3_TDly, FEB2_TDly, FEB1_TDly, FEB0_TDly):
        self.gemroc_LV_XX.set_target_GEMROC(GEMROC_ID_param)
        self.gemroc_LV_XX.set_timing_toFEB_delay(FEB3_TDly, FEB2_TDly, FEB1_TDly, FEB0_TDly)
        COMMAND_STRING = 'CMD_GEMROC_LV_CFG_WR'
        command_echo = self.send_GEMROC_LV_CMD(GEMROC_ID_param, COMMAND_STRING)
        COMMAND_STRING = 'CMD_GEMROC_TIMING_DELAYS_UPDATE'
        command_echo = self.send_GEMROC_LV_CMD(GEMROC_ID_param, COMMAND_STRING)
        return command_echo


    # acr 2018-03-06 changed order of parameters of send_GEMROC_DAQ_CMD
    def send_GEMROC_DAQ_CMD(self, GEMROC_ID_param, gemroc_DAQ_inst_param, COMMAND_STRING_PARAM):
        gemroc_DAQ_inst_param.set_target_GEMROC(GEMROC_ID_param)
        gemroc_DAQ_inst_param.set_gemroc_cmd_code(COMMAND_STRING_PARAM, 1)
        gemroc_DAQ_inst_param.update_command_words()
        array_to_send = gemroc_DAQ_inst_param.command_words
        command_echo = self.send_GEMROC_CFG_CMD_PKT(GEMROC_ID_param, COMMAND_STRING_PARAM, array_to_send, self.DEST_IP_ADDRESS,
                                               self.DEST_PORT_NO)
        return command_echo

    # acr 2018-04-23
    def send_GEMROC_DAQ_CMD_num_rep(self,GEMROC_ID_param, gemroc_DAQ_inst_param, COMMAND_STRING_PARAM, num_of_repetitions_param):
        gemroc_DAQ_inst_param.set_target_GEMROC(GEMROC_ID_param)
        gemroc_DAQ_inst_param.set_gemroc_cmd_code(COMMAND_STRING_PARAM, num_of_repetitions_param)
        gemroc_DAQ_inst_param.update_command_words()
        print '\n gemroc_DAQ_inst_param.number_of_repetitions = %03X' % gemroc_DAQ_inst_param.number_of_repetitions
        array_to_send = gemroc_DAQ_inst_param.command_words
        command_echo = self.send_GEMROC_CFG_CMD_PKT(GEMROC_ID_param, COMMAND_STRING_PARAM, array_to_send, self.DEST_IP_ADDRESS, self.DEST_PORT_NO)
        return command_echo


    def ResetTgtGEMROC_ALL_TIGER_GCfgReg(self, GEMROC_ID_param, gemroc_DAQ_inst_param):
        COMMAND_STRING = 'CMD_GEMROC_DAQ_TIGER_GCFGREG_RESET'
        command_echo = self.send_GEMROC_DAQ_CMD(GEMROC_ID_param, gemroc_DAQ_inst_param, COMMAND_STRING)
        print'\n CMD_GEMROC_DAQ_TIGER_GCFGREG_RESET'
        time.sleep(1)


    def WriteTgtGEMROC_TIGER_GCfgReg_fromfile(self, GCFGReg_setting_inst, GEMROC_ID_param, TIGER_ID_param,
                                              GCFGReg_def_fname_param):

        GCFGReg_setting_inst.reload_gcfg_settings_from_file(
            GCFGReg_def_fname_param)  ## acr 2018-02-23 new method to reaload from a default file
        GCFGReg_setting_inst.set_target_GEMROC(GEMROC_ID_param)
        GCFGReg_setting_inst.set_target_TIGER(TIGER_ID_param)
        COMMAND_STRING = 'WR'
        GCFGReg_setting_inst.set_command_code(COMMAND_STRING)
        GCFGReg_setting_inst.update_command_words()
        self.log_file.write('\nList of Global Config Register settings to TIGER%d of RESPONDING GEMROC%d:' % (
        TIGER_ID_param, GEMROC_ID_param))
        classes_test_functions.print_log_GReg_members(GCFGReg_setting_inst, 1, self.log_file)
        returned_array = classes_test_functions.get_GReg_GEMROC_words(GCFGReg_setting_inst)
        # keep print '\nGCFG_168_137: ' + "%08X" %returned_array[0]
        # keep print '\nGCFG_136_105: ' + "%08X" %returned_array[1]
        # keep print '\nGCFG_104_73:  ' + "%08X" %returned_array[2]
        # keep print '\nGCFG_72_41:   ' + "%08X" %returned_array[3]
        # keep print '\nGCFG_40_9:    ' + "%08X" %returned_array[4]
        # keep print '\nGCFG_8_m23:   ' + "%08X" %returned_array[5]
        # keep print '\nG_reg_inst WR bitstring_TO_format:'
        print('\nList of Global Config Register settings to TIGER%d of RESPONDING GEMROC%d in Torino string format:' % (
        TIGER_ID_param, GEMROC_ID_param))
        self.log_file.write(
            '\nList of Global Config Register settings to TIGER%d of RESPONDING GEMROC%d in Torino string format:' % (
            TIGER_ID_param, GEMROC_ID_param))
        classes_test_functions.print_GReg_bitstring_TO_format(returned_array, 1, self.log_file)
        array_to_send = GCFGReg_setting_inst.command_words
        command_echo = self.send_TIGER_GCFG_Reg_CMD_PKT(TIGER_ID_param, COMMAND_STRING, array_to_send, self.DEST_IP_ADDRESS,
                                                   self.DEST_PORT_NO)
        return command_echo


    def set_FE_TPEnable(self, GCFGReg_setting_inst, GEMROC_ID_param, TIGER_ID_param, FE_TPEnable_param):
        GCFGReg_setting_inst.set_FE_TPEnable(FE_TPEnable_param)
        GCFGReg_setting_inst.set_target_GEMROC(GEMROC_ID_param)
        GCFGReg_setting_inst.set_target_TIGER(TIGER_ID_param)
        COMMAND_STRING = 'WR'
        GCFGReg_setting_inst.set_command_code(COMMAND_STRING)
        GCFGReg_setting_inst.update_command_words()
        array_to_send = GCFGReg_setting_inst.command_words
        command_echo = self.send_TIGER_GCFG_Reg_CMD_PKT(TIGER_ID_param, COMMAND_STRING, array_to_send, self.DEST_IP_ADDRESS,
                                                   self.DEST_PORT_NO)
        print('\nFE_TPEnable of Global CFG reg of TIGER%d of RESPONDING GEMROC%d: set to %d' % (
        TIGER_ID_param, GEMROC_ID_param, FE_TPEnable_param))
        self.log_file.write('\nFE_TPEnable of Global CFG reg of TIGER%d of RESPONDING GEMROC%d: set to %d' % (
        TIGER_ID_param, GEMROC_ID_param, FE_TPEnable_param))
        return command_echo

    def ReadTgtGEMROC_TIGER_GCfgReg(self, GCFGReg_setting_inst, GEMROC_ID_param, TIGER_ID_param):
        GCFGReg_setting_inst.set_target_GEMROC(GEMROC_ID_param)
        GCFGReg_setting_inst.set_target_TIGER(TIGER_ID_param)
        COMMAND_STRING = 'RD'
        GCFGReg_setting_inst.set_command_code(COMMAND_STRING)
        GCFGReg_setting_inst.update_command_words()
        array_to_send = GCFGReg_setting_inst.command_words
        command_echo = self.send_TIGER_GCFG_Reg_CMD_PKT(TIGER_ID_param, COMMAND_STRING, array_to_send, self.DEST_IP_ADDRESS,
                                                   self.DEST_PORT_NO) #Leggo due volte, la prima mi ritorna cio che ho mandato, la seconda la lettura vera.
        command_echo = self.send_TIGER_GCFG_Reg_CMD_PKT(TIGER_ID_param, COMMAND_STRING, array_to_send, self.DEST_IP_ADDRESS,
                                                   self.DEST_PORT_NO)
        return command_echo


    def WriteTgtGEMROC_TIGER_ChCfgReg_fromfile(self, ChCFGReg_setting_inst, GEMROC_ID_param, TIGER_ID_param, channel_ID_param,
                                               ChCFGReg_def_fname_param):
        ChCFGReg_setting_inst.reload_chcfg_settings_from_file(
            ChCFGReg_def_fname_param)  ## acr 2018-02-23 new method to reaload from a default file
        ChCFGReg_setting_inst.set_target_GEMROC(GEMROC_ID_param)
        ChCFGReg_setting_inst.set_target_TIGER(TIGER_ID_param)
        ChCFGReg_setting_inst.set_to_ALL_param(
            0)  ## let's do multiple configuration under script control rather than under GEMROC NIOS2 processor control
        COMMAND_STRING = 'WR'
        ChCFGReg_setting_inst.set_command_code(COMMAND_STRING)
        if channel_ID_param < 64:
            ChCFGReg_setting_inst.set_target_channel(channel_ID_param)
            ChCFGReg_setting_inst.update_command_words()
            array_to_send = ChCFGReg_setting_inst.command_words
            command_echo = self.send_TIGER_Ch_CFG_Reg_CMD_PKT(TIGER_ID_param, COMMAND_STRING, array_to_send, self.DEST_IP_ADDRESS,
                                                         self.DEST_PORT_NO)
        else:
            for i in range(0, 64):
                ChCFGReg_setting_inst.set_target_channel(i)
                ChCFGReg_setting_inst.update_command_words()
                array_to_send = ChCFGReg_setting_inst.command_words
                command_echo = self.send_TIGER_Ch_CFG_Reg_CMD_PKT(TIGER_ID_param, COMMAND_STRING, array_to_send,
                                                             self.DEST_IP_ADDRESS,
                                                             self.DEST_PORT_NO)
        return command_echo


    def ReadTgtGEMROC_TIGER_ChCfgReg(self, ChCFGReg_setting_inst, GEMROC_ID_param, TIGER_ID_param, channel_ID_param, verbose_mode):
        ChCFGReg_setting_inst.set_target_GEMROC(GEMROC_ID_param)
        ChCFGReg_setting_inst.set_target_TIGER(TIGER_ID_param)
        ChCFGReg_setting_inst.set_target_channel(channel_ID_param)
        COMMAND_STRING = 'RD'
        ChCFGReg_setting_inst.set_command_code(COMMAND_STRING)
        array_to_send = ChCFGReg_setting_inst.command_words
        if channel_ID_param < 64:
            ChCFGReg_setting_inst.set_target_channel(channel_ID_param)
            ChCFGReg_setting_inst.update_command_words()
            array_to_send = ChCFGReg_setting_inst.command_words
            command_echo = self.send_TIGER_Ch_CFG_Reg_CMD_PKT(TIGER_ID_param, COMMAND_STRING, array_to_send, self.DEST_IP_ADDRESS,
                                                         self.DEST_PORT_NO)
            command_echo = self.send_TIGER_Ch_CFG_Reg_CMD_PKT(TIGER_ID_param, COMMAND_STRING, array_to_send, self.DEST_IP_ADDRESS,
                                                         self.DEST_PORT_NO)
            if verbose_mode == 1:
                self.display_log_ChCfg_readback(command_echo, 1)
        else:
            for i in range(0, 64):
                ChCFGReg_setting_inst.set_target_channel(i)
                ChCFGReg_setting_inst.update_command_words()
                array_to_send = ChCFGReg_setting_inst.command_words
                command_echo = self.send_TIGER_Ch_CFG_Reg_CMD_PKT(TIGER_ID_param, COMMAND_STRING, array_to_send, self.DEST_IP_ADDRESS,
                                                             self.DEST_PORT_NO)
                if verbose_mode == 1:
                    self.display_log_ChCfg_readback(command_echo, 1)
        return command_echo


    def Set_GEMROC_TIGER_ch_TPEn(self, ChCFGReg_setting_inst, GEMROC_ID_param, TIGER_ID_param, Channel_ID_param,
                                 TP_disable_FE_param, TriggerMode_param):
        ChCFGReg_setting_inst.set_target_GEMROC(GEMROC_ID_param)
        ChCFGReg_setting_inst.set_target_TIGER(TIGER_ID_param)
        ChCFGReg_setting_inst.set_to_ALL_param(            0)  ## let's do multiple configuration under script control rather than under GEMROC NIOS2 processor control
        COMMAND_STRING = 'WR'
        ChCFGReg_setting_inst.set_command_code(COMMAND_STRING)
        if Channel_ID_param < 64:
            ChCFGReg_setting_inst.set_target_channel(Channel_ID_param)
            ChCFGReg_setting_inst.set_TP_disable_FE(TP_disable_FE_param)  # ACR 2018-03-04
            ChCFGReg_setting_inst.TriggerMode = TriggerMode_param
            ChCFGReg_setting_inst.update_command_words()
            array_to_send = ChCFGReg_setting_inst.command_words
            command_echo = self.send_TIGER_Ch_CFG_Reg_CMD_PKT(TIGER_ID_param, COMMAND_STRING, array_to_send, self.DEST_IP_ADDRESS,
                                                         self.DEST_PORT_NO)
        else:
            for i in range(0, 64):
                ChCFGReg_setting_inst.set_target_channel(i)
                ChCFGReg_setting_inst.set_TP_disable_FE(TP_disable_FE_param)
                ChCFGReg_setting_inst.TriggerMode = TriggerMode_param
                ChCFGReg_setting_inst.update_command_words()
                array_to_send = ChCFGReg_setting_inst.command_words
                command_echo = self.send_TIGER_Ch_CFG_Reg_CMD_PKT(TIGER_ID_param, COMMAND_STRING, array_to_send, self.DEST_IP_ADDRESS,
                                                             self.DEST_PORT_NO)

        last_command_echo = command_echo
        return last_command_echo


    def Set_Vth_T1(self,ChCFGReg_setting_inst, GEMROC_ID_param, TIGER_ID_param, Channel_ID_param, VthT1_param):
        # self.log_file.write("\n Setting VTH to {}, TIGER {}, CH {} \n".format(VthT1_param,TIGER_ID_param,Channel_ID_param))
        ChCFGReg_setting_inst.set_target_GEMROC(GEMROC_ID_param)
        ChCFGReg_setting_inst.set_target_TIGER(TIGER_ID_param)
        ChCFGReg_setting_inst.set_to_ALL_param(0)  ## let's do multiple configuration under script control rather than under GEMROC NIOS2 processor control
        ChCFGReg_setting_inst.set_Vth_T1(VthT1_param)
        COMMAND_STRING = 'WR'
        ChCFGReg_setting_inst.set_command_code(COMMAND_STRING)
        if Channel_ID_param < 64:
            ChCFGReg_setting_inst.set_target_channel(Channel_ID_param)
            ChCFGReg_setting_inst.update_command_words()
            array_to_send = ChCFGReg_setting_inst.command_words
            command_echo = self.send_TIGER_Ch_CFG_Reg_CMD_PKT(TIGER_ID_param, COMMAND_STRING, array_to_send, self.DEST_IP_ADDRESS,
                                                         self.DEST_PORT_NO)
        else:
            for i in range(0, 64):
                ChCFGReg_setting_inst.set_target_channel(i)
                ChCFGReg_setting_inst.update_command_words()
                array_to_send = ChCFGReg_setting_inst.command_words
                command_echo = self.send_TIGER_Ch_CFG_Reg_CMD_PKT(TIGER_ID_param, COMMAND_STRING, array_to_send, self.DEST_IP_ADDRESS,
                                                             self.DEST_PORT_NO)
        last_command_echo = command_echo
        return last_command_echo
    def Set_Vth_T1V2(self,ChCFGReg_setting_inst, GEMROC_ID_param, TIGER_ID_param, Channel_ID_param, VthT1_param):
        self.log_file.write("\n Setting VTH to {}, TIGER {}, CH {} \n".format(VthT1_param,TIGER_ID_param,Channel_ID_param))
        ChCFGReg_setting_inst.set_target_GEMROC(GEMROC_ID_param)
        ChCFGReg_setting_inst.set_target_TIGER(TIGER_ID_param)
        ChCFGReg_setting_inst.set_to_ALL_param(0)  ## let's do multiple configuration under script control rather than under GEMROC NIOS2 processor control
        ChCFGReg_setting_inst.set_Vth_T1(VthT1_param)
        print VthT1_param
        COMMAND_STRING = 'WR'
        ChCFGReg_setting_inst.set_command_code(COMMAND_STRING)
        ChCFGReg_setting_inst.set_target_channel(Channel_ID_param)
        ChCFGReg_setting_inst.update_command_words()
        array_to_send = ChCFGReg_setting_inst.command_words
        command_echo = self.send_TIGER_Ch_CFG_Reg_CMD_PKT(TIGER_ID_param, COMMAND_STRING, array_to_send, self.DEST_IP_ADDRESS,
                                                     self.DEST_PORT_NO)
        print binascii.b2a_hex(command_echo)
        last_command_echo = command_echo
        return last_command_echo

    def set_AVcasp_global(self, GCFGReg_setting_inst, GEMROC_ID_param, TIGER_ID_param, AVcasp_global_param):
        GCFGReg_setting_inst.set_target_GEMROC(GEMROC_ID_param)
        GCFGReg_setting_inst.set_target_TIGER(TIGER_ID_param)
        GCFGReg_setting_inst.set_AVcasp_global(AVcasp_global_param)
        COMMAND_STRING = 'WR'
        GCFGReg_setting_inst.set_command_code(COMMAND_STRING)
        GCFGReg_setting_inst.update_command_words()
        array_to_send = GCFGReg_setting_inst.command_words
        command_echo = self.send_TIGER_GCFG_Reg_CMD_PKT(TIGER_ID_param, COMMAND_STRING, array_to_send, self.DEST_IP_ADDRESS,
                                                   self.DEST_PORT_NO)
        print('\nAVcasp_global of Global CFG reg of TIGER%d of RESPONDING GEMROC%d: set to %d' % (
        TIGER_ID_param, GEMROC_ID_param, AVcasp_global_param))
        self.log_file.write('\nAVcasp_global of Global CFG reg of TIGER%d of RESPONDING GEMROC%d: set to %d' % (
        TIGER_ID_param, GEMROC_ID_param, AVcasp_global_param))
        return command_echo

    def SynchReset_to_TgtFEB(self, gemroc_DAQ_inst, GEMROC_ID_param, TargetFEB_param, To_ALL_param):
        gemroc_DAQ_inst.set_target_GEMROC(GEMROC_ID_param)
        gemroc_DAQ_inst.set_target_TCAM_ID(TargetFEB_param, To_ALL_param)
        COMMAND_STRING = 'CMD_GEMROC_DAQ_TIGER_SYNCH_RST'
        command_echo = self.send_GEMROC_DAQ_CMD(GEMROC_ID_param, gemroc_DAQ_inst, COMMAND_STRING)
        return command_echo


    def SynchReset_to_TgtTCAM(self, gemroc_DAQ_inst, GEMROC_ID_param, TargetTCAM_param, To_ALL_param):
        gemroc_DAQ_inst.set_target_GEMROC(GEMROC_ID_param)
        gemroc_DAQ_inst.set_target_TCAM_ID(TargetTCAM_param, To_ALL_param)
        COMMAND_STRING = 'CMD_GEMROC_DAQ_TCAM_SYNCH_RST'
        command_echo = self.send_GEMROC_DAQ_CMD(GEMROC_ID_param, gemroc_DAQ_inst, COMMAND_STRING)
        return command_echo

    ###-------Enables coommunication with a pattern of TIGER--and starts data trasmission-----------------------------###

    # def DAQ_set_and_TL_start(self, gemroc_DAQ_inst, GEMROC_ID_param, TCAM_Enable_pattern_param, Per_FEB_TP_Enable_pattern_param):
    #     gemroc_DAQ_inst.set_target_GEMROC(GEMROC_ID_param)
    #     gemroc_DAQ_inst.set_EN_TM_TCAM_pattern(TCAM_Enable_pattern_param)
    #     gemroc_DAQ_inst.set_TP_width(5)
    #     gemroc_DAQ_inst.set_AUTO_TP_EN_pattern(0x0)
    #     gemroc_DAQ_inst.set_Periodic_TP_EN_pattern(Per_FEB_TP_Enable_pattern_param)
    #     gemroc_DAQ_inst.set_TL_nTM_ACQ(1)
    #     gemroc_DAQ_inst.set_TP_Pos_nNeg(1)
    #     gemroc_DAQ_inst.set_TP_period(8)
    #     COMMAND_STRING = 'CMD_GEMROC_DAQ_CFG_WR'
    #     command_echo = self.send_GEMROC_DAQ_CMD(GEMROC_ID_param, gemroc_DAQ_inst, COMMAND_STRING)
    #     return command_echo



    def DAQ_set_Pause_Mode(self,gemroc_DAQ_inst, GEMROC_ID_param, DAQ_PauseMode_Enable_param):
        gemroc_DAQ_inst.set_target_GEMROC(GEMROC_ID_param)
        Dbg_funct_ctrl_bits_U4_localcopy = gemroc_DAQ_inst.get_Dbg_functions_ctrl_bits_LoNibble()
        Dbg_funct_ctrl_bits_U4_localcopy &= 0x7
        Dbg_funct_ctrl_bits_U4_localcopy |= ((DAQ_PauseMode_Enable_param & 0x1) << 3)  # acr 2018-04-24 keep a copy of the "debug functions control bits"; initialize it to 0
        print '\n Dbg_funct_ctrl_bits_U4_localcopy = %d' % Dbg_funct_ctrl_bits_U4_localcopy
        # gemroc_DAQ_inst.set_Dbg_functions_ctrl_bits_LoNibble(Dbg_funct_ctrl_bits_U4_localcopy)
        gemroc_DAQ_inst.set_Dbg_functions_ctrl_bits_LoNibble(Dbg_funct_ctrl_bits_U4_localcopy)
        COMMAND_STRING = 'CMD_GEMROC_DAQ_CFG_WR'
        command_echo = self.send_GEMROC_DAQ_CMD(GEMROC_ID_param, gemroc_DAQ_inst, COMMAND_STRING)
        return command_echo

    def DAQ_Toggle_Set_Pause_bit(self,gemroc_DAQ_inst, GEMROC_ID_param):
        gemroc_DAQ_inst.set_target_GEMROC(GEMROC_ID_param)
        Dbg_funct_ctrl_bits_U4_localcopy = gemroc_DAQ_inst.get_Dbg_functions_ctrl_bits_LoNibble()
        Dbg_funct_ctrl_bits_U4_localcopy &= 0xB
        print '\n Dbg_funct_ctrl_bits_U4_localcopy = %d' % Dbg_funct_ctrl_bits_U4_localcopy
        # gemroc_DAQ_inst.set_Dbg_functions_ctrl_bits_LoNibble(Dbg_funct_ctrl_bits_U4_localcopy)
        gemroc_DAQ_inst.set_Dbg_functions_ctrl_bits_LoNibble(Dbg_funct_ctrl_bits_U4_localcopy)
        COMMAND_STRING = 'CMD_GEMROC_DAQ_CFG_WR'
        command_echo = self.send_GEMROC_DAQ_CMD(GEMROC_ID_param, gemroc_DAQ_inst, COMMAND_STRING)
        Dbg_funct_ctrl_bits_U4_localcopy |= 0x4
        print '\n Dbg_funct_ctrl_bits_U4_localcopy = %d' % Dbg_funct_ctrl_bits_U4_localcopy
        gemroc_DAQ_inst.set_Dbg_functions_ctrl_bits_LoNibble(Dbg_funct_ctrl_bits_U4_localcopy)
        COMMAND_STRING = 'CMD_GEMROC_DAQ_CFG_WR'
        command_echo = self.send_GEMROC_DAQ_CMD(GEMROC_ID_param, gemroc_DAQ_inst, COMMAND_STRING)
        Dbg_funct_ctrl_bits_U4_localcopy &= 0xB
        print '\n Dbg_funct_ctrl_bits_U4_localcopy = %d' % Dbg_funct_ctrl_bits_U4_localcopy
        gemroc_DAQ_inst.set_Dbg_functions_ctrl_bits_LoNibble(Dbg_funct_ctrl_bits_U4_localcopy)
        COMMAND_STRING = 'CMD_GEMROC_DAQ_CFG_WR'
        command_echo = self.send_GEMROC_DAQ_CMD(GEMROC_ID_param, gemroc_DAQ_inst, COMMAND_STRING)
        return command_echo

    def DAQ_set_DAQck_source(self,gemroc_DAQ_inst, GEMROC_ID_param, DAQck_source_param):
        gemroc_DAQ_inst.set_target_GEMROC(GEMROC_ID_param)
        # Dbg_funct_ctrl_bits_U4_localcopy = gemroc_DAQ_inst.get_Dbg_functions_ctrl_bits_LoNibble()
        Dbg_funct_ctrl_bits_U4_localcopy = gemroc_DAQ_inst.get_Dbg_functions_ctrl_bits_LoNibble()
        Dbg_funct_ctrl_bits_U4_localcopy &= 0xE
        Dbg_funct_ctrl_bits_U4_localcopy |= ((DAQck_source_param & 0x1) << 0)  # acr 2018-04-24
        print '\n Dbg_funct_ctrl_bits_U4_localcopy = %d' % Dbg_funct_ctrl_bits_U4_localcopy
        # gemroc_DAQ_inst.set_Dbg_functions_ctrl_bits_LoNibble(Dbg_funct_ctrl_bits_U4_localcopy)
        gemroc_DAQ_inst.set_Dbg_functions_ctrl_bits_LoNibble(Dbg_funct_ctrl_bits_U4_localcopy)
        COMMAND_STRING = 'CMD_GEMROC_DAQ_CFG_WR'
        command_echo = self.send_GEMROC_DAQ_CMD(GEMROC_ID_param, gemroc_DAQ_inst, COMMAND_STRING)
        return command_echo

    def DAQ_set_TP_from_Ext_Trig(self,gemroc_DAQ_inst, GEMROC_ID_param, Enab_nDisab_TP_from_Ext_Trig_param):
        gemroc_DAQ_inst.set_target_GEMROC(GEMROC_ID_param)
        Dbg_funct_ctrl_bits_U4_localcopy = gemroc_DAQ_inst.get_Dbg_functions_ctrl_bits_LoNibble()
        Dbg_funct_ctrl_bits_U4_localcopy &= 0xD
        Dbg_funct_ctrl_bits_U4_localcopy |= ((Enab_nDisab_TP_from_Ext_Trig_param & 0x1) << 1)  # acr 2018-04-24
        print '\n Dbg_funct_ctrl_bits_U4_localcopy = %d' % Dbg_funct_ctrl_bits_U4_localcopy
        # gemroc_DAQ_inst.set_Dbg_functions_ctrl_bits_LoNibble(Dbg_funct_ctrl_bits_U4_localcopy)
        gemroc_DAQ_inst.set_Dbg_functions_ctrl_bits_LoNibble(Dbg_funct_ctrl_bits_U4_localcopy)
        COMMAND_STRING = 'CMD_GEMROC_DAQ_CFG_WR'
        command_echo = self.send_GEMROC_DAQ_CMD(GEMROC_ID_param, gemroc_DAQ_inst, COMMAND_STRING)
        return command_echo

    def MENU_set_L1_Lat_TM_Win_in_B3Ck_cycles(self, gemroc_DAQ_inst, GEMROC_ID_param, L1_lat_B3clk_param, TM_window_in_B3clk_param):  # acr 2018-07-23
        gemroc_DAQ_inst.set_target_GEMROC(GEMROC_ID_param)
        gemroc_DAQ_inst.set_L1_Lat_TM_Win_in_B3Ck_cycles(L1_lat_B3clk_param, TM_window_in_B3clk_param)
        COMMAND_STRING = 'CMD_GEMROC_DAQ_CFG_WR'
        command_echo = self.send_GEMROC_DAQ_CMD(GEMROC_ID_param, gemroc_DAQ_inst, COMMAND_STRING)
        return command_echo

    def set_Periodic_L1_EN_pattern(self,gemroc_DAQ_inst,Enab_nDisab_Periodic_L1_param):  # acr 2018-07-11 created definition
        Dbg_funct_ctrl_bits_U4_HI_localcopy = gemroc_DAQ_inst.get_Dbg_functions_ctrl_bits_HiNibble()
        Dbg_funct_ctrl_bits_U4_HI_localcopy &= 0xE
        Dbg_funct_ctrl_bits_U4_HI_localcopy |= ((Enab_nDisab_Periodic_L1_param & 0x1) << 0)
        print '\n Dbg_funct_ctrl_bits_U4_HI_localcopy = %d' % Dbg_funct_ctrl_bits_U4_HI_localcopy
        gemroc_DAQ_inst.set_Dbg_functions_ctrl_bits_HiNibble(Dbg_funct_ctrl_bits_U4_HI_localcopy)
        return

    ## ACR 2018-07-23 END

    def DAQ_set(self,gemroc_DAQ_inst, GEMROC_ID_param, TCAM_Enable_pattern_param, Per_FEB_TP_Enable_pattern_param, TP_repeat_burst_param, TP_Num_in_burst_param, TL_nTM_ACQ_param, Periodic_L1_Enable_param):
        gemroc_DAQ_inst.set_target_GEMROC(GEMROC_ID_param)
        gemroc_DAQ_inst.set_EN_TM_TCAM_pattern(TCAM_Enable_pattern_param)
        gemroc_DAQ_inst.set_TP_width(5)
        gemroc_DAQ_inst.set_AUTO_TP_EN_pattern(0x0)
        gemroc_DAQ_inst.set_Periodic_TP_EN_pattern(Per_FEB_TP_Enable_pattern_param)
        #gemroc_DAQ_inst.set_Periodic_L1_EN_pattern(Periodic_L1_Enable_param)
        self.set_Periodic_L1_EN_pattern(gemroc_DAQ_inst,Periodic_L1_Enable_param)
        gemroc_DAQ_inst.set_TL_nTM_ACQ(TL_nTM_ACQ_param)
        gemroc_DAQ_inst.set_TP_Pos_nNeg(1)
        gemroc_DAQ_inst.set_TP_period(8)
        number_of_repetitions = ((TP_repeat_burst_param & 0X1) << 9) + TP_Num_in_burst_param
        print 'DAQSET {0} {1} {2} {3} {4} {5} '.format(TCAM_Enable_pattern_param,Per_FEB_TP_Enable_pattern_param, TP_repeat_burst_param, TP_Num_in_burst_param, TL_nTM_ACQ_param,Periodic_L1_Enable_param) 
        print '\n number_of_repetitions = %03X' % number_of_repetitions
        print '\n number_of_repetitions = %d' % number_of_repetitions
        COMMAND_STRING = 'CMD_GEMROC_DAQ_CFG_WR'
        # acr 2018-04-023 command_echo = send_GEMROC_DAQ_CMD(GEMROC_ID_param, gemroc_DAQ_inst, COMMAND_STRING)
        command_echo = self.send_GEMROC_DAQ_CMD_num_rep(GEMROC_ID_param, gemroc_DAQ_inst, COMMAND_STRING, number_of_repetitions)
        return command_echo

    def DAQ_TIGER_SET(self, gemroc_DAQ_inst, GEMROC_ID_param, TCAM_Enable_pattern_param, Per_FEB_TP_Enable_pattern_param=0,
                TP_repeat_burst_param=0, TP_Num_in_burst_param=0, TL_nTM_ACQ_param=1, Periodic_L1_Enable_param=0):
        gemroc_DAQ_inst.set_target_GEMROC(GEMROC_ID_param)
        gemroc_DAQ_inst.set_EN_TM_TCAM_pattern(TCAM_Enable_pattern_param)
        gemroc_DAQ_inst.set_TP_width(5)
        gemroc_DAQ_inst.set_AUTO_TP_EN_pattern(0x0)
        gemroc_DAQ_inst.set_Periodic_TP_EN_pattern(Per_FEB_TP_Enable_pattern_param)
        # gemroc_DAQ_inst.set_Periodic_L1_EN_pattern(Periodic_L1_Enable_param)
        self.set_Periodic_L1_EN_pattern(gemroc_DAQ_inst,Periodic_L1_Enable_param)
        gemroc_DAQ_inst.set_TL_nTM_ACQ(1)
        gemroc_DAQ_inst.set_TP_Pos_nNeg(1)
        gemroc_DAQ_inst.set_TP_period(8)
        number_of_repetitions = ((TP_repeat_burst_param & 0X1) << 9) + TP_Num_in_burst_param
        print 'DAQSET {0} {1} {2} {3} {4} {5} '.format(TCAM_Enable_pattern_param, Per_FEB_TP_Enable_pattern_param,
                                                       TP_repeat_burst_param, TP_Num_in_burst_param,
                                                       TL_nTM_ACQ_param, Periodic_L1_Enable_param)
        print '\n number_of_repetitions = %03X' % number_of_repetitions
        print '\n number_of_repetitions = %d' % number_of_repetitions
        COMMAND_STRING = 'CMD_GEMROC_DAQ_CFG_WR'
        # acr 2018-04-023 command_echo = send_GEMROC_DAQ_CMD(GEMROC_ID_param, gemroc_DAQ_inst, COMMAND_STRING)
        command_echo = self.send_GEMROC_DAQ_CMD_num_rep(GEMROC_ID_param, gemroc_DAQ_inst, COMMAND_STRING,
                                                        number_of_repetitions)
        return command_echo

    ###-------Enables coommunication with a pattern of TIGER-----------------------------------------------------------###
    def TCAM_enable (self,gemroc_DAQ_inst,GEMROC_ID_param,TCAM_Enable_pattern_param):
        gemroc_DAQ_inst.set_target_GEMROC(GEMROC_ID_param)
        gemroc_DAQ_inst.set_EN_TM_TCAM_pattern(TCAM_Enable_pattern_param)
        COMMAND_STRING = 'CMD_GEMROC_DAQ_CFG_WR'
        command_echo = self.send_GEMROC_DAQ_CMD(GEMROC_ID_param, gemroc_DAQ_inst, COMMAND_STRING)
        return command_echo

###----##Start and stop data trasmission----------------------------------------------------------------------------###

    def TL_start(self, gemroc_DAQ_inst, GEMROC_ID_param):
        gemroc_DAQ_inst.set_target_GEMROC(GEMROC_ID_param)
        gemroc_DAQ_inst.set_TL_nTM_ACQ(1)
        COMMAND_STRING = 'CMD_GEMROC_DAQ_CFG_WR'
        command_echo = self.send_GEMROC_DAQ_CMD(GEMROC_ID_param, gemroc_DAQ_inst, COMMAND_STRING)
        return command_echo

    def TL_stop (self, gemroc_DAQ_inst, GEMROC_ID_param):
        gemroc_DAQ_inst.set_target_GEMROC(GEMROC_ID_param)
        gemroc_DAQ_inst.set_TL_nTM_ACQ(0)
        COMMAND_STRING = 'CMD_GEMROC_DAQ_CFG_WR'
        command_echo = self.send_GEMROC_DAQ_CMD(GEMROC_ID_param, gemroc_DAQ_inst, COMMAND_STRING)
        return command_echo
###-----------------------------------------------------------------------------------------------------------------###

    def Set_OV_OC_OT_PWR_CUT_EN_FLAGS(self, gemroc_inst_param, GEMROC_ID_param, FEB_OVC_EN_pattern_param,
                                      FEB_OVV_EN_pattern_param, FEB_OVT_EN_pattern_param, ROC_OVT_EN_param):
        gemroc_inst_param.FEB_OVC_EN_pattern = FEB_OVC_EN_pattern_param & 0xF
        gemroc_inst_param.FEB_OVV_EN_pattern = FEB_OVV_EN_pattern_param & 0xF
        gemroc_inst_param.FEB_OVT_EN_pattern = FEB_OVT_EN_pattern_param & 0xF
        gemroc_inst_param.ROC_OVT_EN = ROC_OVT_EN_param & 0x1
        COMMAND_STRING = 'CMD_GEMROC_LV_CFG_WR'
        command_echo = self.send_GEMROC_LV_CMD(GEMROC_ID_param, COMMAND_STRING)
        return command_echo


    def Set_OVVA_LIMIT(self, gemroc_inst_param, GEMROC_ID_param, FEB3_OVVA_thr_param, FEB2_OVVA_thr_param, FEB1_OVVA_thr_param,
                       FEB0_OVVA_thr_param):
        Vout_atten_factor = 0.5
        V_ADC_data_shift = 4
        shifted_V_ADC_res_mV_1LSB = 0.305 * (2 ** V_ADC_data_shift)
        FEB3_OVVA_thr_int = int((FEB3_OVVA_thr_param * Vout_atten_factor) / shifted_V_ADC_res_mV_1LSB)
        if FEB3_OVVA_thr_int <= 511:
            FEB3_OVVA_thr_Unsigned8 = FEB3_OVVA_thr_int
        else:
            FEB3_OVVA_thr_Unsigned8 = 511
        FEB2_OVVA_thr_int = int((FEB2_OVVA_thr_param * Vout_atten_factor) / shifted_V_ADC_res_mV_1LSB)
        if FEB2_OVVA_thr_int <= 511:
            FEB2_OVVA_thr_Unsigned8 = FEB2_OVVA_thr_int
        else:
            FEB2_OVVA_thr_Unsigned8 = 511
        FEB1_OVVA_thr_int = int((FEB1_OVVA_thr_param * Vout_atten_factor) / shifted_V_ADC_res_mV_1LSB)
        if FEB1_OVVA_thr_int <= 511:
            FEB1_OVVA_thr_Unsigned8 = FEB1_OVVA_thr_int
        else:
            FEB1_OVVA_thr_Unsigned8 = 511
        FEB0_OVVA_thr_int = int((FEB0_OVVA_thr_param * Vout_atten_factor) / shifted_V_ADC_res_mV_1LSB)
        if FEB0_OVVA_thr_int <= 511:
            FEB0_OVVA_thr_Unsigned8 = FEB0_OVVA_thr_int
        else:
            FEB0_OVVA_thr_Unsigned8 = 511
        gemroc_inst_param.A_OVV_LIMIT_FEB3 = FEB3_OVVA_thr_Unsigned8
        gemroc_inst_param.A_OVV_LIMIT_FEB2 = FEB2_OVVA_thr_Unsigned8
        gemroc_inst_param.A_OVV_LIMIT_FEB1 = FEB1_OVVA_thr_Unsigned8
        gemroc_inst_param.A_OVV_LIMIT_FEB0 = FEB0_OVVA_thr_Unsigned8
        COMMAND_STRING = 'CMD_GEMROC_LV_CFG_WR'
        command_echo = self.send_GEMROC_LV_CMD(GEMROC_ID_param, COMMAND_STRING)
        return command_echo


    def Set_OVVD_LIMIT(self, gemroc_inst_param, GEMROC_ID_param, FEB3_OVVD_thr_param, FEB2_OVVD_thr_param, FEB1_OVVD_thr_param,
                       FEB0_OVVD_thr_param):
        Vout_atten_factor = 0.5
        V_ADC_data_shift = 4
        shifted_V_ADC_res_mV_1LSB = 0.305 * (2 ** V_ADC_data_shift)
        FEB3_OVVD_thr_int = int((FEB3_OVVD_thr_param * Vout_atten_factor) / shifted_V_ADC_res_mV_1LSB)
        if FEB3_OVVD_thr_int <= 511:
            FEB3_OVVD_thr_Unsigned8 = FEB3_OVVD_thr_int
        else:
            FEB3_OVVD_thr_Unsigned8 = 511
        FEB2_OVVD_thr_int = int((FEB2_OVVD_thr_param * Vout_atten_factor) / shifted_V_ADC_res_mV_1LSB)
        if FEB2_OVVD_thr_int <= 511:
            FEB2_OVVD_thr_Unsigned8 = FEB2_OVVD_thr_int
        else:
            FEB2_OVVD_thr_Unsigned8 = 511
        FEB1_OVVD_thr_int = int((FEB1_OVVD_thr_param * Vout_atten_factor) / shifted_V_ADC_res_mV_1LSB)
        if FEB1_OVVD_thr_int <= 511:
            FEB1_OVVD_thr_Unsigned8 = FEB1_OVVD_thr_int
        else:
            FEB1_OVVD_thr_Unsigned8 = 511
        FEB0_OVVD_thr_int = int((FEB0_OVVD_thr_param * Vout_atten_factor) / shifted_V_ADC_res_mV_1LSB)
        if FEB0_OVVD_thr_int <= 511:
            FEB0_OVVD_thr_Unsigned8 = FEB0_OVVD_thr_int
        else:
            FEB0_OVVD_thr_Unsigned8 = 511
        gemroc_inst_param.D_OVV_LIMIT_FEB3 = FEB3_OVVD_thr_Unsigned8
        gemroc_inst_param.D_OVV_LIMIT_FEB2 = FEB2_OVVD_thr_Unsigned8
        gemroc_inst_param.D_OVV_LIMIT_FEB1 = FEB1_OVVD_thr_Unsigned8
        gemroc_inst_param.D_OVV_LIMIT_FEB0 = FEB0_OVVD_thr_Unsigned8
        COMMAND_STRING = 'CMD_GEMROC_LV_CFG_WR'
        command_echo = self.send_GEMROC_LV_CMD(GEMROC_ID_param, COMMAND_STRING)
        return command_echo


    def Set_OVCA_LIMIT(self, gemroc_inst_param, GEMROC_ID_param, FEB3_OVCA_thr_param, FEB2_OVCA_thr_param, FEB1_OVCA_thr_param,
                       FEB0_OVCA_thr_param):
        IADC_conv_fact_INA_GAIN_50 = 8.13
        IADC_conv_fact_INA_GAIN_200 = 8.13 / 4  ## mA per LSB
        if self.GEMROC_ID < 3:
            IADC_conv_fact_INA_GAIN = IADC_conv_fact_INA_GAIN_50
        else:
            IADC_conv_fact_INA_GAIN = IADC_conv_fact_INA_GAIN_200
        FEB3_OVCA_thr_int = int(FEB3_OVCA_thr_param / IADC_conv_fact_INA_GAIN)
        if FEB3_OVCA_thr_int <= 511:
            FEB3_OVCA_thr_U9 = FEB3_OVCA_thr_int
        else:
            FEB3_OVCA_thr_U9 = 511
        FEB2_OVCA_thr_int = int(FEB2_OVCA_thr_param / IADC_conv_fact_INA_GAIN)
        if FEB2_OVCA_thr_int <= 511:
            FEB2_OVCA_thr_U9 = FEB2_OVCA_thr_int
        else:
            FEB2_OVCA_thr_U9 = 511
        FEB1_OVCA_thr_int = int(FEB1_OVCA_thr_param / IADC_conv_fact_INA_GAIN)
        if FEB1_OVCA_thr_int <= 511:
            FEB1_OVCA_thr_U9 = FEB1_OVCA_thr_int
        else:
            FEB1_OVCA_thr_U9 = 511
        FEB0_OVCA_thr_int = int(FEB0_OVCA_thr_param / IADC_conv_fact_INA_GAIN)
        if FEB0_OVCA_thr_int <= 511:
            FEB0_OVCA_thr_U9 = FEB0_OVCA_thr_int
        else:
            FEB0_OVCA_thr_U9 = 511
        gemroc_inst_param.A_OVC_LIMIT_FEB3 = FEB3_OVCA_thr_U9
        gemroc_inst_param.A_OVC_LIMIT_FEB2 = FEB2_OVCA_thr_U9
        gemroc_inst_param.A_OVC_LIMIT_FEB1 = FEB1_OVCA_thr_U9
        gemroc_inst_param.A_OVC_LIMIT_FEB0 = FEB0_OVCA_thr_U9
        COMMAND_STRING = 'CMD_GEMROC_LV_CFG_WR'
        command_echo = self.send_GEMROC_LV_CMD(GEMROC_ID_param, COMMAND_STRING)
        return command_echo


    def Set_OVCD_LIMIT(self, gemroc_inst_param, GEMROC_ID_param, FEB3_OVCD_thr_param, FEB2_OVCD_thr_param, FEB1_OVCD_thr_param,
                       FEB0_OVCD_thr_param):
        IADC_conv_fact_INA_GAIN_50 = 8.13
        IADC_conv_fact_INA_GAIN_200 = 8.13 / 4  ## mA per LSB
        if self.GEMROC_ID < 3:
            IADC_conv_fact_INA_GAIN = IADC_conv_fact_INA_GAIN_50
        else:
            IADC_conv_fact_INA_GAIN = IADC_conv_fact_INA_GAIN_200
        FEB3_OVCD_thr_int = int(FEB3_OVCD_thr_param / IADC_conv_fact_INA_GAIN)
        if FEB3_OVCD_thr_int <= 511:
            FEB3_OVCD_thr_U9 = FEB3_OVCD_thr_int
        else:
            FEB3_OVCD_thr_U9 = 511
        FEB2_OVCD_thr_int = int(FEB2_OVCD_thr_param / IADC_conv_fact_INA_GAIN)
        if FEB2_OVCD_thr_int <= 511:
            FEB2_OVCD_thr_U9 = FEB2_OVCD_thr_int
        else:
            FEB2_OVCD_thr_U9 = 511
        FEB1_OVCD_thr_int = int(FEB1_OVCD_thr_param / IADC_conv_fact_INA_GAIN)
        if FEB1_OVCD_thr_int <= 511:
            FEB1_OVCD_thr_U9 = FEB1_OVCD_thr_int
        else:
            FEB1_OVCD_thr_U9 = 511
        FEB0_OVCD_thr_int = int(FEB0_OVCD_thr_param / IADC_conv_fact_INA_GAIN)
        if FEB0_OVCD_thr_int <= 511:
            FEB0_OVCD_thr_U9 = FEB0_OVCD_thr_int
        else:
            FEB0_OVCD_thr_U9 = 511
        gemroc_inst_param.D_OVC_LIMIT_FEB3 = FEB3_OVCD_thr_U9
        gemroc_inst_param.D_OVC_LIMIT_FEB2 = FEB2_OVCD_thr_U9
        gemroc_inst_param.D_OVC_LIMIT_FEB1 = FEB1_OVCD_thr_U9
        gemroc_inst_param.D_OVC_LIMIT_FEB0 = FEB0_OVCD_thr_U9
        COMMAND_STRING = 'CMD_GEMROC_LV_CFG_WR'
        command_echo = self.send_GEMROC_LV_CMD(GEMROC_ID_param, COMMAND_STRING)
        return command_echo


    def Set_OVTF_LIMIT(self, gemroc_inst_param, GEMROC_ID_param, FEB3_OVTF_thr_param, FEB2_OVTF_thr_param, FEB1_OVTF_thr_param,
                       FEB0_OVTF_thr_param):
        T_ref_PT1000 = 25.0
        V_ADC_at_25C = 247.2
        ADC_res_mV_1LSB = 0.305
        # acr 2018-03-15 BEGIN increased the sensitivity of temperature measurement and adjusted some parameters
        # T_ADC_data_shift = 3
        T_ADC_data_shift = 2  # acr 2018-03-15 increased the sensitivity
        T_MEASUREMENT_ROUTINE_VERSION = 2  ## ACR 2018-03-23 introduced T_MEASUREMENT_ROUTINE_VERSION
        if (T_MEASUREMENT_ROUTINE_VERSION < 2):
            T_ADC_data_shift = 3
        else:
            T_ADC_data_shift = 2
        ##calibration_offset_mV_FEB3 = 4.0
        ##calibration_offset_mV_FEB2 = 4.0
        ##calibration_offset_mV_FEB1 = 4.0
        ##calibration_offset_mV_FEB0 = 4.0
        calibration_offset_mV_FEB3 = 1.0
        calibration_offset_mV_FEB2 = 1.0
        calibration_offset_mV_FEB1 = 1.0
        calibration_offset_mV_FEB0 = 1.0
        # acr 2018-03-15 END increased the sensitivity of temperature measurement and adjusted some parameters
        shifted_T_ADC_res_mV_1LSB = ADC_res_mV_1LSB * (2 ** T_ADC_data_shift)
        deltaT_over_deltaV_ratio = 1.283
        FEB3_OVTF_thr_int = int((((
                                              FEB3_OVTF_thr_param - T_ref_PT1000) / deltaT_over_deltaV_ratio) + V_ADC_at_25C - calibration_offset_mV_FEB3) / shifted_T_ADC_res_mV_1LSB)
        if FEB3_OVTF_thr_int <= 255:
            FEB3_OVTF_thr_Unsigned8 = FEB3_OVTF_thr_int
        else:
            FEB3_OVTF_thr_Unsigned8 = 255
        FEB2_OVTF_thr_int = int((((
                                              FEB2_OVTF_thr_param - T_ref_PT1000) / deltaT_over_deltaV_ratio) + V_ADC_at_25C - calibration_offset_mV_FEB2) / shifted_T_ADC_res_mV_1LSB)
        if FEB2_OVTF_thr_int <= 255:
            FEB2_OVTF_thr_Unsigned8 = FEB2_OVTF_thr_int
        else:
            FEB2_OVTF_thr_Unsigned8 = 255
        FEB1_OVTF_thr_int = int((((
                                              FEB1_OVTF_thr_param - T_ref_PT1000) / deltaT_over_deltaV_ratio) + V_ADC_at_25C - calibration_offset_mV_FEB1) / shifted_T_ADC_res_mV_1LSB)
        if FEB1_OVTF_thr_int <= 255:
            FEB1_OVTF_thr_Unsigned8 = FEB1_OVTF_thr_int
        else:
            FEB1_OVTF_thr_Unsigned8 = 255
        FEB0_OVTF_thr_int = int((((
                                              FEB0_OVTF_thr_param - T_ref_PT1000) / deltaT_over_deltaV_ratio) + V_ADC_at_25C - calibration_offset_mV_FEB0) / shifted_T_ADC_res_mV_1LSB)
        if FEB0_OVTF_thr_int <= 255:
            FEB0_OVTF_thr_Unsigned8 = FEB0_OVTF_thr_int
        else:
            FEB0_OVTF_thr_Unsigned8 = 255
        gemroc_inst_param.OVT_LIMIT_FEB3 = FEB3_OVTF_thr_Unsigned8
        gemroc_inst_param.OVT_LIMIT_FEB2 = FEB2_OVTF_thr_Unsigned8
        gemroc_inst_param.OVT_LIMIT_FEB1 = FEB1_OVTF_thr_Unsigned8
        gemroc_inst_param.OVT_LIMIT_FEB0 = FEB0_OVTF_thr_Unsigned8
        COMMAND_STRING = 'CMD_GEMROC_LV_CFG_WR'
        command_echo = self.send_GEMROC_LV_CMD(GEMROC_ID_param, COMMAND_STRING)
        return command_echo


    def set_ROC_OVT_LIMIT(self, gemroc_inst_param, GEMROC_ID_param, ROC_OVT_thr_param):
        ## ACR 2018-03-15 please note that for this measurement 1 LSB = 1 Centigrade (approximately)
        if ROC_OVT_thr_param <= 63:
            ROC_OVT_thr_Unsigned6 = ROC_OVT_thr_param
        else:
            ROC_OVT_thr_Unsigned6 = 63
        gemroc_inst_param.ROC_OVT_LIMIT = ROC_OVT_thr_Unsigned6
        COMMAND_STRING = 'CMD_GEMROC_LV_CFG_WR'
        command_echo = self.send_GEMROC_LV_CMD(GEMROC_ID_param, COMMAND_STRING)
        return command_echo


    def display_log_GEMROC_LV_CfgReg_readback(self, command_echo_param, display_enable_param, log_enable_param):  # acr 2018-03-16 at IHEP
        L_array = array.array('L')  # L is an array of unsigned long
        L_array.fromstring(command_echo_param)
        L_array.byteswap()
        if (display_enable_param == 1):
            print ('\nList of LV related GEMROC Config Register parameters read back RESPONDING GEMROC%d:' % (
            ((L_array[0] >> 16) & 0X1f)))
            print ('\n  OVT_LIMIT_FEB3 : %d' % ((L_array[1] >> 22) & 0xFF))
            print ('\nD_OVV_LIMIT_FEB3 : %d' % ((L_array[1] >> 13) & 0x1FF))
            print ('\nD_OVC_LIMIT_FEB3 : %d' % ((L_array[1] >> 4) & 0x1FF))
            print ('\n  OVT_LIMIT_FEB2 : %d' % ((L_array[2] >> 22) & 0xFF))
            print ('\nD_OVV_LIMIT_FEB2 : %d' % ((L_array[2] >> 13) & 0x1FF))
            print ('\nD_OVC_LIMIT_FEB2 : %d' % ((L_array[2] >> 4) & 0x1FF))
            print ('\n  OVT_LIMIT_FEB1 : %d' % ((L_array[3] >> 22) & 0xFF))
            print ('\nD_OVV_LIMIT_FEB1 : %d' % ((L_array[3] >> 13) & 0x1FF))
            print ('\nD_OVC_LIMIT_FEB1 : %d' % ((L_array[3] >> 4) & 0x1FF))
            print ('\n  OVT_LIMIT_FEB0 : %d' % ((L_array[4] >> 22) & 0xFF))
            print ('\nD_OVV_LIMIT_FEB0 : %d' % ((L_array[4] >> 13) & 0x1FF))
            print ('\nD_OVC_LIMIT_FEB0 : %d' % ((L_array[4] >> 4) & 0x1FF))
            print ('\nA_OVV_LIMIT_FEB3 : %d' % ((L_array[5] >> 13) & 0x1FF))
            print ('\nA_OVC_LIMIT_FEB3 : %d' % ((L_array[5] >> 4) & 0x1FF))
            print ('\nA_OVV_LIMIT_FEB2 : %d' % ((L_array[6] >> 13) & 0x1FF))
            print ('\nA_OVC_LIMIT_FEB2 : %d' % ((L_array[6] >> 4) & 0x1FF))
            print ('\nA_OVV_LIMIT_FEB1 : %d' % ((L_array[7] >> 13) & 0x1FF))
            print ('\nA_OVC_LIMIT_FEB1 : %d' % ((L_array[7] >> 4) & 0x1FF))
            print ('\nA_OVV_LIMIT_FEB0 : %d' % ((L_array[8] >> 13) & 0x1FF))
            print ('\nA_OVC_LIMIT_FEB0 : %d' % ((L_array[8] >> 4) & 0x1FF))
            print ('\nROC_OVT_LIMIT : %d' % ((L_array[9] >> 24) & 0x3F))
            print ('\nXCVR_LPBCK_TST_EN = %d' % ((L_array[9] >> 18) & 0x1))
            print ('\nROC_OVT_EN = %d' % ((L_array[9] >> 16) & 0x1))
            print ('\nFEB_OVT_EN_pattern : %d' % ((L_array[9] >> 12) & 0xF))
            print ('\nFEB_OVV_EN_pattern : %d' % ((L_array[9] >> 8) & 0xF))
            print ('\nFEB_OVC_EN_pattern : %d' % ((L_array[9] >> 4) & 0xF))
            print ('\nFEB_PWR_EN_pattern : %d' % ((L_array[9] >> 0) & 0xF))
            print ('\nTIMING_DLY_FEB3 : %d' % ((L_array[10] >> 24) & 0x3F))
            print ('\nTIMING_DLY_FEB2 : %d' % ((L_array[10] >> 16) & 0x3F))
            print ('\nTIMING_DLY_FEB1 : %d' % ((L_array[10] >> 8) & 0x3F))
            print ('\nTIMING_DLY_FEB0 : %d' % ((L_array[10] >> 0) & 0x3F))
        if (log_enable_param == 1):
            self.log_file.write(
                '\nList of LV related GEMROC Config Register parameters read back RESPONDING GEMROC%d:' % (
                ((L_array[0] >> 16) & 0X1f)))
            self.log_file.write('\n  OVT_LIMIT_FEB3 : %d' % ((L_array[1] >> 22) & 0xFF))
            self.log_file.write('\nD_OVV_LIMIT_FEB3 : %d' % ((L_array[1] >> 13) & 0x1FF))
            self.log_file.write('\nD_OVC_LIMIT_FEB3 : %d' % ((L_array[1] >> 4) & 0x1FF))
            self.log_file.write('\n  OVT_LIMIT_FEB2 : %d' % ((L_array[2] >> 22) & 0xFF))
            self.log_file.write('\nD_OVV_LIMIT_FEB2 : %d' % ((L_array[2] >> 13) & 0x1FF))
            self.log_file.write('\nD_OVC_LIMIT_FEB2 : %d' % ((L_array[2] >> 4) & 0x1FF))
            self.log_file.write('\n  OVT_LIMIT_FEB1 : %d' % ((L_array[3] >> 22) & 0xFF))
            self.log_file.write('\nD_OVV_LIMIT_FEB1 : %d' % ((L_array[3] >> 13) & 0x1FF))
            self.log_file.write('\nD_OVC_LIMIT_FEB1 : %d' % ((L_array[3] >> 4) & 0x1FF))
            self.log_file.write('\n  OVT_LIMIT_FEB0 : %d' % ((L_array[4] >> 22) & 0xFF))
            self.log_file.write('\nD_OVV_LIMIT_FEB0 : %d' % ((L_array[4] >> 13) & 0x1FF))
            self.log_file.write('\nD_OVC_LIMIT_FEB0 : %d' % ((L_array[4] >> 4) & 0x1FF))
            self.log_file.write('\nA_OVV_LIMIT_FEB3 : %d' % ((L_array[5] >> 13) & 0x1FF))
            self.log_file.write('\nA_OVC_LIMIT_FEB3 : %d' % ((L_array[5] >> 4) & 0x1FF))
            self.log_file.write('\nA_OVV_LIMIT_FEB2 : %d' % ((L_array[6] >> 13) & 0x1FF))
            self.log_file.write('\nA_OVC_LIMIT_FEB2 : %d' % ((L_array[6] >> 4) & 0x1FF))
            self.log_file.write('\nA_OVV_LIMIT_FEB1 : %d' % ((L_array[7] >> 13) & 0x1FF))
            self.log_file.write('\nA_OVC_LIMIT_FEB1 : %d' % ((L_array[7] >> 4) & 0x1FF))
            self.log_file.write('\nA_OVV_LIMIT_FEB0 : %d' % ((L_array[8] >> 13) & 0x1FF))
            self.log_file.write('\nA_OVC_LIMIT_FEB0 : %d' % ((L_array[8] >> 4) & 0x1FF))
            self.log_file.write('\nROC_OVT_LIMIT : %d' % ((L_array[9] >> 24) & 0x3F))
            self.log_file.write('\nXCVR_LPBCK_TST_EN = %d' % ((L_array[9] >> 18) & 0x1))
            self.log_file.write('\nROC_OVT_EN = %d' % ((L_array[9] >> 16) & 0x1))
            self.log_file.write('\nFEB_OVT_EN_pattern : %d' % ((L_array[9] >> 12) & 0xF))
            self.log_file.write('\nFEB_OVV_EN_pattern : %d' % ((L_array[9] >> 8) & 0xF))
            self.log_file.write('\nFEB_OVC_EN_pattern : %d' % ((L_array[9] >> 4) & 0xF))
            self.log_file.write('\nFEB_PWR_EN_pattern : %d' % ((L_array[9] >> 0) & 0xF))
            self.log_file.write('\nTIMING_DLY_FEB3 : %d' % ((L_array[10] >> 24) & 0x3F))
            self.log_file.write('\nTIMING_DLY_FEB2 : %d' % ((L_array[10] >> 16) & 0x3F))
            self.log_file.write('\nTIMING_DLY_FEB1 : %d' % ((L_array[10] >> 8) & 0x3F))
            self.log_file.write('\nTIMING_DLY_FEB0 : %d' % ((L_array[10] >> 0) & 0x3F))


    def Read_GEMROC_LV_CfgReg(self, gemroc_inst_param, GEMROC_ID_param):
        COMMAND_STRING = 'CMD_GEMROC_LV_CFG_RD'
        command_echo = self.send_GEMROC_LV_CMD(GEMROC_ID_param, COMMAND_STRING)
        return command_echo

    def set_sampleandhold_mode(self, ChCFGReg_setting_inst, GEMROC_ID_param, TIGER_ID_param, Channel_ID_param):
        ChCFGReg_setting_inst.set_target_GEMROC(GEMROC_ID_param)
        ChCFGReg_setting_inst.set_target_TIGER(TIGER_ID_param)
        ChCFGReg_setting_inst.set_to_ALL_param(0)  ## let's do multiple configuration under script control rather than under GEMROC NIOS2 processor control
        COMMAND_STRING = 'WR'
        ChCFGReg_setting_inst.set_command_code(COMMAND_STRING)
        if Channel_ID_param < 64:
            ChCFGReg_setting_inst.set_target_channel(Channel_ID_param)
            ChCFGReg_setting_inst.sample_and_hold_mode()  # ACR 2018-03-04
            ChCFGReg_setting_inst.update_command_words()
            array_to_send = ChCFGReg_setting_inst.command_words
            command_echo = self.send_TIGER_Ch_CFG_Reg_CMD_PKT(TIGER_ID_param, COMMAND_STRING, array_to_send,
                                                              self.DEST_IP_ADDRESS,
                                                              self.DEST_PORT_NO)
        else:
            for i in range(0, 64):
                ChCFGReg_setting_inst.set_target_channel(i)
                ChCFGReg_setting_inst.sample_and_hold_mode()  # ACR 2018-03-04
                ChCFGReg_setting_inst.update_command_words()
                array_to_send = ChCFGReg_setting_inst.command_words
                command_echo = self.send_TIGER_Ch_CFG_Reg_CMD_PKT(TIGER_ID_param, COMMAND_STRING, array_to_send,
                                                                  self.DEST_IP_ADDRESS,
                                                                  self.DEST_PORT_NO)
        last_command_echo = command_echo
        return last_command_echo

    def display_log_GEMROC_DAQ_CfgReg_readback(self, command_echo_param, display_enable_param, log_enable_param):  # acr 2018-03-16 at IHEP
        L_array = array.array('I')  # L is an array of unsigned long
        L_array.fromstring(command_echo_param)
        L_array.byteswap()
        if (display_enable_param == 1):
            print ('\nList of DAQ related GEMROC Config Register parameters read back RESPONDING GEMROC%d:' % (((L_array[0] >> 16) & 0X1f)))
            print ('\nUDP_DATA_DESTINATION_IPADDR: %d' % ((L_array[0] >> 8) & 0xFF))
            print ('\nUDP_DATA_DESTINATION_IPPORT: %d' % ((L_array[4] >> 26) & 0xF))
            print ('\nL1_latency_OBSOLETE: %d' % ((L_array[1] >> 20) & 0x3FF))
            print ('\nTP_width: %d' % ((L_array[1] >> 16) & 0xF))
            print ('\nL1_win_upper_edge_offset: %d' % ((L_array[1] >> 0) & 0xFFFF))
            print ('\nL1_period: %d' % ((L_array[2] >> 20) & 0x3FF))
            # print ('\nPeriodic_L1_EN_pattern: %X' % ((L_array[2] >> 16) & 0xF))
            print ('\nDbg_functions_ctrl_bits_HiNibble: %X' % ((L_array[2] >> 16) & 0xF))
            print ('\nL1_win_lower_edge_offset: %d' % ((L_array[2] >> 0) & 0xFFFF))
            print ('\nTP_period: %d' % ((L_array[3] >> 20) & 0x3FF))
            print ('\nPeriodic_TP_EN_pattern: %X' % ((L_array[3] >> 16) & 0xF))
            print ('\nDbg_functions_ctrl_bits_LoNibble: %X' % ((L_array[3] >> 12) & 0xF))
            print ('\nTL_nTM_ACQ: %d' % ((L_array[3] >> 11) & 0x1))
            print ('\nAUTO_L1_EN: %d' % ((L_array[3] >> 10) & 0x1))
            print ('\nAUTO_TP_EN: %d' % ((L_array[3] >> 9) & 0x1))
            print ('\nTP_Pos_nNeg: %d' % ((L_array[3] >> 8) & 0x1))
            print ('\nEN_TM_TCAM_pattern: %X' % ((L_array[3] >> 0) & 0xFF))
            # ACR 2018-04-26 print ('\nnumber_of_repetitions: %d'        %( (L_array[4]>>16)&0x3FF ) )
            print ('\nTest Pulse Burst Repeat Enable: %d' % ((L_array[4] >> 25) & 0x1))  # ACR 2018-04-26 "TP_repeat_burst": Test Pulse repeat Enable
            print ('\nNumber of TP in one burst: %d' % (((L_array[4] >> 16) & 0x1FF) << 2))  # ACR 2018-04-26
            print ('\ntarget_TCAM_ID: %d' % ((L_array[4] >> 8) & 0x3))
            print ('\nto_ALL_TCAM_enable: %d' % ((L_array[4] >> 6) & 0x1))
            print ('\ntop_daq_pll_locked: %d' % ((L_array[4] >> 0) & 0x1))  # acr 2018-04-26
            print ('\nEnable_DAQPause_Until_First_Trigger: %d' % ((L_array[3] >> 15) & 0x1))  # acr 2018-04-26
            print ('\nDAQPause_Set: %d' % ((L_array[3] >> 14) & 0x1))  # acr 2018-04-26
            print ('\nTpulse_generation_w_ext_trigger_enable: %d' % ((L_array[3] >> 13) & 0x1))  # acr 2018-04-26
            print ('\nEXT_nINT_B3clk: %d' % ((L_array[3] >> 12) & 0x1))  # acr 2018-04-26
        if (log_enable_param == 1):
            self.log_file.write('\nList of DAQ related GEMROC Config Register parameters read back RESPONDING GEMROC%d:' % (((L_array[0] >> 16) & 0X1f)))
            self.log_file.write('\nUDP_DATA_DESTINATION_IPADDR: %d' % ((L_array[0] >> 8) & 0xFF))
            self.log_file.write('\nUDP_DATA_DESTINATION_IPPORT: %d' % ((L_array[4] >> 26) & 0xF))
            self.log_file.write('\nL1_latency_OBSOLETE: %d' % ((L_array[1] >> 20) & 0x3FF))
            self.log_file.write('\nTP_width: %d' % ((L_array[1] >> 16) & 0xF))
            self.log_file.write('\nL1_win_upper_edge_offset: %d' % ((L_array[1] >> 0) & 0xFFFF))
            self.log_file.write('\nL1_period: %d' % ((L_array[2] >> 20) & 0x3FF))
            self.log_file.write('\nDbg_functions_ctrl_bits_HiNibble: %X' % ((L_array[2] >> 16) & 0xF))
            self.log_file.write('\nL1_win_lower_edge_offset: %d' % ((L_array[2] >> 0) & 0xFFFF))
            self.log_file.write('\nTP_period: %d' % ((L_array[3] >> 20) & 0x3FF))
            self.log_file.write('\nPeriodic_TP_EN_pattern: %X' % ((L_array[3] >> 16) & 0xF))
            self.log_file.write('\nDbg_functions_ctrl_bits_LoNibble: %X' % ((L_array[3] >> 12) & 0xF))
            self.log_file.write('\nTL_nTM_ACQ: %d' % ((L_array[3] >> 11) & 0x1))
            self.log_file.write('\nAUTO_L1_EN: %d' % ((L_array[3] >> 10) & 0x1))
            self.log_file.write('\nAUTO_TP_EN: %d' % ((L_array[3] >> 9) & 0x1))
            self.log_file.write('\nTP_Pos_nNeg: %d' % ((L_array[3] >> 8) & 0x1))
            self.log_file.write('\nEN_TM_TCAM_pattern: %X' % ((L_array[3] >> 0) & 0xFF))
            # ACR 2018-04-26 self.log_file.write('\nnumber_of_repetitions: %d'        %( (L_array[4]>>16)&0x3FF ) )
            self.log_file.write('\nTest Pulse Burst Repeat Enable: %d' % ((L_array[4] >> 25) & 0x1))  # ACR 2018-04-26 "TP_repeat_burst": Test Pulse repeat Enable
            self.log_file.write('\nNumber of TP in one burst: %d' % (((L_array[4] >> 16) & 0x1FF) << 2))  # ACR 2018-04-26
            self.log_file.write('\ntarget_TCAM_ID: %d' % ((L_array[4] >> 8) & 0x3))
            self.log_file.write('\nto_ALL_TCAM_enable: %d' % ((L_array[4] >> 6) & 0x1))
            self.log_file.write('\ntop_daq_pll_locked: %d' % ((L_array[4] >> 0) & 0x1))  # acr 2018-04-26
            self.log_file.write('\nEnable_DAQPause_Until_First_Trigger: %d' % ((L_array[3] >> 15) & 0x1))  # acr 2018-04-26
            self.log_file.write('\nDAQPause_Set: %d' % ((L_array[3] >> 14) & 0x1))  # acr 2018-04-26
            self.log_file.write('\nTpulse_generation_w_ext_trigger_enable: %d' % ((L_array[3] >> 13) & 0x1))  # acr 2018-04-26
            self.log_file.write('\nEXT_nINT_B3clk: %d' % ((L_array[3] >> 12) & 0x1))  # acr 2018-04-26


    def Read_GEMROC_DAQ_CfgReg(self, gemroc_inst_param, GEMROC_ID_param):
        COMMAND_STRING = 'CMD_GEMROC_DAQ_CFG_RD'
        command_echo = self.send_GEMROC_DAQ_CMD(GEMROC_ID_param, gemroc_inst_param, COMMAND_STRING)
        return command_echo

    def Load_VTH_fromfile(self, ChCFGReg_setting_inst, GEMROC_ID_param, TIGER_ID_param, number_sigma, offset, save_on_LOG=False):
        file_p=self.conf_folder+sep+"GEMROC{}_Chip{}.thr".format(self.GEMROC_ID,TIGER_ID_param)
        self.log_file.write("\n Setting VTH from file in  TIGER {}\n".format(TIGER_ID_param))


        thr0=np.loadtxt(file_p,)
        thr=np.rint(thr0[:,0]) - np.rint(thr0[:,1])*number_sigma+offset

        for c in range (0,64):
            if thr[c]<0 or thr[c]==0:

                thr[c]=0
            if thr[c]>63:
                thr[c]=63

        print ("Thr={}".format(thr))
        for i in range(0, 64):
            binascii.b2a_hex(self.Set_Vth_T1(ChCFGReg_setting_inst,GEMROC_ID_param,TIGER_ID_param,i,int(thr[i])))


        if save_on_LOG:
            name="."+sep+"log_folder"+sep+"THR_LOG{}_TIGER_{}.txt".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),TIGER_ID_param)
            np.savetxt(name,np.c_[thr])

        return 0

    def Load_VTH_fromfile_autotuned(self,ChCFGReg_setting_inst, GEMROC_ID_param, TIGER_ID_param):
        file_p=self.conf_folder+sep+"GEMROC{}_TIGER_{}_autotuned.thr".format(self.GEMROC_ID,TIGER_ID_param)
        self.log_file.write("\n Setting VTH from file autotuned in  TIGER {}\n".format(TIGER_ID_param))


        thr=np.loadtxt(file_p,)

        for c in range (0,64):
            if thr[c]<0 or thr[c]==0:

                thr[c]=0
            if thr[c]>63:
                thr[c]=63

        print ("Thr={}".format(thr))
        for i in range(0, 64):
            binascii.b2a_hex(self.Set_Vth_T1(ChCFGReg_setting_inst,GEMROC_ID_param,TIGER_ID_param,i,int(thr[i])))

        name="."+sep+"log_folder"+sep+"THR_LOG{}_TIGER_{}.txt".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),TIGER_ID_param)
        np.savetxt(name,np.c_[thr])

        return 0
    def Load_VTH_fromMatrix(self,ChCFGReg_setting_inst, GEMROC_ID_param, TIGER_ID_param,vthr_matrix):
        for i in range(0, 64):
            binascii.b2a_hex(self.Set_Vth_T1(ChCFGReg_setting_inst, GEMROC_ID_param, TIGER_ID_param, i,
                                             int(vthr_matrix[TIGER_ID_param, i])))

        name = "." + sep + "log_folder" + sep + "THR_LOG{}_TIGER_{}.txt".format(
            datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"), TIGER_ID_param)

        return 0



    def TP_ENABLE(self,gemroc_DAQ_inst,GEMROC_ID_param,TP_PATTERN): #Enable test pulses from FPGA
        gemroc_DAQ_inst.set_target_GEMROC(GEMROC_ID_param)
        gemroc_DAQ_inst.set_TP_width(5)
        gemroc_DAQ_inst.set_AUTO_TP_EN_pattern(0x0)
        gemroc_DAQ_inst.set_Periodic_TP_EN_pattern(TP_PATTERN)
        gemroc_DAQ_inst.set_TP_Pos_nNeg(1)
        gemroc_DAQ_inst.set_TP_period(8)
        COMMAND_STRING = 'CMD_GEMROC_DAQ_CFG_WR'
        command_echo = self.send_GEMROC_DAQ_CMD(GEMROC_ID_param, gemroc_DAQ_inst, COMMAND_STRING)
        return command_echo

    def DAQ_set_TP_from_L1Chk(self, gemroc_DAQ_inst, GEMROC_ID_param, Enab_nDisab_TP_from_L1Chk_param):  # acr 2018-07-11 created definition
        gemroc_DAQ_inst.set_target_GEMROC(GEMROC_ID_param)
        Dbg_funct_ctrl_bits_U4_HI_localcopy = gemroc_DAQ_inst.get_Dbg_functions_ctrl_bits_HiNibble()
        Dbg_funct_ctrl_bits_U4_HI_localcopy &= 0xD
        Dbg_funct_ctrl_bits_U4_HI_localcopy |= ((Enab_nDisab_TP_from_L1Chk_param & 0x1) << 1)
        print '\n Dbg_funct_ctrl_bits_U4_HI_localcopy = %d' % Dbg_funct_ctrl_bits_U4_HI_localcopy
        gemroc_DAQ_inst.set_Dbg_functions_ctrl_bits_HiNibble(Dbg_funct_ctrl_bits_U4_HI_localcopy)
        COMMAND_STRING = 'CMD_GEMROC_DAQ_CFG_WR'
        command_echo = self.send_GEMROC_DAQ_CMD(GEMROC_ID_param, gemroc_DAQ_inst, COMMAND_STRING)
        return command_echo

    ## acr 2018-08-08 BEGIN
    def XCVR_Loopback_Test(self, gemroc_DAQ_inst, GEMROC_ID_param, NumWordToSend_param):
        gemroc_DAQ_inst.set_target_GEMROC(GEMROC_ID_param)
        backup_copy_num_rep = gemroc_DAQ_inst.number_of_repetitions
        print '\nbackup copy of number_of_repetitions: %d' % backup_copy_num_rep
        COMMAND_STRING = 'CMD_GEMROC_DAQ_XCVR_LPBCK_TEST'
        # gemroc_DAQ_inst.set_command_code(COMMAND_STRING)
        command_echo = self.send_GEMROC_DAQ_CMD_num_rep(GEMROC_ID_param, gemroc_DAQ_inst, COMMAND_STRING, NumWordToSend_param)
        print '\ncurrent gemroc_DAQ_inst.number_of_repetitions: %d' % gemroc_DAQ_inst.number_of_repetitions
        gemroc_DAQ_inst.number_of_repetitions = backup_copy_num_rep
        print '\nrestored gemroc_DAQ_inst.number_of_repetitions: %d' % gemroc_DAQ_inst.number_of_repetitions
        return command_echo
    ## acr 2018-08-08 END
    def Channel_set_check(self, command_echo_param, command_read_param,log): #check for differnces between configuration and lecture
        L_array = array.array('I')  # L is an array of unsigned long
        L_array.fromstring(command_echo_param)
        L_array.byteswap()

        L_array2 = array.array('I')  # L is an array of unsigned long
        L_array2.fromstring(command_read_param)
        L_array2.byteswap()

        if ((L_array[9] >> 0) & 0X3F) != ((L_array2[9] >> 0) & 0X3F):
            print "\nWrong channel"
            with open(log, 'a') as log_file:
                log_file.write("\nWrong channel")

        if ((L_array[9] >> 8) & 0X7) != ((L_array2[9] >> 8) & 0X7):
            print "\n Wrong TIGER"
            with open(log, 'a') as log_file:
                log_file.write("\nWrong TIGER")
        if ((L_array[9] >> 16) &  0X1f) != ((L_array2[9] >> 16)  & 0X1f):
            print "\n Wrong GEMROC"
            with open(log, 'a') as log_file:
                log_file.write("\nWrong GEMROC")
        if (((L_array[9] >> 16) & 0Xff)) != (((L_array2[9] >> 16) & 0Xff)):
            print "\n Error flag rised"
            with open(log, 'a') as log_file:
                log_file.write("\nError flag rised")
        if ((L_array[4] >> 16) & 0x7F) != ((L_array2[4] >> 16) & 0x7F):
            print "\n MaxIntegTime worng"
            with open(log, 'a') as log_file:
                log_file.write("\nMaxIntegTime worng, found {}\n".format((L_array2[4] >> 16)))
        if ((L_array[3] >> 0) & 0x3F) != ((L_array2[3] >> 0) & 0x3F):
            print "\n VTH wrong"
            with open(log, 'a') as log_file:
                log_file.write("VTH wrong, {} instead of {}\n ".format(((L_array2[3] >> 0) & 0x3F),((L_array[3] >> 0) & 0x3F)))
        if ((L_array[3] >> 8) & 0x3F) != ((L_array2[3] >> 8) & 0x3F):
            print "\n VTH2 wrong"
            with open(log, 'a') as log_file:
                log_file.write("VTH2 wrong, {} instead of {}\n ".format(((L_array2[3] >> 8) & 0x3F),((L_array[3] >> 8) & 0x3F)))
        if ((L_array[8] >> 16) & 0x3) != ((L_array2[8] >> 16) & 0x3):
            print "\n TRIGGER mode WRONG"
            with open(log, 'a') as log_file:
                log_file.write("TRIGGER mode WRONG, {} instead of {}\n ".format(((L_array2[8] >> 16) & 0x3),((L_array[8] >> 16) & 0x3)))
       #
        # print('\n DisableHyst: %d' % ((L_array[1] >> 24) & 0x1))
        # print('\n T2Hyst: %d' % ((L_array[1] >> 16) & 0x7))
        # print('\n T1Hyst: %d' % ((L_array[1] >> 8) & 0x7))
        # print('\n Ch63ObufMSB: %d' % ((L_array[1] >> 0) & 0x1))
        # print('\n TP_disable_FE: %d' % ((L_array[2] >> 24) & 0x1))
        # print('\n TDC_IB_E: %d' % ((L_array[2] >> 16) & 0xF))
        # print('\n TDC_IB_T: %d' % ((L_array[2] >> 8) & 0xF))
        # print('\n Integ: %d' % ((L_array[2] >> 0) & 0x1))
        # print('\n PostAmpGain: %d' % ((L_array[3] >> 24) & 0x3))
        # print('\n FE_delay: %d' % ((L_array[3] >> 16) & 0x1F))
        # print('\n Vth_T2: %d' % ((L_array[3] >> 8) & 0x3F))
        # print('\n Vth_T1: %d' % ((L_array[3] >> 0) & 0x3F))
        # print('\n QTx2Enable: %d' % ((L_array[4] >> 24) & 0x1))
        # print('\n MaxIntegTime: %d' % ((L_array[4] >> 16) & 0x7F))
        # print('\n MinIntegTime: %d' % ((L_array[4] >> 8) & 0x7F))
        # print('\n TriggerBLatched: %d' % ((L_array[4] >> 0) & 0x1))
        # print('\n QdcMode: %d' % ((L_array[5] >> 24) & 0x1))
        # print('\n BranchEnableT: %d' % ((L_array[5] >> 16) & 0x1))
        # print('\n BranchEnableEQ: %d' % ((L_array[5] >> 8) & 0x1))
        # print('\n TriggerMode2B: %d' % ((L_array[5] >> 0) & 0x7))
        # print('\n TriggerMode2Q: %d' % ((L_array[6] >> 24) & 0x3))
        # print('\n TriggerMode2E: %d' % ((L_array[6] >> 16) & 0x7))
        # print('\n TriggerMode2T: %d' % ((L_array[6] >> 8) & 0x3))
        # print('\n TACMinAge: %d' % ((L_array[6] >> 0) & 0x1F))
        # print('\n TACMaxAge: %d' % ((L_array[7] >> 24) & 0x1F))
        # print('\n CounterMode: %d' % ((L_array[7] >> 16) & 0xF))
        # print('\n DeadTime: %d' % ((L_array[7] >> 8) & 0x3F))
        # print('\n SyncChainLen: %d' % ((L_array[7] >> 0) & 0x3))
        # print('\n Ch_DebugMode: %d' % ((L_array[8] >> 24) & 0x3))
        # print('\n TriggerMode: %d' % ((L_array[8] >> 16) & 0x3))