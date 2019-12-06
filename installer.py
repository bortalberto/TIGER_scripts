
import os
# Create target Directory if don't exis
import sys

OS = sys.platform
if OS == 'win32':
	sep = '\\'
elif OS == 'linux2':
	sep = '/'
else:
	print("ERROR: OS {} non compatible".format(OS))
	sys.exit()

def create_folder(dirName):
    if not os.path.exists(dirName):
        os.mkdir(dirName)
        print("Directory ", dirName, " Created ")
    else:
        print("Directory ", dirName, " already exists")

create_folder("log_folder")
create_folder("thr_scan")
create_folder("thr_scan_vth2")

for GEMROC in range (0,22):
    create_folder("thr_scan"+ sep +"GEMROC{}".format(GEMROC))
    create_folder("thr_scan"+ sep +"GEMROC{}".format(GEMROC)+sep+"channel_fits")
    create_folder("thr_scan_vth2"+ sep +"GEMROC{}".format(GEMROC))
    create_folder("thr_scan_vth2"+ sep +"GEMROC{}".format(GEMROC)+sep+"channel_fits")

create_folder("conf"+sep+"TD_scan_results")
