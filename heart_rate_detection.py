# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 10:20:32 2018

@author: Angela
"""

import numpy as np
from scipy import signal
import math, csv
import time
import matplotlib.pyplot as plt

SAMPLING_RATE = 100
PATH = r"C:\Users\Angela\Documents\CMU\F18\18-500\\"
FILENAME = "heartRate_nice.txt"

def plot(xvals, yvals, axis = None, xlabel = None, ylabel = None):
    plt.plot(xvals, yvals)
    if axis != None:
        plt.axis(axis)
    if xlabel != None:
        plt.xlabel(xlabel)
    if ylabel != None:
        plt.ylabel(ylabel)
    plt.show()

# find the next power of 2 greater than i
def nextpow2(i):
    n = 1
    while n < i: n *= 2
    return n

# center the data around 0
def zero_mean(data):
    n = len(data)
    mean = sum(data)/n
    res = [0]*n
    for i in range(n):
        res[i] = data[i] - mean
    return res

# clean up raw data from
# valid IR values [50,000 to 109,000]
def clean_data(path, filename):
    input = path + filename
    raw_data = []
    n = 0
    with open(input) as f:
        reader = csv.reader(f)
        for row in reader:
            if (row != []) and not("No finger?" in row[2]):
                n += 1
                row0 = row[0].split("=")
                row1 = row[1].split("=")
                row2 = row[2].split("=")
                # print(row, row0, row1, row2)
                ir = float(row0[1])
                bpm = float(row1[1])
                avg_bpm = float(row2[1])
                raw_data.append([ir, bpm, avg_bpm])
    time_sec = n/SAMPLING_RATE
    ir_data = [0]*n
    for i in range(n):
        ir_data[i] = raw_data[i][0]
    return raw_data, ir_data, time_sec

def check_data_good(data):
    for i in range(len(data)):
        if (data[i] < 50000 or data[i] > 106000):
            print(data[i])
            return False
    return True

def beat_detection():
    start = time.time()
    T = 1.0/SAMPLING_RATE # sampling interval
    Fs = 1.0 / T
    [raw_data, ir_data, time_sec] = clean_data(PATH, FILENAME)
    hr = zero_mean(ir_data)
    print(len(hr))

    cutoff_bpm = [50.0, 200.0]
    cutoff_hz = [x/60 for x in cutoff_bpm] # cutoff frequency in HZ
    cutoff = [x/(Fs/2) for x in cutoff_hz]
    print(cutoff, cutoff_bpm, cutoff_hz, Fs)
    [b, a] = signal.butter(2, cutoff, 'bandpass') # 2nd order butterworth filter

    num_seg = int(math.floor(time_sec/15))
    for i in range(num_seg):
        hr_seg = hr[i * SAMPLING_RATE * 15:(i + 1) * SAMPLING_RATE * 15 - 1]
        ir_seg = ir_data[i * SAMPLING_RATE * 15:(i + 1) * SAMPLING_RATE * 15 - 1]
        is_valid = check_data_good(ir_seg)
        print("data is " + str(is_valid))
        # filter out the noise from signal
        hr_filt = signal.lfilter(b, a, hr_seg)

        pks = signal.find_peaks_cwt(hr_filt, np.arange(3, 10))
        num_pks = len(pks)
        beats_from_peaks = num_pks/2
        time_btw_peaks = sum(pks[1:num_pks] - pks[0:-1])/(num_pks - 1)
        bpm_from_peaks = SAMPLING_RATE*60/time_btw_peaks/2
        print("HR Found is = " + str(bpm_from_peaks) + " " + str(beats_from_peaks*4) + " BPM")
        end = time.time()
        print("total time = " + str(end - start))
    return bpm_from_peaks


beat_detection()

