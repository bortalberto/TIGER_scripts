
import os
# Create target Directory if don't exist and initialize virtual environment
import sys

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")

OS = sys.platform
if OS == 'win32':
	sep = '\\'
elif OS == 'linux':
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
create_folder("conf"+sep+"thr")

for GEMROC in range (0,22):
    create_folder("thr_scan"+ sep +"GEMROC{}".format(GEMROC))
    create_folder("thr_scan"+ sep +"GEMROC{}".format(GEMROC)+sep+"channel_fits")
    create_folder("thr_scan_vth2"+ sep +"GEMROC{}".format(GEMROC))
    create_folder("thr_scan_vth2"+ sep +"GEMROC{}".format(GEMROC)+sep+"channel_fits")
    create_folder("noise_scan"+ sep +"GEMROC{}".format(GEMROC))
    create_folder("noise_scan_save")

create_folder("conf"+sep+"TD_scan_results")

if not os.path.exists("gufi_venv"):
    ans = query_yes_no("Vistual env doens't exist, do you want to create one?")
    if ans:
        print("Creating virtual env")
        os.system("python3.8 -m venv gufi_venv && . gufi_venv/bin/activate && pip install -r requirements.txt")
os.system("chmod +x GUFI.sh")
