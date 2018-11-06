# file: classes_test_functions.py
# author: Angelo Cotta Ramusino INFN Ferrara
# date: 29 Jan 2018
# purpose: to debug TIGER configuration and data acquisition through the GEMROC prototype
# last modifications / additions
import GEM_CONF_classes

# NIOS GCFG words definitions
#//INTERFACE DPRAM word 5
BufferBias_MASK = 0x3
BufferBias_shift = 30
TDCVcasN_MASK = 0xF
TDCVcasN_shift = 26
TDCVcasP_MASK = 0x1F
TDCVcasP_shift = 21
TDCVcasPHyst_MASK = 0x3F
TDCVcasPHyst_shift = 15
DiscFE_Ibias_MASK = 0x3F
DiscFE_Ibias_shift = 9
BiasFE_PpreN_MASK = 0x3F
BiasFE_PpreN_shift = 3
AVcasp_global_MASK = 0x1F
AVcasp_global_RIGHT_shift = 2
#//INTERFACE DPRAM word 4
AVcasp_global_LEFT_shift = 30
unused_134_MASK = 0x1
unused_134_shift = 29
TDCcompVcas_MASK = 0xF
TDCcompVcas_shift = 25
TDCIref_cs_MASK = 0x1F
TDCIref_cs_shift = 20
unused_124to119_MASK = 0x3F
unused_124to119_shift = 14
DiscVcasN_MASK = 0xF
DiscVcasN_shift = 10
IntegVb1_MASK = 0x3F
IntegVb1_shift = 4
unused_108_MASK = 0x1
unused_108_shift = 3
BiasFE_A1_MASK = 0xF
BiasFE_A1_RIGHTshift = 1
#//INTERFACE DPRAM word 3
BiasFE_A1_LEFTshift = 31
Vcasp_Vth_MASK = 0x3F
Vcasp_Vth_shift = 25
TAC_I_LSB_MASK = 0x1F
TAC_I_LSB_shift = 20
TDCcompVbias_MASK = 0x1F
TDCcompVbias_shift = 15
unused_87to77_MASK = 0x7FF
unused_87to77_shift = 4
unused_87to83_MASK = 0x1F
unused_87to83_shift = 10
Vref_Integ_MASK = 0x3F
Vref_Integ_RIGHTshift = 2
Vref_Integ_LEFTshift_mainz = 4
unused_76to73_MASK = 0xF
unused_76to73_shift = 0
##//INTERFACE DPRAM word 2
unused_72to71_MASK = 0x3
unused_72to71_shift = 30
IBiasTPcal_MASK = 0x1F
IBiasTPcal_shift = 25
TP_Vcal_MASK = 0x1F
TP_Vcal_shift = 20
ShaperIbias_MASK = 0xF
ShaperIbias_shift = 16
unused_56_MASK = 0x1
unused_56_shift = 15
IPostamp_MASK = 0x1F
IPostamp_shift = 10
TP_Vcal_ref_MASK = 0x1F
TP_Vcal_ref_shift = 5
Vref_integ_diff_MASK = 0x3F
Vref_integ_diff_RIGHTshift = 1
##//INTERFACE DPRAM word 1
Vref_integ_diff_LEFTshift = 31
unused_39to34_MASK = 0x3F
unused_39to34_shift = 25
Sig_pol_MASK = 0x1
Sig_pol_shift = 24
FE_TPEnable_MASK = 0x1
FE_TPEnable_shift = 23
CompactDataFormat_MASK = 0x1
CompactDataFormat_shift = 22
DataClkDiv_MASK = 0x3
DataClkDiv_shift = 20
TACrefreshPeriod_MASK = 0xF
TACrefreshPeriod_shift = 16
TACrefreshEnable_MASK = 0x1
TACrefreshEnable_shift = 15
CounterPeriod_MASK = 0x7
CounterPeriod_shift = 12
CounterEnable_MASK = 0x1
CounterEnable_shift = 11
StopRampEnable_MASK = 0x3
StopRampEnable_shift = 9
RClkEnable_MASK = 0x1F
RClkEnable_shift = 4
TDCClkdiv_MASK = 0x1
TDCClkdiv_shift = 3
VetoMode_MASK = 0x3F
VetoMode_RIGHTshift = 3
##//INTERFACE DPRAM word 0
VetoMode_LEFTshift = 29
DebugMode_MASK = 0x1
DebugMode_shift = 28
TxMode_MASK = 0x3
TxMode_shift = 26
TxDDR_MASK = 0x1
TxDDR_shift = 25
TxLinks_MASK = 0x3
TxLinks_shift = 23

