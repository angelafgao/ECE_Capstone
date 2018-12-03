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

PATH = r"C:\Users\Angela\Documents\CMU\F18\18-500\\"
FILENAME = ["ac1calibrate.csv", "ac1jerk.csv", "ac1move.csv"]
THRESHOLD = 300  # THRESHOLD definitely can be greater than 20
SAMPLING_RATE = 65
TIME_SEC = 60

# Calibrate: [0, 0, 0] 0.06605493689756113 7.389945063102441 200 94.29
# Jerk: [919, 203, 1169] 2.265723076924019 1223.825723076924 200 91.00000000000001
# Move: [0, 297, 339] 0.31225848142153695 385.28425848142143 200 86.66000000000001


def box_conv(data):
    # makes the box filter
    box_width = SAMPLING_RATE * 5  # 5 second box for 20 second thing
    n = data.size
    signal_width = int(n / 3)
    box_filt = [0] * signal_width
    min_ones = int(math.floor(signal_width / 2 - box_width / 2) - 1)
    max_ones = int(math.floor(signal_width / 2 + box_width / 2))
    box_width = max_ones - min_ones
    print(min_ones, max_ones, len(box_filt), signal_width)
    for i in range(min_ones, max_ones):
        box_filt[i] = 1

    # find the fft of the box and signal
    fft_box_filt = np.fft.fft(box_filt)
    res = [0, 0, 0]
    for i in range(3):
        signal = data[:, i]
        fft_signal = np.fft.fft(signal)

        # multiply the signals together
        filt_signal = np.absolute(np.fft.ifft(np.multiply(fft_box_filt, fft_signal)))
        filt_signal = filt_signal/box_width
        res[i] = sum(abs(filt_signal))
    return res


def check_sleep_3D(accData):
    # makes the box filter
    box_width = SAMPLING_RATE * 5  # 5 second box for 20 second thing
    n = accData.size
    signal_width = int(n / 3)
    box_filt = [0] * signal_width
    min_ones = int(math.floor(signal_width / 2 - box_width / 2) - 1)
    max_ones = int(math.floor(signal_width / 2 + box_width / 2))
    for i in range(min_ones, max_ones):
        box_filt[i] = 1

    # find the fft of the box and signal
    fft_box_filt = np.fft.fft(box_filt)
    is_asleep_acc = [0, 0, 0]
    sums = [0, 0, 0]
    for i in range(3):
        signal = accData[:, i]
        fft_signal = np.fft.fft(signal)

        # multiply the signals together
        filt_signal = np.absolute(np.fft.ifft(np.multiply(fft_box_filt, fft_signal)))
        filt_signal = filt_signal / box_width
        sums[i] = sum(abs(filt_signal))
        if sums[i] < THRESHOLD:
            is_asleep_acc[i] = 1
    print(sums, THRESHOLD)
    if (sum(is_asleep_acc) >= 2):
        return True
    else:
        return False
    return "ERROR"
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

# acc_x, acc_y, acc_z
def get_data(path, filename):
    count = 0
    raw_data = []
    input = path + filename
    with open(input) as f:
        reader = csv.reader(f)
        for row in reader:
            if (count != 0):
                ax, ay, az = row
                ax = float(ax)/1000
                ay = float(ay)/1000
                az = float(az)/1000
                raw_data.append([ax, ay, az])
            count += 1
    return np.array(zero_mean(raw_data))

def zero_mean(data):
    n = len(data)
    mean = np.sum(data, axis = 0) / n
    for i in range(n):
        for j in range(len(data[0])):
            data[i][j] = data[i][j] - mean[j]
    return data

def plot(xvals, yvals, axis=None, xlabel=None, ylabel=None):
    plt.plot(xvals, yvals)
    if axis != None:
        plt.axis(axis)
    if xlabel != None:
        plt.xlabel(xlabel)
    if ylabel != None:
        plt.ylabel(ylabel)
    plt.show()

def main():
    print("start main")
    start = time.time()
    accData = get_data()

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

calibrate_data = get_data(PATH, FILENAME[0])
jerk_data = get_data(PATH, FILENAME[1])
move_data = get_data(PATH, FILENAME[2])
print(sum(abs(calibrate_data[1:-1] - calibrate_data[0:-2])))
print(sum(abs(jerk_data[1:-1] - jerk_data[0:-2])))
print(sum(abs(move_data[1:-1] - move_data[0:-2])))
calibrate_data = zero_mean(calibrate_data)
jerk_data = zero_mean(jerk_data)
move_data = zero_mean(move_data)
print(sum(abs(calibrate_data)))
print(sum(abs(jerk_data)))
print(sum(abs(move_data)))
print(check_sleep_3D(zero_mean(calibrate_data)))
print(check_sleep_3D(zero_mean(jerk_data)))
print(check_sleep_3D(zero_mean(move_data)))