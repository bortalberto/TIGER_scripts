import GEM_OFFLINE_classes
import sys
if len(sys.argv)!=2:
    path=raw_input("Insert path:")
else:
    path = sys.argv[1]
GEM5=GEM_OFFLINE_classes.reader(0)

GEM5.write_txt_TM_folder(path)
GEM5.write_txt_TL_folder(path)

