import GEM_OFFLINE_classes
import sys
if len(sys.argv)!=3:
    path=raw_input("Insert path:")
    binary=raw_input("Binary :")

else:
    path = sys.argv[1]
    binary = int(sys.argv[2])
GEM5=GEM_OFFLINE_classes.reader(0)

GEM5.write_txt_TM_folder(path,binary)
GEM5.write_txt_TL_folder(path)

