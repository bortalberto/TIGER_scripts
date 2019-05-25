# file: GEMconf_module.py
# author: Angelo Cotta Ramusino INFN Ferrara
# date: 27 June 2017
# purpose: a collection of classes handling settings for the global, channel and GEMROC module functional registers
# list of main modifications / additions:
# acr 2018-01-25 removing unused parameter self.CompactDataFormat 
# acr 2018-01-13 split the handling of the GEMROC LV and DAQ configuration parameters
import pickle
import copy
command_code_shift = 11 # acr 2017-08-29
target_TIGER_ID_shift = 8 # acr 2017-08-29
GEMROC_CMD_LV_Num_of_params = 31 # acr 2018-01-15
GEMROC_CMD_LV_Num_Of_PktWords = 12 # acr 2018-01-15
# acr 2018-04-24 GEMROC_CMD_DAQ_Num_of_params = 15 ## ACR 2018-03-15 AT IHEP: ADDED UDP_DATA_DESTINATION_IPADDR AND UDP_DATA_DESTINATION_IPPORT; GEMROC_CMD_DAQ_Num_of_params = 13 # acr 2018-01-15
GEMROC_CMD_DAQ_Num_of_params = 16 # ACR 2018-04-23 AT CERN: ADDED Debug_functions_control_bits_U4
GEMROC_CMD_DAQ_Num_Of_PktWords = 5 # acr 2018-01-15


# acr 2018-01-25 introduced swap function for little endian parameter values
def swap_order_N_bits( Hex_data, N_bits ):
    #"function_docstring"
    temp = 0
    for i in range(0,N_bits):
        if (Hex_data >> i) & 1: temp |= 1 << (N_bits - 1 - i)
    return temp


