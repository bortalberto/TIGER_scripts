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
GEM_COM1=COM_class.communication(GEMROC_ID, FEB_PWR_EN_pattern) #Create communication class

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
# \n LVCR                                                                             read and print setting of GEMROC LV configuration register  \
"\n DAQCR                                                                            read and print setting of GEMROC DAQ configuration register  \
\n GRST                                                                             RESETS ALL TIGER CONFIGURATION REGISTERS: must be executed before TIGER Global Register Write \
\n(GW)def   <TIGER_ID>(0 thru 7)                                                    (default file: \"TIGER_def_g_cfg_2018.txt\") \
\n(CW)def   <TIGER_ID>(0 thru 7) <channel_ID>(0 thru 64);                           if channel_ID =64 then WRITE ALL IN SEQUENCE (default file: \"TIGER_def_ch_cfg_2018.txt\"); \
\n(GR)d     <TIGER_ID>(0 thru 7)  \
\n(CR)d     <TIGER_ID>(0 thru 7) <channel_ID>(0 thru 64);                           if channel_ID = 64 then READ ALL channels IN SEQUENCE \
\n TPEnG    <TIGER_ID>(0 thru 7) <On_Off_param> (0 or 1);                           set FE_TPEnable bit in the Global Configuration Register\
\n(TP)EW_ch <TIGER_ID>(0 thru 7) <channel_ID>(0 thru 64) <TP_disable_FE_param> (0 or 1) <TriggerMode_param> (0 or 1);   if channel_ID = 64 then act on all channels\
\n(VT1)_ch  <TIGER_ID>(0 thru 7) <channel_ID>(0 thru 64) <VthT1 param> (0 thru 63); if channel_ID = 64 then act on VthT1 for ALL channels\
\n SRst     <SynchRst_TargetFEB>(0 to 4)                                            send a sycnh rst to the target FEB(0 to 3); if 4 is input then send synch rst to ALL FEBs  \
\n DRst     <SynchRst_TargetTCAM>(0 to 4)                                           send a sycnh rst to the TIGER Data Processing unit (TCAM)0 to 3; if 4 is input then send synch rst to ALL TCAMs    \
\n DAQSET   <TCAM_En_pattern>(0x0 thru 0xF) <FEB_TP_En_pattern>(0x0 thru 0xF) <TP_repeat_burst>(0 or 1) <TP_Num_in_burst>(0 thru 511) <TL_nTM_ACQ_choice>(0 or 1) <Periodic_L1_Enable>(0 or 1)  set DAQ related parameters  \
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
\n CHECK_RATE <TIGER NUMBER><NUMBER OF FRAMES>                                      show the rate with the selected number of frames\
\n RUN_PREP  <Number of sigma>                                                      get ready for run, set how many sigma away set the threshold\
\n PULSE_MODE                                                                       use enter for pulse on designed channels, write q to exit\
\n SH                                                                               set sample and hold mode\
\n TMSET    <L1_lat_B3clk_param>( 100 to 1023; default = 358) <TM_window_in_B3clk_param>(1 to 127; default = 66) \
\n CONFIG_PAUSE                                                                     set default config (global and channel, pause state) in all the TIGERS\
\n(X)CVRTST  <NumWordToSend>(0 thru 127; ONLY 0 is implemented at the moment)      Perform XCVR loopback test. If NumWordToSend=0 then capture of the next TM pkt is performed; else NumWordToSend data words are looped back\
\n(D)efault_Init <Num_of_TIGERs_Enabled>(1 thru 8) <Ext/Int timing>(\"1\" for Ext) <TL/TM mode>(\"1\" for TL mode)      Default initialization \
\n(Dtest)Default_Init_test <ID_of_TIGERs_Enabled>(1 thru 8) <Ext/Int timing>(\"1\" for Ext) <TL/TM mode>(\"1\" for TL mode)      Default initialization \
\n(Q)uit: leave\
\nEnter your command:\n ")

