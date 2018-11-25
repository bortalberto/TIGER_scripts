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

OS = sys.platform
if OS == 'win32':
	sep = '\\'
elif OS == 'linux2':
	sep = '/'
else:
	print("ERROR: OS {} non compatible".format(OS))
	sys.exit()

if len(sys.argv) < 3:
    print"\n Provide first and last GEMROC to test or the one to be tested"
    exit()
first=int(sys.argv[1])
last=int(sys.argv[2])+1
FEB_PWR_EN_pattern = 0x0

GEM_COM_list = []
g_inst_list = []
c_inst_list = []
GEM_AN_list = []
configuration_error_list=[]

for G in range(first,last):
    GEM_COM_list.append(COM_class.communication(G, FEB_PWR_EN_pattern))
    default_g_inst_settigs_filename = GEM_COM_list[G-first].conf_folder + sep + "TIGER_def_g_cfg_2018.txt"
    default_c_inst_settigs_filename = GEM_COM_list[G-first].conf_folder + sep+ "TIGER_def_ch_cfg_2018.txt"

    g_inst_list.append(GEM_CONF.g_reg_settings(G, default_g_inst_settigs_filename))
    c_inst_list.append(GEM_CONF.ch_reg_settings(G, default_c_inst_settigs_filename))

    GEM_AN_list.append(AN_CLASS.analisys_conf(GEM_COM_list[G-first],c_inst_list[G-first],g_inst_list[G-first]))

for G in range (first,last):
    print "Turning ON FEBs on GEMROC {}".format(G)
    GEM_COM_list[G-first].FEBPwrEnPattern_set(int(0xff))
    GEM_AN_list[G-first].TIGER_config_test() #Configuration test
    GEM_AN_list[G-first].TIGER_TP_test() #Test pulse reception test
    GEM_AN_list[G-first].TIGER_GEMROC_sync_test()  #Test the GEMROC syncronous reset
    print "Turning OFF febs on GEMROC {}".format(G)
    GEM_COM_list[G-first].FEBPwrEnPattern_set(int(0x0))
