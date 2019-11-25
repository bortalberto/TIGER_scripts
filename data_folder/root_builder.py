import log_loader as lg
import numpy as np
import ROOT
from ROOT import gROOT, AddressOf

class root_builder(lg.measure_8_10):

    def write_root(self):
        gROOT.ProcessLine('struct TreeStruct {\
                   int run_id;\
                   int gemroc_id;\
                   int number_sub;\
                   int tiger_id;\
                   int sub_duration;\
                   int errors;\
                   };')

        rname = "8_10.root"
        rootFile = ROOT.TFile(rname, 'recreate')
        tree = ROOT.TTree('tree', '')
        mystruct = ROOT.TreeStruct()

        for key in ROOT.TreeStruct.__dict__.keys():
            if '__' not in key:
                formstring = '/F'
                if isinstance(mystruct.__getattribute__(key), int):
                    formstring = '/I'
                tree.Branch(key, AddressOf(mystruct, key), key + formstring)

        # for key,matrix in self.dict_8_10.items():
        #     mystruct.run_id = int(key.split("-")[0])
        #     mystruct.sub_run_id = int(key.split("-")[1])
        #     for G in range (0,20):
        #         for T in range(0,8):
        #             mystruct.errors = int(matrix[G][T])
        #             mystruct.gemroc_id = int(G)
        #             mystruct.tiger_id = int(T)
        #             tree.Fill()
        # mystruct.tiger_id = 0




        for key,matrix in self.dict_8_10.items():
            mystruct.run_id = int(key.split("-")[0])
            for G in range (0,20):
                for T in range(0,8):
                    mystruct.errors = int(matrix[G][T])
                    mystruct.tiger_id = int(T)
                    mystruct.gemroc_id = int(G)
                    mystruct.number_sub = int(key.split("-")[1])
                    mystruct.sub_duration = int(self.dict_duration[key])
                    tree.Fill()


        # sub_run_maximizer={}
        # sub_run_max={}
        # errors_dict={}
        #
        # for key,matrix in self.dict_8_10.items():
        #     if int(key.split("-")[0]) not in sub_run_maximizer:
        #         sub_run_maximizer[int(key.split("-")[0])] = []
        #         sub_run_max[int(key.split("-")[0])] = 0
        #         errors_dict[int(key.split("-")[0])] = np.zeros((20))
        #     sub_run_maximizer[int(key.split("-")[0])].append(int(key.split("-")[1]))
        #
        #     for G in range(0,20):
        #         if np.sum(matrix[G])>-1:
        #             # print (np.sum(matrix[G]))
        #             errors_dict[int(key.split("-")[0])][G] += float(np.sum(matrix[[G]]))
        #         else:
        #             sub_run_max[int(key.split("-")[0])] -= 1
        #             break
        # for key,matrix in sub_run_max.items():
        #     sub_run_max[key] = sub_run_max[key] +np.max(sub_run_maximizer[key])+1
        #     print (sub_run_max[key])
        #
        # for key,matrix in sub_run_maximizer.items():
        #     mystruct.run_id = int(key)
        #     for G in range (0,20):
        #         mystruct.errors = float(errors_dict[key][G]/sub_run_max[key])
        #         mystruct.gemroc_id = int(G)
        #         mystruct.number_sub = int(sub_run_max[key])
        #         tree.Fill()


        rootFile.Write()
        rootFile.Close()

if __name__ == "__main__":
    error_importer = root_builder(".")
    error_importer.load_dict_in_pickle()
    error_importer.write_root()