###CCCCCCCCCCCCCCCC###     CLASS g_reg_settings BEGIN  ###CCCCCCCCCCCCCCCC######CCCCCCCCCCCCCCCC######CCCCCCCCCCCCCCCC######CCCCCCCCCCCCCCCC######CCCCCCCCCCCCCCCC###
class g_reg_settings: # purpose: organize the Global Configuration Register Settings in an array format which can be sent over Ethernet or optical link
   def __init__(self,
                TARGET_GEMROC_ID_param = 0, # acr 2017-09-22
                cfg_filename_param = "default_g_cfg_2018_all_big_endian.txt" # acr 2017-07-11
                ):
      self.TARGET_GEMROC_ID = TARGET_GEMROC_ID_param # acr 2017-09-22
      self.cfg_filename = cfg_filename_param
      ## acr 2017-07-12 BEGIN implementing a parameter array loaded from a configuration file
      self.parameter_array = [0 for i in range(37)] # acr 2018-01-25 [0 for i in range(38)]
      with open(self.cfg_filename, "r") as f:
         self.parameter_array = map(int, f)
      self.BufferBias = self.parameter_array [0] ## BufferBias_param; default 0
      self.TDCVcasN        = swap_order_N_bits(self.parameter_array [1],4)  # acr 2018-01-25 ## TDCVcasN_param; default 0
      self.TDCVcasP        = swap_order_N_bits(self.parameter_array [2],5)  # acr 2018-01-25 ## TDCVcasP_param; default 0
      self.TDCVcasPHyst    = swap_order_N_bits(self.parameter_array [3],6)  # acr 2018-01-25 ## TDCVcasPHyst_param; default 55
      self.DiscFE_Ibias    = swap_order_N_bits(self.parameter_array [4],6)  # acr 2018-01-25 ## DiscFE_Ibias_param; default 50

      self.BiasFE_PpreN = self.parameter_array [5] ## BiasFE_PpreN_param; default 10
      self.AVcasp_global   = swap_order_N_bits(self.parameter_array [6],5)  # acr 2018-01-25 ## AVcasp_global_param; default 20
      self.TDCcompVcas     = swap_order_N_bits(self.parameter_array [7],4)  # acr 2018-01-25 ## TDCcompVcas_param; default 0
      self.TDCIref_cs      = swap_order_N_bits(self.parameter_array [8],5)  # acr 2018-01-25 ## TDCIref_cs_param; default 20
      self.DiscVcasN       = swap_order_N_bits(self.parameter_array [9],4)  # acr 2018-01-25 elf.parameter_array [9] ## DiscVcasN_param; default 7

      self.IntegVb1        = swap_order_N_bits(self.parameter_array [10],6) # acr 2018-01-25 ## IntegVb1_param; default 27
      self.BiasFE_A1 = self.parameter_array [11] ## BiasFE_A1_param; default 8
      self.Vcasp_Vth       = swap_order_N_bits(self.parameter_array [12],6) # acr 2018-01-25 ## Vcasp_Vth_param; default 55
      self.TAC_I_LSB = self.parameter_array [13] ## TAC_I_LSB_param; default 0
      self.TDCcompVbias = self.parameter_array [14] ## TDCcompVbias_param; default 0

      self.Vref_Integ      = swap_order_N_bits(self.parameter_array [15],6) # acr 2018-01-25 ## Vref_Integ_param; default 55
      self.IBiasTPcal      = swap_order_N_bits(self.parameter_array [16],5) # acr 2018-01-25 ## IBiasTPcal_param; default 29
      self.TP_Vcal         = swap_order_N_bits(self.parameter_array [17],5) # acr 2018-01-25 ## TP_Vcal_param; default 8
      self.ShaperIbias = self.parameter_array [18] ## ShaperIbias_param; default 0
      self.IPostamp        = swap_order_N_bits(self.parameter_array [19],5) # acr 2018-01-25 ## IPostamp_param; default 26

      self.TP_Vcal_ref     = swap_order_N_bits(self.parameter_array [20],5) # acr 2018-01-25 ## TP_Vcal_ref_param; default 23
      self.Vref_integ_diff = swap_order_N_bits(self.parameter_array [21],6) # acr 2018-01-25 ## Vref_integ_diff_param; default 39
      self.Sig_pol = self.parameter_array [22] ## Sig_pol_param; default p-type (1?)
      self.FE_TPEnable = self.parameter_array [23] ## FE_TPEnable_param; default X (1?)
      # acr 2018-01-25 removing unused parameter self.CompactDataFormat = self.parameter_array [24] ## CompactDataFormat_param; default EMPTY BOX (0?)

      self.DataClkDiv = self.parameter_array [24] # acr 2018-01-25 [25] ## DataClkDiv_param; default 0
      self.TACrefreshPeriod = self.parameter_array [25] # acr 2018-01-25 [26] ## TACrefreshPeriod_param; default 9
      self.TACrefreshEnable = self.parameter_array [26] # acr 2018-01-25 [27] ## TACrefreshEnable_param; default X (1?)
      self.CounterPeriod = self.parameter_array [27] # acr 2018-01-25 [28] ## CounterPeriod_param; default 6
      self.CounterEnable = self.parameter_array [28] # acr 2018-01-25 [29] ## CounterEnable_param; default EMPTYBOX (0?)

      self.StopRampEnable = self.parameter_array [29] # acr 2018-01-25 [30] ## StopRampEnable_param; default 0
      self.RClkEnable = self.parameter_array [30] # acr 2018-01-25 [31] ## RClkEnable_param; default 7
      self.TDCClkdiv = self.parameter_array [31] # acr 2018-01-25 [32] ## TDCClkdiv_param; default EMPTYBOX (0?)
      self.VetoMode = self.parameter_array [32] # acr 2018-01-25 [33] ## VetoMode_param; default 0
      self.Ch_DebugMode = self.parameter_array [33] # acr 2018-01-25 [34] ## Ch_DebugMode_param; default EMPTYBOX (0?)

      self.TxMode = self.parameter_array [34] # acr 2018-01-25 [35] ## TxMode_param; default 2
      self.TxDDR = self.parameter_array [35] # acr 2018-01-25 [36] ## TxDDR_param; default X (1?)
      self.TxLinks = self.parameter_array [36] # acr 2018-01-25 [37] ## TxLinks_param; default 2 links nel GUI di Torino; dovrebbe corrispondeere ad un codice 1 per 2 links

      #Created dictionary to better implement the field controll and saving on file
      Global_config_dict= {
          "BufferBias" : self.parameter_array[0], ## BufferBias_param; default 0
          "TDCVcasN" : self.parameter_array[1],  # acr 2018-01-25 ## TDCVcasN_param; default 0
          "TDCVcasP": self.parameter_array[2],  # acr 2018-01-25 ## TDCVcasP_param; default 0
          "TDCVcasPHyst": self.parameter_array[3],  # acr 2018-01-25 ## TDCVcasPHyst_param; default 55
          "DiscFE_Ibias": self.parameter_array[4],   # acr 2018-01-25 ## DiscFE_Ibias_param; default 50
          "BiasFE_PpreN": self.parameter_array[5],  ## BiasFE_PpreN_param; default 10
          "AVcasp_global": self.parameter_array[6],  # acr 2018-01-25 ## AVcasp_global_param; default 20
          "TDCcompVcas": self.parameter_array[7],  # acr 2018-01-25 ## TDCcompVcas_param; default 0
          "TDCIref_cs": self.parameter_array[8],  # acr 2018-01-25 ## TDCIref_cs_param; default 20
          "DiscVcasN": self.parameter_array[9],  # acr 2018-01-25 elf.parameter_array [9] ## DiscVcasN_param; default 7
          "IntegVb1": self.parameter_array[10],  # acr 2018-01-25 ## IntegVb1_param; default 27
          "BiasFE_A1": self.parameter_array[11],  ## BiasFE_A1_param; default 8
          "Vcasp_Vth": self.parameter_array[12],   # acr 2018-01-25 ## Vcasp_Vth_param; default 55
          "TAC_I_LSB": self.parameter_array[13],  ## TAC_I_LSB_param; default 0
          "TDCcompVbias": self.parameter_array[14],  ## TDCcompVbias_param; default 0
          "Vref_Integ": self.parameter_array[15],   # acr 2018-01-25 ## Vref_Integ_param; default 55
          "IBiasTPcal": self.parameter_array[16],   # acr 2018-01-25 ## IBiasTPcal_param; default 29
          "TP_Vcal": self.parameter_array[17],  # acr 2018-01-25 ## TP_Vcal_param; default 8
          "ShaperIbias": self.parameter_array[18],  ## ShaperIbias_param; default 0
          "IPostamp": self.parameter_array[19],  # acr 2018-01-25 ## IPostamp_param; default 26
          "TP_Vcal_ref": self.parameter_array[20],  # acr 2018-01-25 ## TP_Vcal_ref_param; default 23
          "Vref_integ_diff": self.parameter_array[21], # acr 2018-01-25 ## Vref_integ_diff_param; default 39
          "Sig_pol": self.parameter_array[22],  ## Sig_pol_param; default p-type (1?)
          "FE_TPEnable": self.parameter_array[23],  ## FE_TPEnable_param; default X (1?)
          "DataClkDiv": self.parameter_array[24],  # acr 2018-01-25 [25] ## DataClkDiv_param; default 0
          "TACrefreshPeriod": self.parameter_array[25],  # acr 2018-01-25 [26] ## TACrefreshPeriod_param; default 9
          "TACrefreshEnable": self.parameter_array[26],  # acr 2018-01-25 [27] ## TACrefreshEnable_param; default X (1?)
          "CounterPeriod": self.parameter_array[27],  # acr 2018-01-25 [28] ## CounterPeriod_param; default 6
          "CounterEnable": self.parameter_array[28],  # acr 2018-01-25 [29] ## CounterEnable_param; default EMPTYBOX (0?)
          "StopRampEnable": self.parameter_array[29],  # acr 2018-01-25 [30] ## StopRampEnable_param; default 0
          "RClkEnable": self.parameter_array[30],  # acr 2018-01-25 [31] ## RClkEnable_param; default 7
          "TDCClkdiv": self.parameter_array[31],  # acr 2018-01-25 [32] ## TDCClkdiv_param; default EMPTYBOX (0?)
          "VetoMode": self.parameter_array[32], # acr 2018-01-25 [33] ## VetoMode_param; default 0
          "Ch_DebugMode": self.parameter_array[33],  # acr 2018-01-25 [34] ## Ch_DebugMode_param; default EMPTYBOX (0?)
          "TxMode": self.parameter_array[34],  # acr 2018-01-25 [35] ## TxMode_param; default 2
          "TxDDR": self.parameter_array[35],  # acr 2018-01-25 [36] ## TxDDR_param; default X (1?)
          "TxLinks": self.parameter_array[36]  # acr 2018-01-25 [37] ## TxLinks_param; default 2 links nel GUI di Torino; dovrebbe corrispondeere ad un codice 1 per 2 links

      }
      self.Global_cfg_list=[]
      for T in range (0,8):
          self.Global_cfg_list.append(Global_config_dict.copy())

      ## acr 2017-07-12 END   implementing a parameter array loaded from a configuration file
      self.is_a_write = 0x1
      self.target_TIGER_ID = 0x1
      self.command_code = 0x9

    ## command codes as defined by Ricardo Bugalho's configurator: CMD_WRCHCFG 0x0; CMD_RDCHCFG = 0x1; CMD_WRGCFG = 0x8; CMD_RDGCFG = 0x9;
      header_tag = 0x8 << 28
      Global_cfg_cmd_ID = 0xF
      gcfg_cmd_tag = Global_cfg_cmd_ID << 24
      gcfg_cmd_word_count = 11
      self.cmd_header = header_tag + (self.TARGET_GEMROC_ID << 16) + gcfg_cmd_tag + gcfg_cmd_word_count
      self.cmd_word10 = ((self.BufferBias & 0x3) << 24) + ((self.TDCVcasN & 0xF) << 16) + ((self.TDCVcasP & 0x1F) << 8) + ((self.TDCVcasPHyst & 0x3F))
      self.cmd_word9 = ((self.DiscFE_Ibias & 0x3f) << 24) + ((self.BiasFE_PpreN & 0x3F) << 16) + ((self.AVcasp_global & 0x1F) << 8) + ((self.TDCcompVcas & 0xF))
      self.cmd_word8 = ((self.TDCIref_cs & 0x1f) << 24) + ((self.DiscVcasN & 0xF) << 16) + ((self.IntegVb1 & 0x3F) << 8) + ((self.BiasFE_A1 & 0xF))
      self.cmd_word7 = ((self.Vcasp_Vth & 0x3f) << 24) + ((self.TAC_I_LSB & 0x1F) << 16) + ((self.TDCcompVbias & 0x1F) << 8) + ((self.Vref_Integ & 0x3F))
      self.cmd_word6 = ((self.IBiasTPcal & 0x1f) << 24) + ((self.TP_Vcal & 0x1F) << 16) + ((self.ShaperIbias & 0xF) << 8) + ((self.IPostamp & 0x1F))
      self.cmd_word5 = ((self.TP_Vcal_ref & 0x1f) << 24) + ((self.Vref_integ_diff & 0x3F) << 16) + ((self.Sig_pol & 0x1) << 8) + ((self.FE_TPEnable & 0x1))
      # acr 2018-01-25 removing unused parameter self.cmd_word4 = ((self.CompactDataFormat & 0x1) << 24) + ((self.DataClkDiv & 0x3) << 16) + ((self.TACrefreshPeriod & 0xf) << 8) + ((self.TACrefreshEnable & 0x1))
      self.cmd_word4 =                                           ((self.DataClkDiv & 0x3) << 16) + ((self.TACrefreshPeriod & 0xf) << 8) + ((self.TACrefreshEnable & 0x1))
      self.cmd_word3 = ((self.CounterPeriod & 0x7) << 24) + ((self.CounterEnable & 0x1) << 16) + ((self.StopRampEnable & 0x3) << 8) + ((self.RClkEnable & 0x1F))
      self.cmd_word2 = ((self.TDCClkdiv & 0x1) << 24) + ((self.VetoMode & 0x3F) << 16) + ((self.Ch_DebugMode & 0x1) << 8) + ((self.TxMode & 0x3))
      self.cmd_word1 = ((self.TxDDR & 0x1) << 24) + ((self.TxLinks & 0x3) << 16)
      self.cmd_word0 = ((self.command_code & 0xF) << command_code_shift) + ((self.target_TIGER_ID & 0x7) << target_TIGER_ID_shift)

      self.command_words = [ self.cmd_header,
                             self.cmd_word10,
                             self.cmd_word9,
                             self.cmd_word8,
                             self.cmd_word7,
                             self.cmd_word6,
                             self.cmd_word5,
                             self.cmd_word4,
                             self.cmd_word3,
                             self.cmd_word2,
                             self.cmd_word1,
                             self.cmd_word0
                              ]

   def __del__(self):
      class_name = self.__class__.__name__
      #print class_name, "g_reg_settings destroyed"

   def reload_gcfg_settings_from_file(self, GCFGReg_def_fname_param): ## acr 2018-02-23 new method to reaload from a default file
      self.parameter_array = [0 for i in range(37)] # acr 2018-01-25 [0 for i in range(38)]
      with open(GCFGReg_def_fname_param, "r") as f:
         self.parameter_array = map(int, f)
         f.close()
      self.BufferBias = self.parameter_array [0] ## BufferBias_param; default 0
      self.TDCVcasN        = swap_order_N_bits(self.parameter_array [1],4)  # acr 2018-01-25 ## TDCVcasN_param; default 0
      self.TDCVcasP        = swap_order_N_bits(self.parameter_array [2],5)  # acr 2018-01-25 ## TDCVcasP_param; default 0
      self.TDCVcasPHyst    = swap_order_N_bits(self.parameter_array [3],6)  # acr 2018-01-25 ## TDCVcasPHyst_param; default 55
      self.DiscFE_Ibias    = swap_order_N_bits(self.parameter_array [4],6)  # acr 2018-01-25 ## DiscFE_Ibias_param; default 50
      self.BiasFE_PpreN    = self.parameter_array [5] ## BiasFE_PpreN_param; default 10
      self.AVcasp_global   = swap_order_N_bits(self.parameter_array [6],5)  # acr 2018-01-25 ## AVcasp_global_param; default 20
      self.TDCcompVcas     = swap_order_N_bits(self.parameter_array [7],4)  # acr 2018-01-25 ## TDCcompVcas_param; default 0
      self.TDCIref_cs      = swap_order_N_bits(self.parameter_array [8],5)  # acr 2018-01-25 ## TDCIref_cs_param; default 20
      self.DiscVcasN       = swap_order_N_bits(self.parameter_array [9],4)  # acr 2018-01-25 elf.parameter_array [9] ## DiscVcasN_param; default 7
      self.IntegVb1        = swap_order_N_bits(self.parameter_array [10],6) # acr 2018-01-25 ## IntegVb1_param; default 27
      self.BiasFE_A1 = self.parameter_array [11] ## BiasFE_A1_param; default 8
      self.Vcasp_Vth       = swap_order_N_bits(self.parameter_array [12],6) # acr 2018-01-25 ## Vcasp_Vth_param; default 55
      self.TAC_I_LSB = self.parameter_array [13] ## TAC_I_LSB_param; default 0
      self.TDCcompVbias = self.parameter_array [14] ## TDCcompVbias_param; default 0
      self.Vref_Integ      = swap_order_N_bits(self.parameter_array [15],6) # acr 2018-01-25 ## Vref_Integ_param; default 55
      self.IBiasTPcal      = swap_order_N_bits(self.parameter_array [16],5) # acr 2018-01-25 ## IBiasTPcal_param; default 29
      self.TP_Vcal         = swap_order_N_bits(self.parameter_array [17],5) # acr 2018-01-25 ## TP_Vcal_param; default 8
      self.ShaperIbias = self.parameter_array [18] ## ShaperIbias_param; default 0
      self.IPostamp        = swap_order_N_bits(self.parameter_array [19],5) # acr 2018-01-25 ## IPostamp_param; default 26
      self.TP_Vcal_ref     = swap_order_N_bits(self.parameter_array [20],5) # acr 2018-01-25 ## TP_Vcal_ref_param; default 23
      self.Vref_integ_diff = swap_order_N_bits(self.parameter_array [21],6) # acr 2018-01-25 ## Vref_integ_diff_param; default 39
      self.Sig_pol = self.parameter_array [22] ## Sig_pol_param; default p-type (1?)
      self.FE_TPEnable = self.parameter_array [23] ## FE_TPEnable_param; default X (1?)
      # acr 2018-01-25 removing unused parameter self.CompactDataFormat = self.parameter_array [24] ## CompactDataFormat_param; default EMPTY BOX (0?)
      self.DataClkDiv = self.parameter_array [24] # acr 2018-01-25 [25] ## DataClkDiv_param; default 0
      self.TACrefreshPeriod = self.parameter_array [25] # acr 2018-01-25 [26] ## TACrefreshPeriod_param; default 9
      self.TACrefreshEnable = self.parameter_array [26] # acr 2018-01-25 [27] ## TACrefreshEnable_param; default X (1?)
      self.CounterPeriod = self.parameter_array [27] # acr 2018-01-25 [28] ## CounterPeriod_param; default 6
      self.CounterEnable = self.parameter_array [28] # acr 2018-01-25 [29] ## CounterEnable_param; default EMPTYBOX (0?)
      self.StopRampEnable = self.parameter_array [29] # acr 2018-01-25 [30] ## StopRampEnable_param; default 0
      self.RClkEnable = self.parameter_array [30] # acr 2018-01-25 [31] ## RClkEnable_param; default 7
      self.TDCClkdiv = self.parameter_array [31] # acr 2018-01-25 [32] ## TDCClkdiv_param; default EMPTYBOX (0?)
      self.VetoMode = self.parameter_array [32] # acr 2018-01-25 [33] ## VetoMode_param; default 0
      self.Ch_DebugMode = self.parameter_array [33] # acr 2018-01-25 [34] ## Ch_DebugMode_param; default EMPTYBOX (0?)
      self.TxMode = self.parameter_array [34] # acr 2018-01-25 [35] ## TxMode_param; default 2
      self.TxDDR = self.parameter_array [35] # acr 2018-01-25 [36] ## TxDDR_param; default X (1?)
      self.TxLinks = self.parameter_array [36] # acr 2018-01-25 [37] ## TxLinks_param; default 2 links nel GUI di Torino; dovrebbe corrispondeere ad un codice 1 per 2 links

   def cmd_words_array_size(self):
      return len(self.command_words)

   def print_command_words(self):
      for i in range (0, len(self.command_words)):
         print '%08X'% self.command_words[i]

   def set_target_GEMROC(self, GEMROC_ID_param): # acr 2017-09-22
      self.TARGET_GEMROC_ID = GEMROC_ID_param & 0x1f
      self.cmd_header = (self.cmd_header & 0xFF00FFFF) + (self.TARGET_GEMROC_ID << 16)

   def set_target_TIGER(self, target_TIGER_param):
      self.target_TIGER_ID = target_TIGER_param & 0x7
      self.cmd_word0 = ((self.command_code & 0xF) << command_code_shift) + ((self.target_TIGER_ID & 0x7) << target_TIGER_ID_shift)
      self.command_words[11] = self.cmd_word0

   def set_FE_TPEnable(self, FE_TPEnable_param):
      self.FE_TPEnable = FE_TPEnable_param & 0x1

   def set_AVcasp_global(self, AVcasp_global_param):
      self.AVcasp_global = AVcasp_global_param & 0x1F

   def set_command_code(self, command_code_param):
      if (command_code_param == 'WR'):
         self.command_code = 0x8
         self.is_a_write = 1
         self.cmd_word0 = ((self.command_code & 0xF) << command_code_shift) + ((self.target_TIGER_ID & 0x7) << target_TIGER_ID_shift)
         self.command_words[11] = self.cmd_word0
      elif (command_code_param == 'RD'):
         self.command_code = 0x9
         self.is_a_write = 0
         self.cmd_word0 = ((self.command_code & 0xF) << command_code_shift) + ((self.target_TIGER_ID & 0x7) << target_TIGER_ID_shift)
         self.command_words[11] = self.cmd_word0


   def update_command_words(self):
      if ( (self.command_code & 0xF) == 0x9 ):
         self.cmd_word10 = 0
         self.cmd_word9  = 0
         self.cmd_word8  = 0
         self.cmd_word7  = 0
         self.cmd_word6  = 0
         self.cmd_word5  = 0
         self.cmd_word4  = 0
         self.cmd_word3  = 0
         self.cmd_word2  = 0
         self.cmd_word1  = 0
      else :
          BufferBias = self.Global_cfg_list[self.target_TIGER_ID]["BufferBias"] & 0x3  ## BufferBias_param; default 0
          TDCVcasN = swap_order_N_bits(self.Global_cfg_list[self.target_TIGER_ID]["TDCVcasN"] , 4) & 0xF  # acr 2018-01-25 ## TDCVcasN_param; default 0
          TDCVcasP = swap_order_N_bits(self.Global_cfg_list[self.target_TIGER_ID]["TDCVcasP"] , 5) & 0x1F  # acr 2018-01-25 ## TDCVcasP_param; default 0
          TDCVcasPHyst = swap_order_N_bits(self.Global_cfg_list[self.target_TIGER_ID]["TDCVcasPHyst"] , 6) & 0x3F # acr 2018-01-25 ## TDCVcasPHyst_param; default 55
          DiscFE_Ibias = swap_order_N_bits(self.Global_cfg_list[self.target_TIGER_ID]["DiscFE_Ibias"] , 6) & 0x3F  # acr 2018-01-25 ## DiscFE_Ibias_param; default 50
          BiasFE_PpreN = self.Global_cfg_list[self.target_TIGER_ID]["BiasFE_PpreN"]  & 0x3F  ## BiasFE_PpreN_param; default 10
          AVcasp_global = swap_order_N_bits(self.Global_cfg_list[self.target_TIGER_ID]["AVcasp_global"],5)  & 0x1F  # acr 2018-01-25 ## AVcasp_global_param; default 20
          TDCcompVcas = swap_order_N_bits(self.Global_cfg_list[self.target_TIGER_ID]["TDCcompVcas"], 4) & 0xF  # acr 2018-01-25 ## TDCcompVcas_param; default 0
          TDCIref_cs = swap_order_N_bits(self.Global_cfg_list[self.target_TIGER_ID]["TDCIref_cs"], 5)  & 0x1f # acr 2018-01-25 ## TDCIref_cs_param; default 20
          DiscVcasN = swap_order_N_bits(self.Global_cfg_list[self.target_TIGER_ID]["DiscVcasN"], 4) & 0xF  # acr 2018-01-25 elf.parameter_array [9] ## DiscVcasN_param; default 7
          IntegVb1 = swap_order_N_bits(self.Global_cfg_list[self.target_TIGER_ID]["IntegVb1"], 6) & 0x3F  # acr 2018-01-25 ## IntegVb1_param; default 27
          BiasFE_A1 = self.Global_cfg_list[self.target_TIGER_ID]["BiasFE_A1"] & 0xF  ## BiasFE_A1_param; default 8
          Vcasp_Vth = swap_order_N_bits(self.Global_cfg_list[self.target_TIGER_ID]["Vcasp_Vth"], 6) & 0x3F   # acr 2018-01-25 ## Vcasp_Vth_param; default 55
          TAC_I_LSB = self.Global_cfg_list[self.target_TIGER_ID]["TAC_I_LSB"] & 0x1F   ## TAC_I_LSB_param; default 0
          TDCcompVbias = self.Global_cfg_list[self.target_TIGER_ID]["TAC_I_LSB"] & 0x1F  ## TDCcompVbias_param; default 0
          Vref_Integ = swap_order_N_bits(self.Global_cfg_list[self.target_TIGER_ID]["Vref_Integ"] , 6)& 0x3F   # acr 2018-01-25 ## Vref_Integ_param; default 55
          IBiasTPcal = swap_order_N_bits(self.Global_cfg_list[self.target_TIGER_ID]["IBiasTPcal"] , 5) & 0x1f  # acr 2018-01-25 ## IBiasTPcal_param; default 29
          TP_Vcal = swap_order_N_bits(self.Global_cfg_list[self.target_TIGER_ID]["TP_Vcal"] , 5)& 0x1F   # acr 2018-01-25 ## TP_Vcal_param; default 8
          ShaperIbias = self.Global_cfg_list[self.target_TIGER_ID]["ShaperIbias"]& 0xF   ## ShaperIbias_param; default 0
          IPostamp = swap_order_N_bits(self.Global_cfg_list[self.target_TIGER_ID]["IPostamp"], 5)& 0x1F   # acr 2018-01-25 ## IPostamp_param; default 26
          TP_Vcal_ref = swap_order_N_bits(self.Global_cfg_list[self.target_TIGER_ID]["TP_Vcal_ref"], 5)& 0x1F   # acr 2018-01-25 ## TP_Vcal_ref_param; default 23
          Vref_integ_diff = swap_order_N_bits(self.Global_cfg_list[self.target_TIGER_ID]["Vref_integ_diff"], 6)& 0x3F   # acr 2018-01-25 ## Vref_integ_diff_param; default 39
          Sig_pol = self.Global_cfg_list[self.target_TIGER_ID]["Sig_pol"] & 0x1   ## Sig_pol_param; default p-type (1?)
          FE_TPEnable = self.Global_cfg_list[self.target_TIGER_ID]["FE_TPEnable"] & 0x1   ## FE_TPEnable_param; default X (1?)
          DataClkDiv = self.Global_cfg_list[self.target_TIGER_ID]["DataClkDiv"] & 0x3  # acr 2018-01-25 [25] ## DataClkDiv_param; default 0
          TACrefreshPeriod = self.Global_cfg_list[self.target_TIGER_ID]["TACrefreshPeriod"]& 0xF   # acr 2018-01-25 [26] ## TACrefreshPeriod_param; default 9
          TACrefreshEnable = self.Global_cfg_list[self.target_TIGER_ID]["TACrefreshEnable"] & 0x1  # acr 2018-01-25 [27] ## TACrefreshEnable_param; default X (1?)
          CounterPeriod = self.Global_cfg_list[self.target_TIGER_ID]["CounterPeriod"] & 0x7  # acr 2018-01-25 [28] ## CounterPeriod_param; default 6
          CounterEnable = self.Global_cfg_list[self.target_TIGER_ID]["CounterEnable"]  & 0x1 # acr 2018-01-25 [29] ## CounterEnable_param; default EMPTYBOX (0?)
          StopRampEnable = self.Global_cfg_list[self.target_TIGER_ID]["StopRampEnable"]& 0x3   # acr 2018-01-25 [30] ## StopRampEnable_param; default 0
          RClkEnable = self.Global_cfg_list[self.target_TIGER_ID]["RClkEnable"]& 0x1F   # acr 2018-01-25 [31] ## RClkEnable_param; default 7
          TDCClkdiv =self.Global_cfg_list[self.target_TIGER_ID]["TDCClkdiv"]& 0x1   # acr 2018-01-25 [32] ## TDCClkdiv_param; default EMPTYBOX (0?)
          VetoMode = self.Global_cfg_list[self.target_TIGER_ID]["VetoMode"]& 0x3F   # acr 2018-01-25 [33] ## VetoMode_param; default 0
          Ch_DebugMode = self.Global_cfg_list[self.target_TIGER_ID]["Ch_DebugMode"] & 0x1  # acr 2018-01-25 [34] ## Ch_DebugMode_param; default EMPTYBOX (0?)
          TxMode = self.Global_cfg_list[self.target_TIGER_ID]["TxMode"] & 0x3  # acr 2018-01-25 [35] ## TxMode_param; default 2
          TxDDR = self.Global_cfg_list[self.target_TIGER_ID]["TxDDR"] & 0x1  # =cr 2018-01-25 [36] ## TxDDR_param; default X (1?)
          TxLinks = self.Global_cfg_list[self.target_TIGER_ID]["TxLinks"] & 0x3   # acr 2018-01-25 [37] ## TxLinks_param; default 2 links nel GUI di Torino; dovrebbe corrispondeere ad un codice 1 per 2 links

          self.cmd_word10 = (BufferBias << 24) + ( TDCVcasN << 16)  + (TDCVcasP << 8)  + TDCVcasPHyst
          self.cmd_word9 =  (DiscFE_Ibias  << 24)     + (BiasFE_PpreN  << 16)    + ( AVcasp_global << 8)   + TDCcompVcas
          self.cmd_word8 =  (TDCIref_cs  << 24)          + (DiscVcasN  << 16)        + (IntegVb1  << 8)        + (BiasFE_A1 )
          self.cmd_word7 =  (Vcasp_Vth  << 24)        + (TAC_I_LSB  << 16)       + (TDCcompVbias  << 8)    + (Vref_Integ )
          self.cmd_word6 =  (IBiasTPcal  << 24)       + (TP_Vcal  << 16)         + (ShaperIbias  << 8)      + (IPostamp )
          self.cmd_word5 =  (TP_Vcal_ref  << 24)      + (Vref_integ_diff  << 16) + (Sig_pol  << 8)          + (FE_TPEnable )
          # acr 2018-01-25 removing unused parameter self.cmd_word4 = ((self.CompactDataFormat & 0x1) << 24) + ((self.DataClkDiv & 0x3) << 16) + ((self.TACrefreshPeriod & 0xf) << 8) + ((self.TACrefreshEnable & 0x1))
          self.cmd_word4 =                                           (DataClkDiv  << 16) + (TACrefreshPeriod  << 8) + (TACrefreshEnable )
          self.cmd_word3 =  (CounterPeriod << 24)     + (CounterEnable  << 16)    + (StopRampEnable  << 8)   + (RClkEnable )
          self.cmd_word2 =  (TDCClkdiv  << 24)         + (VetoMode  << 16)        + (Ch_DebugMode << 8)     + (TxMode )
          self.cmd_word1 =  (TxDDR  << 24)             + (TxLinks  << 16)
      self.cmd_word0 = ((self.command_code & 0xF) << command_code_shift) + ((self.target_TIGER_ID & 0x7) << target_TIGER_ID_shift)
      self.command_words = [ self.cmd_header,
                             self.cmd_word10,
                             self.cmd_word9,
                             self.cmd_word8,
                             self.cmd_word7,
                             self.cmd_word6,
                             self.cmd_word5,
                             self.cmd_word4,
                             self.cmd_word3,
                             self.cmd_word2,
                             self.cmd_word1,
                             self.cmd_word0
                              ]

   # def update_command_words(self):
   #    if ( (self.command_code & 0xF) == 0x9 ):
   #       self.cmd_word10 = 0
   #       self.cmd_word9  = 0
   #       self.cmd_word8  = 0
   #       self.cmd_word7  = 0
   #       self.cmd_word6  = 0
   #       self.cmd_word5  = 0
   #       self.cmd_word4  = 0
   #       self.cmd_word3  = 0
   #       self.cmd_word2  = 0
   #       self.cmd_word1  = 0
   #    else :
   #       self.cmd_word10 = ((self.BufferBias & 0x3) << 24)        + ((self.TDCVcasN & 0xF) << 16)         + ((self.TDCVcasP & 0x1F) << 8)        + ((self.TDCVcasPHyst & 0x3F))
   #       self.cmd_word9 =  ((self.DiscFE_Ibias & 0x3f) << 24)     + ((self.BiasFE_PpreN & 0x3F) << 16)    + ((self.AVcasp_global & 0x1F) << 8)   + ((self.TDCcompVcas & 0xF))
   #       self.cmd_word8 =  ((self.TDCIref_cs & 0x1f) << 24)          + ((self.DiscVcasN & 0xF) << 16)        + ((self.IntegVb1 & 0x3F) << 8)        + ((self.BiasFE_A1 & 0xF))
   #       self.cmd_word7 =  ((self.Vcasp_Vth & 0x3f) << 24)        + ((self.TAC_I_LSB & 0x1F) << 16)       + ((self.TDCcompVbias & 0x1F) << 8)    + ((self.Vref_Integ & 0x3F))
   #       self.cmd_word6 =  ((self.IBiasTPcal & 0x1f) << 24)       + ((self.TP_Vcal & 0x1F) << 16)         + ((self.ShaperIbias & 0xF) << 8)      + ((self.IPostamp & 0x1F))
   #       self.cmd_word5 =  ((self.TP_Vcal_ref & 0x1f) << 24)      + ((self.Vref_integ_diff & 0x3F) << 16) + ((self.Sig_pol & 0x1) << 8)          + ((self.FE_TPEnable & 0x1))
   #       # acr 2018-01-25 removing unused parameter self.cmd_word4 = ((self.CompactDataFormat & 0x1) << 24) + ((self.DataClkDiv & 0x3) << 16) + ((self.TACrefreshPeriod & 0xf) << 8) + ((self.TACrefreshEnable & 0x1))
   #       self.cmd_word4 =                                           ((self.DataClkDiv & 0x3) << 16) + ((self.TACrefreshPeriod & 0xf) << 8) + ((self.TACrefreshEnable & 0x1))
   #       self.cmd_word3 =  ((self.CounterPeriod & 0x7) << 24)     + ((self.CounterEnable & 0x1) << 16)    + ((self.StopRampEnable & 0x3) << 8)   + ((self.RClkEnable & 0x1F))
   #       self.cmd_word2 =  ((self.TDCClkdiv & 0x1) << 24)         + ((self.VetoMode & 0x3F) << 16)        + ((self.Ch_DebugMode & 0x1) << 8)     + ((self.TxMode & 0x3))
   #       self.cmd_word1 =  ((self.TxDDR & 0x1) << 24)             + ((self.TxLinks & 0x3) << 16)
   #    self.cmd_word0 = ((self.command_code & 0xF) << command_code_shift) + ((self.target_TIGER_ID & 0x7) << target_TIGER_ID_shift)
   #    self.command_words = [ self.cmd_header,
   #                           self.cmd_word10,
   #                           self.cmd_word9,
   #                           self.cmd_word8,
   #                           self.cmd_word7,
   #                           self.cmd_word6,
   #                           self.cmd_word5,
   #                           self.cmd_word4,
   #                           self.cmd_word3,
   #                           self.cmd_word2,
   #                           self.cmd_word1,
   #                           self.cmd_word0
   #                            ]
