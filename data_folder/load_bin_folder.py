import GEM_OFFLINE_classes
path=raw_input("Insert path:")
GEM5=GEM_OFFLINE_classes.reader(0)

GEM5.write_txt_TM_folder(path)
GEM5.write_txt_TL_folder(path)


command=(raw_input("Press enter to exit"))
print "FINE"
