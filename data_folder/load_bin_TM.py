import GEM_OFFLINE_classes
filename=raw_input("Insert file name:")
GEM5=GEM_OFFLINE_classes.reader(0)

GEM5.write_txt_TM(filename)

command=(raw_input("Press enter to exit"))
print "FINE"