## acr 2018-01-29 BEGIN must take into account the different endianness for different fields
   def extract_parameters_from_UDP_packet(self):
      print'\nList of parameters sent to TIGER%d:'%self.target_TIGER_ID
      print ( "\nBufferBias:%02X;\t\tTDCVcasN:%02X;\t\tTDCVcasP:%02X;\t\tTDCVcasPHyst:%02X;" %( ((self.cmd_word10>>24)&0x3), swap_order_N_bits(((self.cmd_word10>>16)&0xF),4), swap_order_N_bits(((self.cmd_word10>>8)&0x1F),5), swap_order_N_bits(((self.cmd_word10>>0)&0x3F),6) ) )
      print ( "\nDiscFE_Ibias:%02X;\tBiasFE_PpreN:%02X;\tAVcasp_global:%02X;\tTDCcompVcas:%02X;" %( swap_order_N_bits(((self.cmd_word9>>24)&0x3F),6), ((self.cmd_word9>>16)&0x3F), swap_order_N_bits(((self.cmd_word9>>8)&0x1F),5), swap_order_N_bits(((self.cmd_word9>>0)&0xF),4) ) )
      print ( "\nTDCIref_cs:%02X;\t\tDiscVcasN:%02X;\t\tIntegVb1:%02X;\t\tBiasFE_A1:%02X;" %( swap_order_N_bits(((self.cmd_word8>>24)&0x1F),5), swap_order_N_bits(((self.cmd_word8>>16)&0xF),4), swap_order_N_bits(((self.cmd_word8>>8)&0x3F),6), ((self.cmd_word8>>0)&0xF) ) )
      print ( "\nVcasp_Vth:%02X;\t\tTAC_I_LSB:%02X;\t\tTDCcompVbias:%02X;\tVref_Integ:%02X;" %( swap_order_N_bits(((self.cmd_word7>>24)&0x3F),6), ((self.cmd_word7>>16)&0x1F), ((self.cmd_word7>>8)&0x1F), swap_order_N_bits(((self.cmd_word7>>0)&0x3F),6) ) )
      print ( "\nIBiasTPcal:%02X;\t\tTP_Vcal:%02X;\t\tShaperIbias:%02X;\t\tIPostamp:%02X;" %( swap_order_N_bits(((self.cmd_word6>>24)&0x1F),5), swap_order_N_bits(((self.cmd_word6>>16)&0x1F),5), ((self.cmd_word6>>8)&0xF), swap_order_N_bits(((self.cmd_word6>>0)&0x1F),5) ) )
      print ( "\nTP_Vcal_ref:%02X;\t\tVref_integ_diff:%02X;\tSig_pol:%02X;\t\tFE_TPEnable:%02X;" %( swap_order_N_bits(((self.cmd_word5>>24)&0x1F),5), swap_order_N_bits(((self.cmd_word5>>16)&0x3F),6), ((self.cmd_word5>>8)&0x1), ((self.cmd_word5>>0)&0x1) ) )
      #acr 2018-01-25 print ( "\nCompactDataFormat:%02X;\tDataClkDiv:%02X;\t\tTACrefreshPeriod:%02X;\tTACrefreshEnable:%02X;" %( ((self.cmd_word4>>24)&0x1), ((self.cmd_word4>>16)&0x3), ((self.cmd_word4>>8)&0xF), ((self.cmd_word4>>0)&0x1) ) )
      print ( "\nDataClkDiv:%02X;\t\tTACrefreshPeriod:%02X;\tTACrefreshEnable:%02X;" %( ((self.cmd_word4>>16)&0x3), ((self.cmd_word4>>8)&0xF), ((self.cmd_word4>>0)&0x1) ) )
      print ( "\nCounterPeriod:%02X;\tCounterEnable:%02X;\tStopRampEnable:%02X;\tRClkEnable:%02X;" %( ((self.cmd_word3>>24)&0x7), ((self.cmd_word3>>16)&0x1), ((self.cmd_word3>>8)&0x3), ((self.cmd_word3>>0)&0x1F) ) )
      print ( "\nTDCClkdiv:%02X;\t\tVetoMode:%02X;\t\tCh_DebugMode:%02X;\tTxMode:%02X;" %( ((self.cmd_word2>>24)&0x1), ((self.cmd_word2>>16)&0x3F), ((self.cmd_word2>>8)&0x1 ), ((self.cmd_word2>>0)&0x3) ) )
      print ( "\nTxDDR:%02X;\t\tTxLinks:%02X;" %( ((self.cmd_word1>>24)&0x1), ((self.cmd_word1>>16)&0x3) ) )
   def extract_d_parameters_from_UDP_packet(self):
      print'\nList of parameters sent to TIGER%d:'%self.target_TIGER_ID
      print ( "\nBufferBias:%d;\t\tTDCVcasN:%d;\t\tTDCVcasP:%d;\t\tTDCVcasPHyst:%d;" %( ((self.cmd_word10>>24)&0x3), swap_order_N_bits(((self.cmd_word10>>16)&0xF),4), swap_order_N_bits(((self.cmd_word10>>8)&0x1F),5), swap_order_N_bits(((self.cmd_word10>>0)&0x3F),6) ) )
      print ( "\nDiscFE_Ibias:%d;\tBiasFE_PpreN:%d;\tAVcasp_global:%d;\tTDCcompVcas:%d;" %( swap_order_N_bits(((self.cmd_word9>>24)&0x3F),6), ((self.cmd_word9>>16)&0x3F), swap_order_N_bits(((self.cmd_word9>>8)&0x1F),5), swap_order_N_bits(((self.cmd_word9>>0)&0xF),4) ) )
      print ( "\nTDCIref_cs:%d;\t\tDiscVcasN:%d;\t\tIntegVb1:%d;\t\tBiasFE_A1:%d;" %( swap_order_N_bits(((self.cmd_word8>>24)&0x1F),5), swap_order_N_bits(((self.cmd_word8>>16)&0xF),4), swap_order_N_bits(((self.cmd_word8>>8)&0x3F),6), ((self.cmd_word8>>0)&0xF) ) )
      print ( "\nVcasp_Vth:%d;\t\tTAC_I_LSB:%d;\t\tTDCcompVbias:%d;\tVref_Integ:%d;" %( swap_order_N_bits(((self.cmd_word7>>24)&0x3F),6), ((self.cmd_word7>>16)&0x1F), ((self.cmd_word7>>8)&0x1F), swap_order_N_bits(((self.cmd_word7>>0)&0x3F),6) ) )
      print ( "\nIBiasTPcal:%d;\t\tTP_Vcal:%d;\t\tShaperIbias:%d;\t\tIPostamp:%d;" %( swap_order_N_bits(((self.cmd_word6>>24)&0x1F),5), swap_order_N_bits(((self.cmd_word6>>16)&0x1F),5), ((self.cmd_word6>>8)&0xF), swap_order_N_bits(((self.cmd_word6>>0)&0x1F),5) ) )
      print ( "\nTP_Vcal_ref:%d;\t\tVref_integ_diff:%d;\tSig_pol:%d;\t\tFE_TPEnable:%d;" %( swap_order_N_bits(((self.cmd_word5>>24)&0x1F),5), swap_order_N_bits(((self.cmd_word5>>16)&0x3F),6), ((self.cmd_word5>>8)&0x1), ((self.cmd_word5>>0)&0x1) ) )
      print ( "\nDataClkDiv:%d;\t\tTACrefreshPeriod:%d;\tTACrefreshEnable:%d;" %( ((self.cmd_word4>>16)&0x3), ((self.cmd_word4>>8)&0xF), ((self.cmd_word4>>0)&0x1) ) )
      print ( "\nCounterPeriod:%d;\tCounterEnable:%d;\tStopRampEnable:%d;\tRClkEnable:%d;" %( ((self.cmd_word3>>24)&0x7), ((self.cmd_word3>>16)&0x1), ((self.cmd_word3>>8)&0x3), ((self.cmd_word3>>0)&0x1F) ) )
      print ( "\nTDCClkdiv:%d;\t\tVetoMode:%d;\t\tCh_DebugMode:%d;\tTxMode:%d;" %( ((self.cmd_word2>>24)&0x1), ((self.cmd_word2>>16)&0x3F), ((self.cmd_word2>>8)&0x1 ), ((self.cmd_word2>>0)&0x3) ) )
      print ( "\nTxDDR:%d;\t\tTxLinks:%d;" %( ((self.cmd_word1>>24)&0x1), ((self.cmd_word1>>16)&0x3) ) )
## acr 2018-01-29 END  must take into account the different endianness for different fields
   def save_glob_conf(self,filename):
        with  open(filename,'wb') as f:
            pickle.dump(self.Global_cfg_list,f)
        return 0
   def load_glob_conf(self,filename):
        with  open(filename,'rb') as f:
            self.Global_cfg_list=pickle.load(f)
        print self.Global_cfg_list
        return 0

   def load_TP_cal(self,config_dict, TP_amplitude= "low"):
       for T in range(0,8):
           if config_dict[self.TARGET_GEMROC_ID][T]["TP_Vcal_ref"] != 'NA':
               self.Global_cfg_list[T]["TP_Vcal_ref"] = config_dict[self.TARGET_GEMROC_ID][T]["TP_Vcal_ref"]
               self.Global_cfg_list[T]["TP_Vcal"] = config_dict[self.TARGET_GEMROC_ID][T]["TP_Vcal"]
               self.Global_cfg_list[T]["IBiasTPcal"] = config_dict[self.TARGET_GEMROC_ID][T]["Ibias_TP_cal_diff"]
               if TP_amplitude == "low":
                   self.Global_cfg_list[T]["TP_Vcal_ref"] = config_dict[self.TARGET_GEMROC_ID][T]["start"]+self.search_for_Q( config_dict[self.TARGET_GEMROC_ID][T],7)
               if TP_amplitude == "high":
                   self.Global_cfg_list[T]["TP_Vcal_ref"] = config_dict[self.TARGET_GEMROC_ID][T]["start"]+self.search_for_Q( config_dict[self.TARGET_GEMROC_ID][T],20)
           else:
               if TP_amplitude == "low":
                   self.Global_cfg_list[T]["TP_Vcal_ref"] = 4
               if TP_amplitude == "high":
                   self.Global_cfg_list[T]["TP_Vcal_ref"] = 13

   def search_for_Q(self,conf_dict, Q):
       if conf_dict["TP_calib"] != 'NA':
           distance = 1000
           for key in conf_dict["TP_calib"]:
               new_dist = abs((conf_dict["TP_calib"][key]['Q']) - Q)
               if new_dist > distance:
                   print (distance)
                   return key - 1
               distance = new_dist
       else:
           return 2
