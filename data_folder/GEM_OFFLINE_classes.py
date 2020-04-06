import binascii
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os
import glob



class reader:
    def __init__(self, GEMROC_ID):
        self.GEMROC_ID = GEMROC_ID
        self.thr_scan_matrix = np.zeros((8, 64))  # Tiger,Channel
        self.thr_scan_frames = np.ones(8)
        self.thr_scan_rate = np.zeros((8, 64))

    def __del__(self):
        print ("bye")

    def read_bin(self, path, frameword_check=False):
        self.thr_scan_matrix = np.zeros((8, 64))  # Tiger,Channel
        self.thr_scan_frames = np.ones(8)
        self.thr_scan_rate = np.zeros((8, 64))
        statinfo = os.stat(path)
        last_framecount = np.zeros(8)
        first_frameword = np.zeros(8)
        print ("size={}\n".format(statinfo.st_size))
        with open(path, 'rb') as f, open(path + "_missing_framewords", 'w') as fmiss:
            for i in range(0, int(statinfo.st_size / 8)):
                data = f.read(8)
                hexdata = binascii.hexlify(data)

                for x in range(0, len(hexdata) - 1, 16):
                    int_x = 0
                    for b in range(7, 0, -1):
                        hex_to_int = (int(hexdata[x + b * 2], 16)) * 16 + int(hexdata[x + b * 2 + 1], 16)
                        int_x = (int_x + hex_to_int) << 8

                    hex_to_int = (int(hexdata[x], 16)) * 16 + int(hexdata[x + 1], 16)
                    int_x = (int_x + hex_to_int)

                    if (((int_x & 0xFF00000000000000) >> 59) == 0x04):  # It's a framword

                        self.thr_scan_frames[(int_x >> 56) & 0x7] = self.thr_scan_frames[(int_x >> 56) & 0x7] + 1

                        this_framecount = ((int_x >> 15) & 0xFFFF)
                        this_tiger = ((int_x >> 56) & 0x7)

                        if frameword_check:
                            if first_frameword[this_tiger] == 0:
                                last_framecount[this_tiger] = this_framecount
                                first_frameword[this_tiger] = 1
                            else:
                                if this_framecount == 0xffff:
                                    first_frameword[this_tiger] = 0
                                else:
                                    for F in range(int(last_framecount[this_tiger]), int(this_framecount)):
                                        if last_framecount[this_tiger] + 1 == this_framecount:
                                            last_framecount[this_tiger] = this_framecount
                                            break
                                        else:
                                            print ("Frameword {} from Tiger {} missing".format(hex(F + 1), this_tiger))
                                            fmiss.write("Frameword {} from Tiger {} missing\n".format(hex(F + 1), this_tiger))
                                            last_framecount[this_tiger] = last_framecount[this_tiger] + 1

                    if (((int_x & 0xFF00000000000000) >> 59) == 0x00):
                        self.thr_scan_matrix[(int_x >> 56) & 0x7, int(int_x >> 48) & 0x3F] = self.thr_scan_matrix[(int_x >> 56) & 0x7, int(int_x >> 48) & 0x3F] + 1

                    # with open ("out.txt", 'a') as ff:
                    # ff.write("{}\n".format(raw))

    def write_txt(self, path,outfile="out.txt"):
        statinfo = os.stat(path)
        f = open("out.txt", 'w')
        f.close()

        with open(path, 'rb') as f:
            for i in range(0, int(statinfo.st_size / 8)):
                data = f.read(8)
                hexdata = binascii.hexlify(data)
                string= "{:064b}".format(int(hexdata,16))
                raw_raw="{} \n".format(string)
                print (string)
                inverted=[]
                for i in range (8,0,-1):
                    inverted.append(string[(i-1)*8:i*8])
                string_inv="".join(inverted)
                int_x = int(string_inv,2)
                raw = "{:064b}  ".format(int_x)


                if (((int_x & 0xFF00000000000000) >> 59) == 0x04):  # It's a frameword
                    s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'HB: ' + 'Framecount: %08X ' % (
                            (int_x >> 15) & 0xFFFF) + 'SEUcount: %08X\n' % (int_x & 0x7FFF)

                if (((int_x & 0xFF00000000000000) >> 59) == 0x08):
                    s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'CW: ' + 'ChID: %02X ' % (
                            (int_x >> 24) & 0x3F) + ' CounterWord: %016X\n' % (int_x & 0x00FFFFFF)
                if (((int_x & 0xFF00000000000000) >> 59) == 0x00):
                    s = 'TIGER ' + '%01X: ' % ((int_x >> 56) & 0x7) + 'EW: ' + 'ChID: %02X ' % (
                            (int_x >> 48) & 0x3F) + 'tacID: %01X ' % ((int_x >> 46) & 0x3) + 'Tcoarse: %04X ' % (
                                (int_x >> 30) & 0xFFFF) + 'Ecoarse: %03X ' % (
                                (int_x >> 20) & 0x3FF) + 'Tfine: %03X ' % ((int_x >> 10) & 0x3FF) + 'Efine: %03X \n' % (
                                int_x & 0x3FF)
                    self.thr_scan_matrix[(int_x >> 56) & 0x7, int(int_x >> 48) & 0x3F] = self.thr_scan_matrix[(int_x >> 56) & 0x7, int(int_x >> 48) & 0x3F] + 1
                with open(outfile, 'a') as ff:
                    ff.write("{} {}     {}".format(raw_raw,raw,s))
    def write_txt_TM(self, path,outfile="out.txt", binary=0):

        LOCAL_L1_TIMESTAMP = 0
        HITCOUNT = 0
        BUFSIZE = 4096
        FEB_index = 0
        statinfo = os.stat(path)
        f = open("out.txt", 'w')
        f.close()
        previous_L1_TS = 0
        L1_TS_abs_diff = 0
        with open(path, 'rb') as f, open(outfile, 'w') as out_file:
            for i in range(0, int(statinfo.st_size / 8)):
                data = f.read(8)
                hexdata = binascii.hexlify(data)
                string = "{:064b}".format(int(hexdata, 16))
                inverted = []
                for i in range(8, 0, -1):
                    inverted.append(string[(i - 1) * 8:i * 8])
                string_inv = "".join(inverted)
                int_x = int(string_inv, 2)
                raw = "{:064b}  ".format(int_x)
                s = '%016X \n' % int_x
                    # acr 2018-06-25 out_file.write(s)

                ## comment this block to avoid parsing
                ##acr 2017-11-16        if (((int_x & 0xFF00000000000000)>>56) == 0x20):
                if (((int_x & 0xE000000000000000) >> 61) == 0x6):
                    LOCAL_L1_COUNT_31_6 = int_x >> 32 & 0x3FFFFFF
                    LOCAL_L1_COUNT_5_0 = int_x >> 24 & 0x3F
                    LOCAL_L1_COUNT = (LOCAL_L1_COUNT_31_6 << 6) + LOCAL_L1_COUNT_5_0
                    LOCAL_L1_TIMESTAMP = int_x & 0xFFFF
                    HITCOUNT = (int_x >> 16) & 0xFF
                    if (((int_x & 0xFFFF) - previous_L1_TS) > 0):
                        L1_TS_abs_diff = ((int_x & 0xFFFF) - previous_L1_TS)
                    else:
                        L1_TS_abs_diff = 65536 + ((int_x & 0xFFFF) - previous_L1_TS)
                    s = 'HEADER :  ' + 'STATUS BIT[2:0]: %01X: ' % ((int_x >> 58) & 0x7) + 'LOCAL L1 COUNT: %08X ' % (LOCAL_L1_COUNT) + 'HitCount: %02X ' % ((int_x >> 16) & 0xFF) + 'LOCAL L1 TIMESTAMP: %04X; ' % (int_x & 0xFFFF) + 'Diff w.r.t. previous L1_TS: %04f us\n' % (
                                L1_TS_abs_diff * 6 / 1000)
                    previous_L1_TS = (int_x & 0xFFFF)
                    # s = 'HEADER :  ' + 'STATUS BIT[2:0]: %01X: '%((int_x >> 58)& 0x7) + 'LOCAL L1 COUNT: %08X '%( LOCAL_L1_COUNT ) + 'HitCount: %02X '%((int_x >> 16) & 0xFF) + 'LOCAL L1 TIMESTAMP: %04X\n'%(int_x & 0xFFFF)
                if (((int_x & 0xE000000000000000) >> 61) == 0x7):
                    s = 'TRAILER: ' + 'LOCAL L1  FRAMENUM [23:0]: %06X: ' % ((int_x >> 37) & 0xFFFFFF) + 'GEMROC_ID: %02X ' % ((int_x >> 32) & 0x1F) + 'TIGER_ID: %01X ' % ((int_x >> 27) & 0x7) + 'LOCAL L1 COUNT[2:0]: %01X ' % (
                                (int_x >> 24) & 0x7) + 'LAST COUNT WORD FROM TIGER:CH_ID[5:0]: %02X ' % ((int_x >> 18) & 0x3F) + 'LAST COUNT WORD FROM TIGER: DATA[17:0]: %05X \n' % (int_x & 0x3FFFF)
                if (((int_x & 0xC000000000000000) >> 62) == 0x0):
                    LOCAL_L1_TS_minus_TIGER_COARSE_TS = LOCAL_L1_TIMESTAMP - ((int_x >> 32) & 0xFFFF)
                    s = 'DATA   : TIGER: %01X ' % ((int_x >> 59) & 0x7) + 'L1_TS - TIGERCOARSE_TS: %d ' % (LOCAL_L1_TS_minus_TIGER_COARSE_TS) + 'LAST TIGER FRAME NUM[2:0]: %01X ' % ((int_x >> 56) & 0x7) + 'TIGER DATA: ChID [base10]: %d ' % ((int_x >> 50) & 0x3F) + 'tacID: %01X ' % (
                                (int_x >> 48) & 0x3) + 'Tcoarse: %04X ' % ((int_x >> 32) & 0xFFFF) + 'Ecoarse: %03X ' % ((int_x >> 20) & 0x3FF) + 'Tfine: %03X ' % ((int_x >> 10) & 0x3FF) + 'Efine: {} \n' .format(int_x & 0x3FF)
                if (((int_x & 0xF000000000000000) >> 60) == 0x4):
                    s = 'UDP_SEQNO: ' + 'GEMROC_ID: %02X ' % ((int_x >> 52) & 0x1F) + 'UDP_SEQNO_U48: %012X' % (((int_x >> 32) & 0xFFFFF) + ((int_x >> 0) & 0xFFFFFFF)) + "  " \
                                                                                                                                                                          "STATUS BIT[5:3]:{}\n\n".format((int_x>>57)&0x7)
                if binary==1:
                    out_file.write(raw)
                out_file.write(s)

            print ('finished writing file')
    def  write_txt_TM_folder(self, path,binary=0):
        for data_file in glob.glob(path+"/*TM*.dat"):
            print (data_file)
            self.write_txt_TM(data_file, outfile=data_file+"out.txt",binary=binary)

    def  write_txt_TL_folder(self, path):
        for data_file in glob.glob(path+"/*TL*.dat"):
            print (data_file)
            self.write_txt(data_file, outfile=data_file+"out.txt")

    def create_rate_plot(self):
        plt.ion()
        for i in range(0, 8):
            self.thr_scan_rate[i, :] = (self.thr_scan_matrix[i, :] / self.thr_scan_frames[i]) * (1 / 0.0002048)
        thr_scan_copy = self.thr_scan_rate
        fig = plt.figure(figsize=(8, 8))
        gs = gridspec.GridSpec(nrows=3, ncols=3)  # , height_ratios=[1, 1, 2])

        ax0 = fig.add_subplot(gs[0, 0])
        ax0.bar(np.arange(0, 64), thr_scan_copy[0, :])
        ax0.set_title('GEMROC {}, TIGER {}'.format(self.GEMROC_ID, 0))
        ax0.set_xlabel('Channel')
        ax0.set_ylabel('Rate [Hz]')

        ax1 = fig.add_subplot(gs[0, 1])
        ax1.bar(np.arange(0, 64), thr_scan_copy[1, :])
        ax1.set_title('GEMROC {}, TIGER {}'.format(self.GEMROC_ID, 1))
        ax1.set_xlabel('Channel')
        ax1.set_ylabel('Rate [Hz]')

        ax2 = fig.add_subplot(gs[1, 0])
        ax2.bar(np.arange(0, 64), thr_scan_copy[2, :])
        ax2.set_title('GEMROC {}, TIGER {}'.format(self.GEMROC_ID, 2))
        ax2.set_xlabel('Channel')
        ax2.set_ylabel('Rate [Hz]')

        ax3 = fig.add_subplot(gs[1, 1])
        ax3.bar(np.arange(0, 64), thr_scan_copy[3, :])
        ax3.set_title('GEMROC {}, TIGER {}'.format(self.GEMROC_ID, 3))
        ax3.set_xlabel('Channel')
        ax3.set_ylabel('Rate [Hz]')

        ax4 = fig.add_subplot(gs[2, 0])
        ax4.bar(np.arange(0, 64), thr_scan_copy[4, :])
        ax4.set_title('GEMROC {}, TIGER {}'.format(self.GEMROC_ID, 4))
        ax4.set_xlabel('Channel')
        ax4.set_ylabel('Rate [Hz]')

        ax5 = fig.add_subplot(gs[2, 1])
        ax5.bar(np.arange(0, 64), thr_scan_copy[5, :])
        ax5.set_title('GEMROC {}, TIGER {}'.format(self.GEMROC_ID, 5))
        ax5.set_xlabel('Channel')
        ax5.set_ylabel('Rate [Hz]')

        ax6 = fig.add_subplot(gs[0, 2])
        ax6.bar(np.arange(0, 64), thr_scan_copy[6, :])
        ax6.set_title('GEMROC {}, TIGER {}'.format(self.GEMROC_ID, 6))
        ax6.set_xlabel('Channel')
        ax6.set_ylabel('Rate [Hz]')

        ax7 = fig.add_subplot(gs[1, 2])
        ax7.bar(np.arange(0, 64), thr_scan_copy[7, :])
        ax7.set_title('GEMROC {}, TIGER {}'.format(self.GEMROC_ID, 7))
        ax7.set_xlabel('Channel')
        ax7.set_ylabel('Rate [Hz]')

    def refresh_rate_plot(self, fig, axarray):
        for i in range(0, 8):
            self.thr_scan_rate[i, :] = (self.thr_scan_matrix[i, :] / self.thr_scan_frames[i]) * (1 / 0.0002048)
            thr_scan_copy = self.thr_scan_rate
        for i in range(0, 4):
            axarray[i].bar(np.arange(0, 64), thr_scan_copy[i, :])
