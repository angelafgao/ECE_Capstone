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
FILENAME = "hc1.csv"

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

def check_data_good(data):
    for i in range(len(data)):
        if (data[i] < 50000 or data[i] > 109000):
            print(data[i])
            return False
    return True

# IR, BPM, AVG
def get_data(path, filename):
    with open(path + "/" + filename) as f:
        reader = csv.reader(f)
        rawData = []
        for row in reader:
            rawData.append(row)
    raw_data = np.array(rawData)
    ir_data = raw_data[:][0:]
    bpm_data = raw_data[:][1:]
    avg_bpm_data = raw_data[:][2:]
    return ir_data, bpm_data, avg_bpm_data

def main():
    start = time.time()
    T = 1.0/SAMPLING_RATE # sampling interval
    Fs = 1.0 / T
    ir_data, bpm_data, avg_bpm_data = get_data(PATH, FILENAME)
    hr_data = zero_mean(ir_data)

    cutoff_bpm = [50.0, 200.0]
    cutoff_hz = [x/60 for x in cutoff_bpm] # cutoff frequency in HZ
    cutoff = [x/(Fs/2) for x in cutoff_hz]
    [b, a] = signal.butter(2, cutoff, 'bandpass') # 2nd order butterworth filter

    is_valid = check_data_good(ir_data)
    print("data is " + str(is_valid))
    # filter out the noise from signal
    hr_filt = signal.lfilter(b, a, hr_data)

    pks = signal.find_peaks_cwt(hr_filt, np.arange(3, 10))
    num_pks = len(pks)
    beats_from_peaks = num_pks/2
    time_btw_peaks = sum(pks[1:num_pks] - pks[0:-1])/(num_pks - 1)
    bpm_from_peaks = SAMPLING_RATE*60/time_btw_peaks/2
    print("HR Found is = " + str(bpm_from_peaks) + " " + str(beats_from_peaks*3) + " BPM")
    end = time.time()
    print("total time = " + str(end - start))
    return bpm_from_peaks


main()