###CCCCCCCCCCCCCCCC###     CLASS ch_reg_settings BEGIN  ###CCCCCCCCCCCCCCCC######CCCCCCCCCCCCCCCC######CCCCCCCCCCCCCCCC######CCCCCCCCCCCCCCCC######CCCCCCCCCCCCCCCC###
class ch_reg_settings: # purpose: organize the Channel Configuration Register Settings in an array format which can be sent over Ethernet or optical link
   def __init__(self,
                TARGET_GEMROC_ID_param = 0, # acr 2017-09-22
                cfg_filename_param = "default_ch_cfg_mainz.txt" # acr 2017-11-16
                ):
      self.TARGET_GEMROC_ID = TARGET_GEMROC_ID_param # acr 2017-09-22
      self.cfg_filename = cfg_filename_param
      ## acr 2017-07-12 BEGIN implementing a parameter array loaded from a configuration file
      self.parameter_array = [0 for i in range(30)]
      with open(self.cfg_filename, "r") as f:
         self.parameter_array = map(int, f)
      self.DisableHyst = self.parameter_array [0]  ## DisableHyst_param
      self.T2Hyst = self.parameter_array [1]  ## T2Hyst_param
      self.T1Hyst = self.parameter_array [2]  ## T1Hyst_param
      self.Ch63ObufMSB = self.parameter_array [3]  ## Ch63ObufMSB_param
      self.TP_disable_FE = self.parameter_array [4]  ## TP_disable_FE_param
      self.TDC_IB_E = self.parameter_array [5]  ## TDC_IB_E_param
      self.TDC_IB_T = self.parameter_array [6]  ## TDC_IB_T_param
      self.Integ = self.parameter_array [7]  ## Integ_param
      self.PostAmpGain = self.parameter_array [8]  ## PostAmpGain_param
      self.FE_delay = self.parameter_array [9]  ## FE_delay_param
      self.Vth_T2 = self.parameter_array [10]  ## Vth_T2_param
      self.Vth_T1 = self.parameter_array [11]  ## Vth_T1_param
      self.QTx2Enable = self.parameter_array [12]  ## QTx2Enable_param
      self.MaxIntegTime = self.parameter_array [13]  ## MaxIntegTime_param
      self.MinIntegTime = self.parameter_array [14]  ## MinIntegTime_param
      self.TriggerBLatched = self.parameter_array [15]  ## TriggerBLatched_param
      self.QdcMode = self.parameter_array [16]  ## QdcMode_param
      self.BranchEnableT = self.parameter_array [17]  ## BranchEnableT_param
      self.BranchEnableEQ = self.parameter_array [18]  ## BranchEnableEQ_param
      self.TriggerMode2B = self.parameter_array [19]  ## TriggerMode2B_param
      self.TriggerMode2Q = self.parameter_array [20]  ## TriggerMode2Q_param
      self.TriggerMode2E = self.parameter_array [21]  ## TriggerMode2E_param
      self.TriggerMode2T = self.parameter_array [22]  ## TriggerMode2T_param
      self.TACMinAge = self.parameter_array [23]  ## TACMinAge_param
      self.TACMaxAge = self.parameter_array [24]  ## TACMaxAge_param
      self.CounterMode = self.parameter_array [25]  ## CounterMode_param
      self.DeadTime = self.parameter_array [26]  ## DeadTime_param
      self.SyncChainLen = self.parameter_array [27]  ## SyncChainLen_param
      self.Ch_DebugMode = self.parameter_array [28]  ## Ch_DebugMode_param
      self.TriggerMode = self.parameter_array [29]  ## TriggerMode_param
      ## acr 2017-07-12 END   implementing a parameter array loaded from a configuration file

      sav_channel_dic={
      "TP_disable_FE": self.parameter_array [4],  ## TP_disable_FE_param
      "Integ": self.parameter_array [7],  ## Integ_param
      "Vth_T2": self.parameter_array [10],  ## Vth_T2_param
      "Vth_T1": self.parameter_array [11],  ## Vth_T1_param
      "TriggerBLatched": self.parameter_array [15],  ## TriggerBLatched_param
      "TriggerMode2B": self.parameter_array[19],  ## TriggerMode2B_param
      "TriggerMode2Q": self.parameter_array[20],  ## TriggerMode2Q_param
      "TriggerMode2E": self.parameter_array[21],  ## TriggerMode2E_param
      "TriggerMode2T": self.parameter_array[22],  ## TriggerMode2T_param
      "QdcMode": self.parameter_array [16],  ## QdcMode_param
      "CounterMode": self.parameter_array [25],  ## CounterMode_param
      "TriggerMode": self.parameter_array [29],  ## TriggerMode_param
      "MaxIntegTime": self.parameter_array [13] ,
      "MinIntegTime":self.parameter_array [14]
      }
      sav_channel_chlist=[]
      for ch in range (0,64):
        sav_channel_chlist.append(sav_channel_dic.copy())
      self.Channel_cfg_list=[]
      for T in range (0,8):
          copia=copy.deepcopy(sav_channel_chlist)
          self.Channel_cfg_list.append(copia)

      self.is_a_write = 0x1
      self.target_TIGER_ID = 0x1
      self.command_code = 0x9
      self.TO_ALL_enable = 0x1
      self.channel_ID = 0x3
    ## command codes as defined by Ricardo Bugalho's configurator: CMD_WRCHCFG 0x0; CMD_RDCHCFG = 0x1; CMD_WRccfg = 0x8; CMD_RDccfg = 0x9;
      header_tag = 0x8 << 28
      Channel_cfg_cmd_ID = 0xE #F for Global; E for channel
      ccfg_cmd_tag = Channel_cfg_cmd_ID << 24
      ccfg_cmd_word_count = 9 #11 for Global cfg reg; 9 for channel cfg reg
      self.cmd_header = header_tag + (self.TARGET_GEMROC_ID << 16) + ccfg_cmd_tag + ccfg_cmd_word_count
      self.cmd_word8 = ((self.DisableHyst & 0x1) << 24) + ((self.T2Hyst & 0x7) << 16) + ((self.T1Hyst & 0x7) << 8) + ((self.Ch63ObufMSB & 0x1))
      self.cmd_word7 = ((self.TP_disable_FE & 0x1) << 24) + ((self.TDC_IB_E & 0xF) << 16) + ((self.TDC_IB_T & 0xF) << 8) + ((self.Integ & 0x1))
      self.cmd_word6 = ((self.PostAmpGain & 0x3) << 24) + ((self.FE_delay & 0x1F) << 16) + ((self.Vth_T2 & 0x3F) << 8) + ((self.Vth_T1 & 0x3F))
      self.cmd_word5 = ((self.QTx2Enable & 0x1) << 24) + ((self.MaxIntegTime & 0x7F) << 16) + ((self.MinIntegTime & 0x7F) << 8) + ((self.TriggerBLatched & 0x1))
      self.cmd_word4 = ((self.QdcMode & 0x1) << 24) + ((self.BranchEnableT & 0x1) << 16) + ((self.BranchEnableEQ & 0x1) << 8) + ((self.TriggerMode2B & 0x7))
      self.cmd_word3 = ((self.TriggerMode2Q & 0x3) << 24) + ((self.TriggerMode2E & 0x7) << 16) + ((self.TriggerMode2T & 0x3) << 8) + ((self.TACMinAge & 0x1F))
      self.cmd_word2 = ((self.TACMaxAge & 0x1F) << 24) + ((self.CounterMode & 0xF) << 16) + ((self.DeadTime & 0x3F) << 8) + ((self.SyncChainLen & 0x3))
      self.cmd_word1 = ((self.Ch_DebugMode & 0x3) << 24) + ((self.TriggerMode & 0x3) << 16)
      self.cmd_word0 = ((self.command_code & 0xF) << 11) + ((self.target_TIGER_ID & 0x7) << 8) + ((self.is_a_write & 0x1) << 7) + ((self.TO_ALL_enable & 0x1) << 6) + (self.channel_ID & 0x3F)

      self.command_words = [ self.cmd_header,
                             self.cmd_word8,
                             self.cmd_word7,
                             self.cmd_word6,
                             self.cmd_word5,
                             self.cmd_word4,
                             self.cmd_word3,
                             self.cmd_word2,
                             self.cmd_word1,
                             self.cmd_word0
                              ]

   def __del__(self):
      class_name = self.__class__.__name__
      #print class_name, "ch_reg_settings destroyed"

   def reload_chcfg_settings_from_file(self, ChCFGReg_def_fname_param): ## acr 2018-02-23 new method to reaload from a default file
      self.parameter_array = [0 for i in range(30)] # acr 2018-01-25 [0 for i in range(38)]
      with open(ChCFGReg_def_fname_param, "r") as f:
         self.parameter_array = map(int, f)
      self.DisableHyst = self.parameter_array [0]  ## DisableHyst_param
      self.T2Hyst = self.parameter_array [1]  ## T2Hyst_param
      self.T1Hyst = self.parameter_array [2]  ## T1Hyst_param
      self.Ch63ObufMSB = self.parameter_array [3]  ## Ch63ObufMSB_param
      self.TP_disable_FE = self.parameter_array [4]  ## TP_disable_FE_param
      self.TDC_IB_E = self.parameter_array [5]  ## TDC_IB_E_param
      self.TDC_IB_T = self.parameter_array [6]  ## TDC_IB_T_param
      self.Integ = self.parameter_array [7]  ## Integ_param
      self.PostAmpGain = self.parameter_array [8]  ## PostAmpGain_param
      self.FE_delay = self.parameter_array [9]  ## FE_delay_param
      self.Vth_T2 = self.parameter_array [10]  ## Vth_T2_param
      self.Vth_T1 = self.parameter_array [11]  ## Vth_T1_param
      self.QTx2Enable = self.parameter_array [12]  ## QTx2Enable_param
      self.MaxIntegTime = self.parameter_array [13]  ## MaxIntegTime_param
      self.MinIntegTime = self.parameter_array [14]  ## MinIntegTime_param
      self.TriggerBLatched = self.parameter_array [15]  ## TriggerBLatched_param
      self.QdcMode = self.parameter_array [16]  ## QdcMode_param
      self.BranchEnableT = self.parameter_array [17]  ## BranchEnableT_param
      self.BranchEnableEQ = self.parameter_array [18]  ## BranchEnableEQ_param
      self.TriggerMode2B = self.parameter_array [19]  ## TriggerMode2B_param
      self.TriggerMode2Q = self.parameter_array [20]  ## TriggerMode2Q_param
      self.TriggerMode2E = self.parameter_array [21]  ## TriggerMode2E_param
      self.TriggerMode2T = self.parameter_array [22]  ## TriggerMode2T_param
      self.TACMinAge = self.parameter_array [23]  ## TACMinAge_param
      self.TACMaxAge = self.parameter_array [24]  ## TACMaxAge_param
      self.CounterMode = self.parameter_array [25]  ## CounterMode_param
      self.DeadTime = self.parameter_array [26]  ## DeadTime_param
      self.SyncChainLen = self.parameter_array [27]  ## SyncChainLen_param
      self.Ch_DebugMode = self.parameter_array [28]  ## Ch_DebugMode_param
      self.TriggerMode = self.parameter_array [29]  ## TriggerMode_param

   def cmd_words_array_size(self):
      return len(self.command_words)

   def print_command_words(self):
      for i in range (0, len(self.command_words)):
         print '%08X'% self.command_words[i]

   def set_target_GEMROC(self, GEMROC_ID_param): # acr 2017-09-22
      self.TARGET_GEMROC_ID = GEMROC_ID_param & 0x1f
      self.cmd_header = (self.cmd_header & 0xFF00FFFF) + (self.TARGET_GEMROC_ID << 16)

   def set_target_TIGER(self, target_TIGER_param):
      self.target_TIGER_ID = target_TIGER_param & 0x7
      self.cmd_word0 = ((self.command_code & 0xF) << 12) + ((self.target_TIGER_ID & 0x7) << 8) + ((self.is_a_write & 0x1) << 7) + ((self.TO_ALL_enable & 0x1) << 6) + (self.channel_ID & 0x1F)
      self.command_words[9] = self.cmd_word0

   def set_target_channel(self, target_channel_param):
      self.channel_ID = target_channel_param & 0x3F ## acr 2018-02-20 corrected !! 0x1F
      self.cmd_word0 = ((self.command_code & 0xF) << 12) + ((self.target_TIGER_ID & 0x7) << 8) + ((self.is_a_write & 0x1) << 7) + ((self.TO_ALL_enable & 0x1) << 6) + (self.channel_ID & 0x3F) ## acr 2018-02-20 corrected !!0x1F)
      self.command_words[9] = self.cmd_word0

   def set_Vth_T1(self, Vth_T1_param):
      self.Vth_T1 = Vth_T1_param & 0x3F

   def set_to_ALL_param(self, to_ALL_param):
      self.TO_ALL_enable = to_ALL_param & 0x1
      self.cmd_word0 = ((self.command_code & 0xF) << 12) + ((self.target_TIGER_ID & 0x7) << 8) + ((self.is_a_write & 0x1) << 7) + ((self.TO_ALL_enable & 0x1) << 6) + (self.channel_ID & 0x1F)
      self.command_words[9] = self.cmd_word0

   def set_command_code(self, command_code_param):
      if (command_code_param == 'WR'):
         self.command_code = 0x0
         self.is_a_write = 1
         self.cmd_word0 = ((self.command_code & 0xF) << 12) + ((self.target_TIGER_ID & 0x7) << 8) + ((self.is_a_write & 0x1) << 7) + ((self.TO_ALL_enable & 0x1) << 6) + (self.channel_ID & 0x1F)
         self.command_words[9] = self.cmd_word0
      elif (command_code_param == 'RD'):
         self.command_code = 0x1
         self.is_a_write = 0
         self.cmd_word0 = ((self.command_code & 0xF) << 12) + ((self.target_TIGER_ID & 0x7) << 8) + ((self.is_a_write & 0x1) << 7) + ((self.TO_ALL_enable & 0x1) << 6) + (self.channel_ID & 0x1F)
         self.command_words[9] = self.cmd_word0

   def set_TP_disable_FE(self, TP_disable_FE_param):
      self.TP_disable_FE = TP_disable_FE_param & 0x1

      # Alberto:Added sample and hold and TOT modes

   def sample_and_hold_mode(self):
      self.Integ = 1 & 0x1
      self.QdcMode = 1 & 0x1

   def ToT_mode(self):
      self.Integ = 1 & 0x1
      self.QdcMode = 1 & 0x1

   def update_command_words(self):  # acr 2017-09-01
      if ( (self.command_code & 0xF) == 0x1 ): # acr 2017-09-01
         self.cmd_word8  = 0
         self.cmd_word7  = 0
         self.cmd_word6  = 0
         self.cmd_word5  = 0
         self.cmd_word4  = 0
         self.cmd_word3  = 0
         self.cmd_word2  = 0
         self.cmd_word1  = 0

      elif (self.TO_ALL_enable==1) :

         self.cmd_word8 = ((self.DisableHyst & 0x1) << 24)   + ((self.T2Hyst & 0x7) << 16)        + ((self.T1Hyst & 0x7) << 8)         + ((self.Ch63ObufMSB & 0x1))
         self.cmd_word7 = ((self.TP_disable_FE & 0x1) << 24) + ((self.TDC_IB_E & 0xF) << 16)      + ((self.TDC_IB_T & 0xF) << 8)       + ((self.Integ & 0x1))
         self.cmd_word6 = ((self.PostAmpGain & 0x3) << 24)   + ((self.FE_delay & 0x1F) << 16)     + ((self.Vth_T2 & 0x3F) << 8)        + ((self.Vth_T1 & 0x3F))
         self.cmd_word5 = ((self.QTx2Enable & 0x1) << 24)    + ((self.MaxIntegTime & 0x7F) << 16) + ((self.MinIntegTime & 0x7F) << 8)  + ((self.TriggerBLatched & 0x1))
         self.cmd_word4 = ((self.QdcMode & 0x1) << 24)       + ((self.BranchEnableT & 0x1) << 16) + ((self.BranchEnableEQ & 0x1) << 8) + ((self.TriggerMode2B & 0x7))
         self.cmd_word3 = ((self.TriggerMode2Q & 0x3) << 24) + ((self.TriggerMode2E & 0x7) << 16) + ((self.TriggerMode2T & 0x3) << 8)  + ((self.TACMinAge & 0x1F))
         self.cmd_word2 = ((self.TACMaxAge & 0x1F) << 24)    + ((self.CounterMode & 0xF) << 16)   + ((self.DeadTime & 0x3F) << 8)      + ((self.SyncChainLen & 0x3))
         self.cmd_word1 = ((self.Ch_DebugMode & 0x3) << 24)  + ((self.TriggerMode & 0x3) << 16)

      else:
          TP_disable_FE=self.Channel_cfg_list[self.target_TIGER_ID][self.channel_ID]["TP_disable_FE"] & 0x1
          Integ=self.Channel_cfg_list[self.target_TIGER_ID][self.channel_ID]["Integ"] & 0x1
          Vth_T2= self.Channel_cfg_list[self.target_TIGER_ID][self.channel_ID]["Vth_T2"] & 0x3F
          Vth_T1= self.Channel_cfg_list[self.target_TIGER_ID][self.channel_ID]["Vth_T1"] & 0x3F
          TriggerBLatched = self.Channel_cfg_list[self.target_TIGER_ID][self.channel_ID]["TriggerBLatched"] & 0x1  ## TriggerBLatched_param
          TriggerMode2B = self.Channel_cfg_list[self.target_TIGER_ID][self.channel_ID]["TriggerMode2B"] & 0x7   ## TriggerMode2B_param
          TriggerMode2Q = self.Channel_cfg_list[self.target_TIGER_ID][self.channel_ID]["TriggerMode2Q"] & 0x3   ## TriggerMode2Q_param
          TriggerMode2E = self.Channel_cfg_list[self.target_TIGER_ID][self.channel_ID]["TriggerMode2E"] & 0x7  ## TriggerMode2E_param
          TriggerMode2T = self.Channel_cfg_list[self.target_TIGER_ID][self.channel_ID]["TriggerMode2T"] & 0x3  ## TriggerMode2T_param
          QdcMode= self.Channel_cfg_list[self.target_TIGER_ID][self.channel_ID]["QdcMode"] & 0x1
          CounterMode= self.Channel_cfg_list[self.target_TIGER_ID][self.channel_ID]["CounterMode"]  & 0xF
          TriggerMode= self.Channel_cfg_list[self.target_TIGER_ID][self.channel_ID]["TriggerMode"]  & 0x3
          MaxIntegTime= self.Channel_cfg_list[self.target_TIGER_ID][self.channel_ID]["MaxIntegTime"] & 0x7F
          MinIntegTime= self.Channel_cfg_list[self.target_TIGER_ID][self.channel_ID]["MinIntegTime"] & 0X7F

          self.cmd_word8 = ((self.DisableHyst & 0x1) << 24) + ((self.T2Hyst & 0x7) << 16) + ((self.T1Hyst & 0x7) << 8) + ((self.Ch63ObufMSB & 0x1))
          self.cmd_word7 = (TP_disable_FE << 24) + ((self.TDC_IB_E & 0xF) << 16) + ((self.TDC_IB_T & 0xF) << 8) + (Integ )
          self.cmd_word6 = ((self.PostAmpGain & 0x3) << 24) + ((self.FE_delay & 0x1F) << 16) + (Vth_T2 << 8) + (Vth_T1 )
          self.cmd_word5 = ((self.QTx2Enable & 0x1) << 24) + ((MaxIntegTime) << 16) + ((MinIntegTime) << 8) + ((TriggerBLatched))
          self.cmd_word4 = (QdcMode << 24) + ((self.BranchEnableT & 0x1) << 16) + ((self.BranchEnableEQ & 0x1) << 8) + (TriggerMode2B )
          self.cmd_word3 = (TriggerMode2Q << 24) + (TriggerMode2E << 16) + (TriggerMode2T << 8) + ((self.TACMinAge & 0x1F))
          self.cmd_word2 = ((self.TACMaxAge & 0x1F) << 24) + (CounterMode << 16) + ((self.DeadTime & 0x3F) << 8) + ((self.SyncChainLen & 0x3))
          self.cmd_word1 = ((self.Ch_DebugMode & 0x3) << 24) + (TriggerMode  << 16)


      self.cmd_word0 = ((self.command_code & 0xF) << command_code_shift) + ((self.target_TIGER_ID & 0x7) << target_TIGER_ID_shift) + ((self.TO_ALL_enable & 0x1) << 6) + (self.channel_ID & 0x3F)

      self.command_words = [ self.cmd_header,
                             self.cmd_word8,
                             self.cmd_word7,
                             self.cmd_word6,
                             self.cmd_word5,
                             self.cmd_word4,
                             self.cmd_word3,
                             self.cmd_word2,
                             self.cmd_word1,
                             self.cmd_word0
                              ]
   def extract_parameters_from_UDP_packet(self):
      print'\nList of parameters sent to TIGER%d:'%self.target_TIGER_ID
      print ("\ncmd_word8: DisableHyst:%02X;\t\tT2Hyst:%02X;\t\tT1Hyst:%02X;\t\tCh63ObufMSB:%02X;"                  %( ((self.cmd_word8>>24)&0x1), ((self.cmd_word8>>16)&0x7),  ((self.cmd_word8>>8)&0x7),  ((self.cmd_word8>>0)&0x1)  ) )
      print ("\ncmd_word7: TP_disable_FE:%02X;\t\tTDC_IB_E:%02X;\t\tTDC_IB_T:%02X;\t\tInteg:%02X;"                  %( ((self.cmd_word7>>24)&0x1), ((self.cmd_word7>>16)&0xF),  ((self.cmd_word7>>8)&0xF),  ((self.cmd_word7>>0)&0x1)  ) )
      print ("\ncmd_word6: PostAmpGain:%02X;\t\tFE_delay:%02X;\t\tVth_T2:%02X;\t\tVth_T1:%02X;"                     %( ((self.cmd_word6>>24)&0x3), ((self.cmd_word6>>16)&0x1F), ((self.cmd_word6>>8)&0x3F), ((self.cmd_word6>>0)&0x3F) ) )
      print ("\ncmd_word5: QTx2Enable:%02X;\t\tMaxIntegTime:%02X;\t\tMinIntegTime:%02X;\t\tTriggerBLatched:%02X;"   %( ((self.cmd_word5>>24)&0x1), ((self.cmd_word5>>16)&0x7F), ((self.cmd_word5>>8)&0x7F), ((self.cmd_word5>>0)&0x1)  ) )
      print ("\ncmd_word4: QdcMode:%02X;\t\tBranchEnableT:%02X;\t\tBranchEnableEQ:%02X;\t\tTriggerMode2B:%02X;"     %( ((self.cmd_word4>>24)&0x1), ((self.cmd_word4>>16)&0x1),  ((self.cmd_word4>>8)&0x1),  ((self.cmd_word4>>0)&0x7)  ) )
      print ("\ncmd_word3: TriggerMode2Q:%02X;\t\tTriggerMode2E:%02X;\t\tTriggerMode2T:%02X;\t\tTACMinAge:%02X;"    %( ((self.cmd_word3>>24)&0x3), ((self.cmd_word3>>16)&0x7),  ((self.cmd_word3>>8)&0x3),  ((self.cmd_word3>>0)&0x1F) ) )
      print ("\ncmd_word2: TACMaxAge:%02X;\t\tCounterMode:%02X;\t\tDeadTime:%02X;\t\tSyncChainLen:%02X;"            %( ((self.cmd_word2>>24)&0x1F),((self.cmd_word2>>16)&0xF),  ((self.cmd_word2>>8)&0x3F), ((self.cmd_word2>>0)&0x3)  ) )
      print ("\ncmd_word1: Ch_DebugMode:%02X;\t\tTriggerMode:%02X;"                                                 %( ((self.cmd_word1>>24)&0x3), ((self.cmd_word1>>16)&0x3)                                                          ) )
      print ("\ncmd_word0: command_code:%02X;\t\ttarget_TIGER_ID:%02X;\t\tTO_ALL_enable:%02X;\t\tchannel_ID:%02X;"  %( ((self.cmd_word0>>command_code_shift)&0xF), ((self.cmd_word0>>target_TIGER_ID_shift)&0x7),  ((self.cmd_word0>>6)&0x1), ((self.cmd_word0>>0)&0x3F)  ) )

   def save_ch_conf(self,filename):
        with  open(filename,'wb') as f:
            pickle.dump(self.Channel_cfg_list,f)
        with open("file.txt", "w") as output:
                output.write(str(self.Channel_cfg_list))
        return 0
   def load_ch_conf(self,filename):
        with  open(filename,'rb') as f:
            self.Channel_cfg_list=pickle.load(f)
        with open("file2.txt", "w") as output:
            output.write(str(self.Channel_cfg_list))
        return 0
