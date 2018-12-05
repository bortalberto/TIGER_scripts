# -*- coding: cp1252 -*-
import socket
import string
import binascii

HOST_IP = "192.168.1.200"
#HOST_PORT = 58912+2 ACR 2018-03-23
HOST_PORT = 58880
####FF_PORT => SLV(58880, 16), -- S.C. 2018-03-08: FF_PORT sends data to UDP port group 58880+0..58880+15 (base pattern 0xNNN[0] = 0xE600)
##HOST_PORT = 58880+2




#Total_data_size = 2**24
#Total_data_size = 2**16
Total_data_size = 2**22
BUFSIZE = 4096
FEB_index = 0
data_file = 'FEB%d_data.txt'% FEB_index
bindata_file = 'FEB%d_bin.dat'% FEB_index
out_file = open(data_file, 'w')
binout_file = open(bindata_file, 'wb')

serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSock.settimeout(None)
serverSock.bind((HOST_IP, HOST_PORT))
print 'after bind....'
s=''
Total_Data=0
while Total_Data < Total_data_size :
    data,addr = serverSock.recvfrom(BUFSIZE)
    binout_file.write(data)
    hexdata = binascii.hexlify(data)
    Total_Data += len(data)
    for x in range (0, len(hexdata)-1, 16):
        int_x = 0
        for b in range (7, 0, -1):
            hex_to_int = (int(hexdata[x+b*2],16))*16 + int(hexdata[x+b*2+1],16)
            int_x = (int_x + hex_to_int) << 8
        hex_to_int = (int(hexdata[x],16))*16 + int(hexdata[x+1],16) # acr 2017-11-17 this should fix the problem
        int_x = (int_x + hex_to_int)
        s = '%016X '%int_x
        out_file.write(s)

## comment this block to avoid parsing
##PACKET FORMAT FOR TRIGGER MATCHED DATA FROM GEM-ROC to GEM-DC (for N HITs)                                                                                                
##                  31     30     29     28      27      26          25           24     23     22     21     20     19     18     17     16     15     14     13     12     11     10     9     8     7     6     5     4     3     2     1     0
##Packet Header      1      1     0      L1_HDR_STATUS_BITS          LOCAL L1  COUNT [ 31 : 6 ]---------------------------------------------------------------------------------------------------------------------------------------------------                                                                          
##                   0      0     LOCAL L1  COUNT [ 5 : 0 ]------------------------      COUNT OF MATCHED HIT IN THE PACKET-----------------     LOCAL L1 Timestamp-------------------------------------------------------------------------------                                             
##Hit record         0      0     TIGER_ID--------       LAST TIGER FRAME NUM[ 2:0 ]     TIGER RAW DATA [ 53 : 30 ]-------------------------------------------------------------------------------------------------------------------------------
##                   0      0     TIGER RAW DATA [ 29 : 0 ]---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##Hit record         0      0     TIGER_ID--------       LAST TIGER FRAME NUM[ 2:0 ]     TigerChannelID_U6--------------------     TAC_ID_U2     TCOARSE_U16--------------------------------------------------------------------------------------
##                   0      0     ECOARSE_U10-------------------------------------------------------------------     TFINE_U10--------------------------------------------------------     EFINE_U10----------------------------------------------

##Packet Trailer     1      1     1      LOCAL L1  FRAMENUM [ 23 : 8 ]-------------------------------------------------------------------------------------------     LOCAL L1  FRAMENUM [ 7 : 0 ]------------------     GEMROC_ID----------------            
##                   0      0     TIGER_ID--------       LOCAL L1  COUNT [2 : 0 ]--      LAST COUNT WORD FROM TIGER:CH_ID[5:0]     LAST COUNT WORD FROM TIGER:  DATA[ 17 : 0 ]--------------------------------------------------------------------                                                   
        
##acr 2017-11-16        if (((int_x & 0xFF00000000000000)>>56) == 0x20):
        if (((int_x & 0xE000000000000000)>>61) == 0x6):
            LOCAL_L1_COUNT_31_6 = int_x >> 32 & 0x3FFFFFF
            LOCAL_L1_COUNT_5_0  = int_x >> 24 & 0x3F
            LOCAL_L1_COUNT      = (LOCAL_L1_COUNT_31_6 << 6) + LOCAL_L1_COUNT_5_0
            s = 'HEADER :  ' + 'STATUS BIT[2:0]: %01X: '%((int_x >> 58)& 0x7) + 'LOCAL L1 COUNT: %08X '%( LOCAL_L1_COUNT ) + 'HitCount: %02X '%((int_x >> 16) & 0xFF) + 'LOCAL L1 TIMESTAMP: %04X\n'%(int_x & 0xfFFF)
##acr 2017-11-16        if (((int_x & 0xFF00000000000000)>>56) == 0x20):
        if (((int_x & 0xE000000000000000)>>61) == 0x7):
            s = 'TRAILER: ' + 'LOCAL L1  FRAMENUM [23:0]: %06X: '%((int_x >> 37) & 0xFFFFFF) + 'GEMROC_ID: %02X '%( (int_x >> 32) & 0x1F ) + 'TIGER_ID: %01X '%((int_x >> 27) & 0x7) +'LOCAL L1 COUNT[2:0]: %01X '%((int_x >> 24) & 0x7) + 'LAST COUNT WORD FROM TIGER:CH_ID[5:0]: %02X '%((int_x >> 18) & 0x3F) + 'LAST COUNT WORD FROM TIGER: DATA[17:0]: %05X \n'%(int_x & 0x3FFFF)
#acr 2017-11-16        if (((int_x & 0xFF00000000000000)>>56) == 0x40):
        if (((int_x & 0xC000000000000000)>>62) == 0x0):
            s = 'DATA   : TIGER: %01X '%((int_x >> 59) & 0x7) + 'LAST TIGER FRAME NUM[2:0]: %01X '%((int_x >> 56)& 0x7)+ 'TIGER DATA: ChID: %02X '%((int_x >> 50)& 0x3F)+'tacID: %01X '%((int_x >> 48)& 0x3)+'Tcoarse: %04X '%((int_x >> 32)& 0xFFFF)+'Ecoarse: %03X '%((int_x >> 20)& 0x3FF)+'Tfine: %03X '%((int_x >> 10)& 0x3FF)+'Efine: %03X \n'%(int_x & 0x3FF)
        out_file.write(s)        
##-- field size in bits (56 total):   2      6        2       16         10       10     10
##-- received_tdata                 "10" & ch_ID & tac_ID & tcoarse & ecoarse & tfine & efine
##-- tcoarse(15) should match bit 0 of framecount in the HB FrameWord
##-- received_tdata (53 downto 48); -- channel_id: 6 bits
##-- received_tdata (47 downto 46); -- tac_id: 2 bits
##-- received_tdata (45 downto 30); -- Tcoarse: 16 bits
##-- received_tdata (29 downto 20); -- Ecoarse: 10 bits
##-- received_tdata (19 downto 10); -- Tfine: 10 bits
##-- received_tdata ( 9 downto  0); -- Efine: 10 bits
## comment this block to avoid parsing        

out_file.close()
binout_file.close()
print 'finished writing file'
serverSock.close()
