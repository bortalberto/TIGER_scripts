import glob2
import numpy as np
import pickle
import sys

OS = sys.platform
if OS == 'win32':
    sep = '\\'
elif OS == 'linux' or 'linux2':
    sep = '/'
else:
    print("ERROR: OS {} non compatible".format(OS))
    sys.exit()
RUN = 300

class measure_8_10():

    def __init__(self, path):
        self.data_path = path
        self.dict_8_10 = {}
        self.dict_duration = {}

    def run_trough_files(self):
        for acq_log_file, (run, sub_run) in glob2.iglob(self.data_path + sep + "RUN_*" + sep + "ACQ_log_*", with_matches=True, recursive=True):
            if run + "-" + sub_run not in self.dict_8_10:
                self.dict_8_10[run + "-" + sub_run] = self.extract_from_acq_log(acq_log_file)
                self.dict_duration[run + "-" + sub_run] = self.exctract_duration(acq_log_file)

    def exctract_duration(self, log_file):
        """
        Extract subrun duration in secs
        :param log_file:
        :return:
        """
        day_list = ["Sun", "Mon", "Sat", "Tue", "Thu", "Wed", "Fri"]
        try:
            with open(log_file, 'r') as log_file_opened:
                lines = log_file_opened.readlines()
            for line in lines:
                if len(line) > 1:
                    if line.split()[0] in day_list:
                        if "Acquiring" in line:
                            start_time = int(line.split()[2]) * 24 * 60 * 60 + int(line.split()[3].split(":")[0]) * 60 * 60 + int(line.split()[3].split(":")[1]) * 60 + int(line.split()[3].split(":")[2])
                        if "Finished" in line:
                            finish_time = int(line.split()[2]) * 24 * 60 * 60 + int(line.split()[3].split(":")[0]) * 60 * 60 + int(line.split()[3].split(":")[1]) * 60 + int(line.split()[3].split(":")[2])
            return (finish_time - start_time)
        except Exception as E:
            print ("File : {}".format(log_file))
            print (E)
            return 1

    def extract_from_acq_log(self, log_file):
        """
        Extract from each file the information about the 8_10_bit
        :param log_file:
        :return:
        """
        error_matrix = np.zeros((22, 8))
        with open(log_file, 'r') as log_file_opened:
            lines = log_file_opened.readlines()
        for line in lines:
            if "errors since" in line:
                for number, element in enumerate(line.split(" ")):
                    if element == "GEMROC":
                        gemroc = (line.split(" ")[number + 1])

                    if element == "TIGER":
                        tiger = (line.split(" ")[number + 1])

                    if element == "8/10":
                        errors = (line.split(" ")[number - 1])

                # print (gemroc, tiger,errors)
                if int(errors) > error_matrix[int(gemroc)][int(tiger)]:
                    error_matrix[int(gemroc)][int(tiger)] = int(errors)
            if "Timed_out" in line:
                error_matrix[:][:] = -999

        return error_matrix

    def save_dict_in_pickle(self):
        with open("error_log_all_runs", "wb+") as fileout:
            pickle.dump(self.dict_8_10, fileout)
        with open("duration", "wb+") as fileout:
            pickle.dump(self.dict_duration, fileout)

    def load_dict_in_pickle(self):
        with open("error_log_all_runs", "rb") as fileout:
            self.dict_8_10 = pickle.load(fileout)
        with open("duration", "rb") as fileout:
            self.dict_duration = pickle.load(fileout)

    def print_stats(self, min_dur, run):
        error_counters = np.zeros((22, 8))
        run_counter = 0
        for key in self.dict_8_10.keys():
            if int(key.split("-")[0]) == run:
                if self.dict_duration[key] > min_dur:
                    run_counter += 1
                    for G in range(0, 22):
                        for T in range(0, 8):
                            if self.dict_8_10[key][G][T] == 16777215:
                                error_counters[G][T] += 1
        for G in range(0, 22):
            for T in range(0, 8):
                print ("GEMROC {} TIGER {} -- (RUN {})Saturated counter {} times in {} subruns of at least {} seconds. {}%".format(G, T, run, error_counters[G][T], run_counter, min_dur, error_counters[G][T] / run_counter * 100))


    def log_stats(self, min_dur, norm_duration=False):
        run_list =[ key.split("-")[0] for key in self.dict_8_10.keys()]
        for run in run_list:
            error_counters = np.zeros((22, 8))
            run_counter = 0
            duration = 0
            for key in self.dict_8_10.keys():

                if int(key.split("-")[0]) == int(run):
                    if self.dict_duration[key] > min_dur:
                        run_counter += 1
                        duration += self.dict_duration [key]
                        for G in range(0, 22):
                            for T in range(0, 8):
                                if self.dict_8_10[key][G][T] == 16777215:
                                    error_counters[G][T] += 1
            with open ("error_saturation_log"+sep+str(run), "w+") as file:
                for G in range(0, 22):
                    for T in range(0, 8):
                        if norm_duration:
                            file.write("GEMROC {} TIGER {} -- (RUN {})Saturated counter {} times in {}  seconds. Saturation per second = {}\n".format(G, T, run, error_counters[G][T], duration, error_counters[G][T]/duration   ))

                        else:
                            file.write ("GEMROC {} TIGER {} -- (RUN {})Saturated counter {} times in {} subruns of at least {} seconds. {}%\n".format(G, T, run, error_counters[G][T], run_counter, min_dur, error_counters[G][T] / run_counter * 100))
if __name__ == "__main__":
    error_importer = measure_8_10(".")
    error_importer.run_trough_files()
    error_importer.save_dict_in_pickle()
    error_importer.load_dict_in_pickle()
    # error_importer.print_stats(MIN_TIME, RUN)
    error_importer.log_stats(30, True)