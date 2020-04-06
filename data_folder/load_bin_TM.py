import GEM_OFFLINE_classes
import sys

if len(sys.argv)!=3:
    path=raw_input("Insert file name :")
    binary=raw_input("Binary :")
else:
    path = sys.argv[1]
    binary = sys.argv[2]
GEM5=GEM_OFFLINE_classes.reader(0)

GEM5.write_txt_TM(path, binary=binary)
