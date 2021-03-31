import psutil
import time
import datetime
from threading import Thread
from multiprocessing import Process, Pipe
import configparser
import sys
try:
    from influxdb import InfluxDBClient

    DB = True
except:
    print("Can't find DB library")
    DB = False

OS = sys.platform
if OS == 'win32':
    sep = '\\'
elif OS == 'linux2' or 'linux':
    sep = '/'
config=configparser.ConfigParser()
config.read("conf"+sep+"GUFI.ini")

DB = config["DB"].getboolean("active")

class Database_Manager():
    """
    Class to manage the DB logging and be able to log also from conf_GUI
    """
    def __init__(self, address=config["DB"]["address"], port=8086):
    # def __init__(self, address='127.0.0.1', port=8086):
        self.db_client=InfluxDBClient(host=address, port=port)
        self.db_client.switch_database("GUFI_DB")
        self.last_net_time = 0
        self.last_net_values = {}


    def send_to_db(self, json):
        try:
            self.db_client.write_points(json)
        except Exception as e:
            print("Unable to log in infludb: {}\n json: {}".format(e, json))

    def log_PC_stats(self):
        """
        Log the PC status
        :return:
        """
        perf_field = {
            "CPU_usage": psutil.cpu_percent(),
            "Memory usage": psutil.virtual_memory().percent
        }
        raw_dict = psutil.net_io_counters(True, True)
        key_list = [key for key in raw_dict]
        net_field = {}
        this_net_time = time.time()

        for key in key_list:
            if self.last_net_time != 0:
                speed_rcv_byte = (raw_dict[key].bytes_recv - self.last_net_values[key + "_bytes_recv"]) / (this_net_time - self.last_net_time)
                speed_snd_byte = (raw_dict[key].bytes_sent - self.last_net_values[key + "_bytes_sent"]) / (this_net_time - self.last_net_time)
                speed_rcv_pkts = (raw_dict[key].packets_recv - self.last_net_values[key + "_packets_recv"]) / (this_net_time - self.last_net_time)
                speed_snd_pkts = (raw_dict[key].packets_sent - self.last_net_values[key + "_packets_sent"]) / (this_net_time - self.last_net_time)
                net_field.update({
                                 key + "_speed_bytes_recv": speed_rcv_byte,
                                 key + "_speed_bytes_sent": speed_snd_byte,
                                 key + "_speed_packets_recv": speed_rcv_pkts,
                                 key + "_speed_packets_sent": speed_snd_pkts,
                                 key + "_err_in": raw_dict[key].errin,
                                 key + "_err_out": raw_dict[key].errout,
                                 key + "_drop_in": raw_dict[key].dropin,
                                 key + "_drop_out": raw_dict[key].dropout,
                                 })

            self.last_net_values.update({
                                        key + "_bytes_recv": raw_dict[key].bytes_recv,
                                        key + "_bytes_sent": raw_dict[key].bytes_sent,
                                        key + "_packets_recv": raw_dict[key].packets_recv,
                                        key + "_packets_sent": raw_dict[key].packets_sent
                                        })

        self.last_net_time = this_net_time
        perf_field.update(net_field)
        body = [{
            "measurement": "Online",
            "tags": {
                "type": "PC_status",
            },
            "time": str(datetime.datetime.utcnow()),
            "fields": perf_field,
            "retention_policy": "online_data"
        }]

        self.send_to_db(body)

    def log_IVT_in_DB(self, GEMROC_num, GEM_dict, pipe):
        FEB_to_shut_down=[]
        GEMROC = GEM_dict[GEMROC_num]
        IVT = GEMROC.GEM_COM.save_IVT()

        for FEB in range(0, 4):
            body = [{
                "measurement": "Offline",
                "tags": {
                    "type": "IVT_LOG_FEB",
                    "gemroc": GEMROC.GEM_COM.GEMROC_ID,
                    "FEB": FEB
                },
                "time": str(datetime.datetime.utcnow()),
                "fields":
                    IVT['status']['FEB{}'.format(FEB)]
            }]
            if (IVT['status']['FEB{}'.format(FEB)]["TEMP[degC]"] < 117):
                if IVT['status']['FEB{}'.format(FEB)]["TEMP[degC]"] > 47:
                        if GEMROC_num!="GEMROC 8" and FEB!=1:
                            FEB_to_shut_down.append(FEB)
                if not ((GEMROC.GEM_COM.GEMROC_ID == 8 and FEB in (1, 2)) or (GEMROC.GEM_COM.GEMROC_ID == 12 and FEB in (2, 3))):
                    self.send_to_db(body)
            else:
                print("Rejected IVT value")

        body = [{
            "measurement": "Offline",
            "tags": {
                "type": "IVT_LOG_GEMROC",
                "gemroc": GEMROC.GEM_COM.GEMROC_ID,
            },
            "time": str(datetime.datetime.utcnow()),
            "fields":
                IVT['status']['ROC']

        }]
        pipe.send((GEMROC_num, FEB_to_shut_down))
        pipe.close()
        self.send_to_db(body)

    def log_IVT_in_DB_GEM_COM(self, GEM_COM ):
        """
        Call of the IVT LOG with GEM_COM like argoument
        :param GEM_COM:
        :return:
        """
        FEB_to_shut_down=[]
        IVT =GEM_COM.save_IVT()

        for FEB in range(0, 4):
            body = [{
                "measurement": "Offline",
                "tags": {
                    "type": "IVT_LOG_FEB",
                    "gemroc": GEM_COM.GEMROC_ID,
                    "FEB": FEB
                },
                "time": str(datetime.datetime.utcnow()),
                "fields":
                    IVT['status']['FEB{}'.format(FEB)]
            }]
            if (IVT['status']['FEB{}'.format(FEB)]["TEMP[degC]"] < 117):
                if IVT['status']['FEB{}'.format(FEB)]["TEMP[degC]"] > 47:
                        if GEM_COM.GEMROC_ID !=8 and FEB!=1:
                            FEB_to_shut_down.append(FEB)
                if not ((GEM_COM.GEMROC_ID == 8 and FEB in (1, 2)) or (GEM_COM.GEMROC_ID == 12 and FEB in (2, 3))):
                    self.send_to_db(body)
            else:
                print("Rejected IVT value")

        body = [{
            "measurement": "Offline",
            "tags": {
                "type": "IVT_LOG_GEMROC",
                "gemroc": GEM_COM.GEMROC_ID,
            },
            "time": str(datetime.datetime.utcnow()),
            "fields":
                IVT['status']['ROC']

        }]
        self.send_to_db(body)
        if GEM_COM.GEMROC_ID == 3 or GEM_COM.GEMROC_ID == 7:
            self.log_PC_stats()


    def log_ivt_caller(self, dict):
        """Process caller for LOG_IVT"""
        process_list_2 = []
        pipe_list_2 = []
        for number, GEMROC in dict.items():
            pipe_in, pipe_out = Pipe()
            p = Process(target=self.log_IVT_in_DB, args=(number, dict, pipe_in))
            pipe_list_2.append(pipe_out)
            process_list_2.append(p)
            p.start()
            time.sleep(0.05)

        for process, pipe_out in zip(process_list_2, pipe_list_2):
            try:
                process.join(timeout=2)
                gem_number, FEBs_to_off = pipe_out.recv()
                if len(FEBs_to_off) > 0:
                    for FEB in FEBs_to_off:
                        pass
                        self.shut_down_FEB(dict[gem_number].GEM_COM, FEB)
            except Exception as e:
                print("IVT logger controller timeout: {}".format(e))

    def send_810b_error_to_DB(self, GEM_dict, error_dict):
        """
        Log the error GEMROC status in DB
        :return:
        """
        for GEMROC in GEM_dict.keys():
            body = [{
                "measurement": "Offline",
                "tags": {
                    "type": "8_10_b_errors",
                    "gemroc": GEMROC.split(" ")[1],
                    "tiger": -1
                },
                "time": str(datetime.datetime.utcnow()),
                "fields": {
                }
            }]
            for T in range(0, 8):
                body[0]["tags"]["tiger"] = T
                if error_dict["{} TIGER {}".format(GEMROC, T)]["text"] != "-----":
                    body[0]["fields"]["8_10_errors"] = int(error_dict["{} TIGER {}".format(GEMROC, T)]["text"])
                else:
                    body[0]["fields"]["8_10_errors"] = 0
                self.send_to_db(body)
                time.sleep(0.01)
    #
    # def shut_down_FEB(self, gemcom, num, logfile):
    #     pwr_pattern=gemcom.gemroc_LV_XX.FEB_PWR_EN_pattern
    #     pwr_pattern = pwr_pattern & ~(1 << num)
    #     print (pwr_pattern)
    #     print("SHUT DOWN FEB {}, GEMROC{}".format(num,gemcom.GEMROC_ID))
    #     self.write_in_log(logfile,"SHUT DOWN FEB {}, GEMROC{}".format(num,gemcom.GEMROC_ID))
    #     gemcom.FEBPwrEnPattern_set(pwr_pattern)

    def write_in_log(self, logfile, text):
        """
        Just to write on log
        :param text:
        :return:
        """
        with open(logfile, 'a') as f:
            f.write(time.ctime() + " -- " + text + "\n")

    def shut_down_FEB(self, gemcom, num):
        pwr_pattern=gemcom.gemroc_LV_XX.FEB_PWR_EN_pattern
        pwr_pattern = pwr_pattern & ~(1 << num)
        print (pwr_pattern)
        print("SHUT DOWN FEB {}, GEMROC{}".format(num,gemcom.GEMROC_ID))
        gemcom.FEBPwrEnPattern_set(pwr_pattern)

    def __del__(self):
        self.db_client.close()
        return 0


