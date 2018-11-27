import sleepwake_accelerometer
import heart_rate_detection
import time

prev = time.time()
is_asleep = None
hr = None
eyes_closed = None
while True:
    sleep_wake_data = pull_data()
    is_asleep = sleepwake_accelerometer.test(sleep_wake_data)
    heart_rate_data = pull_data()
    hr = heart_rate_detection.beat_detection(heart_rate_data)
    if (time.time()-prev > 15):
        take_photo()
        prev = time.time()
    update_app_data(is_asleep, hr, eyes_closed)