#NIOSII to TIGER interface DPRAM word 5
##GCFG_168_137 = 	  ((BufferBias & BufferBias_MASK ) << BufferBias_shift) +
##                    ((TDCVcasN & TDCVcasN_MASK ) << TDCVcasN_shift) +
##                    ((TDCVcasP & TDCVcasP_MASK ) << TDCVcasP_shift) +
##                    ((TDCVcasPHyst & TDCVcasPHyst_MASK ) << TDCVcasPHyst_shift) +
##                    ((DiscFE_Ibias & DiscFE_Ibias_MASK ) << DiscFE_Ibias_shift) +
##                    ((BiasFE_PpreN & BiasFE_PpreN_MASK ) << BiasFE_PpreN_shift) +
##                    ((AVcasp_global & AVcasp_global_MASK ) >> AVcasp_global_RIGHT_shift);
#NIOSII to TIGER interface DPRAM word 4
##GCFG_136_105 = ((AVcasp_global & AVcasp_global_MASK ) >> AVcasp_global_LEFT_shift) +
##                ((unused_134_default & unused_134_MASK ) << unused_134_shift) +
##                ((TDCcompVcas & TDCcompVcas_MASK ) << TDCcompVcas_shift) +
##                ((TDCIres & TDCIref_cs_MASK ) << TDCIref_cs_shift) +
##                ((unused_124to119_default & unused_124to119_MASK ) << unused_124to119_shift) +
##                ((DiscVcasN & DiscVcasN_MASK ) << DiscVcasN_shift) +
##                ((IntegVb1 & IntegVb1_MASK ) << IntegVb1_shift) +
##                ((unused_108_default & unused_108_MASK ) << unused_108_shift) +
##                ((BiasFE_A1 & BiasFE_A1_MASK ) >> BiasFE_A1_RIGHTshift);
#NIOSII to TIGER interface DPRAM word 3
##GCFG_104_73 = ((BiasFE_A1 & BiasFE_A1_MASK ) << BiasFE_A1_LEFTshift) +
##                ((Vcasp_Vth & Vcasp_Vth_MASK ) << Vcasp_Vth_shift) +
##                ((TAC_I_LSB & TAC_I_LSB_MASK ) << TAC_I_LSB_shift) +
##                ((TDCcompVbias & TDCcompVbias_MASK ) << TDCcompVbias_shift) +
##                ((unused_87to83_default & unused_87to83_MASK ) << unused_87to83_shift) + // acr 2017-11-16
##                ((Vref_Integ & Vref_Integ_MASK ) << Vref_Integ_LEFTshift_mainz)+ // acr 2017-11-16
##                ((unused_76to73_default & unused_76to73_MASK ) << unused_76to73_shift); // acr 2017-11-16
#NIOSII to TIGER interface DPRAM word 2
##GCFG_72_41 = ((unused_72to71_default & unused_72to71_MASK ) << unused_72to71_shift); // acr 2017-11-16
##                ((IBiasTPcal & IBiasTPcal_MASK ) << IBiasTPcal_shift) +
##                ((TP_Vcal & TP_Vcal_MASK ) << TP_Vcal_shift) +
##                ((ShaperIbias & ShaperIbias_MASK ) << ShaperIbias_shift) +
##                ((unused_56_default & unused_56_MASK ) << unused_56_shift) +
##                ((TP_Vcal_ref & TP_Vcal_ref_MASK ) << TP_Vcal_ref_shift) +
##                ((Vref_integ_diff & Vref_integ_diff_MASK ) >> Vref_integ_diff_RIGHTshift);
#NIOSII to TIGER interface DPRAM word 1
##GCFG_40_9 = ((Vref_integ_diff & Vref_integ_diff_MASK ) << Vref_integ_diff_LEFTshift) +
##            ((unused_39to34_default & unused_39to34_MASK ) << unused_39to34_shift) +
##            ((Sig_pol & Sig_pol_MASK ) << Sig_pol_shift) +
##            ((FE_TPEnable & FE_TPEnable_MASK ) << FE_TPEnable_shift) +
##            ((CompactDataFormat & CompactDataFormat_MASK ) << CompactDataFormat_shift) +
##            ((DataClkDiv & DataClkDiv_MASK ) << DataClkDiv_shift) +
##            ((TACrefreshPeriod & TACrefreshPeriod_MASK ) << TACrefreshPeriod_shift) +
##            ((TACrefreshEnable & TACrefreshEnable_MASK ) << TACrefreshEnable_shift) +
##            ((CounterPeriod & CounterPeriod_MASK ) << CounterPeriod_shift) +
##            ((CounterEnable & CounterEnable_MASK ) << CounterEnable_shift) +
##            ((StopRampEnable & StopRampEnable_MASK ) << StopRampEnable_shift) +
##            ((RClkEnable & RClkEnable_MASK ) << RClkEnable_shift) +
##            ((TDCClkdiv & TDCClkdiv_MASK ) << TDCClkdiv_shift) +
##            ((VetoMode & VetoMode_MASK ) >> VetoMode_RIGHTshift);
#NIOSII to TIGER interface DPRAM word 0
##GCFG_8_m23 = ((VetoMode & VetoMode_MASK ) << VetoMode_LEFTshift) +
##              ((G_DebugMode & DebugMode_MASK ) << DebugMode_shift) +
##              ((TxMode & TxMode_MASK ) << TxMode_shift) +
##            ((TxDDR & TxDDR_MASK ) << TxDDR_shift) +
##            ((TxLinks & TxLinks_MASK ) << TxLinks_shift);

