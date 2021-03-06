from lib import GEM_COM_classes as COM_class
from lib import GEM_ANALYSIS_classes as AN_CLASS, GEM_CONF_classes as GEM_CONF
import binascii
import sys
import threading ## acr 2018-02-21
import Queue     ## acr 2018-02-21
import os        ## acr 2018-02-21
import datetime
import time
import array

default_arg_needed = 0
TARGET_GEMROC_ID_param = 0
TARGET_FEB_PWR_PATTERN_param = 0
IVT_LOG_PERIOD_SECONDS = 20
IVT_LOG_ENABLE = 1

OS = sys.platform
if OS == 'win32':
	sep = '\\'
elif OS == 'linux2':
	sep = '/'
else:
	print("ERROR: OS {} non compatible".format(OS))
	sys.exit()


if len(sys.argv) < 3:
    print"\n GEMROC_TIGER_CFG argument list: <Target_GEMROC: 1 thru 22> <Target_FEB_PWR_EN_pattern(Hex):0x0 thru 0xF>"
    ##    exit()
    default_arg_needed = 1
if default_arg_needed == 1:
    TARGET_GEMROC_ID_param = 2
    TARGET_FEB_PWR_PATTERN_param = 0x1
else:
    TARGET_GEMROC_ID_param = int(sys.argv[1])
    TARGET_FEB_PWR_PATTERN_param = int(sys.argv[2], 16)

GEMROC_ID = TARGET_GEMROC_ID_param
FEB_PWR_EN_pattern = TARGET_FEB_PWR_PATTERN_param
GEM_COM1= COM_class.communication(GEMROC_ID)  #Create communication class

## creating an instance of the TIGER global configuration settings object
##    parameter list:
##    TARGET_GEMROC_ID_param = 0,
##    cfg_filename_param = "default_g_cfg_2018_all_big_endian.txt"
default_g_inst_settigs_filename = GEM_COM1.conf_folder+sep+"TIGER_def_g_cfg_2018.txt"
g_inst = GEM_CONF.g_reg_settings(GEMROC_ID, default_g_inst_settigs_filename)

#### creating an instance of the channel configuration settings object
##    parameter list:
##    TARGET_GEMROC_ID_param = 0,
##    cfg_filename_param = "default_ch_cfg_mainz.txt"
default_ch_inst_settigs_filename = GEM_COM1.conf_folder+sep+"TIGER_def_ch_cfg_2018.txt"
c_inst = GEM_CONF.ch_reg_settings(GEMROC_ID, default_ch_inst_settigs_filename)


menu_string = "-- GEMROC {} --\n".format(GEMROC_ID)+"\
\nGEMROC_SCRIPTS V2. INFN-FE/INFN-TO\
\nMENU: \
\n(P)EW     <PWR_EN_PATTERN>(Hex, 0x0 thru 0xF) \
\n CONFIG                                                                           set default config (global and channel) in all the TIGERS\
\n(TD)ly    <FEB3_timing_dly> <FEB2_timing_dly> <FEB1_timing_dly> <FEB0_timing_dly> range of parameters is 0 to 63 corresponding to 88ps of incremental delay per LSB \
\n(I)VT                                                                             read and print IVT parameters of GEM"+(
# \n OCVTEn   <FEB_OVC_EN_pattern>(Hex, 0x0 thru 0xF) <FEB_OVV_EN_pattern>(Hex, 0x0 thru 0xF) <FEB_OVT_EN_pattern>(Hex, 0x0 thru 0xF) <ROC_OVT_EN>(0 or 1)\
# \n OVVA     <FEB3_OVVA_thr_param> <FEB2_OVVA_thr_param> <FEB1_OVVA_thr_param> <FEB0_OVVA_thr_param>  range of parameters is 0 to 5000(dec) [mV]\
# \n OVVD     <FEB3_OVVD_thr_param> <FEB2_OVVD_thr_param> <FEB1_OVVD_thr_param> <FEB0_OVVD_thr_param>  range of parameters is 0 to 5000(dec) [mV]\
# \n OVCA     <FEB3_OVCA_thr_param> <FEB2_OVCA_thr_param> <FEB1_OVCA_thr_param> <FEB0_OVCA_thr_param>  range of parameters is 0 to 1200(dec) [mA]\
# \n OVCD     <FEB3_OVCD_thr_param> <FEB2_OVCD_thr_param> <FEB1_OVCD_thr_param> <FEB0_OVCD_thr_param>  range of parameters is 0 to 1200(dec) [mA]\
# \n OVTF     <FEB3_OVT_thr_param>  <FEB2_OVT_thr_param>  <FEB1_OVT_thr_param>  <FEB0_OVT_thr_param>   range of parameters is 0 to 100(dec)[degree Celsius]\
# \n OVTR     <FEB3_OVT_thr_param>                                                                     range of parameters is 0 to 63(dec)[degree Celsius]\
"\n LVCR                                                                             read and print setting of GEMROC LV configuration register  \
\n DAQCR                                                                            read and print setting of GEMROC DAQ configuration register  \
\n GRST                                                                             RESETS ALL TIGER CONFIGURATION REGISTERS: must be executed before TIGER Global Register Write \
\n (GW)def   <TIGER_ID>(0 thru 7)                                                    (default file: \"TIGER_def_g_cfg_2018.txt\") \
\n (CW)def   <TIGER_ID>(0 thru 7) <channel_ID>(0 thru 64);                           if channel_ID =64 then WRITE ALL IN SEQUENCE (default file: \"TIGER_def_ch_cfg_2018.txt\"); \
\n (GR)d     <TIGER_ID>(0 thru 7)  \
\n field_set <field name> <TIGER> <value>                                            set a certain field to a value \
\n (CR)d     <TIGER_ID>(0 thru 7) <channel_ID>(0 thru 64);                           if channel_ID = 64 then READ ALL channels IN SEQUENCE \
\n (TP)EW_ch <TIGER_ID>(0 thru 7) <channel_ID>(0 thru 64) <TP_disable_FE_param> (0 or 1) <TriggerMode_param> (0 or 1);   if channel_ID = 64 then act on all channels\
\n (VT1)_ch  <TIGER_ID>(0 thru 7) <channel_ID>(0 thru 64) <VthT1 param> (0 thru 63); if channel_ID = 64 then act on VthT1 for ALL channels\
\n SRst     <SynchRst_TargetFEB>(0 to 4)                                            send a sycnh rst to the target FEB(0 to 3); if 4 is input then send synch rst to ALL FEBs  \
\n DRst     <SynchRst_TargetTCAM>(0 to 4)                                           send a sycnh rst to the TIGER Data Processing unit (TCAM)0 to 3; if 4 is input then send synch rst to ALL TCAMs    \
\n DAQSET   <TCAM_En_pattern>(0x0 thru 0xF) <FEB_TP_En_pattern>(0x0 thru 0xF) <TP_repeat_burst>(0 or 1) <TP_Num_in_burst>(0 thru 511) <TL_nTM_ACQ_choice>(0 or 1) <Periodic_L1_Enable>(0 or 1) <L1_from_TP_bit_param> (0 or 1) set DAQ related parameters  \
\n DT   <TCAM_En_pattern>(0x0 thru 0xF)                                             read from selected pattern with default values  \
\n ENPM     <On_Off_param>                                                          Enable PAUSE mode for DAQ and test pulsing: if set then it allows DAQ_PAUSE_SET to pause DAQ which will restart after reception of first trigger \
\n PAUSE                                                                            Set DAQ in Pause; first trigger received will stop pausing \
\n CKEXT    <On_Off_param>                                                          Select Clock source for DAQ functions: \"1\" for DAQ clock derived from External source (same for all boards); \"0\" for for DAQ clock derived from on-board generator\
\n TRIG2TP  <On_Off_param>                                                          Enable (\"1\") / Disable(\"0\") generation of test pulses from external trigger\
\n CHK2TP   <On_Off_param>                                                          Enable (\"1\") / Disable(\"0\") generation of test pulses from external L1_Chk signal\
\n THR_SCAN                                                                         launch a threshold scan on all the chips\
\n VTHR_LOAD <Tiger_ID(0 thru 7)><Number of sigma>                                  load thrshold file on chip\
\n AUTO  <TIGER><Desidered rate>                                                    load thrshold files on chip and try to reach desidered rate\
\n LOAD_AUTO <TIGER>                                                                load thrshold files on chip and try to reach desidered rate\
\n gsave\"gload <filename>                                                          save\"load global configuratution for all TIGERS\
\n csave\"cload <filename>                                                          save\"load channel configuratution for all TIGERS (only sensible fields)\
\n CHECK_RATE <TIGER NUMBER><NUMBER OF FRAMES>                                      show the rate with the selected number of frames\
\n SH                                                                               set sample and hold mode\
\n TMSET    <L1_lat_B3clk_param>( 100 to 1023; default = 358) <TM_window_in_B3clk_param>(1 to 127; default = 66) \
\n CONFIG_PAUSE                                                                     set default config (global and channel, pause state) in all the TIGERS\
\n (X)CVRTST  <NumWordToSend>(0 thru 127; ONLY 0 is implemented at the moment)       Perform XCVR loopback test. If NumWordToSend=0 then capture of the next TM pkt is performed; else NumWordToSend data words are looped back\
\n(D)efault_Init <Pattern_of_Enabled_TIGERs>(0 thru 0xFF) <Ext/Int timing>(\"1\" for Ext) <TL/TM mode>(\"1\" for TL mode) \
\n              <Pause_Mode_En>(0 or 1) <Int_TP_Burst_repeat_En>(0 or 1) <TP_Num_in_burst>(0 thru 511) <Periodic_L1_Enable>(0 or 1) <Enable Auto L1 generation after TP>(0 or 1). Default initialization \
\n TEST <kind of test>                                                              \"s\" for synch test, \"c\" for configuration test, \"t\" for test pulse test\
\n Counter <TIGER> <mode> <Channel>                                                 set the counter. Mode 1 = error mode, mode 0 = counter mode \
\n counter_reset                                                                    reset counter\
\n counter_display                                                                  display counter\
\n AUTO_TD                                                                          search for the best communication delay \
\n(Q)uit: leave\
\nEnter your command:\n ")
DONE = False
def clear_term():
    if OS == 'linux2':
        os.system('clear')
    else:
        os.system('cls')


