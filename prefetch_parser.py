# Windows 10 Prefetch parser python 3+

import struct
import binascii
import os
import os.path
import sys
import time
import csv
from datetime import datetime, timedelta
from XPRESS_decompress import *

def dt_from_win32_ts(timestamp):
    WIN32_EPOCH = datetime(1601, 1, 1)
    return WIN32_EPOCH + timedelta(microseconds=timestamp // 10, hours=9)

path = sys.argv[1]
filename_list = os.listdir(path)

f = open('result.csv', 'w', encoding='utf-8', newline='')
wr = csv.writer(f)
wr.writerow(["Filename", "Created_Time", "Modified_Time", "Last_Run_Time", "Run_Count"])

for filename in filename_list:
    if filename.endswith('.pf'):
        data = decompress(path+"/"+filename)
        prefetch_version = struct.unpack_from("<L", data)[0]
        if prefetch_version == 30:
            prefetch_file_size = struct.unpack_from("<L", data[12:])[0]
            Last_Run_Time = dt_from_win32_ts(struct.unpack_from("<Q", data[0x80:])[0]).strftime('%Y:%m:%d %H:%M:%S.%f')
            Created_time = datetime.fromtimestamp(os.path.getctime(path+"/"+filename)).strftime('%Y:%m:%d %H:%M:%S.%f')
            Modified_time = datetime.fromtimestamp(os.path.getmtime(path+"/"+filename)).strftime('%Y:%m:%d %H:%M:%S.%f')
            Run_Count =  struct.unpack_from("<L", data[0xD0:])[0]
            FileNameInfoOffset = struct.unpack_from("<L", data[0x64:])[0]
            FileNameInfoSize = struct.unpack_from("<L", data[0x68:])[0]
            load_file = binascii.hexlify(bytes(data[FileNameInfoOffset:FileNameInfoOffset+FileNameInfoSize])).decode("utf-8").split("0000")
            load_file = [i.replace("00","") for i in load_file]

            wr.writerow([filename, Created_time, Modified_time, Last_Run_Time, Run_Count])
            print("[*] Filename : " + filename)
            print("[*] Created_time : " + str(Created_time))
            print("[*] Modified_time : " + str(Modified_time))
            print("[*] Last_Run_Time : " + str(Last_Run_Time))
            print("[*] Run_Count : " + str(Run_Count))
            print("[***] Load_file_list")

            for i in load_file:
                if i == "00":
                    break
                try:
                    data = binascii.unhexlify(i).decode("utf-8")
                    print(data)
                except:
                    print(i) ## (Odd String Error) ??
                    

f.close()