###CCCCCCCCCCCCCCCC###     CLASS gemroc_cmd_LV_settings BEGIN  ###CCCCCCCCCCCCCCCC######CCCCCCCCCCCCCCCC######CCCCCCCCCCCCCCCC######CCCCCCCCCCCCCCCC######CCCCCCCCCCCCCCCC###
# acr 2018-01-13 split the handling of the GEMROC LV and DAQ configuration parameters
class gemroc_cmd_LV_settings(object): # purpose: organize the GEMROC Configuration Register Settings in an array format which can be sent over Ethernet or optical link
   def __init__(self,
                TARGET_GEMROC_ID_param = 0, # acr 2017-09-22
                command_string_param = 'NONE',
                #acr 2018-01-22 TCAM_ID_param = 1,
                number_of_repetitions_param = 1,
                #acr 2018-01-22 to_ALL_TCAM_enable_param = 0
                cfg_filename_param = 'GEMROC_X_def_cfg_LV_2018.txt',# acr 2018-02-19
                delay_save="time_delay_save"):
      self.TARGET_GEMROC_ID = TARGET_GEMROC_ID_param # acr 2017-09-22
      # acr 2017-09-22 self.cfg_filename = 'GEMROC_%d_def_cfg_LV_2018.txt'% self.TARGET_GEMROC_ID
      self.cfg_filename = cfg_filename_param # acr 2017-09-22
      #self.parameter_array = [0 for i in range(34)] # acr 2017-12-07 range extended from 30 to 34
      self.parameter_array = [0 for i in range(GEMROC_CMD_LV_Num_of_params-1)] # acr 2018-01-15
      with open(self.cfg_filename, "r") as f:
         self.parameter_array = map(int, f)

      # acr 2018-01-15 NOTE: position of parameters in parameter file and index in parameter array redefined on the basis of GEMROC_CMD_LV_Num_of_params
      # setting of delay of timing signals to TIGER FEB0 in xns units (relative to TIGER_CLK_LVDS)
      try:
          with open(delay_save, "r") as f:
              while True:
                  line = f.readline()
                  if (line.split())[0] == "GEMROC" and int(line.split()[1]) == TARGET_GEMROC_ID_param:
                      timing_array = f.readline().split()
                      break
          self.TIMING_DLY_FEB0 = int(timing_array[0]) # acr 2018-01-15 last parameter written in default configuration file
          self.TIMING_DLY_FEB1 = int(timing_array[1])
          self.TIMING_DLY_FEB2 = int(timing_array[2])
          self.TIMING_DLY_FEB3 = int(timing_array[3])
      except:
            raise Exception ('Problems with the time delay settings file')
      self.FEB_PWR_EN_pattern = self.parameter_array [GEMROC_CMD_LV_Num_of_params-5]
      self.FEB_OVC_EN_pattern = self.parameter_array [GEMROC_CMD_LV_Num_of_params-6]
      self.FEB_OVV_EN_pattern = self.parameter_array [GEMROC_CMD_LV_Num_of_params-7]
      self.FEB_OVT_EN_pattern = self.parameter_array [GEMROC_CMD_LV_Num_of_params-8]
      self.ROC_OVT_EN  = self.parameter_array [GEMROC_CMD_LV_Num_of_params-9] # 1 bit
      self.XCVR_LPBCK_TST_EN  = self.parameter_array [GEMROC_CMD_LV_Num_of_params-10] #
      self.ROC_OVT_LIMIT = self.parameter_array [GEMROC_CMD_LV_Num_of_params-11] # Overtemperature limit for GEMROC module; range 0..63: resolution 1 bin = 1degree C
      self.A_OVC_LIMIT_FEB0 = self.parameter_array [GEMROC_CMD_LV_Num_of_params-12] # Overcurrent limit for V_analog of FEBx connected to the target GEMROC module; range 0..511
      self.A_OVV_LIMIT_FEB0 = self.parameter_array [GEMROC_CMD_LV_Num_of_params-13] # Overvoltage limit for V_analog of FEBx connected to the target GEMROC module; range 0..511
      self.A_OVC_LIMIT_FEB1 = self.parameter_array [GEMROC_CMD_LV_Num_of_params-14]
      self.A_OVV_LIMIT_FEB1 = self.parameter_array [GEMROC_CMD_LV_Num_of_params-15]
      self.A_OVC_LIMIT_FEB2 = self.parameter_array [GEMROC_CMD_LV_Num_of_params-16]
      self.A_OVV_LIMIT_FEB2 = self.parameter_array [GEMROC_CMD_LV_Num_of_params-17]
      self.A_OVC_LIMIT_FEB3 = self.parameter_array [GEMROC_CMD_LV_Num_of_params-18]
      self.A_OVV_LIMIT_FEB3 = self.parameter_array [GEMROC_CMD_LV_Num_of_params-19]
      self.D_OVC_LIMIT_FEB0 = self.parameter_array [GEMROC_CMD_LV_Num_of_params-20] # Overcurrent limit for V_digital of FEBx connected to the target GEMROC module; range 0..511
      self.D_OVV_LIMIT_FEB0 = self.parameter_array [GEMROC_CMD_LV_Num_of_params-21] # Overvoltage limit for V_digital of FEBx connected to the target GEMROC module; range 0..511
      self.OVT_LIMIT_FEB0 = self.parameter_array [GEMROC_CMD_LV_Num_of_params-22] # OverTemperature limit for FEBx connected to the target GEMROC module; range 0..255
      self.D_OVC_LIMIT_FEB1 = self.parameter_array [GEMROC_CMD_LV_Num_of_params-23]
      self.D_OVV_LIMIT_FEB1 = self.parameter_array [GEMROC_CMD_LV_Num_of_params-24]
      self.OVT_LIMIT_FEB1 = self.parameter_array [GEMROC_CMD_LV_Num_of_params-25]
      self.D_OVC_LIMIT_FEB2 = self.parameter_array [GEMROC_CMD_LV_Num_of_params-26]
      self.D_OVV_LIMIT_FEB2 = self.parameter_array [GEMROC_CMD_LV_Num_of_params-27]
      self.OVT_LIMIT_FEB2 = self.parameter_array [GEMROC_CMD_LV_Num_of_params-28]
      self.D_OVC_LIMIT_FEB3 = self.parameter_array [GEMROC_CMD_LV_Num_of_params-29]
      self.D_OVV_LIMIT_FEB3 = self.parameter_array [GEMROC_CMD_LV_Num_of_params-30]
      self.OVT_LIMIT_FEB3 = self.parameter_array [GEMROC_CMD_LV_Num_of_params-31]

      self.TIGER_for_counter = 0 #TIGER on which we count error or hits
      self.HIT_counter_disable = 0 # 1= counting errors, 0= counting hits
      self.CHANNEL_for_counter =64 #0-63 for single channel hits, 64 for chip total
      self.RX_ERR_CNT_RST =0 #counter reset
      self.command_string = command_string_param
      self.command_list = [ 'NONE',
                            'CMD_GEMROC_LV_CFG_WR',
                            'CMD_GEMROC_LV_CFG_RD',
                            'CMD_GEMROC_LV_IVT_UPDATE',
                            'CMD_GEMROC_LV_IVT_READ',
                            'CMD_GEMROC_TIMING_DELAYS_UPDATE',
                            'CMD_GEMROC_LV_REMOTE_HARD_RESET'
                       ]
      self.is_a_write = 0x1
      for i in range (0, len(self.command_list)):
         if (self.command_string == self.command_list[i]):
            self.gemroc_cmd_code = i
      header_tag = 0x8 << 28
      self.gemroc_cmd_ID = 0xC #F for Global config register settings; E for channel config register settings; D for gemroc DAQ parameter settings; C for gemroc lv_Config parameter settings
      gemroc_cmd_word_count = GEMROC_CMD_LV_Num_Of_PktWords - 1 # acr 2018-01-15 number of packet words following the header
      self.cmd_header = ((0x8 & 0xF) << 28) + ((self.gemroc_cmd_ID & 0xF) << 24) + ((self.TIGER_for_counter & 0x7) << 21) + ((self.TARGET_GEMROC_ID & 0x1f) << 16) + ((self.HIT_counter_disable & 0x1) << 15) + ((self.CHANNEL_for_counter & 0x7F) << 8) + (gemroc_cmd_word_count & 0xff)
      self.cmd_word10 = ((self.OVT_LIMIT_FEB3 & 0xFF) << 22) + ((self.D_OVV_LIMIT_FEB3 & 0x1FF) << 13) + ((self.D_OVC_LIMIT_FEB3 & 0x1FF) << 4)
      self.cmd_word9 = ((self.OVT_LIMIT_FEB2 & 0xFF) << 22) + ((self.D_OVV_LIMIT_FEB2 & 0x1FF) << 13) + ((self.D_OVC_LIMIT_FEB2 & 0x1FF) << 4)
      self.cmd_word8 = ((self.OVT_LIMIT_FEB1 & 0xFF) << 22) + ((self.D_OVV_LIMIT_FEB1 & 0x1FF) << 13) + ((self.D_OVC_LIMIT_FEB1 & 0x1FF) << 4)
      self.cmd_word7 = ((self.OVT_LIMIT_FEB0 & 0xFF) << 22) + ((self.D_OVV_LIMIT_FEB0 & 0x1FF) << 13) + ((self.D_OVC_LIMIT_FEB0 & 0x1FF) << 4)
      self.cmd_word6 = ((self.A_OVV_LIMIT_FEB3 & 0x1FF) << 13) + ((self.A_OVC_LIMIT_FEB3 & 0x1FF) << 4)
      self.cmd_word5 = ((self.A_OVV_LIMIT_FEB2 & 0x1FF) << 13) + ((self.A_OVC_LIMIT_FEB2 & 0x1FF) << 4)
      self.cmd_word4 = ((self.A_OVV_LIMIT_FEB1 & 0x1FF) << 13) + ((self.A_OVC_LIMIT_FEB1 & 0x1FF) << 4)
      self.cmd_word3 = ((self.A_OVV_LIMIT_FEB0 & 0x1FF) << 13) + ((self.A_OVC_LIMIT_FEB0 & 0x1FF) << 4)
      self.cmd_word2 = ((self.ROC_OVT_LIMIT & 0x3F) << 24) +((self.RX_ERR_CNT_RST & 0x1) << 19)+ ((self.XCVR_LPBCK_TST_EN & 0x1) << 18) + ((self.ROC_OVT_EN & 0x1) << 16) + ((self.FEB_OVT_EN_pattern & 0xF) << 12) + ((self.FEB_OVV_EN_pattern & 0xF) << 8) + ((self.FEB_OVC_EN_pattern & 0xF) << 4) + (self.FEB_PWR_EN_pattern & 0xF)
      self.cmd_word1 = ((self.TIMING_DLY_FEB3 & 0x3F) << 24) + ((self.TIMING_DLY_FEB2 & 0x3F) << 16) + ((self.TIMING_DLY_FEB1 & 0x3F) << 8) + ((self.TIMING_DLY_FEB0 & 0x3F) << 0)
      self.cmd_word0 = ((self.gemroc_cmd_code & 0xF) << 11)
      self.command_words = [self.cmd_header,
                            self.cmd_word10,
                            self.cmd_word9,
                            self.cmd_word8,
                            self.cmd_word7,
                            self.cmd_word6,
                            self.cmd_word5,
                            self.cmd_word4,
                            self.cmd_word3,
                            self.cmd_word2,
                            self.cmd_word1,
                            self.cmd_word0
                            ]

   def __del__(self):
      class_name = self.__class__.__name__
      #print class_name, "gemroc_cmd_LV_settings destroyed"

   def cmd_words_array_size(self):
      return len(self.command_words)

   def print_command_words(self):
      for i in range (0, len(self.command_words)):
         print '%08X'% self.command_words[i]

   def set_target_GEMROC (self, GEMROC_ID_param):
      self.TARGET_GEMROC_ID = GEMROC_ID_param & 0x1F
      self.cmd_header = (self.cmd_header & 0xFF00FFFF) + (self.TARGET_GEMROC_ID << 16)

   def set_FEB_PWR_EN_pattern(self, target_FEB_PWR_EN_pattern): # acr 2017-10-03
      self.FEB_PWR_EN_pattern = target_FEB_PWR_EN_pattern & 0xF

   def set_timing_toFEB_delay(self, FEB3dly_param, FEB2dly_param, FEB1dly_param, FEB0dly_param): # acr 2017-12-07
      self.TIMING_DLY_FEB3 = FEB3dly_param & 0x3F
      self.TIMING_DLY_FEB2 = FEB2dly_param & 0x3F
      self.TIMING_DLY_FEB1 = FEB1dly_param & 0x3F
      self.TIMING_DLY_FEB0 = FEB0dly_param & 0x3F

   def set_gemroc_cmd_code(self, command_string_param, no_of_executions_param):
      self.number_of_repetitions = no_of_executions_param
      self.command_string = command_string_param
      for i in range (0, len(self.command_list)):
         if (self.command_string == self.command_list[i]):
            self.gemroc_cmd_code = i

