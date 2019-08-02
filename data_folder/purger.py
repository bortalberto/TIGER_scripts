import glob2
import sys
import os
OS = sys.platform
if OS == 'win32':
    sep = '\\'
elif OS == 'linux':
    sep = '/'
else:
    print("ERROR: OS {} non compatible".format(OS))
    sys.exit()
for root, dirs, files in os.walk("."):
    sub_dict = {}
    for dat_file, (subrun, GEMROC) in glob2.glob(root+sep+"SubRUN_*_GEMROC_*_TM.dat", with_matches=True, recursive=True):
        try:
            sub_dict[subrun].append(dat_file)
        except KeyError:
            sub_dict[subrun]=[]
            sub_dict[subrun].append(dat_file)

    for sub_run in sub_dict.keys():
        for sub_file in sub_dict[sub_run]:
            # print (sub_file)
            # print (os.stat(sub_file).st_size )
            if (os.stat(sub_file).st_size ) ==0:
                for file_to_del in sub_dict[sub_run]:
                    print ("Removing {}, size: {}".format(file_to_del,os.stat(file_to_del).st_size))
                    os.remove(file_to_del)
                break