# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 10:20:32 2018

@author: Angela
"""
import numpy as np
import scipy
import math, csv
import time
import matplotlib.pyplot as plt

PATH = r"C:\Users\Angela\Documents\CMU\F18\18-500\data_sleep_wake\\"
FILENAME = "sleep_4.tsv"
THRESHOLD = 200 # THRESHOLD definitely can be greater than 7

def check_sleep_3D(accData, sampling_per_sec):
    # makes the box filter
    box_width = sampling_per_sec * 10
    n = accData.size
    signal_width = int(n/3)
    box_filt = [0] * signal_width
    min_ones = int(math.floor(signal_width / 2 - box_width / 2) - 1)
    max_ones = int(math.floor(signal_width / 2 + box_width / 2))
    # print(min_ones, max_ones, len(box_filt), signal_width)
    for i in range(min_ones, max_ones):
        box_filt[i] = 1

    # find the fft of the box and signal
    fft_box_filt = np.fft.fft(box_filt)
    is_asleep = [0, 0, 0]
    for i in range(3):
        signal = accData[:, i]
        fft_signal = np.fft.fft(signal)

        # multiply the signals together
        filt_signal = np.absolute(np.fft.ifft(np.multiply(fft_box_filt, fft_signal)))
        count = 0
        # print(sum(filt_signal)/np.size(filt_signal))
        for j in range(0, len(filt_signal)):
            if filt_signal[j] > THRESHOLD:
                count += 1
        if count < signal_width * 0.07:
            is_asleep[i] = 1
    return is_asleep

def clean_data(path, filename):
    input = path + filename
    with open(input) as f:
        reader = csv.reader(f, delimiter = "\t")
        rawData = []
        count = 0
        for row in reader:
            count += 1
            if (row[0] == str(count)):
                rawData.append(row)
    min_time = int(rawData[0][1])
    max_time = int(rawData[count-1][1])
    time_sec = (max_time - min_time)/1000
    accData = np.empty([count, 3])
    timeData = np.empty(count)
    for i in range(len(rawData)):
        row = rawData[i]
        [counter, timestamp, acc_x, acc_y, acc_z, filename] = row
        timestamp = int(timestamp)
        accData[i] = [float(acc_x), float(acc_y), float(acc_z)]
        timeData[i] = timestamp
    sampling_rate_ms = np.sum(np.subtract(timeData[1:count-1], timeData[0:count-2]))/count
    print("sampling rate ms = " + str(sampling_rate_ms))
    sampling_rate_sec = 1000/sampling_rate_ms
    # sampling_per_sec = 40
    accData_wo_nan = np.nan_to_num(accData)
    return accData_wo_nan, sampling_rate_sec, time_sec

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

def test():
    start = time.time()
    accData, sampling_per_sec, time_sec = clean_data(PATH, FILENAME)
    # sampling_per_sec = 20

    # length of data should be 1 minute
    numel = int(round(sampling_per_sec))*60
    print("Sampling rate = " + str(numel/60))
    print("Data length = " + str(len(accData)))
    # find number of minutes in data
    n = int(math.floor(time_sec/60))
    print(n)
    if n ==  0:
        print("ERROR: not enough data")
    sleeping = [False]*(n-1)
    # classify each minute of data
    for i in range(n-1):
        data_segment = accData[i*numel:min(len(accData), (i+1)*numel-1)]
        data = data_segment
        # data = zero_mean(data_segment)

        print("Iteration = " + str(i) + " len of data = " + str(len(data)))
        t = check_sleep_3D(data, sampling_per_sec)
        if (sum(t) > 1):
            sleeping[i] = True

    # for i in range(3):
    #     plot(np.arange(0, len(accDat)), data[:, i])
    end = time.time()
    print(end - start)
    print(sleeping, sum(sleeping))
    print("The baby is sleeping is " + str(True if (sum(sleeping) > math.floor((n-1)/2)) else False))
    return

test()