class Thread_handler_IVT(Thread):


    def __init__(self, menu_caller):
        Thread.__init__(self)
        self.menu_caller=menu_caller
        self.Database_Manager=Database_Manager()
        print ("thread created")
        self.logging=False
        self.terminator=False

    def run(self):
        last_time=0
        while True:
            if self.terminator:
                return 0
            if (not self.menu_caller.doing_something) and (time.time()-last_time > 7):
                self.logging = True
                last_time=time.time()
                process_list_2 = []
                pipe_list_2 = []
                for number, GEMROC in self.menu_caller.GEMROC_reading_dict.items():
                        pipe_in, pipe_out = Pipe()
                        p = Process(target=self.Database_Manager.log_IVT_in_DB, args=(number, self.menu_caller.GEMROC_reading_dict, pipe_in))
                        pipe_list_2.append(pipe_out)
                        process_list_2.append(p)
                        p.start()
                        time.sleep(0.05)
                self.Database_Manager.log_PC_stats()
                for process, pipe_out in zip(process_list_2, pipe_list_2):
                    try:
                        process.join(timeout=2)
                        gem_number, FEBs_to_off = pipe_out.recv()
                        if len(FEBs_to_off) > 0:
                            for FEB in FEBs_to_off:
                                self.Database_Manager.shut_down_FEB(self.menu_caller.GEMROC_reading_dict[gem_number].GEM_COM, FEB)
                    except Exception as e:
                        print("IVT logger controller timeout: {}".format(e))
                self.logging = False
            if self.menu_caller.doing_something:
                last_time=time.time()
            time.sleep(1)

    def __del__(self):
        self.Database_Manager.__del__()
        return 0