##self.cmd_word10 = ((self.BufferBias & 0x3) << 24) + ((self.TDCVcasN & 0xF) << 16) + ((self.TDCVcasP & 0x1F) << 8) + ((self.TDCVcasPHyst & 0x3F))  
##self.cmd_word9 = ((self.DiscFE_Ibias & 0x3f) << 24) + ((self.BiasFE_PpreN & 0x3F) << 16) + ((self.AVcasp_global & 0x1F) << 8) + ((self.TDCcompVcas & 0xF))  
##self.cmd_word8 = ((self.TDCIref_cs & 0x1f) << 24) + ((self.DiscVcasN & 0xF) << 16) + ((self.IntegVb1 & 0x3F) << 8) + ((self.BiasFE_A1 & 0xF))  
##self.cmd_word7 = ((self.Vcasp_Vth & 0x3f) << 24) + ((self.TAC_I_LSB & 0x1F) << 16) + ((self.TDCcompVbias & 0x1F) << 8) + ((self.Vref_Integ & 0x3F))  
##self.cmd_word6 = ((self.IBiasTPcal & 0x1f) << 24) + ((self.TP_Vcal & 0x1F) << 16) + ((self.ShaperIbias & 0xF) << 8) + ((self.IPostamp & 0x1F))  
##self.cmd_word5 = ((self.TP_Vcal_ref & 0x1f) << 24) + ((self.Vref_integ_diff & 0x3F) << 16) + ((self.Sig_pol & 0x1) << 8) + ((self.FE_TPEnable & 0x1))  
##self.cmd_word4 = ((self.CompactDataFormat & 0x1) << 24) + ((self.DataClkDiv & 0x3) << 16) + ((self.TACrefreshPeriod & 0xf) << 8) + ((self.TACrefreshEnable & 0x1))  
##self.cmd_word3 = ((self.CounterPeriod & 0x7) << 24) + ((self.CounterEnable & 0x1) << 16) + ((self.StopRampEnable & 0x3) << 8) + ((self.RClkEnable & 0x1F))  
##self.cmd_word2 = ((self.TDCClkdiv & 0x1) << 24) + ((self.VetoMode & 0x3F) << 16) + ((self.Ch_DebugMode & 0x1) << 8) + ((self.TxMode & 0x3))  
##self.cmd_word1 = ((self.TxDDR & 0x1) << 24) + ((self.TxLinks & 0x3) << 16)    

# acr 2018-01-25 introduced diagnostic print out of the Global register configuration bit string in GEMROC format
def get_GReg_GEMROC_words( g_reg_setting_object ):
    "diagnostic print out of the Global register configuration bit string in GEMROC format"
    ##for i in range(0,len(g_reg_setting_object.command_words)):
    ##    print (hex(g_reg_setting_object.command_words[i]))
    ##    print (bin(g_reg_setting_object.command_words[i]))
    GCFG_168_137 = 0
    GCFG_168_137 = ( (((g_reg_setting_object.cmd_word10 >> 24) & BufferBias_MASK)    << BufferBias_shift) + \
    (((g_reg_setting_object.cmd_word10 >> 16) & TDCVcasN_MASK)      << TDCVcasN_shift) + \
    (((g_reg_setting_object.cmd_word10 >>  8) & TDCVcasP_MASK)      << TDCVcasP_shift) + \
    (((g_reg_setting_object.cmd_word10 >>  0) & TDCVcasPHyst_MASK)  << TDCVcasPHyst_shift) + \
    (((g_reg_setting_object.cmd_word9  >> 24) & DiscFE_Ibias_MASK)  << DiscFE_Ibias_shift) + \
    (((g_reg_setting_object.cmd_word9  >> 16) & BiasFE_PpreN_MASK)  << BiasFE_PpreN_shift) + \
    (((g_reg_setting_object.cmd_word9  >>  8) & AVcasp_global_MASK) >> AVcasp_global_RIGHT_shift) ) & 0xFFFFFFFF
    GCFG_136_105 = 0
    GCFG_136_105 = ( (((g_reg_setting_object.cmd_word9  >>  8) & AVcasp_global_MASK) << AVcasp_global_LEFT_shift) | \
    (((g_reg_setting_object.cmd_word9  >>  0) & TDCcompVcas_MASK)   << TDCcompVcas_shift) | \
    (((g_reg_setting_object.cmd_word8  >> 24) & TDCIref_cs_MASK)    << TDCIref_cs_shift) | \
    (((g_reg_setting_object.cmd_word8  >> 16) & DiscVcasN_MASK)     << DiscVcasN_shift) | \
    (((g_reg_setting_object.cmd_word8  >>  8) & IntegVb1_MASK)      << IntegVb1_shift) | \
    (((g_reg_setting_object.cmd_word8  >>  0) & BiasFE_A1_MASK)     >> BiasFE_A1_RIGHTshift) ) & 0xFFFFFFFF
    GCFG_104_73 = 0
    GCFG_104_73 = ( (((g_reg_setting_object.cmd_word8  >>  0) & BiasFE_A1_MASK)     << BiasFE_A1_LEFTshift) + \
    (((g_reg_setting_object.cmd_word7  >> 24) & Vcasp_Vth_MASK)     << Vcasp_Vth_shift) + \
    (((g_reg_setting_object.cmd_word7  >> 16) & TAC_I_LSB_MASK)     << TAC_I_LSB_shift) + \
    (((g_reg_setting_object.cmd_word7  >>  8) & TDCcompVbias_MASK)  << TDCcompVbias_shift) + \
    (((g_reg_setting_object.cmd_word7  >>  0) & Vref_Integ_MASK)    << Vref_Integ_LEFTshift_mainz) ) & 0xFFFFFFFF
    GCFG_72_41 = 0
    GCFG_72_41 = ( (((g_reg_setting_object.cmd_word6  >> 24) & IBiasTPcal_MASK)        << IBiasTPcal_shift) + \
    (((g_reg_setting_object.cmd_word6  >> 16) & TP_Vcal_MASK)           << TP_Vcal_shift) + \
    (((g_reg_setting_object.cmd_word6  >>  8) & ShaperIbias_MASK)       << ShaperIbias_shift) + \
    (((g_reg_setting_object.cmd_word6  >>  0) & IPostamp_MASK)          << IPostamp_shift) + \
    (((g_reg_setting_object.cmd_word5  >> 24) & TP_Vcal_ref_MASK)       << TP_Vcal_ref_shift) + \
    (((g_reg_setting_object.cmd_word5  >> 16) & Vref_integ_diff_MASK)   >> Vref_integ_diff_RIGHTshift) ) & 0xFFFFFFFF
    GCFG_40_9  = 0
    GCFG_40_9  = ( (((g_reg_setting_object.cmd_word5  >> 16) & Vref_integ_diff_MASK)   << Vref_integ_diff_LEFTshift) + \
    (((g_reg_setting_object.cmd_word5  >>  8) & Sig_pol_MASK)           << Sig_pol_shift) + \
    (((g_reg_setting_object.cmd_word5  >>  0) & FE_TPEnable_MASK)       << FE_TPEnable_shift) + \
    (((g_reg_setting_object.cmd_word4  >> 24) & CompactDataFormat_MASK) << CompactDataFormat_shift) + \
    (((g_reg_setting_object.cmd_word4  >> 16) & DataClkDiv_MASK)        << DataClkDiv_shift) + \
    (((g_reg_setting_object.cmd_word4  >>  8) & TACrefreshPeriod_MASK)  << TACrefreshPeriod_shift) + \
    (((g_reg_setting_object.cmd_word4  >>  0) & TACrefreshEnable_MASK)  << TACrefreshEnable_shift) + \
    (((g_reg_setting_object.cmd_word3  >> 24) & CounterPeriod_MASK)     << CounterPeriod_shift) + \
    (((g_reg_setting_object.cmd_word3  >> 16) & CounterEnable_MASK)     << CounterEnable_shift) + \
    (((g_reg_setting_object.cmd_word3  >>  8) & StopRampEnable_MASK)    << StopRampEnable_shift) + \
    (((g_reg_setting_object.cmd_word3  >>  0) & RClkEnable_MASK)        << RClkEnable_shift) + \
    (((g_reg_setting_object.cmd_word2  >> 24) & TDCClkdiv_MASK)         << TDCClkdiv_shift) + \
    (((g_reg_setting_object.cmd_word2  >> 16) & VetoMode_MASK)          >> VetoMode_RIGHTshift) ) & 0xFFFFFFFF
    GCFG_8_m23  = 0
    GCFG_8_m23  = ( (((g_reg_setting_object.cmd_word2  >> 16) & VetoMode_MASK)          << VetoMode_LEFTshift) + \
    (((g_reg_setting_object.cmd_word2  >>  8) & DebugMode_MASK)         << DebugMode_shift) + \
    (((g_reg_setting_object.cmd_word2  >>  0) & TxMode_MASK)            << TxMode_shift) + \
    (((g_reg_setting_object.cmd_word1  >> 24) & TxDDR_MASK)             << TxDDR_shift) + \
    (((g_reg_setting_object.cmd_word1  >> 16) & TxLinks_MASK)           << TxLinks_shift) ) & 0xFFFFFFFF
    return (GCFG_168_137, GCFG_136_105, GCFG_104_73, GCFG_72_41, GCFG_40_9, GCFG_8_m23)

