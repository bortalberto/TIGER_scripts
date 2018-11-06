from lib import GEM_ACQ_classes as GEM_ACQ

# if len(sys.argv) < 3:
#     print"\n Wrong input: GEM_ACQ argument list: <acq time><number of spill>"
#     exit()
# acq_time=int(sys.argv[1])
# spill=int(sys.argv[2])


GEM1=GEM_ACQ.reader(1)
GEM0=GEM_ACQ.reader(0)

fig1,axarray1=GEM1.create_rate_plot()
#fig0,axarray0=GEM0.create_rate_plot()

while True:
    inp=raw_input("Start spill with enter, write q to exit----->> ")
    if inp=="q":
        break
    else:
            thread_1 = GEM_ACQ.Thread_handler("GEM1",2 , GEM1)
            #thread_0 = GEM_ACQ.Thread_handler("GEM0", 2, GEM0)
            thread_1.start()
            #thread_0.start()
            print("-Acquiring_data-")
            thread_1.join()
            #thread_0.join()
            GEM1.build_hist_and_miss()
            GEM1.refresh_rate_plot(fig1,axarray1)
            #GEM0.build_hist_and_miss()
            #GEM0.refresh_rate_plot(fig0, axarray0)

            fig1.canvas.draw()
            #fig0.canvas.draw()

print "END"




