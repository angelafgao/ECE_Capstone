# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 10:20:32 2018

@author: Angela
"""
import numpy as np
import scipy
import math, csv
import time
import os

# PATH = r"C:\Users\Angela\Documents\CMU\F18\18-500\data_sleep_wake\\"
# FILENAME = "sleep_4.tsv"
PATH = "/home/pi/Desktop"
FILENAME = "/ac1.csv"
THRESHOLD = 200 # THRESHOLD definitely can be greater than 7
SAMPLING_RATE = 65
TIME_SEC = 60

def check_sleep_3D(accData):
    # makes the box filter
    box_width = SAMPLING_RATE * 5 # 5 second box for 20 second thing
    n = accData.size
    signal_width = int(n/3)
    box_filt = [0] * signal_width
    min_ones = int(math.floor(signal_width / 2 - box_width / 2) - 1)
    max_ones = int(math.floor(signal_width / 2 + box_width / 2))
    print(min_ones, max_ones, len(box_filt), signal_width)
    for i in range(min_ones, max_ones):
        box_filt[i] = 1

    # find the fft of the box and signal
    fft_box_filt = np.fft.fft(box_filt)
    is_asleep = [0, 0, 0]
    count = [0, 0, 0]
    for i in range(3):
        signal = accData[:, i]
        fft_signal = np.fft.fft(signal)

        # multiply the signals together
        filt_signal = np.absolute(np.fft.ifft(np.multiply(fft_box_filt, fft_signal)))
        # print(sum(filt_signal)/np.size(filt_signal))
        for j in range(0, len(filt_signal)):
            if filt_signal[j] > THRESHOLD:
                count[i] += 1
        if count[i] < signal_width * 0.07:
            is_asleep[i] = 1
    print(count, THRESHOLD, signal_width*0.07)
    return is_asleep

# acc_x, acc_y, acc_z
def clean_data(data):
    count = 0
    raw_data = []
    for row in data:
        if (count != 0):
            ax, ay, az = row
            ax = float(ax)
            ay = float(ay)
            az = float(az)
            raw_data.append([ax, ay, az])
        count += 1
    
    return np.array(raw_data)

def zero_mean(data):
    n = len(data)
    mean = sum(data)/n
    for i in range(n):
        for j in range(len(data[0])):
            data[i][j] = data[i][j] - mean[j]
    print(mean)
    return data

def plot(xvals, yvals, axis = None, xlabel = None, ylabel = None):
    plt.plot(xvals, yvals)
    if axis != None:
        plt.axis(axis)
    if xlabel != None:
        plt.xlabel(xlabel)
    if ylabel != None:
        plt.ylabel(ylabel)
    plt.show()

def main(data):
    start = time.time()
    accData = clean_data(data)

    print("Data length = " + str(len(accData)))

    # classify each minute of data

    t = check_sleep_3D(accData)
    sleeping = False
    if (sum(t) > 1):
        sleeping = True
    end = time.time()
    print(end - start)
    print("The baby is sleeping is " + str(sleeping))
    return sleeping

