import numpy as np
import cv2 as cv
import dlib
from scipy.spatial import distance as dist
from imutils import face_utils
import imutils
import time
from time import sleep
from picamera import PiCamera

##### https://www.pyimagesearch.com/2017/05/08/drowsiness-detection-opencv/
##### https://www.pyimagesearch.com/2017/04/10/detect-eyes-nose-lips-jaw-dlib-opencv-python/

EAR = 0.30

def adjust_gamma(image, gamma=1.0):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")
    return cv.LUT(image, table)

def ear_fn(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def main():
    camera = PiCamera()
    camera.resolution = (1024, 768)
    camera.start_preview()
    # Camera warm-up time
    sleep(1)
    camera.capture('foo.jpg', resize=(1024, 768))
    camera.stop_preview()
    camera.close()

    start = time.time()
    img = cv.imread('foo.jpg')
    w = len(img[0])
    h = len(img)
    M = cv.getRotationMatrix2D((w/2, h/2), 270, 1.0)
    img = cv.warpAffine(img, M, (h, w))

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('/home/pi/Desktop/shape_predictor_68_face_landmarks.dat')
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
    rects = detector(gray, 0)
    if (len(rects) == 0):
        return "Eyes: Failed Detection. Try Repositioning the Camera"
    print(rects)
    for rect in rects:
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
        clone = img.copy()
        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        for (x, y) in leftEye:
            cv.circle(clone, (x, y), 1, (0, 0, 255), -1)
        for (x, y) in rightEye:
            cv.circle(clone, (x, y), 1, (0, 0, 255), -1)
        leftEAR = ear_fn(leftEye)
        rightEAR = ear_fn(rightEye)
        ear = (leftEAR + rightEAR) / 2.0
        if (ear < EAR):
            return ("Closed")
            eyeOpenClose = "Eyes: Closed"
        else:
            return ("Open")
            eyeOpenClose = "Eyes: Open"
        cv.putText(clone, eyeOpenClose, (100, 200), cv.FONT_ITALIC,
        0.7, (0, 0, 255), 2)
        end = time.time()
        cv.imshow("Image", clone)
        cv.waitKey(0)
    print(end - start)
    return 