class Thread_handler_IVT_std_alone(Thread):
    """
    To handle the logging in standalone mode
    """

    def __init__(self,GEMROC_reading_dict):
        Thread.__init__(self)
        self.Database_Manager=Database_Manager()
        print ("thread created")
        self.logging=False
        self.terminator=False
        self.GEMROC_reading_dict = GEMROC_reading_dict

    def run(self):
        last_time=0
        while True:
            print ("Logging")
            if self.terminator:
                print ("Terminated")
                return 0

            if  (time.time()-last_time > 7):
                self.logging = True
                last_time=time.time()
                process_list_2 = []
                pipe_list_2 = []
                for number, GEMROC in self.GEMROC_reading_dict.items():
                        pipe_in, pipe_out = Pipe()
                        p = Process(target=self.Database_Manager.log_IVT_in_DB, args=(number, self.GEMROC_reading_dict, pipe_in))
                        pipe_list_2.append(pipe_out)
                        process_list_2.append(p)
                        p.start()
                        time.sleep(0.05)
                self.Database_Manager.log_PC_stats()
                for process, pipe_out in zip(process_list_2, pipe_list_2):
                    try:
                        process.join(timeout=2)
                        gem_number, FEBs_to_off = pipe_out.recv()
                        if len(FEBs_to_off) > 0:
                            for FEB in FEBs_to_off:
                                self.Database_Manager.shut_down_FEB(self.GEMROC_reading_dict[gem_number].GEM_COM, FEB)
                    except Exception as e:
                        print("IVT logger controller timeout: {}".format(e))
                self.logging = False
            time.sleep(1)

    def __del__(self):
        self.Database_Manager.__del__()
        return 0