def add_input(input_queue):
    while True:
        input_queue.put(sys.stdin.readline())

def Menu_and_prompt():
    input_queue = Queue.Queue()
    input_thread = threading.Thread(target=add_input, args=(input_queue,))
    input_thread.daemon = True
    input_thread.start()
    last_update = time.time()
    DONE = False
    IVT_DISPLAY_ENABLE = 1
    fmt='%Y-%m-%d-%H-%M-%S'
    #GEM_COM1.IVT_log_file.write('\n%s' %datetime.datetime.now().strftime(fmt) )
    GEM_COM1.GEMROC_IVT_read_and_log(IVT_DISPLAY_ENABLE, IVT_LOG_ENABLE, GEM_COM1.IVT_log_file)
    LOCAL_L1_TS_minus_TIGER_COARSE_TS = 0 # acr 2018-08-08
    LOCAL_L1_TIMESTAMP = 0 # acr 2018-08-08
    previous_L1_TS = 0 # acr 2018-08-08

    ##os.system('clear')
    sys.stdout.write(menu_string)
    # print "Enter your command: "

    while not DONE:
        if (time.time() - last_update)>IVT_LOG_PERIOD_SECONDS:
            #os.system('clear')
            IVT_DISPLAY_ENABLE = 0
            GEM_COM1.IVT_log_file.write('\n%s' %datetime.datetime.now().strftime(fmt) )
            GEM_COM1.GEMROC_IVT_read_and_log(IVT_DISPLAY_ENABLE, IVT_LOG_ENABLE, GEM_COM1.IVT_log_file)
            last_update = time.time()
            #sys.stdout.write(menu_string)
        else:
            time.sleep(0.01)  #greatly reduce the CPU usage
            if not input_queue.empty():
                input_array = (input_queue.get()).split()
                if len(input_array) > 0:
                    if (input_array[0] == 'quit') or (input_array[0] == 'q') or (input_array[0] == 'Quit') or (input_array[0] == 'Q'):
                        DONE = True
                    elif (input_array[0] == 'PEW') or (input_array[0] == 'P'):
                        if len(input_array) == 2:
                            GEM_COM1.FEBPwrEnPattern_set(int(input_array[1], 0))
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif (input_array[0] == 'TDly') or (input_array[0] == 'TD'):
                        if len(input_array) == 5:
                            FEB3_TIGER_timing_delay_setting = int(input_array[1]) # decimal format is expected
                            FEB2_TIGER_timing_delay_setting = int(input_array[2])
                            FEB1_TIGER_timing_delay_setting = int(input_array[3])
                            FEB0_TIGER_timing_delay_setting = int(input_array[4])
                            GEM_COM1.set_FEB_timing_delays(FEB3_TIGER_timing_delay_setting,
                                                           FEB2_TIGER_timing_delay_setting,
                                                           FEB1_TIGER_timing_delay_setting,
                                                           FEB0_TIGER_timing_delay_setting)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif (input_array[0] == 'IVT') or (input_array[0] == 'I'):
                        if len(input_array) == 1:
                            IVT_DISPLAY_ENABLE = 1
                            GEM_COM1.IVT_log_file.write('\n%s' %datetime.datetime.now().strftime(fmt) )
                            GEM_COM1.GEMROC_IVT_read_and_log(IVT_DISPLAY_ENABLE, IVT_LOG_ENABLE, GEM_COM1.IVT_log_file)
                            print '\npress RETURN to continue'
                            while input_queue.empty():
                                time.sleep(1)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif input_array[0] == 'OCVTEn':
                        if len(input_array) == 5:
                            GEM_COM1.Set_OV_OC_OT_PWR_CUT_EN_FLAGS(GEM_COM1.gemroc_LV_XX, int(input_array[1], 16),
                                                                   int(input_array[2], 16), int(input_array[3], 16),
                                                                   int(input_array[4]))
                            GEM_COM1.GEMROC_IVT_read_and_log(1, 0,
                                                             GEM_COM1.IVT_log_file)  ## ACR 2018-03-15 PERFORM IVT READ TO UPDATE STATUS OF FEB POWER ENABLE BITS which may change as a consequence
                            ##time.sleep(2)
                            print '\npress RETURN to continue'
                            while input_queue.empty():
                                time.sleep(1)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif input_array[0] == 'OVVA':
                        if len(input_array) == 5:
                            GEM_COM1.Set_OVVA_LIMIT(GEM_COM1.gemroc_LV_XX, int(input_array[1]), int(input_array[2]),
                                                    int(input_array[3]), int(input_array[4]))
                            GEM_COM1.GEMROC_IVT_read_and_log(1, 0,
                                                             GEM_COM1.IVT_log_file)  ## ACR 2018-03-15 PERFORM IVT READ TO UPDATE STATUS OF FEB POWER ENABLE BITS which may change as a consequence
                            ##time.sleep(2)
                            print '\npress RETURN to continue'
                            while input_queue.empty():
                                time.sleep(1)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif input_array[0] == 'OVVD':
                        if len(input_array) == 5:
                            GEM_COM1.Set_OVVD_LIMIT(GEM_COM1.gemroc_LV_XX, int(input_array[1]), int(input_array[2]),
                                                    int(input_array[3]), int(input_array[4]))
                            GEM_COM1.GEMROC_IVT_read_and_log(1, 0,
                                                             GEM_COM1.IVT_log_file)  ## ACR 2018-03-15 PERFORM IVT READ TO UPDATE STATUS OF FEB POWER ENABLE BITS which may change as a consequence
                            ##time.sleep(2)
                            print '\npress RETURN to continue'
                            while input_queue.empty():
                                time.sleep(1)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif input_array[0] == 'OVCA':
                        if len(input_array) == 5:
                            GEM_COM1.Set_OVCA_LIMIT(GEM_COM1.gemroc_LV_XX, int(input_array[1]), int(input_array[2]),
                                                    int(input_array[3]), int(input_array[4]))
                            GEM_COM1.GEMROC_IVT_read_and_log(1, 0,
                                                             GEM_COM1.IVT_log_file)  ## ACR 2018-03-15 PERFORM IVT READ TO UPDATE STATUS OF FEB POWER ENABLE BITS which may change as a consequence
                            ##time.sleep(2)
                            print '\npress RETURN to continue'
                            while input_queue.empty():
                                time.sleep(1)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif input_array[0] == 'OVCD':
                        if len(input_array) == 5:
                            GEM_COM1.Set_OVCD_LIMIT(GEM_COM1.gemroc_LV_XX, int(input_array[1]), int(input_array[2]),
                                                    int(input_array[3]), int(input_array[4]))
                            GEM_COM1.GEMROC_IVT_read_and_log(1, 0,
                                                             GEM_COM1.IVT_log_file)  ## ACR 2018-03-15 PERFORM IVT READ TO UPDATE STATUS OF FEB POWER ENABLE BITS which may change as a consequence
                            ##time.sleep(2)
                            print '\npress RETURN to continue'
                            while input_queue.empty():
                                time.sleep(1)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif input_array[0] == 'OVTF':
                        if len(input_array) == 5:
                            GEM_COM1.Set_OVTF_LIMIT(GEM_COM1.gemroc_LV_XX, int(input_array[1]), int(input_array[2]),
                                                    int(input_array[3]), int(input_array[4]))
                            GEM_COM1.GEMROC_IVT_read_and_log(1, 0,
                                                             GEM_COM1.IVT_log_file)  ## ACR 2018-03-15 PERFORM IVT READ TO UPDATE STATUS OF FEB POWER ENABLE BITS which may change as a consequence
                            ##time.sleep(2)
                            print '\npress RETURN to continue'
                            while input_queue.empty():
                                time.sleep(1)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif input_array[0] == 'OVTR':
                        if len(input_array) == 2:
                            GEM_COM1.set_ROC_OVT_LIMIT(GEM_COM1.gemroc_LV_XX, int(input_array[1]))
                            GEM_COM1.GEMROC_IVT_read_and_log(1, 0,
                                                             GEM_COM1.IVT_log_file)  ## ACR 2018-03-15 PERFORM IVT READ TO UPDATE STATUS OF FEB POWER ENABLE BITS which may change as a consequence
                            ##time.sleep(2)
                            print '\npress RETURN to continue'
                            while input_queue.empty():
                                time.sleep(1)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif input_array[0] == 'LVCR': # acr 2018-03-16 at IHEP
                        if len(input_array) == 1:
                            command_reply = GEM_COM1.Read_GEMROC_LV_CfgReg()
                            print '\nLVCR command_reply: %s' %binascii.b2a_hex(command_reply)
                            GEM_COM1.display_log_GEMROC_LV_CfgReg_readback(command_reply, 1, 1)
                            print '\npress RETURN to continue'
                            while input_queue.empty():
                                time.sleep(1)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif input_array[0] == 'DAQCR':
                        if len(input_array) == 1:
                            command_reply = GEM_COM1.Read_GEMROC_DAQ_CfgReg()
                            command_reply = GEM_COM1.Read_GEMROC_DAQ_CfgReg()
                            print '\nDAQCR command_reply: %s' %binascii.b2a_hex(command_reply)
                            GEM_COM1.display_log_GEMROC_DAQ_CfgReg_readback(command_reply, 1, 1)
                            print '\npress RETURN to continue'
                            while input_queue.empty():
                                time.sleep(1)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif input_array[0] == 'GRST':
                        if len(input_array) == 1:
                            GEM_COM1.ResetTgtGEMROC_ALL_TIGER_GCfgReg(GEM_COM1.gemroc_DAQ_XX)
                            os.system('clear')
                            sys.stdout.write(menu_string)

                    elif (input_array[0] == 'GWdef') or (input_array[0] == 'GW'):
                        if len(input_array) == 2:
                            command_sent = GEM_COM1.WriteTgtGEMROC_TIGER_GCfgReg(g_inst, int(input_array[1]))
                            print '\nGWdef command_reply: %s' %binascii.b2a_hex(command_sent)
                            command_reply = GEM_COM1.ReadTgtGEMROC_TIGER_GCfgReg(g_inst, int(input_array[1]))
                            print '\nGRd   command_reply: %s' %binascii.b2a_hex(command_reply)
                            if (int (binascii.b2a_hex(command_sent),16)) !=( (int (binascii.b2a_hex(command_reply),16)) -2048 ):
                                print "---____----____----____----____----"
                                print "!!! ERROR IN CONFIGURATION !!!"
                                print "---____----____----____----____----"
                                time.sleep(1)
                            time.sleep(1)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif (input_array[0] == 'GRd') or (input_array[0] == 'GR'):
                        if len(input_array) == 2:
                            command_reply = GEM_COM1.ReadTgtGEMROC_TIGER_GCfgReg(g_inst, int(input_array[1]))
                            print '\nGRd command_reply: %s' %binascii.b2a_hex(command_reply)
                            GEM_COM1.display_log_GCfg_readback(command_reply, 1) ## acr 2018-03-02
                            print '\npress RETURN to continue'
                            while input_queue.empty():
                                time.sleep(0.1)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif (input_array[0] == 'CWdef') or (input_array[0] == 'CW'):
                        if len(input_array) == 3:
                            command_sent= GEM_COM1.WriteTgtGEMROC_TIGER_ChCfgReg(c_inst, int(input_array[1]), int(input_array[2]))
                            print '\nCWdef command_reply: %s' %binascii.b2a_hex(command_sent)
                            command_reply = GEM_COM1.ReadTgtGEMROC_TIGER_ChCfgReg(c_inst, int(input_array[1]),
                                                                                  int(input_array[2]), 0)
                            print '\nCRd   command_reply: %s' %binascii.b2a_hex(command_reply)
                            if (int (binascii.b2a_hex(command_sent),16)) !=( (int (binascii.b2a_hex(command_reply),16)) -2048 ):
                                print "---____----____----____----____----"
                                print "!!! ERROR IN CONFIGURATION !!!"
                                print "---____----____----____----____----"
                                time.sleep(4)
                            time.sleep(1)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif (input_array[0] == 'CRd') or (input_array[0] == 'CR'):
                        if len(input_array) == 3:
                            command_reply = GEM_COM1.ReadTgtGEMROC_TIGER_ChCfgReg(c_inst, int(input_array[1]),
                                                                                  int(input_array[2]), 1)
                            print '\nCRd   command_reply: %s' %binascii.b2a_hex(command_reply)
                            print '\npress RETURN to continue'
                            while input_queue.empty():
                                time.sleep(1)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif input_array[0] == 'TPEnG':
                        if len(input_array) == 3:
                            FE_TPEnable_PARAM = int(input_array[2])
                            GEM_COM1.set_FE_TPEnable(g_inst, int(input_array[1]), FE_TPEnable_PARAM)
                            print '\nTo TIGER %d on GEMROC %d: GCreg FE_TPEnable bit set to %d' %(int(input_array[1]), GEMROC_ID, int(input_array[2]) )
                            time.sleep(2)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif (input_array[0] == 'TPEW_ch') or (input_array[0] == 'TP'):
                        if len(input_array) == 5:
                            if int(input_array[1])!=8:
                                TP_disable_FE_param = int(input_array[3])
                                TriggerMode_param = int(input_array[4])
                                GEM_COM1.Set_GEMROC_TIGER_ch_TPEn(c_inst, int(input_array[1]), int(input_array[2]),
                                                                  TP_disable_FE_param, TriggerMode_param)
                                print '\nTo TIGER %d on GEMROC %d: TP_disable_FE bit set to %d and TriggerMode bit set to %d for channel %d' %(int(input_array[1]), GEMROC_ID, int(input_array[3]), int(input_array[4]),int(input_array[2]) )
                                time.sleep(2)
                            else:
                                for T in range (0,8):
                                    TP_disable_FE_param = int(input_array[3])
                                    TriggerMode_param = int(input_array[4])
                                    GEM_COM1.Set_GEMROC_TIGER_ch_TPEn(c_inst, T, int(input_array[2]),
                                                                      TP_disable_FE_param, TriggerMode_param)
                                    print '\nTo TIGER %d on GEMROC %d: TP_disable_FE bit set to %d and TriggerMode bit set to %d for channel %d' %(int(input_array[1]), GEMROC_ID, int(input_array[3]), int(input_array[4]),int(input_array[2]) )
                                    time.sleep(0.2)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif (input_array[0] == 'VT1_ch') or (input_array[0] == 'VT1'):
                        if len(input_array) == 4:
                            GEM_COM1.Set_Vth_T1(c_inst, int(input_array[1]), int(input_array[2]), int(input_array[3]))
                            print '\nTo TIGER %d on GEMROC %d: Vth_T1 set to %d for channel %d' %(int(input_array[1]), GEMROC_ID, int(input_array[3]), int(input_array[2]) )
                            time.sleep(2)
                            os.system('clear')
                            sys.stdout.write(menu_string)

                    elif (input_array[0].lower() == 'field_set' or input_array[0].lower() == 'fs'):
                        if len(input_array) == 4:
                            try:
                                if int(input_array[2])!=8:
                                    GEM_COM1.Set_param_dict_global(g_inst, (input_array[1]), int(input_array[2]), int(input_array[3]))
                                else:
                                    for T in range (0,8):
                                        GEM_COM1.Set_param_dict_global(g_inst, (input_array[1]), T, int(input_array[3]))
                            except:
                                print "Can't find this key"
                        if len(input_array) == 5:
                            GEM_COM1.Set_param_dict_channel(c_inst,input_array[1],int(input_array[2]),int(input_array[3]),int(input_array[4]))

                        os.system('clear')
                        sys.stdout.write(menu_string)
                    elif input_array[0] == 'SRst':
                        if len(input_array) == 2:
                            if int(input_array[1]) < 4:
                                To_ALL_FEB_enable = 0
                            else:
                                To_ALL_FEB_enable = 1
                            TargetFEB = int(input_array[1]) & 0x3
                            GEM_COM1.SynchReset_to_TgtFEB(TargetFEB, To_ALL_FEB_enable)
                            print '\nTo FEB %d or ToALL_FEB: %d on GEMROC %d: sent synchronous reset' %( TargetFEB, To_ALL_FEB_enable, GEMROC_ID )
                            time.sleep(2)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif input_array[0] == 'DRst':
                        if len(input_array) == 2:
                            if int(input_array[1]) < 4:
                                To_ALL_TCAM_enable = 0
                            else:
                                To_ALL_TCAM_enable = 1
                            TargetTCAM = int(input_array[1]) & 0x3
                            GEM_COM1.SynchReset_to_TgtTCAM(TargetTCAM, To_ALL_TCAM_enable)
                            print '\nTo TCAM %d or ToALL_TCAM: %d on GEMROC %d: sent synchronous reset' %( TargetTCAM, To_ALL_TCAM_enable, GEMROC_ID )
                            time.sleep(2)
                            os.system('clear')
                            sys.stdout.write(menu_string)

                    elif (input_array[0] == 'DRst'):
                        if (len(input_array) == 2):
                            if (int(input_array[1]) < 4):
                                To_ALL_TCAM_enable = 0
                            else:
                                To_ALL_TCAM_enable = 1
                            TargetTCAM = int(input_array[1]) & 0x3
                            GEM_COM1.SynchReset_to_TgtTCAM(TargetTCAM, To_ALL_TCAM_enable)
                            print '\nTo TCAM %d or ToALL_TCAM: %d on GEMROC %d: sent synchronous reset' % (TargetTCAM, To_ALL_TCAM_enable, GEMROC_ID)
                            time.sleep(2)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                            # acr 2018-04-24 elif (input_array[0] == 'DSTART'):
                    elif (input_array[0] == 'DAQSET'):
                            # acr 2018-04-23 if (len(input_array) == 3):
                            if (len(input_array) == 8):  # 5):
                                TCAM_Enable_pattern = int(input_array[1], 0) & 0xFF
                                Periodic_FEB_TP_Enable_pattern = int(input_array[2], 0) & 0xFF
                                TP_repeat_burst = int(input_array[3], 0) & 0x1
                                TP_Num_in_burst = int(input_array[4], 0) & 0x1FF
                                TL_nTM_ACQ_choice = int(input_array[5], 0) & 0x1
                                Periodic_L1_Enable_pattern = int(input_array[6], 0) & 0x1
                                Enab_Auto_L1_from_TP_bit_param= int(input_array[7], 0) & 0x1

                                # acr 2018-04-23 DAQ_set_and_TL_start(gemroc_DAQ_XX, GEMROC_ID, TCAM_Enable_pattern, Periodic_FEB_TP_Enable_pattern)
                                # acr 2018-05-31 DAQ_set(gemroc_DAQ_XX, GEMROC_ID, TCAM_Enable_pattern, Periodic_FEB_TP_Enable_pattern, TP_repeat_burst, TP_Num_in_burst)
                                # acr 2018-06-04 DAQ_set(gemroc_DAQ_XX, GEMROC_ID, TCAM_Enable_pattern, Periodic_FEB_TP_Enable_pattern, TP_repeat_burst, TP_Num_in_burst, TL_nTM_ACQ_choice)
                                gemroc_DAQ_XX = GEM_COM1.gemroc_DAQ_XX

                                GEM_COM1.DAQ_set(TCAM_Enable_pattern, Periodic_FEB_TP_Enable_pattern, TP_repeat_burst, TP_Num_in_burst, TL_nTM_ACQ_choice, Periodic_L1_Enable_pattern, Enab_Auto_L1_from_TP_bit_param)
                                print '\nStart TL DAQ from enable TCAM pattern: %d on GEMROC %d' % (TCAM_Enable_pattern, GEMROC_ID)
                                time.sleep(2)
                                os.system('clear')
                                sys.stdout.write(menu_string)
                    elif (input_array[0] == 'ENPM'):
                            if (len(input_array) == 2):
                                Enable_DAQ_Pause_Mode = int(input_array[1], 0) & 0x1
                                GEM_COM1.DAQ_set_Pause_Mode(Enable_DAQ_Pause_Mode)
                                print '\nEnable DAQ Pause Mode: %d on GEMROC %d' % (Enable_DAQ_Pause_Mode, GEMROC_ID)
                                time.sleep(2)
                                os.system('clear')
                                sys.stdout.write(menu_string)
                    elif (input_array[0] == 'CKEXT'):
                        if (len(input_array) == 2):
                            Derive_DAQck_From_Ext_nInt_source = int(input_array[1], 0) & 0x1
                            GEM_COM1.DAQ_set_DAQck_source(Derive_DAQck_From_Ext_nInt_source)
                            print '\nDAQ_set_DAQck_source: %d on GEMROC %d' % (Derive_DAQck_From_Ext_nInt_source, GEMROC_ID)
                            time.sleep(2)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif (input_array[0] == 'TRIG2TP'):
                        if (len(input_array) == 2):
                            Enab_nDisab_TP_from_Ext_triggers = int(input_array[1], 0) & 0x1
                            GEM_COM1.DAQ_set_TP_from_Ext_Trig(GEM_COM1.gemroc_DAQ_XX, Enab_nDisab_TP_from_Ext_triggers)
                            print '\nEnab_nDisab_TP_from_Ext_triggers: %d on GEMROC %d' % (Enab_nDisab_TP_from_Ext_triggers, GEMROC_ID)
                            time.sleep(2)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif (input_array[0] == 'PAUSE'):
                        if (len(input_array) == 1):
                            GEM_COM1.DAQ_Toggle_Set_Pause_bit()
                            print '\nDAQ Pause Set bit TOGGLED on GEMROC %d' % (GEMROC_ID)
                            time.sleep(2)
                            os.system('clear')
                            sys.stdout.write(menu_string)

                    elif input_array[0].lower() == 'vthr_load':
                        if len(input_array) == 3:
                            if int(input_array[1])!=8:
                                GEM_COM1.Load_VTH_from_scan_file(c_inst, int(input_array[1]) & 0xFF, int(input_array[2]), 0, True)
                                print ("\nVth Loaded on chip {}").format (int(input_array[1]))
                                time.sleep(1)
                            else:
                                for T in range (0,8):
                                    GEM_COM1.Load_VTH_from_scan_file(c_inst, T, int(input_array[2]), 0, True)
                                    print ("\nVth Loaded on chip {}").format (T)
                                    time.sleep(1)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                        else:
                            print"\nCheck input formatting\n"

                    elif input_array[0].lower()=='gsave':
                        if len(input_array) == 2:
                            g_inst.save_glob_conf("./conf/global_conf_saves"+sep+input_array[1])
                            os.system('clear')
                            sys.stdout.write(menu_string)

                    elif input_array[0].lower()=='gload':
                        if len(input_array) == 2:
                            g_inst.load_glob_conf("./conf/global_conf_saves"+sep+input_array[1])
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif input_array[0].lower()=='csave':
                        if len(input_array) == 2:
                            c_inst.save_ch_conf("./conf/ch_conf_saves"+sep+input_array[1])
                            os.system('clear')
                            sys.stdout.write(menu_string)

                    elif input_array[0].lower()=='cload':
                        if len(input_array) == 2:
                            c_inst.load_ch_conf("./conf/ch_conf_saves"+sep+input_array[1])
                            os.system('clear')
                            sys.stdout.write(menu_string)

                    elif input_array[0].lower() == 'auto':
                        if len(input_array) == 3:
                        #     if int(input_array[1]) != 8:
                        #         T = int(input_array[1])
                        #         test_r = AN_CLASS.analisys_read(GEM_COM1, c_inst)
                        #
                        #         auto_tune_C = AN_CLASS.analisys_conf(GEM_COM1, c_inst, g_inst)
                        #         GEM_COM1.Load_VTH_from_scan_file(c_inst, T, 2, 0)
                        #         print "\nVth Loaded on TIGER {}".format(T)
                        #         auto_tune_C.fill_VTHR_matrix(3, 0, T)
                        #
                        #         auto_tune_C.thr_autotune(T, int(input_array[2]), test_r)
                        #         auto_tune_C.__del__()
                        #
                        #         test_r.__del__()
                        #
                        #     else:
                        #         for T in range(0, 8):
                        #             test_r = AN_CLASS.analisys_read(GEM_COM1, c_inst)
                        #
                        #             auto_tune_C = AN_CLASS.analisys_conf(GEM_COM1, c_inst, g_inst)
                        #             GEM_COM1.Load_VTH_from_scan_file(c_inst, T, 2, 0)
                        #             print "\nVth Loaded on TIGER {}".format(T)
                        #             auto_tune_C.fill_VTHR_matrix(3, 0, T)
                        #
                        #             auto_tune_C.thr_autotune(T, int(input_array[2]), test_r)
                        #
                        #             auto_tune_C.__del__()
                        #
                        #             test_r.__del__()
                        #
                        #     os.system('clear')
                        #     sys.stdout.write(menu_string) if len(input_array) == 3:
                            if int(input_array[1]) != 8:
                                T=int(input_array[1])
                                test_r = AN_CLASS.analisys_read(GEM_COM1, c_inst)

                                auto_tune_C = AN_CLASS.analisys_conf(GEM_COM1, c_inst, g_inst)
                                GEM_COM1.Load_VTH_from_scan_file(c_inst, T, 2, 0)
                                print "\nVth Loaded on TIGER {}".format(T)
                                auto_tune_C.fill_VTHR_matrix(3, 0, T)

                                auto_tune_C.thr_autotune_wth_counter(T, int(input_array[2]), test_r,15,0.02)
                                auto_tune_C.thr_autotune_wth_counter(T, int(input_array[2]), test_r,2,1)


                                auto_tune_C.__del__()

                                test_r.__del__()

                            else:
                                for T in range (0,8):
                                    test_r = AN_CLASS.analisys_read(GEM_COM1, c_inst)

                                    auto_tune_C = AN_CLASS.analisys_conf(GEM_COM1,c_inst,g_inst )
                                    GEM_COM1.Load_VTH_from_scan_file(c_inst, T, 2, 0)
                                    print "\nVth Loaded on TIGER {}".format(T)
                                    auto_tune_C.fill_VTHR_matrix(3, 0, T)

                                    auto_tune_C.thr_autotune_wth_counter(T, int(input_array[2]), test_r, 15, 0.02)
                                    auto_tune_C.thr_autotune_wth_counter(T, int(input_array[2]), test_r, 2, 1)

                                    auto_tune_C.__del__()

                                    test_r.__del__()


                            os.system('clear')
                            sys.stdout.write(menu_string)
                        else:
                            print"\nCheck input formatting\n"
                            time.sleep(0.8)
                            os.system('clear')
                            sys.stdout.write(menu_string)

                    elif input_array[0].lower() == 'load_auto':
                        if len(input_array) == 2:
                            if int(input_array[1])!=8:
                                GEM_COM1.Load_VTH_fromfile_autotuned(c_inst, int(input_array[1]))
                            else:
                                for T in range (0,8):
                                    GEM_COM1.Load_VTH_fromfile_autotuned(c_inst, T)
                            time.sleep(0.8)
                            os.system('clear')
                            sys.stdout.write(menu_string)


                        else:
                            print"\nCheck input formatting\n"
                            time.sleep(0.8)
                            os.system('clear')
                            sys.stdout.write(menu_string)


                    elif input_array[0].lower() == 'check_rate':
                        if len(input_array) == 3:
                            test_r = AN_CLASS.analisys_read(GEM_COM1, c_inst)

                            rate_C = AN_CLASS.analisys_conf(GEM_COM1,c_inst,g_inst )

                            rate_C.check_rate(int(input_array[1]),int(input_array[2]),test_r)

                            rate_C.__del__()
                            test_r.__del__()

                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif input_array[0].lower() == 'thr_scan':
                        if len(input_array)==3:
                            test_c = AN_CLASS.analisys_conf(GEM_COM1, c_inst, g_inst)
                            test_r = AN_CLASS.analisys_read(GEM_COM1,c_inst )
                            test_c.thr_preconf()
                            test_r.thr_scan_matrix=test_c.thr_conf_using_GEMROC_COUNTERS(test_r, int(input_array[1]),int(input_array[2]))

                            test_r.make_rate()
                            test_r.normalize_rate(int(input_array[1]),int(input_array[2]))
                            test_r.save_scan_on_file()
                            test_r.colorPlot(GEM_COM1.Tscan_folder+sep+"GEMROC{}".format(GEMROC_ID)+sep+"GEMROC {}".format(GEMROC_ID)+"rate", int(input_array[1]),int(input_array[2]),True)
                            test_r.colorPlot(GEM_COM1.Tscan_folder+sep+"GEMROC{}".format(GEMROC_ID)+sep+"GEMROC {}".format(GEMROC_ID)+"conteggi", int(input_array[1]),int(input_array[2]))


                            #test_r.normalize_rate( int(input_array[1]),int(input_array[2]))
                            test_r.global_sfit( int(input_array[1]),int(input_array[2]))
                            test_r.__del__()
                            test_c.__del__()
                        else:
                        # if len(input_array) == 3:
                        #     test_c = AN_CLASS.analisys_conf(GEM_COM1, c_inst, g_inst)
                        #     test_r = AN_CLASS.analisys_read(GEM_COM1, c_inst)
                        #     test_c.thr_preconf()
                        #     test_c.thr_conf(test_r, int(input_array[1]), int(input_array[2]))
                        #
                        #     test_r.save_scan_on_file()
                        #
                        #     test_r.make_rate()
                        #     test_r.colorPlot(GEM_COM1.Tscan_folder + sep + "GEMROC{}".format(GEMROC_ID) + sep + "GEMROC {}".format(GEMROC_ID) + "rate", int(input_array[1]), int(input_array[2]), True)
                        #     test_r.colorPlot(GEM_COM1.Tscan_folder + sep + "GEMROC{}".format(GEMROC_ID) + sep + "GEMROC {}".format(GEMROC_ID) + "conteggi", int(input_array[1]), int(input_array[2]))
                        #
                        #     test_r.normalize_rate(int(input_array[1]), int(input_array[2]))
                        #     test_r.global_sfit(int(input_array[1]), int(input_array[2]))
                        #     test_r.__del__()
                        #     test_c.__del__()
                        # else:
                            print ("Declare first and last TIGER")
                        sys.stdout.write(menu_string)
                    elif input_array[0].lower() == 'dt':
                        if (len(input_array) == 2):  # 5):
                            TCAM_Enable_pattern = int(input_array[1], 0) & 0xFF
                            gemroc_DAQ_XX = GEM_COM1.gemroc_DAQ_XX
                            GEM_COM1.DAQ_set(TCAM_Enable_pattern, TCAM_Enable_pattern, 0, 0, 1, 0, 0)
                            GEM_COM1.SynchReset_to_TgtFEB(0, 1)
                            GEM_COM1.SynchReset_to_TgtTCAM(0, 1)
                            time.sleep(2)
                            os.system('clear')
                            sys.stdout.write(menu_string)



                    elif input_array[0].lower() == 'config':
                        GEM_COM1.ResetTgtGEMROC_ALL_TIGER_GCfgReg(GEM_COM1.gemroc_DAQ_XX)
                        for T in range(0,8):
                            GEM_COM1.WriteTgtGEMROC_TIGER_GCfgReg(g_inst, T)
                        print("Global configuration set\n")
                        for T in range (0,8):
                            GEM_COM1.WriteTgtGEMROC_TIGER_ChCfgReg(c_inst, T, 64)
                        print("Channel configuration set\n")
                        time.sleep(0.5)
                        os.system('clear')
                        sys.stdout.write(menu_string)

                    elif input_array[0].lower() == 'sh':
                        for T in range(0,8):
                            GEM_COM1.set_sampleandhold_mode(c_inst)

                        print("Sample and hold mode set set\n")
                        time.sleep(0.5)
                        os.system('clear')
                        sys.stdout.write(menu_string)


                    elif input_array[0].lower() == 'config_pause':
                        #CKEXT 1
                        Derive_DAQck_From_Ext_nInt_source = int("1", 0) & 0x1
                        GEM_COM1.DAQ_set_DAQck_source(Derive_DAQck_From_Ext_nInt_source)
                        print '\nDAQ_set_DAQck_source: %d on GEMROC %d' % (Derive_DAQck_From_Ext_nInt_source, GEMROC_ID)
                        #GRST
                        GEM_COM1.ResetTgtGEMROC_ALL_TIGER_GCfgReg(GEM_COM1.gemroc_DAQ_XX)
                        #GW TIGERID
                        for T in range(0, 8):
                            GEM_COM1.WriteTgtGEMROC_TIGER_GCfgReg(g_inst, T)
                        print("Global configuration set\n")
                        # CW TIGERID ChID
                        for T in range(0, 8):
                            GEM_COM1.WriteTgtGEMROC_TIGER_ChCfgReg(c_inst, T, 64)
                        print("Channel configuration set\n")
                        #ENPM
                        Enable_DAQ_Pause_Mode = int("1", 0) & 0x1
                        GEM_COM1.DAQ_set_Pause_Mode(Enable_DAQ_Pause_Mode)
                        print '\nEnable DAQ Pause Mode: %d on GEMROC %d' % (Enable_DAQ_Pause_Mode, GEMROC_ID)
                        #PAUSE
                        GEM_COM1.DAQ_Toggle_Set_Pause_bit()
                        print '\nDAQ Pause Set bit TOGGLED on GEMROC %d' % (GEMROC_ID)
                        time.sleep(0.5)
                        os.system('clear')
                        sys.stdout.write(menu_string)

                    elif (input_array[0] == 'TMSET'):  # acr 2018-07-23
                        # acr 2018-04-23 if (len(input_array) == 3):
                        if (len(input_array) == 3):  # 5):
                            L1_lat_B3clk_param = int(input_array[1], 0) & 0x3FF
                            TM_window_in_B3clk_param = int(input_array[2], 0) & 0x7F
                            GEM_COM1.MENU_set_L1_Lat_TM_Win_in_B3Ck_cycles(L1_lat_B3clk_param, TM_window_in_B3clk_param)
                            print '\nSet TM latency: %d and TM window: %d parameters on GEMROC %d' % (L1_lat_B3clk_param, TM_window_in_B3clk_param, GEMROC_ID)
                            GEM_COM1.gemroc_DAQ_XX.extract_parameters_from_UDP_packet()  # acr 2018-07-23
                            time.sleep(2)
                            os.system('clear')
                            sys.stdout.write(menu_string)

                    elif (input_array[0] == 'CHK2TP'):
                        if (len(input_array) == 2):
                            Enab_nDisab_TP_from_L1_Chk = int(input_array[1], 0) & 0x1
                            GEM_COM1.DAQ_set_TP_from_L1Chk(GEM_COM1.gemroc_DAQ_XX, Enab_nDisab_TP_from_L1_Chk)
                            print '\nEnab_nDisab_TP_from_Ext_triggers: %d on GEMROC %d' % (Enab_nDisab_TP_from_L1_Chk, GEMROC_ID)
                            time.sleep(2)
                            os.system('clear')
                            sys.stdout.write(menu_string)

                    elif ((input_array[0] == 'XCVRTST') or (input_array[0] == 'X')):
                        if (len(input_array) == 2):
                            NumWordToSend = int(input_array[1], 0) & 0x7F
                            # Max_U64_words_in_UDP_pkt = int(input_array[1], 0) & 0x3F
                            # U64_array_XCVR_LB_data = XCVR_Loopback_Test(gemroc_DAQ_XX, GEMROC_ID, NumWordToSend, Max_U64_words_in_UDP_pkt, log_file)
                            ##U64_array_XCVR_LB_data = XCVR_Loopback_Test(gemroc_DAQ_XX, GEMROC_ID, NumWordToSend, log_file)
                            command_echo = GEM_COM1.XCVR_Loopback_Test(GEM_COM1.gemroc_DAQ_XX, NumWordToSend)
                            print binascii.hexlify(command_echo)
                            X_array = array.array('I')
                            X_array.fromstring(command_echo)
                            X_array.byteswap()
                            X_arraylen = X_array.buffer_info()[1]
                            # for i in range(0, X_arraylen / 2, 2):
                            for i in range(0, X_arraylen, 2):
                                U64_int = X_array[i]
                                # print '\nU64_int %08X' % U64_int
                                i += 1
                                U64_int = (U64_int << 32) + X_array[i]
                                print '\nU64_int %016X' % U64_int
                                if (((U64_int & 0xE000000000000000) >> 61) == 0x6):
                                    LOCAL_L1_COUNT_31_6 = U64_int >> 32 & 0x3FFFFFF
                                    LOCAL_L1_COUNT_5_0 = U64_int >> 24 & 0x3F
                                    LOCAL_L1_COUNT = (LOCAL_L1_COUNT_31_6 << 6) + LOCAL_L1_COUNT_5_0
                                    LOCAL_L1_TIMESTAMP = U64_int & 0xFFFF
                                    HITCOUNT = (U64_int >> 16) & 0xFF
                                    if (((U64_int & 0xFFFF) - previous_L1_TS) > 0):
                                        L1_TS_abs_diff = ((U64_int & 0xFFFF) - previous_L1_TS)
                                    else:
                                        L1_TS_abs_diff = 65536 - ((U64_int & 0xFFFF) - previous_L1_TS)
                                    s = 'HEADER :  ' + 'STATUS BIT[2:0]: %01X: ' % ((U64_int >> 58) & 0x7) + 'LOCAL L1 COUNT: %08X ' % ( LOCAL_L1_COUNT) + 'HitCount: %02X ' % ( (U64_int >> 16) & 0xFF) + 'LOCAL L1 TIMESTAMP: %04X; ' % ( U64_int & 0xFFFF) + 'Diff w.r.t. previous L1_TS: %04f us\n' % ( L1_TS_abs_diff * 6 / 1000)
                                    previous_L1_TS = (U64_int & 0xFFFF)
                                    # s = 'HEADER :  ' + 'STATUS BIT[2:0]: %01X: '%((int_x >> 58)& 0x7) + 'LOCAL L1 COUNT: %08X '%( LOCAL_L1_COUNT ) + 'HitCount: %02X '%((int_x >> 16) & 0xFF) + 'LOCAL L1 TIMESTAMP: %04X\n'%(int_x & 0xFFFF)
                                if (((U64_int & 0xE000000000000000) >> 61) == 0x7):
                                    s = 'TRAILER: ' + 'LOCAL L1  FRAMENUM [23:0]: %06X: ' % ( (U64_int >> 37) & 0xFFFFFF) + 'GEMROC_ID: %02X ' % ( (U64_int >> 32) & 0x1F) + 'TIGER_ID: %01X ' % ( (U64_int >> 27) & 0x7) + 'LOCAL L1 COUNT[2:0]: %01X ' % ((  U64_int >> 24) & 0x7) + 'LAST COUNT WORD FROM TIGER:CH_ID[5:0]: %02X ' % (( U64_int >> 18) & 0x3F) + 'LAST COUNT WORD FROM TIGER: DATA[17:0]: %05X \n' % ( U64_int & 0x3FFFF)
                                if (((U64_int & 0xC000000000000000) >> 62) == 0x0):
                                    LOCAL_L1_TS_minus_TIGER_COARSE_TS = LOCAL_L1_TIMESTAMP - ((U64_int >> 32) & 0xFFFF)
                                    s = 'DATA   : TIGER: %01X ' % ((U64_int >> 59) & 0x7) + 'L1_TS - TIGERCOARSE_TS: %d ' % ( LOCAL_L1_TS_minus_TIGER_COARSE_TS) + 'LAST TIGER FRAME NUM[2:0]: %01X ' % (
                                                (U64_int >> 56) & 0x7) + 'TIGER DATA: ChID: %02X ' % (
                                                (U64_int >> 50) & 0x3F) + 'tacID: %01X ' % (
                                                (U64_int >> 48) & 0x3) + 'Tcoarse: %04X ' % (
                                                (U64_int >> 32) & 0xFFFF) + 'Ecoarse: %03X ' % (
                                                (U64_int >> 20) & 0x3FF) + 'Tfine: %03X ' % (
                                                (U64_int >> 10) & 0x3FF) + 'Efine: %03X \n' % (U64_int & 0x3FF)
                                if (((U64_int & 0xF000000000000000) >> 60) == 0x4):
                                    s = 'UDP_SEQNO: ' + 'GEMROC_ID: %02X ' % ( (U64_int >> 52) & 0x1F) + 'UDP_SEQNO_U48: %012X \n\n' % ( ((U64_int >> 32) & 0xFFFFF) + ((U64_int >> 0) & 0xFFFFFFF))
                                print '\n' + s
                            while input_queue.empty():
                                time.sleep(1)
                            os.system('clear')
                            sys.stdout.write(menu_string)

                    elif ((input_array[0] == 'Default_Init') or (input_array[0] == 'D')):
                        if (len(input_array) == 9):  # ACR 2018-11-02 8):  # ACR 2018-10-30 6):
                            Pattern_of_Tiger_To_Configure = int(input_array[1], 0) & 0xFF # acr 2018-09-11
                            DI_Ext_nInt_Clk_option = int(input_array[2], 0) & 0x1
                            DI_TL_nTM_option       = int(input_array[3], 0) & 0x1
                            PauseMode_Enable_Option = int(input_array[4], 0) & 0x1
                            Int_TP_Burst_repeat_Enable_Option = int(input_array[5], 0) & 0x1
                            DI_TP_Num_in_burst = int(input_array[6], 0) & 0x1FF         # ACR 2018-10-30 added parameter
                            DI_Periodic_L1_Enable_bit = int(input_array[7], 0) & 0x1    # ACR 2018-10-30 added parameter
                            DI_Enab_Auto_L1_from_TP_bit = int(input_array[8], 0) & 0x1    # ACR 2018-11-02 added parameter
                            # SET TIMING SOURCE: 1 for External, 0 for Internal
                            GEM_COM1.DAQ_set_DAQck_source(DI_Ext_nInt_Clk_option)
                            print '\nDAQ_set_DAQck_source: %s' % GEM_COM1.print_int_vs_n_ext(DI_Ext_nInt_Clk_option)
                            # TIGER INITIALIZATION
                            # GEM_COM1.ResetTgtGEMROC_ALL_TIGER_GCfgReg(GEM_COM1.gemroc_DAQ_XX)
                            # print '\nResetTgtGEMROC_ALL_TIGER_GCfgReg issued'
                            # TIGER GLOBAL REGISTER configuration
                            # for nT in range (0, NumTigerToConfigure):
                            #     command_reply = WriteTgtGEMROC_TIGER_GCfgReg_fromfile(g_inst, GEMROC_ID, nT, default_TIGER_global_cfg_fname, log_file)
                            #     print '\nGWdef command_reply: %s' % binascii.b2a_hex(command_reply)
                            #     command_reply = ReadTgtGEMROC_TIGER_GCfgReg(g_inst, GEMROC_ID, nT, log_file)
                            #     print '\nGRd   command_reply: %s' % binascii.b2a_hex(command_reply)
                            # for nT in range (0, 8):
                            #     if ((Pattern_of_Tiger_To_Configure & (0x1 << nT)) != 0):
                            #         command_reply = GEM_COM1.WriteTgtGEMROC_TIGER_GCfgReg(g_inst, nT)
                            #         print '\nGW  %d' % nT
                            #         command_reply = GEM_COM1.ReadTgtGEMROC_TIGER_GCfgReg(g_inst, nT)
                            #         print '\nGRd %d' %nT # command_reply: %s' % binascii.b2a_hex(command_reply)
                            # time.sleep(1)
                            # TIGER CHANNEL REGISTER configuration
                            # for nT in range(0, NumTigerToConfigure):
                            #     command_reply = WriteTgtGEMROC_TIGER_ChCfgReg_fromfile(c_inst, GEMROC_ID, nT, 64, default_TIGER_ch_cfg_fname, log_file)
                            #     print '\nCWdef command_reply: %s' % binascii.b2a_hex(command_reply)
                            # for nT in range(0, 8):
                            #     if ((Pattern_of_Tiger_To_Configure & (0x1 << nT)) != 0):
                            #         command_reply = GEM_COM1.WriteTgtGEMROC_TIGER_ChCfgReg(c_inst, nT, 64, )
                            #         print '\nCWdef %d' %nT #'\nCWdef command_reply: %s' % binascii.b2a_hex(command_reply)
                            # time.sleep(1)
                            # TPEnable bit in the Global Cfg register
                            # for nT in range(0, NumTigerToConfigure):
                            # for nT in range(0, 8):
                            #     if ((Pattern_of_Tiger_To_Configure & (0x1 << nT)) != 0):
                            #         GEM_COM1.set_FE_TPEnable(g_inst,  nT, 1)
                            #         print '\nTo TIGER %d on GEMROC %d: GCreg FE_TPEnable bit set to %d' %(nT, GEMROC_ID, 1)
                            # time.sleep(1)
                            # TP_disable_FE and TriggerMode bit setting in the channel configuration for selected (n_channel = 2 * N_TIGER) channels
                            #for nT in range(0, NumTigerToConfigure):
                            # for nT in range(0, 8):
                            #     channel_ID_for_TPEn = nT
                            #     if ((Pattern_of_Tiger_To_Configure & (0x1 << nT)) != 0):
                            #         GEM_COM1.Set_GEMROC_TIGER_ch_TPEn(c_inst, nT, channel_ID_for_TPEn, 0, 1)
                            #         print '\nTo TIGER %d on GEMROC %d: TP_disable_FE bit set to %d and TriggerMode bit set to %d for channel %d' %(nT, GEMROC_ID, 0, 1, channel_ID_for_TPEn)
                            # TMSET 358 66
                            L1_lat_B3clk_local_param = 358
                            TM_window_in_B3clk_local_param = 66
                            GEM_COM1.MENU_set_L1_Lat_TM_Win_in_B3Ck_cycles(L1_lat_B3clk_local_param, TM_window_in_B3clk_local_param)
                            print '\nSet TM latency: %d and TM window: %d parameters on GEMROC %d' % (
                                L1_lat_B3clk_local_param, TM_window_in_B3clk_local_param, GEMROC_ID)
                            GEM_COM1.gemroc_DAQ_XX.extract_parameters_from_UDP_packet()  # acr 2018-07-23
                            # # CHK2TP
                            # Enab_nDisab_TP_from_L1_Chk_local = 1
                            # DAQ_set_TP_from_L1Chk(gemroc_DAQ_XX, GEMROC_ID, Enab_nDisab_TP_from_L1_Chk_local)
                            # print '\nEnable/nDisable TP from L1CHK signal: %d on GEMROC %d' % (Enab_nDisab_TP_from_L1_Chk_local, GEMROC_ID)
                            # ENPM SET TO 1; REMEMBER TO STOP THE TRIGGER GENERATION AT THIS POINT
                            if (PauseMode_Enable_Option == 1):
                                GEM_COM1.DAQ_set_Pause_Mode(1)
                                print '\nEnable DAQ Pause Mode: %d on GEMROC %d' % (1, GEMROC_ID)
                                # SRst 4 : Synchronous timing reset to all Tiger Configuration and Acquisition modules (TCAM)
                                GEM_COM1.SynchReset_to_TgtFEB(4, 1)
                                print '\nToALL_on GEMROC %d: sent synchronous reset' % (GEMROC_ID)
                                GEM_COM1.SynchReset_to_TgtTCAM(4, 1)
                                # PAUSE FLAG set
                                GEM_COM1.DAQ_Toggle_Set_Pause_bit()
                                print '\nDAQ Pause Set bit TOGGLED on GEMROC %d' % (GEMROC_ID)
                                print '\nDAQ waiting for first trigger'
                            else:
                                GEM_COM1.DAQ_set_Pause_Mode(0)
                                print '\nEnable DAQ Pause Mode: %d on GEMROC %d' % (0, GEMROC_ID)
                                # SRst 4 : Synchronous timing reset to all Tiger Configuration and Acquisition modules (TCAM)
                                GEM_COM1.SynchReset_to_TgtFEB(4, 1)
                                print '\nToALL_on GEMROC %d: sent synchronous reset' % (GEMROC_ID)
                            # DAQSET 0Xpattern 0xf 0 0 tl/TM 0
                            # TCAM_Enable_pattern_local = enable_pattern_array[NumTigerToConfigure]
                            TCAM_Enable_pattern_local = Pattern_of_Tiger_To_Configure
                            Periodic_FEB_TP_Enable_pattern_local = 0xF
                            #TL_nTM_option_local = GEM_COM1.TL_nTM_option
                            if (Int_TP_Burst_repeat_Enable_Option == 1):
                                TP_repeat_burst_local = 1
                            else:
                                TP_repeat_burst_local = 0
                            TP_Num_in_burst_local = 1
                            Periodic_L1_Enable_pattern_local = 0
                            # CHK2TP
                            if (DI_TL_nTM_option == 0):
                                Enab_nDisab_TP_from_L1_Chk_local = 1
                            else:
                                Enab_nDisab_TP_from_L1_Chk_local = 0 #TODO continua da qui
                            GEM_COM1.DAQ_set_TP_from_L1Chk(GEM_COM1.gemroc_DAQ_XX, Enab_nDisab_TP_from_L1_Chk_local)
                            print '\nEnable/nDisable TP from L1CHK signal: %d on GEMROC %d' % (Enab_nDisab_TP_from_L1_Chk_local, GEMROC_ID)
                            # set DAQ mode
                            # acr 2018-11-02 BEGIN using the most recent definition of function DAQ_set
                            # DAQ_set(gemroc_DAQ_XX, GEMROC_ID, TCAM_Enable_pattern_local, Periodic_FEB_TP_Enable_pattern_local,
                            #        TP_repeat_burst_local, DI_TP_Num_in_burst, DI_TL_nTM_option, DI_Periodic_L1_Enable_bit, DI_Enab_Auto_L1_from_TP_bit)
                            GEM_COM1.DAQ_set(TCAM_Enable_pattern_local, Periodic_FEB_TP_Enable_pattern_local, TP_repeat_burst_local, DI_TP_Num_in_burst, DI_TL_nTM_option, DI_Periodic_L1_Enable_bit, DI_Enab_Auto_L1_from_TP_bit)
                            # acr 2018-11-02 END   using the most recent definition of function DAQ_set
                            #print '\nStart DAQ from enabled TCAMs: %d on GEMROC %d; TL_nTM flag: %d' % ( TCAM_Enable_pattern_local, GEMROC_ID, DI_TL_nTM_option)
                            print '\nStart DAQ in %s mode. Enable TIGERs pattern: %d on GEMROC %d. Periodic TP enable: %d. Number of periodic TP in burst: %d. Periodic_L1_Enable_bit: %d. DI_Enab_Auto_L1_from_TP_bit: %d.' % ( GEM_COM1.print_TL_vs_nTM(DI_TL_nTM_option), TCAM_Enable_pattern_local, GEMROC_ID, TP_repeat_burst_local, DI_TP_Num_in_burst, DI_Periodic_L1_Enable_bit, DI_Enab_Auto_L1_from_TP_bit )
                            while input_queue.empty():
                                time.sleep(1)
                            os.system('cls')
                            sys.stdout.write(menu_string)


                    elif (input_array[0].lower() == 'test'):
                        if len(input_array) == 1:
                            print "Specify"
                        else:
                            if input_array[1].lower()=='s':
                                print "Synch test"
                                test_r=AN_CLASS.analisys_conf(GEM_COM1,c_inst,g_inst)
                                test_r.TIGER_GEMROC_sync_test()
                                test_r.__del__()
                            elif input_array[1].lower()=='c':
                                print "Configuration test"
                                test_r=AN_CLASS.analisys_conf(GEM_COM1,c_inst,g_inst)
                                test_r.TIGER_config_test()
                                test_r.__del__()
                            elif input_array[1].lower=="t":
                                print "Test pulse reception test"
                                test_r=AN_CLASS.analisys_conf(GEM_COM1,c_inst,g_inst)
                                test_r.TIGER_TP_test()
                                test_r.__del__()
                            else:
                                print "Wrong test instruction"
                            time.sleep(0.2)
                        sys.stdout.write(menu_string)
                    elif (input_array[0].lower()== 'counter'):
                        if len(input_array) != 4:
                            print "To few arguments"
                        else:
                            GEM_COM1.set_counter(input_array[1], input_array[2], input_array[3])
                    elif input_array[0].lower() == 'counter_display': # acr 2018-03-16 at IHEP
                        if len(input_array) == 1:
                            command_reply = GEM_COM1.Read_GEMROC_LV_CfgReg()
                            print '\nLVCR command_reply: %s' %binascii.b2a_hex(command_reply)
                            GEM_COM1.display_counter(command_reply)
                            print '\npress RETURN to continue'
                            while input_queue.empty():
                                time.sleep(1)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif input_array[0].lower() == 'counter_reset':  # acr 2018-03-16 at IHEP
                        if len(input_array) == 1:
                            GEM_COM1.reset_counter()
                            print ("\n counter reset")
                            time.sleep(0.1)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif (input_array[0].lower() == 'auto_td'):
                        print "Auto Time Delay setting"
                        test_r=AN_CLASS.analisys_conf(GEM_COM1,c_inst,g_inst)
                        safe_delays=test_r.TIGER_delay_tuning()

                        test_r.__del__()
                        input_queue.empty()
                        del input_array
                        print("Final TD values: FEB 0 = {}, FEB 1 = {},FEB 2 = {},FEB 3 = {}\n".format(safe_delays[0], safe_delays[1], safe_delays[2], safe_delays[3]))
                        print ("Do you want to set them? (y or n)\n")
                        input_array = (input_queue.get()).split()
                        ans1=input_array[0]
                        if ans1.lower() == "y":
                            GEM_COM1.set_FEB_timing_delays(int(safe_delays[3]), int(safe_delays[2]), int(safe_delays[1]),int(safe_delays[0]))
                            print "TD set\n"
                            time.sleep(0.5)
                        print ("Do you want to save them? (y or n)\n")
                        input_array = (input_queue.get()).split()
                        ans2=input_array[0]
                        if ans2.lower() == "y":
                            GEM_COM1.save_TD_delay(safe_delays)

                        clear_term()
                        sys.stdout.write(menu_string)
                    else:
                        print('\n bad command')
                        time.sleep(0.5)
                        clear_term()
                        sys.stdout.write(menu_string)

                else:
                    input_queue.empty()
                    del input_array

Menu_and_prompt()
print "\nExit debug. Bye!"
exit()
