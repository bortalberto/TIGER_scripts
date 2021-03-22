"""
This program it's made to log the GEMROC metrics without interfer with the main program functionalities
To use it you need another ethernet line connected for this purpose
"""
from lib import DB_classes as DB_classes
import configparser
from sys import platform, exit
from lib import GEM_COM_classes
from threading import Thread
import requests
import time

OS = platform
if OS == 'win32':
    sep = '\\'
elif OS == 'linux2' or 'linux':
    sep = '/'

else:
    print("ERROR: OS {} not compatible".format(OS))
    sep=""
    exit()

# Create the handlers to handle the GEMROC communication
GEMROC_LIST=[0,1,2,3,4,5,6,7,8,9,10,11]
handler_list=[]
for G_N in GEMROC_LIST:
    handler_list.append(GEM_COM_classes.GEMROC_HANDLER(G_N, std_alone_logger=True) )

#Create a dict to handle the handlers
GEMROC_reading_dict={}
for i in range(0, len(handler_list)):
    ID = handler_list[i].GEMROC_ID
    GEMROC_reading_dict["GEMROC {}".format(ID)] = handler_list[i]

#Load the DB configuration
config = configparser.ConfigParser()



auth = requests.auth.HTTPBasicAuth('admin', 'Gr4fana')
url = 'http://localhost:3000/api/alerts'


def stop_DB(IVT_LOG_thread):
    IVT_LOG_thread.terminator = True
    IVT_LOG_thread.__del__()

def start_DB():
    IVT_LOG_thread = DB_classes.Thread_handler_IVT_std_alone(GEMROC_reading_dict)
    IVT_LOG_thread.start()
    return IVT_LOG_thread

def check_temp_allarm_status(IVT_LOG_thread):
    url = 'http://localhost:3000/api/alerts'
    r = requests.get(url=url, auth=auth)
    alerts = r.json()
    for alert in alerts:
        if alert["name"] == "FEB temperature alert" and alert["state"] == "no_data":
                stop_DB(IVT_LOG_thread)
                time.sleep(2)
                start_DB()
                time.sleep(10)
    time.sleep(30)

class check_alarm_thread_handler(Thread):
    """
    To handle the logging in standalone mode
    """

    def __init__(self, IVT_LOG_thread):
        self.IVT_LOG_thread=IVT_LOG_thread
    def run(self):
        check_temp_allarm_status(IVT_LOG_thread)

    def __del__(self):
        return 0

IVT_LOG_thread=start_DB()
check_alarm_thread_handler(IVT_LOG_thread)