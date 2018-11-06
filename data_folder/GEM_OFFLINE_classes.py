import binascii
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os

pin_order_X = [[1, 3], [1, 45], [1, 11], [1, 47], [1, 22], [1, 54], [1, 4], [1, 41],
                [1, 12], [1, 43], [1, 23], [1, 33], [1, 19], [1, 39], [1, 15], [1, 37],
                [1, 14], [1, 6], [1, 61], [1, 9], [1, 0], [1, 25], [1, 26], [1, 29],
                [1, 49], [1, 7], [1, 63], [1, 1], [1, 62], [1, 27], [1, 20], [1, 13],
                [1, 51], [1, 31], [1, 28], [1, 35], [1, 16], [1, 57], [1, 56], [1, 53],
                [1, 59], [1, 2], [1, 52], [1, 17], [1, 60], [1, 21], [1, 40], [1, 8],
                [1, 55], [1, 10], [1, 58], [1, 5], [1, 50], [1, 24], [1, 46], [1, 18],
                [1, 44], [1, 30], [1, 48], [1, 32], [1, 36], [0, 58], [1, 42], [0, 13],
                [1, 38], [0, 40], [1, 34], [0, 7], [0, 36], [0, 3], [0, 62], [0, 32],
                [0, 48], [0, 34], [0, 26], [0, 46], [0, 22], [0, 44], [0, 28], [0, 50],
                [0, 24], [0, 43], [0, 20], [0, 59], [0, 14], [0, 56], [0, 61], [0, 53],
                [0, 9], [0, 17], [0, 63], [0, 37], [0, 5], [0, 51], [0, 30], [0, 60],
                [0, 2], [0, 11], [0, 18], [0, 52], [0, 16], [0, 27], [0, 38], [0, 54],
                [0, 0], [0, 49], [0, 42], [0, 55], [0, 39], [0, 19], [0, 15], [0, 25],
                [0, 31], [0, 29], [0, 1], [0, 35], [0, 41], [0, 33], [0, 6], [0, 12],
                [0, 4], [0, 23], [0, 10], [0, 47], [0, 45], [0, 21], [0, 57], [0, 8]]
pin_order_Y = [[3, 3], [3, 45], [3, 11], [3, 47], [3, 22], [3, 54], [3, 4], [3, 41],
                [3, 12], [3, 43], [3, 23], [3, 33], [3, 19], [3, 39], [3, 15], [3, 37],
                [3, 14], [3, 6], [3, 61], [3, 9], [3, 0], [3, 25], [3, 26], [3, 29],
                [3, 49], [3, 7], [3, 63], [3, 1], [3, 62], [3, 27], [3, 20], [3, 13],
                [3, 51], [3, 31], [3, 28], [3, 35], [3, 16], [3, 57], [3, 56], [3, 53],
                [3, 59], [3, 2], [3, 52], [3, 17], [3, 60], [3, 21], [3, 40], [3, 8],
                [3, 55], [3, 10], [3, 58], [3, 5], [3, 50], [3, 24], [3, 46], [3, 18],
                [3, 44], [3, 30], [3, 48], [3, 32], [3, 36], [2, 58], [3, 42], [2, 13],
                [3, 38], [2, 40], [3, 34], [2, 7], [2, 36], [2, 3], [2, 62], [2, 32],
                [2, 48], [2, 34], [2, 26], [2, 46], [2, 22], [2, 44], [2, 28], [2, 50],
                [2, 24], [2, 43], [2, 20], [2, 59], [2, 14], [2, 56], [2, 61], [2, 53],
                [2, 9], [2, 17], [2, 63], [2, 37], [2, 5], [2, 51], [2, 30], [2, 60],
                [2, 2], [2, 11], [2, 18], [2, 52], [2, 16], [2, 27], [2, 38], [2, 54],
                [2, 0], [2, 49], [2, 42], [2, 55], [2, 39], [2, 19], [2, 15], [2, 25],
                [2, 31], [2, 29], [2, 1], [2, 35], [2, 41], [2, 33], [2, 6], [2, 12],
                [2, 4], [2, 23], [2, 10], [2, 47], [2, 45], [2, 21], [2, 57], [2, 8]]



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
                    raw = "{}".format(bin(int_x))

                    hex_to_int = (int(hexdata[x], 16)) * 16 + int(hexdata[x + 1], 16)  # acr 2017-11-17 this should fix the problem
                    int_x = (int_x + hex_to_int)

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