DONE = False
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
    GEM_COM1.IVT_log_file.write('\n%s' %datetime.datetime.now().strftime(fmt) )
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
                            command_reply = GEM_COM1.Read_GEMROC_DAQ_CfgReg(GEM_COM1.gemroc_DAQ_XX)
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
                            command_sent = GEM_COM1.WriteTgtGEMROC_TIGER_GCfgReg_fromfile(g_inst, int(input_array[1]),
                                                                                          default_g_inst_settigs_filename)
                            print '\nGWdef command_reply: %s' %binascii.b2a_hex(command_sent)
                            command_reply = GEM_COM1.ReadTgtGEMROC_TIGER_GCfgReg(g_inst, int(input_array[1]))
                            print '\nGRd   command_reply: %s' %binascii.b2a_hex(command_reply)
                            if (int (binascii.b2a_hex(command_sent),16)) !=( (int (binascii.b2a_hex(command_reply),16)) -2048 ):
                                print "---____----____----____----____----"
                                print "!!! ERROR IN CONFIGURATION !!!"
                                print "---____----____----____----____----"
                                time.sleep(4)
                            time.sleep(2)
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
                            command_sent= GEM_COM1.WriteTgtGEMROC_TIGER_ChCfgReg_fromfile(c_inst, int(input_array[1]),
                                                                                          int(input_array[2]),
                                                                                          default_ch_inst_settigs_filename)
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
                            TP_disable_FE_param = int(input_array[3])
                            TriggerMode_param = int(input_array[4])
                            GEM_COM1.Set_GEMROC_TIGER_ch_TPEn(c_inst, int(input_array[1]), int(input_array[2]),
                                                              TP_disable_FE_param, TriggerMode_param)
                            print '\nTo TIGER %d on GEMROC %d: TP_disable_FE bit set to %d and TriggerMode bit set to %d for channel %d' %(int(input_array[1]), GEMROC_ID, int(input_array[3]), int(input_array[4]),int(input_array[2]) )
                            time.sleep(2)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif (input_array[0] == 'VT1_ch') or (input_array[0] == 'VT1'):
                        if len(input_array) == 4:
                            GEM_COM1.Set_Vth_T1(c_inst, int(input_array[1]), int(input_array[2]), int(input_array[3]))
                            print '\nTo TIGER %d on GEMROC %d: Vth_T1 set to %d for channel %d' %(int(input_array[1]), GEMROC_ID, int(input_array[3]), int(input_array[2]) )
                            time.sleep(2)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif (input_array[0] == 'AVCaspGset') or (input_array[0] == 'AV'):
                        if len(input_array) == 3:
                            GEM_COM1.set_AVcasp_global(g_inst, int(input_array[1]), int(input_array[2]))
                            time.sleep(2)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                    elif input_array[0] == 'SRst':
                        if len(input_array) == 2:
                            if int(input_array[1]) < 4:
                                To_ALL_FEB_enable = 0
                            else:
                                To_ALL_FEB_enable = 1
                            TargetFEB = int(input_array[1]) & 0x3
                            GEM_COM1.SynchReset_to_TgtFEB(GEM_COM1.gemroc_DAQ_XX, TargetFEB, To_ALL_FEB_enable)
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
                            GEM_COM1.SynchReset_to_TgtTCAM(GEM_COM1.gemroc_DAQ_XX, TargetTCAM, To_ALL_TCAM_enable)
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
                            GEM_COM1.SynchReset_to_TgtTCAM(GEM_COM1.gemroc_DAQ_XX, TargetTCAM, To_ALL_TCAM_enable)
                            print '\nTo TCAM %d or ToALL_TCAM: %d on GEMROC %d: sent synchronous reset' % (TargetTCAM, To_ALL_TCAM_enable, GEMROC_ID)
                            time.sleep(2)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                            # acr 2018-04-24 elif (input_array[0] == 'DSTART'):
                    elif (input_array[0] == 'DAQSET'):
                            # acr 2018-04-23 if (len(input_array) == 3):
                            if (len(input_array) == 7):  # 5):
                                TCAM_Enable_pattern = int(input_array[1], 0) & 0xFF
                                Periodic_FEB_TP_Enable_pattern = int(input_array[2], 0) & 0xFF
                                TP_repeat_burst = int(input_array[3], 0) & 0x1
                                TP_Num_in_burst = int(input_array[4], 0) & 0x1FF
                                TL_nTM_ACQ_choice = int(input_array[5], 0) & 0x1
                                Periodic_L1_Enable_pattern = int(input_array[6], 0) & 0x1
                                # acr 2018-04-23 DAQ_set_and_TL_start(gemroc_DAQ_XX, GEMROC_ID, TCAM_Enable_pattern, Periodic_FEB_TP_Enable_pattern)
                                # acr 2018-05-31 DAQ_set(gemroc_DAQ_XX, GEMROC_ID, TCAM_Enable_pattern, Periodic_FEB_TP_Enable_pattern, TP_repeat_burst, TP_Num_in_burst)
                                # acr 2018-06-04 DAQ_set(gemroc_DAQ_XX, GEMROC_ID, TCAM_Enable_pattern, Periodic_FEB_TP_Enable_pattern, TP_repeat_burst, TP_Num_in_burst, TL_nTM_ACQ_choice)
                                gemroc_DAQ_XX = GEM_COM1.gemroc_DAQ_XX
                                GEM_COM1.DAQ_set(gemroc_DAQ_XX, TCAM_Enable_pattern, Periodic_FEB_TP_Enable_pattern,
                                                 TP_repeat_burst, TP_Num_in_burst, TL_nTM_ACQ_choice,
                                                 Periodic_L1_Enable_pattern)
                                print '\nStart TL DAQ from enable TCAM pattern: %d on GEMROC %d' % (TCAM_Enable_pattern, GEMROC_ID)
                                time.sleep(2)
                                os.system('clear')
                                sys.stdout.write(menu_string)
                    elif (input_array[0] == 'ENPM'):
                            if (len(input_array) == 2):
                                Enable_DAQ_Pause_Mode = int(input_array[1], 0) & 0x1
                                GEM_COM1.DAQ_set_Pause_Mode(GEM_COM1.gemroc_DAQ_XX, Enable_DAQ_Pause_Mode)
                                print '\nEnable DAQ Pause Mode: %d on GEMROC %d' % (Enable_DAQ_Pause_Mode, GEMROC_ID)
                                time.sleep(2)
                                os.system('clear')
                                sys.stdout.write(menu_string)
                    elif (input_array[0] == 'CKEXT'):
                        if (len(input_array) == 2):
                            Derive_DAQck_From_Ext_nInt_source = int(input_array[1], 0) & 0x1
                            GEM_COM1.DAQ_set_DAQck_source(GEM_COM1.gemroc_DAQ_XX, Derive_DAQck_From_Ext_nInt_source)
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
                            GEM_COM1.DAQ_Toggle_Set_Pause_bit(GEM_COM1.gemroc_DAQ_XX)
                            print '\nDAQ Pause Set bit TOGGLED on GEMROC %d' % (GEMROC_ID)
                            time.sleep(2)
                            os.system('clear')
                            sys.stdout.write(menu_string)

                    elif input_array[0].lower() == 'vthr_load':
                        if len(input_array) == 3:
                            GEM_COM1.Load_VTH_fromfile(c_inst, int(input_array[1]) & 0xFF, int(input_array[2]), 0, True)
                            print ("\nVth Loaded on chip {}").format (int(input_array[1]))
                            time.sleep(1)
                            os.system('clear')
                            sys.stdout.write(menu_string)
                        else:
                            print"\nCheck input formatting\n"



                    elif input_array[0].lower() == 'auto':
                        if len(input_array) == 3:
                            test_r = AN_CLASS.analisys_read(GEM_COM1, c_inst)
                            #
                            # auto_tune_C = AN_CLASS.analisys_conf(GEM_COM1,c_inst,g_inst )
                            # GEM_COM1.Load_VTH_fromfile(c_inst, GEMROC_ID, int(input_array[1]),3, 0)
                            # print ("\nVth Loaded on TIGER {}").format(int(input_array[1]))
                            # time.sleep(0.2)
                            # auto_tune_C.fill_VTHR_matrix(3, 0, int(input_array[1]))
                            # auto_tune_C.thr_autotune(int(input_array[1]),int(input_array[2]),test_r)
                            #
                            # auto_tune_C.__del__()
                            #
                            # test_r.__del__()
                            #
                            #
                            # os.system('clear')
                            # sys.stdout.write(menu_string)
                            for T in range (0,8):
                                test_r = AN_CLASS.analisys_read(GEM_COM1, c_inst)

                                auto_tune_C = AN_CLASS.analisys_conf(GEM_COM1,c_inst,g_inst )
                                GEM_COM1.Load_VTH_fromfile(c_inst, T, 3, 0)
                                print "\nVth Loaded on TIGER {}".format(T)
                                time.sleep(0.2)
                                auto_tune_C.fill_VTHR_matrix(3, 0, T)
                                auto_tune_C.thr_autotune(T,int(input_array[2]),test_r)

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


                            GEM_COM1.Load_VTH_fromfile_autotuned(c_inst, int(input_array[1]))

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
                        test_c = AN_CLASS.analisys_conf(GEM_COM1, c_inst, g_inst)
                        test_r = AN_CLASS.analisys_read(GEM_COM1,c_inst )
                        test_c.thr_preconf()
                        test_c.thr_conf(test_r)


                        test_r.save_scan_on_file()

                        test_r.make_rate()
                        test_r.colorPlot(GEM_COM1.Tscan_folder+sep+"GEMROC{}".format(GEMROC_ID)+sep+"GEMROC {}".format(GEMROC_ID)+"rate",True)
                        test_r.colorPlot(GEM_COM1.Tscan_folder+sep+"GEMROC{}".format(GEMROC_ID)+sep+"GEMROC {}".format(GEMROC_ID)+"conteggi")


                        test_r.normalize_rate()
                        test_r.global_sfit()
                        test_r.__del__()
                        test_c.__del__()

                        sys.stdout.write(menu_string)
                    elif input_array[0].lower() == 'dt':
                        if (len(input_array) == 2):  # 5):
                            TCAM_Enable_pattern = int(input_array[1], 0) & 0xFF
                            gemroc_DAQ_XX = GEM_COM1.gemroc_DAQ_XX
                            GEM_COM1.DAQ_TIGER_SET(GEM_COM1.gemroc_DAQ_XX, TCAM_Enable_pattern)
                            GEM_COM1.SynchReset_to_TgtFEB(GEM_COM1.gemroc_DAQ_XX, 0, 1)
                            GEM_COM1.SynchReset_to_TgtTCAM(GEM_COM1.gemroc_DAQ_XX, 0, 1)
                            time.sleep(2)
                            os.system('clear')
                            sys.stdout.write(menu_string)

                    elif input_array[0].lower() == 'run_prep':
                        if len(input_array) == 2:

                            for T in range (0,4):

                                default_filename = "TIGER_def_g_cfg_2018.txt"
                                command_reply = GEM_COM1.WriteTgtGEMROC_TIGER_GCfgReg_fromfile(g_inst, T,
                                                                                               default_filename)
                                print '\nGWdef command_reply: %s' % binascii.b2a_hex(command_reply)
                                command_reply = GEM_COM1.ReadTgtGEMROC_TIGER_GCfgReg(g_inst, T)
                                print '\nGRd   command_reply: %s' % binascii.b2a_hex(command_reply)

                                default_filename = "TIGER_def_ch_cfg_2018.txt"
                                command_reply = GEM_COM1.WriteTgtGEMROC_TIGER_ChCfgReg_fromfile(c_inst, T, 64,
                                                                                                default_filename)
                                print '\nCWdef command_reply: %s' %binascii.b2a_hex(command_reply)
                                command_reply = GEM_COM1.ReadTgtGEMROC_TIGER_ChCfgReg(c_inst, T, 64, 0)
                                print '\nCRd   command_reply: %s' %binascii.b2a_hex(command_reply)
                                # Setting trigger mode 0

                            GEM_COM1.DAQ_set_TP_from_Ext_Trig(GEM_COM1.gemroc_DAQ_XX, 1)
                            #Setting trigger mode 0

                            GEM_COM1.Set_GEMROC_TIGER_ch_TPEn(c_inst, 0, 64, 1, 0)
                            GEM_COM1.Set_GEMROC_TIGER_ch_TPEn(c_inst, 1, 64, 1, 0)
                            GEM_COM1.Set_GEMROC_TIGER_ch_TPEn(c_inst, 2, 64, 1, 0)
                            GEM_COM1.Set_GEMROC_TIGER_ch_TPEn(c_inst, 3, 64, 1, 0)

                            # Loading VTH
                            GEM_COM1.Load_VTH_fromfile(c_inst, 0, int(input_array[1]), 0)
                            GEM_COM1.Load_VTH_fromfile(c_inst, 1, int(input_array[1]), 0)
                            GEM_COM1.Load_VTH_fromfile(c_inst, 2, int(input_array[1]), 3)
                            GEM_COM1.Load_VTH_fromfile(c_inst, 3, int(input_array[1]), 3)

                            print("\nSuppressing noisy channels")

                            GEM_COM1.Set_GEMROC_TIGER_ch_TPEn(c_inst, 1, 14, 1, 3)
                            GEM_COM1.Set_GEMROC_TIGER_ch_TPEn(c_inst, 1, 31, 1, 3)
                            GEM_COM1.Set_GEMROC_TIGER_ch_TPEn(c_inst, 1, 32, 1, 3)
                            GEM_COM1.Set_GEMROC_TIGER_ch_TPEn(c_inst, 3, 14, 1, 3)

                            GEM_COM1.Set_GEMROC_TIGER_ch_TPEn(c_inst, 1, 41, 1, 3)
                            GEM_COM1.Set_GEMROC_TIGER_ch_TPEn(c_inst, 1, 54, 1, 3)
                            GEM_COM1.Set_GEMROC_TIGER_ch_TPEn(c_inst, 1, 34, 1, 3)

                            GEM_COM1.Set_GEMROC_TIGER_ch_TPEn(c_inst, 3, 18, 1, 3)



                            print("\nAllow pulse on channel {} and 11 on chip 2 both FEB".format(3))
                            GEM_COM1.Set_GEMROC_TIGER_ch_TPEn(c_inst, 1, 3, 1, 1)
                            GEM_COM1.Set_GEMROC_TIGER_ch_TPEn(c_inst, 2, 58, 1, 1)


                            print("\nSetting TCAM pattern on all chips")
                            GEM_COM1.DAQ_set(GEM_COM1.gemroc_DAQ_XX, 0xf, 0xf, 0, 0)


                            print("\nSending syncronous reset")
                            # GEM_COM1.SynchReset_to_TgtTCAM(GEM_COM1.gemroc_DAQ_XX, GEMROC_ID, 0, 4)
                            GEM_COM1.SynchReset_to_TgtFEB(GEM_COM1.gemroc_DAQ_XX, 0, 4)
                            #print ("\n pausing")
                            # GEM_COM1.DAQ_set_Pause_Mode(GEM_COM1.gemroc_DAQ_XX, GEMROC_ID, 1)
                            # GEM_COM1.DAQ_Toggle_Set_Pause_bit(GEM_COM1.gemroc_DAQ_XX, GEMROC_ID)

                            print '\npress RETURN to continue'
                        else:
                            print ("\n Missing sigma number")
                        while input_queue.empty():
                            time.sleep(1)
                        os.system('clear')
                        sys.stdout.write(menu_string)
                    elif input_array[0].lower() == 'pulse_mode':
                        running=True
                        while running==True:
                            command=raw_input("press RETURN to launche TP")
                            if command=="q":
                                running=False
                            else:
                                GEM_COM1.TP_ENABLE(GEM_COM1.gemroc_DAQ_XX, 1)
                                time.sleep(0.1)
                                GEM_COM1.TP_ENABLE(GEM_COM1.gemroc_DAQ_XX, 0)

                        os.system('clear')
                        sys.stdout.write(menu_string)

                    elif input_array[0].lower() == 'config':
                        GEM_COM1.ResetTgtGEMROC_ALL_TIGER_GCfgReg(GEM_COM1.gemroc_DAQ_XX)

                        for T in range(0,8):
                            GEM_COM1.WriteTgtGEMROC_TIGER_GCfgReg_fromfile(g_inst, T, default_g_inst_settigs_filename)
                        print("Global configuration set\n")
                        for T in range (0,8):
                            GEM_COM1.WriteTgtGEMROC_TIGER_ChCfgReg_fromfile(c_inst, T, 64,
                                                                            default_ch_inst_settigs_filename)
                        print("Channel configuration set\n")
                        time.sleep(0.5)
                        os.system('clear')
                        sys.stdout.write(menu_string)

                    elif input_array[0].lower() == 'sh':
                        for T in range(0,8):
                            GEM_COM1.set_sampleandhold_mode(c_inst, T, 64)

                        print("Sample and hold mode set set\n")
                        time.sleep(0.5)
                        os.system('clear')
                        sys.stdout.write(menu_string)


                    elif input_array[0].lower() == 'config_pause':
                        #CKEXT 1
                        Derive_DAQck_From_Ext_nInt_source = int("1", 0) & 0x1
                        GEM_COM1.DAQ_set_DAQck_source(GEM_COM1.gemroc_DAQ_XX, Derive_DAQck_From_Ext_nInt_source)
                        print '\nDAQ_set_DAQck_source: %d on GEMROC %d' % (Derive_DAQck_From_Ext_nInt_source, GEMROC_ID)
                        #GRST
                        GEM_COM1.ResetTgtGEMROC_ALL_TIGER_GCfgReg(GEM_COM1.gemroc_DAQ_XX)
                        #GW TIGERID
                        for T in range(0, 8):
                            GEM_COM1.WriteTgtGEMROC_TIGER_GCfgReg_fromfile(g_inst, T, default_g_inst_settigs_filename)
                        print("Global configuration set\n")
                        # CW TIGERID ChID
                        for T in range(0, 8):
                            GEM_COM1.WriteTgtGEMROC_TIGER_ChCfgReg_fromfile(c_inst, T, 64,
                                                                            default_ch_inst_settigs_filename)
                        print("Channel configuration set\n")
                        #ENPM
                        Enable_DAQ_Pause_Mode = int("1", 0) & 0x1
                        GEM_COM1.DAQ_set_Pause_Mode(GEM_COM1.gemroc_DAQ_XX, Enable_DAQ_Pause_Mode)
                        print '\nEnable DAQ Pause Mode: %d on GEMROC %d' % (Enable_DAQ_Pause_Mode, GEMROC_ID)
                        #PAUSE
                        GEM_COM1.DAQ_Toggle_Set_Pause_bit(GEM_COM1.gemroc_DAQ_XX)
                        print '\nDAQ Pause Set bit TOGGLED on GEMROC %d' % (GEMROC_ID)
                        time.sleep(0.5)
                        os.system('clear')
                        sys.stdout.write(menu_string)

                    elif (input_array[0] == 'TMSET'):  # acr 2018-07-23
                        # acr 2018-04-23 if (len(input_array) == 3):
                        if (len(input_array) == 3):  # 5):
                            L1_lat_B3clk_param = int(input_array[1], 0) & 0x3FF
                            TM_window_in_B3clk_param = int(input_array[2], 0) & 0x7F
                            GEM_COM1.MENU_set_L1_Lat_TM_Win_in_B3Ck_cycles(GEM_COM1.gemroc_DAQ_XX, L1_lat_B3clk_param,
                                                                           TM_window_in_B3clk_param)
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
                            os.system('cls')
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
                            os.system('cls')
                            sys.stdout.write(menu_string)

                    elif ((input_array[0] == 'Default_Init') or (input_array[0] == 'D')):
                        if (len(input_array) == 4):
                            NumTigerToConfigure = int(input_array[1], 0) & 0x7
                            Ext_nInt_Clk_option = int(input_array[2], 0) & 0x1
                            TL_nTM_option = int(input_array[3], 0) & 0x1
                            # SET TIMING SOURCE: 1 for External, 0 for Internal
                            GEM_COM1.DAQ_set_DAQck_source(GEM_COM1.gemroc_DAQ_XX, Ext_nInt_Clk_option)
                            # TIGER INITIALIZATION
                            GEM_COM1.ResetTgtGEMROC_ALL_TIGER_GCfgReg(GEM_COM1.gemroc_DAQ_XX)
                            # TIGER GLOBAL REGISTER configuration
                            for nT in range(0, NumTigerToConfigure):
                                command_reply = GEM_COM1.WriteTgtGEMROC_TIGER_GCfgReg_fromfile(g_inst, nT,
                                                                                               default_g_inst_settigs_filename)
                                print '\nGWdef command_reply: %s' % binascii.b2a_hex(command_reply)
                                command_reply = GEM_COM1.ReadTgtGEMROC_TIGER_GCfgReg(g_inst, nT)
                                print '\nGRd   command_reply: %s' % binascii.b2a_hex(command_reply)
                            # TIGER CHANNEL REGISTER configuration
                            for nT in range(0, NumTigerToConfigure):
                                # command_reply = GEM_COM1.WriteTgtGEMROC_TIGER_ChCfgReg_fromfile(c_inst, GEMROC_ID, nT, 64,default_TIGER_ch_cfg_fname, GEM_COM1.log_file)
                                command_reply = GEM_COM1.WriteTgtGEMROC_TIGER_ChCfgReg_fromfile(c_inst, nT, 64,
                                                                                                default_ch_inst_settigs_filename)
                                print '\nCWdef command_reply: %s' % binascii.b2a_hex(command_reply)
                                # command_reply = ReadTgtGEMROC_TIGER_ChCfgReg (c_inst, GEMROC_ID, int(input_array[1]), int(input_array[2]), 0 )
                                command_reply = GEM_COM1.ReadTgtGEMROC_TIGER_ChCfgReg(c_inst, nT, 64, 0)
                                print '\nCRd   command_reply: %s' % binascii.b2a_hex(command_reply)
                            # TPEnable bit in the Global Cfg register
                            for nT in range(0, NumTigerToConfigure):
                                GEM_COM1.set_FE_TPEnable(g_inst, nT, 1)
                                print '\nTo TIGER %d on GEMROC %d: GCreg FE_TPEnable bit set to %d' % (nT, GEMROC_ID, 1)
                            # TP_disable_FE and TriggerMode bit setting in the channel configuration for selected (n_channel = 2 * N_TIGER) channels
                            for nT in range(0, NumTigerToConfigure):
                                GEM_COM1.Set_GEMROC_TIGER_ch_TPEn(c_inst, nT, nT * 2, 0, 1)
                                print '\nTo TIGER %d on GEMROC %d: TP_disable_FE bit set to %d and TriggerMode bit set to %d for channel %d' % (
                                nT, GEMROC_ID, 0, 1, nT * 2)
                            # ENPM SET TO 1; REMEMBER TO STOP THE TRIGGER GENERATION AT THIS POINT
                            GEM_COM1.DAQ_set_Pause_Mode(GEM_COM1.gemroc_DAQ_XX, 1)
                            print '\nEnable DAQ Pause Mode: %d on GEMROC %d' % (1, GEMROC_ID)
                            # SRst 4 : Synchronous timing reset to all Tiger Configuration and Acquisition modules (TCAM)
                            GEM_COM1.SynchReset_to_TgtFEB(GEM_COM1.gemroc_DAQ_XX, 4, 1)
                            print '\nToALL_on GEMROC %d: sent synchronous reset' % (GEMROC_ID)
                            # PAUSE FLAG set
                            GEM_COM1.DAQ_Toggle_Set_Pause_bit(GEM_COM1.gemroc_DAQ_XX)
                            print '\nDAQ Pause Set bit TOGGLED on GEMROC %d' % (GEMROC_ID)
                            # TMSET 358 66
                            L1_lat_B3clk_local_param = 358
                            TM_window_in_B3clk_local_param = 66
                            GEM_COM1.MENU_set_L1_Lat_TM_Win_in_B3Ck_cycles(GEM_COM1.gemroc_DAQ_XX,
                                                                           L1_lat_B3clk_local_param,
                                                                           TM_window_in_B3clk_local_param)
                            print '\nSet TM latency: %d and TM window: %d parameters on GEMROC %d' % ( L1_lat_B3clk_local_param, TM_window_in_B3clk_local_param, GEMROC_ID)
                            GEM_COM1.gemroc_DAQ_XX.extract_parameters_from_UDP_packet()  # acr 2018-07-23
                            # CHK2TP
                            Enab_nDisab_TP_from_L1_Chk_local = 1
                            GEM_COM1.DAQ_set_TP_from_L1Chk(GEM_COM1.gemroc_DAQ_XX, Enab_nDisab_TP_from_L1_Chk_local)
                            print '\nEnab_nDisab_TP_from_Ext_triggers: %d on GEMROC %d' % (Enab_nDisab_TP_from_L1_Chk_local, GEMROC_ID)

                            # DAQSET 0Xpattern 0xf 0 0 tl/TM 0
                            TCAM_Enable_pattern_local = GEM_COM1.enable_pattern_array[NumTigerToConfigure]
                            Periodic_FEB_TP_Enable_pattern_local = 0xF
                            TP_repeat_burst_local = 0
                            TP_Num_in_burst_local = 0
                            TL_nTM_option_local = TL_nTM_option
                            Periodic_L1_Enable_pattern_local = 0
                            GEM_COM1.DAQ_set(GEM_COM1.gemroc_DAQ_XX, TCAM_Enable_pattern_local,
                                             Periodic_FEB_TP_Enable_pattern_local, TP_repeat_burst_local,
                                             TP_Num_in_burst_local, TL_nTM_option_local,
                                             Periodic_L1_Enable_pattern_local)
                            print '\nStart DAQ from enabled TCAMs: %d on GEMROC %d; TL_nTM flag: %d' % (TCAM_Enable_pattern_local, GEMROC_ID, TL_nTM_option_local)
                            while input_queue.empty():
                                time.sleep(1)
                            os.system('cls')
                            sys.stdout.write(menu_string)


                    elif ((input_array[0] == 'Default_Init_Test') or (input_array[0] == 'Dtest')):
                        if (len(input_array) == 4):
                            # NumTigerToConfigure = int(input_array[1], 0) & 0x7
                            NumTigerToConfigure = int(input_array[1], 0) & 0xF
                            Ext_nInt_Clk_option = int(input_array[2], 0) & 0x1
                            TL_nTM_option = int(input_array[3], 0) & 0x1
                            # SET TIMING SOURCE: 1 for External, 0 for Internal
                            GEM_COM1.DAQ_set_DAQck_source(GEM_COM1.gemroc_DAQ_XX, Ext_nInt_Clk_option)
                            # TIGER INITIALIZATION
                            GEM_COM1.ResetTgtGEMROC_ALL_TIGER_GCfgReg(GEM_COM1.gemroc_DAQ_XX)
                            # TIGER GLOBAL REGISTER configuration
                            # for nT in range(0, NumTigerToConfigure):
                            for nT in range(0, 8):
                                command_reply = GEM_COM1.WriteTgtGEMROC_TIGER_GCfgReg_fromfile(g_inst, nT,
                                                                                               default_g_inst_settigs_filename)
                                print '\nGWdef command_reply: %s' % binascii.b2a_hex(command_reply)
                                command_reply = GEM_COM1.ReadTgtGEMROC_TIGER_GCfgReg(g_inst, nT)
                                print '\nGRd   command_reply: %s' % binascii.b2a_hex(command_reply)
                            # TIGER CHANNEL REGISTER configuration
                            for nT in range(0, 8):
                            # for nT in range(0, NumTigerToConfigure):
                                # command_reply = GEM_COM1.WriteTgtGEMROC_TIGER_ChCfgReg_fromfile(c_inst, GEMROC_ID, nT, 64,default_TIGER_ch_cfg_fname, GEM_COM1.log_file)
                                command_reply = GEM_COM1.WriteTgtGEMROC_TIGER_ChCfgReg_fromfile(c_inst, nT, 64,
                                                                                                default_ch_inst_settigs_filename)
                                print '\nCWdef command_reply: %s' % binascii.b2a_hex(command_reply)
                                # command_reply = ReadTgtGEMROC_TIGER_ChCfgReg (c_inst, GEMROC_ID, int(input_array[1]), int(input_array[2]), 0 )
                                command_reply = GEM_COM1.ReadTgtGEMROC_TIGER_ChCfgReg(c_inst, nT, 64, 0)
                                print '\nCRd   command_reply: %s' % binascii.b2a_hex(command_reply)
                            # TPEnable bit in the Global Cfg register
                            for nT in range(0, 8):
                                # for nT in range(0, NumTigerToConfigure):
                                GEM_COM1.set_FE_TPEnable(g_inst, nT, 1)
                                print '\nTo TIGER %d on GEMROC %d: GCreg FE_TPEnable bit set to %d' % (nT, GEMROC_ID, 1)
                            # TP_disable_FE and TriggerMode bit setting in the channel configuration for selected (n_channel = 2 * N_TIGER) channels
                            for nT in range(0, 8):
                                # for nT in range(0, NumTigerToConfigure):
                                GEM_COM1.Set_GEMROC_TIGER_ch_TPEn(c_inst, nT, nT * 2, 0, 1)
                                print '\nTo TIGER %d on GEMROC %d: TP_disable_FE bit set to %d and TriggerMode bit set to %d for channel %d' % (
                                    nT, GEMROC_ID, 0, 1, nT * 2)
                            # ENPM SET TO 1; REMEMBER TO STOP THE TRIGGER GENERATION AT THIS POINT
                            GEM_COM1.DAQ_set_Pause_Mode(GEM_COM1.gemroc_DAQ_XX, 1)
                            print '\nEnable DAQ Pause Mode: %d on GEMROC %d' % (1, GEMROC_ID)
                                    # SRst 4 : Synchronous timing reset to all Tiger Configuration and Acquisition modules (TCAM)
                            GEM_COM1.SynchReset_to_TgtFEB(GEM_COM1.gemroc_DAQ_XX, 4, 1)
                            print '\nToALL_on GEMROC %d: sent synchronous reset' % (GEMROC_ID)
                                    # PAUSE FLAG set
                            GEM_COM1.DAQ_Toggle_Set_Pause_bit(GEM_COM1.gemroc_DAQ_XX)
                            print '\nDAQ Pause Set bit TOGGLED on GEMROC %d' % (GEMROC_ID)
                            # TMSET 358 66
                            L1_lat_B3clk_local_param = 358
                            TM_window_in_B3clk_local_param = 66
                            GEM_COM1.MENU_set_L1_Lat_TM_Win_in_B3Ck_cycles(GEM_COM1.gemroc_DAQ_XX, L1_lat_B3clk_local_param,TM_window_in_B3clk_local_param)
                            print '\nSet TM latency: %d and TM window: %d parameters on GEMROC %d' % (
                            L1_lat_B3clk_local_param, TM_window_in_B3clk_local_param, GEMROC_ID)
                            GEM_COM1.gemroc_DAQ_XX.extract_parameters_from_UDP_packet()  # acr 2018-07-23
                            # CHK2TP
                            Enab_nDisab_TP_from_L1_Chk_local = 1
                            GEM_COM1.DAQ_set_TP_from_L1Chk(GEM_COM1.gemroc_DAQ_XX,
                                                           Enab_nDisab_TP_from_L1_Chk_local)
                            print '\nEnab_nDisab_TP_from_Ext_triggers: %d on GEMROC %d' % (
                            Enab_nDisab_TP_from_L1_Chk_local, GEMROC_ID)

                            # DAQSET 0Xpattern 0xf 0 0 tl/TM 0
                            # TCAM_Enable_pattern_local = GEM_COM1.enable_pattern_array[NumTigerToConfigure]

                            # TCAM_Enable_pattern_local = 2**(NumTigerToConfigure-1)#Test 1 Tiger
                            TCAM_Enable_pattern_local = GEM_COM1.enable_pattern_array_test[NumTigerToConfigure]
                            print  '\n!!! NumTigerToConfigur: %d TCAM_Enable_pattern_local %d' % (NumTigerToConfigure, TCAM_Enable_pattern_local)

                            Periodic_FEB_TP_Enable_pattern_local = 0xF
                            TP_repeat_burst_local = 0
                            TP_Num_in_burst_local = 0
                            TL_nTM_option_local = TL_nTM_option
                            Periodic_L1_Enable_pattern_local = 0
                            GEM_COM1.DAQ_set(GEM_COM1.gemroc_DAQ_XX, TCAM_Enable_pattern_local, Periodic_FEB_TP_Enable_pattern_local,TP_repeat_burst_local, TP_Num_in_burst_local, TL_nTM_option_local, Periodic_L1_Enable_pattern_local)
                            print '\nStart DAQ from enabled TCAMs: %d on GEMROC %d; TL_nTM flag: %d' % (
                            TCAM_Enable_pattern_local, GEMROC_ID, TL_nTM_option_local)
                        while input_queue.empty():
                            time.sleep(1)
                        os.system('cls')
                        sys.stdout.write(menu_string)

                    else:
                        print('\n bad command')
                        time.sleep(0.5)
                        os.system('clear')
                        sys.stdout.write(menu_string)

                else:
                    input_queue.empty()
                    del input_array

Menu_and_prompt()
print "\nExit debug. Bye!"
GEM_COM1.__del__()
exit()