## acr 2018-01-15 updated definition: zero all setting when it's a 'CMD_GEMROC_LV_CFG_RD' ( = 2 ) or 'CMD_GEMROC_LV_IVT_READ' ( = 3 ) or 'CMD_GEMROC_TIMING_DELAYS_UPDATE' ( = 4 )
   def update_command_words(self):
      gemroc_cmd_tag = 0xC << 24
      gemroc_cmd_word_count = GEMROC_CMD_LV_Num_Of_PktWords - 1
      if ( ((self.gemroc_cmd_code & 0xF) == 0x2) or ((self.gemroc_cmd_code & 0xF) == 0x3) or ((self.gemroc_cmd_code & 0xF) == 0x4) ):
         self.cmd_word10  = 0
         self.cmd_word9  = 0
         self.cmd_word8  = 0
         self.cmd_word7  = 0
         self.cmd_word6  = 0
         self.cmd_word5  = 0
         self.cmd_word4  = 0
         self.cmd_word3  = 0
         self.cmd_word2  = 0
         self.cmd_word1  = 0
      else:
         self.cmd_header = ((0x8 & 0xF) << 28) + ((self.gemroc_cmd_ID & 0xF) << 24) + ((self.TIGER_for_counter & 0x7) << 21) + ((self.TARGET_GEMROC_ID & 0x1f) << 16) + ((self.HIT_counter_disable & 0x1) << 15) + (
                 (self.CHANNEL_for_counter & 0x7F) << 8) + (gemroc_cmd_word_count & 0xff)
         self.cmd_word10 = ((self.OVT_LIMIT_FEB3 & 0xFF) << 22) + ((self.D_OVV_LIMIT_FEB3 & 0x1FF) << 13) + ((self.D_OVC_LIMIT_FEB3 & 0x1FF) << 4)
         self.cmd_word9 = ((self.OVT_LIMIT_FEB2 & 0xFF) << 22) + ((self.D_OVV_LIMIT_FEB2 & 0x1FF) << 13) + ((self.D_OVC_LIMIT_FEB2 & 0x1FF) << 4)
         self.cmd_word8 = ((self.OVT_LIMIT_FEB1 & 0xFF) << 22) + ((self.D_OVV_LIMIT_FEB1 & 0x1FF) << 13) + ((self.D_OVC_LIMIT_FEB1 & 0x1FF) << 4)
         self.cmd_word7 = ((self.OVT_LIMIT_FEB0 & 0xFF) << 22) + ((self.D_OVV_LIMIT_FEB0 & 0x1FF) << 13) + ((self.D_OVC_LIMIT_FEB0 & 0x1FF) << 4)
         self.cmd_word6 = ((self.A_OVV_LIMIT_FEB3 & 0x1FF) << 13) + ((self.A_OVC_LIMIT_FEB3 & 0x1FF) << 4)
         self.cmd_word5 = ((self.A_OVV_LIMIT_FEB2 & 0x1FF) << 13) + ((self.A_OVC_LIMIT_FEB2 & 0x1FF) << 4)
         self.cmd_word4 = ((self.A_OVV_LIMIT_FEB1 & 0x1FF) << 13) + ((self.A_OVC_LIMIT_FEB1 & 0x1FF) << 4)
         self.cmd_word3 = ((self.A_OVV_LIMIT_FEB0 & 0x1FF) << 13) + ((self.A_OVC_LIMIT_FEB0 & 0x1FF) << 4)
         self.cmd_word2 = ((self.ROC_OVT_LIMIT & 0x3F) << 24) + ((self.RX_ERR_CNT_RST & 0x1) << 19) + ((self.XCVR_LPBCK_TST_EN & 0x1) << 18) + ((self.ROC_OVT_EN & 0x1) << 16) + ((self.FEB_OVT_EN_pattern & 0xF) << 12) + ((self.FEB_OVV_EN_pattern & 0xF) << 8) + (
                 (self.FEB_OVC_EN_pattern & 0xF) << 4) + (self.FEB_PWR_EN_pattern & 0xF)
         self.cmd_word1 = ((self.TIMING_DLY_FEB3 & 0x3F) << 24) + ((self.TIMING_DLY_FEB2 & 0x3F) << 16) + ((self.TIMING_DLY_FEB1 & 0x3F) << 8) + ((self.TIMING_DLY_FEB0 & 0x3F) << 0)
      # acr 2018-01-16      self.cmd_word0 = ((self.number_of_repetitions & 0x3FF) << 16) + ((self.gemroc_cmd_code & 0xF) << 11) + ((self.target_TCAM_ID & 0x3) << 8) + ((self.to_ALL_TCAM_enable & 0x1) << 6)
      self.cmd_word0 = ((self.gemroc_cmd_code & 0xF) << 11)
      self.command_words = [self.cmd_header,
                            self.cmd_word10,
                            self.cmd_word9,
                            self.cmd_word8,
                            self.cmd_word7,
                            self.cmd_word6,
                            self.cmd_word5,
                            self.cmd_word4,
                            self.cmd_word3,
                            self.cmd_word2,
                            self.cmd_word1,
                            self.cmd_word0
                            ]
   def extract_parameters_from_UDP_packet(self):
      print ( "\n   OVT_LIMIT_FEB3 = %04X %d")  % ( ((self.cmd_word10 >> 22) &  0xFF), ((self.cmd_word10 >> 22) &  0xFF) )
      print ( "\n D_OVV_LIMIT_FEB3 = %04X %d ") % ( ((self.cmd_word10 >> 13) &  0x1FF), ((self.cmd_word10 >> 13) &  0x1FF) )
      print ( "\n D_OVC_LIMIT_FEB3 = %04X %d")  % ( ((self.cmd_word10 >> 4) &  0x1FF), ((self.cmd_word10 >> 4) &  0x1FF) )
      print ( "\n   OVT_LIMIT_FEB2 = %04X %d")  % ( ((self.cmd_word9 >> 22) &  0xFF), ((self.cmd_word9 >> 22) &  0xFF) )
      print ( "\n D_OVV_LIMIT_FEB2 = %04X %d ") % ( ((self.cmd_word9 >> 13) &  0x1FF), ((self.cmd_word9 >> 13) &  0x1FF) )
      print ( "\n D_OVC_LIMIT_FEB2 = %04X %d")  % ( ((self.cmd_word9 >> 4) &  0x1FF), ((self.cmd_word9 >> 4) &  0x1FF) )
      print ( "\n   OVT_LIMIT_FEB1 = %04X %d")  % ( ((self.cmd_word8 >> 22) &  0xFF), ((self.cmd_word8 >> 22) &  0xFF) )
      print ( "\n D_OVV_LIMIT_FEB1 = %04X %d ") % ( ((self.cmd_word8 >> 13) &  0x1FF), ((self.cmd_word8 >> 13) &  0x1FF) )
      print ( "\n D_OVC_LIMIT_FEB1 = %04X %d")  % ( ((self.cmd_word8 >> 4) &  0x1FF), ((self.cmd_word8 >> 4) &  0x1FF) )
      print ( "\n   OVT_LIMIT_FEB0 = %04X %d")  % ( ((self.cmd_word7 >> 22) &  0xFF), ((self.cmd_word7 >> 22) &  0xFF) )
      print ( "\n D_OVV_LIMIT_FEB0 = %04X %d ") % ( ((self.cmd_word7 >> 13) &  0x1FF), ((self.cmd_word7 >> 13) &  0x1FF) )
      print ( "\n D_OVC_LIMIT_FEB0 = %04X %d")  % ( ((self.cmd_word7 >> 4) &  0x1FF), ((self.cmd_word7 >> 4) &  0x1FF) )
      print ( "\n A_OVV_LIMIT_FEB3 = %04X %d ") % ( ((self.cmd_word6 >> 13) &  0x1FF), ((self.cmd_word6 >> 13) &  0x1FF) )
      print ( "\n A_OVC_LIMIT_FEB3 = %04X %d")  % ( ((self.cmd_word6 >> 4) &  0x1FF), ((self.cmd_word6 >> 4) &  0x1FF) )
      print ( "\n A_OVV_LIMIT_FEB2 = %04X %d ") % ( ((self.cmd_word5 >> 13) &  0x1FF), ((self.cmd_word5 >> 13) &  0x1FF) )
      print ( "\n A_OVC_LIMIT_FEB2 = %04X %d")  % ( ((self.cmd_word5 >> 4) &  0x1FF), ((self.cmd_word5 >> 4) &  0x1FF) )
      print ( "\n A_OVV_LIMIT_FEB1 = %04X %d ") % ( ((self.cmd_word4 >> 13) &  0x1FF), ((self.cmd_word4 >> 13) &  0x1FF) )
      print ( "\n A_OVC_LIMIT_FEB1 = %04X %d")  % ( ((self.cmd_word4 >> 4) &  0x1FF), ((self.cmd_word4 >> 4) &  0x1FF) )
      print ( "\n A_OVV_LIMIT_FEB0 = %04X %d ") % ( ((self.cmd_word3 >> 13) &  0x1FF), ((self.cmd_word3 >> 13) &  0x1FF) )
      print ( "\n A_OVC_LIMIT_FEB0 = %04X %d")  % ( ((self.cmd_word3 >> 4) &  0x1FF), ((self.cmd_word3 >> 4) &  0x1FF) )
      print ( "\n ROC_OVT_LIMIT = %04X %d")  % ( ((self.cmd_word2 >> 24) &  0x3F), ((self.cmd_word2 >> 24) &  0x3F) )
      print ( "\n XCVR_LPBCK_TST_EN = %d")  % ((self.cmd_word2 >> 18) &  0x1)
      print ( "\n ROC_OVT_EN = %d")  % ((self.cmd_word2 >> 16) &  0x1)
      print ( "\n FEB_OVT_EN_pattern = %01X %d")  % ( ((self.cmd_word2 >> 12) &  0xF), ((self.cmd_word2 >> 12) &  0xF) )
      print ( "\n FEB_OVV_EN_pattern = %01X %d")  % ( ((self.cmd_word2 >> 8) &  0xF), ((self.cmd_word2 >> 8) &  0xF) )
      print ( "\n FEB_OVC_EN_pattern = %01X %d")  % ( ((self.cmd_word2 >> 4) &  0xF), ((self.cmd_word2 >> 4) &  0xF) )
      print ( "\n FEB_PWR_EN_pattern = %01X %d")  % ( ((self.cmd_word2 >> 0) &  0xF), ((self.cmd_word2 >> 0) &  0xF) )
      print ( "\n TIMING_DLY_FEB3 = %02X %d")  % ( ((self.cmd_word1 >> 24) &  0x3F), ((self.cmd_word1 >> 24) &  0x3F) )
      print ( "\n TIMING_DLY_FEB2 = %02X %d")  % ( ((self.cmd_word1 >> 16) &  0x3F), ((self.cmd_word1 >> 16) &  0x3F) )
      print ( "\n TIMING_DLY_FEB1 = %02X %d")  % ( ((self.cmd_word1 >>  8) &  0x3F), ((self.cmd_word1 >>  8) &  0x3F) )
      print ( "\n TIMING_DLY_FEB0 = %02X %d")  % ( ((self.cmd_word1 >>  0) &  0x3F), ((self.cmd_word1 >>  0) &  0x3F) )


