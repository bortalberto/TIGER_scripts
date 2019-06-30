import numpy as np
import time
import sys
from array import array
import pickle
import ROOT
from ROOT import gROOT, AddressOf
import glob
import sys
import os

OS = sys.platform
if OS == 'win32':
    sep = '\\'
elif OS == 'linux2' or OS == "linux":
    sep = '/'
else:
    print("ERROR: OS {} non compatible".format(OS))
    sys.exit()

class configuration_extractor:

    def __init__(self,conf_folder):
        self.conf_folder = conf_folder

    def extract_thr(self):
        for file in glob.glob(self.conf_folder+sep+"*"+sep+"CONF*.pkl"):
            print ("Found :{}".format(file))
            with open (file, 'rb') as f:
                self.conf_dict = pickle.load(f)
            self._write_root(file)

    def _write_root(self, filename):
        rname = filename.replace(".pkl", ".root")
        rname = rname.replace("CONF", "threshold")

        rootFile = ROOT.TFile(rname, 'recreate')
        conftree = ROOT.TTree('tree', '')

        mapfile = ROOT.TFile.Open("mapping_IHEP.root")
        map_array_x = np.zeros((11,8,64),"int")
        map_array_v = np.zeros((11,8,64),"int")
        for event in mapfile.tree :
            map_array_x[event.gemroc_id][event.SW_FEB_id][event.channel_id]=event.pos_x
            map_array_v[event.gemroc_id][event.SW_FEB_id][event.channel_id]=event.pos_v

        gemroc_id = array( 'i', [ 0 ] )
        conftree.Branch("gemroc_id",gemroc_id,"gemroc_id/I")
        tiger_id = array( 'i', [ 0 ] )
        conftree.Branch("tiger_id",tiger_id,"tiger_id/I")
        channel_id = array( 'i', [ 0 ] )
        conftree.Branch("channel_id",channel_id,"channel_id/I")
        threshold_t = array( 'i', [ 0 ] )
        conftree.Branch("threshold_t",threshold_t,"threshold_t/I")
        threshold_e = array( 'i', [ 0 ] )
        conftree.Branch("threshold_e",threshold_e,"threshold_e/I")
        trigger_mode = array( 'i', [ 0 ] )
        conftree.Branch("trigger_mode",trigger_mode,"trigger_mode/I")
        triggermode2B = array( 'i', [ 0 ] )
        conftree.Branch("triggermode2B",triggermode2B,"triggermode2B/I")
        strip_x = array( 'i', [ 0 ] )
        conftree.Branch("strip_x",strip_x,"strip_x/I")
        strip_v = array( 'i', [ 0 ] )
        conftree.Branch("strip_v",strip_v,"strip_v/I")
        layer_id = array( 'i', [ 0 ] )
        conftree.Branch("layer_id",layer_id,"layer_id/I")


        for GEMROC_key, dict in self.conf_dict.items():
            gemroc_id[0] = int(GEMROC_key.split(" ")[1])
            for TIGER_key, dict2 in dict.items():
                if TIGER_key.split(" ")[0] == "TIGER":
                    tiger_id[0] = int (TIGER_key.split(" ")[1])
                    for channel_key, dict3 in dict2.items():
                        if channel_key.split(" ")[0] == "Ch":
                            channel_id[0] = int(channel_key.split(" ")[1])
                            # print ("{} - {} - {}".format(gemroc_id[0], tiger_id[0], channel_id[0]))
                            threshold_e[0] = dict3["Vth_T2"]
                            threshold_t[0] = dict3["Vth_T1"]
                            trigger_mode[0] = dict3["TriggerMode"]
                            triggermode2B[0] = dict3["TriggerMode2B"]
                            strip_x[0] = map_array_x[gemroc_id[0]][tiger_id[0]][channel_id[0]]
                            strip_v [0] = map_array_v[gemroc_id[0]][tiger_id[0]][channel_id[0]]
                            if gemroc_id[0] < 4:
                                layer_id[0] = 1
                            elif gemroc_id[0] < 11:
                                layer_id[0] = 2
                            else:
                                layer_id[0] = 3
                            conftree.Fill()
        rootFile.Write()
        rootFile.Close()
        print ("Wrote: {}".format(rname))

if __name__ == "__main__":
    conf_elaborator = configuration_extractor("/home/alb/TIGER_scriptsV3/data_folder/")
    conf_elaborator.extract_thr()
