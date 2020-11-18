import GEM_OFFLINE_classes
filename=raw_input("Insert file name:")
GEM5=GEM_OFFLINE_classes.reader(0)

GEM5.read_bin(filename, True)
GEM5.write_txt(filename)


fig0,axarray0=GEM5.create_rate_plot()
fig0.canvas.draw()
command=(raw_input("Press enter to exit"))
print ("FINE")