# acr 2018-01-25 introduced diagnostic print out of the Global register configuration bit string in GEMROC format
def print_log_GReg_members( g_reg_setting_object, log_enable, log_fname):
    print('\nBufferBias: %d' %g_reg_setting_object.BufferBias)
    print('\nTDCVcasN: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.TDCVcasN, 4)))
    print('\nTDCVcasP: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.TDCVcasP, 5)))
    print('\nTDCVcasPHyst: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.TDCVcasPHyst, 6)))
    print('\nDiscFE_Ibias: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.DiscFE_Ibias, 6)))
    print('\nBiasFE_PpreN: %d' %g_reg_setting_object.BiasFE_PpreN)
    print('\nAVcasp_global: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.AVcasp_global, 5)))
    print('\nTDCcompVcas: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.TDCcompVcas, 4)))
    print('\nTDCIref_cs: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.TDCIref_cs, 5)))
    print('\nDiscVcasN: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.DiscVcasN, 4)))
    print('\nIntegVb1: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.IntegVb1, 6)))
    print('\nBiasFE_A1: %d' %g_reg_setting_object.BiasFE_A1)
    print('\nVcasp_Vth: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.Vcasp_Vth, 6)))
    print('\nTAC_I_LSB: %d' %g_reg_setting_object.TAC_I_LSB)
    print('\nTDCcompVbias: %d' %g_reg_setting_object.TDCcompVbias)
    print('\nVref_Integ: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.Vref_Integ, 6)))
    print('\nIBiasTPcal: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.IBiasTPcal, 5)))
    print('\nTP_Vcal: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.TP_Vcal, 5)))
    print('\nShaperIbias: %d' %g_reg_setting_object.ShaperIbias)
    print('\nIPostamp: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.IPostamp, 5)))
    print('\nTP_Vcal_ref: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.TP_Vcal_ref, 5)))
    print('\nVref_integ_diff: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.Vref_integ_diff, 6)))
    print('\nSig_pol: %d' %g_reg_setting_object.Sig_pol)
    print('\nFE_TPEnable: %d' %g_reg_setting_object.FE_TPEnable)
    print('\nDataClkDiv: %d' %g_reg_setting_object.DataClkDiv)
    print('\nTACrefreshPeriod: %d' %g_reg_setting_object.TACrefreshPeriod)
    print('\nTACrefreshEnable: %d' %g_reg_setting_object.TACrefreshEnable)
    print('\nCounterPeriod: %d' %g_reg_setting_object.CounterPeriod)
    print('\nCounterEnable: %d' %g_reg_setting_object.CounterEnable)
    print('\nStopRampEnable: %d' %g_reg_setting_object.StopRampEnable)
    print('\nRClkEnable: %d' %g_reg_setting_object.RClkEnable)
    print('\nTDCClkdiv: %d' %g_reg_setting_object.TDCClkdiv)
    print('\nVetoMode: %d' %g_reg_setting_object.VetoMode)
    print('\nCh_DebugMode: %d' %g_reg_setting_object.Ch_DebugMode)
    print('\nTxMode: %d' %g_reg_setting_object.TxMode)
    print('\nTxDDR: %d' %g_reg_setting_object.TxDDR)
    print('\nTxLinks: %d' %g_reg_setting_object.TxLinks)
    if (log_enable == 1):
        log_fname.write ('\nBufferBias: %d' %g_reg_setting_object.BufferBias)
        log_fname.write ('\nTDCVcasN: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.TDCVcasN, 4)))
        log_fname.write ('\nTDCVcasP: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.TDCVcasP, 5)))
        log_fname.write ('\nTDCVcasPHyst: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.TDCVcasPHyst, 6)))
        log_fname.write ('\nDiscFE_Ibias: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.DiscFE_Ibias, 6)))
        log_fname.write ('\nBiasFE_PpreN: %d' %g_reg_setting_object.BiasFE_PpreN)
        log_fname.write ('\nAVcasp_global: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.AVcasp_global, 5)))
        log_fname.write ('\nTDCcompVcas: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.TDCcompVcas, 4)))
        log_fname.write ('\nTDCIref_cs: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.TDCIref_cs, 5)))
        log_fname.write ('\nDiscVcasN: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.DiscVcasN, 4)))
        log_fname.write ('\nIntegVb1: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.IntegVb1, 6)))
        log_fname.write ('\nBiasFE_A1: %d' %g_reg_setting_object.BiasFE_A1)
        log_fname.write ('\nVcasp_Vth: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.Vcasp_Vth, 6)))
        log_fname.write ('\nTAC_I_LSB: %d' %g_reg_setting_object.TAC_I_LSB)
        log_fname.write ('\nTDCcompVbias: %d' %g_reg_setting_object.TDCcompVbias)
        log_fname.write ('\nVref_Integ: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.Vref_Integ, 6)))
        log_fname.write ('\nIBiasTPcal: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.IBiasTPcal, 5)))
        log_fname.write ('\nTP_Vcal: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.TP_Vcal, 5)))
        log_fname.write ('\nShaperIbias: %d' %g_reg_setting_object.ShaperIbias)
        log_fname.write ('\nIPostamp: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.IPostamp, 5)))
        log_fname.write ('\nTP_Vcal_ref: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.TP_Vcal_ref, 5)))
        log_fname.write ('\nVref_integ_diff: %d' % (GEM_CONF_classes.swap_order_N_bits(g_reg_setting_object.Vref_integ_diff, 6)))
        log_fname.write ('\nSig_pol: %d' %g_reg_setting_object.Sig_pol)
        log_fname.write ('\nFE_TPEnable: %d' %g_reg_setting_object.FE_TPEnable)
        log_fname.write ('\nDataClkDiv: %d' %g_reg_setting_object.DataClkDiv)
        log_fname.write ('\nTACrefreshPeriod: %d' %g_reg_setting_object.TACrefreshPeriod)
        log_fname.write ('\nTACrefreshEnable: %d' %g_reg_setting_object.TACrefreshEnable)
        log_fname.write ('\nCounterPeriod: %d' %g_reg_setting_object.CounterPeriod)
        log_fname.write ('\nCounterEnable: %d' %g_reg_setting_object.CounterEnable)
        log_fname.write ('\nStopRampEnable: %d' %g_reg_setting_object.StopRampEnable)
        log_fname.write ('\nRClkEnable: %d' %g_reg_setting_object.RClkEnable)
        log_fname.write ('\nTDCClkdiv: %d' %g_reg_setting_object.TDCClkdiv)
        log_fname.write ('\nVetoMode: %d' %g_reg_setting_object.VetoMode)
        log_fname.write ('\nCh_DebugMode: %d' %g_reg_setting_object.Ch_DebugMode)
        log_fname.write ('\nTxMode: %d' %g_reg_setting_object.TxMode)
        log_fname.write ('\nTxDDR: %d' %g_reg_setting_object.TxDDR)
        log_fname.write ('\nTxLinks: %d' %g_reg_setting_object.TxLinks)
           
# ACR 2018-03-01 def print_GReg_bitstring_TO_format( GCFG_word_array ):
def print_GReg_bitstring_TO_format( GCFG_word_array, log_enable, log_fname):
    GCFG_TO_word_array = [0 for i in range(0, 5)] # acr 2018-01-25
    Config_bit_string = 0
    Config_bit_string = GCFG_word_array[0] #GCFG_168_137
    ##print hex(Config_bit_string)
    Config_bit_string = (Config_bit_string << 32) + GCFG_word_array[1] #GCFG_136_105
    ##print hex(Config_bit_string)
    Config_bit_string = (Config_bit_string << 32) + GCFG_word_array[2] #GCFG_104_73
    ##print hex(Config_bit_string)
    Config_bit_string = (Config_bit_string << 32) + GCFG_word_array[3] #GCFG_72_41
    ##print hex(Config_bit_string)
    Config_bit_string = (Config_bit_string << 32) + GCFG_word_array[4] #GCFG_40_9
    ##print hex(Config_bit_string)
    Config_bit_string = (Config_bit_string << 32) + GCFG_word_array[5] #GCFG_8_m23
    ##print hex(Config_bit_string)
    Config_bit_string = Config_bit_string >> 23
    print hex(Config_bit_string)
    if ( log_enable == 1):
        log_fname.write ('\nprint_GReg_bitstring_TO_format output: %s' %(hex(Config_bit_string)))
    
### create an instance of the TIGER global configuration settings object and test its parameters
####    parameter list:
####    TARGET_GEMROC_ID_param = 0, 
####    cfg_filename_param = "default_g_cfg_mainz.txt" 
##g_inst = GEM_CONF_classes_2018.g_reg_settings(30,"default_g_cfg_2018_all_big_endian.txt")
##returned_array = get_GReg_GEMROC_words( g_inst )
####for i in range (0, len(returned_array)):
####    print "%08X" %returned_array[i]
##print '\nGCFG_168_137: ' + "%08X" %returned_array[0]
##print '\nGCFG_136_105: ' + "%08X" %returned_array[1]
##print '\nGCFG_104_73:  ' + "%08X" %returned_array[2]
##print '\nGCFG_72_41:   ' + "%08X" %returned_array[3]
##print '\nGCFG_40_9:    ' + "%08X" %returned_array[4]
##print '\nGCFG_8_m23:   ' + "%08X" %returned_array[5]    
##print_GReg_bitstring_TO_format(returned_array)
##g_inst.print_command_words()
###g_inst.extract_parameters_from_UDP_packet()
##g_inst.extract_d_parameters_from_UDP_packet()
##


## ***** BEGIN: test channel configuration words in GEMROC format
##//acr 2017-02-21 BEGIN CHCFG parameters of setting words
##//INTERFACE DPRAM CHCFG word 3
DisableHyst_MASK = 0x1
DisableHyst_shift = 31
unused_123to121_MASK = 0x7
unused_123to121_shift = 28
T2Hyst_MASK = 0x7
T2Hyst_shift = 25
T1Hyst_MASK = 0x7
T1Hyst_shift = 22
unused_114to111_MASK = 0xF
unused_114to111_shift = 18
Ch63ObufMSB_MASK = 0x1
Ch63ObufMSB_shift = 17
unused_109_MASK = 0x1
unused_109_shift = 16
TP_disable_FE_MASK = 0x1
TP_disable_FE_shift = 15
TDC_IB_E_MASK = 0xF
TDC_IB_E_shift = 11
TDC_IB_T_MASK = 0xF
TDC_IB_T_shift = 7
unused_99to96_MASK = 0xF
unused_99to96_shift = 3
Integ_MASK = 0x1
Integ_shift = 2
unused_94to93_MASK = 0x3
unused_94to93_shift = 0
##//INTERFACE DPRAM CHCFG word 2
unused_92to91_MASK = 0x3
unused_92to91_shift = 30
PostAmpGain_MASK = 0x3
PostAmpGain_shift = 28
FE_delay_MASK = 0x1F
FE_delay_shift = 23
unused_83to75_MASK = 0x1FF
unused_83to75_shift = 14
Vth_T2_MASK = 0x3F
Vth_T2_shift = 8
Vth_T1_MASK = 0x3F
Vth_T1_shift = 2
unused_62to61_MASK = 0x3
unused_62to61_shift = 0
##//INTERFACE DPRAM CHCFG word 1
unused_60to57_MASK = 0xF
unused_60to57_shift = 28
QTx2Enable_MASK = 0x1
QTx2Enable_shift = 27
unused_55to54_MASK = 0x3
unused_55to54_shift = 25
MaxIntegTime_MASK = 0x7F
MaxIntegTime_shift = 18
MinIntegTime_MASK = 0x7F
MinIntegTime_shift = 11
TriggerBLatched_MASK = 0x1
TriggerBLatched_shift = 10
QdcMode_MASK = 0x1
QdcMode_shift = 9
BranchEnableT_MASK = 0x1
BranchEnableT_shift = 8
BranchEnableEQ_MASK = 0x1
BranchEnableEQ_shift = 7
TriggerMode2B_MASK = 0x7
TriggerMode2B_shift = 4
TriggerMode2Q_MASK = 0x3
TriggerMode2Q_shift = 2
TriggerMode2E_MASK = 0x7
TriggerMode2E_RIGHTshift = 1
##//INTERFACE DPRAM CHCFG word 0
TriggerMode2E_LEFTshift = 31
TriggerMode2T_MASK = 0x3
TriggerMode2T_shift = 29
TACMinAge_MASK = 0x1F
TACMinAge_shift = 24
TACMaxAge_MASK = 0x1F
TACMaxAge_shift = 19
CounterMode_MASK = 0xF
CounterMode_shift = 15
DeadTime_MASK = 0x3F
DeadTime_shift = 9
SyncChainLen_MASK = 0x3
SyncChainLen_shift = 7
Ch_DebugMode_MASK = 0x3
Ch_DebugMode_shift = 5
TriggerMode_MASK = 0x3
TriggerMode_shift = 3

##//INTERFACE DPRAM CHCFG word 3
##CHCFG_124_93 = 0;
##CHCFG_124_93 = 	((DisableHyst & DisableHyst_MASK ) << DisableHyst_shift) +
##                ((T2Hyst & T2Hyst_MASK ) << T2Hyst_shift) +
##                ((T1Hyst & T1Hyst_MASK ) << T1Hyst_shift) +
##                ((Ch63ObufMSB & Ch63ObufMSB_MASK ) << Ch63ObufMSB_shift) +
##                ((TP_disable_FE & TP_disable_FE_MASK ) << TP_disable_FE_shift) +
##                ((TDC_IB_E & TDC_IB_E_MASK ) << TDC_IB_E_shift) +
##                ((TDC_IB_T & TDC_IB_T_MASK ) << TDC_IB_T_shift) +
##                ((Integ & Integ_MASK ) << Integ_shift);
##//INTERFACE DPRAM CHCFG word 2
##CHCFG_92_61 = 0;
##CHCFG_92_61 = 	((PostAmpGain & PostAmpGain_MASK ) << PostAmpGain_shift) +
##                ((FE_delay & FE_delay_MASK ) << FE_delay_shift) +
##                ((Vth_T2 & Vth_T2_MASK ) << Vth_T2_shift) +
##                ((Vth_T1 & Vth_T1_MASK ) << Vth_T1_shift) ;
##//INTERFACE DPRAM CHCFG word 1
##CHCFG_60_29 = 0;
##CHCFG_60_29 = 	((QTx2Enable & QTx2Enable_MASK ) << QTx2Enable_shift) +
##                ((MaxIntegTime & MaxIntegTime_MASK ) << MaxIntegTime_shift) +
##                ((MinIntegTime & MinIntegTime_MASK ) << MinIntegTime_shift) +
##                ((TriggerBLatched & TriggerBLatched_MASK ) << TriggerBLatched_shift) +
##                ((QdcMode & QdcMode_MASK ) << QdcMode_shift) +
##                ((BranchEnableT & BranchEnableT_MASK ) << BranchEnableT_shift) +
##                ((BranchEnableEQ & BranchEnableEQ_MASK ) << BranchEnableEQ_shift) +
##                ((TriggerMode2B & TriggerMode2B_MASK ) << TriggerMode2B_shift) +
##                ((TriggerMode2Q & TriggerMode2Q_MASK ) << TriggerMode2Q_shift) +
##                ((TriggerMode2E & TriggerMode2E_MASK ) << TriggerMode2E_RIGHTshift);
##//INTERFACE DPRAM CHCFG word 0
##CHCFG_28_m3 = 0;
##CHCFG_28_m3 = 	((TriggerMode2E & TriggerMode2E_MASK ) << TriggerMode2E_LEFTshift) +
##                ((TriggerMode2T & TriggerMode2T_MASK ) << TriggerMode2T_shift) +
##                ((TACMinAge & TACMinAge_MASK ) << TACMinAge_shift) +
##                ((TACMaxAge & TACMaxAge_MASK ) << TACMaxAge_shift) +
##                ((CounterMode & CounterMode_MASK ) << CounterMode_shift) +
##                ((DeadTime & DeadTime_MASK ) << DeadTime_shift) +
##                ((SyncChainLen & SyncChainLen_MASK ) << SyncChainLen_shift) +
##                ((Ch_DebugMode & Ch_DebugMode_MASK ) << Ch_DebugMode_shift) +
##                ((TriggerMode & TriggerMode_MASK ) << TriggerMode_shift);

##    self.cmd_word8 = ((self.DisableHyst & 0x1) << 24) + ((self.T2Hyst & 0x7) << 16) + ((self.T1Hyst & 0x7) << 8) + ((self.Ch63ObufMSB & 0x1))  
##    self.cmd_word7 = ((self.TP_disable_FE & 0x1) << 24) + ((self.TDC_IB_E & 0xF) << 16) + ((self.TDC_IB_T & 0xF) << 8) + ((self.Integ & 0x1))  
##    self.cmd_word6 = ((self.PostAmpGain & 0x3) << 24) + ((self.FE_delay & 0x1F) << 16) + ((self.Vth_T2 & 0x3F) << 8) + ((self.Vth_T1 & 0x3F))  
##    self.cmd_word5 = ((self.QTx2Enable & 0x1) << 24) + ((self.MaxIntegTime & 0x7F) << 16) + ((self.MinIntegTime & 0x7F) << 8) + ((self.TriggerBLatched & 0x1))  
##    self.cmd_word4 = ((self.QdcMode & 0x1) << 24) + ((self.BranchEnableT & 0x1) << 16) + ((self.BranchEnableEQ & 0x1) << 8) + ((self.TriggerMode2B & 0x7))  
##    self.cmd_word3 = ((self.TriggerMode2Q & 0x3) << 24) + ((self.TriggerMode2E & 0x7) << 16) + ((self.TriggerMode2T & 0x3) << 8) + ((self.TACMinAge & 0x1F))  
##    self.cmd_word2 = ((self.TACMaxAge & 0x1F) << 24) + ((self.CounterMode & 0xF) << 16) + ((self.DeadTime & 0x3F) << 8) + ((self.SyncChainLen & 0x3))  
##    self.cmd_word1 = ((self.Ch_DebugMode & 0x3) << 24) + ((self.TriggerMode & 0x3) << 16)

# acr 2018-01-25 introduced diagnostic print out of the Channel configuration register configuration bit string in GEMROC format
def get_Ch_CfgReg_GEMROC_words( ch_cfg_reg_setting_object ):
    "diagnostic print out of the Channel configuration register configuration bit string in GEMROC format"
    ##//INTERFACE DPRAM CHCFG word 3
    CHCFG_124_93 = 0;
    CHCFG_124_93 =  (   \
    (((ch_cfg_reg_setting_object.cmd_word8 >> 24) & DisableHyst_MASK)       << DisableHyst_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word8 >> 16) & T2Hyst_MASK)            << T2Hyst_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word8 >>  8) & T1Hyst_MASK)            << T1Hyst_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word8 >>  0) & Ch63ObufMSB_MASK)       << Ch63ObufMSB_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word7 >> 24) & TP_disable_FE_MASK)     << TP_disable_FE_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word7 >> 16) & TDC_IB_E_MASK)          << TDC_IB_E_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word7 >>  8) & TDC_IB_T_MASK)          << TDC_IB_T_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word7 >>  0) & Integ_MASK)             << Integ_shift) )   & 0xFFFFFFFF
    ##//INTERFACE DPRAM CHCFG word 2
    CHCFG_92_61 = 0;
    CHCFG_92_61 =   (   \
    (((ch_cfg_reg_setting_object.cmd_word6 >> 24) & PostAmpGain_MASK)       << PostAmpGain_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word6 >> 16) & FE_delay_MASK)          << FE_delay_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word6 >>  8) & Vth_T2_MASK)            << Vth_T2_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word6 >>  0) & Vth_T1_MASK)            << Vth_T1_shift)    )   & 0xFFFFFFFF
    ##//INTERFACE DPRAM CHCFG word 1
    CHCFG_60_29 = 0;
    CHCFG_60_29 =   (   \
    (((ch_cfg_reg_setting_object.cmd_word5 >> 24) & QTx2Enable_MASK)       << QTx2Enable_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word5 >> 16) & MaxIntegTime_MASK)      << MaxIntegTime_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word5 >>  8) & MinIntegTime_MASK)      << MinIntegTime_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word5 >>  0) & TriggerBLatched_MASK)   << TriggerBLatched_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word4 >> 24) & QdcMode_MASK)           << QdcMode_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word4 >> 16) & BranchEnableT_MASK)     << BranchEnableT_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word4 >>  8) & BranchEnableEQ_MASK)    << BranchEnableEQ_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word4 >>  0) & TriggerMode2B_MASK)     << TriggerMode2B_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word3 >> 24) & TriggerMode2Q_MASK)     << TriggerMode2Q_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word3 >> 16) & TriggerMode2E_MASK)     >> TriggerMode2E_RIGHTshift)    )   & 0xFFFFFFFF
    ##//INTERFACE DPRAM CHCFG word 0
    CHCFG_28_m3 = 0;
    CHCFG_28_m3 =   (   \
    (((ch_cfg_reg_setting_object.cmd_word3 >> 16) & TriggerMode2E_MASK)     << TriggerMode2E_LEFTshift) + \
    (((ch_cfg_reg_setting_object.cmd_word3 >>  8) & TriggerMode2T_MASK)     << TriggerMode2T_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word3 >>  0) & TACMinAge_MASK)         << TACMinAge_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word2 >> 24) & TACMaxAge_MASK)         << TACMaxAge_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word2 >> 16) & CounterMode_MASK)       << CounterMode_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word2 >>  8) & DeadTime_MASK)          << DeadTime_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word2 >>  0) & SyncChainLen_MASK)      << SyncChainLen_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word1 >> 24) & Ch_DebugMode_MASK)      << Ch_DebugMode_shift) + \
    (((ch_cfg_reg_setting_object.cmd_word1 >> 16) & TriggerMode_MASK)       << TriggerMode_shift)    )   & 0xFFFFFFFF
    return (CHCFG_124_93, CHCFG_92_61, CHCFG_60_29, CHCFG_28_m3)

