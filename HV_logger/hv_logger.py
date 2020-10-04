from influxdb import InfluxDBClient
from os import path, listdir,stat
from configparser import ConfigParser
from datetime import datetime
from influxdb import SeriesHelper
from time import sleep

config=ConfigParser()
config.read("HV_conf.ini")
db_address=config["DB"].get("address")
db_port=config["DB"].getint("port")
data_folder=config["data"].get("folder")
key_list=["I0Set", "V0Set", "VMon", "IMon", "IMonDet","IMonReal", "alarm"]
db_client = InfluxDBClient(host=db_address, port=db_port)
db_client.switch_database("GUFI_DB")

class HVSeriesHelper(SeriesHelper):
    """Instantiate SeriesHelper to write points to the backend."""
    class Meta:
        """Meta class stores time series helper configuration."""

        # The client should be an instance of InfluxDBClient.
        client = db_client

        # The series name must be a string. Add dependent fields/tags
        # in curly brackets.
        series_name = 'HVmeas'

        # Defines all the fields in this time series.
        fields = key_list

        # Defines all the tags for the series.
        tags = ['Electrode','Layer']

        # Defines the number of data points to store prior to writing
        # on the wire.
        bulk_size = 200

        # autocommit must be set to True when using bulk_size
        autocommit = True


def create_list_file(layer):
    file_list = [f for f in listdir(data_folder) if path.isfile(path.join(data_folder, f))]
    file_list = [ f for f in file_list if "Layer{}.txt".format(layer) in f]
    return file_list

def get_last_file(f_list):
    f_list.sort()
    last_f=f_list[-1]
    return data_folder+last_f

def get_number_of_lines(file):
    with open(file,'r') as f:
        if stat(file).st_size>0:
            for i, l in enumerate(f):
                pass
        else:
            return 0
    return i+1

def update_data_layer(layer, old_fname,old_number_lines):
    f_list=create_list_file(layer)
    if len(f_list)==0:
        raise Exception("Can't find any log file")
    f_name=get_last_file(f_list)
    n_lines = get_number_of_lines(f_name)
    if f_name!=old_fname:
        parse_and_send(f_name,n_lines,layer)
        return (f_name,n_lines,n_lines)
    else:
        parse_and_send(f_name,n_lines-old_number_lines,layer)
        return (f_name,n_lines,n_lines-old_number_lines)

def parse_and_send(fname, n_lines,layer):
    with open(fname, 'r') as f:
        line_list=f.readlines()
        line_list=line_list[len(line_list)-n_lines:]
    dict_list=[]
    for thisline in [line for line in line_list if any (key in line for key in key_list)]:
        thisline=thisline.replace(":","")
        elem=thisline.split("\t")
        time=datetime.fromtimestamp(float(elem[1])-2082844800-28800)
        dict_list.append((
            elem[0],
            datetime.isoformat(time),
            # float(elem[1])-2082844800, # converting labview timestamp in epoch
            {"In":float(elem[2]),
            "G3":float(elem[3]),
            "T2":float(elem[4]),
            "G2": float(elem[5]),
            "T1": float(elem[6]),
            "G1": float(elem[7]),
            "Dr": float(elem[8]),
             }))

    for elem in dict_list:
        #     body = [{
        #         "measurement": "HVmeas",
        #         "tags": {
        #             "Electrode": key,
        #             "Layer" : layer
        #         },
        #         "time": elem[1],
        #         "fields": {
        #
        #         }
        #     }]
        #     print (body)
        #     send_to_db(body)

        for key in elem[2]:
                kwargs = {
                    elem[0]:elem[2][key]
                }
                HVSeriesHelper(Electrode=key,Layer=layer,time=elem[1], **kwargs)
    HVSeriesHelper.commit()
    return( fname)

def send_to_db(json):
    try:
        db_client.write_points(json,time_precision='s')
    except Exception as e:
        print("Unable to log in infludb: {}\n json: {}".format(e, json))
if __name__ == "__main__":

    old_filename_lst=["init","init","init"]
    old_line_num_lst=[0,0,0]
    layer_list=[1,2,3]
    while len (layer_list) !=0:
        for num, layer in enumerate(layer_list):
            try:
                old_filename_lst[num],old_line_num_lst[num],logged_lines = update_data_layer(layer,old_filename_lst[num],old_line_num_lst[num])
            except Exception as E:
                print ("Layer {} exception: {}".format(layer,E))
                layer_list.pop(num)
                old_line_num_lst.pop(num)
                old_filename_lst.pop(num)
                print ("L{} dropped".format(layer))

            else:
                print ("Layer {} : logged {} lines from file {}".format(layer, logged_lines, old_filename_lst[num]))

        sleep(10)