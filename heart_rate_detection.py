# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 10:20:32 2018

@author: Angela
"""
import numpy as np
import scipy.signal as signal
import math, csv
import time
import os

SAMPLING_RATE = 100
TIME_SEC = 20
PATH = "/home/pi/Desktop"
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
    mean = np.sum(data)/n
    res = [0]*n
    for i in range(n):
        res[i] = data[i] - mean
    return res

def check_data_good(data):
    for i in range(len(data)):
        if (data[i] < 50000 or data[i] > 120000):
            print(data[i])
            return False
    return True

# IR, BPM, AVG
def clean_data(data):
    count = 0
    ir_data = []
    bpm_data = []
    avg_bpm_data = []
    for row in data:
        if (count != 0):
            ir, bpm, avg = data[count]
            ir = float(ir)
            bpm = float(bpm)
            avg = float(avg)
            ir_data.append(ir)
            bpm_data.append(bpm)
            avg_bpm_data.append(avg)
        count += 1
    return ir_data, bpm_data, avg_bpm_data

def main(data):
    start = time.time()
    T = 1.0/SAMPLING_RATE # sampling interval
    Fs = 1.0 / T
    ir_data, bpm_data, avg_bpm_data = clean_data(data)
    hr_data = zero_mean(ir_data)

    cutoff_bpm = [50.0, 200.0]
    cutoff_hz = [x/60 for x in cutoff_bpm] # cutoff frequency in HZ
    cutoff = [x/(Fs/2) for x in cutoff_hz]
    [b, a] = signal.butter(2, cutoff, 'bandpass') # 2nd order butterworth filter

    is_valid = check_data_good(ir_data)
    if (is_valid == False):
        return "Heart Rate: Please Place Sensor on Feet"
    else:
        # filter out the noise from signal
        hr_filt = signal.lfilter(b, a, hr_data)

        pks = signal.find_peaks_cwt(hr_filt, np.arange(3, 10))
        num_pks = len(pks)
        beats_from_peaks = num_pks/2
        bpm_from_peaks = beats_from_peaks*60/TIME_SEC
        print("HR Found from Beats is = " + str(bpm_from_peaks) + " BPM")
        time_btw_peaks = sum(np.array(pks[1:num_pks]) - np.array(pks[0:-1]))/(num_pks - 1)
        bpm_from_peaks = SAMPLING_RATE*60/time_btw_peaks/2
        print("HR Found from Time is = " + str(bpm_from_peaks) + " BPM")
        end = time.time()
        print("total time = " + str(end - start))
        return "Heart Rate:" + str(bpm_from_peaks)

print(clean_data([["IR", "hello", "sup"], ["1", "2", "3"], ["3", "2", "1"]]))