# acr 2018-01-13 split the handling of the GEMROC LV and DAQ configuration parameters
# ab 2018-02-02 changing the import in order to have only 1 default config file
class gemroc_cmd_DAQ_settings(object): # purpose: organize the GEMROC Configuration Register Settings in an array format which can be sent over Ethernet or optical link
   def __init__(self,
                TARGET_GEMROC_ID_param = 0, # acr 2017-09-22
                command_string_param = 'NONE',
                TCAM_ID_param = 1,
                number_of_repetitions_param = 1,
                to_ALL_TCAM_enable_param = 0,
                # acr 2018-04-24 cfg_filename_param = 'GEMROC_X_def_cfg_DAQ_2018v3.txt'# acr 2018-02-19
                cfg_filename_param = 'GEMROC_X_def_cfg_DAQ_2018v5.txt'# acr 2018-07-11
                ):
      self.TARGET_GEMROC_ID = TARGET_GEMROC_ID_param # acr 2017-09-22
      # acr 2018-02-19 self.cfg_filename = 'GEMROC_%d_def_cfg_DAQ_2018.txt'% self.TARGET_GEMROC_ID
      self.cfg_filename = cfg_filename_param # acr 2018-02-19
      self.parameter_array = [0 for i in range(GEMROC_CMD_DAQ_Num_of_params-1)] # acr 2018-01-15
      with open(self.cfg_filename, "r") as f:
         self.parameter_array = map(int, f)
      self.Dbg_functions_ctrl_bits_LoNibble = self.parameter_array [GEMROC_CMD_DAQ_Num_of_params-16] # acr 2018-04-24 last parameter written (at the top!) in default configuration file v4
      self.Dbg_functions_ctrl_bits_HiNibble = self.parameter_array [GEMROC_CMD_DAQ_Num_of_params-15] # Enable simulated L1 (periodic) Trigger Generation for TCAM[3..0]
      self.UDP_DATA_DESTINATION_IPADDR = self.parameter_array [GEMROC_CMD_DAQ_Num_of_params-14] # latency with respect to the event of BES-III L1 trigger (in units of BES-III clk cycles); range: 0..1023
      self.UDP_DATA_DESTINATION_IPPORT = int(TARGET_GEMROC_ID_param) # latency with respect to the event of BES-III L1 trigger (in units of BES-III clk cycles); range: 0..1023
      self.L1_TM_xtrct_start_latency = self.parameter_array [GEMROC_CMD_DAQ_Num_of_params-12] # acr 2018-07-11 IT IS OBSOLETE!!! latency with respect to the event of BES-III L1 trigger (in units of BES-III clk cycles); range: 0..1023
      self.L1_period = self.parameter_array [GEMROC_CMD_DAQ_Num_of_params-11] # period (in units of BES-III clk cycles) of periodic simulated L1 triggers; range: 0..1023
      self.TP_width = self.parameter_array [GEMROC_CMD_DAQ_Num_of_params-10] # acr 2017-09-28 width (in units of BES-III clk cycles) of periodic Test Pulses; range: 0..15
      self.L1_win_upper_edge_offset = self.parameter_array [GEMROC_CMD_DAQ_Num_of_params-9] # offset, w.r.t. to current write pointer, at which to stop reading data from the TIGER data ring buffers; range: 16 bits
      self.L1_win_lower_edge_offset = self.parameter_array [GEMROC_CMD_DAQ_Num_of_params-8] # offset, w.r.t. to current write pointer, at which to start reading data from the TIGER data ring buffers; range: 16 bits
      self.TP_period = self.parameter_array [GEMROC_CMD_DAQ_Num_of_params-7] # period (in units of BES-III clk cycles) of periodic Test Pulses; range: 0..1023
      self.Periodic_TP_EN_pattern = self.parameter_array [GEMROC_CMD_DAQ_Num_of_params-6] # Enable Periodic Test Pulse Generation for TCAM[3..0]
      self.TL_nTM_ACQ = self.parameter_array [GEMROC_CMD_DAQ_Num_of_params-5] # 1 bit selector between TL and nTM data acquisition
      self.AUTO_L1_EN_bit = self.parameter_array [GEMROC_CMD_DAQ_Num_of_params-4] # REDUCED TO 1 bit Enable simulated L1 Trigger Generation for TCAM[3..0]
      self.AUTO_TP_EN_bit = self.parameter_array [GEMROC_CMD_DAQ_Num_of_params-3] # REDUCED TO 1 bit Enable Test Pulse Generation for TCAM[3..0]
      self.TP_Pos_nNeg = self.parameter_array [GEMROC_CMD_DAQ_Num_of_params-2] # select polarity of test pulse output to TIGER
      #Note: TCAM = Tiger Configuration/ Acquisition Module
      self.EN_TM_TCAM_pattern = self.parameter_array [GEMROC_CMD_DAQ_Num_of_params-1] # acr 2018-01-15 last parameter written in default configuration file # 8 bit field; EN_TM_TCAM[7..0] Enable the target TCAM to generate Trigger Matched data packets
      self.command_string = command_string_param
      self.target_TCAM_ID = TCAM_ID_param
      self.to_ALL_TCAM_enable = to_ALL_TCAM_enable_param
      self.number_of_repetitions = number_of_repetitions_param
      self.command_list = [ 'NONE',
                            'CMD_GEMROC_DAQ_CFG_WR',
                            'CMD_GEMROC_DAQ_CFG_RD',
                            'CMD_GEMROC_DAQ_TIGER_GCFGREG_RESET',
                            'CMD_GEMROC_DAQ_TIGER_SYNCH_RST',
                            'CMD_GEMROC_DAQ_TCAM_SYNCH_RST',
                            'CMD_GEMROC_DAQ_TP_GEN',
                            'CMD_GEMROC_DAQ_L1_GEN',
                            'CMD_GEMROC_DAQ_ACK_SEQ_ERROR',
                            'CMD_GEMROC_DAQ_XCVR_LPBCK_TEST',
                            'CMD_GEMROC_DAQ_DIAGN_DPRAM_ACCESS'
                       ]
      self.is_a_write = 0x1
      if self.TARGET_GEMROC_ID in (0,4,11):
          B3Clk_sim_en_param=1
      else:
          B3Clk_sim_en_param=0

      self.DAQ_config_dict = {
        "GEMROC":                                   self.TARGET_GEMROC_ID,
        "UDP_DATA_DESTINATION_IPADDR":              self.UDP_DATA_DESTINATION_IPADDR,
        "Simulated_L1_latency":                     self.L1_TM_xtrct_start_latency,
        "TP_width":                                 self.TP_width,
        "L1_scan_window_UPPER_edge":                self.L1_win_upper_edge_offset,
        "L1_period_simulated":                      self.L1_period,
        "Tpulse_generation_w_L1Chk_enable":         ((self.Dbg_functions_ctrl_bits_HiNibble &0x2 )>>1),
        "Periodic_L1En":                            ((self.Dbg_functions_ctrl_bits_HiNibble &0x1 )>>0),
        "L1_scan_window_LOWER_edge":                self.L1_win_lower_edge_offset,
        "TP_period":                                self.TP_period,
        "Periodic_TP_EN_pattern":                   self.Periodic_TP_EN_pattern,
        "Enable_DAQPause_Until_First_Trigger":      ((self.Dbg_functions_ctrl_bits_LoNibble &0x8)>>3),
        "DAQPause_Set":                             ((self.Dbg_functions_ctrl_bits_LoNibble &0x4)>>2),
        "Tpulse_generation_w_ext_trigger_enable":   ((self.Dbg_functions_ctrl_bits_LoNibble &0x2)>>1),
        "EXT_nINT_B3clk":                           ((self.Dbg_functions_ctrl_bits_LoNibble &0x1)>>0),
        "TL_nTM_ACQ":                               self.TL_nTM_ACQ,
        "AUTO_L1_EN":                               self.AUTO_L1_EN_bit,
        "AUTO_TP_EN":                               self.AUTO_TP_EN_bit,
        "TP_Pos_nNeg":                              self.TP_Pos_nNeg,
        "EN_TM_TCAM_pattern":                       self.EN_TM_TCAM_pattern,
        "UDP_DATA_DESTINATION_IPPORT":              self.UDP_DATA_DESTINATION_IPPORT,
        "number_of_repetitions":                    self.number_of_repetitions,
        "target_TCAM_ID":                           self.target_TCAM_ID,
        "TO_ALL_TCAM_EN":                           self.to_ALL_TCAM_enable,
        "B3Clk_sim_en":                             B3Clk_sim_en_param,
        "DAQPause_Flag":                            0,
        "top_daq_pll_unlocked_sticky_flag":         0
      }
      for i in range (0, len(self.command_list)):
         if (self.command_string == self.command_list[i]):
            self.gemroc_cmd_code = i
      header_tag = 0x8 << 28
      gemroc_cmd_ID = 0xD #F for Global config register settings; E for channel config register settings; D for gemroc DAQ parameter settings; C for gemroc lv_Config parameter settings
      gemroc_cmd_tag = gemroc_cmd_ID << 24
      gemroc_cmd_word_count = GEMROC_CMD_DAQ_Num_Of_PktWords - 1 # acr 2018-01-15 number of packet words following the header

      ## ACR 2018-03-15 AT IHEP: BEGIN ADDED UDP_DATA_DESTINATION_IPADDR AND UDP_DATA_DESTINATION_IPPORT; GEMROC_CMD_DAQ_Num_of_params = 13 # acr 2018-01-15
      # self.cmd_header = header_tag + (self.TARGET_GEMROC_ID << 16) + gemroc_cmd_tag + gemroc_cmd_word_count
      self.cmd_header = header_tag + (self.TARGET_GEMROC_ID << 16) + gemroc_cmd_tag + ((self.UDP_DATA_DESTINATION_IPADDR & 0xFF)<<8) + gemroc_cmd_word_count
      #self.cmd_word0 = ((self.number_of_repetitions & 0x3FF) << 16) + ((self.gemroc_cmd_code & 0xF) << 11) + ((self.target_TCAM_ID & 0x3) << 8) + ((self.to_ALL_TCAM_enable & 0x1) << 6)
      self.cmd_word0 = ((self.UDP_DATA_DESTINATION_IPPORT & 0xF)<<26) + ((self.number_of_repetitions & 0x3FF) << 16) + ((self.gemroc_cmd_code & 0xF) << 11) + ((self.target_TCAM_ID & 0x3) << 8) + ((self.to_ALL_TCAM_enable & 0x1) << 6)
      ## ACR 2018-03-15 AT IHEP: END ADDED UDP_DATA_DESTINATION_IPADDR AND UDP_DATA_DESTINATION_IPPORT; GEMROC_CMD_DAQ_Num_of_params = 13 # acr 2018-01-15

      #self.cmd_word3 = ((self.L1_latency & 0x3FF) << 20) + ((self.Periodic_TP_EN_pattern & 0xF) << 16) + (self.L1_win_upper_edge_offset & 0xFFFF)
      self.cmd_word3 = ((self.L1_TM_xtrct_start_latency & 0x3FF) << 20) + ((self.TP_width & 0xF) << 16) + (self.L1_win_upper_edge_offset & 0xFFFF)
      #self.cmd_word2 = ((self.L1_period  & 0x3FF) << 20) + ((self.Periodic_TP_EN_pattern  & 0xF) << 16) + (self.L1_win_lower_edge_offset & 0xFFFF)
      self.cmd_word2 = ((self.L1_period  & 0x3FF) << 20) + ((self.Dbg_functions_ctrl_bits_HiNibble  & 0xF) << 16) + (self.L1_win_lower_edge_offset & 0xFFFF)
      # acr 2018-04-24 self.cmd_word1 = ((self.TP_period & 0x3FF) << 20) + ((self.Periodic_TP_EN_pattern & 0xF) << 16) + ((self.TL_nTM_ACQ & 0x1) << 11) + ((self.AUTO_L1_EN_pattern & 0x1) << 10) + ((self.AUTO_TP_EN_pattern & 0x1) << 9) + ((self.TP_Pos_nNeg & 0x1) << 8)  + (self.EN_TM_TCAM_pattern & 0xFF)
      self.cmd_word1 = ((self.TP_period & 0x3FF) << 20) + ((self.Periodic_TP_EN_pattern & 0xF) << 16) + ((self.Dbg_functions_ctrl_bits_LoNibble & 0xF) << 12) + ((self.TL_nTM_ACQ & 0x1) << 11) + ((self.AUTO_L1_EN_bit & 0x1) << 10) + ((self.AUTO_TP_EN_bit & 0x1) << 9) + ((self.TP_Pos_nNeg & 0x1) << 8)  + (self.EN_TM_TCAM_pattern & 0xFF)
      self.command_words = [ self.cmd_header,
                             self.cmd_word3,
                             self.cmd_word2,
                             self.cmd_word1,
                             self.cmd_word0
                              ]

   def __del__(self):
      class_name = self.__class__.__name__
      #print class_name, "gemroc_cmd_DAQ_settings destroyed"

   def cmd_words_array_size(self):
      return len(self.command_words)

   def print_command_words(self):
      for i in range (0, len(self.command_words)):
         print '%08X'% self.command_words[i]

   def set_target_GEMROC (self, GEMROC_ID_param):
      self.TARGET_GEMROC_ID = GEMROC_ID_param & 0x1F
      self.cmd_header = (self.cmd_header & 0xFF00FFFF) + (self.TARGET_GEMROC_ID << 16)

   def set_target_TCAM_ID(self, target_TA_param, to_ALL_TCAM_EN_param):
      self.target_TCAM_ID = target_TA_param & 0x3
      self.to_ALL_TCAM_enable = to_ALL_TCAM_EN_param & 0x1

   def set_TP_width(self, target_TP_width_param): # acr 2017-09-28
      self.TP_width = target_TP_width_param & 0xF

   def set_TP_period(self, TP_period_param): # acr 2017-09-28
      self.TP_period = TP_period_param & 0x3FF

   def set_AUTO_TP_EN_bit(self, target_AUTO_TP_EN_param): #acr 2018-11-02 updated # acr 2017-10-03
      self.AUTO_TP_EN_bit = target_AUTO_TP_EN_param & 0x1

   def set_AUTO_L1_EN_bit(self, target_AUTO_L1_EN_param): #acr 2018-11-02 defined
      self.AUTO_L1_EN_bit = target_AUTO_L1_EN_param & 0x1

   def set_Periodic_TP_EN_pattern(self, Periodic_TP_EN_pattern_param): # acr 2017-10-03
      self.Periodic_TP_EN_pattern = Periodic_TP_EN_pattern_param & 0xF

   # acr 2018-07-11 BEGIN new functions added
   # Dbg_functions_ctrl_bits_U8[7] <-> roc_ctl_port[19] <-> RESERVED
   # Dbg_functions_ctrl_bits_U8[6] <-> roc_ctl_port[18] <-> RESERVED
   # Dbg_functions_ctrl_bits_U8[5] <-> roc_ctl_port[17] <-> Tpulse_generation_w_L1Chk_enable
   # Dbg_functions_ctrl_bits_U8[4] <-> roc_ctl_port[16] <-> Periodic_L1_EN_bit
   def set_Dbg_functions_ctrl_bits_HiNibble(self, Dbg_functions_ctrl_bits_Hi_param): # acr 2018-07-11
       self.Dbg_functions_ctrl_bits_HiNibble = Dbg_functions_ctrl_bits_Hi_param & 0xF
   def get_Dbg_functions_ctrl_bits_HiNibble(self):
      return self.Dbg_functions_ctrl_bits_HiNibble
   # Dbg_functions_ctrl_bits_U8[3] <-> aux_ctrl_port_out[17] <-> Enable_DAQPause_Until_First_Trigger      acr 2018-04-24 DAQPause will have effect only if this bit allows it
   # Dbg_functions_ctrl_bits_U8[2] <-> aux_ctrl_port_out[16] <-> DAQPause_Set                             acr 2018-04-24 DAQPause will be removed by the first trigger received
   # Dbg_functions_ctrl_bits_U8[1] <-> aux_ctrl_port_out[15] <-> Tpulse_generation_w_ext_trigger_enable
   # Dbg_functions_ctrl_bits_U8[0] <-> aux_ctrl_port_out[14] <-> EXT_nINT_B3clk
   def set_Dbg_functions_ctrl_bits_LoNibble(self, Dbg_functions_ctrl_bits_Lo_param): # acr 2018-07-11
       self.Dbg_functions_ctrl_bits_LoNibble = Dbg_functions_ctrl_bits_Lo_param & 0xF
   def get_Dbg_functions_ctrl_bits_LoNibble(self):
      return self.Dbg_functions_ctrl_bits_LoNibble
   ##   def set_Periodic_L1_En_bit(self, Periodic_L1_EN_param): # acr 2018-07-11
   ##       self.Dbg_functions_ctrl_bits_HiNibble &= ~(0x1 << 0)
   ##       self.Dbg_functions_ctrl_bits_HiNibble |= ( (Periodic_L1_EN_param & 0x1) << 0 )
   ##   def set_Tpulse_gen_w_L1Chk_enable(self, Tpulse_gen_w_L1Chk_enable_param): # acr 2018-07-11
   ##       self.Dbg_functions_ctrl_bits_HiNibble &= ~(0x1 << 1)
   ##       self.Dbg_functions_ctrl_bits_HiNibble |= ( (Periodic_L1_EN_param & 0x1) << 1 )
   ##
   ##   def set_Tpulse_gen_w_L1Chk_enable(self, Tpulse_gen_w_L1Chk_enable_param): # acr 2018-07-11
   ##       self.Dbg_functions_ctrl_bits_HiNibble &= ~(0x1 << 1)
   ##       self.Dbg_functions_ctrl_bits_HiNibble |= ( (Periodic_L1_EN_param & 0x1) << 1 )
   def set_L1_Lat_TM_Win_in_B3Ck_cycles(self, L1_lat_B3clk_param, TM_window_in_B3clk_param): #acr 2018-07-11
       L1_lat_TIGER_clk_param = L1_lat_B3clk_param * 4          # default 358 <-> 8.6us
       TM_window_TIGER_clk_param = TM_window_in_B3clk_param * 4 # default  66 <-> 1.6us
       L1_win_upper_edge_offset_Tiger_clk = int( L1_lat_TIGER_clk_param - (TM_window_TIGER_clk_param / 2) )
       L1_win_lower_edge_offset_Tiger_clk = int( L1_lat_TIGER_clk_param + (TM_window_TIGER_clk_param / 2) )
       self.L1_win_upper_edge_offset = L1_win_upper_edge_offset_Tiger_clk
       self.L1_win_lower_edge_offset = L1_win_lower_edge_offset_Tiger_clk
       self.L1_TM_xtrct_start_latency = L1_lat_B3clk_param
   # acr 2018-07-11 END new functions added

   def set_TL_nTM_ACQ(self, TL_nTM_ACQ_param): # acr 2017-10-03
      self.TL_nTM_ACQ = TL_nTM_ACQ_param & 0x1

   def set_EN_TM_TCAM_pattern(self, EN_TM_TCAM_pattern_param): # acr 2017-11-15
      self.EN_TM_TCAM_pattern = EN_TM_TCAM_pattern_param & 0xFF

   def set_TP_Pos_nNeg(self, TP_Pos_nNeg_param): # acr 2017-10-03
      self.TP_Pos_nNeg = TP_Pos_nNeg_param & 0x1

   def set_gemroc_cmd_code(self, command_string_param,num_of_rep="Default"):
      if num_of_rep!="Default":
         self.DAQ_config_dict["number_of_repetitions"]=num_of_rep
      self.command_string = command_string_param
      for i in range (0, len(self.command_list)):
         if (self.command_string == self.command_list[i]):
            self.gemroc_cmd_code = i

