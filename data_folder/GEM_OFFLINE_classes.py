import binascii
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os



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
        with open(path, 'r') as f, open(path + "_missing_framewords", 'w') as fmiss:
            for i in range(0, statinfo.st_size / 8):
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

    def write_txt(self, path):
        statinfo = os.stat(path)
        f = open("out.txt", 'w')
        f.close()

        with open(path, 'r') as f:
            for i in range(0, statinfo.st_size / 8):
                data = f.read(8)
                hexdata = binascii.hexlify(data)

                for x in range(0, len(hexdata) - 1, 16):
                    int_x = 0
                    for b in range(7, 0, -1):
                        hex_to_int = (int(hexdata[x + b * 2], 16)) * 16 + int(hexdata[x + b * 2 + 1], 16)
                        int_x = (int_x + hex_to_int) << 8


                    hex_to_int = (int(hexdata[x], 16)) * 16 + int(hexdata[x + 1], 16)  # acr 2017-11-17 this should fix the problem
                    int_x = (int_x + hex_to_int)
                    raw = "{}".format(hex(int_x))


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

                    with open("out.txt", 'a') as ff:
                        ff.write("{}     {}".format(raw,s))

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

    def ordered_rate_plot(self):
        plt.ion()
        for i in range(0, 8):
            self.thr_scan_rate[i, :] = (self.thr_scan_matrix[i, :] / self.thr_scan_frames[i]) * (1 / 0.0002048)
        thr_scan_copy = self.thr_scan_rate
        fig = plt.figure(figsize=(8, 8))
        gs = gridspec.GridSpec(nrows=1, ncols=1)  # , height_ratios=[1, 1, 2])
        ax0 = fig.add_subplot(gs[0, 0])
        chip,channel = pin_order_X[:]
        ax0.bar(np.arange(0, 128), thr_scan_copy [chip,channel], width=1.0)
        ax0.set_title('GEMROC {}, TIGER {}'.format(self.GEMROC_ID, 0))
        ax0.set_xlabel('Channel')
        ax0.set_ylabel('Rate [Hz]')

        chip=chip+2

        ax1 = fig.add_subplot(gs[0, 1])
        ax1.bar(np.arange(0, 128),  thr_scan_copy[chip,channel], width=1.0)
        ax1.set_title('GEMROC {}, TIGER {}'.format(self.GEMROC_ID, 1))
        ax1.set_xlabel('Channel')
        ax1.set_ylabel('Rate [Hz]')


        plt.tight_layout()

        axarray = [ax0, ax1]
        return fig, axarray

    def refresh_rate_plot(self, fig, axarray):
        for i in range(0, 8):
            self.thr_scan_rate[i, :] = (self.thr_scan_matrix[i, :] / self.thr_scan_frames[i]) * (1 / 0.0002048)
            thr_scan_copy = self.thr_scan_rate
        for i in range(0, 4):
            axarray[i].bar(np.arange(0, 64), thr_scan_copy[i, :])
