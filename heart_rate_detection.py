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

def generate_hr_with_artifact(bpm, seconds, T, bpm_artifact):
    signal_artifact_ratio = 100
    #artifact has a bpm of bpm_artifact
    hr = generate_hr(bpm, seconds, T)
    normalization_factor = bpm_artifact*seconds/60*2*math.pi/(np.size(hr)*T)
    artifact = np.sin(np.linspace(0, np.size(hr) * T, num = np.size(hr)) * normalization_factor) \
               / signal_artifact_ratio
    hr_with_artifact = artifact + hr
    plot(np.linspace(0, len(hr_with_artifact), num=len(hr_with_artifact)), hr_with_artifact)
    return hr_with_artifact

def generate_hr(bpm, seconds, T):
    y = np.linspace(0, seconds, num = seconds/T)
    beats = math.floor(seconds/60*bpm)
    base_len = math.floor(np.size(y)/beats)
    base = np.linspace(0, base_len-1, num = base_len)
    base = base/max(base)*(seconds/beats)
    peak = math.floor(np.size(base)*7/10)
    slope = (peak - T)/(np.size(base)-peak)
    base[peak+1:base_len] = base[peak] - base[peak+1:base_len]*slope + peak*T*slope
    # plot(np.linspace(0, len(base), num = base_len), base)
    for beat in range(beats):
        y[beat*np.size(base): beat*np.size(base) + np.size(base)] = base
    # plot(np.linspace(0, len(y), num = len(y)), y)
    return y

# find the next power of 2 greater than i
def nextpow2(i):
    n = 1
    while n < i: n *= 2
    return n

# center the data around 0
def zero_mean(data):
    n = len(data)
    mean = sum(data)/n
    for i in range(n):
        data[i] = data[i] - mean
    return data

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

def test_beat_detection():
    # bpmavg = 0
    bpm = 120
    seconds = 12
    T = 0.001 # sampling interval
    Fs = 1 / T
    bpm_artifact = 10
    for i in range(100):
        hr = generate_hr_with_artifact(bpm, seconds, T, bpm_artifact)
        hr_og = generate_hr(bpm, seconds, T)

        snr = 15
        stdev = max(hr)/snr
        hr_with_noise = np.random.normal(0, stdev, np.size(hr)) + hr
        plot(np.linspace(0, len(hr_with_noise), num=len(hr_with_noise)), hr_with_noise)

        cutoff_bpm = [50, 200]
        cutoff_hz = [x/60 for x in cutoff_bpm] # cutoff frequency in HZ
        cutoff = [x/(Fs/2) for x in cutoff_hz]
        [b, a] = signal.butter(2, cutoff, 'bandpass') # 2nd order butterworth filter

        # filter out the noise from signal
        hr_filt = signal.lfilter(b, a, hr)
        hr_filt_noise = signal.lfilter(b, a, hr_with_noise)

        hr_fft = np.fft.fft(hr_filt_noise)
        L = np.size(hr_filt)
        P2 = abs(hr_fft / L)
        P1 = P2[0:int(L / 2)]
        P1[1: -1] = 2 * P1[1: -1] # -1 for end -1
        NFFT = 2 ^ nextpow2(L)
        f = Fs / 2 * np.linspace(0, 1, NFFT / 2)

        index1 = np.argmax(2*abs(hr_fft[0:int(NFFT/2)-1]))
        hz_found1 = f[index1]
        cons = 0.58
        cons = 0.6
        bpm_found1 = hz_found1 * 60 / cons
        pks = signal.find_peaks(hr_filt)
        bpm_peakcount = np.size(pks) / seconds * 60
        bpmavg = bpmavg + bpm_found1
    bpmavg = bpmavg / 100
    return [bpm_found1, hz_found1, bpm_peakcount, bpmavg]

def beat_detection():
    T = 1/SAMPLING_RATE # sampling interval
    Fs = 1 / T
    [raw_data, ir_data, time_sec] = clean_data(PATH, FILENAME)
    hr = zero_mean(ir_data)

    cutoff_bpm = [50, 200]
    cutoff_hz = [x/60 for x in cutoff_bpm] # cutoff frequency in HZ
    cutoff = [x/(Fs/2) for x in cutoff_hz]
    [b, a] = signal.butter(2, cutoff, 'bandpass') # 2nd order butterworth filter

    num_seg = int(math.floor(time_sec/15))

    for i in range(num_seg):
        hr_seg = hr[i*SAMPLING_RATE*20:(i+1)*SAMPLING_RATE*20-1]
        # filter out the noise from signal
        hr_filt = signal.lfilter(b, a, hr_seg)

        hr_fft = np.fft.fft(hr_filt)
        L = np.size(hr_filt)
        P2 = abs(hr_fft / L)
        P1 = P2[0:int(L / 2)]
        P1[1: -1] = 2 * P1[1: -1] # -1 for end -1
        NFFT = nextpow2(L)
        f = Fs / 2 * np.linspace(0, 1, num = NFFT / 2, endpoint = False)

        index1 = np.argmax(2*abs(hr_fft[0:int(NFFT/2)]))
        # plot(f, abs(hr_fft[0:int(NFFT/2)]))
        hz_found = f[index1]/2
        cons = 0.58
        cons = 0.6
        bpm_found = hz_found * 60 / cons
        pks = signal.find_peaks(hr_filt)
        beats_from_peaks = len(pks[0])/2
        time_btw_peaks = sum(pks[0][1:len(pks[0])] - pks[0][0:-1])/len(pks[0]-1)
        bpm_from_peaks = SAMPLING_RATE*60/time_btw_peaks/2
        # print(hz_found, bpm_found, time_sec*60*bpm_found/2, bpm_from_peaks, time_sec)
        print("HR Found is = " + str(bpm_from_peaks) + "BPM")
        # plot(np.linspace(0, len(hr), num=len(hr)), hr)
        # plot(np.linspace(0, len(hr_filt), num=len(hr_filt)), hr_filt)
    return [bpm_found, hz_found, time_sec*60*bpm_found/2]


start = time.time()
beat_detection()
# clean_data(PATH, FILENAME)
# test_beat_detection()
# generate_hr(150, 20, 0.001)
# generate_hr_with_artifact(150, 20, 0.001, 5)
stop = time.time()
print(stop-start)

