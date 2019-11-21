import numpy as np
import time
import sys
import array
import pickle
import ROOT
from ROOT import gROOT, AddressOf

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


class reader:
    def write_root(self, NUM):
        path = "noise.n"
        gROOT.ProcessLine('struct TreeStruct {\
                int layer_id;\
                int gemroc_id;\
                int tiger_id;\
                float noise_lvl;\
                int channel_id;\
                float variance;\
                };')

        rname = path.replace(".n", ".root")

        rootFile = ROOT.TFile(rname, 'recreate')
        tree = ROOT.TTree('tree', '')
        mystruct = ROOT.TreeStruct()

        for key in ROOT.TreeStruct.__dict__.keys():
            if '__' not in key:
                formstring = '/F'
                if isinstance(mystruct.__getattribute__(key), int):
                    formstring = '/I'
                tree.Branch(key, AddressOf(mystruct, key), key + formstring)
        if type(NUM) == tuple:
            first = NUM[0]
            last = NUM[1] + 1
        else:
            first = NUM
            last = NUM + 1
        for G in range(first, last):
            filename = "GEMROC{}".format(G) + sep + "noise.n"
            with open(filename, 'r') as file:
                linee = file.readlines()

            for linea in linee:
                mystruct.gemroc_id = G
                mystruct.tiger_id = int(linea.split()[2].replace("TIG", ""))
                mystruct.channel_id = int(linea.split()[3].replace("CH", ""))
                mystruct.noise_lvl = float(linea.split()[5])
                mystruct.variance = float(linea.split()[7])
                if G < 4:
                    mystruct.layer_id = 1
                elif G < 11:
                    mystruct.layer_id = 2
                else:
                    mystruct.layer_id = 3

                tree.Fill()

        rootFile.Write()
        rootFile.Close()

GEMROC_NUM = (0,20)
filename= sys.argv[1]
filename_noise = "noise.n"

print ("Decoding: \n" + filename)

GEM5 = reader()
GEM5.write_root(GEMROC_NUM)
os.system("mv noise.root ~/Noise_analysis/")
os.chdir("/home/alb/Noise_analysis/")
os.system("root -l convert.cxx")
os.system("mv noise_new.root {}.root".format(filename))
os.system("root -l  'export_noise_Fabio.cxx"+'("{}.root")'.format(filename)+"'")