def print_Ch_CfgReg_bitstring_TO_format( ChCFG_word_array ):
    Config_bit_string = 0
    Config_bit_string = ChCFG_word_array[0] #CHCFG_124_93
    print hex(Config_bit_string)
    Config_bit_string = (Config_bit_string << 32) + ChCFG_word_array[1] #CHCFG_92_61
    print hex(Config_bit_string)
    Config_bit_string = (Config_bit_string << 32) + ChCFG_word_array[2] #CHCFG_60_29
    print hex(Config_bit_string)
    Config_bit_string = (Config_bit_string << 32) + ChCFG_word_array[3] #CHCFG_28_m3
    print hex(Config_bit_string)
    Config_bit_string = Config_bit_string >> 3
    print hex(Config_bit_string)
                        
### create an instance of the TIGER global configuration settings object and test its parameters
####    parameter list:
####    TARGET_GEMROC_ID_param = 0, 
####    cfg_filename_param = "default_ch_cfg_2018_all_big_endian.txt" 
##ch_reg_inst = GEM_CONF_classes_2018.ch_reg_settings(30,"default_ch_cfg_2018_all_big_endian.txt")
##returned_array = get_Ch_CfgReg_GEMROC_words( ch_reg_inst )
##for i in range (0, len(returned_array)):
##    print "%08X" %returned_array[i]
##print_Ch_CfgReg_bitstring_TO_format(returned_array)