## acr 2018-01-15 updated definition: zero all setting when it's a 'CMD_GEMROC_DAQ_CFG_RD' ( = 2 ) or
   def update_command_words_dict(self):
       if ( ((self.gemroc_cmd_code & 0xF) != 0x0) and ((self.gemroc_cmd_code & 0xF) != 0x1) ):
           self.cmd_header &= ~(0xFF << 8)
           self.cmd_word3  = 0
           self.cmd_word2  = 0
           self.cmd_word1  = 0
           self.cmd_word0 = ((self.DAQ_config_dict["number_of_repetitions"] & 0x3FF) << 16) + ((self.gemroc_cmd_code & 0xF) << 11) + ((self.DAQ_config_dict["target_TCAM_ID"] & 0x3) << 8) + ((self.DAQ_config_dict["TO_ALL_TCAM_EN"] & 0x1) << 6)
       else:
           Dbg_functions_ctrl_bits_HiNibble= ((self.DAQ_config_dict["B3Clk_sim_en"]& 0x1) << 2)+ ((self.DAQ_config_dict["Tpulse_generation_w_L1Chk_enable"] &0x1 )<<1) +((self.DAQ_config_dict["Periodic_L1En"] &0x1 )<<0)
           Dbg_functions_ctrl_bits_LoNibble=((self.DAQ_config_dict["Enable_DAQPause_Until_First_Trigger"] &0x1)<<3 ) +((self.DAQ_config_dict["DAQPause_Set"] &0x1 )<<2)+((self.DAQ_config_dict["Tpulse_generation_w_ext_trigger_enable"] &0x1 )<<1) +((self.DAQ_config_dict["EXT_nINT_B3clk"] & 0x1 )<<0)
           self.cmd_header &= ~(0xFF << 8)
           self.cmd_header += ((self.DAQ_config_dict["UDP_DATA_DESTINATION_IPADDR"] & 0xFF)<<8)
           self.cmd_word3 = ((self.DAQ_config_dict["Simulated_L1_latency"] & 0x3FF) << 20) + ((self.DAQ_config_dict["TP_width"] & 0xF) << 16) + (self.DAQ_config_dict["L1_scan_window_UPPER_edge"] & 0xFFFF)
           self.cmd_word2 = ((self.DAQ_config_dict["L1_period_simulated"]  & 0x3FF) << 20) + ((self.DAQ_config_dict["B3Clk_sim_en"]& 0x1) << 18)+((self.DAQ_config_dict["Tpulse_generation_w_L1Chk_enable"] &0x1 )<<17) +((self.DAQ_config_dict["Periodic_L1En"] &0x1 )<<16) + (self.DAQ_config_dict["L1_scan_window_LOWER_edge"] & 0xFFFF)
           self.cmd_word1 = ((self.DAQ_config_dict["TP_period"] & 0x3FF) << 20) + ((self.DAQ_config_dict["Periodic_TP_EN_pattern"] & 0xF) << 16) +((self.DAQ_config_dict["Enable_DAQPause_Until_First_Trigger"] &0x1)<<15 ) +((self.DAQ_config_dict["DAQPause_Set"] &0x1 )<<14)+((self.DAQ_config_dict["Tpulse_generation_w_ext_trigger_enable"] &0x1 )<<13) +((self.DAQ_config_dict["EXT_nINT_B3clk"] & 0x1 )<<12)+ ((self.DAQ_config_dict["TL_nTM_ACQ"] & 0x1) << 11) + ((self.DAQ_config_dict["AUTO_L1_EN"] & 0x1) << 10) + ((self.DAQ_config_dict["AUTO_TP_EN"] & 0x1) << 9) + ((self.DAQ_config_dict["TP_Pos_nNeg"] & 0x1) << 8)  + (self.DAQ_config_dict["EN_TM_TCAM_pattern"] & 0xFF)
           self.cmd_word0 = ((self.DAQ_config_dict["UDP_DATA_DESTINATION_IPPORT"] & 0xF)<<26) + ((self.DAQ_config_dict["number_of_repetitions"] & 0x3FF) << 16) + ((self.gemroc_cmd_code & 0xF) << 11) + ((self.DAQ_config_dict["target_TCAM_ID"] & 0x3) << 8 )+ ((self.DAQ_config_dict["TO_ALL_TCAM_EN"] & 0x1) << 6)
           # self.cmd_word0 = ((self.UDP_DATA_DESTINATION_IPPORT & 0xF) << 26) + ((self.number_of_repetitions & 0x3FF) << 16) + ((self.gemroc_cmd_code & 0xF) << 11) + ((self.target_TCAM_ID & 0x3) << 8) + ((self.to_ALL_TCAM_enable & 0x1) << 6)

       self.command_words = [ self.cmd_header,
                             self.cmd_word3,
                             self.cmd_word2,
                             self.cmd_word1,
                             self.cmd_word0
                             ]

   def update_command_words(self):

       if ( ((self.gemroc_cmd_code & 0xF) != 0x0) and ((self.gemroc_cmd_code & 0xF) != 0x1) ):
           self.cmd_header &= ~(0xFF << 8)
           self.cmd_word3  = 0
           self.cmd_word2  = 0
           self.cmd_word1  = 0
           self.cmd_word0 = ((self.number_of_repetitions & 0x3FF) << 16) + ((self.gemroc_cmd_code & 0xF) << 11) + ((self.target_TCAM_ID & 0x3) << 8) + ((self.to_ALL_TCAM_enable & 0x1) << 6)
       else:
           self.cmd_header &= ~(0xFF << 8)
           self.cmd_header += ((self.UDP_DATA_DESTINATION_IPADDR & 0xFF)<<8)
           self.cmd_word3 = ((self.L1_TM_xtrct_start_latency & 0x3FF) << 20) + ((self.TP_width & 0xF) << 16) + (self.L1_win_upper_edge_offset & 0xFFFF)

           # acr 2018-07-11 BEGIN
           # self.cmd_word2 = ((self.L1_period  & 0x3FF) << 20) + ((self.Dbg_functions_ctrl_bits_HiNibble  & 0xF) << 16) + (self.L1_win_lower_edge_offset & 0xFFFF)
           # self.cmd_word1 = ((self.TP_period & 0x3FF) << 20) + ((self.Periodic_TP_EN_pattern & 0xF) << 16) + ((self.Dbg_functions_ctrl_bits_U8 & 0xF) << 12) + ((self.TL_nTM_ACQ & 0x1) << 11) + ((self.AUTO_L1_EN_pattern & 0x1) << 10) + ((self.AUTO_TP_EN_pattern & 0x1) << 9) + ((self.TP_Pos_nNeg & 0x1) << 8)  + (self.EN_TM_TCAM_pattern & 0xFF)
           self.cmd_word2 = ((self.L1_period  & 0x3FF) << 20) + ((self.Dbg_functions_ctrl_bits_HiNibble  & 0xF) << 16) + (self.L1_win_lower_edge_offset & 0xFFFF)
           self.cmd_word1 = ((self.TP_period & 0x3FF) << 20) + ((self.Periodic_TP_EN_pattern & 0xF) << 16) + ((self.Dbg_functions_ctrl_bits_LoNibble & 0xF) << 12) + ((self.TL_nTM_ACQ & 0x1) << 11) + ((self.AUTO_L1_EN_bit & 0x1) << 10) + ((self.AUTO_TP_EN_bit & 0x1) << 9) + ((self.TP_Pos_nNeg & 0x1) << 8)  + (self.EN_TM_TCAM_pattern & 0xFF)
           # acr 2018-07-11 END
           self.cmd_word0 = ((self.UDP_DATA_DESTINATION_IPPORT & 0xF)<<26) + ((self.number_of_repetitions & 0x3FF) << 16) + ((self.gemroc_cmd_code & 0xF) << 11) + ((self.target_TCAM_ID & 0x3) << 8) + ((self.to_ALL_TCAM_enable & 0x1) << 6)
       self.command_words = [ self.cmd_header,
                             self.cmd_word3,
                             self.cmd_word2,
                             self.cmd_word1,
                             self.cmd_word0
                             ]

   def extract_parameters_from_UDP_packet(self):
      print ( "\n DATA_DESTINATION_IPadr  = %X %d")     % ( ((self.cmd_header >>  8) &  0xFF) , ((self.cmd_header >>  8) &  0xFF) )
      print ( "\n DATA_DESTINATION_IPport = %X %d")     % ( ((self.cmd_word0 >> 26) &  0xF)   , ((self.cmd_word0 >> 26) &  0xF) )
      print ( "\n L1_TM_xtrct_start_latency = %X %d")                  % ( ((self.cmd_word3 >> 20) &  0x3FF) , ((self.cmd_word3 >> 20) &  0x3FF) )
      print ( "\n L1_win_upper_edge_offset = %X %d")   % ( ((self.cmd_word3 >> 0)  &  0xFFFF), ((self.cmd_word3 >> 0)  &  0xFFFF) )
      print ( "\n L1_win_lower_edge_offset = %X %d")   % ( ((self.cmd_word2 >> 0)  &  0xFFFF), ((self.cmd_word2 >> 0)  &  0xFFFF) )
      print ( "\n L1_period = %X %d")                   % ( ((self.cmd_word2 >> 20) &  0x3FF) , ((self.cmd_word2 >> 20) &  0x3FF) )
      print ( "\n TP_period = %X %d")                   % ( ((self.cmd_word1 >> 20)  &  0x3FF), ((self.cmd_word1 >> 20)  &  0x3FF) )
      print ( "\n TP_width = %X %d")                    % ( ((self.cmd_word3 >> 16) &  0xF)   , ((self.cmd_word3 >> 16) &  0xF) )
      print ( "\n Periodic_TP_EN_pattern = %X %d")      % ( ((self.cmd_word1 >> 16)  &  0xF)  , ((self.cmd_word1 >> 16)  &  0xF) )
      print ( "\n Dbg_functions_ctrl_bits_HiNibble = %X %d")    % ( ((self.cmd_word2 >> 16) &  0xF)   , ((self.cmd_word2 >> 16) &  0xF) )
      print ( "\n Dbg_functions_ctrl_bits_LoNibble = %X %d")    % ( ((self.cmd_word1 >> 12) &  0xF)   , ((self.cmd_word1 >> 12) &  0xF) )
      print ( "\n TL_nTM_ACQ = %X %d")                  % ( ((self.cmd_word1 >> 11)  &  0x1)  , ((self.cmd_word1 >> 11)  &  0x1) )
      print ( "\n AUTO_L1_EN_bit = %X %d")          % ( ((self.cmd_word1 >> 10)  &  0x1)  , ((self.cmd_word1 >> 10)  &  0x1) )
      print ( "\n AUTO_TP_EN_bit = %X %d")          % ( ((self.cmd_word1 >>  9)  &  0x1)  , ((self.cmd_word1 >>  9)  &  0x1) )
      print ( "\n TP_Pos_nNeg = %X %d")                 % ( ((self.cmd_word1 >>  8)  &  0x1)  , ((self.cmd_word1 >>  8)  &  0x1) )
      print ( "\n EN_TM_TCAM_pattern = %X %d")          % ( ((self.cmd_word1 >>  0)  &  0xFF) , ((self.cmd_word1 >>  0)  &  0xFF) )
      print ( "\n number_of_repetitions = %X %d")       % ( ((self.cmd_word0 >> 16)  & 0x3FF)  , ((self.cmd_word0 >> 16)  & 0x3FF) )
      print ( "\n target_TCAM_ID = %X %d")              % ( ((self.cmd_word0 >>  8)  &  0x3)  , ((self.cmd_word0 >>  8)  &  0x3) )
      print ( "\n to_ALL_TCAM_enable = %X %d")          % ( ((self.cmd_word0 >>  6)  &  0x1)  , ((self.cmd_word0 >>  6)  &  0x1) )
