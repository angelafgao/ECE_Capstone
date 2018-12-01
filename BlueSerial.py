#! /usr/bin/python
import serial
import time
import csv
import subprocess
#import numpy as np

def main():

    r = subprocess.call(["sudo", "rfcomm" , "bind", "0", "00:21:13:00:1A:EC"])
    print(r)
    heartrateData = [["irValue", "beatsPerMinute", "averageHR"]]
    print("o")
    accelorometerData = [["ax", "ay", "az"]]
    bluetoothSerial = serial.Serial("/dev/rfcomm0", baudrate = 9600)
    bluetoothSerial.flushInput();
    print("Bluetooth connected")
    start = time.time()
    now = start
    while((now-start) < 60.0):
        try:
            data = bluetoothSerial.readline()
            temp= data.decode("utf-8")
            temp = (temp.strip("\n"))[1:-1]
            temp = temp.split(",")
            if len(temp) == 4: 
                type = temp[0]
                v1 = temp[1]
                v2 = temp[2]
                v3 = temp[3]
                if type == "s":
                   heartrateData.append([v1,v2,v3])
                elif type == "a":
                    accelorometerData.append([v1,v2,v3])
                    #print([v1,v2,v3]);
                now = time.time()
        except serial.SerialException as e:
            bluetoothSerial.close()
            print("error: " + "Got Serial Exception")
            raise e
        except KeyboardInterrupt:
            bluetoothSerial.close()
        except UnicodeDecodeError as ex:
            bluetoothSerial.close()
            print("Got unicode decode error")
            raise ex
    bluetoothSerial.close()
    with open('hc1.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(heartrateData)
    f.close()
    with open('ac1.csv', 'w') as d:
        writer = csv.writer(d)
        writer.writerows(accelorometerData)
    d.close()
    r1 = subprocess.call(["sudo", "rfcomm", "release", "all"])
    print(r1)
    r2 = subprocess.call(["sudo", "rfkill", "list"])
    print(r2)
    #return (heartrateData, accelorometerData)
    return